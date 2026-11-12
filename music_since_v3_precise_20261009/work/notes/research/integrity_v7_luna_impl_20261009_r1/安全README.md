# v7 安全实现说明

## 交付

v7 新增四个实现模块与一个独立测试套件：tools/execution_integrity_v7.py、tools/gpt2_adapter_v7.py、tools/runner_v7.py、tools/experiment_calls_v7.py、tools/tests/test_execution_integrity_v7.py。本目录保存本轮 report、测试 stdout/stderr、首次失败和修复记录。未覆盖 v4/v5/v6 文件。

## 已实现的执行完整性约束

- request identity 绑定 producer、精确 prompt digest、sampling identity、模型与已知行为环境；completion、terminal、prompt、output、finalization seal、pending ledger 和 cache source 逐项做精确归属与 digest 校验。无归属、冲突、损坏、不可读、旧 schema、遗留 seal 或孤儿 prompt/output 均 fail closed。
- v4/v5/v6 和 v7 的 inflight tickets 与 provider hold 都阻止新提交；提交前通过排他创建 ticket 并 fsync 文件和目录。ticket 写入失败时不启动 provider。ticket 后结果未知时保留 ticket/hold，不会按成功处理。
- Codex/OpenCode 解析使用事件与阶段 allowlist；不认识、状态矛盾、不完整 terminal、terminal 后事件和禁止工具均拒绝。缺省 status 只对精确的已知合成 fixture 形状兼容。
- GPT-2 adapter 要求实际返回 metadata 中的 thinking_effort 精确等于请求的 max，并只使用根级 server_metadata_summary 判断 backend slug。effort 是返回 metadata 的一致性绑定，不是远端 attestation。
- parse failure 默认停止。只有显式 opt-in、非空 reason、attempt budget 至少为 2 且提供新的 sampling key，才可提交新 immutable sample；新 sample 可沿用冻结 prompt，identity 仍区分 sampling key。只有完整、来源绑定且落盘 seal 验证的 proven-pre-submit 失败可在预算内用相同 prompt 创建新 transport attempt。unknown/post-submit ambiguous/queue-stop 永不自动重试。
- use_cache=False 仍验证 ledgers 与 exact source；如有 exact source，返回原 source 并标记 cache_hit=true, cache_requested=false，不提交、不写 alias、不重定向 source。
- 环境 identity 只读取显式允许的非私密行为值。凭证值不读取、不 hash、不持久化；未知 GPT2AGENT_* 只按变量名拒绝；session file 变量值排除。proxy userinfo/query 与敏感形态拒绝。OPENCODE_CONFIG_CONTENT 按变量名 fail closed，不取值。
- REAL_EXECUTION_APPROVED 在实现中为 False。单测局部 patch 此 gate 时，所有适配器 RUN_PROCESS 均由 mock 替代。跨进程验证只启动本地 Python 检查 queue gate，不调用任何 provider。

## 未验证范围与限制

Codex/OpenCode 的真实 CLI 事件契约未在本轮执行；测试只验证已知合成 fixture 与 fail-closed 行为。GPT-2 活跃调用链的四个源码文件按路径和 SHA-256 绑定，但没有调用 GPT-2 CLI、网络或外部服务。remote BOM/CRLF/rstrip 输入归一化、private/global config、session state、Docker image、外部 service 与远端行为均未冻结；inline Gemini config 的应用范围也未实测，相关 coverage gate 为 false。环境 identity 是已知变量的 binding，不代表进程的全部环境被冻结。

finalization 使用普通可重算 SHA-256，不是 MAC 或签名；能够改写整个 run directory 的写者可以重算 seal。不得据此宣称 route healthy、music acceptance 或 production ready。没有执行音乐候选或裁决。
