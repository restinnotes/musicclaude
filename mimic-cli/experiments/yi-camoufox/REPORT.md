# yi 原 Chrome / 移植 Camoufox 水杯题对照

状态：complete。

同一个 yi 账号、同一道固定题面、GPT-5.6 Sol / 实际 Extra High，Temporary Chat + Unpersonalized。
两组各计划 3 轮串行请求；正常轮间隔 10 秒。先关闭原 Chrome 再运行 Fox，没有同账号并发。
用户指定正常答案为 8。这里报告完整回答的最终结论和探针匹配情况，不代表独立验证每份数学证明。

|组别|轮次|开始（纽约）|结束（纽约）|答案 / 状态|总耗时 秒|提交至完成 秒|网页计时|实际档位|截图哈希一致|
|---|---:|---|---|---|---:|---:|---|---|---|
|Chrome|1|2026-10-06T01:08:17.773572-04:00|2026-10-06T01:10:49.695572-04:00|6|151.922|134.92|Worked for 2m 6s|xhigh|True|
|Chrome|2|2026-10-06T01:11:00.029537-04:00|2026-10-06T01:21:53.138537-04:00|6|653.109|639.007|Worked for 10m 27s|xhigh|True|
|Chrome|3|2026-10-06T01:22:03.565620-04:00|2026-10-06T01:24:43.081620-04:00|6|159.516|142.207|Worked for 2m 15s|xhigh|True|
|Camoufox|1|2026-10-06T01:28:16.071150-04:00|2026-10-06T01:31:52.243150-04:00|6|216.172|100.495|Worked for 1m 32s|xhigh|True|
|Camoufox|2|2026-10-06T01:32:02.664437-04:00|2026-10-06T01:35:20.664437-04:00|6|198.0|89.461|Worked for 1m 20s|xhigh|True|
|Camoufox|3|2026-10-06T01:35:31.101511-04:00|2026-10-06T01:39:31.711511-04:00|6|240.61|115.774|Worked for 1m 46s|xhigh|True|

总耗时含准备、输入、思考、输出和截图；提交至完成不含最终截图，包含思考和输出。网页 Worked for / Thought for 标签另外记录。

## 实测判断

原 Chrome 已完成答案：[6, 6, 6]。
Camoufox 已完成答案：[6, 6, 6]。
移植 Camoufox 后仍出现偏离 8 的完整答案；本次不能认定 Fox 解决了该探针异常。

## 原始证据

- yi 第 1 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T050817.773572Z-ce3d72b7/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T050817.773572Z-ce3d72b7/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T050817.773572Z-ce3d72b7/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T050817.773572Z-ce3d72b7/screenshots)。
- yi 第 2 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T051100.029537Z-4409ceae/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T051100.029537Z-4409ceae/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T051100.029537Z-4409ceae/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T051100.029537Z-4409ceae/screenshots)。
- yi 第 3 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T052203.565620Z-c3a387e6/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T052203.565620Z-c3a387e6/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T052203.565620Z-c3a387e6/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T052203.565620Z-c3a387e6/screenshots)。
- yi-camoufox 第 1 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T052816.071150Z-1e56126b/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T052816.071150Z-1e56126b/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T052816.071150Z-1e56126b/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T052816.071150Z-1e56126b/screenshots)。
- yi-camoufox 第 2 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T053202.664437Z-e90f7da7/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T053202.664437Z-e90f7da7/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T053202.664437Z-e90f7da7/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T053202.664437Z-e90f7da7/screenshots)。
- yi-camoufox 第 3 轮：[诊断](D:/musicclaude/mimic-cli/runs/20261006T053531.101511Z-896b4073/diagnostics.json)、[回答](D:/musicclaude/mimic-cli/runs/20261006T053531.101511Z-896b4073/response.txt)、[页面截图](D:/musicclaude/mimic-cli/runs/20261006T053531.101511Z-896b4073/screenshots/response-viewport.jpg)、[全部截图目录](D:/musicclaude/mimic-cli/runs/20261006T053531.101511Z-896b4073/screenshots)。

