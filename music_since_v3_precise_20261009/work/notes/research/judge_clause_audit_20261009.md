# 旧 judge 提示词禁偏见 / 信息权限条款审计（REQ-REV-02 补记，2026-10-09，只读）

范围：runs/run126_canon_op60（reviews round63）、run127_bead_e1e4（round64）、
run129_opus_bead（round65）、run130_thread_e6（round66）、run128_mech_calib（round67）
的真实 prompts，加上 run137 E7_COMPARE_v0、MECH_AUDIT_v0 tooling 模板与
run138 governed prompt（只 prepare、零模型调用）新入口的静态核。
旧 prompt / run / source / 宪法 / 验收 / 台账 / memory 均未改动。
未调用任何真实模型 / CLI / 网络；未使用 Opus / Sol；无子委派；未写音乐候选。

权威基准：notes/EXPERIMENT_AND_REVIEW.md §3 统一条款——只按材料/时间依据、
有效听者体验、信息增量、具体性、前缀诚实、语义保真、作品特异、阅读效果裁判；
戏剧化、笃定、因果写得很满、单一情感故事本身均不扣分；仅缺证据、矛盾、
压掉关键独立解释、重复灌水扣分；NONE / NO CHANGE 合法，不追求空白；
每项裁决引用原文与支持/反例；缺证据判不可判；不按模型名评分。
§4 独立评审：匿名化 + 种子、脚本算数、重大判决独立 judge、生成者自评须 alias
归一并标出、不以平均分掩盖分歧、主 Claude 不自产候选。

## 1. 实测基数

- 逐文件清单：1820 个文件（judge 子集 + run126 全量 prompts + run138 全部 audit_prompts）。
- 全文 unique SHA：1184。
- 指令模板分组（指令头哈希）：100 组。归组仅为阅读方便；manifest 仍逐文件列 full SHA。
- 每个独立 prompt SHA 均已全文读过代表文件；同 SHA 重复文件内容逐字节一致（SHA 相同即证）；
  未读全量 raw（EEG/音频/大输出），仅核条款文本。
- 逐文件 full SHA 清单见同目录 judge_clause_audit_20261009.json（perfile 数组，1820 条）。

## 2. 模板分组与 §3 presence（Y=明确含有，-=缺失，p=部分）

说明：旧版本不必与今日 §3 逐字相同；下表判的是该维度是否明确出现或缺失。
"戏剧化"一词出现只计对应一维通过，不宣布全过。

