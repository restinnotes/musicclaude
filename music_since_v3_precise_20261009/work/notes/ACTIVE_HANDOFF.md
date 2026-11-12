# ACTIVE_HANDOFF（≤30 行；主会话维护）

更新：2026-10-08 晚｜git 见 `git log -5`｜启动顺序：CLAUDE.md → 本文件 → notes/PROJECT_STATE.md
规则：宪法本体 reference/PRODUCT_CONSTITUTION_V2.md；验收 notes/chat_findings_20261005/*/06_ACCEPTANCE_CRITERIA.md
生产配置：未变（run124 surface B gpt56w）。新链只做实验，未切换。
网页 GPT：tools/gpt2_adapter.py（gpt2.cmd ask --model gpt-5-6-thinking|gpt-6-thinking，固定 max，≤65536 字符）mock 18/18 过；
  真实烟雾 run131 待跑；runner 默认仍走旧 mg，`MUSIC_WEB_ROUTE=gpt2` 才走 gpt2。
Muse：delegate_task claude-proxy / muse-spark-1.3-contributor-free / xhigh。注意：Muse 会话结束会杀掉它起的后台进程 →
  长任务让 Muse 只写 go.py + dry-run，主会话用后台进程运行。
Gemini 代理 8045 会掉线：用桌面 "Antigravity Tools.lnk" 拉起。
基线：Op.52 = notes/baselines/op52_v2a_gemini_02/05；Op.60/61 无原始基线 → run132 用原版 V2A 提示词在 Gemini 重建（待跑）。
索引：notes/BASELINE_INDEX.md；增量案例：notes/research/r1_increment_cases.md
本轮进行中：
  run131_gpt2_smoke（go.py 由 Muse 写，主会话跑）
  run132_v2a_gemini_baseline（同上）
  run133_thread_spec：C7_STEP_v2 vs v3（作品特异性一句）× gpt56w/opus，识别测试 + 盲比
  run134_e7_diag（未开始）：E7_SURFACE_v0（ATTN_v1+撤下规则），Op.60 新珠子，与 run124 及重建 V2A 基线盲比
最重要的待裁决问题：Thread 塌成通用弧是不是"提示词没要求作品特异性"造成（run133）。
已知判断：E5 的 gpt56w 输出大多是真洞见（A1–A9），问题是少数与珠子矛盾（B1/B7）→ 倾向"生成后审核过滤"，
  而非追求 NONE 率；验收"NONE common enough"的本意应是"不被迫硬造"，如需改条文须用户授权。
不要自动复读：runs/run1xx 全量 outputs、旧聊天、run124 附录全文。
10-09 用户：生成者可以评自己；评审全上（gpt56w/gpt6w/opus/luna/gpro + Muse delegate），分评审单列、标出自评。gpt2 已恢复（直调 58 s 正常）。
10-09 主会话裁决：run137→148（E7 flash r1–r7、thread_resume r3–r6、收据类型绑定 C5/C6）停止——六版零产出，偏离产品目标；只读保留。
gpt2 hold（run135 gpt6w post_submit_ambiguous）已归档到 runs/_call_slots/gpt2web/_hold_archive/。
  opus 初判：v3 线作品特异（"你知道吗……"那句话能否在摇晃的水上被说出/接住），v2 仍是通用"美好会过去"。
10-09 用户：不要调用 Opus（我误派过一次 Opus 子代理，含 1 次冒烟调用，已停）。run149 作废。
gpt2 输入上限：约 2.1–2.3 万字（k17 20,479 字成功，k18 23,051 起提交前拒）。长输入任务两个 w 不能做。
run133：opus 23 段 + gpt56w 17 段（v2/v3 同截止）；Center 缺（opus 禁、gpt56w 超长）。识别评审 gpt56w/gpt6w/luna/gflash；盲比 luna/gflash(+Muse)。
run134 E7 诊断：gen=gflash_web（WHY 需长输入），chooser=gpt56w，审核 gpt56w+luna，judges luna/gflash/gpt56w/gpt6w(+Muse)。
runner 修：codex 的 error 事件（配置警告）不再算工具使用（luna 恢复）。
