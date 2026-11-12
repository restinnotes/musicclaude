# A_POOL_REVIEW v3（复核说明与去向台账）

审阅输出：`step3_review_raw_A.json` + `step3_review_raw_B.json` + `step3_review_raw_C.json`（分片 A/B/C，判定集互不重叠）；机械映射：`A_POOL_MAP_v3_prejson.json`。审阅只做语义判定与长跨度归类；机械 PRIMARY/普通 CROSS 未复判定，以逐字范围为准。

## 判定统计
| 槽位 | 说明 | 条数 |
|---|---|---|
| PRIMARY | 完全落在一段 | 126 |
| CROSS | 跨段连续叙述（每段各留一条，全文重复出现） | 217 |
| GLOBAL | 整曲全局底色（进每段附件第五部分，不进读者正文） | 55 |
| UNCERTAIN | 无法确定（仅内部台账） | 0 |
| DROP | 从 Pool 剔除 | 5 |
| UNRESOLVED | 机械与复核后仍无位置（需人工查看） | 0 |
| **合计（=单元数）** | | **403** |

覆盖核查：全部 403 个单元各占一个最终槽位（断言通过）。放置问题条数：0。

## 审阅者备注（原样）

分片A：共判定44条。muse-int-2-U01与muse-int-3-U01均以错误的138小节版本为编号前提，且独立内容价值有限，DROP。gpt6w-int-1-U12、gpt6w-int-3-U10虽含多组明确小节范围，但整体是跨全曲的心理历程概述，不宜强行转换成单一RANGE，判GLOBAL。部分GLOBAL单元含未经核实的传记细节、引语及强烈主观诠释；归段判定不代表事实背书。

分片B：NR中的资料清单具有全曲研究依据与解释边界的价值，归GLOBAL；U19虽提及103–110小节，主体仍是整曲回顾。OOB两条muse材料均描述了第116小节之后不存在的音乐进程，无法可靠截取；luna材料可保留111–116的终结段。C中gpt6w-web-3-U07仅有概括性标题，无独立分析内容。D仅提供截断头行，未发现足以确认的正文范围矛盾或全曲误归段情形，故不标旗。

分片C：五个单元均以全曲心理轨迹、情感矛盾或诠释框架为主要对象。U16虽提及m.84、m.103，但核心是主题再现与聆听记忆的跨段关系，不宜单段归属。U22虽列出多组明确小节范围，并重点提示78–83、107–110及116小节，但其主体是全曲情感历程的综合概括，不能据此收窄为一个连续范围。均保留为GLOBAL，不改动原文。

## 重定向单元（机械初判 → 复核后最终）

- SRC-gflash-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-int-1-U22：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-int-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-int-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-1-U11：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-2-U08：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gflash-web-3-U04：复核判定 `OK_CROSS` → **CROSS** S06,S07,S08,S09,S10
- SRC-gflash-web-3-U08：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-int-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-int-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-web-1-U04：复核判定 `OK_CROSS` → **CROSS** S05,S06,S07,S08,S09
- SRC-gpro-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpro-web-2-U03：复核判定 `OK_CROSS` → **CROSS** S04,S05,S06,S07,S08,S09
- SRC-gpro-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-int-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-int-2-U13：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-int-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-int-3-U13：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-web-2-U16：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt56w-web-2-U17：复核判定 `SPLIT_AS_GLOBAL` → **GLOBAL**
- SRC-gpt56w-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-1-U12：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-1-U13：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-2-U10：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-int-3-U10：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-1-U22：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-1-U23：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-2-U15：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-2-U16：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-3-U07：复核判定 `DROP` → **DROP**
- SRC-gpt6w-web-3-U18：复核判定 `GLOBAL` → **GLOBAL**
- SRC-gpt6w-web-3-U19：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-int-1-U07：复核判定 `RANGE:mm.111-116` → **PRIMARY** S14 （复核范围 [111, 116]）
- SRC-luna-int-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-int-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-1-U12：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-2-U13：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-luna-web-3-U14：复核判定 `GLOBAL` → **GLOBAL**
- SRC-muse-int-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-muse-int-2-U01：复核判定 `DROP` → **DROP**
- SRC-muse-int-2-U11：复核判定 `DROP` → **DROP**
- SRC-muse-int-3-U01：复核判定 `DROP` → **DROP**
- SRC-muse-int-3-U09：复核判定 `DROP` → **DROP**
- SRC-muse-web-1-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-muse-web-2-U01：复核判定 `GLOBAL` → **GLOBAL**
- SRC-muse-web-3-U01：复核判定 `GLOBAL` → **GLOBAL**

## 去向台账（全单元，36 份来源全部列出）

