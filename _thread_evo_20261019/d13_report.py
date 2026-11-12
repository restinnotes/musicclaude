"""Write a status-aware report from actual D13 evidence, without a model call."""
from d13_experiment import *
from d13_evaluate import draft_files,latest_review
from collections import Counter
from datetime import datetime,timezone

DEST=Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs')

def report():
 drafts=[load(p)for p in sorted((O/'drafts').glob('*.json'))]
 summary=load(O/'experiment_summary.json')if (O/'experiment_summary.json').exists()else []
 provenance=load(O/'provenance_verification.json')if (O/'provenance_verification.json').exists()else {}
 attribution=load(O/'G25_source_attribution.json')if (O/'G25_source_attribution.json').exists()else []
 state=load(O/'resume_20261025_state.json')if (O/'resume_20261025_state.json').exists()else {}
 valid=[d for d in drafts if d.get('pipeline_valid',True)]
 invalid=[d for d in drafts if not d.get('pipeline_valid',True)]
 lines=['D13 独立上游机制与历史自洽路径：实验报告与真实完成范围',
  '生成时间（UTC）：'+datetime.now(timezone.utc).isoformat(),
  '本报告由实际输入、原始回答及已保存评审汇总。不是一份新的Thread成稿。',
  '当前接续状态：'+state.get('status','首条串行接续调用执行中，队列尚未启动'),'',
  '一、现在能作出的判断','',
  '现有证据尚不足以认定独立Thread池已经能够成为主生产来源。已审查的主要重复样本核心解释仍不足；“稿件连贯”与“在同一自洽路径上解释重要体验”必须分开。没有用新G25补缺掩盖缺口。',
  '此结论适用于已完成并验收的样本，不把接收失败当成模型内容失败，不用尚未结束的试验推断全曲能力。',
  'Op.60 S01–S05的v2是目前主要的同条件三次重复。Op.61和长距离链的完成范围见下；未完成部分保留缺口。','',
  '二、从本轮计划开始，实际做过什么','',
  '1. 读取并冻结旧基准，建立来源清单。D10/D11/D12共68篇旧独立稿，每首34篇；27段取出原稿本段、同源前史、旧池、最终选定机制，保存forensics/inputs。旧包3与已有最终语义/关系图不再当作本轮可随意改写的目标。',
  '2. 建立27段来源首轮审计，覆盖最终49个mechanism，并审查旧池的前提/桥/结果合并。Op61 S13分三家族取得原始审计，最终并集为明确标注的确定性整理，不冒称新的模型合并判断。',
  '3. 重新校准评委。用户指定的“不是第一次那个人/更有分量/更在乎”、音乐偷换外部事实、珠子同义复述，以及“允许共存不等于解释实际发生”均纳入测试。强化版17例中GPT5.6、GPT6各17/17通过。有限校准集通过不代表评委在真实任务上不会错。',
  '4. 独立音乐输入从两份本地乐谱提取，记录PDF页码、哈希与不确定项；生成阶段只给本条History、当段音乐事实和相邻结构。未给最终珠子、G25或旧最佳答案；珠子在事后评审阶段才进入。尚未做独立听音核查，乐谱事实不是心理机制的真值。',
  '5. 做A自由/B历史关系/C最小解释逐段生成，并保留v1–v8提示词迭代及原始回答。每段History只来自本条已生成内容，不跨稿注入。模型主生成显式GPT5.6/max，未把GPT6暗中换成主生成。',
  '6. v1–v4诊断到“表达管理/兼容性命题代替实际心理原因”的偏差。v5恢复用户原始五标题，v6增加假说起点澄清；旧History解析器误收说明文字，v5/v6整链标无效，保留原文、排除成绩。v7用修复解析器重新开始；v8仅改变宽松Center方向。',
  '7. 用通过强化校准的评委逐颗验收、留存gap，抽取机制池；原始前提、桥、结果和History要求不因结果词相近而合并，不设6–8条上限。',
  '8. 用户报告网页版中断后停止批量，另行做故障记录。用户随后明确授权继续当前provider。本次恢复串行请求；2026-10-25晚间v8 A/S02已返回完整结果。续接队列及后续失败以resume状态和过程时间线为准。',
  '9. 整理原始输入输出、可读逐稿、来源表、覆盖表、模型证明、失败日志与报告。ZIP校验及SHA保存在交付回执。档案是已完成与未完成工作的真实记录，不把计划文件当作完成证明。','',
  '三、主要重复实验：Op.60 S01–S05，17颗非演奏条件珠子','',
  '版本 | 变体 | 重复 | explained/17 | 核心段通过/5 | 评委认为路径内部自洽 | 可作主来源',]
 for r in summary:
  if r['version']=='v2'and r['work']=='op60'and r['scope']=='prefix':
   lines.append(f"v2 | {r['variant']} | {r['repeat']} | {r['explained']}/{r['total']} | {r['core_pass_sections']}/5 | {r['path_coherent']} | {r['ready']}")
 lines+=['',
  'explained不含compatible independent；后者保留为相容体验，不能计作解释覆盖。A第二次有7/17局部解释且内部前史被判连贯，但核心段通过0/5，仍未达到主来源要求。不同重复的局部解释不能直接相加成一条合法路径。',
  'A/B/C每变体S01的实际输入哈希相同、后台任务不同；后续History由各自结果产生，故会分叉。完整前缀快照与后来延长链分开，原评审按SHA绑定快照。','',
  '四、所有独立稿的真实完成范围','',
  '稿件 | 已完成段数 | 管道是否有效 | 当前SHA是否已有强化版评审']
 for p in sorted((O/'drafts').glob('*.json')):
  d=load(p);review=latest_review(p)
  lines.append(f"{d['name']} | {len(d['sections'])} | {d.get('pipeline_valid',True)} | {bool(review)}")
 lines+=['',
  'Op60 v2九条五段前缀的评审可能绑定draft_prefixes快照，故延长稿当前SHA无评审不意味着原五段重复未评审。S12–S13只能由S01顺序延伸；没有跳段移植旧G25 History。未到达者不能算远距离检查通过。',
  f"结构化原稿共{len(drafts)}条，其中有效管道{len(valid)}条、无效管道{len(invalid)}条；有效稿当前合计{sum(len(d['sections'])for d in valid)}个已完成Section（不是独立全篇数）。",'',
  '五、最终G25机制的来源审计：完整范围与尚待复核之处','',
  '旧包3最终选定机制：Op60 25个中直接来自旧池1个，Op61 24个中0个。旧池manifest的来源范围原本只含d12*，所以D10/D11已有但未进池，首先属于来源范围排除，不能都归咎于合并丢失。',
  '以下是覆盖49个目标的首轮A/B/C分类，不是已完成上下文复核后的最终因果裁决：']
 for w in TAGS:
  subset=[x for x in attribution if x['work']==w]
  counts=Counter(x['class']for x in subset)
  checked=sum(x.get('review_status')=='context_review_complete'for x in subset)
  lines.append(f"{w}: {len(subset)}个目标，A={counts['A']}、B={counts['B']}、C={counts['C']}；已完成上下文复核{checked}个。")
 lines+=['',
  'A是原稿已有同前提+桥+结果；B是近似但桥/前提不完整；C只指给定全集没有。首轮对“需要多严格才算同一机制”、G25自身价值和真实最终前史有待纠正之处，不用首轮C=0就宣布上游没有缺失。',
  '旧合并的一个明确问题是Op60 S04/M1：将“不确定、心慌或孤单”等不同来源前提统一成再次亲近更珍贵。它们不能仅因结果接近就合并。完整坏合并清单留在每段原始审计中；首轮标记也不自动当作最终裁决。',
  '首轮原回答有顶层sec误写S01的情况，权威段号取原始输入与文件名；原始回答不改。引用检查另保存source_quote_verification_v2，剥除外层引号只修格式；未匹配引用仍标需复核，不冒称逐字核验全部通过。',
  '此前有一份上下文调用收到空rows并返回空targets，它不完成任何目标。现已在接受结果前检查真实目标集，合并表会分别标context_review_complete与first_pass_provisional_context_review_missing。','',
  '六、mechanism pool与coherent-path coverage','']
 for w in TAGS:
  ps=sorted((O/f'pools/v2/{w}').glob('S*.json'))
  counts=[(p.stem,len(load(p)['mechanisms']))for p in ps]
  lines.append(w+' v2池：'+str(counts))
  selection=O/f'paths/v2_{w}_selection.json';verify=O/f'paths/v2_{w}_verification.json'
  if selection.exists():
   j=load(selection);cs=[b for s in j['sections']for b in s['coverage']]
   lines.append(f"池选择已返回：{sum(b['status']=='explained'for b in cs)}/{len(cs)} explained，选择器path_coherent={j['path_coherent']}。")
  else:lines.append('尚无完整返回并校验的跨稿选取路径，不报告已经验证的池路径coverage。')
  if verify.exists():
   j=load(verify);cs=[b for s in j['sections']for b in s['coverage']]
   lines.append(f"独立复核：{sum(b['status']=='explained'for b in cs)}/{len(cs)} explained，path_coherent={j['path_coherent']}，ready={j['upstream_main_source_ready']}。")
  else:lines.append('尚无完成的独立路径复核。')
 lines+=['',
  '当前池机制保留来源自带前史；最终选取时仍须逐项映射到此前实际选中的History。没有映射就不能把独立稿某一条的解释计入另一条路径。任何有限搜索结果只作已发现可行路径的下界，不称理论最大值。','',
  '七、prompt具体卡在哪里','',
  '已验收旧样本反复出现的行为：把“不能虚构对方回应”变成主人公“不索取答案”的人生原则；把“某体验允许共存/不必消失”当成它实际发生的原因；把愿望/可能性升级为已得到的事实；用显露、收敛、连续性监测代替真正的亲近、满足、牵挂、落空。',
  '这不是要求加更多心理步骤。更需要的是让少量真实具体前史改变当前体验的内容，明确欲望、已得体验及其局限；不能只改变力度/表达的形容。既不能给生成器偷塞G25答案，也不能把不虚构外部事实扩大成不允许合理的主观体验假说。',
  'v7/v8及后续新样本必须按实际完成范围单列。仅恢复用户原prompt、增加宽松Center或成功返回一段，均不能先宣称上述行为已改善。','',
  '八、尚未完成与不能作出的结论','',
  '不能根据当前材料宣称全曲或陌生作品高概率成功；不能把未完成的第三次重复视为三次完成；不能把未到S12/S13的链当远距离检查；不能将合并池内来自互斥前史的解释覆盖相加。',
  '如没有完整池路径复核，上游到底还需多少局部补缺不能可靠计数。“原稿池里有相近句子”不是最终合法路径可用的证明。本轮没有新增G25来填数。',
  '评委校准不等于所有真实判断可靠。来源首轮、引用未匹配、上下文缺审、当前无评审稿件都保留明确标记。','',
  '九、接收故障与晚间恢复记录','',
  '17:36–18:29的暂停前主账号245个提交标记：203完整成功，9异步续接未完成、19接收超时、14停止时未知。不同错误不能混称后台模型失败；备用账号额度拒绝不能套到主账号。',
  '用户后确认手动网页与gpt4同账号/工作区，同一回合各设备均无后续正文，并提供正文句中截断、界面已出现结束操作栏的截图。这是故障调查材料，不作为Thread内容评分依据。',
  '晚间用户授权继续同provider后，采用一次一个请求。运行状态、请求次数、连续失败与停止原因见resume_20261025_state.json及对应events。没有更换账号规避限制，没有跳过完成校验，没有新增强制锁。']
 if state:
  lines.append('当前状态摘要：'+json.dumps({k:state.get(k)for k in ('status','stop_rule','consecutive_failures','stop_reason')},ensure_ascii=False))
  lines.append('晚间请求记录：'+json.dumps(state.get('new_calls',[]),ensure_ascii=False))
 lines+=['',
  '十、交付档案如何读','',
  '00_先读实验报告.txt：本报告。01_本轮实验：各版本prompt、原始稿、逐段评审、来源审计与可读导出。02_运行代码：实际脚本与计划。03_运行日志：实际过程。04_实际模型输入输出：每次真正发送的input和回答/失败记录。05_后台任务成功证据：返回模型/max与完成校验。06_旧稿对照：D10/D11/D12、旧池、G25逐段记录和冻结最终图。07_独立乐谱输入：本轮独立音乐输入的PDF来源。',
  '文件清单与SHA256.json及ZIP同名.sha256用于核对。档案包含可审查的输入、输出、程序与事件记录，不包含模型私有内部思维。',
  '旧包3保留为单独的原历史交付；D13另包归档，不覆盖它。']
 text='\n'.join(lines)+'\n'
 (DEST/'D13_实验报告_20261025.txt').write_text(text,encoding='utf-8-sig')
 print('REPORT',len(text),'characters')

if __name__=='__main__':report()
