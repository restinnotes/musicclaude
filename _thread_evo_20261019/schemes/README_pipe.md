# Thread 流水线说明与运行

`pipe.py` 把一份 JSON 说明执行为流水线。运行时继续使用现有 `evo.done`、`evo.call` 和 `v6fix.parse`；本次开发只做了离线打桩验证，没有提交模型请求。

在 `D:\musicclaude\_thread_evo_20261019` 打开 PowerShell：

```powershell
python pipe.py run schemes/P.json pa
python pipe.py run schemes/Q.json qa
```

每次同时处理 `op60`、`op61`。说明文件路径相对于当前工作目录，也可以传绝对路径；`prompt_file` 始终相对于本脚本所在目录下的 `schemes/`，与启动目录无关。

默认上游版本为 `m6w`，与 `schemes.py` 一致；可用 `$env:REF = '其他版本'` 指定。上游数据是 `evaluations/v6fix/<作品>_<REF>.json`。运行正常完成后生成 `evaluations/v6fix/op60_<TAG>.json/.md`、`op61_<TAG>.json/.md`。

## JSON 格式

顶层字段：

| 字段 | 含义 |
| --- | --- |
| `name` | 可选，默认说明文件名（去扩展名）；用于 `meta.stage = scheme-<name>`。P/Q 分别使用 P、Q，与原脚本一致。 |
| `note` | 可选，默认等于 `name`；写入成品 JSON 的 `base` 字段。 |
| `steps` | 必填，非空步骤数组；数组顺序不隐含依赖。 |
| `edits` | 可选，提示词片段替换数组，只作用于内存。 |
| `final` | 必填，要保存的最终步骤 id。所有步骤完成后才保存它的输出。 |

每个步骤：

| 字段 | 含义 |
| --- | --- |
| `id` | 唯一标识，只含英文字母、数字、下划线、连字符，且以字母或数字开头。 |
| `prompt_file` | `schemes/` 内现有 `.txt` 文件的相对路径，例如 `P_A0.txt`。 |
| `replace` | 必填，占位符 → 来源的 JSON 对象；无替换时填 `{}`。键含占位符本身的括号，例如 `"{NAME}"`。按 JSON 中的键顺序执行 `str.replace`，替换全部匹配片段。 |
| `model` | 必填，`g6` 或 `g56`，直接映射 `v6fix.JUDGES`。 |
| `append` | 可选，原样追加到提示词末尾的字符串模板；需要的换行自行写成 `\n`，其中的占位符也由本步 `replace` 替换。 |
| `after` | 可选，依赖步骤 id 的数组，也接受单个 id 字符串；依赖完成后才执行。 |

来源支持以下形式，也适用于 `edits[].new`：

| 来源 | 展开内容 |
| --- | --- |
| `"WORK_INFO"` | 从 `works/<作品>/work.json` 读取 `composer`、可选 `composer_en`、`title_zh`、`opus`，拼为作曲家及作品两行；当前双曲输出逐字保持原样。 |
| `"SEGMENTS"` | 上游图各段依次拼为 `S01：第 <bars> 小节`，用换行连接；与 `schemes.segments()` 相同，不包含 Center。 |
| `"CENTER"` | 上游图 `center` 原文。 |
| `"BEADS_TEXT"` | `covjudge.bead_text(作品)` 原文。 |
| `"step:A1"` | A1 解析出的整个 JSON，严格按 `json.dumps(value, ensure_ascii=False, indent=1)` 展开。 |
| 普通字符串 | 固定文字，例如 `"3"`、`"（无）"`。 |
| `{"text": "CENTER"}` | 强制使用固定文字，避免与内置量或 `step:` 前缀混淆。 |
| 来源数组 | 逐项展开并直接连接，不加分隔符，例如 `["SEGMENTS", {"text": "\n【Center】\n"}, "CENTER"]`。 |

`step:` 引用自动形成依赖，包括来源数组和 `edits[].new` 中的引用；无需重复填写 `after`。`after` 可补充“不读取输出但必须等它完成”的依赖。无依赖的步骤并行执行；各分支完成后，已满足依赖的后续步骤立即可以执行。

渲染顺序固定为：读取 UTF-8 提示词 → 按数组顺序应用本文件的 `edits` → 原样追加 `append` → 按键顺序应用 `replace`。不使用 Python `format()`，提示词中的 JSON 花括号不会被误处理。固定文本和展开的 JSON 如果含后续替换键，也会受到后续 `str.replace` 的影响，与原脚本一致。

