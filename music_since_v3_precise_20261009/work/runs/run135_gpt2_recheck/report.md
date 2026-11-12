# run135 GPT 网页短/长新鲜复测

未重复杯题；旧 run131 只读。每模型各短/长一次，无自动重试。
route_healthy=False；这是工程证据，不是音乐质量判决。

| job | status | healthy | end marker | seconds | chars | server verdict |
|---|---|---|---|---|---|---|
| run135__gpt56w__short_q | ok | True | True | 60.5 | 173 | match |
| run135__gpt6w__short_q | failed | False | False | 66.3 | 0 | None |
| run135__gpt56w__long_sum | skipped_queue_stop | None | None | None | None | None |
| run135__gpt6w__long_sum | skipped_queue_stop | None | None | None | None | None |

## 失败事实
- run135__gpt6w__short_q：exit 1: {"completed": false, "error_code": "headless_native_result_rejected", "phase": "post_submit_ambiguous", "automatic_retry": false}

