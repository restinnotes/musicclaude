- **成功。** 已完成修改和离线验证，过程记录在 [_codex/gap_log.md](D:/musicclaude/_thread_evo_20261019/_codex/gap_log.md)。

- **主要修改：** [gpt3_call.py](D:/musicclaude/_thread_evo_20261019/gpt3_call.py) 现在在同一个 GATE 锁内等待上次提交间隔、启动 `Popen`，并轮询本次新建且正文匹配的任务目录，直到取得真实提交时间且 `first_chunk_ms` 非空，或进程退出、达到 180 秒超时。STAMP 使用真实提交时间，缺失时回退到当前时间；锁外调用 `communicate()`，删除了结束时覆盖 STAMP 的代码。日志新增 `submitted_utc`、`gap_since_prev_submit_s`。已自查：提示词、联网权限、工具能力、附件/珠子输入、模型与推理强度校验、评审标准、槽位、GAP 默认值、重试和停止规则均未改变；未修改 `evo.py`、`mg_call.py`、保温机制或 watchdog，未操作后台进程及其运行目录。

- **测试情况：** [_codex/test_gap.py](D:/musicclaude/_thread_evo_20261019/_codex/test_gap.py) 的 7 项离线测试全部通过，最终耗时 14.927 秒。使用真实 Windows 跨进程字节锁、4 个并发调用和缩放后的慢上传场景；测试 GAP 为 0.3 秒，三段真实提交间隔为 **1.6753、1.0155、1.0282 秒**，且每个后续调用都在前一个首片段出现后才启动。超时、提前退出、结果解析、日志字段、附件、长提示词和停止规则验证通过，编译及修改范围检查通过。未发出真实模型请求，未写入真实 runs、STAMP 或锁文件。完整输出见 [gap_test_output.txt](D:/musicclaude/_thread_evo_20261019/_codex/gap_test_output.txt)。

- **重大风险：** 现有 6 个旧后台进程仍使用旧逻辑并共享 STAMP，混跑期间无法保证全局满足新节奏；未重启它们，重启由你操作。按要求，180 秒超时后会警告并释放 GATE，因此超时回退路径不能保证“前一个开始返回后才启动下一个”；缺失真实提交时间时，两项日志字段为 `null`。