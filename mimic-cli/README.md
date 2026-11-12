# 独立 MimicGate CLI

> 2026-10-08 UTC（纽约 10-07 晚）：最新修复已部署到原 yi 容器。显式开启原生浏览器策略并关闭额外 stealth 注入，保留 Patchright；发送前不再读取页面主执行环境，以免诊断触发驱动 Runtime 操作。没有重新导入原 profile/cookie。原链路 `mg probe cup` 已完整回答 **8、8**，两轮耗时分别为 1185.422 秒、781.110 秒，网页 `Worked for 17m 30s`、`Worked for 11m 40s`；第二轮在原容器正常重启后完成。两轮 SSE DONE 完整、无 OOM，原始证据分别在 `runs/20261008T010053.024441Z-b4ef4111/`、`runs/20261008T012442.872642Z-4dcbb81c/`。此前原容器一轮为网页 Error in message stream / incomplete_response，无最终答案，不能统计为答 6。单浏览器的隔离副本开关对照已完成，随后恢复了同一个原容器及四个持久卷；02:41 UTC 的实际 `mg check` 返回 TEST_OK，耗时 29.625 秒。原容器在线、实验副本停止。功能验收通过与精确因果结论分开记录。
>
> 额外 stealth 开关对照：保留原生浏览器身份策略，同一个副本、profile 卷、代码哈希、UA 提示配置和 2 GiB 内存上限；开启、关闭额外脚本都完整答 **8**，分别耗时 723.609 秒、1237.109 秒，网页 Worked 时间为 10m43s、19m11s。回答完成后，仅在副本既有隔离执行环境里读到 languages 分别为 `["en-US","en"]`、`["en-US"]`，确认开关实际生效；未读取页面主执行环境。两轮 DONE 完整、无 OOM。此对照不支持把能力差异归因于其余额外脚本，不能宣称已证明唯一责任因素。完整对照在 `experiments/yi-rootcause/20261007T2135Z/causal-stealth-pair-result.json`。第二轮 Windows 可用物理内存曾降到 0.669 GiB，因此结束后停下所有本任务实验副本；用户批准的另一闲置 clone 也已正常停止并保留登录卷，没有停止其他服务或关闭用户 Chrome。
>
> 上述答 8 仍缺少 `browser_context`，且只带三个浏览器原生基础 UA 提示。补高熵提示的旧实验出现过 8 和 6，不能视为稳定修复。缺少这两组字段无法单独解释能力差异。脱敏元数据对照见 `experiments/yi-rootcause/20261007T2135Z/candidate-source-wire-comparison.json`；未知服务器内部决策仍不可从客户端日志证明。
>
> 10-07 历史回归审计：08:00–14:40 UTC 原服务记录 328 次实际生成，08 点 89 次、09 点 210 次，观察到的响应流重叠峰值为 3。最短实际发送尝试间隔 11.930 秒、最短 wire 间隔 11.923 秒，没有低于五秒的发送。最后一次答 8 与第一轮答 6 的请求元数据完全一致，已记录的设备摘要、实际认证数量、上下文 cookie 名称及客户端头也一致；此范围未记录认证丢失、删除指令或服务生命周期重启。两次 160-cookie 保护均为 submission_blocked，inactive_temporary_cookie_count=0，没有执行清理或修改认证。以上支持排除“本次回归由掉登录或忘记五秒间隔单独造成”；高历史负载与质量差异的因果仍未证明。其他 cookie 值、当时前端资源版本和服务端 STE 元数据没有完整历史记录，不能把缺失证据当成相同。报告见 `historical-last8-first6-wire-comparison.json`、`historical-workload-0800-1440.json`。
>
> 待加载的诊断增强：本地 request_observer 现在利用既有 CDP ExtraInfo，在内存中比较六个白名单上下文/设备 cookie，跨 worker 记录新增、消失、变化名称及进程内 revision，不保存值或摘要。乱序/缺失证据不更新比较基线，也不增加浏览器脚本、导航或生成请求。29 项观察器测试已通过；当前原服务仍运行旧版，主机物理余量不足 2 GiB，尚未重启加载。部署状态以 `pending-cookie-sequence-observer.json` 为准，不宣称已上线。
>
> 断流诊断现记录有限网络错误类别、请求持续时间、最后收包时间与结束时空闲时长，并识别明确的服务端错误帧，不保留错误正文。SSE DONE 之后的浏览器取消与 DONE 之前的失败分开记录。原生策略由 `config/native-browser.env`、`native-browser-policy.json`、`native-hints.json` 和正式部署脚本维持。当前单题实验复用既有浏览器，门槛为 1 GiB 物理/3 GiB 提交；启动或重启要求 2/5 GiB。已有 Windows 六小时探针的 3/3 GiB 门槛保持不变。本轮最低物理余量 2.35 GiB、提交余量 6.574 GiB，容器峰值约 1.48 GiB。

