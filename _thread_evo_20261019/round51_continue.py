"""Second batch: carry forward prior understanding, or defer premature closure.
Frozen requests; collection never applies edits.
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV','2')
import experiment_batch as B
import round50_continue as R
import e2e_open as O

ROOT=B.ROOT/'runs/_batches/round51_from_r49b'
FOCUS={
 'carry':'只检验已经经历过、明白过的内容在后续压力中是否真正起作用：相近的顾虑回来时，前面得到的认识或已经作出的选择仍应存在，新的困难由此长出来，而不是把那件事从头再想一遍。优先修必要的承接或重分已有条目作用，不另列账本，不每段硬塞新认识，不把回返本身当缺点。保留具体的相互关系、归属和所求，不用泛泛亲近替掉已有实质内容。结尾最终选择不改。',
 'closure':'只检验中途是否过早写得像已经彻底想通、问题已经解决或最终选择已经做完，以致后面的犹疑像倒带。分清当下的一次轻松、某个具体念头的变化与最终选择，让后面的压力由仍未安定的具体所求推动，真正收束留给已有结尾。不一律加暂时、不把全篇降成模糊迟疑、不人为推迟已经成立的认识。保留回返中实际不同的处境，不为建立路线新编事件。结尾最终选择不改。'
}

def prepare():
 ROOT.mkdir(parents=True,exist_ok=True)
 tasks=[]
 for mode,focus in FOCUS.items():
  for draw in (1,2):
   tag=f'r51{mode}{draw}'
   for w in B.F.WORKS:
    feedback=[]
    for j in ('g6','g56','gem'):
     for k in ((1,) if j=='gem' else (1,2)):
      rid=f'eo2_{w}_r49b_{j}_r{k}'
      if not B.reviewed(rid):raise ValueError('unread I01: '+rid)
      feedback.append({'run':rid,'raw':B.evo.output(rid)})
    evidence={'full_current_I01':feedback,'executor_boundaries':'保留原评审评级与分歧。建议不是标准：不按小节长度规定字数，不采用每段一条，不追求特定审美的崇高/史诗/能量量级，不新增具体动作/对白/前史；这些建议与原硬约束不合时不采用。R50把相互需要改成仅被接纳、把被当自己人改成泛亲近的两套依据机制已失败；不能把删除具体关系当成本批目的。'}
    msg=R.PROMPT.format(FOCUS=focus,LINE=B.V.view(B.V.graph_of(w,'r49b'),ids=True),BEADS=B.V.beads(w),REVIEWS=B.json_text(evidence))
    rid=f'sc{tag}_{w}_A5'
    B.write_frozen(B.evo.RUNS/rid/'prepared_input.txt',msg)
    tasks.append({'tag':tag,'work':w,'mode':mode,'draw':draw,'rid':rid,'sha256':B.digest(msg)})
 manifest={'base':'r49b','mainline_comparison':'compare each candidate with the then-accepted mainline; do not presume old-fork improvements are cumulative','hypotheses':FOCUS,'tasks':tasks,'base_hashes':{w:B.digest((B.V.OUT/f'{w}_r49b.json').read_text(encoding='utf-8')) for w in B.F.WORKS}}
 B.write_frozen(ROOT/'manifest.json',B.json_text(manifest))
 print('Frozen',len(tasks),'requests; no calls')

def collect(route='mimic'):
 import msvcrt,mg_schedule
 os.environ['THREAD_ROUTE']=route;B.F.configure()
 m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
 assert all(B.digest((B.V.OUT/f'{w}_r49b.json').read_text(encoding='utf-8'))==h for w,h in m['base_hashes'].items())
 with (ROOT/'receiver.lock').open('a+') as lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
  def one(t):
   msg=(B.evo.RUNS/t['rid']/'prepared_input.txt').read_text(encoding='utf-8');assert B.digest(msg)==t['sha256']
   if not B.evo.done(t['rid']):
    try:
     state=mg_schedule.status()
     if state['cooling'] and state.get('cooldown_kind')=='suspicious_behavior':mg_schedule.check()
     r=B.evo.call(t['rid'],msg,model=B.evo.G6,meta={'stage':'r51_local_revision','web':True})
    except mg_schedule.CoolingDown as exc:return {**t,'status':'cooldown','reason':str(exc)}
    if not r:return {**t,'status':'incomplete_inspect_original_receiver'}
   return {**t,'status':'full_read_required'}
  with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(one,m['tasks']))
  (ROOT/'collection_result.json').write_text(B.json_text({'terminal':True,'tasks':rows}),encoding='utf-8');print(B.json_text(rows),flush=True)

if __name__=='__main__':
 import sys
 prepare() if sys.argv[1]=='prepare' else collect(sys.argv[2] if len(sys.argv)>2 else 'mimic')
