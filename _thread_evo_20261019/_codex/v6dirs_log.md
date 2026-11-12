# v6dirs 实现与验证记录

工作目录：`D:\musicclaude\_thread_evo_20261019`。任务日期：2026-10-29。

## 边界与准备

- 只实现 A2/B1 运行器和离线验证；未启动真实 `whole` / `rad`。
- Python 读写文本全部显式使用 UTF-8。最初尝试 PowerShell here-string 经管道传给 Python 时，PowerShell 5.1 在 stdin 前带了 BOM，触发 SyntaxError；该命令未执行任何文件操作。随后改用 `python -c` 和补丁工具。
- 已阅读 `v6fix.py`、`v6dirs_prompts.py`、`evo.py` 及分段、作品名与珠子读取接口；工作目录及检查的父目录没有适用的 AGENTS.md。
- 修改前保存 `_codex/v6dirs_baseline.json`：受保护文件 SHA-256、除 view 外的 v6fix AST、原 view 函数源码、两首 v6 在 ids=False/True 下的原始渲染。
- op60 有 14 段，op61 有 13 段。
- 不操作后台进程、watchdog、缓存保温、定时任务。运行器拒绝使用 `r2`，避免写入仍在运行的 A1 结果。

## 实现

- 新增 `v6dirs.py`，提供 `whole <w> [w1]`、`rad <w> [s1]`、`dry <w>`。
- A2：原始 v6 + 全曲珠子 + 顺序诊断；按 sec 重组；tidy；核对使用独立的前缀图，调用原 `v6fix.check`，`evo.run_parallel(..., 4)`；收集原 `review_notes`，最多一次整首退改；保留最终 edit 和 changes。
- B1：按段串行；只传已完成段落和本段珠子；首次和退改后均清空 relation；核对沿用 A1 的意见提取规则，仅去掉 lost 并增加 progress；每段立即保存 JSON/MD；最后调用 Center 并填 relation，缺项默认“正在面对”且记录。
- 首轮生成 JSON/基本容器结构无法解析时，使用 G56 和后缀 b 重试一次；所有调用先检查 `evo.done`。退改失败保留第一版并记录。核对或 Center 无有效解析结果时抛错退出，B1 保留已落盘进度。
- 所有模型调用仅经 `evo.call`，写作/退改 meta 有 web=True；核对/Center 没有 web。没有额外模型参数、推理参数、槽位、节流、轮询。
- JSON 保持 graph/rows 接口；A2 另含 changes；异常兜底情况另存 errors。MD 使用指定 A2/B1 标题及 `v6fix.view(graph)`。
- `v6fix.py` 仅修改 view 的段标题两行：relation 为 None 或空串时省略括号，非空时保留原完整空格、标点和内容。
- `_codex/test_v6dirs.py` 使用 unittest/monkeypatch；FakeModel 的 call/done/output 仅使用 TemporaryDirectory，另将 evo.RUNS 和 v6fix.OUT 指向临时目录。文件写入守卫同时检查 builtins.open 与 io.open，任何临时目录外写入立即报错。

## 初次 dry

直接运行 `python v6dirs.py dry op60` 和 `python v6dirs.py dry op61`，均成功，输出到 `_codex/dry_{w}_*.txt`。

| 消息 | op60 字符数 | op61 字符数 |
| --- | ---: | ---: |
| whole | 51279 | 52314 |
| rad_first | 2510 | 2813 |
| rad_second | 2752 | 2904 |
| rad_check | 1572 | 1717 |
| rad_center | 460 | 467 |

以上为 Python len，包含空格与换行。whole 的诊断来自现有只读诊断缓存；dry 中 B1 使用明确构造的假段落，不调用模型。

## 验证结果

首轮离线执行：12 项中 11 项通过；唯一失败是测试错误地把 Center 示例中嵌套 JSON 的合法 `}}` 当成未展开花括号。运行器和提示词没有问题。已删除错误的括号尾部断言，保留大写占位符检查与对每份 JSON 示例的 `json.loads` 验证。B1 完整流程额外禁止调用 v6fix.v6，确认运行器不会读取底稿。

修正后 12 项全部通过。最终自查又补充一个 Center 边界：若整个 relations 字段缺失/为 None，也视作各段缺少 relation，逐段填入“正在面对”并记录；非对象类型仍报错。这符合“缺的填默认值”，不修改提示词或评审规则。新增对应测试后，最终共 **13 项全部通过**。

### 实际执行的验证命令

均直接使用 Python 3.12.10，没有 `-I`。

```text
python v6dirs.py dry op60     # exit 0
python v6dirs.py dry op61     # exit 0
python _codex/test_v6dirs.py  # 最终 exit 0，Ran 13 tests in 2.179s，OK
```

另用 Python `py_compile.compile(..., doraise=True)` 检查 `v6dirs.py`、`v6fix.py` 和 `_codex/test_v6dirs.py`，全部通过。编译仅产生常规字节码缓存。

对磁盘上的 10 份实际 dry 产物再次检查：每份均无 `{NAME}` / `{SEC}` 等大写占位符残留，每份都恰有一个 JSON 示例块，全部可由 `json.loads` 解析。合法嵌套 JSON 的 `}}` 原样保留。中文 UTF-8 正常。