> 2026-10-06：已复现 Chromium 的站点 cookie 容量淘汰风险，新增旧 Temporary cookie 定向回收及每轮结束回收，原 yi 重启后的 171→99 回收保留了认证。并发上限仍为 8，发送间隔至少 5 秒。该机制的 8 路 cookie 生命周期已验证；尚不能把它等同于 8 路真实长请求能力验证。水杯题能力差异继续调查，最新证据见 `experiments/yi-rootcause/20261006T1625Z/REPORT.txt`。
>
> 标准等待改为默认 30 分钟，并补齐“存在 Stop 时 Copy 不能判完成”的检测。杯题截图在 worker 回收前生成，自动导出并核对 SHA256；缺少截图的 yi probe 不判为通过。旧记录中的拒绝作答/下界 6 不会当作精确答案 6。
>
> 2026-10-06 内存控制：单题验收复用一个既有浏览器，发送前至少保留 3 GiB 物理内存和 3 GiB Windows 全局提交余量，实验期间每 5 秒记录两项指标。此前 1.5 GiB 提交门槛没有为用户同时打开其他应用留下足够余量，因此后续提高为 3 GiB。这个预算只适用于一个请求，八路压力测试需要另行评估。已有 Windows 六小时探针采用相同单题门槛；Docker 停止、网关已有活动/排队请求或余量不足时记录跳过，不自动启动 Docker，也不将跳过判成答案异常。原网关并发上限仍为 8。
>
> Cookie 恢复不能只凭“认证存在”认定能力恢复。本轮“仅更新原生认证 token”的完整杯题为 6；导入同账号原生 Chrome 的完整非会话 cookie 集合后，隔离副本在原 Chrome 153 和原洛杉矶时区完整回答 8。恢复时保留认证、设备和客户端会话上下文，不导入旧对话的 conv_key/history_off；先备份 Chrome 加密 cookie 数据库，再向空闲浏览器添加，避免全站清空。原 yi 的完整集合已于 18:24 UTC 导入，原链路完整回答 8 两次，第二次为同一容器正常重启后运行真实 Windows 隐藏后台探针、没有重新导入 cookie。两轮网页 Worked 时间分别为 13m 38s、11m 1s。用户认可两次作为修复验收；因果调查仍不将某个单独 cookie 判为已确认的责任因素。

> 2026-10-04 登录态调查：yi 已从原 Windows Default 来源恢复缺失会话 cookie，并通过新页面、刷新及 GPT-5.6 Sol Extra High 的标准 TEST_OK。临时调用冻结已解除；随后按用户指令已通过现有配置接口将 yi 并发上限设为 8，没有重启浏览器。此前 cookie 消失的精确触发事件尚未确定。
>
> 已实现可调 1～8 并发、独立 worker tab、UI/剪贴板短锁和空闲 tab 回收。用户随后授权使用既有 shiyan Plus profile 测试；该容器独立使用原有四个 volume，不替换 yi 登录态。shiyan 的单请求 TEST_OK 已通过，更多实测结果见此会话输出报告。
>
> shiyan 的 2、4（修复后复测）、6、8 并发均已通过，实际同时生成峰值分别达到对应档位，配置保留为 8。High 的完整水杯 probe 返回 x=8。yi 导入时没有重启容器；启动清理修复已写入 yi 源码。