`edits` 示例（这里只展示格式；完整 Center 片段见 `P.json`）：

```json
[
  {
    "prompt_file": "P_A2.txt",
    "old": "原文中的完整片段，包含准确的空行",
    "new": [
      {"text": "新片段的开头\n"},
      "CENTER",
      {"text": "\n新片段的结尾\n"}
    ]
  }
]
```

`old` 必须是非空的逐字原文，并且能在相应提示词中找到；不会写回 `.txt`。同一文件的 edits 依次执行；如果后续 edit 要匹配前一 edit 新增的文字，前一 edit 的 `new` 应为固定字符串或 `{"text": "…"}`，以便启动前验证。未知步骤、循环依赖、无效模型、缺少提示词、失效的原文片段等会在启动调用前报错。

## 完整例子：Q

下面是一份可执行说明，结构与附带的 `Q.json` 相同；`note` 可按用途填写。

```json
{
  "name": "Q",
  "note": "三条经历骨架及账本 → 宏观选路与珠子去词化 → 一次成图",
  "steps": [
    {
      "id": "A1",
      "prompt_file": "Q_A1.txt",
      "replace": {"{NAME}": "WORK_INFO", "{SECTIONS}": "SEGMENTS", "{K}": "3"},
      "model": "g6"
    },
    {
      "id": "A2",
      "prompt_file": "Q_A2.txt",
      "replace": {"{ROUTES}": "step:A1"},
      "model": "g6",
      "append": "\n\n【候选路线】\n{ROUTES}"
    },
    {
      "id": "A3",
      "prompt_file": "Q_A3.txt",
      "replace": {"{SEGMENTS}": "SEGMENTS", "{BEADS_TEXT}": "BEADS_TEXT"},
      "model": "g6",
      "after": ["A1"],
      "append": "\n\n【段落】\n{SEGMENTS}\n\n【珠子】\n{BEADS_TEXT}"
    },
    {
      "id": "A4",
      "prompt_file": "Q_A4.txt",
      "replace": {
        "{SECTIONS}": "SEGMENTS",
        "{ROUTES}": ["step:A1", {"text": "\n\n【宏观评审结果】\n"}, "step:A2"],
        "{TARGETS}": "step:A3"
      },
      "model": "g6"
    }
  ],
  "final": "A4"
}
```

A2 因读取 `step:A1` 自动等待 A1。A3 用 `after` 等待 A1，然后与 A2 并行；A4 等待 A1、A2、A3。P 的结构是 A0 → A1 → A2，并在 A0 输入 Center、在 A2 内存替换 Center 规则。

**模型沿用事实：**旧 `schemes.py` 的通用 `call()` 对 P、Q 均固定传 `evo.G6`。Q 的“GPT-5.6 顾问方案一”描述的是顾问来源，因此附带的 P/Q 说明均填写 `g6`。新说明可以按需要明确选择 `g56`。

## SAMPLE 与运行 id

普通运行 id 为 `sc<TAG>_<作品>_<步骤id>`，如 `scpa_op60_A0`。有 `SAMPLE=k` 时，在运行 id 末尾加 `_s{k}`，成品 TAG 则加 `s{k}`：

```powershell
$env:SAMPLE = '2'
python pipe.py run schemes/P.json pa
Remove-Item Env:SAMPLE
```

此例运行 id 为 `scpa_op60_A0_s2`、`scpa_op60_A1_s2`、`scpa_op60_A2_s2` 等，成品为 `op60_pas2.json/.md`、`op61_pas2.json/.md`。SAMPLE 接受非负整数，原样保留数字（`02` 与 `2` 是不同样本）。空字符串不代表未设置，应删除环境变量。

Best-of-N 可在多个 PowerShell 进程中用相同说明、相同 TAG、不同 SAMPLE 同时运行，每个进程自行生成两首作品；本脚本不自动筛选最优样本。TAG 与步骤 id 使用相同字符规则。

## 最终 JSON、缓存及离线验证

最终步骤应输出 `{"segments": [...]}`，每段有 `sec`、`relation`、非空 `items`；条目有 `text`，可含 `cite`（编号字符串数组）和 `after`（按真假转为 `follows`）。例如：

```json
{"segments": [{"sec": "S01", "relation": "还说不清", "items": [{"text": "他还没想清楚。", "cite": [], "after": false}]}]}
```

