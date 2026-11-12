# 隔离调用 runner 使用说明

入口：`D:\musicclaude\_bead_quality_20261017\scripts\run_calls.py`。

本脚本不生成输入、不重采 A、不补写 GLOBAL、不编辑共享配置。它把主 agent 指定的完整文件冻结为一个 job 的输入，发起一次显式指定通道的调用，保存成功或失败证据。**默认只做离线校验；只有 `--execute` 才会提交模型请求。**

2026-10-17 交接状态：本实现者只做了源码/配置只读检查、OpenCode `run --help` 和离线测试，没有发起任何模型调用。主 agent 已自行运行手工 GPT6 jobs 和 28 来源 pilot 的 FlashA；本 runner 不接管这些既有调用。后续 B/C 由主 agent 根据进展排队。正式 30 来源池应使用新的 job ID 和冻结哈希。

## 立即使用

在 PowerShell 中运行，路径可加引号：

```powershell
python -B D:\musicclaude\_bead_quality_20261017\scripts\run_calls.py --jobs D:\musicclaude\_bead_quality_20261017\scripts\jobs.example.json --dry-run

# 以下会真实调用；由主 agent 选择合适时机执行。
python -B D:\musicclaude\_bead_quality_20261017\scripts\run_calls.py --jobs D:\musicclaude\_bead_quality_20261017\scripts\jobs.example.json --execute --job-id S02_FLASH_A --max-workers 1
```

`jobs.example.json` 仅为格式示例，不是实验计划或已冻结清单。它引用 `../inputs/S02_OLD.txt` 和 `../inputs/S02_A.txt`。身份查证或来源池变化后，先冻结输入，再准备实际 manifest。不要把示例 job 名称当作 28/30 来源身份标识。

可重复使用 `--job-id` 精确选择多个 job，别名是 `--jobid`。默认只执行所选 job；没有筛选时执行 manifest 中所有启用的 job。`max_workers=1` 时按 manifest 顺序执行，不按命令行筛选参数的排列顺序。没有通配符和自动依赖/自动备选调度。

## jobs.json schema v1

下例假设 `jobs.json` 位于实验根目录。所有输入路径和 `output_dir` 都相对于 **manifest 所在目录**，不相对于终端 cwd。实际写出目录必须严格位于本实验 `scripts/` 下；这样不会覆盖其他 agent 的产物。

```json
{
  "schema_version": 1,
  "max_workers": 1,
  "output_dir": "scripts/call_results",
  "jobs": [
    {
      "job_id": "S02_pool30_G6_OLD_r1",
      "channel": "gpt2",
      "model": "gpt-6-thinking",
      "prompt_file": "inputs/S02_OLD.txt",
      "attachments": [],
      "timeout_seconds": 7200,
      "min_response_chars": 100,
      "labels": {"pool": "30", "method": "OLD"}
    },
    {
      "job_id": "S02_pool30_FLASH_A_r1",
      "channel": "opencode",
      "model": "antigravity-tools/gemini-3.8-flash-high",
      "prompt_file": "inputs/S02_A.txt",
      "attachments": [],
      "timeout_seconds": 7200,
      "min_response_chars": 100,
      "labels": {"pool": "30", "method": "A"}
    }
  ]
}
```

| 字段 | 规则 |
|---|---|
| `schema_version` | 必须为 `1`。未知顶层字段和未知 job 字段会拒绝，不会悄悄忽略。 |
| `max_workers` | 默认 `1`，只接受 `1` 或 `2`；`--max-workers` 可显式覆盖。 |
| `output_dir` | 默认 `scripts/call_results`，相对于 manifest。若 manifest 放在 `scripts/`，应填 `call_results`，如示例文件。 |
| `jobs` | 非空数组。`job_id` 不区分大小写去重，避免 Windows 文件名冲突。 |
| `job_id` | 必填，字母/数字开头，可包含 `_ . -`，最长 120 字符；拒绝 Windows 保留名和结尾点。每个新输入/新尝试用新 ID。 |
| `channel` / `model` | 必填，使用下表中的明确配对；不接受显示别名或自动推断。 |
| `prompt_file` | 必填，UTF-8 或 UTF-8 BOM 完整文件。不拼接、不截断、不提取、不重写内容。 |
| `prompt_sha256` | 可选，但冻结后的正式实验应填写；是**整个原始文件字节**的 64 位小写 SHA256。不符则 `failed_preflight`，零调用。 |
| `attachments` | 默认 `[]`。GPT2 支持路径字符串或 `{"path":"...","sha256":"..."}`。可选哈希同样绑定完整原始字节。OpenCode 本版只允许空数组，必须提供固定的完整 inline 文件。 |
| `timeout_seconds` | 默认 `7200`，接受 1–86400 秒。不是缩减模型 reasoning budget。超时不重试。 |
| `min_response_chars` | 默认 `1`；可显式设质量门槛。低于门槛保留正文并判失败，不补写或重试。 |
| `enabled` | 可选布尔值，`false` 时跳过，可用于尚未冻结/尚不应运行的 job。 |
| `labels` | 可选的实验标记，仅存档，不进入模型 prompt。不要放认证信息。 |

