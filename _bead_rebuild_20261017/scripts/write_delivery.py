from pathlib import Path
from collections import Counter
import json, shutil,hashlib
R=Path(__file__).resolve().parents[1];Q=R.parent/'_bead_quality_20261017'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,s):p.write_text(s,encoding='utf-8')
def run():
 d=read(R/'CONTENT.json');v=read(R/'VALIDATION.json');s=v['coverage_summary'];layout=read(R/'VIEW_CHECK.json') if (R/'VIEW_CHECK.json').exists() else {}
 notfit=[x['segment'] for x in layout.get('pages',[]) if not x['fits_one_frame']]
 globalrows=read(R/'reviews'/'global_scope.json');gc=dict(Counter(x['disposition'] for x in globalrows))
 runs=read(R/'MODEL_RUNS.json') if (R/'MODEL_RUNS.json').exists() else []
 brief=f'''# 先看真正的内容

[打开十四段阅读页](船歌·每段一页.html#S02) · [上一版／新版／原稿逐项核对](内容与原稿核对.html) · [仍未完整保留的全部项目](尚未完整保留.html) · [真实模型实验判读](模型实验判读.html) · [全曲原意去向](reviews/global_registry.html)

本轮成品在 CONTENT.json；原始模型响应、主编辑稿、独立语义复核、后续修补分别留档。旧版与原A未覆盖。

本轮优先解决三类实际丢失：三次变化被压成一种感受；不同动因被当成重复；几种读法被编辑连接成一条必然经历。S02的安慰、犹豫、疼，S04的流连与怕结束，S07的沉默、回放与感官沉醉，均单独留在文字里。特殊词汇由原稿决定，不因为听来浓烈就单独放大。

## 当前验证结果与限制

- 固定比较范围：旧审计已经可判断的 {s['fixed_baseline_assessed_canonical_experience_denominator']} 组局部体验，分母未因本轮删留而缩小。
- 上一版完整保留：{s['baseline_counts'].get('full',0)} 组（{s['baseline_full_pct']}%）。本轮判定完整保留：{s['new_counts'].get('full',0)} 组（{s['new_full_pct']}%）。其余状态：{json.dumps({k:n for k,n in s['new_counts'].items() if k!='full'},ensure_ascii=False)}。
- 逐项局部记录 {v['local_ledger_rows']} 项；已完成独立复核或明确主编辑裁决 {v['independently_reviewed_rows']} 项。原始逐段记录与跨段同义组均保留，未把“引用了来源”当作完整覆盖。
- 本轮包含审计者分歧。S02第二轮更保守复核将部分主体、范围和合场歧义降为partial；未明确修好的项目采用较保守状态，不采用最高一轮的分数。原始分歧在AUDIT_DISAGREEMENTS.json，后续明确修补与裁决另列。这个比例是账本定义下的判断结果，并非全原稿的客观总保真率。
- 正文取材引句 {v['source_quote_count']} 条，当前机械验证错误 {len(v['errors'])} 个。语义覆盖不是机械匹配的结果；复核者也可能误判，具体句子与裁决均公开。
- 94条全曲/余料去向：{json.dumps(gc,ensure_ascii=False)}。全曲层面的65条不强塞进单S，也不冒充已经在读者正文中保留。三条可靠定位的新增原意并入S10/S13，独立列账，不抬高旧局部覆盖率。
- 每个S只有一个页面，全部内容可见，不自动轮播或频繁切页；没有任意句子加粗。1920×1080、固定可读字号下，仍需滚动的段落：{', '.join(notfit) or '无'}。这部分未通过单帧展示验收。
- 尚未绑定某一录音，也未声称普通观众可以随音乐读完。完整内容的保留与音乐时长内的阅读不是同一项测试；本轮不靠隐藏内容、缩字号或高分宣告完成。

## 怎样判断这版是否更好

先读S02/S04/S07，然后读S13；再打开核对页，查任何一种你认为丢掉的差别。full表示复核认为完整原意可恢复；partial会写明仍缺什么；pending保留错位/未定位条件；omitted明确承认未保留。S13的持续能量与渐退听法附着各自条件，m.111的收束不倒灌到103–110。

本轮的语言目标是：共同前提只说一次，差别仍然用自然句子说清楚。页面使用真正存在的顺序、并列解释、可并存观察和演奏条件。没有关系可节省理解时，就保留普通句子，不为“结构化”加一个抽象标签。
'''
 write(R/'READ_ME_FIRST.md',brief)
 old={x['segment']:x for x in read(Q/'editorial'/'FINAL_BEADS.json')}
 parts=['# 原稿、旧版与本轮编辑版\n\n完整逐项对应见同目录“内容与原稿核对.html”。下面直接展示文字，便于脱离工具阅读。\n']
 for p in d['pages']:
  parts.append(f"\n## {p['segment']} · {p['bars']}\n\n### 上一版\n\n{old[p['segment']]['body']}\n\n### 本轮\n\n{p.get('intro','')}\n")
  for b in p['blocks']:
   parts.append(f"\n**{b['label']}**\n\n{b.get('text','')}\n")
  parts.append('\n### 直接取材的原稿\n')
  seen=set()
  for b in p['blocks']:
   for e in b.get('evidence',[])[:2]:
    key=(e['uid'],e['quote'])
    if key in seen:continue
    seen.add(key);parts.append(f"\n> {e['quote']}\n\n来源：{e['uid']}\n")
 write(R/'BEAD_CONTENT_REVIEW.md',''.join(parts))
 method='''# 实验机制与实际发现

本轮使用同一批30份原A、固定十四段和现有事实边界；不重新采A、不细切S、不写Thread/History/Outer/E7。

1. 输入保持完整原稿，另带旧审计原意账本。账本用于提醒差异，不代替阅读。每项都有去向；共享情绪、来源被引用和关键词重合，均不构成无损合并。
2. 写作只压重复前提、同义解释和编辑连接。并列读法之间不补因果；同一读法内部若有清楚的顺序或条件，则保留它。独特主体、身体感、动因、时间、词汇必须有具体落点。
3. 作者索引不直接算覆盖率。独立复核逐项回看原稿和成品，给出full/partial/omitted/pending；主编辑再裁决实质问题与过度字面的误判。所有修补另存，不改模型原始输出。
4. 反向查正文：新增因果、动作、人物和转折有无来源。引句用连续精确子串；有出处不自动代表所有细节都已保留。
5. 固定旧审计858个可判断的跨段同义组作前后比较。其余候选与GLOBAL保留各自状态，不靠改pending或挪分母提高百分比。
6. 内容与版式分开检查。一个S一页，全部异质性同等可见。顺序条只用于原稿确有三次变化之处；其他内容使用平行读法、观察、条件或普通段落。字号一致，未选几句“语气重”的内容独占强调。

Flash首轮实际生成了三段；Muse三次均在本地服务就绪以前退出，不能把失败当成它的内容能力证据。GPT-6w另做S02附件对照，实际状态见MODEL_RUNS.json。

Flash可以补回大量细节，但S02长达2865字；S04仍把“旧事没有过去”塞进流连细节类；还有过强的作曲意图判断。S07的输出遗漏10个旧ID去向，表明即便提示词要求完整映射，也仍需实际核验。部分引文去除了Markdown标记或跨过分段，已不再是严格连续子串；这不等于内容全为编造，但不能当精确溯源通过。

因此，本轮未采用“让一个模型写完，自报覆盖率，然后换模型抽冠军”。主编辑的稿子与模型响应单独保留，独立复核确实找到了主编辑的新损失。补齐遗漏后，仍必须直面字数和阅读时间，不能说“都做成卡片了”就等于轻松。

S06另做压缩实验，S02另做组件实验。完整原稿不变，实验稿与日志分别留档；未通过逐项复核的稿件不替换活动成品。S12原计划做第二轮压缩，但未产出可复核结果，不计作完成实验。

旧阶段关于A、Pool和Bead的诊断仍成立：原A已有丰富材料，也夹杂错位与传记推断；Pool曾有标题继承等传递问题，当前生产输入已补回；Bead的自然文章要求、强求连缀和主编辑取舍，是本次确认的实际损失环节。以上证据不能证明某个模型天然不适合统合。
'''
 write(R/'EXPERIMENT_METHOD.md',method)
 experiment_notes='''
## 本轮最终采用与未采用

S06压缩稿已在独立逐项复核后采用，修掉“自辩”、不同双人场景合流以及两种走神动因串接；恢复美好夜晚突然冒出疑问的时点。这里只能确认文字中多数差别仍在、重复铺垫减少，不能据此称同步阅读成功。

S02组件实验未采用。稿件在实验过程中有多个快照，早期观察1740字符，最终冻结复核1639字符；最终审计使用的组件稿哈希见S02_component_review.json。早期观察的正文与行数据曾不一致，最终冻结快照逐字一致，两个观察不混用。其最终复核仍只有72/85项full，并发现共享前提扩域、人物合场及电报式省句问题。它较当时1839字符的主稿短约10.9%，这不构成同等覆盖或更轻负担的胜利。

S02更严格复核对主稿给出比第一轮低的判断。没有删除这份不利结果；其对主稿的判定单独提取入活动审计，再保留有具体正文依据的后续修补。全部33项分歧公开，不按模型多数票或最高分通过。

S12第二轮压缩稿没有产出可供独立复核的结果；不把计划中的实验写成已经完成。当前S12仍采用第一轮稿，经末轮修补及错位链隔离。

最终反查另撤出S12退潮冷汗与S14溺水求生两块；保留原文、原因及原意ID。S13暂缓未定位Muse单元的擦脸和原谅链，保留另有可靠来源的玩心。反查中“没有遗留已登记连接错误”只针对登记的反查清单，不是所有可能错误已消失的保证。

十四段在1920×1080的当前版式均超出一屏。完整内容稿已经可供核读，视频随音乐低负担阅读仍未达标。未完成的音乐同步与阅读验证不是通过机械检查可以补签的。
'''
 write(R/'EXPERIMENT_METHOD.md',method+experiment_notes)
 (R/'reference'/'original_A').mkdir(parents=True,exist_ok=True)
 for f in (Q/'sources').glob('SRC-*.md'):shutil.copyfile(f,R/'reference'/'original_A'/f.name)
 shutil.copyfile(Q/'sources'/'SOURCE_MANIFEST.json',R/'reference'/'SOURCE_MANIFEST.json')
 shutil.copyfile(Q/'editorial'/'FINAL_BEADS.json',R/'reference'/'previous_beads.json')
 print('delivery texts written; original A files',len(list((R/'reference'/'original_A').glob('*.md'))))
if __name__=='__main__':run()
