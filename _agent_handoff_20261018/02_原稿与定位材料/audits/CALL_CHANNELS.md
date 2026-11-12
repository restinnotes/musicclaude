# 调用通道审计与交接（2026-10-17）

范围：只读核对本机已有脚本、safechain README/源码、既有 OpenCode provider 配置和历史 metadata；实现新目录的隔离 runner。没有修改共享调用配置或旧脚本，没有重采 A，没有发起收费/模型测试。本轮实际实验由主 agent 执行。

可靠的依据是**本机实际命令与配置**，不是显示名称推断，也不是一次新的可用性测试。未检查当前账户剩余额度、服务端实时健康或未来调用成功率。

## 已确认的实际通道

| 实验名 | 实际请求 ID | 本机入口与配置 | 证据限度 |
|---|---|---|---|
| GPT-6w | `gpt-6-thinking` | `D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd ask --file <完整指令> --model gpt-6-thinking --json` | 旧 STEP4 lane 和现有 CLI 源码一致；要求回包 SSE/终态/哈希。没有本轮新健康探针。 |
| GPT-5.6w | `gpt-5-6-thinking` | 同一 safechain，显式换为此 ID | `research_fill/run_gpt2_fills*.ps1` 使用此精确 ID；不是 `gpt-5.6w` 或 `gpt-5.6-sol`。 |
| Gemini Flash | `antigravity-tools/gemini-3.8-flash-high` | OpenCode `run --standalone --format json --model ...`；provider 配置指向 `http://127.0.0.1:8045/v1` | 当前全局配置仅声明 `gemini-3.8-flash`；既有音乐 runner 在私有 server 的进程配置中声明 `gemini-3.8-flash-high`。新 runner 沿用相同显式声明。 |
| Muse | `opencode2api/muse-spark-1.3-contributor-free#xhigh` | OpenCode private server；provider 配置指向 `http://127.0.0.1:18080/v1` | 全局 model 存在，默认 options 为 medium，因此必须保留 `#xhigh`。本轮没有真实调用或健康验收。 |

OpenCode 可执行文件：

`C:\Users\zuoyi\AppData\Local\Programs\@openchamberelectron\resources\opencode-cli\opencode.exe`

已有 provider 配置：

`C:\Users\zuoyi\.config\opencode\opencode.json`

审计只输出了指定 provider 的模型 ID、非认证选项和“认证字段存在”布尔值，没有显示认证内容。runner 继承该 client 的认证读取方式，不复制密钥，不把密钥放入 argv，也不改变全局文件。

用户所称 mimic Flash/Muse，在已有音乐执行代码中实际对应上述 OpenCode provider。`D:\musicclaude\mimic-cli\bin\mg.cmd` 是另一条固定 GPT-5.6 浏览器通道：固定 `model=gpt-5.6-sol`、`reasoning_effort=xhigh` 和 Temporary/Unpersonalized header，不支持这里需要的自由模型选择。**没有把 mg 当作 Flash/Muse 或 GPT6 的兜底。**

特别注意：mg 的 `check` 会实际发送 `TEST_OK` 模型请求；本次未执行。safechain 自己的 `check` / `health` 在文档中为只读检查，本次也没有执行，避免把检查误作任务必需调用。

## GPT2 命令、完整输入与字节上限

```powershell
# 完整 inline：--file 是正文输入，不是上传附件。
& 'D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd' ask --file '<完整prompt.txt>' --model gpt-6-thinking --json

# 真附件：可以重复 --attach，每个文件单独上传。
& 'D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd' ask --file '<任务指令.txt>' --attach '<完整Pool.txt>' --model gpt-6-thinking --json
```

新 runner 直接执行 `gpt2.cmd` 内部同一个 `.venv-local\Scripts\python.exe` 和 `tools\chatgpt_web\gpt2_cli.py`，使用参数数组、`shell=False`，避免通过 cmd.exe 解释文件路径。请求 `ask` 创建独立会话，不使用之前的 session handle。

| 限制 | 源码实际值 | 影响 |
|---|---:|---|
| 归一化正文 | 65,536 字符 | 超限拒绝，不裁剪。 |
| 默认 native JSON | **65,536 B** | 包含 JSON 编码和其他请求字段；不能用字符数替代，也不能把“低于 60KB”误作整个请求已验证。 |
| 显式研究模式 native JSON | **1,048,576 B** | 仅现有 `MUSIC_RESEARCH_LARGE_NATIVE_BODY=1` 开关。本 runner 不启用/修改它，只记录继承状态。 |
| 附件数量 | 10 | 每个使用 `--attach`，不能在正文里只写路径。 |
| 单附件 | **104,857,600 B（100 MiB）** | 完整快照/哈希验证；更严格的网页限制仍可能失败。 |
| 附件总大小 | **209,715,200 B（200 MiB）** | 总量检查，不分拆、压缩或删输入来绕过。 |

旧 inline 调用即使 prompt 文件有约 60,003 B 且成功，`metadata.attachments=[]` 也只说明其走正文路径，不证明附件上传能力。真附件的完成回包必须包含与本地清单一致的 `name / size / sha256`；原生请求验证还检查每个文件 descriptor 的名称、字节数和 file ID 绑定。

