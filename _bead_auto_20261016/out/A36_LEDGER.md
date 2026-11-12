# A36 采用台账（Op.60 固定分段 A Pool / 2026-10-16）

采用规则：每 (允许模型, 研究路线) 恰好 3 份成功且来源可核实的独立轮次；同一输出副本按 sha 去重不算新轮；
同一家族不同版本不互相顶替（gflash36/37 各自存档不计入 gflash 三轮）；V2A 基线单独保留为质量参照，不入 Pool、不混算轮次；
允许模型本轮 = Gemini(3.8-flash/3.1-pro)、Muse、Luna(gpt-6-luna)、GPT-w(gpt-5.6 与 gpt-6 分别标注)；排除：Grok、Opus、Sonnet、旧 Sol。

## 一、采用 36 份

| SRC | 组 | 类型 | run/任务 | 模型名 | prompt版 | 轮 | 字符 | 路径 | sha256(前12) |
|---|---|---|---|---|---|---|---|---|---|
| SRC-gflash-int-1 | gflash-int | historical | run05_saturation s1 | gemini-3.8-flash-high | A_int_v1 | #1 | 6937 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s1.md | 0e685f46bc26 |
| SRC-gflash-int-2 | gflash-int | historical | run05_saturation s2 | gemini-3.8-flash-high | A_int_v1 | #2 | 6371 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s2.md | eafde7307dec |
| SRC-gflash-int-3 | gflash-int | historical | run05_saturation s3 | gemini-3.8-flash-high | A_int_v1 | #3 | 6920 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s3.md | 7dfa9128b167 |
| SRC-gpro-int-1 | gpro-int | historical | run08_final_models s1 | gemini-3.1-pro-high | A_int_v1 | #1 | 6201 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__gpro__op60__s1.md | a23e80e6ed95 |
| SRC-gpro-int-2 | gpro-int | historical | run08_final_models s2 | gemini-3.1-pro-high | A_int_v1 | #2 | 5100 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__gpro__op60__s2.md | 193ffc5d7742 |
| SRC-gpro-int-3 | gpro-int | historical | run44_gpro s1 | gemini-3.1-pro-high | A_int_v1 | #3 | 4628 | music_work_since_1008v3_20261009\runs\run44_gpro\outputs\A-int__A_int_v1__gpro__op60__s1.md | cfa676360bb8 |
| SRC-muse-int-1 | muse-int | historical | run08_final_models s1 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_int_v1 | #1 | 5099 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__muse__op60__s1.md | cd539e72d63d |
| SRC-muse-int-2 | muse-int | historical | run08_final_models s2 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_int_v1 | #2 | 5481 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__muse__op60__s2.md | 3f9685b9285e |
| SRC-muse-int-3 | muse-int | historical | run37_pool_novelty s3 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_int_v1 | #3 | 4852 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s3.md | 2a8ad809cd68 |
| SRC-luna-int-1 | luna-int | historical | run08_final_models s1 | gpt-6-luna | A_int_v1 | #1 | 2839 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__luna_noweb__op60__s1.md | 2b762cda34b0 |
| SRC-luna-int-2 | luna-int | historical | run08_final_models s2 | gpt-6-luna | A_int_v1 | #2 | 2684 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__luna_noweb__op60__s2.md | 6beecfa90cc3 |
| SRC-luna-int-3 | luna-int | fill | A-int__A_int_v1__luna__op60__f1 | codex exec luna_noweb (tool-free) | A_int_v1 | #3 | 2423 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__luna__op60__f1.md | 875b25efb585 |
| SRC-gpt56w-int-1 | gpt56w-int | historical | run106_gpt56_material s1 | gpt-5.6-sol#xhigh (web, mimicgate) | A_int_v1 | #1 | 10578 | music_work_since_1008v3_20261009\runs\run106_gpt56_material\outputs\A-int__A_int_v1__gpt56w__op60__s1.md | 22359c50ba24 |
| SRC-gpt56w-int-2 | gpt56w-int | fill | A-int__A_int_v1__gpt56w__op60__f1 | gpt-5-6-thinking | A_int_v1 | #2 | 4504 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__gpt56w__op60__f1.md | 13f5739f52bb |
| SRC-gpt56w-int-3 | gpt56w-int | fill | A-int__A_int_v1__gpt56w__op60__f2 | gpt-5-6-thinking | A_int_v1 | #3 | 4083 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__gpt56w__op60__f2.md | b889422b0809 |
| SRC-gpt6w-int-1 | gpt6w-int | fill | A-int__A_int_v1__gpt6w__op60__f1 | gpt-6-thinking | A_int_v1 | #1 | 4472 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__gpt6w__op60__f1.md | 15113c9f8c95 |
| SRC-gpt6w-int-2 | gpt6w-int | fill | A-int__A_int_v1__gpt6w__op60__f2 | gpt-6-thinking | A_int_v1 | #2 | 3142 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__gpt6w__op60__f2.md | 9f2c016528ef |
| SRC-gpt6w-int-3 | gpt6w-int | fill | A-int__A_int_v1__gpt6w__op60__f3 | gpt-6-thinking | A_int_v1 | #3 | 5086 | _bead_auto_20261016\research_fill\outputs\A-int__A_int_v1__gpt6w__op60__f3.md | d565dc8d47a2 |
| SRC-gflash-web-1 | gflash-web | historical | run08_final_models s1 | gemini-3.8-flash-high | A_web_v2 | #1 | 10684 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__gflash_web__op60__s1.md | 3348fb17f674 |
| SRC-gflash-web-2 | gflash-web | historical | run08_final_models s2 | gemini-3.8-flash-high | A_web_v2 | #2 | 8803 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__gflash_web__op60__s2.md | 850ca028be19 |
| SRC-gflash-web-3 | gflash-web | historical | run37_pool_novelty s3 | gemini-3.8-flash-high | A_web_v2 | #3 | 10893 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s3.md | 9498fa00ae16 |
| SRC-gpro-web-1 | gpro-web | historical | run08_final_models s1 | gemini-3.1-pro-high | A_web_v2 | #1 | 5484 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__gpro_web__op60__s1.md | 41876a331640 |
| SRC-gpro-web-2 | gpro-web | historical | run08_final_models s2 | gemini-3.1-pro-high | A_web_v2 | #2 | 5295 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__gpro_web__op60__s2.md | 43ceae37c0e9 |
| SRC-gpro-web-3 | gpro-web | historical | run44_gpro s1 | gemini-3.1-pro-high | A_web_v2 | #3 | 5643 | music_work_since_1008v3_20261009\runs\run44_gpro\outputs\A-web__A_web_v2__gpro_web__op60__s1.md | fb33c19c0c6c |
| SRC-muse-web-1 | muse-web | historical | run08_final_models s1 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_web_v2 | #1 | 8134 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__muse_web__op60__s1.md | a925a2019f94 |
| SRC-muse-web-2 | muse-web | historical | run08_final_models s2 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_web_v2 | #2 | 7120 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__muse_web__op60__s2.md | c4e5d9e1c4f6 |
| SRC-muse-web-3 | muse-web | historical | run37_pool_novelty s3 | opencode2api/muse-spark-1.3-contributor-free#xhigh | A_web_v2 | #3 | 7160 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s3.md | 00f552333bd7 |
| SRC-luna-web-1 | luna-web | historical | run05_saturation s1 | gpt-6-luna | A_web_v2 | #1 | 8388 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s1.md | 572b6c477370 |
| SRC-luna-web-2 | luna-web | historical | run05_saturation s2 | gpt-6-luna | A_web_v2 | #2 | 8519 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s2.md | 0ceeec5ba5ea |
| SRC-luna-web-3 | luna-web | historical | run05_saturation s3 | gpt-6-luna | A_web_v2 | #3 | 9081 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s3.md | 848ed054c23d |
| SRC-gpt56w-web-1 | gpt56w-web | historical | run106_gpt56_material s1 | gpt-5.6-sol#xhigh (web, mimicgate) | A_web_v2 | #1 | 17598 | music_work_since_1008v3_20261009\runs\run106_gpt56_material\outputs\A-web__A_web_v2__gpt56w__op60__s1.md | 7bfd64e80946 |
| SRC-gpt56w-web-2 | gpt56w-web | fill | A-web__A_web_v2__gpt56w__op60__f1 | gpt-5-6-thinking | A_web_v2 | #2 | 6805 | _bead_auto_20261016\research_fill\outputs\A-web__A_web_v2__gpt56w__op60__f1.md | ede4ea27125c |
| SRC-gpt56w-web-3 | gpt56w-web | fill | A-web__A_web_v2__gpt56w__op60__f2 | gpt-5-6-thinking | A_web_v2 | #3 | 5666 | _bead_auto_20261016\research_fill\outputs\A-web__A_web_v2__gpt56w__op60__f2.md | 791a2f45f4d2 |
| SRC-gpt6w-web-1 | gpt6w-web | fill | A-web__A_web_v2__gpt6w__op60__f1 | gpt-6-thinking | A_web_v2 | #1 | 7933 | _bead_auto_20261016\research_fill\outputs\A-web__A_web_v2__gpt6w__op60__f1.md | 5bd46a3b77b7 |
| SRC-gpt6w-web-2 | gpt6w-web | fill | A-web__A_web_v2__gpt6w__op60__f2 | gpt-6-thinking | A_web_v2 | #2 | 6808 | _bead_auto_20261016\research_fill\outputs\A-web__A_web_v2__gpt6w__op60__f2.md | 000d58faf54d |
| SRC-gpt6w-web-3 | gpt6w-web | fill | A-web__A_web_v2__gpt6w__op60__f3 | gpt-6-thinking | A_web_v2 | #3 | 8114 | _bead_auto_20261016\research_fill\outputs\A-web__A_web_v2__gpt6w__op60__f3.md | 0ebaf4cbfde3 |