| # | 模板（代表文件） | 文件数 | 时间/材料依据 | 有效听者体验 | 信息增量 | 具体性 | 前缀诚实 | 语义保真 | 作品特异 | 阅读效果 | 戏剧不扣分 | 仅四类扣分 | NONE合法 | 逐裁决引文 | 缺证据不可判 | 模型名不评分 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T01 | BEAD_COMPARE_v0（run127 CMP 9组 + run129 compare 9组；指令头同源） | 142 | Y | Y | Y | Y | p | - | - | - | Y | p | Y（可判平手） | p（a_only/b_only一句） | - | Y（A/B随机+无关，见§4） |
| T02 | COVER_v0 系（run127 COV + run129 coverage；单模板283+18文件） | 301 | - | p | Y | Y | - | Y | - | - | - | - | - | -（只出bool数组） | - | Y（体内无模型名） |
| T03 | LEAK_CHECK_v1（run127 LEAK 12文件） | 12 | Y | - | - | Y | Y | - | - | - | - | - | p（无则[]） | Y（quote逐字） | - | Y |
| T04 | LEAK_CHECK_v2（run127 24 + run129 4 + run130 5） | 33 | Y | - | - | Y | Y | - | - | - | - | - | p（无则[]） | Y（quote逐字） | - | Y |
| T05 | TRACE_v0 系（run127 208 + run129 9） | 217 | - | - | - | - | - | Y | - | - | - | - | - | Y（来源句逐字） | Y（找不到返空、不硬凑） | Y |
| T06 | H_RESID_v0（run126 RESID 174文件 + tooling模板） | 174+1 | p（needs_future） | p | Y | Y | p | - | - | - | Y | - | - | p（overlap序号） | - | Y（体内无模型名；但调用者=被评者，见§4） |
| T07 | CANON/EXT/H1-H5（run126 生成类；非judge，附记） | 184 | n/a 生成 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | - | - | - | - | - | - |
| T08 | THREAD_ADJ_v0（run130 adj 21文件 + tooling模板） | 21+1 | Y（只凭体验+变化） | Y | Y | Y | - | - | p | - | Y | - | p（alternative可留） | Y（segments+why） | - | Y（体内无模型名） |
| T09 | THREAD_AUDIT_v1（run130 audit 9文件 + tooling模板） | 9+1 | Y（第5项+实时） | Y | Y | Y | Y | - | Y（第1/4项） | p（第7项climate） | Y | p（第6项硬写≈灌水） | p（第6项查硬写） | Y（逐字摘抄） | - | Y（体内零命中） |
| T10 | center（run130 3文件；生成+自裁混合） | 3 | - | Y | Y | Y | - | Y（不改写体验） | Y | - | - | - | - | p（段号+压扁说明） | - | Y |
| T11 | c7e6（run130 69文件；生成类Thread步骤，非judge） | 69 | Y（只看本段+后果门） | - | Y | Y | - | - | - | - | - | - | Y（没有就不写/还看不出） | p | - | Y |
| T12 | c7e6match（run130 22文件；机械对齐，非实质judge） | 22 | - | - | - | - | - | Y | - | - | - | - | p（match null合法） | Y（quote+note） | - | Y |
| T13 | MECH_AUDIT_v0（run128 AUDIT128 600文件 + run138 v0 64文件 + tooling模板） | 664+1 | p（imported=整体叙事外来） | Y | Y | - | - | - | - | - | Y | p（四类≈四扣分） | -（无undetermined/空类） | p（why一句话） | - | Y（体内无模型名；审核者排除生成者，见§4） |
| T14 | MECH128 生成模板（run128 183文件；非judge，附记） | 183 | - | Y | Y | Y | - | - | - | - | - | - | Y（0到2条+空数组正常） | - | - | - |
| T15 | AUDIT138 v1（= MECH_AUDIT_v1_counterfactual，56文件） | 56 | p | Y | Y（why须说损失） | - | - | - | - | - | Y | p | p（undetermined合法+禁猜） | p | Y（明示undetermined+缺哪份证据） | Y（评审纪律：不把来源模型/长度当证据） |
| T16 | E7_COMPARE_v0（run137 compare经run134复用；三方盲比） | 1模板 | Y | Y | Y | Y | Y（此刻诚实+hindsight） | - | Y | Y（读得下去/负担+不抢音乐；长短不加减分） | Y | Y（四扣分全） | - | Y（每项引原文+best/worst/only_here） | Y（依据不足不可判） | Y（甲乙丙+轮换，见§4） |

## 3. 原文短引（每模板一条，可追溯）

- T01 BEAD_COMPARE_v0：`不扣分：写得戏剧化、语气笃定、……假设它说的都成立，不管事实对错。` /
  `扣分：先提出一个说法再否定它……；提前说后面才发生的事；把相反的几种体验挤在一起却不点明……` /
  `A、B 的先后是随机的，与作者无关。`
- T02 COVER：`换了说法、换了意象、合并进别的句子，只要读者能从文章里得到同样的理解，都算表达了。`
  （无禁偏见句；输出只有 covered bool 数组。）
