from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
stage = json.loads((HERE / 'stages-state.json').read_text(encoding='utf-8'))
candidate_state = json.loads((Path(stage['candidate_batch'])/'state.json').read_text(encoding='utf-8'))
stage['candidate_status'] = candidate_state['status']
stage['status'] = 'complete' if candidate_state['status'] == 'complete' else ('candidate_running' if candidate_state['status'] == 'running' else 'stopped')
stage['updated_utc'] = datetime.now(timezone.utc).isoformat()
(HERE/'stages-state.json').write_text(json.dumps(stage, indent=2), encoding='utf-8')
rows = []
for key in ('baseline_batch', 'candidate_batch'):
    directory = Path(stage[key]) if stage.get(key) else None
    if directory and (directory / 'results.jsonl').exists():
        for line in (directory / 'results.jsonl').read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                run = Path(row['run_path'])
                diagnostic = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
                evidence = diagnostic.get('diagnostics', {}).get('screenshot_evidence') or {}
                row['screenshots_hash_verified'] = all(
                    (run / 'screenshots' / image['filename']).exists()
                    and hashlib.sha256((run / 'screenshots' / image['filename']).read_bytes()).hexdigest() == image['sha256']
                    for image in evidence.get('files', [])) and bool(evidence.get('files'))
                rows.append(row)
fields = ['profile', 'sequence', 'started_new_york', 'completed_new_york', 'answer',
          'actual_model', 'actual_effort', 'total_seconds', 'submit_to_complete_seconds',
          'thinking_time_ui_labels', 'screenshot_capture_seconds', 'screenshots_hash_verified', 'run_path']
