# 实际调用清单

每条对应实际落盘调用。planned jobs 不等于已调用；失败保留原输出，不暗中降配置或缩输入。

| Job | 模型请求标识 | 段 | 来源数 | 方法 | 状态 | 正文 |
|---|---|---|---|---|---|---|
| S02_G6_A_initial | gpt-6-thinking | S02 | 28 | A | ok | [原始响应](../calls/S02_G6_A_initial/response.txt) |
| S02_G6_OLD_initial | gpt-6-thinking | S02 | 28 | OLD | ok | [原始响应](../calls/S02_G6_OLD_initial/response.txt) |
| S02_FLASH_A2_28 | antigravity-tools/gemini-3.8-flash-high | S02 | 28 | A2 | ok | [原始响应](../scripts/call_results/S02_FLASH_A2_28/response.txt) |
| S02_FLASH_A_28 | antigravity-tools/gemini-3.8-flash-high | S02 | 28 | A | ok | [原始响应](../scripts/call_results/S02_FLASH_A_28/response.txt) |
| S02_G6_A2_28 | gpt-6-thinking | S02 | 28 | A2 | ok | [原始响应](../scripts/call_results/S02_G6_A2_28/response.txt) |
| S02_G6_B2_28 | gpt-6-thinking | S02 | 28 | B2 | ok | [原始响应](../scripts/call_results/S02_G6_B2_28/response.txt) |
| S02_G6_C2_28 | gpt-6-thinking | S02 | 28 | C2 | ok | [原始响应](../scripts/call_results/S02_G6_C2_28/response.txt) |
| S07_FLASH_A2_30 | antigravity-tools/gemini-3.8-flash-high | S07 | 30 | A2 | ok | [原始响应](../scripts/call_results/S07_FLASH_A2_30/response.txt) |
| S07_G6_A2_30 | gpt-6-thinking | S07 | 30 | A2 | ok | [原始响应](../scripts/call_results/S07_G6_A2_30/response.txt) |
| S13_FLASH_A2_30 | antigravity-tools/gemini-3.8-flash-high | S13 | 30 | A2 | ok | [原始响应](../scripts/call_results/S13_FLASH_A2_30/response.txt) |
| S13_G6_A2_30 | gpt-6-thinking | S13 | 30 | A2 | ok | [原始响应](../scripts/call_results/S13_G6_A2_30/response.txt) |
| S13_G6_OLD_30 | gpt-6-thinking | S13 | 30 | OLD | ok | [原始响应](../scripts/call_results/S13_G6_OLD_30/response.txt) |