- T03 LEAK v1：`但听到这里已经能感到的期待、预感或担心不算违反：它说的是此刻的感觉，不是后面实际发生了什么。`
- T04 LEAK v2（增量）：`检验办法：把后面的音乐全部遮住，这句话还会从已经听到的音乐里自然产生吗？`
- T05 TRACE：`如果某条内容在这些来源里找不到出处，就返回空列表，不要硬凑。`
- T06 H_RESID：`写得戏剧化、具体、笃定都不影响分类。`（needs_future 为唯一时间维度。）
- T08 THREAD_ADJ：`只凭各段的体验和已经记下的变化来判断；一条假设讲得越完整、越动人，并不代表它越有依据。` /
  `不要改写任何一段原来的体验。写得戏剧化、具体、笃定都不影响判断。`
- T09 THREAD_AUDIT_v1：`写得戏剧化、笃定、写成具体场景都不是缺点；不要因为这些扣分。`（7项检查+逐字引文JSON。）
- T10 center：`不要改写任何一段原来的体验。用具体、普通人能懂的话。` /
  `它能解释哪几段；哪几段它解释不了，或者会被它压扁`（缺整套§3禁偏见句。）
- T11 c7e6：`要写的是这一段留下的后果，不是这一段本身的感受；很多段落可能没有。` /
  `否则写"还看不出"，很多时候要过好几段才看得出。`
- T12 c7e6match：`判断它指的是清单中的哪一条；判断不了的，match 写 null。`
- T13 MECH_AUDIT_v0：`写得戏剧化、具体、笃定都不影响判断。`（四类insight/restatement/manufactured/imported。）
- T15 AUDIT138 v1增量：`只有你能指出删掉这条关系……听者会失去哪一种……理解，才可判 insight` /
  `评审纪律补充：……不追求 NONE 或空白率；……不把来源模型或长度当证据。` /
  `可以输出 {"class":"undetermined",…}，不要猜测。`
- T16 E7_COMPARE_v0：`请只根据文字中可辨的时间/音乐依据、具体性、作品特异性、此刻的诚实……来判断。`
  `戏剧化、笃定、因果写得很满、单一情感故事本身都不扣分；只有缺依据、与音乐矛盾、`
  `压掉关键的独立理解、重复灌水，或用后见之明定义此刻时才扣分。……每项判断都要引用原文；依据不足就说不可判。`

## 4. 命名泄身份 / 自评 / 独立 judge / 分歧（实证，非推测）

- 文件名泄身份：prompts 文件名含 `__gpt56w__/__muse__/__luna_noweb__/__opus__/__sol61_cx__`、
  `by_gpt56w/by_muse`、`R001…` 等生产者标记，1820 个文件均有此类 basename。
  但抽验的全部 judge 模板体内均无模型名（CMP/AUDIT128/audit130 grep 零命中），
  落盘 prompt 只是带文件名的容器；是否泄身份取决于 runner 喂 judge 时是否剥离文件名。
  run127 run_compare 以 `core = "CMP__w%d__..."` 为缓存键、prompt 体内只放 A/B 文本，
  文件名不进入 prompt——CMP/E7 的盲化链完整；其余单对象 judge 无 A/B 位，文件名无载荷意义。
- 盲化实证（run127 CMP）：tools/run127_bead_e1e4.py run_compare 用
  `rng = random.Random("%s|%s|%s" % (w, old_cond+"_vs_"+new_cond, judge))` 做 A/B 随机，
  模板内 `A、B 的先后是随机的，与作者无关`，compare.json 记录 `new_is_A` 供事后解盲。
  E7（run134→run137）同样 `SEED_COMPARE + 100*set_index + …` 轮换甲乙丙并记 mapping。
  其余 judge（COV/LEAK/TRACE/AUDIT128）为单对象判定，无 A/B 位，无需盲化；
  round64/67 review 称"muse/luna 审核"指的是按模型分发的调用记录，非 prompt 体内点名。
