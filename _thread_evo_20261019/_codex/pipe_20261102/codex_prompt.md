# 任务：给 Thread 迭代写一个“流水线说明 → 直接运行”的通用脚本

工作目录：D:\musicclaude\_thread_evo_20261019（下称 ROOT）。本机 Windows；PowerShell 5.1 会把无 BOM 的 UTF-8 中文读成乱码，读写文本一律用 Python 或 `-Encoding UTF8`。

## 背景
ROOT/schemes.py 是我手写的一次性运行脚本：它按顾问给的提示词（ROOT/schemes/*.txt），一步步调用模型（`evo.call`），把上一步的 JSON 输出填进下一步提示词的占位符，最后把“线”保存成标准格式（`evaluations/v6fix/<作品>_<版本名>.json/.md`，见 schemes.py 的 `save()`）。每来一套新方案我都要再手写一次。请把它做成通用的。

## 要做的
1. 新建 ROOT/pipe.py 和说明格式（JSON），一份说明描述一套流水线：
   - steps：每步有 id、prompt_file（ROOT/schemes 下的文件）、replace（占位符 → 来源）、model（"g6"/"g56"，对应 `v6fix.JUDGES`）、可选 append（在提示词末尾追加的段落模板，也可含占位符）、可选 after（依赖的步骤 id；没有依赖的步骤并行跑）。
   - 来源可以是内置量：WORK_INFO、SEGMENTS、CENTER、BEADS_TEXT（含义和 schemes.py 里完全一样），也可以是 `step:<id>`（那一步解析出的 JSON，按 `json.dumps(ensure_ascii=False, indent=1)` 填入），还可以是固定文字。
   - 可选 edits：对某个提示词文件做“原文片段 → 新片段”的替换（schemes.py 的 P_A2_C_OLD/P_A2_C_NEW 就是这种）。
   - final：最后一步的 id，它的输出用 `save()` 的同样逻辑存成标准格式（字段 sec/relation/items[text,cite,after]）。
   - 运行 id 规则与 schemes.py 一致：`sc{TAG}_{作品}_{step id}`；再加可选 `SAMPLE=k` 环境变量，用于同一说明并行生成多份（Best-of-N），此时 id 后缀 `_s{k}`、TAG 后缀 `s{k}`。
   - 用法：`python pipe.py run <说明文件> <TAG>`，两首作品（op60、op61）并行。
2. 把 schemes.py 现有的两套方案 P、Q 各写成一份说明：ROOT/schemes/P.json、ROOT/schemes/Q.json。
3. 验证（不调用任何模型、不联网）：用打桩替换 `evo.call`/`evo.done`/`V.parse`，对 P、Q 两套、两首作品，证明 pipe.py 渲染出的每一步提示词与 schemes.py 渲染出的**逐字一致**（用相同的假 JSON 作为上一步输出）。另外如果 ROOT/runs/scpa_op60_A0/prompt.txt 等真实运行文件已经存在，也拿 pipe.py 渲染结果和它们逐字比对。
4. 中文 README：ROOT/schemes/README_pipe.md，写清格式和一个例子。

## 边界
- 只新建 pipe.py、schemes/P.json、schemes/Q.json、schemes/README_pipe.md，以及验证用的临时文件（放 ROOT/_codex/pipe_20261102/ 下）。不要修改任何已有文件（包括 schemes.py、evo.py、v6fix.py）。
- 不调用任何模型，不发网络请求；不改提示词内容、模型、推理参数、联网权限；不动缓存保温机制和 watchdog，不新增定时任务。
- 详细日志写到 ROOT/_codex/pipe_20261102/log.md。最后只回报：成功/失败、新增文件、逐字比对结果、风险。
