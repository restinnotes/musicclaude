# run134 E7 诊断性整篇样稿（Op.60；诊断用，不进 production）

- 生成（why/mech）：`gflash_web`；chooser：`gpt56w`；MECH 审核：gpt56w、luna_noweb；评审：luna_noweb、gflash_web、gpt56w、gpt6w；历史清单来源：`run130:gpt56w`
- 只报告脚本算出的数字与原文，不做审美裁决。

## 1. 上游

- why：22 颗中 differs=true 6、false 0、解析失败 16
- mech：生成关系 3 条（解析失败 20 颗），审核后存活 2 条

## 2. 屏幕统计（gpt56w）

| 指标 | 值 |
|---|---|
| n_beads | 23 |
| n_failed | 23 |
| actions | {"保持": 0, "补充": 0, "更新": 0, "沉默": 0} |
| action_mismatch | 0 |
| mean_screen_items | 0.0 |
| total_screen_chars_summed_over_beads | 0 |
| total_shown_chars | 0 |
| retired_count | 0 |
| shown_by_kind | {"认": 0, "此刻": 0, "因为前面": 0, "更深": 0} |
| candidates_by_kind | {"认": 23, "此刻": 375, "因为前面": 6, "更深": 2} |
| staleness_hist | {} |

读者视图对照：本稿 {"n_steps": 23, "n_new_lines": 0, "new_chars": 0, "status": {"unchanged": 23}, "mean_screen": 0.0}；run124 B {"n_steps": 14, "n_new_lines": 31, "new_chars": 1839, "status": {"new": 14}, "mean_screen": 2.79}

## 3. 三方盲比（a=本稿读者视图，b=run124 生产稿 B，c=V2A+Gemini 基线）

候选生成模型：a=gflash_web、gpt56w；b=gpt56w；c=gpro 组 gpro_web / gflash 组 gflash_web。“评审=生成者”列标出该评审是哪个候选的生成模型（自评可查）。

| 组 | 评审 | 评审=生成者 | ok/n | 平均名次 a | b | c | 第一 a/b/c | 第一名一致 | 全序一致 | 第一按位置 |
|---|---|---|---|---|---|---|---|---|---|---|
| c_gflash_s1 | luna_noweb | 否 | 3/3 | 3.0 | 1.0 | 2.0 | 0/3/0 | 3/3（b） | 3/3 | {"甲": 1, "丙": 1, "乙": 1} |
| c_gflash_s1 | gflash_web | a,c | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gflash_s1 | gpt56w | a,b | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gflash_s1 | gpt6w | 否 | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gflash_s1 | ALL | — | 3/12 | 3.0 | 1.0 | 2.0 | 0/3/0 |  |  | {"甲": 1, "丙": 1, "乙": 1} |
| c_gpro_s3 | luna_noweb | 否 | 3/3 | 3.0 | 1.0 | 2.0 | 0/3/0 | 3/3（b） | 3/3 | {"乙": 1, "甲": 1, "丙": 1} |
| c_gpro_s3 | gflash_web | a | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gpro_s3 | gpt56w | a,b | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gpro_s3 | gpt6w | 否 | 0/3 | None | None | None | 0/0/0 | — | — | {} |
| c_gpro_s3 | ALL | — | 3/12 | 3.0 | 1.0 | 2.0 | 0/3/0 |  |  | {"乙": 1, "甲": 1, "丙": 1} |

评审原文：

- c_gflash_s1 / luna_noweb / 第1次 映射={"甲": "b", "乙": "a", "丙": "c"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gflash_s1__luna_noweb__r0__he69912483e.md`
- c_gflash_s1 / luna_noweb / 第2次 映射={"甲": "a", "乙": "c", "丙": "b"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gflash_s1__luna_noweb__r1__h247ebf0f09.md`
- c_gflash_s1 / luna_noweb / 第3次 映射={"甲": "c", "乙": "b", "丙": "a"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gflash_s1__luna_noweb__r2__h5597bca88d.md`
- c_gflash_s1 / gflash_web / 第1次 映射={"甲": "c", "乙": "a", "丙": "b"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gflash_s1 / gflash_web / 第2次 映射={"甲": "a", "乙": "b", "丙": "c"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gflash_s1 / gflash_web / 第3次 映射={"甲": "b", "乙": "c", "丙": "a"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gflash_s1 / gpt56w / 第1次 映射={"甲": "a", "乙": "c", "丙": "b"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gflash_s1 / gpt56w / 第2次 映射={"甲": "c", "乙": "b", "丙": "a"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gflash_s1 / gpt56w / 第3次 映射={"甲": "b", "乙": "a", "丙": "c"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gflash_s1 / gpt6w / 第1次 映射={"甲": "c", "乙": "b", "丙": "a"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gflash_s1 / gpt6w / 第2次 映射={"甲": "b", "乙": "a", "丙": "c"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gflash_s1 / gpt6w / 第3次 映射={"甲": "a", "乙": "c", "丙": "b"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / luna_noweb / 第1次 映射={"甲": "c", "乙": "b", "丙": "a"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gpro_s3__luna_noweb__r0__h5b8d444756.md`
- c_gpro_s3 / luna_noweb / 第2次 映射={"甲": "b", "乙": "a", "丙": "c"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gpro_s3__luna_noweb__r1__hbb531ea35d.md`
- c_gpro_s3 / luna_noweb / 第3次 映射={"甲": "a", "乙": "c", "丙": "b"} → ['b', 'c', 'a']：`runs/run134_e7_diag/outputs/cmp134__c_gpro_s3__luna_noweb__r2__h29e275d7d2.md`
- c_gpro_s3 / gflash_web / 第1次 映射={"甲": "a", "乙": "c", "丙": "b"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gpro_s3 / gflash_web / 第2次 映射={"甲": "c", "乙": "b", "丙": "a"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gpro_s3 / gflash_web / 第3次 映射={"甲": "b", "乙": "a", "丙": "c"} → 解析失败(run failed: provider queue held; inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gemini\queue_hold.json)：`—`
- c_gpro_s3 / gpt56w / 第1次 映射={"甲": "b", "乙": "a", "丙": "c"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / gpt56w / 第2次 映射={"甲": "a", "乙": "c", "丙": "b"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / gpt56w / 第3次 映射={"甲": "c", "乙": "b", "丙": "a"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / gpt6w / 第1次 映射={"甲": "c", "乙": "a", "丙": "b"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / gpt6w / 第2次 映射={"甲": "a", "乙": "b", "丙": "c"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`
- c_gpro_s3 / gpt6w / 第3次 映射={"甲": "b", "乙": "c", "丙": "a"} → 解析失败(run failed: gpt2 queue held: inspect D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924\runs\_call_slots\gpt2web\queue_hold.json)：`—`

## 4. 撤下示例（5 条）

（无撤下）

## 5. 上屏的 [因为前面] / [更深]

（无）

## 6. 文件

- 内部稿 `surface__gpt56w__op60.md`；读者视图 `reading__gpt56w__op60.md`；run124 读者视图 `reading__run124B__op60.md`；三方输入 `compare_inputs/`
- 全部提示词/原始输出在 `prompts/`、`outputs/`、`meta/`；缓存 `cache_*.json`；哈希见 `run_manifest.json`
