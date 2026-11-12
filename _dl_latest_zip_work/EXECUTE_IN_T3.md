# T3 本地主控专用：固定提示词 + 重复采样 + 盲评 + 饱和分析

本任务仅执行一次 GPT-6w / GPT-5.6w 能力基线，不接受长期自主研究授权；停止后将 ZIP 交还用户/ChatGPT 决定下一轮。**不用 Opus、Sonnet、Sol、Luna。T3 主线程尽量不进行文本研究，执行都交给 Muse。**

## Muse 子智能体

T3 内使用 `delegate_task`，指定 `providerInstanceId='claude-proxy'`、`model='muse-spark-1.3-contributor-free'`、`options.effort='xhigh'`。独立 review 使用新 `clientRequestId`，不通过 `childThreadId` 续聊。不要调用禁用的 `muse` provider。相关工作可并行委派多个 Muse，但外部 `gpt2` 浏览器初始化默认串行，防止本机内存/锁冲突。

## 任务边界与顺序

1. 解压包到项目内独立文件夹，不覆盖旧 prompts/runs。读取 `README_FIRST.md`、`jobs/repetition_plan.json`、`docs/04_REPEATABILITY_AND_SATURATION.md`；先运行 `scripts/verify_bundle.py` 和 `scripts/verify_repeat_plan.py`。
2. 检查 `gpt2 --help`、`gpt2 ask --help`；只用 `gpt2 ask --file PATH --model gpt-6-thinking|gpt-5-6-thinking --json`，不经 `claude-proxy` 调用网页 GPT；不猜测模型ID、档位，也不对无法证明已成功的调用伪造完成。
3. **可选优先**导入历史试跑 `D:\musicclaude\_chatgpt_music_pilot`：必须核对 job/模型/入参 SHA /原始 `completed=true`、真实路由与输出，再接到 r01。仅 A01/B02 四条成功可导入；C02 失败不要导入。`python scripts/import_pilot.py --pilot-root "D:\musicclaude\_chatgpt_music_pilot"`。
4. 调用冻结 A/B/C：同一 job、不同模型、不同重复号均发送同一份真实 prompt 的**相同字节**。每次单独 `gpt2 ask` 创建新会话，不允许 `resume`，禁止带先前答复。执行 r01–r05，两个模型交错，按 `jobs/manifest.json` 冻结顺序/每轮翻转方向。可按 A/B/C 并行准备数据，但 `gpt2` 初始化同时只开一个；参考命令：`python scripts/run_repeated_trials.py --round-start 1 --round-end 5 --execute`。默认非 --execute 仅列计划。
5. 每次保存 `results/trials/<model>/<job>/rXX.txt`、`rXX.meta.json`、`rXX.raw.json`、`rXX.stderr.txt`。校验 `completed`、命令退出码、`metadata.model`、`thinking_effort=max`（若缺记录未验证）、提示词 SHA、response hash、是否完整。失败区分 confirmed pre-submit、ambiguous / post-submit；**禁止自动重试**。失败时不要写成功 `.txt`；默认不重试。只有确认**确实是提交前失败**、已人工检查本地证据，才能指定某一个 job/轮次使用 `--retry-confirmed-pre-submit --only-job C02 --round-start 1 --round-end 1 --execute`，脚本会先把旧失败日志归档为 `attemptNN`，且绝不会对 ambiguous/post-submit 请求重试。
6. 跑 `python scripts/analyze_repeats.py`。输出 A 每案例同模型五轮类别分布、与旧标签一致数；B 每条历史假说五轮 verdict 分布；C 每站五轮操作与使用 source ID 分布、非结构化语义风险队列。这些都是机械统计，不代表质量真值。
7. 跑 `python scripts/build_repeat_judges.py` 生成 **预先指定的** r01、r05 （扩展至 r08/r12 后再补）评审。只在生成后读取 `private/`。 D：旧 run124 vs 某一稿，由**另一**模型评，A/B 顺序互换；G：6w vs 5.6w 同站同重复，两个模型各评、顺序互换；F：每模型每站的多次 E7 稿，另一模型做语义去重、价值与边际增益审查。新评审 prompt 来自冻结 D/F/G 模板加真实数据，不许现场改标准。
8. 运行 `python scripts/run_repeated_trials.py --phase review --execute`；然后 `python scripts/analyze_repeats.py` 汇总。冲突需按原文抽样复核，不能直接多数投票；自评与评审者身份应独立报告。
9. 根据预设规则决定是否继续 r06–r08：任一模型判断翻转影响决策、两个模型持续分歧、C r04/r05 出现新的**有价值**且源文本支持的独立语义单元、D/G 评审受顺序/模型身份明显影响、模型路由/输出疑似异常。**扩样对同一 job 的两个模型同时进行，不只给看上去较差的一方加次数。** 到 r08 后仍不稳定或新增高价值项，则对有关 job 双模型扩到 r12；仍未饱和要明确标 UNSATURATED，而不是假装验证完。
10. 结束后交付 ZIP（原始 prompt、试次响应/metadata、评审、统计、5个站点的典型分歧），简短中文报告分清：稳定性、跨题泛化、语义饱和、生成 vs 审查、历史旧裁决局限。不要声称在五站上证明全曲泛化。

## 首轮验收门槛

- 16 个任务 × 2 个模型 × 5 次独立调用有**有效输出或明确失败原因**；不能将失败当模型弱，更不能因为失败被空输出视为高质量沉默。
- 所有可比较的 paired 调用其 job prompt SHA 完全一致、真实模型路由/effort 与新会话身份有记录；旧 pilot 严格核对后方可作为 r01。
- 在每个 C 站点比较重复内容时，必须**人工/研究模型语义级**去重（不是词频统计）；比较单次随机输出与相同采样次数下的选择最佳稿，不把 r05 事后挑出的最佳稿当正常单次性能。
- D/G/ F 评审覆盖有数据的站点；不存在时如实报告，不能给空白打分。配对结果既要逐案也要提供跨站趋势及分歧样本。
- 所有历史输出、不变的提示词和生产配置保留；**本轮不演化提示词、不扩展 Op.52/Op.61、不自动切换生产模型、不让 T3 主线程调用 Opus 做持续 orchestration**。

如工程阻塞，优先解决真正阻塞具体任务的最小问题，不重新开始 run137–148 的完整性框架循环。到不确定是否提交外部服务时停下来保留诊断，不越权重试。