实际必须覆盖上游全部段落。保存完全沿用旧 `save()`：按上游顺序和小节数保存；条目重编为 `S01-1` 等；只保留对前面已完成段落的合法引用；转换为 `引用` 链接并调用 `V.tidy`。成品 Center 使用上游原文，`rows` 也继承上游，`base` 使用说明中的 `note`。最终步骤自写的 Center 不覆盖上游 Center。

已有 `evo.done(id)` 为真的结果会跳过提交，仍通过 `V.parse` 解析。解析失败或最终缺段会报错；任一作品失败，进程退出码非零，另一首已完成的成品可以保留。更换说明、提示词或模型时应使用新 TAG / SAMPLE，因为旧缓存按运行 id 判断；重复同一 TAG / SAMPLE 运行会沿用缓存，并重新写相同版本名的成品。每个并行任务须使用不同 id，避免竞争同一缓存和成品文件。

脚本只传现有 `model` 和 `stage`，推理参数、联网权限、路由节流、缓存、保温与 watchdog 均由现有实现处理。渲染正文与路由实际保存的 `prompt.txt` 可能相差现有路由自动追加的 `evo.NO_WEB`；验证对此分别记录正文和完整提示词的比较结果，不向正文额外加入该段落。

离线验证产物在 `_codex/pipe_20261102/`。可在 ROOT 运行：

```powershell
python -B _codex/pipe_20261102/verify.py
```

验证脚本对 `evo.call` / `evo.done` / `V.parse` 打桩，用相同假 JSON 分别执行旧、新流程，比较两套方案、两首作品的全部提示词和调用参数；成品比较只写入验证目录。它还阻止网络与子进程调用，以及验证目录外的文件写入。详细结果见该目录的 `log.md` 和 `results.json`。读取中文文件请用 Python 显式 UTF-8 或 PowerShell `Get-Content -Encoding UTF8`。


## 2026-11-02 批量分关入口

新实验使用 `experiment_batch.py`；两个旧测量入口转为盲比→覆盖→单独读，默认不启动复述诊断和开放评审。`pipe.py` 仍可复现旧方案。

```powershell
# 只冻结顾问输入，不提交模型调用
python experiment_batch.py prepare-advisors round28_fast --count 10 --base qurefs --sources qu qb r27p2
# 恢复迭代后运行三位顾问，再导入十套方案
python experiment_batch.py run-advisors runs/_batches/round28_fast/advisors.json
python experiment_batch.py import-advisors runs/_batches/round28_fast/advisors.json
# 执行者通读提示词、检查泛化/接口后记录，不是向用户新增审批
python experiment_batch.py review-prompts runs/_batches/round28_fast/manifest.json --notes '实际检查结论'
python experiment_batch.py generate runs/_batches/round28_fast/manifest.json
# 新阶段返回即停；执行者读完整output.txt后记录
python experiment_batch.py review <run_id> --notes '完整阅读及硬约束检查结论'
# 不合格加 --reject；合格再generate，直到双曲A4完成并读过
python experiment_batch.py screen runs/_batches/round28_fast/manifest.json
# 只读已有证据，不发模型请求
python screen_flow.py r27p2 --base qurefs --inspect
# 幸存者完成所需生产后补第二组盲比
python measure_candidates_20261102.py <tag> --base qurefs --repeat
# 上游×写线层交叉，必要时另起名字加 --split-upstream
python experiment_batch.py cross locate28 --upstreams schemes/Q15.json schemes/R27P2.json --writers schemes/Q15.json schemes/R27P2.json --base qurefs --sources qu r27p2
```

复用仅限同模型/High/Mimic、实际输入逐字相同且返回完整，保存 `reuse.json`；不覆盖在途记录。新产物的检查绑定output哈希；候选提示词检查绑定scheme/提示词哈希。交叉组合先检查中间结构和语义兼容，再生成；不固定承诺20调用或半小时能定位。只有接近过线者退回，精确定义见迭代准则第五节。


当前通路优先级（用户11-02最新指令）：新批量入口默认gpt3s，MimicGate为普通故障备用；gpt3普通停用标记60秒后可恢复，明确可疑行为暂停半小时，不自动切换。沿用各通路原模型/强度设置；历史已完成上游仍按原模型/High/Mimic输入精确复用，不重生成已接受骨架。真实长任务恢复检查先单请求，成功后才受控并行。

`round28_fast`已经冻结，不要再次prepare同名批次；继续时直接使用现有advisors.json，材料变化另起批次名。其g6顾问任务已完整返回并读过，run-advisors会复用该完整结果，只提交尚缺的顾问任务。
