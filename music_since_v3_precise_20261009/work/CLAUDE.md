# 交接说明：压平架构的内容层 run（肖邦 Op.52 / Op.60 / Op.61）

你是这次 run 的编排者。按顺序读：本文件 → 01_GOAL.md → 02_PROCESS.md → 03_CONSTITUTION_CHECK.md → prompts/DERIVATION.md。
reference/ 下是原始资料：产品宪法、V2A 基线提示词、Op.52 九篇样本（其中文本 02、05 为 Gemini 用 V2A 原版的产出）、用户在上一个会话中发出的全部要求。

## 任务
把宪法的两条线——Affect（此刻正在经历什么）与第二条线（前面的经历怎样改变了此刻的意义）——各拆成「网页调研」与「内部权重」两个分支，分别迭代到稳定；再用综合提示词为每首作品产出一篇边听边读的文章。
全过程按逐句归因的方式迭代提示词，并交付可点击追溯的 run 产物。

## 模型与调用方式

| 角色 | 命令 |
|---|---|
| 网页调研分支（A-web / T-web） | `codex exec --skip-git-repo-check -m gpt-6-luna -c model_reasoning_effort="max" "<提示词>"` |
| 内部权重分支（A-int / T-int），主 | `agy --model gemini-3.1-pro-high --effort high -p="<提示词>"` |
| 内部权重分支，对照 | `agy --model gemini-3.8-flash-high --effort high -p="<提示词>"` |
| 开发子智能体；综合候选 | `opencode run --model opencode2api/muse-spark-1.3-contributor-free#xhigh "<提示词>"` |
| 综合候选（全部） | gemini-3.1-pro-high、gemini-3.8-flash-high、gpt-6-luna max、muse-spark xhigh、你自己 |

调用注意：
- 用 Python subprocess 以参数列表调用，不经 shell 拼接引号。stdout/stderr 按 bytes 捕获，UTF-8 解码后写文件。上一次 run 出现过乱码，这一条必须在冒烟测试里验证。
- Windows 命令行长度上限约 32k 字符。综合阶段的输入（多份材料）会远超这个长度。冒烟测试必须测出每个 CLI 接收长输入的办法（例如 stdin）。测不通的模型不能当综合候选，记录原因。
- 提示词一律把全文直接发给子智能体。不允许让子智能体"去读某个文件的某一段"。通过 stdin 传全文不算违反这一条。
- 额度不用顾虑。

## 分工：尽量让 Muse 代工
交给 Muse（opencode run）：runner 脚本、落盘与 meta 记录、目录整理、编码问题、HTML 查看器、提示词版本 diff 视图、饱和实验的内容单元初筛。
你自己保留：修改提示词、行为归因、评审结论、阶段推进决定。
给 Muse 的开发任务同样内联完整需求；它的产出你要验收。

## 硬性规则（违反即返工）
1. 提示词只从 prompts/ 的 v0 出发，按 02_PROCESS.md 的逐句归因迭代。不整篇重写，不凭想象重写。
2. 提示词里不出现任何只对某一首作品成立的东西：人名、演奏家、具体小节号、具体段落描述、作品专属的例子。例子和反例尽量不用。新增的句子必须能从宪法或 V2A 推导，并在 DERIVATION.md 记录来源。
3. 每轮只改一个变量：一句提示词，或一个模型，或一个采样数 N。
4. 评判以内容实质和语言鲜活度为先。幻觉不扣分，写得满不扣分，篇幅长不扣分。不用物理或生理参数来描述或评判内容。
5. 四个分支冻结之前不调综合。
6. 所有实际发出的提示词原文和原始产物都落盘，附 meta。
7. 每个 run 结束都要更新 index.html。这一条上个会话被提醒了三次。

## 交付
- 每个 run：`runs/<run_id>/`，规格见 02_PROCESS.md。
- 全部结束时：最终的四个分支提示词和综合提示词（每句注明来源与保留理由）、三首作品的最终文章、总 index.html。


## Music Pipeline 长期执行原则（合并到原 CLAUDE.md，不覆盖原有规则）

- 使命：为认真听音乐的人生成**随音乐时间展开、作品特异、具体可感、有来路与可听依据**的“边听边读”理解，不能只优化中间层数字；产品正式宪法 V2 优先。
- Claude 主会话长期负责：理解产品、研究假设、正式 prompt 修改与归因、盲审决策、架构取舍、production 验收；不能一次失败后只写“下一步建议”。主会话**不亲自当内容候选写手**。
- **Muse 免费且已指定路由**：T3 `delegate_task`，target 使用 `providerInstanceId=claude-proxy`、`model=muse-spark-1.3-contributor-free`、`options.effort=xhigh`。不要用禁用的 `muse` provider；每轮独立 review 使用新 `clientRequestId`，不得通过 `childThreadId` 续聊；详见 `notes/CLAUDE_MUSE_ORCHESTRATION.md`。
- 自由给 Muse 并行分配工程、搜索、试验、失败案例、对抗性质疑、盲评包整理；它不代替 Claude 对音乐审美做最终裁决。任务完整结果落盘，只以短可核查报告回主会话。
- 对模型先固定 prompt/输入/预算，再比较 GPT-6 vs GPT-5.6；对提示词只改一个实验变量并记录 DERIVATION，不能“换模型+改 prompt+换架构”混作同一个胜利。
- 保留 **V2A+Gemini 原始基线**和已认可旧稿；不能以长度/覆盖率/抽象词频/NONE 数字单独判胜。戏剧化、笃定、单故事线**不自动扣分**；没有证据的心理意义才是问题。
- A/T 第一轮研究相互独立；H 是补充材料；T/H 不得擅自重写当前 Affect；前缀有效、音乐时间定位、逐句溯源和实时显示生命周期必须保持。
- 新的 E7 可以早做**诊断性样稿**进行最终阅读盲比，但旧的 E1–E7 验收仍适用，未经三首作品复验不得切换 production。
- 汇报用户只用中文且只报重要结论/故障/完成；每轮新 ZIP 到 Downloads，不维护旧 index；维护简短 `notes/ACTIVE_HANDOFF.md`。误存的 Muse 记忆已由用户删除，不要复活或擅自大改其他记忆。
- 本节（10-08）与上文旧条目冲突时以本节为准：上文表格中 `opencode run ... muse-spark` 的 Muse 调用方式已由 T3 `delegate_task` 取代；上文硬性规则 7「每个 run 更新 index.html」已由用户 10-03 撤销（改为每轮 ZIP 到 Downloads）。启动顺序：本文件 → `notes/ACTIVE_HANDOFF.md` → `notes/PRODUCT_AND_AUTHORITY.md` 等；正式宪法本体是 `reference/PRODUCT_CONSTITUTION_V2.md`。