运行链路固定为：`mg → http://127.0.0.1:8652/v1/chat/completions → yi MimicGate → 当前登录浏览器 → chatgpt.com`。

工程目录：`D:\musicclaude\mimic-cli`。运行只需要本机 Python 3、Docker 和现有容器 `yi-mimicgate-20261002`。Python CLI 仅使用标准库，不需要 pip 安装。容器继续使用其现有 `/opt/venv` 和浏览器登录 volume。

## 命令

安装脚本已经把 `bin` 加入用户 PATH。新开的终端可使用：

```powershell
mg ask "你的问题"
mg ask --file .\prompt.txt
mg check
mg probe cup

# 用户授权的 shiyan Plus 测试入口，最高可验证到 High
mg --profile shiyan check
mg --profile shiyan ask "你的问题"
mg --profile shiyan probe cup
mg --profile shiyan parallel
mg --profile shiyan parallel 4

# 两个稳定快捷入口
mg-ask "你的问题"
mg-cup
```

现有终端若还没有继承新 PATH，可立即使用完整路径：

```powershell
& 'D:\musicclaude\mimic-cli\bin\mg.cmd' ask '你的问题'
& 'D:\musicclaude\mimic-cli\bin\mg.cmd' ask --file '.\prompt.txt'
& 'D:\musicclaude\mimic-cli\bin\mg.cmd' check
& 'D:\musicclaude\mimic-cli\bin\mg-cup.cmd'
```

`ask` 支持 UTF-8 文件。stdout 只返回完整回答；stderr 输出 run 路径或明确错误。成功退出码 0，失败退出码 1，参数错误退出码 2。不提供 model、effort、thread 或 conversation 覆盖参数。`check` 检查 8652 health、实时 `/v1/models`、目标模型，再通过同一个标准路径发送短测试，要求回答严格为 `TEST_OK`。

## 每次请求的实际状态控制

CLI 固定发送 `model="gpt-5.6-sol"`、`reasoning_effort="xhigh"`，并带 `X-MimicGate-Mode: temporary-unpersonalized`。该 header 在现有 `/v1/chat/completions` 内选择标准模式，继续调用同一个 `ChatGPTClient.send_message`。标准模式绕开普通会话恢复、历史拼接和响应缓存，没有独立 provider。

1. 为每个请求租赁独立 worker tab，在其中导航到 ChatGPT 根页面，重置前一轮。
2. `ensure_temporary_chat()` 检查真实可见的激活控件及 `temporary-chat=true`。未开启时点击 accessible name 为 `Temporary chat` 的按钮；开启后必须出现 `Turn off temporary chat`，并确认 URL 标志。另有 role、testid 和 aria fallback。只有 URL 不会被认定为成功；已开启时不重复点击。
3. `ensure_non_personalized()` 打开右上角 `Personalized / Unpersonalized` 菜单。必要时点击 `Unpersonalized` 的 `menuitemradio`，重新打开确认 `aria-checked=true`，关闭后确认按钮标签为 `Unpersonalized`。这与 Temporary 检查独立。
4. 模型菜单必须实际选中 `GPT-5.6 Sol` 的 radio。yi 保持 Extra High 的硬性条件。shiyan 单独启用 `allow_high_fallback`：先检查所有实际可选 slider 标签，Extra High 不存在时允许 High；两者都不存在则失败。Plus 使用重新打开菜单的 radio、slider 值和 High 文字作为证据；日志保存 requested=xhigh、selected=high 和降级原因，不把 High 当作 Extra High。
5. 输入完整 prompt；只定位可见 composer 和 Send。当前 UI 存在隐藏的旧 composer，输入、验证和点击均避开隐藏元素。以实际 paragraph / BR 节点还原文本，完整比较输入内容，避免 CSS 的段落间距污染 `innerText`。
6. 在点击 Send 前重新验证 Temporary、Unpersonalized、模型和 effort。验证失败就不发送。
7. 等待完整回答；CLI 的 HTTP 等待最多 1900 秒，标准浏览器响应等待默认 1800000 毫秒，由 `STANDARD_RESPONSE_TIMEOUT` 设置。超时、没有完整回答或仍存在 Stop 控件都失败。存在 Stop 时，Copy 按钮不能作为完成信号。失败后不自动重发。

