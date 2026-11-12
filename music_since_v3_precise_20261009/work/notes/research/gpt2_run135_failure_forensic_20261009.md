# run135 gpt2 gpt6 失败取证（只读，2026-10-09）

## 结论（确定的）
1. 失败发生在**提交之后**（post-submit），不是提交前。证据：
   - CLI 任务目录 `runs/yi-cookie-repair-20261006/job-d0494cd774a2489985e4e0f8be1d15a4/submitted.json` 存在（`utc=2026-10-09T05:02:32Z`，即本地 01:02:32，与失败 meta 的 started 01:01:37 / ended 01:02:44 窗口吻合）。
   - 该目录 `result.json`: `completed=false`, `provider_phase='post_submit_ambiguous'`, `submission_marker_exists=true`。
2. 该次发送的确实是对 gpt-6 的请求（客户端请求身份），但**不能**据此认定服务端实际用了哪个模型：
   - `started.json`: `model='gpt-6-thinking'`, `thinking_effort='max'`, `provider_interface=true`, `prepare_source='native'`, `prompt_sha256=78c3c7…` 与失败 meta 的 `request_identity.prompt_sha256` 一致（同一输入）。
   - 流里仅有的两条服务端模型记录都是 `gpt-6-thinking`（`stream_protocol_metadata` ×2，05:02:42 与 05:02:43），但这是**中断前的中间元数据**，不是 terminal 证据；且按规则不得凭客户端请求字段认实际型号。
3. 失败的直接原因是**服务端流在 terminal 到来前结束**，客户端按 fail-closed 丢弃 partial：
   - 底层错误（`vendor/gpt2agent/sse.py:35`）：`ChatGPT stream ended before completion; partial output was discarded`（`_IncompleteStreamError`）。
   - 触发条件（`sse.py:1399-1404`）：既无 `[DONE]`+无 continuation，也无 `message_completed`，也无 handoff topic —— 三者全缺即抛错。
   - 本次：`requests.jsonl` 仅 6 行事件（2 次 formal_http_generation + 3 次 stream_protocol_metadata + 1 次 reasoning_ended），**无任何 assistant 文本消息事件、无 `[DONE]`、无 handoff、无 conversation_id**；reasoning 观察只有一条 `reasoning_ended`（duration 3s）。
   - `headless_native_provider.py:352-363`：`proven_finished = completed and terminal and work is False`；三者缺 terminal 即 `proven_finished=false` → 抛 `headless_native_result_rejected`，phase 由 `_failure_phase`（`headless_native_provider.py:430-438`）按 `submitted.json` 存在判为 `post_submit_ambiguous`。
4. **不是客户端字段 schema 漂移/解析错判**：`started.json` 绑定检查字段齐全（model/effort/provider_interface/prepare_source/isolated_runtime/temporary/prompt_sha256），初始化 `result.json` 中 `completed=true`、`sealed_handoff_written=true`、`native_prepare.ready=true`、`native_capture.validated=true`；失败点在 SSE 流阶段，不在提交前校验。
5. **run131 的 experience=thinking 误报结论不否认本次失败**：那是旧 run 的模型归因修正；本次是独立的新鲜短输入在流阶段真实中断，有 `submitted.json` + `result.json` + `requests.jsonl` 三重证据。
6. **本地不可恢复该次结果**：该目录无 `response.txt`、无 `session-state.dpapi`（与成功 job-5814… 有这两份文件形成对照）；且错误语义明确要求丢弃 partial。任何“本地回收”都不合法。服务端侧该 turn 是否继续/可续聊，本地无证据（无 conversation_id 落盘），不得断言为服务端取消。

## 身份对照（防张冠李戴）
- 失败 meta（`runs/run135_gpt2_recheck/meta/run135__gpt6w__short_q.json`）：无 `cli_metadata` 字段（失败路径 `gpt2_adapter.py:205-208` 只落 `error/failure_phase/queue_stop/retry_safe`，不落盘 cli_metadata —— 这是**证据缺口**，不是本案病因）。`request_identity.requested_model='gpt-6-thinking'`，`prompt_sha256=78c3c7…`，`seconds=66.3`，`returncode=1`。
- CLI 侧候选 `job-d0494…`：prompt sha 一致、model 为 gpt-6-thinking、时间窗口吻合（01:01:37 启动 ↔ 目录 mtime 01:02:44），且成功对照 `job-5814…`（gpt56，01:00:37 启动）身份同样吻合。故认定 `job-d0494…` 即本次失败任务。注意：失败 meta 本身没有记录 job_directory，本次是按时间+prompt+模型三重只读推定的（成功 job 有 `cli_metadata.job_directory` 可直证，失败 job 无）。

## 确定 / 不确定
- 确定：提交后、terminal 缺席、fail-closed 丢弃、中断语义、本地无可恢复结果、两长项未提交（queue_stop 机制正常）。
- 不确定（本地证据不够）：服务端为何中断该 gpt-6 turn（限流/模型侧失败/网络/截断均无区分证据）；服务端该 turn 是否实际继续产生 token（无 conversation_id，temporary 会话不可 poll）；是否 gpt-6 特异（样本 N=1，且两长项被 queue_stop 挡住，无法比较）；与 66.3s 超时无直接关系（底层 elapsed 仅 11.4s，worker 累计 64.5s，大部分是初始化 52.3s）。

## 可行的下一步（只读/低风险，不在本笔记执行）
1. 给失败路径也落 `job_directory`（改 `gpt2_adapter.py` 的 fail 调用，把 CLI 已知的 out 目录名记入 meta）—— 解决“每次靠时间推定”的证据缺口。属工程改动，需主会话决策。
2. 下一次重跑只做 `gpt6w short_q` 单发（N=1，不碰长项、不自动重试），看 post_submit_ambiguous 是否复现；若复现再连续 3 次看是否稳定失败。
3. 若要区分“服务端中断 vs 传输中断”，需要在 runner 侧记录 SSE 断开时的传输层信号（HTTP 状态/连接错误），当前 `requests.jsonl` 无此类字段——同样需主会话决策是否加。

## 证据路径一览（均为已存在文件，只读）
- `runs/run135_gpt2_recheck/meta/run135__gpt6w__short_q.json`（失败 meta，无 cli_metadata）
- `runs/run135_gpt2_recheck/outputs/raw/run135__gpt6w__short_q.stderr.txt`（131 字节，exit1 JSON）
- `runs/run135_gpt2_recheck/outputs/raw/run135__gpt6w__short_q.stdout.txt`（0 字节）
- `runs/run135_gpt2_recheck/go.py`（health 判定逻辑：ok+marker+verdict match+terminal）
- `runs/_call_slots/gpt2web/queue_hold.json`（`post_submit_ambiguous`，已设）
- CLI 侧（D:/musicclaude/gpt2agent-safechain）：`runs/yi-cookie-repair-20261006/job-d0494cd774a2489985e4e0f8be1d15a4/{started.json,submitted.json,result.json,requests.jsonl,http-worker-console.txt,headless-initializer/result.json}`；对照成功 `job-5814fbe82233479a99abd757f9243030`
- 实现：`src/chatgpt_provider/headless_native_provider.py:352-363,430-438`；`tools/gpt2_adapter.py:199-208`；`vendor/gpt2agent/sse.py:34-42,1391-1404`

## 合规声明
- 全程只读：未启动任何模型/网页请求，未改 safechain、未删 hold、未重试，未读浏览器 cookie 文件或登录数据库。
- 本笔记不含 session_handle/authorization/cookie/token/凭据；所有敏感字段已脱敏或仅记类型；未复制完整原始日志。