| channel | model | 请求配置 |
|---|---|---|
| `gpt2` | `gpt-6-thinking` | GPT-6w，固定 max / Extra High、Temporary、非个性化、1536 MiB initializer PSS 上限。 |
| `gpt2` | `gpt-5-6-thinking` | GPT-5.6w，配置同上。注意 ID 中是 `5-6`，不是 `5.6w`。 |
| `opencode` | `antigravity-tools/gemini-3.8-flash-high` | Gemini Flash high，独立 server，`permission: deny`，provider timeout 关闭，完整 prompt 走 stdin。 |
| `opencode` | `opencode2api/muse-spark-1.3-contributor-free#xhigh` | Muse xhigh，独立 server，同样 deny 工具并关闭 provider timeout。此轮没有真实验证 Muse 可用性。 |

可用 `Get-FileHash -Algorithm SHA256 -LiteralPath <输入>` 读取冻结哈希。对可变的 `inputs/` 文件，只填哈希还不够表达实验来源身份；`job_id` 和 `labels` 同时注明池版本。runner 在预检时读入完整 prompt，执行时保存并使用这份字节快照，即使排队期间原始路径变化，也不会换成后来内容。

## 真附件与 inline 的边界

GPT2 真附件示例：

```json
{
  "job_id": "S02_pool30_G6_attach_r1",
  "channel": "gpt2",
  "model": "gpt-6-thinking",
  "prompt_file": "inputs/S02_task.txt",
  "attachments": ["inputs/S02_complete_pool.txt"],
  "timeout_seconds": 7200
}
```

`prompt_file` 是任务指令正文；`attachments` 才是文件上传。runner 快照附件原始字节，并要求回包 `metadata.attachments` 与提交清单的 `name / size / sha256` 完全一致。非空附件请求回包为空数组会失败，不会记录为附件成功。正文只是写出本地路径不代表上传。

现有 safechain 限制同时包括：

- 归一化后的 prompt 最多 **65,536 字符**。
- native 请求 JSON 默认最多 **65,536 字节**，包括 prompt 以外的协议字段。字数合格并不保证字节数合格。runner 预检只计算 prompt JSON 的下界，不能预知完整 native JSON 的额外开销；最终由现有通道继续严格检查。
- 附件最多 **10 个**，单文件最多 **104,857,600 B（100 MiB）**，合计 **209,715,200 B（200 MiB）**。附件名称不可重复，文件不可为空。
- 现有源码有显式研究开关 `MUSIC_RESEARCH_LARGE_NATIVE_BODY=1`，对应 native JSON 上限 **1,048,576 B**。runner 不设置、删除或改写该开关，只记录继承后的有效上限；该开关不取消 65,536 字符限制。本交接没有使用它或改共享配置。

2026-10-17 本地预检时 S02_A/B/C/OLD 分别为 44,379 / 44,227 / 44,292 / 43,442 B。这是尚未补全 30 来源时的快照大小，不应套用到后来重建的输入；每次 dry-run 都显示实际字节数、字符数和哈希。

safechain 自身会去掉单个前导 BOM、将 CRLF/CR 转为 LF、去掉末尾空白。runner 保存原始 `prompt.txt` 及原始哈希，并另外记录 `normalized_prompt_*`，明确这项通道既有归一化。OpenCode 走原始文件字节 stdin；不把 GPT 的归一化强加给 Flash/Muse。由于后者 CLI/上游不提供最终请求正文哈希，runner 不宣称已独立验证上游逐字收到。

附件失败时，不会自动变成 inline，也不会改走 Flash/Muse。由主 agent 显式增加另一个 job，指向事先冻结的**完整全文文件**；原 GPT 失败目录保留。GLOBAL 是否排除、正文先于短证据等内容规则，由构建输入的一侧决定，runner 不做任何内容级过滤。

## 产物与成功判定

每个 job 独占 `output_dir/job_id/`：

