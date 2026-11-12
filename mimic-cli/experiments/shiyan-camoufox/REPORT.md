# shiyan Chrome / Camoufox 水杯题对照记录

运行状态：complete。

同一个 shiyan Plus 账号，固定题面，GPT-5.6 Sol，实际 High，Temporary Chat + Unpersonalized。
两组各计划 3 次串行请求；正常轮间隔 10 秒，Chrome 超时后恢复第 3 轮间隔约 60 秒。
先停 Chrome 再启动 Camoufox，使用同一 Docker 默认网络出口设置，没有加入参考工程的代理池。
候选采用参考 Grok 工程的 Camoufox 0.5.4 / 152.0.4-beta.31、Windows 指纹、headed、
humanize、geoip、en-US、禁用 WebRTC，以及 30–120ms 逐字输入和偶尔 120–300ms 停顿。
MimicGate 标准状态控制和响应完成判断沿用基线源码；Chrome 组只增加观测截图和私有 cookie 导出。

总耗时含准备、输入、思考、输出和截图；提交至完成不含最终截图，仍包含思考和输出。
Worked for / Thought for 是网页显示的标签，单独记录，不与计时字段混同。

|组别|轮次|开始时间（纽约）|答案 / 状态|总耗时 秒|提交至完成 秒|网页计时|实际档位|最终截图校验|
|---|---:|---|---|---:|---:|---|---|---|
|Chrome|1|2026-10-05T23:28:02.067393-04:00|8|640.141|621.915|Worked for 9m 18s|high|True|
|Chrome|2|2026-10-05T23:38:52.583695-04:00|timeout|923.422|None|未取得|high|False|
|Chrome|3|2026-10-05T23:55:16.453741-04:00|8|652.89|636.707|Worked for 9m 28s|high|True|
|Camoufox|1|2026-10-06T00:18:13.185870-04:00|8|914.188|820.099|Worked for 12m 32s|high|True|
|Camoufox|2|2026-10-06T00:33:37.746967-04:00|8|751.265|660.299|Worked for 9m 54s|high|True|
|Camoufox|3|2026-10-06T00:46:19.441963-04:00|8|829.578|694.153|Worked for 10m 18s|high|True|

## 原始证据

- shiyan 第 1 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T032802.067393Z-f02b2b56/diagnostics.json)、[完整回答](D:/musicclaude/mimic-cli/runs/20261006T032802.067393Z-f02b2b56/response.txt)、[最终视口截图](D:/musicclaude/mimic-cli/runs/20261006T032802.067393Z-f02b2b56/screenshots/response-viewport.jpg)、[最终整页截图](D:/musicclaude/mimic-cli/runs/20261006T032802.067393Z-f02b2b56/screenshots/response-full.jpg)、[发送前截图](D:/musicclaude/mimic-cli/runs/20261006T032802.067393Z-f02b2b56/screenshots/prepared-full.jpg)。
- shiyan 第 2 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T033852.583695Z-fd9fb36b/diagnostics.json)、[未完成页面截图](D:/musicclaude/mimic-cli/runs/20261006T033852.583695Z-fd9fb36b/screenshots/thinking-before-timeout.jpg)。未取得最终答案，不计作答错。
- shiyan 第 3 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T035516.453741Z-32303f98/diagnostics.json)、[完整回答](D:/musicclaude/mimic-cli/runs/20261006T035516.453741Z-32303f98/response.txt)、[最终视口截图](D:/musicclaude/mimic-cli/runs/20261006T035516.453741Z-32303f98/screenshots/response-viewport.jpg)、[最终整页截图](D:/musicclaude/mimic-cli/runs/20261006T035516.453741Z-32303f98/screenshots/response-full.jpg)、[发送前截图](D:/musicclaude/mimic-cli/runs/20261006T035516.453741Z-32303f98/screenshots/prepared-full.jpg)。
- shiyan-camoufox 第 1 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T041813.185870Z-06625764/diagnostics.json)、[完整回答](D:/musicclaude/mimic-cli/runs/20261006T041813.185870Z-06625764/response.txt)、[最终视口截图](D:/musicclaude/mimic-cli/runs/20261006T041813.185870Z-06625764/screenshots/response-viewport.jpg)、[最终整页截图](D:/musicclaude/mimic-cli/runs/20261006T041813.185870Z-06625764/screenshots/response-full.jpg)、[发送前截图](D:/musicclaude/mimic-cli/runs/20261006T041813.185870Z-06625764/screenshots/prepared-full.jpg)。
- shiyan-camoufox 第 2 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T043337.746967Z-f9856e85/diagnostics.json)、[完整回答](D:/musicclaude/mimic-cli/runs/20261006T043337.746967Z-f9856e85/response.txt)、[最终视口截图](D:/musicclaude/mimic-cli/runs/20261006T043337.746967Z-f9856e85/screenshots/response-viewport.jpg)、[最终整页截图](D:/musicclaude/mimic-cli/runs/20261006T043337.746967Z-f9856e85/screenshots/response-full.jpg)、[发送前截图](D:/musicclaude/mimic-cli/runs/20261006T043337.746967Z-f9856e85/screenshots/prepared-full.jpg)。
- shiyan-camoufox 第 3 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T044619.441963Z-7ea16a3b/diagnostics.json)、[完整回答](D:/musicclaude/mimic-cli/runs/20261006T044619.441963Z-7ea16a3b/response.txt)、[最终视口截图](D:/musicclaude/mimic-cli/runs/20261006T044619.441963Z-7ea16a3b/screenshots/response-viewport.jpg)、[最终整页截图](D:/musicclaude/mimic-cli/runs/20261006T044619.441963Z-7ea16a3b/screenshots/response-full.jpg)、[发送前截图](D:/musicclaude/mimic-cli/runs/20261006T044619.441963Z-7ea16a3b/screenshots/prepared-full.jpg)。

