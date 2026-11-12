# D3/D4 回归输入清单（2026-10-09，只读挖掘）

ROOT=`D:/musicclaude/unified_run_handoff_20260924/unified_run_handoff_20260924`。
机器可读版：`d3d4_source_inventory_20261009.json`（同目录，SHA以JSON为准）。
本页只给结论与路径，不搬运原文；裁决一律留给主会话亲读。

## 最高优先结论（Op.60 m.17–34 / m.27）

- `27–43`首次落点：`runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s1.md`
  第14–17行（meta照录生产者`opencode2api/muse-spark-1.3-contributor-free#xhigh`）。
  注意run07同名Op.60是failed空文件，不要引用run07。
- `27–43`被继承：`runs/run64_e4C_scale/steps.json`的bead_sources直接指向上面run08三首全文，
  op60切成8段，k3即`mm.27-43`。这是污染链的实锤落点。
- run70三家读的是另一条链：`runs/run53_struct_v1/outputs/STRUCT__STRUCT_v1__muse__op60__s1.md`
  第31–38行（mm.17–34站），已逐字核对与三份prompt注入的TEXT一致。
  三份prompt字节相同（`d26f6f84…`），是真单变量对照；三家首刀23/24/25是对同一段
  假设文本的三种读法，不是对乐谱的新听。模板`prompts/tooling/BEAD_SPLIT_v0.txt`。
- Run70三份产出（`runs/run70_bead/outputs/BEAD__op60__mm17-34__{gflash,luna_noweb,muse}.md`）
  无一家首刀在27——但这只是假设文本重读的结论，不能当音乐事实（权威04第6节）。
- 现存最细Op.60珠子：`runs/run130_thread_e6/beads_clean.md`（23珠，mm17–34已是k8/k9/k10三切，
  首刀24；上游run127由gpt56w合成，LEAK_CHECK_v2只做洁净不做事实验证）。
  下游C7模板`prompts/versions/C7_STEP_v2.txt`只读珠子【此刻】。

## 三首覆盖

- Op.60：假设文本链最全（run08/run53/run70/run64/run126/run127/run130/run101），
  verified事实只有run115的F-web网页转述（待乐谱核对）。
- Op.52：run08全文 + run53全文 + run70三站 + run64十珠 + run101共识（含m.195）；
  无canon/windows/clean-beads；verified事实只有F-web。
- Op.61：run08全文 + run53全文 + run70三站 + run64七珠 + run101共识（m.24 ratio 0.88最高）；
  无canon/windows/clean-beads；verified事实只有F-web。

## 缺项（新回归前必须面对）

1. 无本地乐谱真值：ROOT及D:/musicclaude顶层只有Op.52相关谱（op52_score.pdf等），
   无Op.60/Op.61乐谱PDF，无任何音频。Step A没有score/audio锚定源。
2. 无独立Texture/Form/Articulation/score-aware timeline证据文件；
   BOUNDARY_FACTS_v0只是从假设文本抽变化，run101只是文本分段共识。
3. H材料（H1–H5、GPT-5.6新生成）只在run126的units/resid里有聚合记录，
   本次按“H5后见隔离、H4产生/检验分开”未拆原文；新回归用H前先单独清点。
4. 回归规则现状（`notes/REGRESSION_CASES.md`）：R1通过、R3/R4不通过、
   R6部分——新case必须保留失败面，不许只挑通过的写。

## 前缀污染病例（原文截取，风格不扣分）

- run08第14–17行：`**mm.27-43：想留住，于是抓得更紧**`——“呼吸变短”“底下有点喘”，
  与run53第31–38行“呼吸变短”“落到同一个音上，和声每次不同”是同一条假设弧线。
- run53第31–38行站内已写“前半/后半/mm.32-34”三分结构，内含切点暗示；
  muse的25切理由是对它的改写，不是新增可听事件，按Step A标准不能直接进Step C。
- 戏剧化、笃定、因果写得满、单故事线本身不扣分；以上只谈时权无乐谱依据。

## 权利

引文全部出自本地用户自有run产物，仅作回归输入引用；
F-web内的外部URL（Kopp/UConn/PTNA等）是模型侧引用记录，本次未拉取未验证。
