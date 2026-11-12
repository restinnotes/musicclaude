"""Read-only audit of backend completion evidence; never invokes a model."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter,defaultdict
import json,statistics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evaluations/d13_20261025'
LOCAL=timezone(timedelta(hours=-4)) # America/New_York on 2026-10-25.
START=datetime.fromisoformat('2026-10-25T17:36:45-04:00')
STOP=datetime.fromisoformat('2026-10-25T18:29:12.5864898-04:00')
def read(p):
 try:return json.loads(p.read_text(encoding='utf-8-sig'))
 except (OSError,ValueError):return {}
def dt(s):return datetime.fromisoformat(s.replace('Z','+00:00')) if s else None

rows=[]
for account in ('gpt4','gpt3'):
 for p in (Path('D:/musicclaude/gpt2agent-safechain/runs')/account).glob('pro-bridge-*'):
  if not 'pro-bridge-20261025T213645' <= p.name <= 'pro-bridge-20261025T222913':continue
  started=read(p/'started.json');beg=dt(started.get('utc'))
  if not beg or not START<=beg<=STOP:continue
  result=read(p/'result.json');end=dt(result.get('utc'));gn=read(p/'generation-network.json');tn=read(p/'topic-network.json')
  code='SUCCESS' if result.get('ok') is True and (p/'response.txt').exists() else result.get('code','NO_COMPLETED_RESULT')
  rows.append({'account':account,'job':p.name,'started_local':beg.astimezone(LOCAL).isoformat(),
   'submitted':(p/'submitted.json').exists(),'result_local':end.astimezone(LOCAL).isoformat() if end else None,
   'code':code,'seconds':result.get('elapsed_seconds'),'response_file_present':(p/'response.txt').exists(),
   'http_status':gn.get('status'),'first_chunk_ms':gn.get('first_chunk_ms'),'initial_segment_ms':gn.get('elapsed_ms'),
   'initial_segment_done_seen':gn.get('done_seen'),'topic_subscribed':tn.get('subscribed'),
   'topic_terminal_seen':tn.get('terminal_seen'),'topic_done_control_seen':tn.get('done_control_seen'),
   'topic_elapsed_ms':tn.get('elapsed_ms'),'topic_frames':tn.get('frames'),'topic_ignored_control_frames':tn.get('ignored_control_frames'),
   'result_path':str(p/'result.json')})
rows.sort(key=lambda x:x['started_local'])
primary=[r for r in rows if r['account']=='gpt4']
bins=defaultdict(Counter)
for r in primary:
 t=dt(r['started_local']);label=t.replace(minute=t.minute//5*5,second=0,microsecond=0).strftime('%H:%M')
 bins[label][r['code']]+=1
stats={}
for code in ('ASYNC_TOPIC_REQUIRED','TOPIC_RECEIVE_TIMEOUT'):
 group=[r for r in primary if r['code']==code];dur=[r['seconds'] for r in group if isinstance(r['seconds'],(float,int))]
 stats[code]={'count':len(group),'first_start':group[0]['started_local'] if group else None,'last_start':group[-1]['started_local'] if group else None,
  'duration_seconds':{'min':min(dur),'median':statistics.median(dur),'max':max(dur)} if dur else None}
summary={'scope':'Actual backend jobs started during this D13 task; client stopped 18:29:12 EDT. No new calls.',
 'primary_account':dict(Counter(r['code'] for r in primary)),
 'primary_submitted':sum(r['submitted'] for r in primary),'all_account_jobs':len(rows),
 'alternate_account':dict(Counter(r['code'] for r in rows if r['account']=='gpt3')),
 'incomplete_response_counts':stats,'primary_by_start_5_minute':{k:dict(v) for k,v in sorted(bins.items())},
 'limitations':['Submission marker does not prove server acceptance/billing.','NO_COMPLETED_RESULT includes tasks stopped locally; never count as proven server failure.','Initial SSE DONE is a segment boundary, not final assistant completion.','Reception/worker timeout does not prove what happened in official webpage UI.']}
(OUT/'interruption_audit.json').write_text(json.dumps({'summary':summary,'jobs':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('TIMEOUT DETAILS')
for r in primary:
 if r['code'] in ('ASYNC_TOPIC_REQUIRED','TOPIC_RECEIVE_TIMEOUT'):print(json.dumps(r,ensure_ascii=False))
