# run142 / run143 r4 主会话离线裁决（2026-10-09，r2）

结论：NOT_ACCEPTED。已有回归测试通过，不等于原工程要求全部通过；音乐验收 NOT_PERFORMED，production_ready=false。生产仍 run124 surface B gpt56w，two-w hold 与 REAL_EXECUTION_APPROVED=false 均保留。

## 本次实际执行

脚本：`tools/probes/run142_143_main_verify_20261009_r2.py`。独立新目录：`notes/research/run142_143_main_verify_20261009_r2/`。仅 Python `-X utf8 -I -B`、离线 suites 和本地注入 MockCaller，无模型 CLI、无真实模型提交。

|命令|实际 rc|suite 正文|墙钟秒|
|---|---:|---|---:|
|run142_tests|0|20 tests，37.303s，OK|37.469|
|run143_tests|0|20 tests，19.977s，OK|20.125|
|run142_real|3|BLOCKED，0 real submissions / CLI / writes|0.063|
|run143_strict|0|COMPLETION_PENDING / HELD_NO_REAL_SUBMISSIONS|0.093|
|run143_real|3|BLOCKED，0 real submissions / CLI / writes|0.079|

无 timeout。主脚本父 rc=0 不是验收判据；上述是子命令记录和亲读 suite stderr 的结果。快照中全部列出的 protected source/prompts/tests/manifest/run inventory 未变化，changed_protected_paths=[]；不是整个环境或远端认证。

## 额外探针已经实证的缺口

1. **当前请求身份未核**：run142 先以 `gflash / WHY_GATE_v4` 生成同一 step/key/prompt 的 mock 结果，再以 `luna_noweb / WHY_GATE_v4` 请求，accepted=true、resumed=true、new_mock_submissions=0，返回旧 attempt=0；另只将 prompt_version 改为 different_version 同样复用。旧记录自身 hash 一致不证明与本次请求身份一致。必须对照本次 model/version/完整逻辑输入，冲突先拒绝，不自动生成同样本。
2. **解析失败证据未保留**：run143 对同一 slot 注入非 JSON raw，连续两次调用均 IntegrityError，但 mock_submissions=2、metadata_index_records=0、saved_artifact_files=[]。源码 `_create_mock_artifact` 在落盘前 parse，异常使原 raw/失败身份丢失；下一调用无法知道失败已经发生。这是本地 mock 实证，不是 backend completed terminal 证明。

## 静态确认的实现缺项（不冒称真实 transport 实测）

- run142 `transport_retry_allowed` 存在且谓词单测通过，但 `Pipeline.execute` 未使用；执行接口没有相应 transport failure proof / bounded retry 接口。安全 pre_submit retry 执行闭环未完成。
- run143 `execute_mock_task` 没有 explicit allow + budget + reason + new sampling identity 接口。已有 failed-slot STOP 代码不能替代解析失败持久化和合法新 immutable sample 的实现。
- full mock `no_longer_valid=[]` 不证明真实 match 删除集成已覆盖。trusted Muse archive verifier 未安装，外部真实身份验证仍 pending；local SHA/MockCaller 不是认证。

## 原保护与审查状态

AST 显示旧15+15测试名称均有对应（两处明确 rename），新20+20已运行。名称对应本身不是逐断言保护证明；旧自动 parse retry 和 caller-declared schema 不安全政策必须按新合同替换，不能恢复。原失败日志、代理 attempt01/02/03/06、旧 main r1 均保留。

已新派独立只读 Muse review r2，client `music-20261009-run142143-muse-review-r2`；任务尚未返回，不预测其结论，不以任务 running 当完成。不会用平均数、多数票或 schema pass 关闭实质异议。

## 后续条件

只在新 revision 修复，不覆盖 r4 或历史。必须加入当前请求身份冲突、失败 raw 保留、同槽重跑0新样本、显式同冻结 prompt 新 sampling identity、第二次失败仍记录、bounded proven pre_submit retry、ambiguous/queue-stop禁重试、实际 match retirement 与 Muse receipt 全字段绑定回归。主会话亲跑和独立 review 后再作工程裁决。该工程通过仍不代替三作品 `06_ACCEPTANCE_CRITERIA.md`，不改 NONE 条款、宪法、A/T/H 权限或 production 默认值。