标准发送使用同一个 UI 锁和全局至少 5 秒的发送尝试间隔；准备页面已经耗时超过 5 秒时不额外等待。并发上限仍为 8，已提交请求继续独立等待回答。诊断保存 `send_attempt_at`、`submitted_at` 和 `submission_pacing`，区分点击尝试与确认提交。

CLI 读取新鲜的脱敏会话观察状态。明确缺少会话 cookie 时在 completion HTTP 前返回 `authentication_missing`；后台也独立读取真实浏览器的 cookie 数量，缺失时不准备页面、不发送 prompt。cookie 存在只代表通过前置检查，后续 UI 状态仍必须验证。认证失败不自动重发、不静默切换账号。

被动观察器和首次导航前的监听器将认证 cookie 的更新/过期/清除指令、401/403、会话数量、数据库行数、页面认证状态和连接变化保存到持久卷 `/app/state/yi-session-observer.jsonl`。不保存 cookie 值、认证头或请求/响应正文。启动钩子会在现有 yi 容器启动时自动运行观察器；5 秒状态采样供 CLI 前置检查使用。2026-10-05 已加载到 yi 当前服务，两个标准 TEST_OK 验证通过。

网页实测行为：发送后会出现 `/c/{uuid}?temporary-chat=true`，Temporary 和 personalization 的发送前控件会消失，并出现 `Save chat`。因此日志保存的是**实际发送前最后一次 UI 验证证据**，另记录回答后 URL 标志和完整回答状态。不会因为发送后控件消失而抹掉已验证的发送前证据，也不会把回答后的 URL 当成额外的 UI 验证。

这套 CLI 是 one-shot。每次调用建立新的 Temporary 环境，绝不使用 `conversation_store` 恢复；记录的 thread ID 仅用于诊断。关闭或切离后能否恢复不作为能力保证，不提供恢复入口。CLI 不点击 `Save chat`，也不把 fresh thread 视为 Temporary。

## 水杯题和日志

固定题面保存于工程自身的 `prompts\cup.txt`，使用任务说明中完整原文，包括“不要联网搜索，也不要写代码辅助计算”的要求。迁移时已读取旧 prompt；旧文件包含字面 `\n`、排版及标点差异，因此工程使用用户本次提供的完整题面，旧原件仅归档在 `backups\cup_prompt.original.txt`。运行时只读取工程内的 prompt。

`ask`、`check`、`probe cup` 全部调用 CLI 的同一个 `standard_call()` 和服务端同一个标准模式，不为 probe 维护第二套发送逻辑。

