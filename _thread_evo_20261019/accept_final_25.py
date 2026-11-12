"""Explicit main acceptance after reading both final judgments. Fail closed on unresolved defects."""
import copy,hashlib,json
from pathlib import Path
import evo,synth_v2,judge_synth_v4
import finish_thread_25 as f

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reduced(g):
 r=copy.deepcopy({'segments':g['segments']})
 for s in r['segments']:
  s['bead_dispositions']=[{k:b[k] for k in ('original','author_disposition')} for b in s['bead_dispositions']]
 return r

def bind(key,model,review,graph,source):
 matches=[]
 for p in evo.RUNS.glob('finish25_'+key+'*verify_*/output.txt'):
  try:
   if judge_synth_v4.parse(p.read_text(encoding='utf-8'))!=review:continue
   rec=load(p.parent/'call.log')
   requested=evo.G6 if model=='g6' else evo.G56
   if '--model '+requested not in rec['command']:continue
   msg=(p.parent/'input.txt').read_text(encoding='utf-8-sig')
   marker=next(x for x in ['【最终人话关系图及独立记录】','【人话关系图及独立保留记录】'] if x in msg)
   actual,_=json.JSONDecoder().raw_decode(msg.split(marker,1)[1].lstrip())
   if actual!=reduced(graph):continue
   original,_=json.JSONDecoder().raw_decode(msg.split('【原始综合】',1)[1].lstrip())
   expected=[{'sec':sec,'chosen':st['chosen'],'hist':st['hist'],'fate':st['pick']['fate']} for sec,st in source['state'].items()]
   assert [{k:v for k,v in s.items() if k!='bars'} for s in original]==expected
   matches.append({'run_id':p.parent.name,'model':requested,'input_sha256':sha(p.parent/'input.txt'),'output_sha256':sha(p),'graph_and_source_match':True})
  except (ValueError,KeyError,StopIteration):continue
 if len(matches)!=1:raise ValueError(('Missing or ambiguous final judgment binding',key,model,matches))
 return matches[0]

works={};bindings=[]
for work,tag,filename in [('op60','C25whole60','C25whole60_op60_final_verify.json'),('op61','C25op61body2','C25op61body2_op61_verify_repaired.json')]:
 key=tag+'_'+work;gp=f.OUT/(key+'_plain.json');sp=evo.ROOT/f'evaluations/synth/{key}/run.json'
 g=load(gp);s=load(sp);rp=f.OUT/filename;reviews=load(rp)
 review_graph=g
 post_review={}
 if work=='op60':
  post_review=load(f.OUT/(key+'_post_review_main_change.json'))
  before_path=evo.ROOT/post_review['before_graph_path']
  assert sha(before_path)==post_review['before_sha256'] and sha(gp)==post_review['after_sha256']
  review_graph=load(before_path)
  expected=copy.deepcopy(review_graph)
  next(z for z in expected['segments'] if z['sec']==post_review['sec'])['because'].remove(post_review['removed_edge'])
  assert expected==g and post_review['only_change']=='delete_one_redundant_cross_edge'
 assert set(reviews)=={'g6','g56'}
 for m,r in reviews.items():
  assert r['pass'] is True and not r['problems'] and not r['arrow_problems'],(key,m)
  assert [z['sec'] for z in r['segments']]==list(s['state'])
  assert all(not z['missing'] and not z['invented'] and z['retained'] for z in r['segments'])
  bindings.append(bind(key,m,r,review_graph,s))
 candidates=load(f.OUT/(key+'_center_candidates.json'));cr=load(f.OUT/(key+'_center_reviews.json'))
 center=next(x['text'] for x in candidates['options'] if x['id']=='C1')
 for r in cr.values():assert next(x['pass'] for x in r['options'] if x['id']=='C1')
 relations=copy.deepcopy(next(x['relations'] for x in cr['g6']['options'] if x['id']=='C1'))
 relation_review={'basis':'Main read both independent full Center reviews against the completed source and final graph. No quotas; analyst explanations are not attributed as conscious self-talk.'}
 if work=='op60':
  focus=load(f.OUT/(key+'_S11_relation_precision.json'))
  assert all(x['relation']=='正在面对' for x in focus.values())
  relations[next(i for i,r in enumerate(relations) if r['sec']=='S11')]={'sec':'S11','relation':'正在面对','why':focus['g6']['why']}
  relation_review['S11_supersedes_initial_label']=focus
 relation_review['final_graph_comparison']='Final repairs restore existing source distinctions and remove weak edges; they do not replace the selected story, whole-work Center basis or attention states. Center selected only after completion of this graph.'
 works[work]={'source_tag':tag,'source_sha256':sha(sp),'graph_path':gp.relative_to(evo.ROOT).as_posix(),'graph_sha256':sha(gp),'fidelity_review_path':rp.relative_to(evo.ROOT).as_posix(),'fidelity_review_sha256':sha(rp),'post_review_main_change':post_review,'center':center,'center_option':'C1','relations':relations,'relation_review':relation_review}