### SRC-gflash-int-1
- SRC-gflash-int-1-U01 — → **GLOBAL**
- SRC-gflash-int-1-U02 1-15 → **CROSS** S01,S02
- SRC-gflash-int-1-U03 1-4 → **CROSS** S01,S02
- SRC-gflash-int-1-U04 5-15 → **PRIMARY** S02
- SRC-gflash-int-1-U05 16-39 → **CROSS** S02,S03,S04,S05
- SRC-gflash-int-1-U06 16-23 → **CROSS** S02,S03
- SRC-gflash-int-1-U07 24-34 → **PRIMARY** S04
- SRC-gflash-int-1-U08 35-39 → **PRIMARY** S05
- SRC-gflash-int-1-U09 40-61 → **CROSS** S06,S07
- SRC-gflash-int-1-U10 40-50 → **PRIMARY** S06
- SRC-gflash-int-1-U11 51-61 → **PRIMARY** S07
- SRC-gflash-int-1-U12 62-83 → **CROSS** S08,S09,S10
- SRC-gflash-int-1-U13 62-75 → **CROSS** S08,S09
- SRC-gflash-int-1-U14 76-83 → **CROSS** S09,S10
- SRC-gflash-int-1-U15 84-102 → **CROSS** S11,S12
- SRC-gflash-int-1-U16 84-92 → **PRIMARY** S11
- SRC-gflash-int-1-U17 93-102 → **PRIMARY** S12
- SRC-gflash-int-1-U18 103-116 → **CROSS** S13,S14
- SRC-gflash-int-1-U19 103-110 → **PRIMARY** S13
- SRC-gflash-int-1-U20 111-113 → **PRIMARY** S14
- SRC-gflash-int-1-U21 114-116 → **PRIMARY** S14
- SRC-gflash-int-1-U22 — → **GLOBAL**
### SRC-gflash-int-2
- SRC-gflash-int-2-U01 — → **GLOBAL**
- SRC-gflash-int-2-U02 1-3 → **PRIMARY** S01
- SRC-gflash-int-2-U03 4-39 → **CROSS** S02,S03,S04,S05
- SRC-gflash-int-2-U04 40-61 → **CROSS** S06,S07
- SRC-gflash-int-2-U05 62-83 → **CROSS** S08,S09,S10
- SRC-gflash-int-2-U06 62-62 → **PRIMARY** S08
- SRC-gflash-int-2-U07 84-102 → **CROSS** S11,S12
- SRC-gflash-int-2-U08 103-116 → **CROSS** S13,S14
### SRC-gflash-int-3
- SRC-gflash-int-3-U01 — → **GLOBAL**
- SRC-gflash-int-3-U03 1-5 → **CROSS** S01,S02
- SRC-gflash-int-3-U05 6-39 → **CROSS** S02,S03,S04,S05
- SRC-gflash-int-3-U07 40-61 51-61 → **CROSS** S06,S07
- SRC-gflash-int-3-U09 62-83 → **CROSS** S08,S09,S10
- SRC-gflash-int-3-U11 84-92 → **PRIMARY** S11
- SRC-gflash-int-3-U13 93-116 → **CROSS** S12,S13,S14
### SRC-gpro-int-1
- SRC-gpro-int-1-U01 — → **GLOBAL**
- SRC-gpro-int-1-U02 1-5 → **CROSS** S01,S02
- SRC-gpro-int-1-U03 6-34 → **CROSS** S02,S03,S04
- SRC-gpro-int-1-U04 35-61 → **CROSS** S05,S06,S07
- SRC-gpro-int-1-U05 62-77 → **CROSS** S08,S09
- SRC-gpro-int-1-U06 78-103 → **CROSS** S10,S11,S12,S13
- SRC-gpro-int-1-U07 104-116 → **CROSS** S13,S14
### SRC-gpro-int-2
- SRC-gpro-int-2-U01 — → **GLOBAL**
- SRC-gpro-int-2-U02 1-32 → **CROSS** S01,S02,S03,S04
- SRC-gpro-int-2-U03 1-3 → **PRIMARY** S01
- SRC-gpro-int-2-U04 4-32 → **CROSS** S02,S03,S04
- SRC-gpro-int-2-U05 33-61 → **CROSS** S04,S05,S06,S07
- SRC-gpro-int-2-U06 33-61 → **CROSS** S04,S05,S06,S07
- SRC-gpro-int-2-U07 62-77 → **CROSS** S08,S09
- SRC-gpro-int-2-U08 62-77 → **CROSS** S08,S09
- SRC-gpro-int-2-U09 78-92 → **CROSS** S10,S11
- SRC-gpro-int-2-U10 78-92 → **CROSS** S10,S11
- SRC-gpro-int-2-U11 93-103 → **CROSS** S12,S13
- SRC-gpro-int-2-U12 93-103 → **CROSS** S12,S13
- SRC-gpro-int-2-U13 104-116 → **CROSS** S13,S14
- SRC-gpro-int-2-U14 104-113 → **CROSS** S13,S14
- SRC-gpro-int-2-U15 114-116 → **PRIMARY** S14
### SRC-gpro-int-3
- SRC-gpro-int-3-U01 — → **GLOBAL**
- SRC-gpro-int-3-U02 1-3 → **PRIMARY** S01
- SRC-gpro-int-3-U03 4-34 → **CROSS** S02,S03,S04
- SRC-gpro-int-3-U04 35-61 → **CROSS** S05,S06,S07
- SRC-gpro-int-3-U05 62-83 → **CROSS** S08,S09,S10
- SRC-gpro-int-3-U06 84-103 → **CROSS** S11,S12,S13
- SRC-gpro-int-3-U07 104-116 → **CROSS** S13,S14
### SRC-muse-int-1
- SRC-muse-int-1-U01 — → **GLOBAL**
- SRC-muse-int-1-U02 1-4 → **CROSS** S01,S02
- SRC-muse-int-1-U03 5-26 → **CROSS** S02,S03,S04
- SRC-muse-int-1-U04 27-43 → **CROSS** S04,S05,S06
- SRC-muse-int-1-U05 44-61 → **CROSS** S06,S07
- SRC-muse-int-1-U06 62-77 → **CROSS** S08,S09
- SRC-muse-int-1-U07 78-92 → **CROSS** S10,S11
- SRC-muse-int-1-U08 93-102 → **PRIMARY** S12
- SRC-muse-int-1-U09 103-116 → **CROSS** S13,S14
### SRC-muse-int-2
- SRC-muse-int-2-U01 — → **DROP**
- SRC-muse-int-2-U02 1-4 → **CROSS** S01,S02
- SRC-muse-int-2-U03 5-22 → **CROSS** S02,S03
- SRC-muse-int-2-U04 23-32 → **CROSS** S03,S04
- SRC-muse-int-2-U05 33-46 → **CROSS** S04,S05,S06
- SRC-muse-int-2-U06 47-61 → **CROSS** S06,S07
- SRC-muse-int-2-U07 62-77 → **CROSS** S08,S09
- SRC-muse-int-2-U08 78-84 → **CROSS** S10,S11
- SRC-muse-int-2-U09 85-102 → **CROSS** S11,S12
- SRC-muse-int-2-U10 103-113 → **CROSS** S13,S14
- SRC-muse-int-2-U11 114-138 → **DROP**
### SRC-muse-int-3
- SRC-muse-int-3-U01 — → **DROP**
- SRC-muse-int-3-U02 1-4 → **CROSS** S01,S02
- SRC-muse-int-3-U03 5-32 → **CROSS** S02,S03,S04
- SRC-muse-int-3-U04 33-61 → **CROSS** S04,S05,S06,S07
- SRC-muse-int-3-U05 62-77 → **CROSS** S08,S09
- SRC-muse-int-3-U06 78-92 → **CROSS** S10,S11
- SRC-muse-int-3-U07 93-102 → **PRIMARY** S12
- SRC-muse-int-3-U08 103-113 → **CROSS** S13,S14
- SRC-muse-int-3-U09 114-138 → **DROP**
### SRC-luna-int-1
- SRC-luna-int-1-U01 — → **GLOBAL**
- SRC-luna-int-1-U02 1-20 → **CROSS** S01,S02,S03
- SRC-luna-int-1-U03 21-40 → **CROSS** S03,S04,S05,S06
- SRC-luna-int-1-U04 41-64 → **CROSS** S06,S07,S08
- SRC-luna-int-1-U05 65-88 → **CROSS** S08,S09,S10,S11
- SRC-luna-int-1-U06 89-110 → **CROSS** S11,S12,S13
- SRC-luna-int-1-U07 111-143 → **PRIMARY** S14 （复核范围 [111, 116]）
### SRC-luna-int-2
- SRC-luna-int-2-U01 — → **GLOBAL**
- SRC-luna-int-2-U02 1-16 → **CROSS** S01,S02
- SRC-luna-int-2-U03 17-36 → **CROSS** S03,S04,S05
- SRC-luna-int-2-U04 37-56 → **CROSS** S05,S06,S07
- SRC-luna-int-2-U05 57-66 → **CROSS** S07,S08
- SRC-luna-int-2-U06 67-88 → **CROSS** S08,S09,S10,S11
- SRC-luna-int-2-U07 89-112 → **CROSS** S11,S12,S13,S14
### SRC-luna-int-3
- SRC-luna-int-3-U01 — → **GLOBAL**
- SRC-luna-int-3-U02 1-3 → **PRIMARY** S01
- SRC-luna-int-3-U03 4-11 → **PRIMARY** S02
- SRC-luna-int-3-U04 12-34 → **CROSS** S02,S03,S04
- SRC-luna-int-3-U05 35-39 35-40 → **CROSS** S05,S06
- SRC-luna-int-3-U06 40-61 → **CROSS** S06,S07
- SRC-luna-int-3-U07 62-70 → **PRIMARY** S08
- SRC-luna-int-3-U08 71-77 78-83 → **CROSS** S08,S09,S10
- SRC-luna-int-3-U09 84-102 100-103 → **CROSS** S11,S12,S13
- SRC-luna-int-3-U10 103-116 110-111 113-116 → **CROSS** S13,S14
### SRC-gpt56w-int-1
- SRC-gpt56w-int-1-U01 — → **GLOBAL**
- SRC-gpt56w-int-1-U02 1-4 → **CROSS** S01,S02
- SRC-gpt56w-int-1-U03 5-20 → **CROSS** S02,S03
- SRC-gpt56w-int-1-U04 21-38 → **CROSS** S03,S04,S05
- SRC-gpt56w-int-1-U05 39-56 → **CROSS** S05,S06,S07
- SRC-gpt56w-int-1-U06 57-77 → **CROSS** S07,S08,S09
- SRC-gpt56w-int-1-U07 78-85 → **CROSS** S10,S11
- SRC-gpt56w-int-1-U08 86-92 → **PRIMARY** S11
- SRC-gpt56w-int-1-U09 93-104 → **CROSS** S12,S13
- SRC-gpt56w-int-1-U10 105-116 → **CROSS** S13,S14
- SRC-gpt56w-int-1-U11 1-20 → **CROSS** S01,S02,S03
### SRC-gpt56w-int-2
- SRC-gpt56w-int-2-U01 — → **GLOBAL**
- SRC-gpt56w-int-2-U02 1-3 → **PRIMARY** S01
- SRC-gpt56w-int-2-U03 4-19 → **CROSS** S02,S03
- SRC-gpt56w-int-2-U04 20-38 → **CROSS** S03,S04,S05
- SRC-gpt56w-int-2-U05 39-51 → **CROSS** S05,S06,S07
- SRC-gpt56w-int-2-U06 52-61 → **PRIMARY** S07
- SRC-gpt56w-int-2-U07 62-77 → **CROSS** S08,S09
- SRC-gpt56w-int-2-U08 78-83 → **PRIMARY** S10
- SRC-gpt56w-int-2-U09 84-93 → **CROSS** S11,S12
- SRC-gpt56w-int-2-U10 94-103 → **CROSS** S12,S13
- SRC-gpt56w-int-2-U11 104-110 → **PRIMARY** S13
- SRC-gpt56w-int-2-U12 111-116 → **PRIMARY** S14
- SRC-gpt56w-int-2-U13 — → **GLOBAL**
- SRC-gpt56w-int-2-U14 1-19 → **CROSS** S01,S02,S03
- SRC-gpt56w-int-2-U15 20-38 → **CROSS** S03,S04,S05
- SRC-gpt56w-int-2-U16 39-61 → **CROSS** S05,S06,S07
- SRC-gpt56w-int-2-U17 62-77 → **CROSS** S08,S09
- SRC-gpt56w-int-2-U18 78-83 → **PRIMARY** S10
- SRC-gpt56w-int-2-U19 84-103 → **CROSS** S11,S12,S13
- SRC-gpt56w-int-2-U20 104-110 → **PRIMARY** S13
- SRC-gpt56w-int-2-U21 111-116 → **PRIMARY** S14
### SRC-gpt56w-int-3
- SRC-gpt56w-int-3-U01 — → **GLOBAL**
- SRC-gpt56w-int-3-U02 1-4 → **CROSS** S01,S02
- SRC-gpt56w-int-3-U03 5-14 → **PRIMARY** S02
- SRC-gpt56w-int-3-U04 15-26 → **CROSS** S02,S03,S04
- SRC-gpt56w-int-3-U05 27-38 → **CROSS** S04,S05
- SRC-gpt56w-int-3-U06 39-51 → **CROSS** S05,S06,S07
- SRC-gpt56w-int-3-U07 52-69 → **CROSS** S07,S08
- SRC-gpt56w-int-3-U08 70-77 → **CROSS** S08,S09
- SRC-gpt56w-int-3-U09 78-93 → **CROSS** S10,S11,S12
- SRC-gpt56w-int-3-U10 94-103 → **CROSS** S12,S13
- SRC-gpt56w-int-3-U11 104-110 → **PRIMARY** S13
- SRC-gpt56w-int-3-U12 111-116 → **PRIMARY** S14
- SRC-gpt56w-int-3-U13 — → **GLOBAL**
### SRC-gpt6w-int-1
- SRC-gpt6w-int-1-U01 — → **GLOBAL**
- SRC-gpt6w-int-1-U03 1-3 → **PRIMARY** S01
- SRC-gpt6w-int-1-U04 4-21 → **CROSS** S02,S03
- SRC-gpt6w-int-1-U05 22-39 → **CROSS** S03,S04,S05
- SRC-gpt6w-int-1-U06 40-61 → **CROSS** S06,S07
- SRC-gpt6w-int-1-U07 62-77 → **CROSS** S08,S09
- SRC-gpt6w-int-1-U08 78-83 → **PRIMARY** S10
- SRC-gpt6w-int-1-U09 84-96 → **CROSS** S11,S12
- SRC-gpt6w-int-1-U10 97-107 → **CROSS** S12,S13
- SRC-gpt6w-int-1-U11 108-116 → **CROSS** S13,S14
- SRC-gpt6w-int-1-U12 — → **GLOBAL**
- SRC-gpt6w-int-1-U13 — → **GLOBAL**
### SRC-gpt6w-int-2
- SRC-gpt6w-int-2-U01 — → **GLOBAL**
- SRC-gpt6w-int-2-U02 1-6 → **CROSS** S01,S02
- SRC-gpt6w-int-2-U03 7-22 → **CROSS** S02,S03
- SRC-gpt6w-int-2-U04 23-39 → **CROSS** S03,S04,S05
- SRC-gpt6w-int-2-U05 40-61 → **CROSS** S06,S07
- SRC-gpt6w-int-2-U06 62-77 → **CROSS** S08,S09
- SRC-gpt6w-int-2-U07 78-92 → **CROSS** S10,S11
- SRC-gpt6w-int-2-U08 93-105 → **CROSS** S12,S13
- SRC-gpt6w-int-2-U09 106-116 → **CROSS** S13,S14
- SRC-gpt6w-int-2-U10 — → **GLOBAL**
### SRC-gpt6w-int-3
- SRC-gpt6w-int-3-U01 — → **GLOBAL**
- SRC-gpt6w-int-3-U02 1-3 → **PRIMARY** S01
- SRC-gpt6w-int-3-U03 4-16 → **PRIMARY** S02
- SRC-gpt6w-int-3-U04 17-32 → **CROSS** S03,S04
- SRC-gpt6w-int-3-U05 33-49 → **CROSS** S04,S05,S06
- SRC-gpt6w-int-3-U06 50-66 → **CROSS** S06,S07,S08
- SRC-gpt6w-int-3-U07 67-83 → **CROSS** S08,S09,S10
- SRC-gpt6w-int-3-U08 84-104 → **CROSS** S11,S12,S13
- SRC-gpt6w-int-3-U09 105-116 → **CROSS** S13,S14
- SRC-gpt6w-int-3-U10 — → **GLOBAL**
### SRC-gflash-web-1
- SRC-gflash-web-1-U01 — → **GLOBAL**
- SRC-gflash-web-1-U02 1-3 → **PRIMARY** S01
- SRC-gflash-web-1-U03 4-34 → **CROSS** S02,S03,S04
- SRC-gflash-web-1-U04 35-61 → **CROSS** S05,S06,S07
- SRC-gflash-web-1-U05 62-77 → **CROSS** S08,S09
- SRC-gflash-web-1-U06 78-83 → **PRIMARY** S10
- SRC-gflash-web-1-U07 84-102 → **CROSS** S11,S12
- SRC-gflash-web-1-U08 103-116 → **CROSS** S13,S14
- SRC-gflash-web-1-U09 103-111 → **CROSS** S13,S14
- SRC-gflash-web-1-U10 112-116 → **PRIMARY** S14
- SRC-gflash-web-1-U11 — → **GLOBAL**
### SRC-gflash-web-2
- SRC-gflash-web-2-U01 — → **GLOBAL**
- SRC-gflash-web-2-U02 1-3 → **PRIMARY** S01
- SRC-gflash-web-2-U03 4-39 → **CROSS** S02,S03,S04,S05
- SRC-gflash-web-2-U04 40-61 → **CROSS** S06,S07
- SRC-gflash-web-2-U05 62-83 → **CROSS** S08,S09,S10
- SRC-gflash-web-2-U06 84-102 → **CROSS** S11,S12
- SRC-gflash-web-2-U07 103-116 → **CROSS** S13,S14
- SRC-gflash-web-2-U08 — → **GLOBAL**
### SRC-gflash-web-3
- SRC-gflash-web-3-U01 — → **GLOBAL**
- SRC-gflash-web-3-U02 1-5 → **CROSS** S01,S02
- SRC-gflash-web-3-U03 6-39 → **CROSS** S02,S03,S04,S05
- SRC-gflash-web-3-U04 40-83 → **CROSS** S06,S07,S08,S09,S10
- SRC-gflash-web-3-U05 78-83 → **PRIMARY** S10
- SRC-gflash-web-3-U06 84-102 → **CROSS** S11,S12
- SRC-gflash-web-3-U07 103-116 → **CROSS** S13,S14
- SRC-gflash-web-3-U08 — → **GLOBAL**
### SRC-gpro-web-1
- SRC-gpro-web-1-U01 — → **GLOBAL**
- SRC-gpro-web-1-U02 1-3 → **PRIMARY** S01
- SRC-gpro-web-1-U03 4-34 → **CROSS** S02,S03,S04
- SRC-gpro-web-1-U04 35-77 → **CROSS** S05,S06,S07,S08,S09
- SRC-gpro-web-1-U05 78-83 → **PRIMARY** S10
- SRC-gpro-web-1-U06 84-103 → **CROSS** S11,S12,S13
- SRC-gpro-web-1-U07 104-116 → **CROSS** S13,S14
### SRC-gpro-web-2
- SRC-gpro-web-2-U01 — → **GLOBAL**
- SRC-gpro-web-2-U02 1-33 → **CROSS** S01,S02,S03,S04
- SRC-gpro-web-2-U03 34-77 → **CROSS** S04,S05,S06,S07,S08,S09
- SRC-gpro-web-2-U04 78-83 → **PRIMARY** S10
- SRC-gpro-web-2-U05 84-102 → **CROSS** S11,S12
- SRC-gpro-web-2-U06 103-103 → **PRIMARY** S13
### SRC-gpro-web-3
- SRC-gpro-web-3-U01 — → **GLOBAL**
- SRC-gpro-web-3-U02 1-3 → **PRIMARY** S01
- SRC-gpro-web-3-U03 4-38 → **CROSS** S02,S03,S04,S05
- SRC-gpro-web-3-U04 39-77 → **CROSS** S05,S06,S07,S08,S09
- SRC-gpro-web-3-U05 78-83 → **PRIMARY** S10
- SRC-gpro-web-3-U06 84-103 → **CROSS** S11,S12,S13
- SRC-gpro-web-3-U07 104-104 → **PRIMARY** S13
### SRC-muse-web-1
- SRC-muse-web-1-U01 — → **GLOBAL**
- SRC-muse-web-1-U02 1-3 → **PRIMARY** S01
- SRC-muse-web-1-U03 4-34 → **CROSS** S02,S03,S04
- SRC-muse-web-1-U04 35-61 → **CROSS** S05,S06,S07
- SRC-muse-web-1-U05 62-77 → **CROSS** S08,S09
- SRC-muse-web-1-U06 78-83 → **PRIMARY** S10
- SRC-muse-web-1-U07 84-102 → **CROSS** S11,S12
- SRC-muse-web-1-U08 103-116 → **CROSS** S13,S14
### SRC-muse-web-2
- SRC-muse-web-2-U01 — → **GLOBAL**
- SRC-muse-web-2-U02 1-3 → **PRIMARY** S01
- SRC-muse-web-2-U03 4-34 → **CROSS** S02,S03,S04
- SRC-muse-web-2-U04 35-61 → **CROSS** S05,S06,S07
- SRC-muse-web-2-U05 62-77 → **CROSS** S08,S09
- SRC-muse-web-2-U06 78-83 → **PRIMARY** S10
- SRC-muse-web-2-U07 84-102 → **CROSS** S11,S12
- SRC-muse-web-2-U08 103-110 → **PRIMARY** S13
- SRC-muse-web-2-U09 111-116 → **PRIMARY** S14
### SRC-muse-web-3
- SRC-muse-web-3-U01 — → **GLOBAL**
- SRC-muse-web-3-U02 1-4 → **CROSS** S01,S02
- SRC-muse-web-3-U03 5-34 → **CROSS** S02,S03,S04
- SRC-muse-web-3-U04 35-61 → **CROSS** S05,S06,S07
- SRC-muse-web-3-U05 62-70 → **PRIMARY** S08
- SRC-muse-web-3-U06 71-83 → **CROSS** S08,S09,S10
- SRC-muse-web-3-U07 84-102 → **CROSS** S11,S12
- SRC-muse-web-3-U08 103-110 → **PRIMARY** S13
- SRC-muse-web-3-U09 111-116 → **PRIMARY** S14
### SRC-luna-web-1
- SRC-luna-web-1-U01 — → **GLOBAL**
- SRC-luna-web-1-U03 1-3 → **PRIMARY** S01
- SRC-luna-web-1-U04 4-16 6-6 12-16 → **PRIMARY** S02
- SRC-luna-web-1-U05 17-34 24-34 → **CROSS** S03,S04
- SRC-luna-web-1-U06 35-61 35-39 35-40 40-61 → **CROSS** S05,S06,S07
- SRC-luna-web-1-U07 62-70 62-77 70-70 71-77 → **CROSS** S08,S09
- SRC-luna-web-1-U08 78-83 → **PRIMARY** S10
- SRC-luna-web-1-U09 84-102 93-102 → **CROSS** S11,S12
- SRC-luna-web-1-U10 103-111 110-111 → **CROSS** S13,S14
- SRC-luna-web-1-U11 111-116 → **PRIMARY** S14
- SRC-luna-web-1-U12 — → **GLOBAL**
### SRC-luna-web-2
- SRC-luna-web-2-U01 — → **GLOBAL**
- SRC-luna-web-2-U03 1-3 → **PRIMARY** S01
- SRC-luna-web-2-U04 4-16 14-15 → **PRIMARY** S02
- SRC-luna-web-2-U05 17-34 → **CROSS** S03,S04
- SRC-luna-web-2-U06 35-39 35-40 → **CROSS** S05,S06
- SRC-luna-web-2-U07 40-61 → **CROSS** S06,S07
- SRC-luna-web-2-U08 62-71 62-77 72-77 → **CROSS** S08,S09
- SRC-luna-web-2-U09 78-83 → **PRIMARY** S10
- SRC-luna-web-2-U10 84-111 84-102 93-102 → **CROSS** S11,S12,S13,S14
- SRC-luna-web-2-U11 103-111 110-111 → **CROSS** S13,S14
- SRC-luna-web-2-U12 112-116 → **PRIMARY** S14
- SRC-luna-web-2-U13 — → **GLOBAL**
### SRC-luna-web-3
- SRC-luna-web-3-U01 — → **GLOBAL**
- SRC-luna-web-3-U03 1-3 → **PRIMARY** S01
- SRC-luna-web-3-U04 4-16 11-15 14-15 → **PRIMARY** S02
- SRC-luna-web-3-U05 17-34 → **CROSS** S03,S04
- SRC-luna-web-3-U06 35-61 35-39 40-40 → **CROSS** S05,S06,S07
- SRC-luna-web-3-U07 62-70 → **PRIMARY** S08
- SRC-luna-web-3-U08 71-77 → **CROSS** S08,S09
- SRC-luna-web-3-U09 78-83 → **PRIMARY** S10
- SRC-luna-web-3-U10 84-92 84-84 → **PRIMARY** S11
- SRC-luna-web-3-U11 93-102 → **PRIMARY** S12
- SRC-luna-web-3-U12 103-111 110-111 → **CROSS** S13,S14
- SRC-luna-web-3-U13 111-116 → **PRIMARY** S14
- SRC-luna-web-3-U14 — → **GLOBAL**
### SRC-gpt56w-web-1
- SRC-gpt56w-web-1-U01 — → **GLOBAL**
- SRC-gpt56w-web-1-U02 1-3 → **PRIMARY** S01
- SRC-gpt56w-web-1-U03 4-14 → **PRIMARY** S02
- SRC-gpt56w-web-1-U04 15-23 → **CROSS** S02,S03
- SRC-gpt56w-web-1-U05 24-34 → **PRIMARY** S04
- SRC-gpt56w-web-1-U06 35-39 → **PRIMARY** S05
- SRC-gpt56w-web-1-U07 39-50 → **CROSS** S05,S06
- SRC-gpt56w-web-1-U08 51-61 → **PRIMARY** S07
- SRC-gpt56w-web-1-U09 62-70 → **PRIMARY** S08
- SRC-gpt56w-web-1-U10 71-77 78-83 → **CROSS** S08,S09,S10
- SRC-gpt56w-web-1-U11 84-92 → **PRIMARY** S11
- SRC-gpt56w-web-1-U12 93-102 → **PRIMARY** S12
- SRC-gpt56w-web-1-U13 103-110 → **PRIMARY** S13
- SRC-gpt56w-web-1-U14 111-116 → **PRIMARY** S14
### SRC-gpt56w-web-2
- SRC-gpt56w-web-2-U01 — → **GLOBAL**
- SRC-gpt56w-web-2-U02 1-3 → **PRIMARY** S01
- SRC-gpt56w-web-2-U03 4-14 → **PRIMARY** S02
- SRC-gpt56w-web-2-U04 15-23 → **CROSS** S02,S03
- SRC-gpt56w-web-2-U05 24-39 → **CROSS** S04,S05
- SRC-gpt56w-web-2-U06 40-61 → **CROSS** S06,S07
- SRC-gpt56w-web-2-U07 62-70 → **PRIMARY** S08
- SRC-gpt56w-web-2-U08 62-70 → **PRIMARY** S08
- SRC-gpt56w-web-2-U09 71-77 78-83 → **CROSS** S08,S09,S10
- SRC-gpt56w-web-2-U10 71-77 → **CROSS** S08,S09
- SRC-gpt56w-web-2-U11 84-92 → **PRIMARY** S11
- SRC-gpt56w-web-2-U12 93-103 → **CROSS** S12,S13
- SRC-gpt56w-web-2-U13 93-102 → **PRIMARY** S12
- SRC-gpt56w-web-2-U14 103-111 → **CROSS** S13,S14
- SRC-gpt56w-web-2-U15 111-116 → **PRIMARY** S14
- SRC-gpt56w-web-2-U16 — → **GLOBAL**
- SRC-gpt56w-web-2-U17 1-3 4-23 24-39 40-61 62-70 71-83 84-103 103-111 111-116 → **GLOBAL**
### SRC-gpt56w-web-3
- SRC-gpt56w-web-3-U01 — → **GLOBAL**
- SRC-gpt56w-web-3-U03 1-3 → **PRIMARY** S01
- SRC-gpt56w-web-3-U04 4-16 → **PRIMARY** S02
- SRC-gpt56w-web-3-U05 17-35 → **CROSS** S03,S04,S05
- SRC-gpt56w-web-3-U06 35-61 → **CROSS** S05,S06,S07
- SRC-gpt56w-web-3-U07 62-70 → **PRIMARY** S08
- SRC-gpt56w-web-3-U08 71-83 78-83 → **CROSS** S08,S09,S10
- SRC-gpt56w-web-3-U09 84-92 → **PRIMARY** S11
- SRC-gpt56w-web-3-U10 93-101 → **PRIMARY** S12
- SRC-gpt56w-web-3-U11 103-111 → **CROSS** S13,S14
- SRC-gpt56w-web-3-U12 111-116 → **PRIMARY** S14
### SRC-gpt6w-web-1
- SRC-gpt6w-web-1-U01 — → **GLOBAL**
- SRC-gpt6w-web-1-U03 1-16 → **CROSS** S01,S02
- SRC-gpt6w-web-1-U04 1-3 → **PRIMARY** S01
- SRC-gpt6w-web-1-U05 4-16 → **PRIMARY** S02
- SRC-gpt6w-web-1-U06 17-39 → **CROSS** S03,S04,S05
- SRC-gpt6w-web-1-U07 17-34 → **CROSS** S03,S04
- SRC-gpt6w-web-1-U08 35-39 → **PRIMARY** S05
- SRC-gpt6w-web-1-U09 40-61 → **CROSS** S06,S07
- SRC-gpt6w-web-1-U10 40-61 → **CROSS** S06,S07
- SRC-gpt6w-web-1-U11 62-77 → **CROSS** S08,S09
- SRC-gpt6w-web-1-U12 62-71 → **PRIMARY** S08
- SRC-gpt6w-web-1-U13 72-77 → **PRIMARY** S09
- SRC-gpt6w-web-1-U14 78-92 → **CROSS** S10,S11
- SRC-gpt6w-web-1-U15 78-83 → **PRIMARY** S10
- SRC-gpt6w-web-1-U16 84-92 → **PRIMARY** S11
- SRC-gpt6w-web-1-U17 93-110 → **CROSS** S12,S13
- SRC-gpt6w-web-1-U18 93-102 → **PRIMARY** S12
- SRC-gpt6w-web-1-U19 103-110 → **PRIMARY** S13
- SRC-gpt6w-web-1-U20 103-106 107-110 → **PRIMARY** S13
- SRC-gpt6w-web-1-U21 111-116 → **PRIMARY** S14
- SRC-gpt6w-web-1-U22 — → **GLOBAL**
- SRC-gpt6w-web-1-U23 — → **GLOBAL**
### SRC-gpt6w-web-2
- SRC-gpt6w-web-2-U01 — → **GLOBAL**
- SRC-gpt6w-web-2-U03 1-3 → **PRIMARY** S01
- SRC-gpt6w-web-2-U04 4-11 → **PRIMARY** S02
- SRC-gpt6w-web-2-U05 12-23 → **CROSS** S02,S03
- SRC-gpt6w-web-2-U06 24-39 → **CROSS** S04,S05
- SRC-gpt6w-web-2-U07 40-61 → **CROSS** S06,S07
- SRC-gpt6w-web-2-U08 62-77 → **CROSS** S08,S09
- SRC-gpt6w-web-2-U09 62-70 → **PRIMARY** S08
- SRC-gpt6w-web-2-U10 78-83 → **PRIMARY** S10
- SRC-gpt6w-web-2-U11 84-92 → **PRIMARY** S11
- SRC-gpt6w-web-2-U12 93-102 → **PRIMARY** S12
- SRC-gpt6w-web-2-U13 103-111 → **CROSS** S13,S14
- SRC-gpt6w-web-2-U14 112-116 → **PRIMARY** S14
- SRC-gpt6w-web-2-U15 — → **GLOBAL**
- SRC-gpt6w-web-2-U16 — → **GLOBAL**
### SRC-gpt6w-web-3
- SRC-gpt6w-web-3-U01 — → **GLOBAL**
- SRC-gpt6w-web-3-U02 1-34 → **CROSS** S01,S02,S03,S04
- SRC-gpt6w-web-3-U03 1-3 → **PRIMARY** S01
- SRC-gpt6w-web-3-U04 4-16 → **PRIMARY** S02
- SRC-gpt6w-web-3-U05 17-23 → **PRIMARY** S03
- SRC-gpt6w-web-3-U06 24-34 → **PRIMARY** S04
- SRC-gpt6w-web-3-U07 35-83 → **DROP**
- SRC-gpt6w-web-3-U08 35-39 → **PRIMARY** S05
- SRC-gpt6w-web-3-U09 40-61 → **CROSS** S06,S07
- SRC-gpt6w-web-3-U10 62-70 → **PRIMARY** S08
- SRC-gpt6w-web-3-U11 71-77 → **CROSS** S08,S09
- SRC-gpt6w-web-3-U12 78-83 → **PRIMARY** S10
- SRC-gpt6w-web-3-U13 84-116 → **CROSS** S11,S12,S13,S14
- SRC-gpt6w-web-3-U14 84-92 → **PRIMARY** S11
- SRC-gpt6w-web-3-U15 93-102 → **PRIMARY** S12
- SRC-gpt6w-web-3-U16 103-110 → **PRIMARY** S13
- SRC-gpt6w-web-3-U17 111-116 → **PRIMARY** S14
- SRC-gpt6w-web-3-U18 — → **GLOBAL**
- SRC-gpt6w-web-3-U19 — → **GLOBAL**