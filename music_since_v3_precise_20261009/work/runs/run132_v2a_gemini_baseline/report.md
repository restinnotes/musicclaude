# run132 V2A 原版 × Gemini 基线

生成时间：2026-10-08 18:42:41

提示词 = prompts/A_orig_V2A.txt 仅替换 {{WORK}}（原文见 prompts_src/）。以下只列机械指标，不做质量判断。suspect = 代理固定道歉句 / 拒答 / <60s 却有 ≥2000 字 / 失败；suspect 已用新 job_id 重跑一次，原件保留。

| job | 模型 | 作品 | 状态 | 耗时(s) | 字数 | 含 mm. 标记 | 段落数 | suspect |
|---|---|---|---|---|---|---|---|---|
| run132__op60__gpro_web__s1 | gpro_web | op60 | ok | 56.7 | 2131 | 是（6） | 12 | 是：<60s with 2131 chars |
| run132__op60__gpro_web__s2 | gpro_web | op60 | ok | 49.7 | 2012 | 否 | 11 | 是：<60s with 2012 chars |
| run132__op60__gpro_web__s3 | gpro_web | op60 | ok | 71.9 | 1958 | 是（7） | 10 | 否 |
| run132__op61__gpro_web__s1 | gpro_web | op61 | ok | 55.6 | 2107 | 是（5） | 11 | 是：<60s with 2107 chars |
| run132__op61__gpro_web__s2 | gpro_web | op61 | ok | 63.0 | 2152 | 是（7） | 10 | 否 |
| run132__op61__gpro_web__s3 | gpro_web | op61 | ok | 77.5 | 2073 | 是（6） | 10 | 否 |
| run132__op52__gpro_web__s1 | gpro_web | op52 | ok | 63.0 | 2234 | 是（13） | 8 | 否 |
| run132__op52__gpro_web__s2 | gpro_web | op52 | ok | 70.6 | 2062 | 是（8） | 11 | 否 |
| run132__op52__gflash_web__s1 | gflash_web | op52 | ok | 98.3 | 3635 | 是（25） | 30 | 否 |
| run132__op60__gflash_web__s1 | gflash_web | op60 | ok | 105.4 | 3571 | 是（7） | 19 | 否 |
| run132__op61__gflash_web__s1 | gflash_web | op61 | ok | 137.0 | 4162 | 是（15） | 31 | 否 |
| run132__op60__gpro_web__s1__retry1 | gpro_web | op60 | ok | 64.3 | 1923 | 是（9） | 9 | 否 |
| run132__op60__gpro_web__s2__retry1 | gpro_web | op60 | ok | 86.4 | 2089 | 是（8） | 11 | 否 |
| run132__op61__gpro_web__s1__retry1 | gpro_web | op61 | ok | 78.1 | 2034 | 是（6） | 12 | 否 |

可用槽位：11/11

原始产物：outputs/<job>.md，outputs/raw/，meta/<job>.json；作业清单 jobs.json。