report='''本次续作与验收记录

续接的是 Claude Code 的真实本地会话，不是 Claude Proxy。原始 JSONL：
C:\\Users\\zuoyi\\.claude\\projects\\D--musicclaude\\7c623294-a1ea-40eb-b513-ae6588ad2c39.jsonl
对应项目：D:\\musicclaude\\_thread_evo_20261019
已读出实际对话并核查最新任务、规范、计划及历史样例，从 D12 已完成的后台结果接续。

本次交付两首完整 Thread：《船歌》Op.60，1–116小节、14段；《幻想波兰舞曲》Op.61，1–288小节、13段。可读版包含事后归纳的 Center、逐段与 Center 的关系、同段因果和确实起作用的跨段历史关系。完整 JSON 另含全部原始珠子、去处、完整候选解释池、选中解释、History、验收及可追溯来源。

流程已做到：无珠子完整草稿与双评覆盖 → 持久解释池 → 依原珠子、当前解释池和此前 History 逐段综合 → 关系图 → 保真人话 → 最后归纳 Center。候选解释未按名额删减，替代听法没有被强编成人物必经心理步骤。

《船歌》的关键修订是：S03保留舒服、短暂急切和暗流同时存在；S04明确同样亲近第二次为何反而更难安定；S05写出原有支撑失效；S06的独自快乐在S07及后文确实起作用；S11保留24–34至84–92的延迟释放；S12让早期相伴的安稳与40–61的另一种快乐真正相遇，解释自身得失退后，并保留狂喜中同时的心疼与恳求；S13明确满足已经得到，而依恋与向前冲动仍未平息。

《幻想波兰舞曲》的关键修订是：S01保留无明确对象的恍惚、尊严与想歇下；S02力量与脆弱共存，控制因眷恋未减而越来越费力；S04把反复追问的心理压力与被时间催着走的身体压力分开，分别建立原因与History；这次改变后，S04–S13的局部验收、相关全局检查及选中候选的解释审计均重新进行。S06愿望逐渐敞开、更迫切但尚未完成；S07保持异质突然打断，不把音乐材料身份硬写成人物事件；S13由实际前史使柔软成为力量，保留失落没有消失。

两首各有3个Center候选，两份独立评审均仅接受C1。最后选择：
Op.60：与对方相伴的幸福已经真实发生，却既留不住正在过去的时光，也不能由他独自保证以后。
Op.61：曾珍惜的生活不能原样回到现在，对它的牵挂却既支撑着他，也让他难以安顿。
Op.60 S11初评把“没有主动概念化”误等同于“还说不清”，经专项双评与主审改为“正在面对”：当下确实承受不舍和心疼，并非只有分析者在讲历史原因。其他段落也不按比例分配三类关系。

验收保留了实际失败与修订过程。两首27个段落的局部检查、9个全局检查点及全部候选解释审计已核查。最终关系图分别经过两份独立保真验收，主审阅读其实际理由，并逐一处理内容缺失和无效箭头；没有用单独一个pass字段替代内容判断。早期退稿、批评、修订前文件和上游流错误全部保留；无正文的调用不算通过。模型回收按实际提示词、附件和模型匹配，核对实际任务中的模型与max思考、提示词和回答，不把另一模型的回答挪作评审。

103颗非演奏条件珠子的最终独立去处为：95颗被解释、6颗相容且独立保留、2颗作为另一读法保留；另有3颗演奏条件珠子原文保留。Op.60为48解释、1相容、1替代；Op.61为47解释、5相容、1替代。未报告“全部103颗均被主线解释”。全部106颗原始珠子逐字保留在完整记录中。

阅读符号：每段条目依次阅读；→只标真正因果或心理推出；←给出更早小节的真实历史作用，关系可为提供理由、动摇、限制、改写、唤起。“改写”指后来经验改变早先的意义或作用，不指换一种说法。单纯先后、相似、指代或阶段重复不连箭头。人物的比喻不实化为真实对白、重逢、拥抱等事件，分析者的因果解释不自动变成人物主动想通。

《船歌》的两份完整正向保真评审针对最后删边前的版本。其后主审依据另一份已返回的独立批评，仅删除S09 I48→S12 I63这条重复价值判断的箭头；没有改动任何条目文字、同段关系、珠子、来源、History或其他边。删边前文件、两份原始正向评审、批评与精确差分全部保存，交付记录明确区分“完整双评”与“之后主审单项删边”，不将原始评审伪装成针对后来不同文件的回执。

本次验收范围是这两首作品的最终具体稿；包含有记录的人工修订。它证明目前这两份交付经完整核对后可用，尚不证明提示词在陌生新作品上已经有高概率的全自动成功率。离线完整性检查另核对段数、原文、解释池、来源、依赖、评审绑定与文件哈希；这类程序检查与内容验收分别记录。
'''
gate={'decision':'accept_complete','works':works,'final_judgment_bindings':bindings,'main_review':{'reviewed':'Full selected sources, historical non-regression values, final graph, actual independent reasons and critique dispositions.','resolved_precision':'S04 baseline; positive S06 increment; S11 expression versus uncertain future; S12 answer versus richer experience; joint ecstatic/painful facet; independent bodily time pressure in Op61.','limits':'Two concrete works with documented human edits; not evidence of general automatic reliability.'},'human_report':report}
synth_v2.dump(f.OUT/'final_acceptance.json',gate)
print('Explicit final acceptance recorded; export and offline checks remain',flush=True)
