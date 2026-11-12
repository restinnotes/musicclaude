# BEAD_SOURCE_LEDGER（STEP4 GPT-6w · 来源台账与保留/舍弃账本）

> 本轮14段全部 pre_submit 秒拒，无任何模型回包，故无保留/舍弃可登记。本台账如实记录每段投放的输入构成与失败证据，不虚构内部珠子。

- 模板：`music_bead_published_structure_only_20261015/prompts/04_固定乐段Aonly珠子.txt`（四占位：WORK＝肖邦船歌Op.60 116小节；SEGMENT＝各段C2范围＋标签；A_POOL＝随附机械附件；STRUCTURE＝C2出处＋C1/C3差异＋分歧区声明）。
- 每段附件：`out/STEP4_inputs/ATTACH_<S>_Apool.txt`（从A_POOL_MAP.json机械提取该段PRIMARY＋CROSS_SEGMENT＋UNCERTAIN逐条原文，未改一字；A07/A08有逐字原文，A01/A03/A04/A05/A06无逐条原文处补同来源小节交集节全文verbatim＋候选UID清单＋各来源preamble；明确标注UNCERTAIN/LONG_RANGE/UNRESOLVED不进读者正文；S09 PRIMARY为空如实写明）。
- 每段短正文：`out/STEP4_inputs/STEP4_short_<S>.txt`（约1044–1153字符）；另有首版长正文 `STEP4_prompt_<S>.txt`（正文内联全部Pool，约5969–9937字符，S01已验证被拒，未再投其余13段）。
- S01尝试2次：①长正文内联（59秒，exit=1）；②短正文＋单附件（秒拒，exit=1）。S02–S14各尝试1次：短正文＋单附件（S07耗时17秒、其余约59秒，均exit=1，同类错误）。均未超每段2次上限。
- 链路对照：重放STEP3已知成功最小探针（probe_min.txt＋grok单件附件）同样 `headless_native_result_rejected/pre_submit` 秒拒，判定为链路侧故障，与STEP4内容无关。health当时ready=true（docker_ready=true，cup=8）。
- 风险：链路恢复前任何STEP4生成均不可行；附件与短正文已就绪，链路恢复后可直接重投，无需重做输入。

| 段 | 范围标签 | PRIMARY/CROSS/UNCERTAIN | 结果 | 证据文件 |
|---|---|---|---|---|
| S01 | 1-3序奏 | 7/3/0 | FAILED×2 | STEP4_stdout_S01.json(0B)/STEP4_stderr_S01.txt；probe_short_S01.json(0B)/.err |
| S02 | 4-16第1主題 | 9/11/0 | FAILED | STEP4_short_out_S02.json(0B)/STEP4_short_err_S02.txt |
| S03 | 17-23間句 | 1/12/0 | FAILED | STEP4_short_out_S03.json(0B)/STEP4_short_err_S03.txt |
| S04 | 24-34第1主題（確保） | 1/11/0 | FAILED | STEP4_short_out_S04.json(0B)/STEP4_short_err_S04.txt |
| S05 | 35-39間句 | 1/11/2 | FAILED | STEP4_short_out_S05.json(0B)/STEP4_short_err_S05.txt |
| S06 | 40-50第2主題前半 | 1/9/5 | FAILED | STEP4_short_out_S06.json(0B)/STEP4_short_err_S06.txt |
| S07 | 51-61第2主題前半（確保） | 2/12/6 | FAILED | STEP4_short_out_S07.json(0B)/STEP4_short_err_S07.txt |
| S08 | 62-71第2主題後半 | 1/11/4 | FAILED | STEP4_short_out_S08.json(0B)/STEP4_short_err_S08.txt |
| S09 | 72-77間句 | 0/8/2 | FAILED | STEP4_short_out_S09.json(0B)/STEP4_short_err_S09.txt |
| S10 | 78-83挿入句 | 10/4/3 | FAILED | STEP4_short_out_S10.json(0B)/STEP4_short_err_S10.txt |
| S11 | 84-92第1主題（再現） | 6/9/2 | FAILED | STEP4_short_out_S11.json(0B)/STEP4_short_err_S11.txt |
| S12 | 93-102第2主題後半（再現） | 5/11/4 | FAILED | STEP4_short_out_S12.json(0B)/STEP4_short_err_S12.txt |
| S13 | 103-110第2主題前半（再現） | 3/10/4 | FAILED | STEP4_short_out_S13.json(0B)/STEP4_short_err_S13.txt |
| S14 | 111-116終結句 | 8/7/6 | FAILED | STEP4_short_out_S14.json(0B)/STEP4_short_err_S14.txt |

## mini12 ledger (GPT-6w only, short-noattach)

11 success, S13 FAILED x2. minis under 500 chars: instruction+pool-compress (A07/A08 verbatim; other UIDs referenced; missing-4 A02/A09/A10/A11 absent). No attachments.

## S13 retry (GPT-6w only, short-noattach fresh)

- Input `STEP4_inputs/STEP4_mini_S13r.txt`: rewritten pool-compress (~380 chars), dropped 110-111 cross-boundary refs and "备查文件" phrasing, kept strictly inside mm.103-110.
- Result OK: `mini_S13r_out.json` completed=True ~49s exit0, len=295 chinese=214. 14/14 complete.

| seg | label | result | evidence | len |
|---|---|---|---|---|
| S02 | mm.4-16 di1zhuTi | OK | mini_S02_out.json | len=292 chinese=222 trunc-tail |
| S03 | mm.17-23 jianJu | OK | mini_S03_out.json | len=287 chinese=220 trunc-tail |
| S04 | mm.24-34 di1zhuTi-queBao | OK | mini_S04_out.json | len=245 chinese=221 |
| S05 | mm.35-39 jianJu | OK | mini_S05_out.json | len=295 chinese=224 trunc-tail |
| S06 | mm.40-50 di2qianBan | OK | mini_S06_out.json | len=282 chinese=212 trunc-tail |
| S07 | mm.51-61 di2qianBan-queBao | OK | mini_S07_out.json | len=247 chinese=225 |
| S08 | mm.62-71 di2houBan | OK | mini_S08_out.json | len=290 chinese=208 |
| S10 | mm.78-83 chaRuJu | OK | mini_S10_out.json | len=273 chinese=246 |
| S11 | mm.84-92 di1zaiXian | OK | mini_S11_out.json | len=294 chinese=213 |
| S12 | mm.93-102 di2houBan-zaiXian | OK | mini_S12_out.json | len=304 chinese=222 |
| S14 | mm.111-116 zhongJieJu | OK | mini_S14_out.json | len=295 chinese=225 trunc-tail |
| S13 | mm.103-110 | OK retry | mini_S13r_out.json len=295 chinese=214; prior FAILEDx2 mini_S13_err.txt | 295 |

- Dropped: UNCERTAIN/LONG_RANGE/UNRESOLVED not in reader text; unexpanded int-PRIMARY only referenced, nothing fabricated.