## 实验条件与判断边界

Chrome 组基于原 yi 当前源码，仅加观测截图与私有 cookie 导出。候选沿用 yi 的登录诊断、5 秒全局发送间隔、完成检测及严格完整题面校验。
候选参考 D:/grok-test/lij-grok-register-panel：Camoufox 0.5.4 / Gecko 152.0.4-beta.31，Windows 指纹、headed、humanize、geoip、en-US、block_webrtc，30–120ms 逐字输入并偶尔停顿；未加入代理池。
Fox 使用独立 browser/state/log 卷，原 yi state 只读挂载导入授权 cookie；原 Chrome profile 不挂载。原 cookie 值与 API token 不写入镜像和实验结果。
原 Chrome 容器内存限制 unlimited；Fox 为 2.5 GiB 内存加 1 GiB swap、shm 512 MiB。这一资源差异会影响耗时，不能把时间差全归因到浏览器。
本实验一次替换浏览器引擎、指纹与输入行为，无法区分各因素贡献，也无法凭单题确认服务端实际模型或所谓降智根因。
先前 shiyan 是另一账号和 High 档位，不与本次 yi / Extra High 混合统计。
Chrome 的部分中文字体显示为方框，完整文本另存；JPEG 是浏览器实际截图，未编辑。

Chrome 第 2 轮的自动最终截图停留在思考摘要，没有露出答案；完整答案 6 由 response.txt 与诊断保留。Fox 尝试在完成后追加滚到答案末尾的截图，初始截图同时保留。
Fox 第 1 轮追加末尾截图失败（定位超时），原始最终截图已保留；截图阶段 30.131 秒，发生在模型完成计时之后，不能算作思考时间。
Fox 第 2 轮追加末尾截图失败（定位超时），原始最终截图已保留；截图阶段 30.119 秒，发生在模型完成计时之后，不能算作思考时间。
Fox 第 3 轮追加末尾截图失败（定位超时），原始最终截图已保留；截图阶段 30.156 秒，发生在模型完成计时之后，不能算作思考时间。

Chrome 每 30 秒资源采样：内存峰值 1788.09 MiB，swap 峰值 0.00 MiB，末次事件 {'low': 0, 'high': 0, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}。
[资源记录](D:/musicclaude/mimic-cli/runs/cup-yi-20261006T050817Z/memory.jsonl)。Chrome 的观察从第 2 轮进行中开始，不覆盖第 1 轮。

Fox 每 30 秒资源采样：内存峰值 2222.76 MiB，swap 峰值 279.31 MiB，末次事件 {'low': 0, 'high': 0, 'max': 3591, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}。
[资源记录](D:/musicclaude/mimic-cli/runs/cup-yi-camoufox-20261006T052815Z/memory.jsonl)。

原 Chrome 正常关闭确认：True，容器 exited，OOMKilled=False。profile/state 卷保留。
[关闭证据](D:/musicclaude/mimic-cli/experiments/yi-camoufox/original-shutdown-evidence.json)。

Fox 正常关闭确认：True，容器 exited，OOMKilled=False。profile/state 卷保留。
[关闭证据](D:/musicclaude/mimic-cli/experiments/yi-camoufox/shutdown-evidence.json)。

## 登录观测

yi：3 次发送前登录快照均保有 session cookie；记录到的 cookie 删除指令 0 次，401/403 观测 0 次。[非秘密观测摘要](D:/musicclaude/mimic-cli/experiments/yi-camoufox/yi-auth-summary.json)。未观察到事件不等于覆盖了所有网络响应。
yi-camoufox：3 次发送前登录快照均保有 session cookie；记录到的 cookie 删除指令 0 次，401/403 观测 0 次。[非秘密观测摘要](D:/musicclaude/mimic-cli/experiments/yi-camoufox/yi-camoufox-auth-summary.json)。未观察到事件不等于覆盖了所有网络响应。
