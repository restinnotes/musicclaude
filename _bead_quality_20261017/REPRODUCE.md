# 保持可追溯地复用本轮方案

## 阅读与复核无需模型

先看 [READER.md](READER.md) 或打开 [离线阅读与对照](阅读与对照.html)。所有最终正文、连续原句和实际模型响应都在文件里；不必运行任何命令才能判断质量。

从工作目录执行以下命令，只做本地验证和重建阅读文件，不发模型请求：

```powershell
python D:\musicclaude\_bead_quality_20261017\scripts\validate_frozen.py
python D:\musicclaude\_bead_quality_20261017\scripts\build_delivery.py
python D:\musicclaude\_bead_quality_20261017\scripts\build_reading_view.py
python D:\musicclaude\_bead_quality_20261017\scripts\validate_delivery.py
```

最后一个脚本验证最终14段、原句、来源、同输入的模型对照及最终文件。它不产出艺术分数。

`build_delivery.py` 以 `editorial/candidate_beads.json` 的已编辑版本为真源，输出 `FINAL_BEADS.json`、`FINAL_TRACE.json` 和阅读文档。该JSON字段仍叫candidate，是编辑过程的文件名；当前条目标记为edited_release。没有把主编辑改稿写回任何模型response.txt。

## 固定输入

- **推荐写作指令：**[COMMON_V2.txt](prompts/COMMON_V2.txt) + [METHOD_A2.txt](prompts/METHOD_A2.txt)。
- **正式十四段完整输入：**[production_context/inputs](production_context/inputs/)，每段均包含任务、原范围、完整相关原A、必要事实边界和继承标题。只读使用，不再摘要原文。
- **受控实验输入：**`inputs_v2` 与 `snapshots/pilot28`，按当时实际版本保留。不要用生产修复版覆盖实验文件。
- **段内事实：**`audits/facts_Sxx.txt`。事实提示仅校准位置／方向／边界，不生产心理解释。
- **源文件：**`sources/SRC-*.md` 是原稿原字节复制；[sources/units.json](sources/units.json)为可检索单元。GLOBAL完整另存，非局部写作输入。

FROZEN 标记阻止旧构建脚本在内容变动时覆盖实验输入。新尝试使用新的输入文件、新job ID和新输出目录；不要删掉标记让结果“对得上”。

## 若继续实际试写

运行器见 [RUN_CALLS.md](scripts/RUN_CALLS.md)。默认dry-run，显式 `--execute` 才调用。它使用本机既有safechain／OpenCode环境；交付包不包含登录凭据，不意味着换一台机器即可免配置运行。

下面只是准备新调用的例子，不是本轮已执行记录。将它保存为实验根目录下的新jobs文件，先用实际输入文件的SHA256替换占位字段：

```json
{
  "schema_version": 1,
  "max_workers": 1,
  "output_dir": "scripts/future_results",
  "jobs": [
    {
      "job_id": "S02_A2_context_next01",
      "channel": "gpt2",
      "model": "gpt-6-thinking",
      "prompt_file": "production_context/inputs/S02_A2.txt",
      "prompt_sha256": "填写实际完整文件的SHA256",
      "timeout_seconds": 7200,
      "min_response_chars": 100,
      "labels": {"segment": "S02", "method": "A2", "source_count": 30, "phase": "future_explicit_run"}
    }
  ]
}
```

预检命令是 `python scripts/run_calls.py --jobs <新清单> --dry-run`。确认输入完整后，将 `--dry-run` 改为 `--execute` 才会发请求。模型不会自动换路、降配置、缩Pool或重试；每个job独占目录，已存在则拒绝覆盖。

`min_response_chars` 仅拦空白／截断输出，不是质量分数。不要用它选冠军。

## 这次真正可删的负担

无需先生成一篇长内部珠子再把同样的意思写一遍；无需按每个来源逐项向读者交代；无需把未采用UID与正文引用混算；无需为全部GLOBAL写一层新的综合研究。保留的是短事实校核、完整原文、正文后的可验证取材证据，以及主编辑的实质删留。

A2并非免编辑保证。遇到“虽然具体，但整段仍只论证怕失去”，或把多套人物场景机械串联时，应回到原A做取舍；不再靠第三轮更换几个形容词继续抽样。本轮实际方法／模型输出保留在 [MODEL_METHOD_COMPARISON.md](MODEL_METHOD_COMPARISON.md)。
