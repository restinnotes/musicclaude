"""Offline whole-thread/day audit; no model, network, or credential access."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib
import json
import sqlite3
import statistics

ROOT = Path(__file__).resolve().parent
BASE = Path('D:/musicclaude/gpt2agent-safechain')
OUT = ROOT/'evaluations/d13_20261025'
DEST = Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs')
SESSION = Path('C:/Users/zuoyi/.codex/sessions/2026/10/25/rollout-2026-10-25T00-44-54-01a17160-3aef-74b0-b14c-fb2952333ec3.jsonl')
TZ = ZoneInfo('America/New_York')
NOW = datetime.now(timezone.utc)

def read(path):
    try:return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):return {}

def epoch(text):
    return datetime.fromisoformat(text.replace('Z','+00:00')).timestamp() if text else None

def local(t):
    return datetime.fromtimestamp(t,TZ).isoformat() if t is not None else None

def counts(rows,key):return dict(Counter(r.get(key) for r in rows))

def peak(times,seconds):
    best=(0,None);left=0
    for right,t in enumerate(times):
        while times[left]<=t-seconds:left+=1
        if right-left+1>best[0]:best=(right-left+1,t)
    return {'count':best[0],'ending_local':local(best[1])}

# Scan every preserved session line, including the pre-compaction portion.
visible=[];commands=[];type_counts=Counter();first_request=None;early_failure_comment=None
line_count=0
for line_count,line in enumerate(SESSION.open(encoding='utf-8'),1):
    try:j=json.loads(line)
    except ValueError:continue
    q=j.get('payload',{});type_counts[j.get('type')]+=1;t=epoch(j.get('timestamp'))
    if j.get('type')=='response_item' and q.get('type')=='message' and q.get('role') in ('user','assistant'):
        text='\n'.join(x.get('text','') for x in q.get('content',[]) if isinstance(x,dict))
        if not text or (q.get('role')=='user' and text.lstrip().startswith(('<environment_context>','<external_codex_apps_open_page>','<subagent_notification>'))):continue
        visible.append({'session_line':line_count,'local_time':local(t),'role':q['role'],'text':text})
        if q['role']=='user' and first_request is None:first_request=visible[-1]
        if q['role']=='assistant' and '一份旧版本评审遇到上游流错误' in text:early_failure_comment=visible[-1]
    if j.get('type')=='event_msg' and q.get('type')=='item_completed':
        item=q.get('item',{})
        if item.get('type')=='CommandExecution':
            command=str(item.get('command',''))
            commands.append({'session_line':line_count,'recorded_local':local(t),'cwd':item.get('cwd'),
                             'exit_code':item.get('exit_code'),'duration':item.get('duration'),
                             'command_sha256':hashlib.sha256(command.encode()).hexdigest(),
                             'mentions_project': '_thread_evo_20261019' in command or '_thread_evo_20261019' in str(item.get('cwd','')),
                             'mentions_model_entry': any(x in command for x in ('gpt4','gpt3','THREAD_GPT'))})

start=datetime(2026,10,25,tzinfo=TZ).timestamp()
db=sqlite3.connect((BASE/'state/usage.sqlite3').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
ledger={r['job']:dict(r) for r in db.execute('SELECT * FROM calls WHERE started>=? AND started<=?',(start,NOW.timestamp()))}
db.close()
run_logs={}
for line in (ROOT/'runs/calls.jsonl').open(encoding='utf-8'):
    try:r=json.loads(line)
    except ValueError:continue
    if r.get('job_directory'):run_logs[Path(r['job_directory']).name]=r

rows=[]
for entry in ('gpt4','gpt3'):
    for directory in (BASE/'runs'/entry).glob('pro-bridge-20261025*'):
        began=epoch(read(directory/'started.json').get('utc'))
        if began is None or not start<=began<=NOW.timestamp():continue
        result=read(directory/'result.json');submitted=epoch(read(directory/'submitted.json').get('utc'))
        key=hashlib.sha256(str(directory.resolve()).casefold().encode()).hexdigest();usage=ledger.get(key,{})
        log=run_logs.get(directory.name,{})
        success=result.get('ok') is True and (directory/'response.txt').is_file()
        rows.append({'entry':entry,'job':directory.name,'job_directory':str(directory),
                     'started_epoch':began,'started_local':local(began),'submitted_epoch':submitted,'submitted_local':local(submitted),
                     'finished_local':local(epoch(result.get('utc'))),'seconds':result.get('elapsed_seconds'),
                     'code':'SUCCESS' if success else result.get('code','NO_COMPLETED_RESULT'),
                     'ledger_code':usage.get('code'),'ledger_outcome':usage.get('outcome'),
                     'model':result.get('model') or usage.get('model'),'run_id':log.get('run_id'),
                     'caller':usage.get('caller'),'account_sha256':usage.get('account_sha256')})
rows.sort(key=lambda r:r['started_epoch'])
primary=[r for r in rows if r['entry']=='gpt4']
morning=[r for r in primary if r['started_epoch']<datetime(2026,10,25,4,tzinfo=TZ).timestamp()]
evening=[r for r in primary if r not in morning]
def stats(group):
    times=sorted(r['submitted_epoch'] for r in group if r['submitted_epoch'] is not None)
    gaps=[b-a for a,b in zip(times,times[1:])]
    return {'jobs':len(group),'submitted':len(times),'first_job_local':group[0]['started_local'] if group else None,
            'last_job_local':group[-1]['started_local'] if group else None,'first_submission_local':local(times[0]) if times else None,
            'last_submission_local':local(times[-1]) if times else None,'codes':counts(group,'code'),'models':counts(group,'model'),
            'peak_rolling_minutes':{str(m):peak(times,m*60) for m in (1,5,15,30,60)},
            'submission_gap_median_seconds':statistics.median(gaps) if gaps else None}

first_bad=next(r for r in primary if r['code'] not in ('SUCCESS','NO_COMPLETED_RESULT','LOCAL_TRANSPORT_FAILURE'))
first_async=min((r for r in primary if r['code']=='ASYNC_TOPIC_REQUIRED'),key=lambda r:r['submitted_epoch'])
def prior_boundary(row):
    t=row['submitted_epoch'];prior=[r for r in primary if r['submitted_epoch'] is not None and r['submitted_epoch']<t]
    return {'job':row['job'],'started_local':row['started_local'],'submitted_local':row['submitted_local'],
            'finished_local':row['finished_local'],'code':row['code'],'seconds':row['seconds'],
            'prior_same_account_submissions':len(prior),
            'prior_rolling_minutes':{str(m):sum(t-m*60<=r['submitted_epoch']<t for r in prior) for m in (1,5,15,60,180)}}

summary={
    'updated_utc':NOW.isoformat(),'timezone':'America/New_York',
    'coverage':'Entire preserved current-thread JSONL from first user request, plus all today gpt4/gpt3 pro-bridge jobs and read-only usage ledger reconciliation.',
    'session_path':str(SESSION),'session_lines_scanned':line_count,'record_type_counts':dict(type_counts),
    'first_user_request_local':first_request['local_time'],'first_user_request_line':first_request['session_line'],
    'visible_message_count':len(visible),'command_event_count':len(commands),
    'primary_today':stats(primary),'morning':stats(morning),'evening_and_diagnostics':stats(evening),
    'earliest_verified_noncompletion':prior_boundary(first_bad),
    'first_evening_async_boundary':prior_boundary(first_async),
    'morning_evening_same_account_hash':set(r['account_sha256'] for r in morning)==set(r['account_sha256'] for r in evening),
    'ledger_failure_but_backend_success_count':sum(r['ledger_outcome']=='failure' and r['code']=='SUCCESS' for r in primary),
    'morning_ledger_failure_but_backend_success_count':sum(r['ledger_outcome']=='failure' and r['code']=='SUCCESS' for r in morning),
    'other_entry':stats([r for r in rows if r['entry']=='gpt3']),
    'other_entry_same_account_as_primary':bool(set(r['account_sha256'] for r in rows if r['entry']=='gpt3') & set(r['account_sha256'] for r in primary)),
    'early_noncompletion_progress_message':early_failure_comment,
    'corrections':[
        'Previous 245-submission report covered only the evening D13 batch, not the whole conversation.',
        '17:54 is an evening failure-cluster boundary, not the earliest failure or the takeover time.',
        'Morning jobs submitted 00:50–02:45 and the delivered package3 continuation outputs must be included in the suspect-period review.',
        'Old latency comparison used only evening D13 tasks, so it does not answer morning-versus-evening quality or reasoning-time change.',
        'Ledger LOCAL_EXCEPTION records alone are not noncompletion evidence when backend result and response prove completion.',
    ],
    'limitations':[
        'No continuous model-fingerprint or server-side compute-budget record exists for the day.',
        'Complete transport return does not prove music quality or requested model identity.',
        'One morning stream error is established; frequent morning noncompletion is not supported by preserved backend outcomes.',
        'Calling project/account association does not measure unrecorded official website or other-device use.',
        'Submission marker precedes network transmission; it is not a billing or inference acceptance receipt.',
        'Pending and locally stopped jobs are not counted as confirmed server failures.',
        'Early and late tasks/models/prompt designs differ, so raw latency comparison is confounded.',
        'Current finite diagnostic third GPT6 probe was already pending; this audit makes no new generation requests.',
    ],
}
(OUT/'whole_thread_frequency_audit.json').write_text(json.dumps({'summary':summary,'jobs':rows},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'whole_thread_visible_timeline.json').write_text(json.dumps({'messages':visible,'command_event_metadata':commands},ensure_ascii=False,indent=2),encoding='utf-8')

# Expand the review scope to morning deliverables while preserving frozen archives.
artifacts=[]
for name in ['Thread_包3_从最新计划开始的全过程与最终产物_20261025.zip','Op60_船歌_Thread.txt','Op61_幻想波兰舞曲_Thread.txt']:
    p=DEST/name
    if p.is_file():artifacts.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
quarantine={
    'updated_utc':NOW.isoformat(),'status':'pending_independent_review',
    'scope_start_local':first_request['local_time'],
    'scope':'All model-derived continuation results and acceptance conclusions produced by this thread today, including morning two-work Thread deliverables, continuation_20261025 and evening D13.',
    'preserved_artifacts':artifacts,
    'archive_policy':'Package3 ZIP remains byte-for-byte unchanged. Its morning continuation and acceptance claims are provisional; original historical records remain source evidence.',
    'meaning':'Conservative review status, not proof all outputs are low quality or all calls used a downgraded model.',
    'audit_path':str(OUT/'whole_thread_frequency_audit.json'),
}
(OUT/'whole_thread_quality_review_status.json').write_text(json.dumps(quarantine,ensure_ascii=False,indent=2),encoding='utf-8')

m=summary['morning'];e=summary['evening_and_diagnostics'];b=summary['earliest_verified_noncompletion'];a=summary['first_evening_async_boundary']
lines=[
    '整个对话频次与故障回溯：修正版（2026-10-25，纽约时间）','',
    '纠正：此前245次统计仅覆盖17:36后的D13首轮，不是整个对话；17:54不是接手时间，也不是今天最早的接收失败。',
    f'扫描本对话原始JSONL共{line_count}行，覆盖压缩前记录；首个用户请求 {first_request["local_time"]}。',
    '底层证据：全部当日gpt4/gpt3 pro-bridge任务目录、只读usage.sqlite3、runs/calls.jsonl。此次没有发送新模型请求。','',
    f'凌晨：{m["first_job_local"]}—{m["last_job_local"]}，{m["jobs"]}个任务，{m["submitted"]}次提交；结果{m["codes"]}。',
    f'凌晨模型分布：{m["models"]}。',
    '凌晨滚动峰值：'+ '；'.join(f'{k}分钟{v["count"]}次' for k,v in m['peak_rolling_minutes'].items())+'。',
    f'最早明确未完成：{b["started_local"]}启动，{b["submitted_local"]}提交，{b["finished_local"]}记录UPSTREAM_STREAM_ERROR；约{b["seconds"]}秒，未返回最终正文。',
    f'该次之前累计已提交{b["prior_same_account_submissions"]}次。',
    f'凌晨另有{summary["morning_ledger_failure_but_backend_success_count"]}条账本LOCAL_EXCEPTION，但底层result/response核实成功，不能算作截断。',
    '',
    f'傍晚与后续诊断：{e["jobs"]}个主账号任务，{e["submitted"]}次提交，结果{e["codes"]}。',
    f'凌晨和傍晚账号哈希一致：{summary["morning_evening_same_account_hash"]}。',
    f'傍晚异步失败集中起点（按提交）：{a["submitted_local"]}；此前当日同账号累计{a["prior_same_account_submissions"]}次提交，包含凌晨{m["submitted"]}次。',
    f'全天截至本次快照：主账号{summary["primary_today"]["jobs"]}个任务、{summary["primary_today"]["submitted"]}次提交。',
    '04点、10点、16点另有其他入口的请求，账号哈希不同，单列，不合并到本账号负载。','',
    '判断：凌晨已经有高密度调用和一次明确上游流错误；现有记录不支持“凌晨已频繁不完整返回”。大规模接收失败聚集在傍晚。因而不能把凌晨产物当作故障前已验证的健康基线，也不能凭完整返回就认定质量正常。',
    '频次仍是重点嫌疑，但没有故障前后的同步指纹、受控质量对照和服务端原因码，不能认定第N次调用触发了降级。',
    '此前23秒→47秒的耗时比较只涉及傍晚D13，不能回答凌晨与傍晚的质量差异。凌晨主要为GPT6评审，傍晚主要为GPT5.6生成/评审，任务构成不同。','',
    '处理：扩大待复核范围到凌晨两首成稿及其验收结论、包3中的本次续作、傍晚D13。冻结ZIP不改写；历史原始记录仍作为证据。',
    '详细数据：'+str(OUT/'whole_thread_frequency_audit.json'),
    '完整可见消息与命令事件索引：'+str(OUT/'whole_thread_visible_timeline.json'),
    '扩大复核状态：'+str(OUT/'whole_thread_quality_review_status.json'),
]
(DEST/'整个对话_凌晨至今频次与故障回溯_20261025.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
(DEST/'Thread_包3_质量复核状态更新_20261025.txt').write_text('包3中的本次Codex凌晨续作及模型验收结论现均列为待独立复核，不能再视作已验证的健康基线。ZIP保持原样；原始历史记录和过程证据继续保留。\n详见：整个对话_凌晨至今频次与故障回溯_20261025.txt\n',encoding='utf-8-sig')
previous=DEST/'D13_接手后频次与故障回溯_20261025.txt'
if previous.exists():
    old=previous.read_text(encoding='utf-8-sig')
    marker='【范围纠正：本文件仅统计傍晚D13首轮；全对话修正版见 整个对话_凌晨至今频次与故障回溯_20261025.txt】'
    if not old.startswith(marker):previous.write_text(marker+'\n\n'+old,encoding='utf-8-sig')
print(json.dumps(summary,ensure_ascii=False,indent=2))
