# shiyan Chrome / Camoufox 对照实验

用户授权将同一个 shiyan 账号的登录态复制到独立 Docker 浏览器，并比较固定水杯题结果。
这不是已验证的“防降智”方案；结果以每轮原始回答和截图为准。

基线：现有 `shiyan-mimicgate-20261002`，API `127.0.0.1:8651`，GUI `127.0.0.1:5801`。
候选：`shiyan-camoufox-20261006`，API `127.0.0.1:8653`，GUI `127.0.0.1:5803`。
yi 容器保持停止；两组串行运行，不同时启动测试浏览器。

候选镜像继承本机 `lij-grok-outlook:local` 的 Camoufox 0.5.4 / 浏览器
152.0.4-beta.31。MimicGate 源码从现有 shiyan 容器复制；更换浏览器启动适配层，
并使用参考工程的逐字输入延迟。不开注册流程，不调用聊天 backend-api。

候选浏览器采用 `os=windows`、`humanize=True`、`geoip=True`、`locale=en-US`、
`block_webrtc=True`、headed 模式和独立 persistent profile。它保留相同的 Docker
网络出口，不使用参考工程的住宅代理池；这是为了避免同时更换网络和浏览器。
候选不叠加 Chrome 的 JS stealth 脚本。

输入仍采用参考工程的逐字键入。ChatGPT 的 ProseMirror 会把 `1. ` 自动转成列表，
候选因此在编号前缀输入时暂时加入一个字符，再立即用方向键和 Delete 删除它。
这段适配只处理编辑器格式转换；发送前仍完整比较原题面，任何差异都阻止发送。
每个失败尝试也保留独立诊断和截图，不计入能力测试的答案。

Cookie 从 shiyan 的浏览器 context 在首次导航前导出到源容器 state 卷的私有文件，
候选只读挂载该卷。首次启动时复制有效的 ChatGPT/OpenAI cookie 到自己的 profile，
之后不重复导入。源 Chrome profile 不挂载到候选，不写入候选镜像，不输出 cookie 值。
运行配置和 API token 在候选自己的 state 卷中生成并限制权限。

两组均使用相同 `prompts/cup.txt`，真实 Temporary Chat、Unpersonalized、GPT-5.6 Sol。
shiyan 授权在 Extra High 不可用时使用验证后的 High，实际档位逐轮记录，不与 yi
Extra High 的结果混为同条件实验。水杯题正常答案按用户指定为 8。

每轮结果保存在 `D:/musicclaude/mimic-cli/runs/`：原文、完整回答、诊断、总耗时、
提交至完成耗时、网页 `Worked for / Thought for` 标签，以及发送前和完成后的真实
viewport/full-page JPEG 截图。截图在 worker tab 回收之前保存。截图耗时单列记录。

基线只增加观察和截图存储，没有更改浏览器、人类化输入、模型选择或发送策略。
基线原版文件备份在 `work/shiyan-camoufox-comparison/`。

```powershell
docker build -t shiyan-mimicgate-camoufox:comparison-20261006 .
.\create-container.ps1
# 确认 Chrome 测试已经结束且源 cookie 导出存在，再启动候选。
docker start shiyan-camoufox-20261006
mg --profile shiyan-camoufox probe cup
```

Chrome 与候选前两轮设置 2 GiB 内存、3 GiB 内存加 swap 上限；候选共享内存 512 MiB。
候选第三轮出现明显回收压力及约 805 MiB swap，在该轮提交之后的纽约时间 00:49:19
增至 2.5 GiB 内存、3.5 GiB 内存加 swap。调整原文在 `resource-adjustment.json`，
第三轮耗时不能当作完全相同内存条件的结果。创建脚本采用新的候选内存上限。
候选不自动重启。CLI 的实验 profile 不更改 yi 或原 shiyan 的默认入口。

候选实验期间每 30 秒另记 cgroup 内存、swap、回收和 OOM 计数。2 GiB 限额下
已观察到回收及 swap，耗时解读需要同时看这份记录。
现有候选容器为保留 profile，通过 `docker cp` 和正常重启部署了输入适配修复；
同一修复已纳入镜像。`runtime-source-manifest.json` 核对运行中 52 个源码文件与
构建源码一致，并分别记录容器创建镜像和最终重建镜像。
最终镜像的退出流程另修为先等待 API/Firefox 正常关闭和写回 profile，再停虚拟显示。
这只修改退出顺序，不修改浏览器配置或模型输入；现有试验容器会先正常关闭 API 再停止。

复用已经建立的候选时，只执行 `docker start shiyan-camoufox-20261006`，
等待 healthy 后运行 `mg --profile shiyan-camoufox probe cup`；不用再次创建容器。
