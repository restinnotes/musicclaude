# 肖邦《幻想波兰舞曲》Op.61 · Bead / STRUCT（2026-10-20）

先读：`deliverable/02_Bead精简输入/D3_十三段reader.md`（十三段读者稿）→ `deliverable/03_Bead机器可读/`（S01–S13 JSON + `13段_STRUCT轻量版.json`，字段与 Op.60 交接包一致：segment / mm_start / mm_end / title / reader / beads / relations / timeline）。完整 STRUCT（含逐字引文、并入说法、审稿回应）在 `deliverable/struct/`，脚本检查在 `deliverable/checks.json`。

结果：13 段全部完成，共 55 条 bead，读者正文合计 4447 字。所有文字都是 gpt3（GPT-6 Thinking / max，Temporary + Unpersonalized）原样输出，脚本只做拼接和核验，没有为了修正音乐事实改写任何 bead。

## 链路（与 Op.60 交接包同一条：`_bead_saturation_20261018` 的生产 DAG）

交接包里 Op.60 的 03_Bead 来自生产 DAG，不是 bead_chain 的 synth_v4（生产 DAG 文档已删除 synth_v4）。开始前问过用户，用户选生产 DAG。

Pool `pool_v2`（bead_chain 冻结版）→ 精选阶梯 `gen_v1` → 独立审稿 `rev1_v1`（先盲列）→ `rev2_v1`（审阶梯）→ 定稿 `final_v2` → 整曲检查 `piece_v1` → 对被点名的段 `fix_v1`。

提示词只改了作品名和分段描述（船歌 Op.60 → 幻想波兰舞曲 Op.61；朝山十四段 → 塚田十三段），见 `prompts/`。`SEC_PER_MEASURE` 按约 13 分钟 / 288 小节取 2.7。Op.60 原脚本和结果都没有动：`chain.py`、`sat.py` 是复制出来的 Op.61 版。

分段：`_thread_evo_20261019/works/op61/segmentation.json`（PTNA / 塚田花恵 13 段），只读，转换成 `inputs/structure.json`。

## 来源组合（24 份，与 Op.60 同构：4 个模型 × int/web × 3）

| 模型 | int | web | 来源 |
|---|---|---|---|
| Gemini Flash | 3 | 3 | 现成：run05 s1–s3（int）；run08 s1–s2 + run37 s3（web）。与 Op.60 用的是同几个 run |
| Luna | 3 | 3 | 现成：run08 luna_noweb s1–s2 + run37 luna_oc2 s4（int）；run05 s1–s3（web） |
| GPT-5.6 | 3 | 3 | 现成 r1（run106）各 1 份；**新生成** int-2/3、web-2/3（gpt3 `--model gpt-5-6-thinking`） |
| GPT-6 | 3 | 3 | Op.61 没有现成稿；**新生成** int-1/2/3、web-1/2/3（gpt3 默认 GPT-6） |

- 新生成的 10 份用原 A 语料同一套提示词（`A_int_v1` / `A_web_v2`，作品名按 WORKS.md），见 `gen_A/`；10 份全部一次成功，均为 max。
- 注意：gpt3 不能关掉联网，10 份里 int 提示词的 5 份也用了 web 工具，所以 int/web 的区别只在提示词（"请查阅资料"），不在实际是否联网。
- 排除：Muse / muse_web（用户 10-18 决定），Opus、Sonnet（用户本次选择不用），Gemini Pro / Grok / 旧 Sol（生产 DAG 不收）。脚本断言 24 份里没有 muse / opus / sonnet。

## 脚本检查（`deliverable/checks.json`）

- 55 条 bead 的小节范围都在本段内；timeline 也在段内；relations / timeline / reader_uses 里没有不存在的 bead id。
- 413 条引文全部能在 A 原稿里逐字找到。其中 9 条（S01、S02、S03、S05、S07、S13）是模型写错了来源 ID，原话其实在另一份稿里（多是 GPT-6 和 GPT-5.6 之间互相标错）。脚本在 `struct/` 里加了 `quote_found_in` 标出真实来源，模型写的标签保留原样。轻量版 JSON 不含 sources，不受影响。
- 整曲检查点名 S07、S10：返回材料的身份写得太确定，跨段被接成同一个"旧舞步回来"。两段都在新会话里修订过。对全曲反复出现的"维持尊严 / 记忆 / 带着脆弱继续"主线，检查判断是 A 原稿本身就在反复讲，不算写作模板问题。
- S10 修订后，B3、B4 的小节写成了 214–225，越进了 S09。于是在同一会话里续问一次，只让模型改 measures 字段（`fix_s10_measures.py`，阶段 `final3_b`）。脚本核对过 text / reader / title 一字未变。

## 失败与偏差

- 共 74 次 gpt3 调用，70 次成功，4 次失败：
  - **S10 Pool 一共提交了 3 次**：
    - 第 1 次：请求已发出，本地 HTTP 1200 秒超时（LOCAL_TRANSPORT_FAILURE）。
    - 第 2 次：被复制来的 sat.py 自动重发。原因是 gpt3 失败时不输出 job_directory，脚本把"已提交"误判成"未提交"；这次也失败了。
    - 第 3 次：由我手动重跑，成功，耗时 9168 秒。
    - Temporary 会话失败后没有可取回的结果，前两次没有任何产出。已修补 `sat.py`：按提示词全文回查 job 目录，找不到时一律当作"可能已提交"，不自动重发。
  - rev1_b/S03：失败发生在提交前，自动重试成功。
  - rev2_b/S10：rev1_b/S10 的会话超过了 gpt3 的 6 小时寿命，本地拒绝（gpt3_session_expired），没有提交。旧的 rev1_b/S10 移到 `runs/_expired/`，S10 的审稿两轮在新会话里重做。
- 与 Op.60 生产 DAG 的偏差：fix 一步按设计应续接 gen_b 会话，但这些会话也已超过 6 小时。所以 S07、S10 的修订是在新会话里做的：把该段的 final_b STRUCT 原文（去掉脚本标记）连同 24 份原稿一起交给模型，见 `sat.py` 的 `t_fix_fresh`。
- 应用当天重启过几次，后台进程被杀过一次。后面的步骤改为独立进程 `finish.py` 运行；所有阶段都按 `parsed.json` 缓存，没有已完成的步骤被重做。
- 没有做 Op.60 实验阶段那样的多版本盲评选优（CHOSEN）；每段就是生产链路的单次采样。

## 目录

`inputs/`（24 份 A、structure.json）· `prompts/` · `gen_A/`（新 A 的生成与恢复脚本）· `sat.py`（Op.61 版生产 DAG + Pool）· `chain.py`（bead_chain 复制件，Pool 实际经 sat.py 用同一 pool_v2 提示词运行，以便单进程统一控制提交节奏）· `finish.py` · `fix_s10_measures.py` · `build_op61.py` · `runs/`（每次调用的 prompt / response / meta / parsed，`calls.jsonl` 为调用记录）· `deliverable/`
