# run140：60 条旧关系独立判断包（机械转写）

**定位：legacy-input E5 单句审核诊断，非 canonical 新 E5 / 三作品验收，不切 production。**

- 输入：`runs/run138_e5_counterfactual/cases.json`（60 条：op52 每站 2×16=32，op60 每站 2×14=28）与 `plan.json`，按原字节 SHA 锁；任一字节改动即拒。
- run138 尚 0 真实 audit，`independent_review_case_ids` 只是占位；本包与两条件结果无关，不泄旧标签、不按 known verdict 挑例、不追 NONE 率。
- 分包：seed20261009 固定 shuffle，5 包 × 12 case；blindID（B001–B060）单独乱排（blind seed 20261010），不泄 original 顺序。
- judge 全文：每包 12 case 原文 inline（WORK 中文名 / MM / items / relation / new_understanding 均为待审旧文字，非乐谱事实）；case_id、工号、生成 model、来源 run、旧标签、条件名一律不进；禁 judge 读文件。
- 评审口径：见包头模板全文（八判据 + 五类 + retain_anchor 单列 + 原文引证 + undetermined 兜底 + input-level 证据边界）。MECH_AUDIT_v0/v1 冻结文件一字未动。
- 映射：`case_mapping.json`（60 条，含 sourceSHA / 原 ID / genCanonical / promptSHA）私存，不进 judge。
- `--prepare` 只写本目录 7 个文件，immutable（冲突即拒），model_submissions=0；driver SHA 与模板 SHA 落盘于 `plan.json`。

## 文件

- `plan.json`（d6272254…）：包清单 + promptSHA + 锁信息 + reviewers_planned（Muse/Luna 各 separate 一份，不平均不多数；外部 producer 按实际 transport 真实记录；工程 mock 自评不算真 review；twowheld 不补造）。
- `case_mapping.json`（c2d32cf4…）：60 条私存映射。
- `review_prompts/pack01–05.txt`：5 包 judge 全文（每包 12 case inline）。

## 验证

- 调试前先跑：`python -I tools/tests/test_run140_mech_review_export.py`（9 项：盲身份未泄 / seed-mapping-pack 完整 / 原文保真 / malformed-schema / missing-duplicate-id / source-prompt 篡改冻结拒 / prepare 字节幂等 / policy production=false）。
- 实际跑 tests：9/9 通过后才执行 `--prepare`；prepare 报告 0 模型提交 + files hash（见主会话报告，不在此 dump 全文）。

## 风险

- 旧中文在部分终端显示为 mojibake（上游 legacy 编码遗留）；本任务按原字节透传，不做转码或“修复”，引证核对以字节为准。
- 后续真实评审需至少 Muse 与 Luna 两份 separate 结果；缺任一份不得报完成，更不得以 mock 自评充数。
