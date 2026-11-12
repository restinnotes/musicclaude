# Gemini 调用故障说明（10-20 晚出现）

## 现象

通过 opencode 调用本地 Antigravity Tools 代理上的 `gemini-3.8-flash-high` 时失败率突然升高。本目录 `runs/calls.jsonl` 共记录 171 次 Gemini 调用，成功 154 次。失败集中在 10-20 16 点以后（本机时间），共 3 类：

| 次数 | 时段 | 错误 | 说明 |
|---|---|---|---|
| 9 | 16 点、18 点 | `provider.invalid-output`：“OpenAI Chat received content after the finish reason” | **主要问题**，见下 |
| 2 | 18 点 | `provider.transport`：`ECONNRESET`，“Connection lost while reading the response” | 读取流式响应时连接被断开，耗时 351–503 秒 |
| 5 | 09、16、18 点 | 1–2 秒内失败，stderr 为 `Standalone server exited before reporting readiness` | opencode 的 standalone 服务没起来，多见于并发调用时 |

另有 1 次失败没有错误信息（日志里 error 为空）。

## 主要问题的原始证据

失败调用的完整记录在 `runs/n1_P0_gem_r1/call_fail.log`、`runs/n1_P0_gem_r2/`、`runs/n1_P0x_gem_r1/`，每个目录有 input.txt、stdout.bin、stderr.bin。opencode 报错里附带的那一个流式分片是：

```json
{"id":"chatcmpl-990586cd-…","object":"chat.completion.chunk","created":1792534842,
 "model":"gemini-3.8-flash-high",
 "choices":[{"index":0,"delta":{"content":"task ready"},"finish_reason":"stop"}]}
```

也就是说，**代理先发了一个内容为 `task ready`、`finish_reason` 为 `stop` 的分片，随后又继续推送正文**。opencode 的 OpenAI 兼容客户端（`@ai-sdk/openai-compatible`）认为收到结束标记后不应再有内容，于是整次调用作废。看起来是代理在流式模式下把一条状态消息当作结束分片发了出来。

## 调用方式（复现用）

```
opencode run --standalone --format json --model antigravity-tools/gemini-3.8-flash-high
```

- 提示词通过 stdin 传入（N1 这批约 3,000–4,000 字）。
- 环境变量 `OPENCODE_CONFIG_CONTENT={"permission":"deny","provider":{"antigravity-tools":{"options":{"timeout":false},"models":{"gemini-3.8-flash-high":{}}}}}`。
- provider 定义在 `~/.config/opencode/opencode.json` 的 `antigravity-tools`：`@ai-sdk/openai-compatible`，baseURL 为 `http://127.0.0.1:8045/v1`。
- 代码见 `evo.py` 的 `call_gemini()`。

## 已经能绕过

对同一个代理**直接发非流式请求**（`POST http://127.0.0.1:8045/v1/chat/completions`，`stream=false`），实测 4 秒正常返回，`finish_reason=stop`。我已在 `evo.py` 加了 `call_gemini_direct()`，N1 的 6 篇 Gemini 稿正改走这条路补跑。

这条路不经过 opencode，也不传任何工具，所以同样是离线调用。代价是没有了 opencode 那一层“如果模型用了工具就作废”的检查，不过不传工具时模型本来就无法调用工具。

## 需要你修的地方（任选其一）

1. **代理**（Antigravity Tools，监听 8045 端口）：流式模式下不要在正文前发带 `finish_reason` 的状态分片（`task ready`）；或者把该分片的 `finish_reason` 置为 `null`。最近如果更新过代理，问题可能是更新带来的。
2. **ECONNRESET**：长响应读到一半连接被代理断开，可能与代理的超时或空闲连接回收设置有关。
3. **standalone 启动失败**：并发启动多个 `opencode run --standalone` 时偶发；可能是端口或锁冲突。直连方案不受这一条影响。
