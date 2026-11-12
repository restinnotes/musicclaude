# run131 gpt2 烟雾测试报告

生成时间：2026-10-09 00:28:26

只记录事实证据，不做内容评价。suspect = 耗时<60s，或水杯题答案≠8，或服务端 slug 与请求不符。（用户规则：疑似≠降智；水杯题正常应 >3 分钟且答 8。）

| job | 模型 | 状态 | 耗时(s) | 输出字数 | 服务端 slug | 水杯=8? | suspect |
|---|---|---|---|---|---|---|---|
| run131__gpt56w__short_q | gpt-5-6-thinking | ok | 61.3 | 135 | gpt-5-6-thinking, thinking（mixed） | - | 是：slug_mismatch |
| run131__gpt6w__short_q | gpt-6-thinking | failed（exit 1: {"completed": false, "error_code": "headless_native_） | 85.8 | 0 | 无（no_slug） | - | 否 |
| run131__gpt56w__long_sum | gpt-5-6-thinking | failed（exit 1: {"completed": false, "error_code": "headless_native_） | 68.5 | 0 | 无（no_slug） | - | 否 |
| run131__gpt6w__long_sum | gpt-6-thinking | failed（exit 1: {"completed": false, "error_code": "headless_native_） | 69.5 | 0 | 无（no_slug） | - | 否 |
| run131__gpt56w__cup | gpt-5-6-thinking | ok | 541.3 | 6618 | gpt-5-6-thinking, thinking（mixed） | 是 | 是：slug_mismatch |
| run131__gpt6w__cup | gpt-6-thinking | ok | 419.0 | 10208 | gpt-6-thinking, thinking（mixed） | 是 | 是：slug_mismatch |

## 水杯题抽取候选（启发式，供人工核对）

- run131__gpt56w__cup：答案=8，候选=[8, 8]，耗时 541.3s
- run131__gpt6w__cup：答案=8，候选=[8, 8, 8, 8]，耗时 419.0s

CLI 版本（safechain HEAD）：dfca0fd

原始产物：outputs/<job>.md，outputs/raw/<job>.stdout.txt / .stderr.txt，meta/<job>.json（smoke 字段）。
