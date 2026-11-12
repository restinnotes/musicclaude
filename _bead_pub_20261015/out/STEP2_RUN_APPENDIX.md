## STEP2 分段与梯度探针追加记录（2026-10-16 UTC）

- 链路：gpt2 ask --file + --model gpt-6-thinking --json；health ready=true 全程；句柄最长6小时
- 成功7轮：G1/29B/14s、G2/3137B/13s、G3/8207B/16s、G4/17437B/13s（中性填充）；任务指令轮x2（2929B/16s，句柄0d9365a4、70c0b9c1）；极小恢复探测x1（12s，句柄2cf1b78c）
- 失败（均为 headless_native_result_rejected/phase=pre_submit）：旧整包37230Bx3（62s）、resume喂S1S2/58s、resume喂S1单2426B/58s、新会话resume喂S1/58s、fresh喂S2单2145B/62s、单包raw加任务19396B/63s、来源批A-S1S2-4056B/60s
- 文件：out/STEP2_response_raw.md bytes=1044 sha256=e468361cb745002f6eb0f7677c5be54a0a01ee213d48009fb4c888867e16db0e / out/STEP2_response_meta.json bytes=2588 sha256=18ea0db966911528cd27137dd99e01cd84df46500a4af314fa7de1a76980fad4 / out/STEP2_check.md bytes=1156 sha256=dea004d06a7a4ea9b89a508a67aa508e5de9b8fc07e988367392bda849747961 / out/STEP2_probes_appendix.md bytes=476 sha256=78da851e19bfc2cc280b3f8977ebc10389a81f767701a5d4dbbe361393910839
- 总探针与投递：梯度探针4次（G1-G4）加STEP2正式/分段投递8轮，均只调GPT-6w链路；无git操作、未读谱、未看旧切点
