"""Exercise real Windows CLI processes in stages, with resource and state evidence."""
import argparse
import ctypes
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mg', ROOT / 'cli/mg.py')
mg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)


class MemoryStatus(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in
        ['total_physical', 'available_physical', 'total_pagefile', 'available_pagefile', 'total_virtual', 'available_virtual', 'available_extended']]


def memory():
    value = MemoryStatus()
    value.length = ctypes.sizeof(value)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value))
    return {'total_physical_bytes': value.total_physical, 'available_physical_bytes': value.available_physical, 'memory_load_percent': value.load}


def docker_memory():
    result = subprocess.run(['docker', 'stats', mg.CONTAINER, '--no-stream', '--format', '{{json .}}'],
        capture_output=True, text=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    data = json.loads(result.stdout)
    return {key: data[key] for key in ['MemUsage', 'CPUPerc', 'PIDs']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('limit', type=int)
    parser.add_argument('--profile', choices=['yi', 'shiyan'], default='yi')
    parser.add_argument('--cup', action='store_true', help='Use the exact fixed cup probe for request zero')
    args = parser.parse_args()
    mg.configure_profile(args.profile)
    if mg.session_frozen():
        raise RuntimeError('The selected profile is frozen; no browser requests were sent')
    token = mg.read_auth()
    _, state = mg.http_json('/v1/mimic-cli/concurrency', token, {'max_concurrency': args.limit})
    (ROOT / 'config' / ('concurrency.json' if args.profile == 'yi' else 'concurrency-shiyan.json')).write_text(
        json.dumps({'max_concurrency': args.limit}), encoding='utf-8')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'runs' / ('parallel-' + args.profile + '-' + stamp + '-' + str(args.limit))
    folder.mkdir()
    samples = []
    stopped = threading.Event()
    def sample():
        while not stopped.is_set():
            item = {'timestamp': time.time(), 'windows': memory()}
            try:
                _, item['pool'] = mg.http_json('/v1/mimic-cli/concurrency', token, timeout=10)
                item['docker'] = docker_memory()
            except Exception as exc:
                item['sample_error'] = type(exc).__name__
            samples.append(item)
            stopped.wait(5)
    sampler = threading.Thread(target=sample)
    sampler.start()
    def request(index):
        marker = f'PARALLEL_{args.limit}_{stamp}_{index}'
        prompt = ('请不要联网，也不要写代码。给出完整严谨证明：所有正整数三元组(a,b,c)满足 '
            'a²+b²+c²=3abc 的解，是否都能从(1,1,1)通过置换和替换c为3ab-c得到？'
            '请证明替换保持正整数性，构造严格下降过程并分析所有边界和等号情形；'
            '还要解释如何逆向枚举，以及为什么这不会漏解。写出完整推导，不能只引用已知定理。'
            '\n回答第一行必须原样写出本次标识：' + marker)
        is_cup = args.cup and index == 0
        command = ['probe', 'cup'] if is_cup else ['ask', prompt]
        result = subprocess.run([sys.executable, str(ROOT / 'cli/mg.py'), '--profile', args.profile] + command,
            capture_output=True, text=True, encoding='utf-8', timeout=1500, creationflags=subprocess.CREATE_NO_WINDOW)
        match = re.search(r'Run: (.+)', result.stderr)
        record = json.loads(Path(match.group(1).strip(), 'diagnostics.json').read_text(encoding='utf-8')) if match else {}
        text = record.get('response', '')
        output = {'index': index, 'marker': marker, 'exit_code': result.returncode, 'run': match.group(1).strip() if match else None,
            'marker_first_line': text.strip().splitlines()[0].strip() == marker if text.strip() else False,
            'marker_count': text.count(marker), 'diagnostics': record.get('diagnostics', {}), 'error': record.get('error'),
            'success': record.get('success', False), 'elapsed_seconds': record.get('elapsed_seconds')}
        output['is_cup'] = is_cup
        output['cup_assessment'] = record.get('probe_assessment')
        print(json.dumps({'completed': index, 'exit_code': result.returncode, 'marker_first_line': output['marker_first_line'],
            'error': output['error']}, ensure_ascii=False), flush=True)
        return output
    try:
        with ThreadPoolExecutor(max_workers=args.limit) as pool:
            results = list(pool.map(request, range(args.limit)))
    finally:
        stopped.set()
        sampler.join(timeout=25)
    events = []
    for item in results:
        diag = item['diagnostics']
        if 'submitted_at' in diag and 'completed_at' in diag:
            events.extend([(diag['submitted_at'], 1), (diag['completed_at'], -1)])
    active = peak = 0
    for stamp_value, delta in sorted(events):
        active += delta
        peak = max(peak, active)
    report = {'profile': args.profile, 'limit': args.limit, 'state_at_start': state, 'requests': results, 'samples': samples,
        'all_passed': all(item['exit_code'] == 0 and (item['cup_assessment']['normal'] if item['is_cup'] else
            item['marker_first_line'] and item['marker_count'] == 1) for item in results),
        'unique_thread_ids': len({item['diagnostics'].get('thread_id') for item in results}) == args.limit,
        'unique_request_ids': len({item['diagnostics'].get('request_id') for item in results}) == args.limit,
        'peak_submitted_uncompleted': peak,
        'peak_in_flight': max((s.get('pool', {}).get('in_flight', 0) for s in samples), default=0),
        'peak_worker_tabs': max((s.get('pool', {}).get('worker_tabs', 0) for s in samples), default=0),
        'minimum_available_physical_bytes': min((s['windows']['available_physical_bytes'] for s in samples), default=0)}
    folder.joinpath('report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['limit', 'all_passed', 'peak_submitted_uncompleted', 'peak_in_flight', 'peak_worker_tabs', 'minimum_available_physical_bytes']}) + '\nReport: ' + str(folder), flush=True)
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
