---
name: run139-141-acceptance-r1
description: run139/run141 只读工程验收r1——run141通过、run139有一处真实失败
metadata:
  type: project
---

# run139/run141 只读工程验收 r1（2026-10-09）

## 文件 SHA（验收时刻）

- runs/run139_e7_flash_diag/go.py `12a8bec6…b8f4d5`
- runs/run139_e7_flash_diag/README.md `f0875b50…333d2983`
- runs/run141_thread_resume_r3/go.py `12712b97…5815e6`
- runs/run141_thread_resume_r3/README.md `bc01555f…b57eff93`
- tools/tests/test_run139_e7_flash_diag_r3.py `b8c6e4b8…689b691`
- tools/tests/test_run141_thread_resume_r3.py `7ec638ed…f6cd7ae7`
- tools/experiment_calls_v4.py `5dbb28ea…4495`（gate=false，只读）

## 实跑结果（均为 python -I -B，真实执行，非引用前人）

- run141：`python -I -B tools/tests/test_run141_thread_resume_r3.py` → exit 0，15/15 ok，耗时约12–19s。完整输出见本目录同名 .json（stdout 尾）。
- run139：`python -I -B tools/tests/test_run139_e7_flash_diag_r3.py` → exit 1，14/15，`test_direct_real_path_blocks_before_creating_real_run_outputs` ERROR。
- run141 `--strict`：exit 0，`COMPLETION_PENDING`，前后目录文件清单 diff 为空（无写入）。

## 任务1：目录名核查

- 现存仅 `runs/run139_e7_flash_diag`（无 `_r3` 后缀），`runs/run141_thread_resume_r3`；两目录内各仅 go.py + README.md，无 manifest/marker。
- notes 全仓 grep `run139|run141` 无命中；git 非本工作即查（git rev-parse true 但 log 对该路径无输出，旧 manifest 不存在）。brief 原文未在本只读输入范围内，故“_r3 交付为无_r3”记 **unknown**，不凭 mtime 断言覆盖关系。mtime 仅记录：run139 go.py 03:46、README 03:44；run141 go.py 03:43、README 03:41；v4 03:47。

## 任务2：import 副作用（读代码确认）

- run139 测试 `test_import_has_no_environment_io_cli_or_source_import_effects` 通过；go.py 顶层 import 仅 argparse/hashlib/importlib/json/random/re/sys/Counter/Path/typing，无 env/IO/write/subprocess 顶层调用。run_all(caller=None) 才走 `_load_v4_lazily_then_block`。
- run141 测试 import 探针通过；go.py 顶层 import 仅 argparse/difflib/hashlib/json/re/sys/Path/typing，无副作用。

## 任务3：挑战项结论（含最小复现）

- run139 compare：**逐位置验 quote**（best/worst 的甲乙丙各自必须含至少一个落在对应候选文本内的引号片段），非“仅一个quote”。复现：单位置伪造 quote 即 `best_moments[乙] has no quote…` 拒绝。注意：quote 只需“片段被包含”，长文本含一小段即过——这是已知宽松点，非失败。
- run139/run141 extract：**都会丢掉前后文字**（find 第一个 `{`/`[` 起解）。复现通过。这是“前后可塞废话”的已知缺口，建议新版本加严格模式（全文必须以 JSON 起止或白名单前缀）。
- mock-as-actual：run139 mock terminal `transport=MOCK`、`namespace=MOCK:run139…`、`real_model_submissions=0`，manifest 隔离明确；run141 mock producer `model=mock` 且 `execution_mode=mock_only`。把 mock 当 actual 的直接路径未发现；但 run141 `_validate_identity` 第365行条件写法可疑（`and`/`or` 混写，request_id 检查可能被短路），建议新版本加单测覆盖。
- run141 review schema：`validate_muse_return` 要求 schema 字典含 schema_id 且 raw 满足 required_keys——**非仅 mock**，且 quote 必须逐字含于 source text。缺口：无证据的真实 terminal 仍缺（muse_real_return_count=0，属预期未验收）。
- queue_stop：两套均有测试覆盖“停当前剩余+拦后续 stage”；run141 `run_stages` 对失败/queue_stop 后续 stage 标记 stopped_before_start。后续 stage 恢复需新 run（未提供恢复路径，属设计内 fail-closed）。
- v4 只读发现（gate=false，不启用）：`call()` 第60行 `resume_validations/new_model_submissions` 计数表达式按 resumed 布尔二选一累加、可读性差；第33–44行 resume 路径依赖外部 `runner_v4`/`execution_integrity_v4`（均缺失，import 即 ModuleNotFoundError）。独立 review 新缺口方向：cache/parse 边界与 queue_stop 语义需等模块就位后补测。

## 任务4：工程判定

- run141：**工程可用（离线）**，未验收项=真实 transport/ reviewers 真返回/音乐验收/production（均明确缺，无宣称）。
- run139：**未验收**——14/15，`test_direct_real_path_blocks_before_creating_real_run_outputs` 真实失败：v4 文件存在但其依赖缺失时抛未捕获 `ModuleNotFoundError` 而非 `RealExecutionBlocked`。复现稳定（两次运行同错，exit 1）。

## 任务5：修复建议（新版本，不碰旧文件）

1. run139 `_load_v4_lazily_then_block` 包 try/except ModuleNotFoundError→RealExecutionBlocked（含缺模块名），并补“依赖缺失”单测。
2. 两套 extract 加 strict 选项：要求全文 strip 后起止为 JSON 边界（或显式允许前缀白名单并记录）。
3. run141 `_validate_identity` 第365行重写为清晰多条件并补 request_id 冒充单测。
4. run141 README 第30行“v4 absent”已过期（v4 现存在但 gate=false），新版本改述为“present but unaccepted/blocked”。

## 完整输出存放

- `/tmp/r139_out.txt`（exit 1，14 ok + 1 ERROR）、`/tmp/r141_out.txt`（exit 0，15 ok）、`/tmp/r141_strict.txt`（exit 0，无写入 diff 空）。三者无 secret/token 关键字命中。建议主会话归档后删除。
- 本验收未写任何旧 runs 文件；mock 产物均在 TemporaryDirectory 内，已随测试清理。

**Why:** 主会话要求只读工程验收、不引用前人通过数、失败必须实跑复现。 **How to apply:** 修上述4项出新版本后重跑两套测试，以 exit 0/1 与本记录 SHA 对照。
