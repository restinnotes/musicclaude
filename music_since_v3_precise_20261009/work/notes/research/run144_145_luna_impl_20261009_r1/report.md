# run144/run145 r5 离线实现报告

## 交付状态

r5 工程实现与本地 mock 回归完成；不包含音乐候选/裁决，不构成音乐验收或 production。上一轮 independent Muse review 的 NOT_ACCEPTED 结论继续有效；第 19 项需要新的独立 review 与主验收后才能关闭。

新增源码、README、manifest 与两套 tests 均在 `report.json` 的 `new_artifacts` 中逐项列明。历史 30 项断言级映射见 [historical_assertion_mapping.json](historical_assertion_mapping.json)。

## 最终亲跑证据

attempt-008 捕获了五条最终命令的 argv、原始 stdout/stderr bytes、SHA、耗时、timeout 和 rc：run144 tests rc=0（25 tests），run145 tests rc=0（24 tests），run144 `--real` rc=3，run145 `--strict` rc=0，run145 `--real` rc=3。测试均仅用 Python `-X utf8 -I -B` 与本地 mock；provider/model CLI=0、network=未使用。

run144 fresh full mock 为 126 submissions（WHY 22、MECH 23、audit 46、surface 23、compare 12），同身份第二次新增 0。run145 fresh full mock 为 600（step 92、NLV match 4、Center 4、identity review 480、compare review 20），Muse TEST_ONLY packs 100；同身份第二次复用 600、提交 0，四条 match 证据均重新校验。数量有回归断言与 manifest 双重记录。

run144 真实入口只做共享入口 presence check 后阻断；run145 strict 是只读 preflight。两条 `--real` 路径均无 model/CLI 调用、无 run 写入。三个作品的 `06_ACCEPTANCE_CRITERIA.md` 未逐条验收，音乐状态为 `NOT_PERFORMED`。

## 失败证据与修复轨迹

attempt-001 至 attempt-008 均独立保留；未删除或改名任何 firstfail。早期失败依次暴露 compare task 缩进、Muse 来源字段 schema、`c` 槽位到具体 baseline 名称映射、直接 receipt helper 的 transport 校验等问题；每次都追加新 attempt。每条命令的原始 stdout/stderr 与 rc 在各 attempt 目录的 `.bin` 和 `commands.json`。

## Protected snapshot

protected-before/after 比较通过：30 个固定历史文件哈希、run141=2/run142=3/run143=3 个旧 run 文件清单及 presence-only probes 全部相等。只 hash 非敏感文件。未枚举、读取或写入 run140 来源归档及共享 v7；未读取 credentials/cookies/tokens；旧 CLAUDE/memory 未写。

## Muse schema 计数校正

先前 Muse review 的 NOT_ACCEPTED 仍为最终状态。报告计数需按实际冻结代码纠正：旧 run143 schema 是 21 个 required、19 个固定等值 expected，另对 `terminal_id` 与 `reported_transport` 单独检查；不能沿用 19/16。run145 r5 是 27 个字段（25 固定值 + attestation class 与 terminal ID 单独检查）；run144 r5 是 26 个精确字段。canonical target 固定为 `claude-proxy/muse-spark-1.3-contributor-free`/`mcp`。测试 receipt 均是 `TEST_ONLY`，没有真实 Muse 服务认证。

## 19 项保护矩阵

| 项 | 状态 | 证据摘要 |
|---:|---|---|
| 1 | PASS | 15+15 assertion-level historical mappings in historical_assertion_mapping.json; default parse retry was intentionally changed to STOP plus explicit bounded sample. |
| 2 | PASS | Distinct run144/run145 IDs and paths; import probes preserve inventories; protected run141/run142/run143 inventories unchanged. |
| 3 | PASS | Both --real commands return 3; preflight tests cover absent/present-unverified entries with 0 CLI, 0 submissions, 0 writes; no exec_module/sys.path import of shared entries. |
| 4 | PASS | Unverified v4, partial v5 and v6 in-flight label remain non-adopted; r5 labels the v6 state in_flight_not_auto_adopted, a descriptive wording correction only. |
| 5 | PASS | Both suites reject prefix/trailer/second JSON value, duplicate keys, nonfinite values, scalar/wrong type and bool-as-int at strict boundaries. |
| 6 | PASS | Frozen parser schemas; quote validation binds to mapped candidate text; exact task and candidate mapping sets; source, template and driver locks rechecked. |
| 7 | PASS | run144 full request identity binds slot, model/version, producer/source/template/driver and prompt bytes; run145 binds current mode, producer and exact slot. |
| 8 | PASS | Canonical Muse alias maps only to claude-proxy/muse-spark-1.3-contributor-free over mcp. run144 exact 26-field receipt; run145 exact 27-field receipt; TEST_ONLY never counts real. No verifier means pending/raw_unverified. |
| 9 | PASS | Thread frozen schemas enforce guess, fits, confidence strict integer, and candidate-specific exact citations; duplicate/unknown fields reject. |
| 10 | PASS | Completed parse failure writes raw/prompt/meta/terminal before parse and survives restart; default STOP; only explicit True + strict budget <=2 + reason can create immutable sample. |
| 11 | PASS | Injected sourcebound pre-submit proof is exercised through execute failure→success→reuse; bad/claimed/ambiguous/queue/exhausted proofs persist hold; same sampling identity retained. |
| 12 | PASS | Full request/slot lineage hashes, exact disk bytes, terminal/meta bindings, duplicate success and tamper paths are rejected before reuse. |
| 13 | PASS | Four 23-step chains complete mock validation; Center binds all 23 step outputs and required match lineage; second identical run has zero submissions. |
| 14 | PASS | One k2 NLV per chain yields four exact source match tasks; full prompt/raw/meta/lineage validated through _stage_parse and exact source map; None does not delete; second run verifies four match artifacts. |
| 15 | PASS | v2/v3 only Q3 single-line change positive; multiple-change, non-Q3, multiline and byte/hash mismatch negatives. |
| 16 | PASS | Canonical self-review labels and anonymous rotations; run144 reader asserts actual expanded/recap text; run145 retirement uses exact source quote and lineage, not caller-supplied judgment. |
| 17 | PASS | Mock status stays COMPLETION_PENDING, no DONE, real count zero, music_acceptance NOT_PERFORMED; no production/gate/hold or CENTER_v0 mutation. |
| 18 | PASS | Import/strict/real side effects tested; first failures and every stdout/stderr/rc retained in attempt-001 through attempt-008. |
| 19 | PENDING_EXTERNAL_REVIEW | This implementation does not accept itself. Prior independent Muse review remains NOT_ACCEPTED; a fresh independent review and main acceptance are still required. |

完整数据、哈希与每轮测试状态见 [report.json](report.json)；源码/输入哈希和 mock boundaries 位于各自 revision `manifest.json`。
