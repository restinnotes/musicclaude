# A_POOL 未构建说明（STEP2 失败交付最终版）

## 为何未构建

- STEP1 成功但 STEP2 失败（READY_FOR_POOL=false，见 STEP2_check.md），按 prompt 03 不得归段，故 A_POOL_MAP.json 状态为 NOT_BUILT，segments 为空。

## 11 件短名单的由来（复用既有产物，未重算、未读内容）

- 全量清单：out/STEP3_inputs/A_manifest_all.json，共 62 件。
- 形式筛选剔除：4 空文件（0 字节）/ 2 截断件 / 5 重复拷贝（冗余包内与既有文件同 sha）/ 8 审计重复（同 sha）。
- 其余按内容去重与版本优先（v1 / v2 / v1f）收敛为 11 件，见 out/STEP3_inputs/A_frozen_shortlist.json（形式短名单，未读内容，不作内容依据）。
- 短名单中含 1 件基线锚点（A_orig_V2A，gflash_web）：仅作盲比锚，不作采用依据。
- 短名单待用：待 STEP2 重投成功并冻结后，再按 prompt 03 执行归段；本轮不推进。

## STEP3 待办（链路恢复后执行）

- 待 GPT-6w 链路不再拒收来源正文，STEP2 重投成功且 READY_FOR_POOL=true 后，再执行归段。
