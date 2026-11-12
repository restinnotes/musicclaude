from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json

here = Path(__file__).resolve().parent
stage = json.loads((here/'stages-state.json').read_text(encoding='utf-8'))
rows = []
for key in ('baseline_batch','candidate_batch'):
    if not stage.get(key):
        continue
    batch = Path(stage[key])
    if not (batch/'results.jsonl').exists():
        continue
    for line in (batch/'results.jsonl').read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        run = Path(row['run_path'])
        record = json.loads((run/'diagnostics.json').read_text(encoding='utf-8'))
        files = (record.get('diagnostics',{}).get('screenshot_evidence') or {}).get('files',[])
        row['answer_view_capture_success'] = (record.get('diagnostics',{}).get('screenshot_evidence') or {}).get('answer_view_capture_success')
        row['screenshots_hash_verified'] = bool(files) and all(
            (run/'screenshots'/f['filename']).exists()
            and hashlib.sha256((run/'screenshots'/f['filename']).read_bytes()).hexdigest()==f['sha256']
            for f in files)
        rows.append(row)
fields = ['profile','sequence','started_new_york','completed_new_york','answer','response_complete',
          'error_type','actual_model','actual_effort','total_seconds','submit_to_complete_seconds',
          'thinking_time_ui_labels','screenshots_hash_verified','run_path']