- 自评实证：
  - run127：CMP_JUDGES=(muse, luna_noweb, gpt56w)，生成者也在 judge 名单，compare.json 保留 judge 字段，
    round64 review 已声明"gpt56w 自评仅参考"——属生成者可自评但须标出的限权形态
    （§4要求alias归一标出；当时是否归一见 compare.json judge 字段）。
  - run128：tools/run128_mech_calib.py `auditors_of(gen) = [g for g in GENS if g != gen]`，
    审核者恒排除生成者，自评不可能——独立性最强的一轮。
  - run126：RESID_MODEL=CANON_MODEL=GEN_MODEL=gpt56w（tools/run126_canon_op60.py），
    第4步残差分类是 gpt56w 判自己聚类的代表句；round63 结论"H1/H2/H5低于噪声底"即出自该自判，
    按今日 §4 属"生成者自评"，须标限权使用，不得当独立判决。
  - run137：judges=(gflash, luna_noweb)，gen=gflash；go.py 用 canonical_model 归一
    （gflash_web=gflash 防漏标），report 断言 c_gflash_s1/gflash 的 judge_is_generator_of=a,c。
    自评被显式标记而非剔除，符合"须标出"要求。
- 独立 judge 实证：run128 每关系由除生成者外两家各审；run127 COV 双 judge（muse+luna_noweb）；
  run130 第二轮三链各由其余两家审（audit 文件名 by_* 即证据）；重大判决（E1分窗/E2挤掉/H4盲比等）
  round64 均有 muse+luna 双源，非单模型自说自话。
- 分歧处理：round64 明确记"muse 6/3、luna 5/4、gpt56w自评仅参考"式分开列数而非平均；
  round67 记"两位都判 insight 43→30"的一致数；
  但旧轮均无"平均分掩盖分歧"的数值平均行为，也无成文的分歧裁决记录——按今日 §4 属缺"分歧明示裁决"项。

## 5. 历史规则 vs 今日合法性（不悄悄改写）

- run126 round63 的"H残差低于噪声底"、run127 round64 的"E2 H平铺挤掉A核心"等结论，
  均产自缺多维 §3 条款的旧 prompt（T06/T02），属历史限权证据：方向可参考，强度不可当独立判决引用。
- round65 的 Opus"重复灌水"判罚产自 T01 系（有反灌水扣分句），在当时规则下成立；今日 §3 仍罚灌水，结论延续有效。
- round66 的"治疗弧仍出现但降为候选之一"产自 T08–T10（有"动人不代表有依据"+"压扁说明"），
  属当时已有去浪漫化机制下的真实发现，非无约束产物。
- round67 的"MECH_AUDIT_v0 区分力不足"（一致 insight 43→30，manufactured/imported≈0）
  与本审计的 T13 缺项（无引文强制、无不可判、无NONE合法）互相印证：不是模型道德问题，是 prompt 缺门。
- AUDIT138 v1 与 MECH_AUDIT_v1_counterfactual 头部逐字一致（模板哈希 8107da3b7959），
  v0 与 MECH_AUDIT_v0/AUDIT128 指令头一致——run138 是旧审核模板的治理版重跑准备，
  不是新禁偏见覆盖；其"评审纪律补充"仍缺：时间/材料依据、语义保真、作品特异、阅读效果、
  前缀诚实、仅四类扣分、逐裁决引文（仅一句话why）七项。

## 6. 新入口静态核（run137 / run138，不采信自述）

- E7_COMPARE_v0（prompts/tooling/E7_COMPARE_v0.txt）：
  16 维中唯一全覆盖§3的模板（缺NONE合法一项，但三方排序本就不产NONE，属形态豁免）。
  明示 `因果写得很满、单一情感故事本身都不扣分`——旧全轮中唯一写全该句的。
  但 run137 README 自述"两 w 对照缺席、Muse评审缺席、只写 COMPLETION_PENDING"——
  在缺席归位前，E7 条款再全也不能当最终裁决用。
