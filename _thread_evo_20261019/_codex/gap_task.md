# 任务：gpt3 提交间隔改成“按真正发出算”，并等上一个开始返回后才发下一个

工作目录：D:\musicclaude\_thread_evo_20261019。本机 Windows PowerShell 5.1 会把无 BOM 的 UTF-8 中文文件读成乱码，读写文本一律用 Python（encoding="utf-8"）。
请自主完成并自行验证，过程写到 `_codex/gap_log.md`；最后只回报：成功/失败、主要修改、测试情况、重大风险。

## 现状与问题
`gpt3_call.py` 的 `_space_submission()` 在 GATE 锁里只保证“两次**启动 gpt3 命令**之间 ≥ GAP(20s)+0–10s 抖动”，STAMP 记的是命令启动时刻；随后在锁外 `subprocess.run` 跑完整个调用。
但 gpt3 CLI 启动后要先做鉴权、`/backend-api/models`、sentinel、prepare，带附件时还要上传，之后才真正提交对话。
所以带附件的调用真正发出可能比启动晚十几秒，下一次的真实间隔就会小于 20 秒（今天 89 次里有 2 次，最短 16.6 秒）。
用户要求：**下一个必须等上一个真正发出去、开始返回（开始思考）之后，再从那一刻起隔够 20 秒才发。**

可用的证据（gpt3 每次调用一个任务目录 `D:\musicclaude\gpt2agent-safechain\runs\gpt3\pro-bridge-<UTC时间戳>`，即 `evo.GPT3_RUNS`）：
- `prompt.txt`：发送的正文（就是我们 input.txt 的内容；超长时是那句“这次的任务全文太长……”）；`started.json`；
- `submitted.json`（`{"utc": ...}`，真正提交对话的时刻）；
- `generation-network.json`：流的进度，`first_chunk_ms` 非空表示已经开始返回。
`evo.find_job()` 有按 prompt 匹配任务目录的现成逻辑可以参考。

## 要改的（只改 gpt3_call.py 的提交节奏）
1. 把“启动命令 + 等它真正发出并开始返回”放进同一个 GATE 锁里：
   - 进锁后先等：距上一次**真正提交**（STAMP）≥ GAP + random.uniform(0,10)；
   - 用 `subprocess.Popen` 启动 gpt3（参数与现在完全相同），记下 t0；
   - 在锁内轮询（约每 1 s）：找到 t0 之后新建、`prompt.txt` 与本次 message 相同的任务目录；等到它的 `submitted.json` 出现且 `generation-network.json` 里 `first_chunk_ms` 非空；或者进程已经退出；或者超时（180 s，超时就记一条警告继续）。
   - 把 STAMP 写成真正提交的时刻（取 submitted.json 的 utc 转 epoch；拿不到就用当前时间），然后释放 GATE 锁。
2. 锁外等进程结束（`communicate()`），之后的 stdout/stderr 处理、成功判定、记录、重试、停止规则全部保持原样。调用结束后**不要**再把 STAMP 改成结束时刻（现在代码在 run 之后会写一次 STAMP=结束时间，这一行去掉，否则会把间隔算错）。
3. call.log 里加两个字段：`submitted_utc`（真正提交时刻）和 `gap_since_prev_submit_s`（与上一次真正提交的间隔），方便以后核对。
4. 其余一律不变：并发槽位（gpt3_slots.txt）、GAP 默认值、`--allow-topic-stream`、附件处理、NO_WEB 规则、模型和推理强度判定、停止词、失败计数。

## 验证
- 写离线测试 `_codex/test_gap.py`：用一个假的 gpt3 可执行（Python 脚本，经 monkeypatch 替换 gpt3_call.GPT3，或用 .cmd 包装）模拟：启动后延迟若干秒才在临时目录里创建任务目录、写 prompt.txt、submitted.json、generation-network.json，再延迟返回 JSON。把 evo.GPT3_RUNS、evo.RUNS、STAMP、GATE、LOCK 都指到临时目录。
  并发起 3–4 个调用（含一个“上传慢”的，提交延迟 15 s），确认：任意两次真实提交间隔 ≥ GAP（测试里可把 GAP 调小，比如 3 s，延迟按比例缩小）；后一个一定在前一个 first_chunk 之后才启动；结果解析、call.log 新字段正确；超时和进程提前退出两条路径都能走通。
- 测试不得发出任何真实的模型调用，不得写入真实的 runs/、STAMP、锁文件。

## 边界
- 不得改变实验语义：提示词、联网权限、模型和推理参数、工具能力、珠子输入、评审标准都不能动；只改提交节奏和记录字段。自查并在回报里说明。
- 不改 evo.py 的调用语义（如需复用 find_job 可以 import，但不要改它）；不改 mg_call.py；不动缓存保温机制和 watchdog，不新增定时任务或轮询（锁内对本次任务目录的短轮询除外）。
- 现在有 6 个后台进程（v6fix.py fix …、v6dirs.py whole/rad …）正在用旧的 gpt3_call 跑，**不要停它们、不要动它们的 runs/ 目录**。改完的文件只对之后新启动的进程生效，重启由我来做。
- Windows 下 msvcrt 锁的写法照现有代码。无法完成或有明显风险时停下回报。
