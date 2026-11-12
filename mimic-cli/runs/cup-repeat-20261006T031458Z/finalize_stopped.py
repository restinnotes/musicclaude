from pathlib import Path
from datetime import datetime, timezone
import json
import sys

batch = Path(__file__).resolve().parent
root = batch.parents[1]
sys.path.insert(0, str(root / 'scripts'))
import cup_repeat

state_path = batch / 'state.json'
state = json.loads(state_path.read_text(encoding='utf-8-sig'))
state['started_utc'] = '2026-10-06T03:14:58.693057+00:00'
state['stopped_utc'] = datetime.fromisoformat(state['stopped_utc'].replace('Z', '+00:00')).astimezone(timezone.utc).isoformat()
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
rows = []
for idx, run_id in enumerate(['20261006T025558.795032Z-76721525', '20261006T030214.404015Z-02820e1d', '20261006T030846.900236Z-3c20082f'], 1):
    run = root / 'runs' / run_id
    row = cup_repeat.summarize(json.loads((run / 'diagnostics.json').read_text(encoding='utf-8')), run)
    row.update(phase='prior', sequence=idx)
    rows.append(row)
rows.extend(json.loads(line) for line in (batch / 'results.jsonl').read_text(encoding='utf-8').splitlines() if line.strip())
run = root / 'runs' / '20261006T032151.999095Z-6dc9b72c'
interruption = {'classification': 'interrupted_by_user', 'reason': 'Docker stopped at user request to reduce memory use.',
                'stopped_utc': state['stopped_utc'], 'is_answer_result': False,
                'note': 'RemoteDisconnected in the original diagnostics is caused by the requested container stop; do not count it as an independent login failure.'}
(run / 'interruption.json').write_text(json.dumps(interruption, ensure_ascii=False, indent=2), encoding='utf-8')
cup_repeat.report(batch, rows)
text = ['# Docker 水杯题测试记录（已按用户要求停止）', '',
        '容器 yi-mimicgate-20261002 已停止。计划 5 轮，本次完成 3 轮；第 4 轮中止，第 5 轮未启动。',
        '同一题目、同一 yi 登录态、GPT-5.6 Sol / Extra High；串行，轮间隔 10 秒。',
        '时间均为纽约时间（UTC-04:00）。总耗时含准备、思考和输出；提交至完成耗时含思考和输出。', '',
        '|阶段|轮次|开始时间（纽约）|总耗时 秒|提交至完成 秒|答案|实际档位|截图|',
        '|---|---:|---|---:|---:|---|---|---|']
for row in rows:
    run_path = Path(row['run_path'])
    shots = list((run_path / 'screenshots').glob('*.jpg'))
    direct = run_path / 'docker-browser-response.jpg'
    shot = run_path / 'docker-browser-last-observed.jpg'
    screenshot = f'[{len(shots)} 张过程截图]({shot.as_posix()})' if shot.exists() else (f'[已有截图]({direct.as_posix()})（生成中）' if direct.exists() else '缺失（截图机制接入前）')
    row.update(screenshot_count=len(shots), screenshot_path=str(shot) if shot.exists() else (str(direct) if direct.exists() else None))
    text.append(f"|{row['phase']}|{row['sequence']}|{row['started_new_york']}|{row['total_seconds']}|{row['submit_to_complete_seconds']}|{row['answer']}|{row['actual_effort']}|{screenshot}|")
text.extend(['', '第 4 轮于纽约时间 23:21:51 开始，按用户要求停止容器后中断，未产生最终答案；已保存 7 张过程截图。',
             '第 1 轮完成时尚未接入截图机制，未补测，因为用户随后要求停止容器。',
             '第 2 轮截图显示 Worked for 3m 10s；第 3 轮截图显示 Worked for 48s，答案 x=6。',
             '过程截图按原样保存；画面中部分中文字体显示为方框，完整中文回答见 response.txt。', '', '## 原始证据', ''])
for row in rows:
    path = Path(row['run_path']).as_posix()
    text.append(f"- {row['phase']} {row['sequence']}: [诊断]({path}/diagnostics.json)、[完整回答]({path}/response.txt)。")
text.append(f'- 中止轮次：[中止原因]({run.as_posix()}/interruption.json)、[原始诊断]({run.as_posix()}/diagnostics.json)。')
(batch / 'report.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
(batch / 'results-with-evidence.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'completed_new_runs': len([r for r in rows if r['phase'] == 'new']), 'report': str(batch / 'report.md'), 'status': state['status']}))
