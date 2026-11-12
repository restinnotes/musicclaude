"""Repeat the existing yi cup CLI, with durable timing and answer evidence."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import csv
import json
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
NY = ZoneInfo('America/New_York')


def stamp(epoch=None):
    moment = datetime.fromtimestamp(epoch, timezone.utc) if epoch is not None else datetime.now(timezone.utc)
    return moment.isoformat()


def summarize(record, run):
    details = record.get('diagnostics', {})
    submitted = details.get('submitted_at')
    completed = details.get('completed_at')
    begin = datetime.fromisoformat(record['timestamp'])
    total = record.get('elapsed_seconds')
    end = begin + timedelta(seconds=total or 0)
    return {
        'run_id': record['run_id'], 'run_path': str(run),
        'started_utc': begin.isoformat(), 'completed_utc': end.isoformat(),
        'started_new_york': begin.astimezone(NY).isoformat(),
        'completed_new_york': end.astimezone(NY).isoformat(),
        'submitted_utc': stamp(submitted) if submitted else None,
        'response_completed_utc': stamp(completed) if completed else None,
        'total_seconds': total,
        'submit_to_complete_seconds': round(completed - submitted, 3) if submitted and completed else None,
        'queue_seconds': details.get('queue_seconds'),
        'actual_model': record.get('actual_model'),
        'actual_effort': record.get('actual_reasoning_effort'),
        'model_ui_label': details.get('model', {}).get('actual_label'),
        'temporary_verified': details.get('temporary_chat', {}).get('verified'),
        'unpersonalized_verified': details.get('non_personalized', {}).get('verified'),
        'prompt_sha256': record.get('prompt_sha256'),
        'answer': record.get('probe_assessment', {}).get('observed_answer'),
        'assessment': record.get('probe_assessment', {}).get('status'),
        'answer_evidence': record.get('probe_assessment', {}).get('evidence'),
        'transport_success': record.get('transport_success', False),
        'response_complete': details.get('response_complete'),
        'request_id': details.get('request_id'),
        'in_flight_at_completion': details.get('concurrency', {}).get('in_flight'),
        'error_type': (record.get('error') or {}).get('type'),
    }


def report(batch, rows):
    fields = ['phase', 'sequence', 'started_new_york', 'completed_new_york',
              'total_seconds', 'submit_to_complete_seconds', 'answer', 'assessment',
              'actual_model', 'actual_effort', 'prompt_sha256', 'run_path']
    with (batch / 'results.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    text = ['# Docker 水杯题重复测试', '',
            '固定 yi 容器、原题、GPT-5.6 Sol / Extra High；5 次串行请求，轮间隔 10 秒。',
            '开始时间采用纽约时间 UTC-04:00。总耗时包含准备、等待、思考和输出。',
            '提交至完成耗时包含思考和输出，不能当作纯思考耗时。', '',
            '|阶段|轮次|开始时间（纽约）|总耗时 秒|提交至完成 秒|答案|档位|',
            '|---|---:|---|---:|---:|---|---|']
    for row in rows:
        text.append(f"|{row['phase']}|{row['sequence']}|{row['started_new_york']}|{row['total_seconds']}|{row['submit_to_complete_seconds']}|{row['answer']}|{row['actual_effort']}|")
    text.extend(['', '## 原始证据', ''])
    for row in rows:
        path = Path(row['run_path']).as_posix()
        text.append(f"- {row['phase']} {row['sequence']}: [diagnostics.json]({path}/diagnostics.json), [完整回答]({path}/response.txt)")
    (batch / 'report.md').write_text('\n'.join(text) + '\n', encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    batch = ROOT / 'runs' / ('cup-repeat-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    batch.mkdir()
    print('BATCH ' + str(batch), flush=True)
    rows = []
    baseline = ['20261006T025558.795032Z-76721525', '20261006T030214.404015Z-02820e1d', '20261006T030846.900236Z-3c20082f']
    for idx, run_id in enumerate(baseline, 1):
        run = ROOT / 'runs' / run_id
        record = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
        row = summarize(record, run)
        row.update(phase='prior', sequence=idx)
        rows.append(row)
    report(batch, rows)
    state = {'status': 'running', 'planned_runs': count, 'started_utc': stamp(), 'interval_seconds': 10}
    for idx in range(1, count + 1):
        state.update(current_run=idx)
        (batch / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'event': 'started', 'sequence': idx, 'utc': stamp()}), flush=True)
        try:
            proc = subprocess.run([sys.executable, str(ROOT / 'cli' / 'mg.py'), '--profile', 'yi', 'probe', 'cup'],
                cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW, timeout=2400)
        except subprocess.TimeoutExpired:
            state.update(status='stopped_infrastructure_error', error='cli_timeout', completed_utc=stamp())
            break
        (batch / f'{idx:02d}-stdout.txt').write_text(proc.stdout, encoding='utf-8')
        (batch / f'{idx:02d}-stderr.txt').write_text(proc.stderr, encoding='utf-8')
        match = re.search(r'^Run:\s*(.+)$', proc.stderr, re.MULTILINE)
        if not match:
            state.update(status='stopped_infrastructure_error', error='missing_run_path', completed_utc=stamp())
            break
        run = Path(match.group(1).strip())
        record = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
        row = summarize(record, run)
        row.update(phase='new', sequence=idx, exit_code=proc.returncode)
        rows.append(row)
        with (batch / 'results.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')
        report(batch, rows)
        print(json.dumps({'event': 'completed', **row}, ensure_ascii=False), flush=True)
        if not row['transport_success'] or not row['response_complete'] or row['actual_effort'] != 'xhigh':
            state.update(status='stopped_infrastructure_error', error=row['error_type'], completed_utc=stamp())
            break
        if idx < count:
            time.sleep(10)
    else:
        state.update(status='complete', completed_utc=stamp())
    (batch / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(state), flush=True)


if __name__ == '__main__':
    main()
