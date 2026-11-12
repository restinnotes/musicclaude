"""Offline incident audit. Reads safe timestamps only; never invokes a model."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'evaluations/d13_20261025'
DEST = Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs')
LOCAL = timezone(timedelta(hours=-4))

def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}

def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None

def iso(value):
    return value.astimezone(LOCAL).isoformat() if value else None

source = read(OUT / 'interruption_audit.json')
rows = []
for old in source['jobs']:
    if old['account'] != 'gpt4':
        continue
    directory = Path(old['result_path']).parent
    submitted = stamp(read(directory / 'submitted.json').get('utc'))
    posts = []
    request_file = directory / 'requests.jsonl'
    if request_file.exists():
        for line in request_file.read_text(encoding='utf-8-sig').splitlines():
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if item.get('method') == 'POST' and item.get('path') in ('/backend-api/f/conversation', '/backend-api/conversation'):
                posts.append({k: item.get(k) for k in ('utc', 'status', 'elapsed_seconds')})
    rows.append(dict(old, submitted_local=iso(submitted), generation_post_receipts=posts))

sent = sorted((r for r in rows if r['submitted_local']), key=lambda r: r['submitted_local'])
times = [stamp(r['submitted_local']) for r in sent]
gaps = [(b-a).total_seconds() for a, b in zip(times, times[1:])]
peaks = {}
for minutes in (1, 5, 15, 30, 60):
    best = max(((sum(t-timedelta(minutes=minutes) < p <= t for p in times), t) for t in times), key=lambda x:x[0])
    peaks[str(minutes)] = {'count':best[0], 'ending_local':iso(best[1]), 'window':'(end-window, end]'}

boundaries = {}
for code in ('ASYNC_TOPIC_REQUIRED', 'TOPIC_RECEIVE_TIMEOUT'):
    first = min((r for r in sent if r['code'] == code), key=lambda r:r['submitted_local'])
    t = stamp(first['submitted_local'])
    prior = [r for r in sent if stamp(r['submitted_local']) < t]
    boundaries[code] = {
        'job':first['job'], 'first_job_started_local':first['started_local'],
        'first_submission_marker_local':iso(t), 'local_result_recorded':first['result_local'],
        'prior_submission_markers':len(prior),
        'prior_windows':{str(m):sum(t-timedelta(minutes=m) <= stamp(r['submitted_local']) < t for r in prior) for m in (1,5,15,30)},
        'prior_local_receivers_not_ended':sum(not r['result_local'] or stamp(r['result_local'])>t for r in prior),
    }

cut = stamp(boundaries['ASYNC_TOPIC_REQUIRED']['first_submission_marker_local'])
before = [r for r in sent if stamp(r['submitted_local']) < cut]
after = [r for r in sent if stamp(r['submitted_local']) >= cut]
counts = lambda group:dict(Counter(r['code'] for r in group))
post_status = Counter(str(p['status']) for r in rows for p in r['generation_post_receipts'])
summary = {
    'updated_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'D13 primary account jobs in preserved 17:36:45–18:29:12 EDT incident snapshot; no new calls.',
    'user_investigation_assumption':'Treat takeover as start of suspect period; use frequent incomplete returns as incident signal, not proof of model downgrade.',
    'job_count':len(rows), 'submission_marker_count':len(sent),
    'first_submission_local':iso(times[0]), 'last_submission_local':iso(times[-1]),
    'submission_gaps_seconds':{'min':min(gaps),'median':statistics.median(gaps),'max':max(gaps),'below_4_9_seconds':sum(g<4.9 for g in gaps)},
    'peak_rolling_submission_windows_minutes':peaks,
    'first_incident_boundaries':boundaries,
    'before_first_async':counts(before),'from_first_async':counts(after),
    'generation_post_receipt_statuses':dict(post_status),
    'implementation_findings':[
        'evo.py MIN_GAP=7 uses a per-process threading.Lock, so separate scripts can start together.',
        'Actual pro-bridge generation path calls gpt3_sessions.pace_submission(account_hash) with a disk lock and default 5 second gap when retain_session is enabled.',
        'Submission-marker gaps, rather than process-start gaps, are the observed transmission-rate proxy.',
        'Pacing spaces submissions but does not cap the number of outstanding inference/reception jobs.',
    ],
    'limitations':[
        'submitted.json is written immediately before generation network invocation, not proof of backend acceptance or billing.',
        'A recorded HTTP 200 does not prove successful final assistant completion.',
        'ASYNC_TOPIC_REQUIRED means local client did not follow required topic stream; it does not establish server truncation.',
        'TOPIC_RECEIVE_TIMEOUT means no verified completion was received before local timeout; server outcome is not established.',
        'NO_COMPLETED_RESULT includes local cancellations, not confirmed server failures.',
        'Outstanding local receivers are not a measurement of simultaneous server inference.',
        'No time-aligned model-fingerprint baseline exists immediately before and after the incident; no downgrade threshold is established.',
        'This snapshot excludes later continuation and diagnostic jobs; it is not a whole-account daily usage total.',
    ],
}
audit = {'summary':summary,'jobs':rows}
(OUT/'frequency_incident_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')

# Preserve a hash manifest, without deleting or rewriting any experiment evidence.
files = []
for directory in (OUT, ROOT/'runs'):
    for path in sorted(directory.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in ('.txt','.json','.jsonl','.log'):
            continue
        if path.name.startswith(('frequency_incident_audit','quality_quarantine')):
            continue
        if directory == ROOT/'runs' and not path.parent.name.startswith('D13'):
            continue
        data = path.read_bytes()
        files.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
quarantine = {
    'updated_utc':summary['updated_utc'],'status':'suspended_pending_independent_review',
    'scope':'D13 provider-generated drafts, judges, mechanism/context/pool assessments produced after takeover on 2026-10-25.',
    'operational_action':'No promotion to accepted music output, no further music queue calls, preserve originals.',
    'evidence_policy':'Raw historical sources, PDFs, archives, hashes and mechanical audits remain evidence; model-authored assessments are provisional.',
    'not_established':'This status is not proof that every answer is poor or that frequency caused a model downgrade.',
    'baseline_package3':'Frozen original package3 remains unmodified; do not extrapolate to all earlier D10/D11/D12 artifacts.',
    'manifest_scope_note':'Snapshot of D13 text/JSON/log evidence at audit time, plus D13-prefixed run directories; active diagnostic evidence may later change.',
    'evidence_snapshot_files':files,
}
(OUT/'quality_quarantine.json').write_text(json.dumps(quarantine,ensure_ascii=False,indent=2),encoding='utf-8')

lines = [
    'D13 接手后调用频次与不完整回答核查（2026-10-25，美国东部夏令时）',
    '',
    '排查口径：按用户要求，从本次接手开始视为可疑期，以高频收不到完整回答定位故障；不把此假设写成已证实的模型降级机制。',
    '音乐队列已停止。本次脚本完全离线，没有发送新生成请求。',
    '',
    f'取证范围：首轮任务快照，{summary["first_submission_local"]} 至 {summary["last_submission_local"]}。',
    f'本地作业 {len(rows)} 个，带提交标记 {len(sent)} 个。',
    f'真实提交前标记的相邻间隔：最小 {min(gaps):.3f} 秒，中位数 {statistics.median(gaps):.3f} 秒。',
    '多个进程同时启动不等于请求同时提交。provider 的跨进程磁盘锁实施约 5 秒提交间隔；evo.py 的 7 秒锁仅作用于单个进程。',
    '', '滚动提交峰值：',
]
for minute, item in peaks.items():
    lines.append(f'{minute} 分钟：{item["count"]} 次；窗口截至 {item["ending_local"]}。')
lines += ['', '故障分界：']
for code, b in boundaries.items():
    lines += [f'{code}: 首个作业启动 {b["first_job_started_local"]}，提交标记 {b["first_submission_marker_local"]}，本地错误落盘 {b["local_result_recorded"]}。',
              f'此前累计提交标记 {b["prior_submission_markers"]}；之前 1/5/15 分钟分别为 '+ '/'.join(str(b['prior_windows'][str(m)]) for m in (1,5,15))+'。']
lines += [
    '',f'首个 ASYNC 之前：{counts(before)}。',f'首个 ASYNC 起：{counts(after)}。',
    'ASYNC_TOPIC_REQUIRED 9 次：接收端未跟随异步 topic，不能都算成后端已截断。',
    'TOPIC_RECEIVE_TIMEOUT 19 次：等待约 21 分钟仍无可核验最终回答。符合“未收到完整回答”排查信号，无法单靠此记录认定服务器已停止。',
    'NO_COMPLETED_RESULT 14 次：包含主动停止的任务，不计为已证实的服务器失败。',
    '',
    '判断：本次接手后的调用密度高，且该阶段出现集中接收失败。提交间隔控制没有限制在途任务总量，长任务可以堆积。频次/在途任务积压应列为首要嫌疑，但缺少故障前后同步指纹和服务端原因码，不能给出触发降级的确定阈值。',
    '耗时独立核查：成功音乐生成的墙钟中位数由故障前约 22.9 秒升至之后约 47.5 秒；现有数据不支持“返回耗时明显变短”。墙钟不等于内部思考耗时。',
    '处理：本次接手后 D13 的生成与模型评审均待独立复核；保留原始文件及哈希，不再据其分数推进实验。旧包3保持原样。',
    '', '证据与限制：', str(OUT/'frequency_incident_audit.json'), str(OUT/'quality_quarantine.json'),
] + summary['limitations']
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'D13_接手后频次与故障回溯_20261025.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('quarantined_manifest_files',len(files))