## 本次实测判断

原 Chrome：[8, 'timeout', 8]。
Camoufox：[8, 8, 8]。

按用户指定的正常答案 8，本次没有复现 shiyan 在原 Chrome 链路稳定降智。
原 Chrome 已能回答 8，Camoufox 也回答 8，因此不能证明浏览器指纹或人类化输入修复了能力异常。
本次不包含同一个 yi / Extra High 账号的浏览器对照，不能解释此前该账号答 6/7 的原因。

## 历史参照与判断边界

历史 shiyan 同题 High 记录 20261005T032106.542102Z-bdc01105：答案 8，总耗时 677.062 秒。
用户指定正常答案为 8；这里记录探针答案是否匹配，不代表已独立复核每份数学证明。
这是浏览器方案整体的对照，同时包含引擎、指纹和输入行为变化，不能单独归因到某个防指纹参数。
yi 的账号和 Extra High 档位与 shiyan Plus / High 不同，不能把两者当作同条件对照。
截图为浏览器原始 JPEG，按哈希验证复制一致；部分中文字体显示为方框，完整文本另存。
原 cookie/profile 保留在原卷中；候选使用独立 profile，并只读导入同账号 cookie。

## 候选输入适配留痕

正式测试前，逐字键入触发了 ProseMirror 的编号列表输入规则；严格完整题面校验阻止了发送。
Ctrl+Z 后补空格仍重新触发列表，最终改为编号前缀逐字输入时增加一个临时字符，随后立即用方向键和 Delete 删除它。
其余字符仍逐字键入并随机停顿。完整题面校验保持原标准，不放宽比较。
以下适配失败均未取得模型答案；启动前探测连接失败也不计为模型结果。
- 2026-10-06T00:06:30.371095-04:00，input_validation，未发送：[诊断](D:/musicclaude/mimic-cli/runs/20261006T040630.371095Z-115c5cef/diagnostics.json)。
- 2026-10-06T00:10:52.850614-04:00，cli_internal，未发送：[诊断](D:/musicclaude/mimic-cli/runs/20261006T041052.850614Z-4211155f/diagnostics.json)。
- 2026-10-06T00:11:08.998448-04:00，input_validation，未发送：[诊断](D:/musicclaude/mimic-cli/runs/20261006T041108.998448Z-f5bcfb1c/diagnostics.json)。
- 2026-10-06T00:13:15.350476-04:00，input_validation，未发送：[诊断](D:/musicclaude/mimic-cli/runs/20261006T041315.350476Z-589712c2/diagnostics.json)。
- 2026-10-06T00:15:26.041833-04:00，input_validation，未发送：[诊断](D:/musicclaude/mimic-cli/runs/20261006T041526.041833Z-d3eece08/diagnostics.json)。

## 资源观测

每 30 秒记录候选 cgroup；采样峰值 1991.25 MiB，
swap 采样峰值 809.45 MiB，末次计数 {'low': 0, 'high': 0, 'max': 9791, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}。
[原始内存观测](D:/musicclaude/mimic-cli/runs/cup-shiyan-camoufox-20261006T041813Z/memory.jsonl)。内存限额与 swap 压力可能影响耗时。

候选第 3 轮资源条件调整：2026-10-06T00:49:19.3208655-04:00，内存上限 2 → 2.5 GiB，内存加 swap 上限 3 → 3.5 GiB。
调整前观察到约 805 MiB swap 和明显内存回收，主机可用内存约 2.28 GiB；未发生 OOM。浏览器会话未重启。
因此第 3 轮耗时不能视为与前两轮完全相同的内存条件；题面、账号、档位和浏览器配置不变。
[资源调整记录](D:/musicclaude/mimic-cli/experiments/shiyan-camoufox/resource-adjustment.json)。

## 收尾状态

候选浏览器正常关闭确认：True；容器 exited，退出码 0，OOMKilled=False。
截图及资源观察进程已结束；候选和原 Chrome 的 profile/state 卷均保留，yi 继续停止。
[正常关闭与卷保留证据](D:/musicclaude/mimic-cli/experiments/shiyan-camoufox/shutdown-evidence.json)。
