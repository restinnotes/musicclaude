# gpt3 CLI：PROTOCOL_STREAM_UNSUPPORTED（10-21 07:32 起）

## 现象

- 从 2026-10-21 07:32（UTC）起，gpt3 的调用大批失败。
  - 第一次失败：`pro-bridge-20261021T073255567166Z`。
  - 最近一次失败：`pro-bridge-20261021T082014037944Z`。
- 06:00–08:20 之间的 gpt3 任务：187 个成功，53 个失败。
  - 失败码：`PROTOCOL_STREAM_UNSUPPORTED`。
  - 失败信息：`ChatGPT returned unsupported SSE data: unframed_delta_after_v1.`
- 同一时段，第二账号 **gpt4 正常**：两条命令走的是同一套 Pro Bridge 纯 HTTP 传输，用的模型也相同（GPT-6 Thinking / GPT-5.6 Thinking，max）。
- 失败发生在流式返回阶段，通常在提交后 30–400 秒报错。`submitted.json` 存在，说明请求已经提交。
- CLI 输出：`{"completed": false, "error_code": "CONVERSATION_FAILED"...}`。`result.json` 里的 `code` 是 `PROTOCOL_STREAM_UNSUPPORTED`。

## 推测

ChatGPT 对 gpt3 绑定的账号（profile `yi/local-codex-auth`）下发了一种新的 SSE 帧格式：v1 帧之后出现了不带帧头的 delta。`tools/chatgpt_web/pro_bridge_http_probe.py` / `.mjs` 的流解析器不认这种格式。

gpt4 绑定的是另一个账号，目前还没有被下发这种格式，所以正常。这类格式很可能按账号灰度推送，之后 gpt4 也可能遇到。

## 复现

```powershell
D:/musicclaude/gpt2agent-safechain/bin/gpt3.cmd ask "只回答一个数字：1+1=?" --json --model gpt-5-6-thinking
```

注：短问题有时能成功（07:00 前后测过一次，正常）。长回答、长思考的任务更容易触发。可以用一个需要长回答的问题复现。

## 证据位置

- 任务目录：`D:\musicclaude\gpt2agent-safechain\runs\gpt3\pro-bridge-20261021T08*`。
  - `result.json`：失败码。
  - `requests.jsonl`、`http-records.dpapi.json`：原始流记录，已加密。
- 本项目调用日志：`D:\musicclaude\_thread_evo_20261019\runs\calls.jsonl`，按 `"account": "gpt3"` 过滤。

## 修复方向

在 `pro_bridge_http_probe` 的 SSE 解析里，补上对 `unframed_delta_after_v1` 的处理：把 v1 帧之后裸露的 delta 当作正文增量拼接。另外，终止校验要能识别这种新格式。

## 本项目的临时做法

所有调用已切到 gpt4（环境变量 `THREAD_GPT=gpt4`）。gpt3 修好之前不再使用 gpt3。

## 更新（10-21 23:54 UTC）

- **gpt3 已恢复。** 中等长度的问答 7 秒正常完成，`stream_completion` 三项都是 true。
- **gpt4 开始出错。** 从约 23:48 UTC 起，gpt4 的调用全部在约 35 秒时失败。
  - 失败码：`INCOMPLETE_RESPONSE`，即回复没写完，流就结束了。
  - 连续 8 次以上都失败，第一次失败是 `pro-bridge-20261021T234829115244Z`。
- **处理：** Thread 任务改回 gpt3，即 `THREAD_GPT=gpt3`。
