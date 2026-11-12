# 先看说明（STEP2 失败交付，请先读本文件）

- 作品：Chopin Barcarolle in F-sharp major, Op.60（肖邦《船歌》升F大调 Op.60）。
- 本轮性质：失败交付。STEP1 成功、STEP2 链路拒收，无珠子生成、无小节切点产出（绝不编造切点）。

## STEP1 通、STEP2 链路拒收

1. STEP1 成功：7 独立来源（Rink / 朝山奈津子 PTNA / Gerling / Damschroder / Kopp / Aziz / Chaffin 等）、73 条范围记录，insufficient_evidence=false（见 STRUCTURE_SOURCE_EXTRACTS.md、STEP1_check.md）。
2. STEP2 失败：累计 9 轮内容投递 + 4 中性梯度探针。中性载荷 17KB 可过；凡含 STEP1 来源正文者无论大小格式全灭，错误恒为 headless_native_result_rejected / phase=pre_submit（详情见 STEP2_check.md）。
3. 停机：READY_FOR_POOL=false，不得进 STEP3/STEP4；A_POOL 未构建（NOT_BUILT）。

## 目录 9 文件导读

1. README_FIRST.md（本文件）：先看说明与恢复条件。
2. STRUCTURE_SOURCE_EXTRACTS.md：STEP1_response_raw.md 的 7 来源真实内容（S1S2 各 14 行逐小节表照录，不编造）。
3. STRUCTURE_LEVELS_AND_CHOICE.md：层级对照、采用决定（READY_FOR_POOL=false）、用户待选事项。
4. structure.json：机器可读结构（7 来源，insufficient_evidence=false，ready_for_pool=false，frozen_segments=null）。
5. A_POOL_MAP.json：Pool 未构建（NOT_BUILT，segments=[]）。
6. A_POOL_REVIEW.md：Pool 未构建原因与 11 件短名单待用说明。
7. BEADS_FOR_USER.md：本轮零珠子生成声明。
8. BEAD_SOURCE_LEDGER.md：空账本。
9. RUN_CALLS_AND_FILES.md：全部调用与文件记录（含 STEP1 成功、STEP2 全部调用、FINAL_HASHES）。

## 恢复条件

- 待 GPT-6w 链路不再拒收来源正文后，用已冻结 STEP1 内容重投 STEP2；READY_FOR_POOL=true 且冻结后，方可执行 STEP3/STEP4。
- 在此之前：绝不向下游（归段、珠子生成）推进；绝不把自合并五段 / 历史九段冒充文献结论；绝不编造切点。
