# run137 E7 Flash 独立诊断（Op.60）

**诊断范围（只读，不扩展）：**

- Flash 分支独立诊断：gen=gflash、chooser=gflash、auditors=(gflash, luna_noweb)、
  judges=(gflash, luna_noweb)。配置冻结，CLI/环境不可覆盖；换模型=另开新 run。
- 输入冻结：run130 Op.60 洁净珠子 + run130:gpt56w 历史清单（只记来源 sha，
  producer 未知，manifest 声明），不新造、不重写旧候选。
- 三方盲比 a=本稿 / b=run124 生产稿 B / c=run132 V2A+Gemini 基线两套；
  **Op.60 的 c 为重建锚，非原始 V2A 真原稿**。
- 本诊断**不代替 GPT、不切 production、不是新模型公平赛**
  （prompt/input 全固定；任何 prompt 变动不得与模型变化混宣胜）。

**阻塞（缺席绝不写 DONE，本 run 只写 COMPLETION_PENDING）：**

- 两 w（gpt56w/gpt6w）新鲜公平对照：缺席（run135 post_submit_ambiguous 全局 hold）。
- Muse 评审：缺席（待主会话 T3 派发；盲审包 `muse_review_pack.json` 含 prompt 全文+seed+mapping+hash）。
- two-w 包（`twow_review_pack.json`）已导出但**不提交执行**。
- 全阵容最终裁决：阻塞，等两 w 解 hold + Muse 评审归位。

**工程说明：**

- 旧 run134 的 go.py 只读复用（切分/历史/解析/统计/盲比/轮换），不改旧文件；
  不兼容处：调用层改用 `tools/experiment_calls.call`（旧 `Store`/`cache_<step>.json`
  不再使用，新缓存为 `cache_<step>_exact.json`），自评 flag 经 `canonical_model`
  归一化（gflash_web 与 gflash 视为同一模型，旧逻辑会漏标），manifest 增补
  stop_reasons/timeouts/producer-unknown，报告增补 lifecycle（§7）与主 WHY 全列（§8）。
- 所有 prompt 全文由 runner 内联调用，不让内容模型读取路径。
- 工程测试：`python -I tools/tests/test_run137_e7_flash_diag.py`
  （纯 mock；import 不调 CLI；mock 在临时目录，不碰真实目录；禁真实 runner 冒烟，
  `go.py --smoke` 直接拒绝）。