with (here/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
(here/'results.json').write_text(json.dumps({'updated_utc':datetime.now(timezone.utc).isoformat(),
    'stage':stage,'trials':rows},ensure_ascii=False,indent=2),encoding='utf-8')
text = ['# yi 原 Chrome / 移植 Camoufox 水杯题对照', '', f"状态：{stage['status']}。", '',
    '同一个 yi 账号、同一道固定题面、GPT-5.6 Sol / 实际 Extra High，Temporary Chat + Unpersonalized。',
    '两组各计划 3 轮串行请求；正常轮间隔 10 秒。先关闭原 Chrome 再运行 Fox，没有同账号并发。',
    '用户指定正常答案为 8。这里报告完整回答的最终结论和探针匹配情况，不代表独立验证每份数学证明。', '',
    '|组别|轮次|开始（纽约）|结束（纽约）|答案 / 状态|总耗时 秒|提交至完成 秒|网页计时|实际档位|截图哈希一致|',
    '|---|---:|---|---|---|---:|---:|---|---|---|']
for row in rows:
    group = 'Chrome' if row['profile']=='yi' else 'Camoufox'
    answer = row['answer'] if row['response_complete'] else row['error_type']
    labels = ', '.join(row.get('thinking_time_ui_labels',[])) or '未取得'
    text.append(f"|{group}|{row['sequence']}|{row['started_new_york']}|{row['completed_new_york']}|{answer}|{row['total_seconds']}|{row['submit_to_complete_seconds']}|{labels}|{row['actual_effort']}|{row['screenshots_hash_verified']}|")
text.extend(['','总耗时含准备、输入、思考、输出和截图；提交至完成不含最终截图，包含思考和输出。网页 Worked for / Thought for 标签另外记录。', '', '## 实测判断',''])
answers = {}
for profile,label in [('yi','原 Chrome'),('yi-camoufox','Camoufox')]:
    answers[profile] = [r['answer'] for r in rows if r['profile']==profile and r['response_complete']]
    text.append(f"{label} 已完成答案：{answers[profile]}。")
if len(answers['yi'])==3 and len(answers['yi-camoufox'])==3:
    base,candidate=answers['yi'],answers['yi-camoufox']
    if any(a!=8 for a in base) and all(a==8 for a in candidate):
        text.append('本次原 Chrome 复现答案偏离 8，移植 Camoufox 三轮均为 8，支持这套浏览器方案在本次条件下改善了探针表现。样本仍只有各三次，不能保证以后稳定，也不能单独归因到防指纹或人工输入。')
    elif any(a!=8 for a in candidate):
        text.append('移植 Camoufox 后仍出现偏离 8 的完整答案；本次不能认定 Fox 解决了该探针异常。')
    else:
        text.append('两组均完整回答 8，本次没有复现 yi 原 Chrome 的探针异常。')
text.extend(['','## 原始证据',''])
for row in rows:
    run=Path(row['run_path'])
    path=run.as_posix()
    photo=run/'screenshots'/('response-answer.jpg' if row['response_complete'] else 'failure-viewport.jpg')
    if not photo.exists() and row['response_complete']:
        photo=run/'screenshots'/'response-viewport.jpg'
    if not photo.exists():
        photo=run/'docker-browser-last-observed.jpg'
    text.append(f"- {row['profile']} 第 {row['sequence']} 轮：[诊断]({path}/diagnostics.json)、[回答]({path}/response.txt)、[页面截图]({photo.as_posix()})、[全部截图目录]({path}/screenshots)。")
text.extend(['','## 实验条件与判断边界','',
    'Chrome 组基于原 yi 当前源码，仅加观测截图与私有 cookie 导出。候选沿用 yi 的登录诊断、5 秒全局发送间隔、完成检测及严格完整题面校验。',
    '候选参考 D:/grok-test/lij-grok-register-panel：Camoufox 0.5.4 / Gecko 152.0.4-beta.31，Windows 指纹、headed、humanize、geoip、en-US、block_webrtc，30–120ms 逐字输入并偶尔停顿；未加入代理池。',
    'Fox 使用独立 browser/state/log 卷，原 yi state 只读挂载导入授权 cookie；原 Chrome profile 不挂载。原 cookie 值与 API token 不写入镜像和实验结果。',
    '原 Chrome 容器内存限制 unlimited；Fox 为 2.5 GiB 内存加 1 GiB swap、shm 512 MiB。这一资源差异会影响耗时，不能把时间差全归因到浏览器。',
    '本实验一次替换浏览器引擎、指纹与输入行为，无法区分各因素贡献，也无法凭单题确认服务端实际模型或所谓降智根因。',
    '先前 shiyan 是另一账号和 High 档位，不与本次 yi / Extra High 混合统计。',
    'Chrome 的部分中文字体显示为方框，完整文本另存；JPEG 是浏览器实际截图，未编辑。'])
text.extend(['', 'Chrome 第 2 轮的自动最终截图停留在思考摘要，没有露出答案；完整答案 6 由 response.txt 与诊断保留。Fox 尝试在完成后追加滚到答案末尾的截图，初始截图同时保留。'])
for row in rows:
    if row['profile']=='yi-camoufox' and row['answer_view_capture_success'] is False:
        text.append(f"Fox 第 {row['sequence']} 轮追加末尾截图失败（定位超时），原始最终截图已保留；截图阶段 {row['screenshot_capture_seconds']} 秒，发生在模型完成计时之后，不能算作思考时间。")
for key,label in [('baseline_batch','Chrome'),('candidate_batch','Fox')]:
    if not stage.get(key):
        continue
    memory=Path(stage[key])/'memory.jsonl'
    if memory.exists():
        valid=[json.loads(l) for l in memory.read_text().splitlines() if 'memory_current_mib' in json.loads(l)]
        if valid:
            text.extend(['',f"{label} 每 30 秒资源采样：内存峰值 {max(r['memory_current_mib'] for r in valid):.2f} MiB，swap 峰值 {max(r['swap_mib'] for r in valid):.2f} MiB，末次事件 {valid[-1]['events']}。",
                         f"[资源记录]({memory.as_posix()})。" + ('Chrome 的观察从第 2 轮进行中开始，不覆盖第 1 轮。' if label=='Chrome' else '')])
for filename,label in [('original-shutdown-evidence.json','原 Chrome'),('shutdown-evidence.json','Fox')]:
    path=here/filename
    if path.exists():
        evidence=json.loads(path.read_text())
        text.extend(['',f"{label} 正常关闭确认：{evidence['browser_close_confirmed']}，容器 {evidence['container_status']}，OOMKilled={evidence['oom_killed']}。profile/state 卷保留。",
                     f"[关闭证据]({path.as_posix()})。"])
text.extend(['','## 登录观测',''])
for profile in ['yi','yi-camoufox']:
    path=here/(profile+'-auth-summary.json')
    if path.exists():
        auth=json.loads(path.read_text())
        text.append(f"{profile}：{len(auth['request_auth_preflights'])} 次发送前登录快照均保有 session cookie；记录到的 cookie 删除指令 {auth['auth_cookie_deletion_observations']} 次，401/403 观测 {len(auth['http_auth_or_access_errors'])} 次。[非秘密观测摘要]({path.as_posix()})。未观察到事件不等于覆盖了所有网络响应。")
(here/'REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print(json.dumps({'trials':len(rows),'report':str(here/'REPORT.md'),'status':stage['status']}))