- MECH_AUDIT_v0（tooling模板）：与 AUDIT128 落盘实例指令头一致；缺项同 T13。
- run138（audit_prompts 120文件 = R023–R062 × v0/v1 × gflash名义；R001–R024 为站内编号）：
  落盘 prompt 体内 judge 恒为 gflash 名义（文件名 `__gflash`），但 plan.json/cases.json 声明只 prepare、
  零模型调用——实际完整 terminal 证据（compare.json 类）不存在。不以"文件名含gflash"认定已执行。
  v1 相对 v0 的单变量 = insight 收紧（须说出删除损失）+ restatement 定义 + undetermined 合法化 +
  评审纪律三句；R001–R024 各站 v0/v1 指令头在站内一致、站间随体验材料变——
  符合"只改一处变量"的单变量形态（变量即 v0→v1 增量句）。
- run138 自述"prepare完成"不等于禁偏见覆盖：v1 仍缺 7 项（见§5），不得引用为充分评审合同。

## 7. 缺项代表（按影响排序）

1. T02 COVER（301文件，最大缺口）：整套 §3 缺失——无时间依据、无戏剧不扣分、无扣分定义、
   无引文（只出bool数组）、无不可判。round64 "E2 H挤掉A核心0.85→0.79"的覆盖数即出自该模板：
   数字可复算，但"挤掉"的价值判断无条款支撑，属限权证据。
2. T05 TRACE（217文件）：只有语义保真+引文+不硬凑；无全部禁偏见句。好在输出是来源句摘抄，
   可复查，判断强度低，限权影响小。
3. T13 MECH_AUDIT_v0 系（664+1）：缺引文强制、缺不可判、缺NONE合法、缺具体性/特异/阅读效果。
   round67 的"一致insight"虚高与此直接相关；v1（T15）补了其中三项，仍缺七项。
4. T06 H_RESID（174+1）：缺独立性（自判）+缺引文强制+缺不可判。round63 H残差结论限权使用。
5. T10 center（3文件）：缺整套禁偏见句；但有"压扁说明"这一作品特异代偿，round66 Opus中心候选2的
   发现仍可参考，不可当判决。
6. T03/T04 LEAK（45文件）：虽缺戏剧/模型名句，但形态是逐句改写而非打分，缺项影响最小；
   v2 的"遮住后文检验"是全轮最强的前缀诚实操作句。

## 8. Terminal 证据可得性

- run126：canon.json/extract.json/gen.json/resid.json/calls.json/manifest.json + DONE 俱在；
  prompts 358文件全落盘。RESID 自判记录在 resid.json（judge=gpt56w 可验）。
- run127：compare.json/coverage.json/leak.json/merge.json/calls.json + DONE 俱在；
  prompts 695文件全落盘。compare.json 含 judge/new_is_A/mapping（盲化解盲可验）。
- run129：compare.json/coverage.json/leak.json/results.json/run_manifest.json + DONE 俱在。
- run130：adjudication.json/audits.json/centers.json/cache_* + DONE 俱在；prompts 129文件全落盘。
- run128：cache_audit.json/cache_gen.json/calls.json/run_manifest.json/report.md + DONE 俱在；
  prompts 783文件全落盘。
- run137：compare.json 缺（两w+Muse缺席，COMPLETION_PENDING）——E7条款全但无完整terminal证据。
- run138：零模型调用，terminal证据不存在——标"未知/缺席"，不推测执行结果。

## 9. 给 ZIP 台账 REQ-REV-02 的补记句

> 旧五轮 judge prompt 已逐 SHA 全文审计（1820文件/1184 unique/100模板组，perfile full SHA 见
> judge_clause_audit_20261009.json）。仅 E7_COMPARE_v0 全覆盖今日§3（缺NONE，形态豁免）；
> 其余模板各缺 3–12 项，最大缺口为 COVER（301文件，无禁偏见无引文）与 MECH_AUDIT_v0 系
> （664+1，无引文强制/不可判/NONE）。自评：run128 恒排除生成者；run126 RESID=自判；
> run127 CMP 含自评但已标仅参考；run137 自评已归一标出。盲化：CMP/E7 有种子随机+解盲记录；
> 单对象 judge 无需盲化。旧结论一律按历史限权证据使用，不追溯改写；run138 零调用、无 terminal 证据。
