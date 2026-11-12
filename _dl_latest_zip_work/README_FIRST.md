# Music Pipeline：GPT-6w / GPT-5.6w 独立重复、稳定性与饱和测试 v2

**这是对 2026-10-09 冻结能力基线包的执行协议升级，不是重新设计问题。原 A/B/C 共 32 份模型提示词及原始素材保留逐字不变。**

## 用户要验证什么

1. 单次判断是否只是随机波动？同一模型同一题目独立重复，统计判词及论证是否稳定。
2. 如果允许同一模型多试几次，会不会发现之前漏掉的、有音乐材料依据的独立理解？尤其 C/E7 的多次内容选择是否饱和。
3. GPT-6w 与 GPT-5.6w 的差异，是模型本身，还是案例选择、顺序或评审模型造成的？

## 一句话流程

`校验冻结文件 → 可选导入已成功 pilot → r01–r05（16组×2模型×5次=160次） → 机械统计 → 生成跨模型/旧版盲评与 C 的语义饱和评审 → r06–r08 有针对性补样（必要时到 r12）→ 中文证据报告 → STOP`。

已有 pilot 的 A01、B02 两模型各一轮，可以先核验身份/提示词 SHA 再记为 r01；C02 的两次 pre-submit 失败不能算有效样本。不能仅凭这四次调用判断模型强弱。

## 本地 T3 主控与模型分工

- **T3 主控**仅负责启动、分配、检查汇总，不承担音乐文本的深度推理，不长时间消费 Opus。
- **Muse**负责 Python/CLI、输出校验、重复调用、统计、制作盲评、报告装包。T3 里调用：`delegate_task`；`providerInstanceId=claude-proxy`；`model=muse-spark-1.3-contributor-free`；`options.effort=xhigh`；每轮独立 review 新 `clientRequestId`，不靠 `childThreadId` 续聊；禁用名为 `muse` 的 provider。
- **音乐内容模型和评审**只通过 `gpt2 ask --file ... --model gpt-6-thinking|gpt-5-6-thinking --json`。不用 Opus、Sonnet、Sol、Luna，不用旧 `mg`，不静默回退。
- 假定 Muse / 两个网页 GPT 无边际调用成本；但要注意实际执行耗时、初始化内存和反复浏览器重试风险。默认**一个 gpt2 初始化任务在运行**，两模型交错执行。

## 入口

从解压目录运行：

```powershell
python scripts/verify_bundle.py
python scripts/verify_repeat_plan.py
# 可选：核验并导入 4 次成功的 pilot（不导入失败）
python scripts/import_pilot.py --pilot-root "D:\musicclaude\_chatgpt_music_pilot"
# 默认仅预览；必须显式 --execute 才会发送模型请求
python scripts/run_repeated_trials.py --round-start 1 --round-end 5
python scripts/run_repeated_trials.py --round-start 1 --round-end 5 --execute
python scripts/analyze_repeats.py
python scripts/build_repeat_judges.py
```

随后让 T3/Muse 执行 `jobs/reviews/review_manifest.json` 的 D（匿名旧稿对比）、G（6w/5.6w 直接对比）、F（语义饱和）审查；审查文件同样使用 `gpt2 --file`，不能编辑冻结模版。`scripts/run_repeated_trials.py --phase review --execute` 可以机械运行上述评审。

报告汇总在 `reports/`，完整响应在 `results/trials/` / `results/reviews/`，每次都带独立元数据。不应以汇总分数代替原文分析。

## 绝对不能混淆

- **重复次数 ≠ 独立题目数**：A 的 36 个案例才是跨题比较单位，B/C 各五个音乐站点；五次重复只是题内稳定性证据。
- **C 的不同文字 ≠ 新的语义**：需要独立做语义判重与价值评审，不能靠词频/重复句/来源 ID 简单宣布饱和。
- **旧裁决 ≠ 真值**：24 个历史 E5 判词只是校准参考，不称准确率。
- **B 是审阅固定候选，不是生成全新 Thread**：主要测审查稳定性，不应以它推断音乐创意饱和。
- **评审者偏差**：G 的正反顺序让两个 GPT 都评，可能会间接评到自己的匿名稿；不得把这种自评作为独立证据。D 继续仅由另一模型评，且两个模型的 D 胜率不能直接当同标尺比较。
- **失败不等于沉默**：提交前/状态不明的 CLI 故障不能当作 E7 选择 SILENCE。

详见 `EXECUTE_IN_T3.md`、`docs/04_REPEATABILITY_AND_SATURATION.md`。一次实验结束后停止，主控回到用户/ChatGPT，不自动启动提示词演化或生产切换。