注：fill 名称 fN = 本轮补齐文件；gpt56w 组的 run106 s1 为第 1 轮，fill f1/f2 为第 2/3 轮（通道已在下表注明）。

## 二、保留归档（未采用原件全部保留）

| 角色 | run | 分支 | 模型 | prompt版 | s | 字符 | 路径 |
|---|---|---|---|---|---|---|---|
| V2A基线参照 | run16_baseline_anchor | A-orig | gflash_web | A_orig_V2A | 1 | 9399 | music_work_since_1008v3_20261009\runs\run16_baseline_anchor\outputs\A-orig__A_orig_V2A__gflash_web__op60__s1.md |
| V2A基线参照 | run16_baseline_anchor | A-orig | gflash_web | A_orig_V2A | 2 | 10443 | music_work_since_1008v3_20261009\runs\run16_baseline_anchor\outputs\A-orig__A_orig_V2A__gflash_web__op60__s2.md |
| V2A基线参照 | run02_stage2_r1 | A-orig | gpro | A_orig_V2A | 1 | 5340 | music_work_since_1008v3_20261009\runs\run02_stage2_r1\outputs\A-orig__A_orig_V2A__gpro__op60__s1.md |
| V2A基线参照 | run16_baseline_anchor | A-orig | gpro_web | A_orig_V2A | 1 | 5160 | music_work_since_1008v3_20261009\runs\run16_baseline_anchor\outputs\A-orig__A_orig_V2A__gpro_web__op60__s1.md |
| V2A基线参照 | run16_baseline_anchor | A-orig | gpro_web | A_orig_V2A | 2 | 6466 | music_work_since_1008v3_20261009\runs\run16_baseline_anchor\outputs\A-orig__A_orig_V2A__gpro_web__op60__s2.md |
| kept-archive | run02_stage2_r1 | A-int | gflash | A_int_v0 | 1 | 8569 | music_work_since_1008v3_20261009\runs\run02_stage2_r1\outputs\A-int__A_int_v0__gflash__op60__s1.md |
| kept-archive | run04_stage2_r2 | A-int | gflash | A_int_v1 | 1 | 7506 | music_work_since_1008v3_20261009\runs\run04_stage2_r2\outputs\A-int__A_int_v1__gflash__op60__s1.md |
| kept-archive | run08_final_models | A-int | gflash | A_int_v1 | 1 | 6049 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__gflash__op60__s1.md |
| kept-archive | run115_facts | A-int | gflash | A_int_v1f | 1 | 8587 | music_work_since_1008v3_20261009\runs\run115_facts\outputs\A-int__A_int_v1f__gflash__op60__s1.md |
| kept-archive | run08_final_models | A-int | gflash | A_int_v1 | 2 | 7252 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-int__A_int_v1__gflash__op60__s2.md |
| kept-archive | run05_saturation | A-int | gflash | A_int_v1 | 4 | 7536 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s4.md |
| kept-archive | run05_saturation | A-int | gflash | A_int_v1 | 5 | 7344 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s5.md |
| kept-archive | run05_saturation | A-int | gflash | A_int_v1 | 6 | 7569 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s6.md |
| kept-archive | run05_saturation | A-int | gflash | A_int_v1 | 7 | 7766 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s7.md |
| kept-archive | run05_saturation | A-int | gflash | A_int_v1 | 8 | 6431 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-int__A_int_v1__gflash__op60__s8.md |
| kept-archive | run37_pool_novelty | A-web | gflash_web | A_web_v2 | 4 | 9393 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s4.md |
| kept-archive | run37_pool_novelty | A-web | gflash_web | A_web_v2 | 5 | 14216 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s5.md |
| kept-archive | run37_pool_novelty | A-web | gflash_web | A_web_v2 | 6 | 10417 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s6.md |
| kept-archive | run37_pool_novelty | A-web | gflash_web | A_web_v2 | 7 | 11290 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s7.md |
| kept-archive | run37_pool_novelty | A-web | gflash_web | A_web_v2 | 8 | 10177 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__gflash_web__op60__s8.md |
| kept-archive | run02_stage2_r1 | A-int | gpro | A_int_v0 | 1 | 4875 | music_work_since_1008v3_20261009\runs\run02_stage2_r1\outputs\A-int__A_int_v0__gpro__op60__s1.md |
| kept-archive | run44_gpro | A-int | gpro | A_int_v1 | 2 | 4820 | music_work_since_1008v3_20261009\runs\run44_gpro\outputs\A-int__A_int_v1__gpro__op60__s2.md |
| kept-archive | run44_gpro | A-web | gpro_web | A_web_v2 | 2 | 6159 | music_work_since_1008v3_20261009\runs\run44_gpro\outputs\A-web__A_web_v2__gpro_web__op60__s2.md |
| kept-archive | run02_stage2_r1 | A-web | luna | A_web_v0_L5 | 1 | 7667 | music_work_since_1008v3_20261009\runs\run02_stage2_r1\outputs\A-web__A_web_v0_L5__luna__op60__s1.md |
| kept-archive | run02_stage2_r1 | A-web | luna | A_web_v0 | 1 | 7102 | music_work_since_1008v3_20261009\runs\run02_stage2_r1\outputs\A-web__A_web_v0__luna__op60__s1.md |
| kept-archive | run04_stage2_r2 | A-web | luna | A_web_v2 | 1 | 8637 | music_work_since_1008v3_20261009\runs\run04_stage2_r2\outputs\A-web__A_web_v2__luna__op60__s1.md |
| kept-archive | run08_final_models | A-web | luna | A_web_v2 | 1 | 9699 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__luna__op60__s1.md |
| kept-archive | run08_final_models | A-web | luna | A_web_v2 | 2 | 8594 | music_work_since_1008v3_20261009\runs\run08_final_models\outputs\A-web__A_web_v2__luna__op60__s2.md |
| kept-archive | run05_saturation | A-web | luna | A_web_v2 | 4 | 9418 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s4.md |
| kept-archive | run05_saturation | A-web | luna | A_web_v2 | 5 | 9901 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s5.md |
| kept-archive | run05_saturation | A-web | luna | A_web_v2 | 6 | 8472 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s6.md |
| kept-archive | run05_saturation | A-web | luna | A_web_v2 | 7 | 7971 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s7.md |
| kept-archive | run05_saturation | A-web | luna | A_web_v2 | 8 | 9214 | music_work_since_1008v3_20261009\runs\run05_saturation\outputs\A-web__A_web_v2__luna__op60__s8.md |
| kept-archive | run03_luna_internal | A-int | luna_noweb | A_int_v0 | 1 | 3321 | music_work_since_1008v3_20261009\runs\run03_luna_internal\outputs\A-int__A_int_v0__luna_noweb__op60__s1.md |
| kept-archive | run115_facts | A-int | muse | A_int_v1f | 1 | 5463 | music_work_since_1008v3_20261009\runs\run115_facts\outputs\A-int__A_int_v1f__muse__op60__s1.md |
| kept-archive | run11_harness_compare | A-int | muse | A_int_v1 | 1 | 3872 | music_work_since_1008v3_20261009\runs\run11_harness_compare\outputs\H__muse__A-int__A_int_v1__op60__s1.md |
| kept-archive | run14_muse_en | A-int | muse | A_int_v1_en | 1 | 4307 | music_work_since_1008v3_20261009\runs\run14_muse_en\outputs\A-int__A_int_v1_en__muse__op60__s1.md |
| kept-archive | run14_muse_en | A-int | muse | A_int_v1_en | 2 | 4385 | music_work_since_1008v3_20261009\runs\run14_muse_en\outputs\A-int__A_int_v1_en__muse__op60__s2.md |
| kept-archive | run37_pool_novelty | A-int | muse | A_int_v1 | 4 | 4715 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s4.md |
| kept-archive | run37_pool_novelty | A-int | muse | A_int_v1 | 5 | 3730 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s5.md |
| kept-archive | run37_pool_novelty | A-int | muse | A_int_v1 | 6 | 5379 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s6.md |
| kept-archive | run37_pool_novelty | A-int | muse | A_int_v1 | 7 | 4600 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s7.md |
| kept-archive | run37_pool_novelty | A-int | muse | A_int_v1 | 8 | 3750 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-int__A_int_v1__muse__op60__s8.md |
| kept-archive | run37_pool_novelty | A-web | muse_web | A_web_v2 | 4 | 8415 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s4.md |
| kept-archive | run37_pool_novelty | A-web | muse_web | A_web_v2 | 5 | 9210 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s5.md |
| kept-archive | run37_pool_novelty | A-web | muse_web | A_web_v2 | 6 | 4884 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s6.md |
| kept-archive | run37_pool_novelty | A-web | muse_web | A_web_v2 | 7 | 5874 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s7.md |
| kept-archive | run37_pool_novelty | A-web | muse_web | A_web_v2 | 8 | 5100 | music_work_since_1008v3_20261009\runs\run37_pool_novelty\outputs\A-web__A_web_v2__muse_web__op60__s8.md |

PENDING 补齐轮数：0（见下）