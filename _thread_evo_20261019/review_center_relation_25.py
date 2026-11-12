"""Audit a doubtful relation label; do not confuse lack of attention with lack of clarity."""
import json
from concurrent.futures import ThreadPoolExecutor
import evo
import synth_v2
import finish_thread_25 as finish

if __name__=='__main__':
 key='C25whole60_op60'
 source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
 center=json.loads((finish.OUT/(key+'_center_candidates.json')).read_text(encoding='utf-8'))['options'][0]['text']
 rule='''请只核查Op60的S11（84–92）与已选Center的关系。三类严格沿用用户定义：正在面对=此刻实际在想、承受或处理核心困难；还说不清=感到牵动但尚不能辨明；没在想=沉浸于别的感受，核心问题暂时不在心上，即使因果上受历史影响。不设比例，也不强求出现某一类。
不能把分析者给出的History理由自动当成人物此刻给自己讲的道理。已经形成的理解不因不再主动想着就变成还说不清；同样，确实在承受核心问题也不要求人物主动说出一句概念化理解。请分别核对三种归类需要何种实际依据，允许否定先前评委把不在注意中心当成还说不清的做法，但不预设必须改成哪一类。
输出JSON：{"sec":"S11","relation":"三类之一","why":"具体理由","alternatives":[{"relation":"另一类","why_not":"具体依据"}],"analyst_vs_person":"哪些句子属于分析理由，哪些是当下实际体验"}。'''
 msg=rule+'\n【Center】'+center+'\n【完整已选综合】'+json.dumps([{ 'sec':sec,'chosen':s['chosen']} for sec,s in source['state'].items()],ensure_ascii=False)
 with ThreadPoolExecutor(max_workers=2) as ex:
  rs=list(ex.map(lambda m:finish.call(key+'_S11_relation_precision',msg,m),('g6','g56')))
 synth_v2.dump(finish.OUT/(key+'_S11_relation_precision.json'),dict(zip(('g6','g56'),rs)))
 print('S11 relation precision saved',flush=True)
