# 任务：历史 SSE 归档的路由字段普查（只写一个离线脚本 + 跑它，不联网）

输入目录：D:\ai-stack\gpt2agent\.sse-archive （约 1749 个 .jsonl，只读，绝不修改/移动/删除）。
每个文件每行是 {"received_at": ISO时间, "event": <字符串>}，event 字符串通常是一段 JSON（ChatGPT 网页 SSE 的一帧），也可能是非 JSON 文本（如 "[DONE]"、"v1" 之类）。文件名形如 20260923T001007-sse-<hex>.jsonl 或 ...-handoff-<hex>.jsonl。

写 D:\musicclaude\webchat-nodegrade\tools\archive_census.py（Python 3 标准库），对每个文件输出一行记录到 D:\musicclaude\webchat-nodegrade\out\archive_census.jsonl，字段：
- file, kind(sse/handoff), start(第一行 received_at), duration_s(末行-首行)
- 递归遍历每帧 JSON（包括 {"p":..,"o":..,"v":..} 这种 patch 格式里的 v，以及 v 为 list 的批量 patch），收集以下键的所有出现值（去重，保持首次出现顺序）：
  model_slug, resolved_model_slug, default_model_slug, requested_model_slug, thinking_effort, requested_model_experience, turn_use_case, turn_mode, tool_invoked, tool_name, fast_convo, warmup_state, server_ttfvt_ms, content_type, channel, reasoning_status, marker, recipient
- 另外把 server_ste_metadata 对象（若出现）完整存一份（取最后一次出现），但删除值看起来像 JWT/token 的字段（值为字符串且以 "eyJ" 开头，或键名含 token/cookie/authorization/sentinel/conduit，大小写不敏感）。
- has_cot_token: 是否出现 marker == "cot_token"
- has_reasoning_recap: 是否出现 content_type == "reasoning_recap"
- user_prompt_head: 第一个 author.role=="user" 消息 content.parts 首段的前 80 个字符
- assistant_tail: 最后一个 author.role=="assistant" 且 channel 为 final 或 null 的文本的最后 200 字符（若能从 patch 拼出最好；拼不出就取出现过的最长 assistant parts 文本的末尾 200 字符，并加字段 assistant_tail_method 说明用了哪种方法）
- resume_token 等 token 类的值一律不写入输出。

再写一个汇总输出 D:\musicclaude\webchat-nodegrade\out\archive_census_summary.md：
1. 按日期（start 的 UTC 日期）× turn_use_case 的计数表；
2. 按日期 × tool_name 的计数表；
3. 按日期 × thinking_effort（若有）× has_cot_token 的计数表；
4. 列出所有 turn_use_case 为 thinking 以外值的文件前 30 个（file, start, model_slug, turn_use_case, tool_name, duration_s, user_prompt_head）。
5. 列出 duration_s 最长的 20 个 sse 文件（同样字段 + has_cot_token + assistant_tail 前 80 字）。

跑完后在汇报里贴出 summary.md 的前 120 行。只做这些，不要分析结论。