### 离线测试覆盖与证据

1. 两首真实 v6 的默认渲染/ids 渲染与修改前保存的四份文本逐字一致；另使用保存的原 view 函数，对每首的 ids、center、head、secs 共 16 种参数组合逐字比对，合计 32 次组合验证。relation=None/空串标题均只有 `### S01｜1–3 小节`。
2. 受保护文件逐字 SHA-256 一致，v6fix 除 view 外的整个 AST 一致；view 源码恰好是允许的标题行替换，没有其他修改。
3. A2 在两首上完整执行，使用倒序返回的 segments 验证按 sec 重组；使用真实 run_parallel，确认参数为 4；逐份检查核对 DONE 只包含该段之前的段，且没有当前或未来段；仅有意见的 S02 出现在退改 NOTES 中；一次整首退改后 edit/changes 为最终版本且所有 rows 标记 revised=True；Center 保持原 v6。
4. A2 无意见时不调用退改；首轮缺段生成空 items 并记录；退改无效保留首版、changes 和 revised=False；tidy 清除向前/不存在的箭头。
5. B1 在两首上完整串行生成、核对、退改和 Center。运行器执行阶段将 v6fix.v6 替换为直接抛错的函数，仍顺利完成，证明不加载 v6 底稿。检查后一段消息包含前一段最终文字，S02 退改先于 S03 生成。
6. 在每次后续段生成和 Center 调用前读取临时进度文件，确认 JSON 已即时落盘、段数正确、center 为空、所有 relation 为空；两首共检查 27 个进度快照。Center 输入不含 ids；缺单段及缺整个 relations 都按要求默认并记录。
7. B1 意见提取验证越界、勉强箭头、读不懂、gaps 之外的 unexplained、wordy 和 progress；排除 lost 及已在 gaps 中的珠子。
8. A2/B1 首次生成解析失败使用正确后缀 b/G56；两次失败会停止。退改失败保留原版；核对失败停止而不接受未核对内容；Center 失败保留所有逐段 JSON/MD 进度。
9. 重复完整运行复用所有 done 结果，包括首次坏 JSON 对应的已完成备用 b，不新增 fake call。逐条断言所有模型、stage 和 web meta 完全符合方向及阶段。
10. 两首 A2 的 JSON/MD、两首 B1 的 JSON/MD 均通过真实 `v6fix.graph_of`、`view` 和 BLIND 消息的组图部分；分别真实执行 `v6fix.join('w1')` / `join('s1')`，读取真实珠子并生成临时合成 MD，两首均被包含，没有修改 join/盲评/评定模块，也没有调用盲评模型。
11. 默认 tag 使用 w1/s1；拒绝 r2 与路径穿越 tag，验证拒绝前没有模型调用或文件写入。
12. 所有 fake call 的 input/output/meta、结果 JSON/MD、join MD 和测试 dry 均写在系统 TemporaryDirectory 内；builtins.open/io.open 写入守卫全程启用，未发生临时目录外写入；临时目录测试结束后自动删除。真实 runs/、evaluations/v6fix/ 没有收到测试写入。真实诊断、v6 和珠子只有只读访问。

### 最终受保护文件指纹

| 文件 | SHA-256（前后相同） |
| --- | --- |
| v6dirs_prompts.py | df011e636642abd6f9b10ef4bbdf6178343960ab02ac9bf542f83daa2e4ec0ef |
| evo.py | 7309412fdfbee1ff550284d2bc0032eb3f8c55675274645f3e369ab0b0a8e8cc |
| gpt3_call.py | 7fabbe3bb1b093ad310b5ce3ce5e7dd3e67bdb93e892d1432f656b5680f1faa3 |
| mg_call.py | 1f50df2b0a3fe6483e90985a1a74d905b908f7cc5851b6dcfb1e9326a2c564fd |

v6fix 的 WHAT、DIAG、FIX、CHK、REV、BLIND 等常量及 beads 输入处理、评审标准、其他函数均未改变。未改联网权限、模型或推理参数。未修改 gate_v6.py。没有新增定时任务或轮询。没有停止/控制后台 A1，未向 `evaluations/v6fix/op60_r2.*`、`op61_r2.*` 或其 runs 目录写入。

## 交付与限制

- 主文件：`v6dirs.py`。
- 唯一既有源码变更：`v6fix.view` 的空 relation 标题兼容。
- 验证与记录：`_codex/test_v6dirs.py`、`_codex/v6dirs_baseline.json`、本日志、10 份 `_codex/dry_op6x_*.txt`。
- 默认启动命令：`python v6dirs.py whole op60` / `whole op61` / `rad op60` / `rad op61`；本次均未在真实传输下执行，由用户自行启动。
- 未发现重大实现风险。真实模型生成的内容质量、真实调用耗时和最终盲评结果尚未验证；本次按照边界只验证运行器行为、消息格式及下游读取兼容性。
- 核对或 Center 无有效解析时会以非零退出码停止。B1 中断文件包含已完成段，但 Center 可能尚为空；此时是进度文件，应以命令完整成功后再做最终盲评/评定。