| 文件 | 内容 |
|---|---|
| `prompt.txt` | 预检时读到的完整原始文件字节。 |
| `attachments/` | 完整附件快照，保持原文件名，并复核字节数/哈希。 |
| `job.json` | 该 job 的配置快照，不复制全局凭据。 |
| `command.json` | 实际 argv、stdin 方式、显式策略和配置指纹；不保存完整环境变量。 |
| `started.json` | 子进程启动前证据；只有它不代表服务端已接受或已完成。 |
| `stdout.raw` / `stderr.raw` | 子进程原始二进制 stdout/stderr，不转码、不截尾；即便失败也保留。 |
| `response.txt` | 可解析的正文。失败也可能有正文，因此**不能以文件存在判断成功**。 |
| `metadata.json` | 最终状态、错误码、退出码、时间、大小/哈希、通道元数据、实际可见的完成证据。 |
| `cwd/` | 此 job 独立工作目录。 |

GPT2 成功必须同时满足：进程退出 0；`completed=true`；请求模型与 metadata.model 一致；effort=max；SSE DONE；message completed；无 continuation pending；成功 assistant terminal；正文 SHA256 一致；附件清单一致；如回包提供 server model slug，也必须一致；正文达到显式最短门槛。

Flash/Muse 成功要求退出 0、有正文、JSONL 可解析、没有错误事件或工具事件、完成证据成立。已知旧 OpenCode CLI 通常仅输出 `step_start` 和带 `time.end` 的完整 text part，而不暴露 `step_finish`：此时记录 `completion_basis=CLI_exit_0_and_text_time_end`、`server_completion_verified=false`，不伪称掌握服务端 finish_reason、usage 或底层模型身份。如果确实有 terminal event，则必须是成功终态；`length` 等状态失败。多个 text part 按顺序以两个换行连接到 `response.txt`，每个 part 本文不裁剪，完整原始 JSONL 始终另存。

OpenCode 每个 job 使用 `--standalone` 和仅属于子进程的 `OPENCODE_CONFIG_CONTENT`，沿用已有 provider 认证。任何工具事件都会让这个无工具样本失败，包括被拒绝的工具尝试；不会自动重跑。共享配置、旧脚本、账户和模型服务均不修改。底层 CLI/provider 自身的重试机制本次没有独立验证；runner 自己没有重试循环、模型替代或通道切换。

raw 文件可能包含私有 session handle 和模型回复，不要公开粘贴。派生 metadata 会隐藏凭据字段和 session_handle；终端只输出 job ID、状态、静态错误代码和产物路径，不打印模型正文、raw、凭据或全局配置。

## 隔离、并发、退出码

- 默认并发 1，硬上限 2。`scripts/.run_calls.lock` 保证本 runner 同时只有一个 batch owner，即使 output_dir 不同也不能并行启动第二批。本地独占锁的作用域只覆盖本 runner，**不覆盖手工 gpt2、旧脚本或其他服务已启动的调用**；主 agent 统一安排外部并发。
- 每个 job 创建目录时使用原子独占 reservation。目录已存在，无论成功、失败还是中断残留，都返回 `exists_not_overwritten`，不覆盖、不自动续跑。新尝试必须用新 job ID，并人工判定是否允许重放。
- 单个 job 失败不阻止其他有效独立 job；没有自动 fallback、失败分支、resume 或重采样。默认每次都是新会话。
- 超时/中断只终止这个 job 启动的本地进程树，保留部分 raw，并记录 `unknown_do_not_automatically_replay`。远程请求可能已接受；本地终止不证明远程取消成功。
- 若进程异常退出导致锁遗留，runner 不自行猜测锁过期。先核实记录 PID 对应的 batch 已退出，再人工清理这一**精确锁文件**；不要删除结果目录来“重试”。
- 总退出码：`0` 所有实际运行 job 成功或离线预检全部通过；`1` 执行批存在失败、预检失败、超时或已有目录冲突；`2` manifest/schema、并发设置、锁问题，或者 dry-run 的 job 预检失败；`130` 用户中断。`enabled=false` 是明确跳过，不是成功样本。

## 已完成的离线验证

```powershell
python -B D:\musicclaude\_bead_quality_20261017\scripts\test_run_calls.py
```

2026-10-17：**11 项通过**，约 2 秒。全部使用 fixture bytes 和本地合成 Python 子进程，mock 掉真实命令构造；没有调用 GPT2、OpenCode 模型、HTTP 模型接口或健康探针。覆盖完整 prompt/归一化哈希、错误哈希/模型拒绝、字节限制、真实附件清单匹配、流未完成/档位不匹配、OpenCode 错误与工具事件、stdout/stderr 原始字节、私有 handle 脱敏、禁止覆盖、非零退出仍保存正文、超时不可安全重放、预检失败留证、筛选、默认 dry-run 和并发上限。