with (HERE / 'results.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
(HERE / 'results.json').write_text(json.dumps({'stage': stage, 'trials': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
text = ['# shiyan Chrome / Camoufox 水杯题对照记录', '',
        f"运行状态：{stage['status']}。", '',
        '同一个 shiyan Plus 账号，固定题面，GPT-5.6 Sol，实际 High，Temporary Chat + Unpersonalized。',
        '两组各计划 3 次串行请求；正常轮间隔 10 秒，Chrome 超时后恢复第 3 轮间隔约 60 秒。',
        '先停 Chrome 再启动 Camoufox，使用同一 Docker 默认网络出口设置，没有加入参考工程的代理池。',
        '候选采用参考 Grok 工程的 Camoufox 0.5.4 / 152.0.4-beta.31、Windows 指纹、headed、',
        'humanize、geoip、en-US、禁用 WebRTC，以及 30–120ms 逐字输入和偶尔 120–300ms 停顿。',
        'MimicGate 标准状态控制和响应完成判断沿用基线源码；Chrome 组只增加观测截图和私有 cookie 导出。', '',
        '总耗时含准备、输入、思考、输出和截图；提交至完成不含最终截图，仍包含思考和输出。',
        'Worked for / Thought for 是网页显示的标签，单独记录，不与计时字段混同。', '',
        '|组别|轮次|开始时间（纽约）|答案 / 状态|总耗时 秒|提交至完成 秒|网页计时|实际档位|最终截图校验|',
        '|---|---:|---|---|---:|---:|---|---|---|']
for row in rows:
    group = 'Chrome' if row['profile'] == 'shiyan' else 'Camoufox'
    label = ', '.join(row.get('thinking_time_ui_labels', [])) or '未取得'
    answer = row['answer'] if row['response_complete'] else (row['error_type'] or '未完成')
    text.append(f"|{group}|{row['sequence']}|{row['started_new_york']}|{answer}|{row['total_seconds']}|{row['submit_to_complete_seconds']}|{label}|{row['actual_effort']}|{row['screenshots_hash_verified']}|")
text.extend(['', '## 原始证据', ''])
for row in rows:
    path = Path(row['run_path']).as_posix()
    if row['response_complete']:
        text.append(f"- {row['profile']} 第 {row['sequence']} 轮：[诊断]({path}/diagnostics.json)、[完整回答]({path}/response.txt)、[最终视口截图]({path}/screenshots/response-viewport.jpg)、[最终整页截图]({path}/screenshots/response-full.jpg)、[发送前截图]({path}/screenshots/prepared-full.jpg)。")
    else:
        run = Path(row['run_path'])
        image = next((p for p in [run / 'screenshots' / 'failure-full.jpg', run / 'screenshots' / 'thinking-before-timeout.jpg', run / 'docker-browser-last-observed.jpg'] if p.exists()), None)
        photo = f'、[未完成页面截图]({image.as_posix()})' if image else '；页面截图缺失'
        text.append(f"- {row['profile']} 第 {row['sequence']} 轮：[诊断]({path}/diagnostics.json){photo}。未取得最终答案，不计作答错。")
text.extend(['', '## 本次实测判断', ''])
for profile, name in [('shiyan','原 Chrome'),('shiyan-camoufox','Camoufox')]:
    trials = [r for r in rows if r['profile']==profile]
    outcomes = [r['answer'] if r['response_complete'] else r['error_type'] for r in trials]
    text.append(f"{name}：{outcomes}。")
baseline_complete = [r['answer'] for r in rows if r['profile']=='shiyan' and r['response_complete']]
candidate_complete = [r['answer'] for r in rows if r['profile']=='shiyan-camoufox' and r['response_complete']]
if baseline_complete and candidate_complete and all(answer==8 for answer in baseline_complete+candidate_complete):
    text.extend(['', '按用户指定的正常答案 8，本次没有复现 shiyan 在原 Chrome 链路稳定降智。',
                 '原 Chrome 已能回答 8，Camoufox 也回答 8，因此不能证明浏览器指纹或人类化输入修复了能力异常。',
                 '本次不包含同一个 yi / Extra High 账号的浏览器对照，不能解释此前该账号答 6/7 的原因。'])
text.extend(['', '## 历史参照与判断边界', '',
             '历史 shiyan 同题 High 记录 20261005T032106.542102Z-bdc01105：答案 8，总耗时 677.062 秒。',
             '用户指定正常答案为 8；这里记录探针答案是否匹配，不代表已独立复核每份数学证明。',
             '这是浏览器方案整体的对照，同时包含引擎、指纹和输入行为变化，不能单独归因到某个防指纹参数。',
             'yi 的账号和 Extra High 档位与 shiyan Plus / High 不同，不能把两者当作同条件对照。',
             '截图为浏览器原始 JPEG，按哈希验证复制一致；部分中文字体显示为方框，完整文本另存。',
             '原 cookie/profile 保留在原卷中；候选使用独立 profile，并只读导入同账号 cookie。'])
text.extend(['', '## 候选输入适配留痕', '',
             '正式测试前，逐字键入触发了 ProseMirror 的编号列表输入规则；严格完整题面校验阻止了发送。',
             'Ctrl+Z 后补空格仍重新触发列表，最终改为编号前缀逐字输入时增加一个临时字符，随后立即用方向键和 Delete 删除它。',
             '其余字符仍逐字键入并随机停顿。完整题面校验保持原标准，不放宽比较。',
             '以下适配失败均未取得模型答案；启动前探测连接失败也不计为模型结果。'])
for directory in stage.get('adaptation_batches', []):
    batch = Path(directory)
    if (batch/'results.jsonl').exists():
        for line in (batch/'results.jsonl').read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            run = Path(row['run_path']).as_posix()
            text.append(f"- {row['started_new_york']}，{row['error_type']}，未发送：[诊断]({run}/diagnostics.json)。")
candidate = Path(stage['candidate_batch'])
if (candidate/'memory.jsonl').exists():
    resource = [json.loads(line) for line in (candidate/'memory.jsonl').read_text().splitlines()]
    valid = [r for r in resource if 'memory_current_mib' in r]
    if valid:
        text.extend(['', '## 资源观测', '',
                     f"每 30 秒记录候选 cgroup；采样峰值 {max(r['memory_current_mib'] for r in valid):.2f} MiB，",
                     f"swap 采样峰值 {max(r['swap_mib'] for r in valid):.2f} MiB，末次计数 {valid[-1]['events']}。",
                     f"[原始内存观测]({(candidate/'memory.jsonl').as_posix()})。内存限额与 swap 压力可能影响耗时。"])
if (HERE/'resource-adjustment.json').exists():
    adjustment = json.loads((HERE/'resource-adjustment.json').read_text(encoding='utf-8-sig'))
    text.extend(['', f"候选第 3 轮资源条件调整：{adjustment['changed_new_york']}，内存上限 2 → 2.5 GiB，内存加 swap 上限 3 → 3.5 GiB。",
                 '调整前观察到约 805 MiB swap 和明显内存回收，主机可用内存约 2.28 GiB；未发生 OOM。浏览器会话未重启。',
                 '因此第 3 轮耗时不能视为与前两轮完全相同的内存条件；题面、账号、档位和浏览器配置不变。',
                 f"[资源调整记录]({(HERE/'resource-adjustment.json').as_posix()})。"])
if (HERE/'shutdown-evidence.json').exists():
    shutdown = json.loads((HERE/'shutdown-evidence.json').read_text(encoding='utf-8'))
    text.extend(['', '## 收尾状态', '',
                 f"候选浏览器正常关闭确认：{shutdown['browser_close_confirmed']}；容器 {shutdown['container_status']}，退出码 {shutdown['exit_code']}，OOMKilled={shutdown['oom_killed']}。",
                 '截图及资源观察进程已结束；候选和原 Chrome 的 profile/state 卷均保留，yi 继续停止。',
                 f"[正常关闭与卷保留证据]({(HERE/'shutdown-evidence.json').as_posix()})。"])
(HERE / 'REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
print(json.dumps({'trials': len(rows), 'report': str(HERE / 'REPORT.md'), 'stage': stage['status']}))
