# v8 主处置追加（2026-10-09）

这是对旧报告的追加，不覆盖旧报告当时的 `PENDING`、失败或历史 review。只裁工程离线范围，不裁音乐，不放行实际路由。

## 已闭合的离线修复

- 原 v7 C1（proof 五 flags 数字冒充布尔）和 C2（explicit 新 sample 接受 budget=3）在 v8 修复。主 `integrity_v8_main_verify_20261009_r1/report.json` 已亲跑：suite **70/70 PASS**，定向 challenges **22/22 PASS**，两 worker 各 **7/7 隔离负向检查 PASS**。readonly queue child 恰好 suite 1、challenges 0；Windows native argv 精确核。real gate=false，真实模型提交/模型 CLI=0。
- 独立 Muse review 原文安全归档：`integrity_v8_muse_review_source_20261009_r2/response.md`；16995 UTF-8 bytes，SHA256 `bd6e9c4f054daee1a889efe91a79b38066e2ff503c4f7fa28fb303f8cc016088`。原始 delegate task 与本地 tool_result 内容分开保存；公开 meta 不含恢复 handles。两个相同 completed status snapshots、summary/latestTerminalSummary 只计 **一次独立 review**。这不是 hidden-backend/service 身份证书。
- 独立 review 静态确认 C1/C2，且 adapter 与 synthetic 同一校验器；无新 confirmed false-accept。主动态结果与静态证据一致，仅闭合上述离线缺陷，不扩成全局 ACCEPTED。

## Assertion 与 fixture 语义处置

主读取全部 mapping 并比较测试与非测试 helpers，记录在 `integrity_v8_residual_disposition_20261009_r2/report.json`：旧 v4 **34**、旧 v7 **63** 方法全部映射，旧 assertion expression 缺失 **0**。AST/同名本身不代替语义；变化如下：

1. v4→v8 `test_pre_submit_contract_not_just_phase` 从宽松 phase envelope 正例改为完整 request/producer/active-source-bound proof 正例。原四断言保留，缺 proof、model_request_sent、automatic_retry 反例仍拒。这是 C1 所要求的合法 proof fixture 收紧，不放宽错误来源。
2. v4→v8 `test_success_resume_readonly_and_cache_reference` 保旧八断言，仅加 execution argv SHA 验证（九断言）。
3. v4/v7→v8 `test_ticket_survives_hold_disk_failure_cross_process` 保五断言；child 改当前 namespace、加 `-X utf8 -I -B` 与 raw bytes/hash/rc 捕获。主已将唯一 report locator **仅进程内**转到新主输出，历史写负例真被拒。原 suite 源仍固定历史 report 路径，**不得裸重跑**；必须保持 seam/独占新输出。
4. v4 helpers：payload 加 `thinking_effort=max`；adapter producer fixture 加真实 active source hash（仍 MOCK_ONLY）与显式旧 `implementation=v7` label；runner 从旧 legacy-builder patch 改当前 `build_task` patch。mock process 注入与原断言保留，不将 test identity 当实际生产者认证。
5. v7 所有十一旧 helpers 归一 namespace 后 AST 一致；v8 新加三 regression helpers。不删除旧方法或改变历史失败。

## Review 残留与纠正（原 review 不改）

- Review 文末“6 negative guards”纠正为主 **每 worker 7 项、两 worker**。
- 实现保护“41 hashes”不等41个文件：after **41 rows / 39 distinct**；其中 **29 distinct** 有 contemporaneous before baseline 并匹配，**10 after-only** 只能 current-after MATCH，不能推断历史 before。主五 source SHA 与十六实现 artifact SHA MATCH；主 scoped protection unchanged，不推广未纳入的目录。
- 重复 `item.started` 同 id 同 type：r2 定向真实 parser 输入为文本。完整 completed item/body/turn **接受**；pending reasoning 未完成和缺 turn terminal **拒绝**。确有重复 start 宽松残留，但本次输入不制造假 terminal；保为可选收紧项，不冒称已拒重复事件。
- **主探针首轮错误保留**：r1 给 `parse_codex` 传 bytes，而该函数要求 str；三次 `event stream must be text` 均只是输入类型拒绝，不能用于 event-state 结论。r1 原报告中重复-start disposition 不成立；r2 仅在诊断边界 UTF-8 decode，生产源码未改，`correction.json` 明确记录。稳定70suite未重复跑。
- Review 所谓 `%40token` userinfo 示例实际 URL path=`/%40token`、username/password=None、query空。主核 changing path 改环境身份；不能从该示例声称凭证绕过。更广 URI/私密配置协议仍未验。
- `classify_stop` 非 OSError 显式上抛，不静默放行；不泛称捕获所有异常。双 unittest.main 是可读性残留，不据此判功能失败。

## 严格保留的阻塞

- ROOT 外 queue_child_run 当前 absent 已核；历史创建/删除范围仍是实现者报告，未独立核证、不追认授权，主本轮未删除。
- seal 只是可重算 SHA，不是 HMAC/签名；不防全目录写者。有限 Python audit 不是 OS sandbox。
- 实际 CLI proof producer、真实事件协议、远端 BOM/CRLF/rstrip 归一化、私有 global config、外部服务和 Docker 仍未验证。
- production 仍 run124 B gpt56w；two-w held；REAL_EXECUTION_APPROVED=False。音乐验收 NOT_PERFORMED，三作品原验收与全部 ZIP 要求未完成。

**主处置：C1/C2 离线修复确认；v8 不获得真实路由 / 音乐 / production ACCEPTED。**