本轮 S02 28 来源完整局部 Pool 构建后，A/B/C/OLD 文件在预检时为 44,379 / 44,227 / 44,292 / 43,442 B。主 agent 已选择先用完整 inline 开始 pilot，后续正式池补入两份已找到的真实 5.6w 来源成为 30。此审计不修改来源身份、不冻结仍在查证的输入，也不把 28 来源结果重新标记为 30 来源结果。

GLOBAL 是独立归档材料，本轮不喂写作者；正文先输出、随后短证据，均由输入构建规则保证。runner 不删除或追加这些内容。若附件路径失败，主 agent 可创建明确的 Flash/Muse job，输入预先冻结的同一份完整全文，同时保留原 GPT6 失败；runner 自身不自动 fallback。

## 安全与配置保持

- safechain 两个 GPT ID 固定 max / Extra High；Temporary、非个性化；保留默认 1536 MiB initializer PSS 上限及原有内存、身份、附件、流完整性守卫。没有降档或取消任何守卫。
- Flash 固定 `gemini-3.8-flash-high`，Muse 固定 `#xhigh`；每 job 独立 `--standalone`，通过该子进程的 `OPENCODE_CONFIG_CONTENT` 设置 `permission: deny`、关闭 provider timeout；这与已有音乐 runner 的有效隔离模式一致。配置只在子进程环境中，不写共享配置。
- upstream 内容安全策略/safetySettings 未由此处配置暴露为可独立认证的实际值。保持继承，不臆称已验证为某个级别，也不设置 `BLOCK_NONE` 等覆盖。
- provider 内部重试或服务端选路无法仅凭这次本地检查完全确认。新 runner 没有自动重试和模型替换；保留可见元数据，并标记未验证的服务端模型身份。Flash/Muse 不会被记录成已验证的 GPT 等价链路。
- 所有 job 独立目录，已有成功/失败/中断目录均不覆盖；相同 job ID 不会重新提交。默认并发 1、最大 2，进程锁只约束新 runner 的批次，手工和旧脚本调用由主 agent 统一协调。

## 主要本地依据

1. `D:\musicclaude\_bead_auto_20261016\step4_out\step4_bead_lane.ps1`：STEP4 明确指定 `gpt-6-thinking`，`--file`，`--json`。
2. `D:\musicclaude\_bead_auto_20261016\research_fill\fill_lane.ps1` 与 `run_gpt2_fills*.ps1`：原始 prompt SHA、两种精确 GPT ID、每 lane 原始输出。旧 lane 只按退出码/长度判定，新 runner 增加完成证据检查；旧文件未修改。
3. `D:\musicclaude\gpt2agent-safechain\README.md` 的 “2026-10-16 stability repair and workload evidence”：真附件、无不确定提交重放、全局初始化锁和各 CLI 进程并发边界。
4. `D:\musicclaude\gpt2agent-safechain\tools\chatgpt_web\gpt2_cli.py`：允许的 ID、固定 max、附件参数、1536 MiB 默认档。
5. `D:\musicclaude\gpt2agent-safechain\src\chatgpt_provider\headless_native_provider.py`：正文归一化、65,536 字符检查、附件清单比较、response SHA、stream/terminal 元数据。
6. `D:\musicclaude\gpt2agent-safechain\vendor\gpt2agent\native_body.py`：64KiB 默认和 1MiB 显式研究开关；`native_attachments.py`：10/100MiB/200MiB 及 descriptor 绑定。
7. `D:\musicclaude\music_since_v3_precise_20261009\work\tools\runner.py`：Flash/Muse 精确模型标识、standalone/permission deny 与 provider timeout 的既有配置。
8. `D:\musicclaude\music_work_since_1008v3_20261009\runs\run115_facts\meta\` 和对应 `outputs\raw\` 的 op60 Flash/Muse：只读取 allowlist 元数据，历史两条命令成功记录；OpenCode JSONL 实际为 step_start + text(time.end)，没有据此推断 usage 或实时可用性。
9. `D:\musicclaude\mimic-cli\README.md`：mg 固定 GPT5.6、`check` 会发模型请求，以及与 safechain/OpenCode 的通道差异。

## 交付与验证

- runner：`D:\musicclaude\_bead_quality_20261017\scripts\run_calls.py`
- schema、命令、产物解释：`D:\musicclaude\_bead_quality_20261017\scripts\RUN_CALLS.md`
- 可离线预检的格式示例：`D:\musicclaude\_bead_quality_20261017\scripts\jobs.example.json`
- 离线测试：`D:\musicclaude\_bead_quality_20261017\scripts\test_run_calls.py`

AST 语法检查通过；示例的当前 OLD/A 完整输入 dry-run 通过；**11 项离线测试全部通过**。测试用合成进程覆盖 raw 留存、hash/附件/完成状态/模型与档位校验、不覆盖、非零退出、超时、预检失败、筛选及并发边界，没有使用模型。主 agent 后续已自行 dry-run 并启动 pilot28 FlashA；其真实结果不属于本次离线验收的宣称范围。收到主 agent 的“保持主逻辑”指示后，只补写本说明与调用审计，不再修改 runner 主逻辑。
