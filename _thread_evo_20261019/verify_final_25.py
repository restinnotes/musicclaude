"""Final semantic check of an immutable full graph; concise evidence, unchanged standards."""
import copy,json,hashlib,sys
from concurrent.futures import ThreadPoolExecutor
import evo,synth_v2
import finish_thread_25 as f

key=sys.argv[1];work=key.rsplit('_',1)[1]
p=f.OUT/(key+'_plain.json');raw=p.read_bytes();g=json.loads(raw)
source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
src=[{'sec':sec,'chosen':st['chosen'],'hist':st['hist'],'fate':st['pick']['fate']} for sec,st in source['state'].items()]
review=copy.deepcopy({'segments':g['segments']})
for s in review['segments']:
 s['bead_dispositions']=[{k:b[k] for k in ('original','author_disposition')} for b in s['bead_dispositions']]
scope='肖邦《船歌》Op.60，14段' if work=='op60' else '肖邦《幻想波兰舞曲》Op.61，13段'
instruction=f.VERIFY.replace('逐段写原有实质内容与图中对应条目，遗漏不靠想象替图补回。','逐段核查全部原有实质内容，遗漏不靠想象替图补回。retained每段用1–2条紧凑列出最关键的核对证据；核查范围仍是全部内容，不得因输出紧凑而省略检查。')
msg=instruction+'\n【范围】本次只验收'+scope+'。另一首不在本次任务内，不得将缺另一首判成本次缺陷。完整源稿与交付图均如下。核查最终实物，不依赖其他评审结论。\n【原始综合】'+json.dumps(src,ensure_ascii=False)+'\n【最终人话关系图及独立记录】'+json.dumps(review,ensure_ascii=False)
with ThreadPoolExecutor(max_workers=2) as ex:rs=list(ex.map(lambda m:f.call(key+'_final_verify',msg,m),('g6','g56')))
if p.read_bytes()!=raw:raise ValueError('Graph changed during final review')
result=dict(zip(('g6','g56'),rs))
for model,r in result.items():
 if [s['sec'] for s in r['segments']]!=list(source['state']):raise ValueError('Incomplete review inventory')
 if r.get('pass') and (r.get('arrow_problems') or r.get('problems') or any(s.get('missing') or s.get('invented') for s in r['segments'])):raise ValueError('Contradictory positive verdict')
synth_v2.dump(f.OUT/(key+'_final_verify.json'),result)
synth_v2.dump(f.OUT/(key+'_final_verify_receipt.json'),{'graph_sha256':hashlib.sha256(raw).hexdigest(),'models':['g6','g56'],'scope':scope,'complete_input':True})
print(key,{m:r['pass'] for m,r in result.items()},flush=True)
