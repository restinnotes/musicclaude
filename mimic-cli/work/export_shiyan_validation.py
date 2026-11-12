"""Export completed run evidence only; never include authentication material."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import re

def gib(text):
    match = re.match(r'([\d.]+)([A-Za-z]+)', text)
    if not match:
        return 0
    value, unit = float(match[1]), match[2]
    return value * {'GiB':1, 'MiB':1/1024, 'KiB':1/1024**2, 'GB':1e9/1024**3, 'MB':1e6/1024**3}.get(unit,0)

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs')

def main():
    stages = []
    for path in sorted(ROOT.glob('runs/parallel-shiyan-*/report.json')):
        r = json.loads(path.read_text(encoding='utf-8'))
        stages.append({'limit': r['limit'], 'all_passed': r['all_passed'],
            'requests': len(r['requests']), 'passed': sum(i['success'] for i in r['requests']),
            'peak_simultaneous_generations': r['peak_submitted_uncompleted'],
            'peak_worker_tabs': r['peak_worker_tabs'],
            'unique_thread_ids': r['unique_thread_ids'], 'unique_request_ids': r['unique_request_ids'],
            'minimum_available_physical_GiB': round(r['minimum_available_physical_bytes']/1024**3, 3),
            'container_memory_samples': sorted({i.get('docker',{}).get('MemUsage','') for i in r['samples']}),
            'peak_container_memory_GiB': round(max((gib(i.get('docker',{}).get('MemUsage','')) for i in r['samples']),default=0),3),
            'generation_peak_covers_all_requests': all('completed_at' in i['diagnostics'] for i in r['requests']),
            'actual_efforts': sorted({i.get('diagnostics',{}).get('model',{}).get('selected_effort','') for i in r['requests']}),
            'full_report': str(path)})
    records = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(ROOT.glob('runs/*/diagnostics.json'))]
    checks = [r for r in records if r.get('profile') == 'shiyan' and r['command'] == 'check']
    cups = [r for r in records if r.get('profile') == 'shiyan' and r['command'] == 'probe']
    result = subprocess.run(['docker','exec','shiyan-mimicgate-20261002','/opt/venv/bin/python','-c',
        "import json; from pathlib import Path; a=json.loads(Path('/app/state/shiyan-session-observations.json').read_text()); print(json.dumps({'samples':len(a),'all_present':all(i['present'] for i in a),'started':a[0]['timestamp'],'ended':a[-1]['timestamp']}))"],
        capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    monitoring = json.loads(result.stdout)
    old_monitor_path = OUT / 'shiyan会话监测-修复前.json'
    if old_monitor_path.exists():
        previous = json.loads(old_monitor_path.read_text(encoding='utf-8'))
        monitoring['previous_segment'] = {'samples':len(previous),'all_present':all(i['present'] for i in previous),
                                        'started':previous[0]['timestamp'],'ended':previous[-1]['timestamp']}
    monitoring['total_samples'] = monitoring['samples'] + monitoring.get('previous_segment',{}).get('samples',0)
    fresh_checks = []
    for path in sorted(OUT.glob('shiyan新页面登录-*.json')):
        fresh_checks.append({'file':path.name, **json.loads(path.read_text(encoding='utf-8'))})
    report = {'generated_at':datetime.now(timezone.utc).isoformat(), 'profile':'shiyan / Profile 7',
        'container':'shiyan-mimicgate-20261002','api':'http://127.0.0.1:8651','gui':'http://127.0.0.1:5801/',
        'existing_login_reused':True,'cookie_reimport_performed':False,
        'yi_login_unchanged_during_parallel_stages':True,
        'yi_cli_frozen':(ROOT/'config/session-investigation.freeze').exists(),
        'previous_yi_loss_root_trigger':'UNPROVEN','model':'gpt-5.6-sol',
        'requested_effort':'xhigh','actual_effort':'high',
        'fallback_reason':'extra_high_unavailable_high_authorized',
        'startup_cleanup_fix_deployed_to_shiyan':True,
        'stages':stages,'session_monitor':monitoring,'fresh_page_checks':fresh_checks,
        'check':checks[-1] if checks else None,'cup':cups[-1] if cups else None}
    restore_path=OUT/'yi登录态恢复.json'
    if restore_path.exists():
        report['subsequent_yi_session_restore']=json.loads(restore_path.read_text(encoding='utf-8'))
        report['startup_cleanup_fix_written_to_yi_without_restart']=True
    OUT.mkdir(exist_ok=True)
    OUT.joinpath('shiyan并发验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['shiyan Plus 并发实测', '复用既有 shiyan 容器和保存的登录态；本轮没有重新导入 cookie。',
        'GPT-5.6 Sol；请求 xhigh，实际 High。网页不提供 Extra High，按用户授权降级。',
        '每次发送前分别验证 Temporary Chat、Unpersonalized、模型及实际档位。',
        '并发测试期间 yi 保持原状；随后按用户新指令已导入原来源的缺失会话 cookie。',
        'yi 新页面和刷新登录均已验证。此前会话消失的精确触发事件仍未证明。', '',
        '配置并发 | 完成/通过 | 实际同时生成峰值 | 最少剩余物理内存 GiB']
    for s in stages:
        peak = s['peak_simultaneous_generations'] if s['generation_peak_covers_all_requests'] else '未完整采集'
        lines.append(f"{s['limit']} | {s['passed']}/{s['requests']} | {peak} | {s['minimum_available_physical_GiB']}")
    lines += ['',f"会话存在性采样：共 {monitoring['total_samples']} 次；最终段 {monitoring['samples']} 次；全部存在：{monitoring['all_present']}。",
        '此指标表示 cookie 存在；新页面可否登录以另外的 UI 检查为准。',
        'TEST_OK：'+str(checks[-1]['success'] if checks else '未测'),
        '水杯 probe：'+str(cups[-1].get('probe_assessment') if cups else '未测'), '',
        '命令：mg --profile shiyan check', '命令：mg --profile shiyan ask "你的问题"',
        '命令：mg --profile shiyan probe cup', '命令：mg --profile shiyan parallel',
        '完整记录位于 D:\\musicclaude\\mimic-cli\\runs。']
    OUT.joinpath('shiyan并发验收.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'stages':[{k:s[k] for k in ['limit','all_passed','passed','requests',
        'peak_simultaneous_generations','peak_container_memory_GiB','minimum_available_physical_GiB']} for s in stages],
        'session_monitor':monitoring},ensure_ascii=False))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
