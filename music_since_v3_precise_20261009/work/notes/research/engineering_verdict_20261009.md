# 2026-10-09 工程裁决：新身份回归通过，网页路由未通过

## 已完成及范围

本轮不新增 Opus/Sol 调用；旧 run131/run133、旧 Opus 内容只读。生产仍 run124 surface B gpt56w。

- execution_integrity：UTF-8 原字节落盘、精确输入/产物哈希与 producer 身份、旧身份拒绝复用、JSON/JSONL/HTTP头脱敏、本地超时进程树回收。
- gpt2_adapter r2：直接入口与 runner 共用文件锁，独立采样键，最多一次提交；超时/提交后不明/未知终态/保护信号停队列，不自动重发。
- 通用 runner：Windows 换行不再破坏续跑哈希；初始化失败也落盘身份；请求 max_attempts 不再触发同 job 自动重提；超时和保护信号持久停同 provider。
- 未显式选择网页路由时 fail closed，**不再默默走 mg**。这不是把健康未通过的 gpt2 当可用默认；显式 gpt2 请求仍受 hold 拦截。没有静默迁到 Codex 或其他替代。
- experiment_calls：解析失败可另取不可变 attempt ID；明确未提交的失败才可推进新尝试；未知/保护失败不继续；成功复跑重新核验输入/输出/producer，不修改旧 meta/raw。

## 离线回归

2026-10-09 执行 `python -X utf8 -I -m unittest discover ... -p test*.py -v`，54 项通过（7.746 秒）。覆盖新尝试/零调用续跑、legacy拒绝、篡改拒绝、失败落盘、队列hold、秘密脱敏、真实 Windows .cmd 桩与真实本地父子进程回收。

第一次合并回归为 50/51，失败是 Windows .cmd 桩测试未隔离真实 run135 hold；已把该测试的 HOLD_FILE 指向临时目录，**没有删除或放行真实队列 hold**。复跑 54/54。

这些是离线工程证据，不是实际服务稳定性、实际后端推理档位或音乐内容验收。后续新入口增加测试后，以上计数不自动代表新增测试通过。

后续增补回归：同路径图片内容变更会改变请求身份，缺图片在提交前拒绝且不写成功产物；Codex 禁工具任务发现 completed command/web/file/MCP 项则作废，reasoning/todo_list 不误判，允许工具的任务仍可运行。2026-10-09 最新共享工具回归 **60/60 通过，8.213 秒**（在 run136/run137 新入口测试加入前）。

## run135 真实结果

| 冻结任务 | GPT-5.6 | GPT-6 |
|---|---|---|
| 短输入＋中文完整性标记 | 60.5 秒，173 字，server model match，terminal 与 marker 通过 | 66.3 秒失败，post_submit_ambiguous，正文为空 |
| 长输入＋中文完整性标记 | 未提交（队列停） | 未提交（队列停） |

事实源：`runs/run135_gpt2_recheck/health.json`、`report.md` 与对应 meta。保留 run131 原报告，不补改旧型号判断。

run131 的 mixed 型号标签误把体验类型 `thinking` 当型号；修正这个检测错误不能把 run135 的真实失败改成通过。

## 未完成/阻塞

- 网页通道整体未通过，两个长输入仍未测；GPT-5.6/6 的新鲜公平音乐角色对照及两w评审受阻。
- 提交后状态不明确只做只读取证；不得以本地进程回收声称服务端取消，不盲删 hold。
- run136 Thread、run137 Flash E7 新入口尚待独立测试/主会话验收；Flash 诊断明确是另一条实验，不替代网页GPT公平比较。
- 上轮 Muse 台账误把“生成者可以自评”解释为解除主会话候选写手禁令；此解释不接受。主会话仍不得写音乐内容候选，SUP-04须在新补充台账纠正。
- 原验收的 NONE common enough、H4 prefix-valid、三作品泛化、整篇三方基线盲比等不因工程通过而成立；不切 production。
