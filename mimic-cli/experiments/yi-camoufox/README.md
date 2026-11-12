# yi 原 Chrome / 移植 Camoufox 实验

用户要求：先重新测 yi 的 Chrome，再直接测同账号移植后的 Fox。正常答案由用户指定为 8。

两组各 3 轮，固定题面与 GPT-5.6 Sol / 实际 Extra High，Temporary Chat + Unpersonalized。使用现有 MimicGate 网页链路，`cup_comparison.py` 串行发送，正常轮间隔 10 秒。Chrome 结束并正常关闭后才启动 Fox，避免同账号同时请求。

原容器 `yi-mimicgate-20261002` 的源码已备份至 `D:/musicclaude/mimic-cli/work/yi-camoufox-comparison/src-baseline`。Chrome 仅添加截图和私有 cookie 导出观测；原登录诊断、5 秒全局发送间隔、完成判定均保留。原容器配置的并发上限不改，本实验自身每次仅一轮。

候选 `yi-camoufox-20261006` 使用 yi 当前源码，新增 Camoufox 管理器与原生逐字输入适配。参考 `D:/grok-test/lij-grok-register-panel` 的 Camoufox 0.5.4 / Gecko 152.0.4-beta.31、Windows 指纹、headed、humanize、geoip、en-US、block_webrtc；不加入参考项目的代理池。使用独立 browser/state/log 卷，原 yi state 卷只读挂载用于导入授权 cookie，不挂载原 Chrome profile。

候选 API `127.0.0.1:8654`，GUI `127.0.0.1:5804`。候选内存上限 2.5 GiB、内存加 swap 上限 3.5 GiB、shm 512 MiB、并发 1、High fallback 关闭。原 Chrome 内存限制为 Docker 配置的 unlimited，保持现状，因此耗时有资源条件差异。

每轮落盘完整文本、诊断、提交前和完整回答后的真实 Docker 页面截图及 SHA-256；另有只读实时截图与 30 秒 cgroup 采样。基线内存观察在第 2 轮进行中开始，不覆盖第 1 轮全部过程。

私有 cookie/API token 仅保存在 Docker 私有状态卷，不打印、不写入源码、镜像或公开实验结果。所有 Windows 后台子进程隐藏窗口。结束后正常关闭实验容器，保留全部 profile/state/日志卷。