每次调用在 `runs\{UTC timestamp}-{random suffix}\` 保存：

- `prompt.txt`：完整 prompt。
- `response.txt`：完整回答；失败且没有回答时为空。
- `diagnostics.json`：UTC timestamp、耗时、success/failure、HTTP 状态、错误类型、实际 model / effort、两项 UI 验证、输入完整性、发送和回答完成状态、安全 completion/thread ID。
- `screenshots/`：杯题的最终页面或失败现场截图，保存文件摘要及网页思考时长。没有完整回答的失败截图不算正常通过；生成前截图留在容器中的同一 request 目录。

主要失败类型包括 `ui_selector`、`temporary_state`、`personalization_state`、`model_state`、`input_validation`、`http`、`http_connection`、`browser_disconnected`、`submission_failed`、`incomplete_response`、`timeout`、`state_evidence`、`busy`。

API token 在 CLI 进程内通过现有容器 `Config` 读取，再访问 8652；不写配置文件，不放 argv，不打印，不记录 cookie、Authorization 或认证存储。日志只取允许的 UI 状态和 API 结果，已知密钥和认证文本会脱敏。CLI 不读取浏览器 cookie 或 localStorage。

用户指定水杯题正常答案为 **8**。probe 不修改题面、不提示答案；得到完整回答后，额外解析明确的最终答案语句（如 `x=8`、`\\boxed{8}`），记录 `probe_assessment` 的 expected/observed answer、判定及原文证据。不会因为正文里偶然出现数字 8 就通过。结论不是 8 或无法可靠识别时退出码为 1，完整回答仍返回 stdout 并保存。`transport_success=true` 表示链路成功；probe 的 `success=true` 还要求结论匹配 8。该自动判定不代表数学证明已被独立复核。

## 并发

`mg --profile shiyan parallel N` 在无活跃请求时设置 1～8 个 worker tab。页面准备、模型/个性化菜单、输入与发送操作持有短 UI 锁；确认发送后释放，多个回答可同时生成。剪贴板提取单独加锁。最多排队 16 个请求、等待 240 秒；结束后只保留最多两个空白 worker tab。每个请求的 prompt、response、诊断和 thread ID 独立。提高并发会增加瞬时内存和账号用量，配置上限不代表实测达到相同数量的同时生成。

## 启动、部署和备份

```powershell
& 'D:\musicclaude\mimic-cli\scripts\start.ps1'
& 'D:\musicclaude\mimic-cli\scripts\deploy.ps1'
& 'D:\musicclaude\mimic-cli\scripts\deploy-shiyan.ps1'
& 'D:\musicclaude\mimic-cli\scripts\install-aliases.ps1'
```

`start.ps1` 只启动已存在的 yi 容器。yi 的启动及部署入口在存在调查 freeze 文件时拒绝操作，本次恢复后已将该文件归档。shiyan 使用独立的 `deploy-shiyan.ps1`，先确认无活跃请求并备份源码，再部署明确列出的补丁，启动或优雅重启同一个既有容器。脚本不删除或重建容器/volume，也不替换 browser profile。新的 manager 启动清理只删除确认无人使用的 Singleton 标记，保留 Cookies/WAL/SHM、缓存、service worker、localStorage 和 IndexedDB；不执行全局 pkill。该修复已部署到 shiyan，并已写入 yi 源码；yi 导入期间没有重启。

初始 live 源码备份：`backups\initial`。每次部署前备份：`backups\deploy-{local timestamp}`。首次比较确认 `client.py`、`openai_routes.py`、`manager.py`、`config.py`、`selectors.py`、`conversation_store.py` 六个 live 文件与迁移参考哈希完全相同，因此采用 live 容器源码作为基线。

现有 volume 保持：`yi-mimicgate-20261002-config`、`yi-mimicgate-20261002-browser`、`yi-mimicgate-20261002-logs`、`yi-mimicgate-20261002-state`。API 为 8652，浏览器 GUI 为 5802；所有宿主端口仅绑定 127.0.0.1。

运行不依赖 LibreChat、Mongo、9090、9091 adapter、旧启动脚本或旧目录的 Python package。未导入或运行任何 gpt2agent；没有新增直接 ChatGPT backend-api 的调用。标准 CLI 是文本调用，跳过继承的生成媒体下载逻辑，不执行该逻辑内的 fetch / urllib；聊天发送和回答提取均由 UI 完成。继承源码中对网页自身 network event 的观察、生成媒体 URL 的识别不作为聊天发送后端。

## 验证

```powershell
python 'D:\musicclaude\mimic-cli\tests\test_cli_guards.py'
docker cp 'D:\musicclaude\mimic-cli\tests\test_standard_contract.py' shiyan-mimicgate-20261002:/app/test_mg_standard_contract.py
docker exec -w /app shiyan-mimicgate-20261002 /opt/venv/bin/python /app/test_mg_standard_contract.py
mg --profile shiyan check
mg --profile shiyan probe cup
```

本地 guard 测试验证密钥脱敏、并发 run 的独立性、yi 冻结在 HTTP 前生效，以及 High fallback 只允许 shiyan。`test_effort_policy.py` 验证 Extra High 优先、严格账号拒绝降级、授权 Plus 允许 High、缺少 High 则拒绝。浏览器 pool 的模拟测试验证八并发上限、排队、取消与空闲回收。容器合同测试验证 Temporary URL 没有 UI 时不能通过，以及模型、effort、stream、历史 ID 等覆盖参数在浏览器租赁前被拒绝。验收结果以对应 run 的日志为准。
