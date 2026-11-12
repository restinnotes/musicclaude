# README_FIRST（music_bead_auto_20261016 · STEP4 GPT-6w珠子生成轮）

先读本文件，再看 BEADS_FOR_USER.md（读者珠子）、BEAD_SOURCE_LEDGER.md（来源台账）、RUN_CALLS_AND_FILES.md（调用记录）。

## 本轮是什么
- 任务：按新任务包执行STEP4——为C2冻结十四段（S01–S14，1–116）逐段生成GPT-6w珠子；只调GPT-6w链路，不做git/读谱/T/H/Thread/WHY/E7/盲评。
- 输入复用：模板（`music_bead_published_structure_only_20261015/prompts/04_固定乐段Aonly珠子.txt`）、`out/structure.json`、`out/A_POOL_MAP.json`（7件归段：A01/A03/A04/A05/A06 int＋A07/A08 web；13段有PRIMARY、S09无；UNRESOLVED 11条、LONG_RANGE 29条不进读者正文；缺口4件 A02/A09/A10/A11 无条目）、`out/STRUCTURE_LEVELS_AND_CHOICE.md`。

## 结果一句话
- **14段全部FAILED，无成功段，读者珠子总字数为0。** 失败为链路侧 `headless_native_result_rejected / pre_submit` 秒拒（含已知成功调用的重放探针），与STEP4内容无关。

## 文件清单（out/）
- BEADS_FOR_USER.md —— 读者珠子（14段如实空缺）
- BEAD_SOURCE_LEDGER.md —— 每段输入构成＋失败证据＋保留/舍弃说明（无回包可登记）
- RUN_CALLS_AND_FILES.md —— 已追加STEP4 14段记录
- STEP4_inputs/ —— 14段长正文（STEP4_prompt_*.txt）、14段短正文（STEP4_short_*.txt）、14段Pool附件（ATTACH_*_Apool.txt）、STEP4_manifest.json、各段stdout/stderr/timing、两份探针记录
- scripts_tmp/build_step4.py、build_short_s01.py、build_short_all.py、split_src.py —— 输入组装脚本（供链路恢复后重投复用）
