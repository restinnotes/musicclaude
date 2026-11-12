# pipe.py 实施及离线验证日志（2026-11-02）

- 授权范围：仅新增 pipe.py、schemes/P.json、schemes/Q.json、schemes/README_pipe.md，以及本目录内验证产物。已有 codex_log.txt / codex_prompt.md 不改。
- 所有文本通过 Python 显式 UTF-8 或 PowerShell -Encoding UTF8 读取。初次 PowerShell 管道向 Python 标准输入传脚本时附带 BOM，Python 报 SyntaxError，未产生写入；后续改用脚本文件或 python -c。
- 读取 ROOT 各父目录、schemes、_codex 及本目录的适用 AGENTS.md；未发现附加指令文件。
- 参考实现：schemes.py 的 work_info/segments/run_P/run_Q/call/save；v6fix.JUDGES/parse/tidy/view；covjudge.bead_text；evo.done/call/run_parallel。
- P：A0 → A1 → A2；A2 在内存替换七、Center 整段。所有原文及注释来自源码 AST / 原始提示词，未改动提示词文件。
- Q：A1 → A2、A3 并行 → A4。A3 虽不读取 A1 输出，仍显式 after A1 以复现原流程。step: 引用自动增加数据依赖。
- 模型核对：schemes.py 唯一 call 包装函数固定 model=evo.G6；因此 P/Q 所有 model 均为 g6。Q 的 GPT-5.6 标签指顾问来源，不代表实际生成模型。通用执行器支持 g56，严格映射 V.JUDGES。
- 调用边界：仅传 model 和原样 stage 元数据；不传 cli_args、web、推理参数，不修改路由、保温、watchdog 或任务计划。
- SAMPLE 规则：输入 TAG=pa、SAMPLE=2 时，运行 id 为 scpa_op60_A0_s2，成品 TAG 为 pas2；避免把 s2 重复加进运行 id。
- 已有真实 prompt.txt 含 evo 路由追加的 NO_WEB 段落；验证分别报告渲染正文直接比较及按现有路由追加后比较，绝不修改新脚本正文来掩盖这项差异。
- 当前仅发现 P 的 A0、Q 的 A1 各两首作品的真实 prompt.txt；未发现它们的 output.txt。
- 保护快照记录已有根目录 Python 源码、7 份提示词、2 份参考成品和现有 pa/qa prompt.txt 的 SHA-256；验证后再次核对。

后续离线验证明细见本日志追加内容及 results.json。

## 离线验证执行

- success: True
- 假 JSON：scpa_op60_A0，正文及调用参数逐字一致，2136 字符，SHA-256 fe2ca75b0bd984560891f8c3074056e26aeb94108ca2b42c98977badcedd3994。
- 假 JSON：scpa_op60_A1，正文及调用参数逐字一致，14184 字符，SHA-256 e7e86a7411645fca207b64761ab65063f556ae7f4fa5e93596b2193f805c4f48。
- 假 JSON：scpa_op60_A2，正文及调用参数逐字一致，11898 字符，SHA-256 93df1ebb1033a0a83be2e27aec3048ce7b48f197fabf23a8004a57ef1bffac2c。
- 假 JSON：scpa_op61_A0，正文及调用参数逐字一致，2147 字符，SHA-256 6f3436abe4a7dcbbd6eff18190171c2809c9ccb2bb2c5d2c85cc549c3a2906c7。
- 假 JSON：scpa_op61_A1，正文及调用参数逐字一致，14165 字符，SHA-256 a164319ed3fbc179dbeeba2caa4160c58d24a17e79680b1d95e62f55f122bf47。
- 假 JSON：scpa_op61_A2，正文及调用参数逐字一致，11249 字符，SHA-256 923ba7c2694f22265de8ba203504464500b361e68c3d53af8b0d36c5d60571e1。
- 假 JSON：scqa_op60_A1，正文及调用参数逐字一致，1451 字符，SHA-256 73078807f8db00df63dad8e5531579b56efb074a8b86255c31f64b862614572f。
- 假 JSON：scqa_op60_A2，正文及调用参数逐字一致，5405 字符，SHA-256 6552011ebc08ada4e5e1d4b3eeed4426aaf5fe1f3529d648dd9b1b858c0ee4d1。
- 假 JSON：scqa_op60_A3，正文及调用参数逐字一致，8223 字符，SHA-256 239f96a39d6fb9e5eafcdd65eec766c0b9cfd4fb43bf0a611cc8d4cd025bafbb。
- 假 JSON：scqa_op60_A4，正文及调用参数逐字一致，16245 字符，SHA-256 9938fa3ff9fd087be16c659a32773c2c3b69409f9ad79686b57ded11cb0848ff。
- 假 JSON：scqa_op61_A1，正文及调用参数逐字一致，1456 字符，SHA-256 dc6f7745fb85d5fc0bc9d4661fe7047db08bdb3459daf09a9a7011cc74822c0c。
- 假 JSON：scqa_op61_A2，正文及调用参数逐字一致，5075 字符，SHA-256 615caf183df37fe9db025abff6c1d1af41445b3601a2354b6964ceb6fdc78521。
- 假 JSON：scqa_op61_A3，正文及调用参数逐字一致，8534 字符，SHA-256 e447970bb365bd7e6b8a9c160376745ea50be516e449e073c670be34d1a2e84f。
- 假 JSON：scqa_op61_A4，正文及调用参数逐字一致，15256 字符，SHA-256 dd83cfcfc0b9ac3a29d9becaa5a35b12ccfdd182f6a7d9d51b18ba54c85025db。
- 真实 prompt：{"run_id": "scpa_op60_A0", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 2151, "utf8_sha256": "9d1cae6ec1411c1ad1584afcac3def261c6d86eb6ad5d16a8e957460bf2a15f7", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scpa_op61_A0", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 2162, "utf8_sha256": "1d9ab77c72e3221841a9e92933a2ebf81edfdd7f1bdfe2a0fbc3d6f764e18745", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scqa_op60_A1", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 1466, "utf8_sha256": "c1d3dda45fcca7cf66044f5ae19a58e928c72f8a70858f111fd5d61149c681d5", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scqa_op61_A1", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 1471, "utf8_sha256": "efe5e0b677ebc3cd56d4ad971e3438f7e8fc60fd40dbc66bb2033d1125d0b994", "windows_written_bytes_equal": true}
- SAMPLE and cache: PASS — 6 cache hits; scpa_<work>_<step>_s2; outputs <work>_pas2.json/.md; no submit
- both works parallel: PASS — P and Q initial steps for op60/op61 met at a two-party barrier
- Q branch dependencies: PASS — A2/A3 ran concurrently after A1; A4 began only after both finished
- independent steps and g56: PASS — two steps without dependencies ran concurrently; both used V.JUDGES['g56']
- source forms: PASS — nested list concatenation, explicit literal and edit step references validated
- failure propagation: PASS — unusable JSON stopped P descendants and save; two-work runner raised a failure
- preflight validation: PASS — cycle, unknown_dep, duplicate, model, path_escape, edit_stale, final, source, empty_placeholder; invalid SAMPLE/TAG; all rejected without model submission
- CLI: PASS — main(['run', absolute_spec, 'cli']) honored SAMPLE=3 and REF=m6w for both works
- protected files: PASS — 285 existing files retain identical SHA-256
- offline/write guard: PASS — no network/process events; no attempted writes outside validation directory; -B prevents pycache
- 成品 JSON/Markdown 字节比较：8 份通过；具体 SHA-256 见 results.json。
- 审计阻止事件：[]。

## 离线验证执行

- success: True
- 假 JSON：scpa_op60_A0，正文及调用参数逐字一致，2136 字符，SHA-256 fe2ca75b0bd984560891f8c3074056e26aeb94108ca2b42c98977badcedd3994。
- 假 JSON：scpa_op60_A1，正文及调用参数逐字一致，14184 字符，SHA-256 e7e86a7411645fca207b64761ab65063f556ae7f4fa5e93596b2193f805c4f48。
- 假 JSON：scpa_op60_A2，正文及调用参数逐字一致，11898 字符，SHA-256 93df1ebb1033a0a83be2e27aec3048ce7b48f197fabf23a8004a57ef1bffac2c。
- 假 JSON：scpa_op61_A0，正文及调用参数逐字一致，2147 字符，SHA-256 6f3436abe4a7dcbbd6eff18190171c2809c9ccb2bb2c5d2c85cc549c3a2906c7。
- 假 JSON：scpa_op61_A1，正文及调用参数逐字一致，14165 字符，SHA-256 a164319ed3fbc179dbeeba2caa4160c58d24a17e79680b1d95e62f55f122bf47。
- 假 JSON：scpa_op61_A2，正文及调用参数逐字一致，11249 字符，SHA-256 923ba7c2694f22265de8ba203504464500b361e68c3d53af8b0d36c5d60571e1。
- 假 JSON：scqa_op60_A1，正文及调用参数逐字一致，1451 字符，SHA-256 73078807f8db00df63dad8e5531579b56efb074a8b86255c31f64b862614572f。
- 假 JSON：scqa_op60_A2，正文及调用参数逐字一致，5405 字符，SHA-256 6552011ebc08ada4e5e1d4b3eeed4426aaf5fe1f3529d648dd9b1b858c0ee4d1。
- 假 JSON：scqa_op60_A3，正文及调用参数逐字一致，8223 字符，SHA-256 239f96a39d6fb9e5eafcdd65eec766c0b9cfd4fb43bf0a611cc8d4cd025bafbb。
- 假 JSON：scqa_op60_A4，正文及调用参数逐字一致，16245 字符，SHA-256 9938fa3ff9fd087be16c659a32773c2c3b69409f9ad79686b57ded11cb0848ff。
- 假 JSON：scqa_op61_A1，正文及调用参数逐字一致，1456 字符，SHA-256 dc6f7745fb85d5fc0bc9d4661fe7047db08bdb3459daf09a9a7011cc74822c0c。
- 假 JSON：scqa_op61_A2，正文及调用参数逐字一致，5075 字符，SHA-256 615caf183df37fe9db025abff6c1d1af41445b3601a2354b6964ceb6fdc78521。
- 假 JSON：scqa_op61_A3，正文及调用参数逐字一致，8534 字符，SHA-256 e447970bb365bd7e6b8a9c160376745ea50be516e449e073c670be34d1a2e84f。
- 假 JSON：scqa_op61_A4，正文及调用参数逐字一致，15256 字符，SHA-256 dd83cfcfc0b9ac3a29d9becaa5a35b12ccfdd182f6a7d9d51b18ba54c85025db。
- 真实 prompt：{"run_id": "scpa_op60_A0", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 2151, "utf8_sha256": "9d1cae6ec1411c1ad1584afcac3def261c6d86eb6ad5d16a8e957460bf2a15f7", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scpa_op61_A0", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 2162, "utf8_sha256": "1d9ab77c72e3221841a9e92933a2ebf81edfdd7f1bdfe2a0fbc3d6f764e18745", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scqa_op60_A1", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 1466, "utf8_sha256": "c1d3dda45fcca7cf66044f5ae19a58e928c72f8a70858f111fd5d61149c681d5", "windows_written_bytes_equal": true}
- 真实 prompt：{"run_id": "scqa_op61_A1", "direct_body_equal": false, "effective_text_equal": true, "only_difference": "evo.NO_WEB suffix", "characters": 1471, "utf8_sha256": "efe5e0b677ebc3cd56d4ad971e3438f7e8fc60fd40dbc66bb2033d1125d0b994", "windows_written_bytes_equal": true}
- SAMPLE and cache: PASS — 6 cache hits; scpa_<work>_<step>_s2; outputs <work>_pas2.json/.md; no submit
- both works parallel: PASS — P and Q initial steps for op60/op61 met at a two-party barrier
- Q branch dependencies: PASS — A2/A3 ran concurrently after A1; A4 began only after both finished
- independent steps and g56: PASS — two steps without dependencies ran concurrently; both used V.JUDGES['g56']
- source forms: PASS — nested list concatenation, explicit literal and edit step references validated
- failure propagation: PASS — unusable JSON stopped P descendants and save; two-work runner raised a failure
- preflight validation: PASS — cycle, unknown_dep, duplicate, model, path_escape, missing_prompt, edit_stale, final, source, empty_placeholder; invalid SAMPLE/TAG; all rejected without model submission
- CLI: PASS — main(['run', absolute_spec, 'cli']) honored SAMPLE=3 and REF=m6w for both works
- CLI failure status: PASS — invalid dependency graph returned SystemExit(1) before any submission
- protected files: PASS — 285 existing files retain identical SHA-256
- offline/write guard: PASS — no network/process events; no attempted writes outside validation directory; -B prevents pycache
- 成品 JSON/Markdown 字节比较：8 份通过；具体 SHA-256 见 results.json。
- 审计阻止事件：[]。

## 最终交付复核

- 首轮全部通过；补充缺失提示词及 CLI 非零退出检查后复验全部通过，最终为 11 项检查。
- 一条收尾只读 python -c 检查因括号笔误报 SyntaxError，未写入文件；已以本次 AST/JSON/哈希检查替代并通过。
- 14/14 假 JSON 提示词及调用参数一致；8/8 成品字节一致；4/4 真实提示词正文直接比较的差异严格等于现有 evo.NO_WEB 后缀，应用既有路由规则后 4/4 文本及 CRLF 写入字节一致。
- 285 份已有文件 SHA-256 不变。验证进程所有文件写入受审计限制在本目录；未触发网络、子进程或越界写入事件；使用 -B，未生成项目 __pycache__。
- 交付文件及最终 SHA-256 见 deliverables_manifest.json；所有假成品、夹具、逐字正文副本、验证标准输出均在本目录中。未写入真实 runs/ 或 evaluations/。
- 限制与风险：未进行真实模型端到端运行；真实历史文件仅覆盖 P/A0 与 Q/A1 两首作品。evo 缓存仍按 id 判定，更换说明需新 TAG/SAMPLE；相同 TAG/SAMPLE 会复用缓存并覆盖同名成品。Q 保留实际 G6 调用，与其顾问来源标签 GPT-5.6 的区别已在 README 说明。
- 新增 pipe.py：12372 bytes；SHA-256 abb861b6a58f1c4ad5b3a462ca4628fc8182359ef3a29ecc54937836c31891a3。
- 新增 schemes/P.json：2337 bytes；SHA-256 c1a7cb02974c72e8bdd75fd012520fd7e2a8242d365303029dfb04f1330e93ac。
- 新增 schemes/Q.json：1285 bytes；SHA-256 8fbc02d2cf2505406869352690b8eb245df8180a25ce09085d61d9fd14baa3b3。
- 新增 schemes/README_pipe.md：9061 bytes；SHA-256 f370fdd702746d09c484dc6be307aab0d369757a7c837ae2deac1fed01178f00。

## 离线验证执行

- success: False
- error: AssertionError('transport-adjusted real prompt mismatch: scpa_op60_A0')
- 假 JSON：scpa_op60_A0，正文及调用参数逐字一致，2136 字符，SHA-256 fe2ca75b0bd984560891f8c3074056e26aeb94108ca2b42c98977badcedd3994。
- 假 JSON：scpa_op60_A1，正文及调用参数逐字一致，14184 字符，SHA-256 e7e86a7411645fca207b64761ab65063f556ae7f4fa5e93596b2193f805c4f48。
- 假 JSON：scpa_op60_A2，正文及调用参数逐字一致，11898 字符，SHA-256 93df1ebb1033a0a83be2e27aec3048ce7b48f197fabf23a8004a57ef1bffac2c。
- 假 JSON：scpa_op61_A0，正文及调用参数逐字一致，2147 字符，SHA-256 6f3436abe4a7dcbbd6eff18190171c2809c9ccb2bb2c5d2c85cc549c3a2906c7。
- 假 JSON：scpa_op61_A1，正文及调用参数逐字一致，14165 字符，SHA-256 a164319ed3fbc179dbeeba2caa4160c58d24a17e79680b1d95e62f55f122bf47。
- 假 JSON：scpa_op61_A2，正文及调用参数逐字一致，11249 字符，SHA-256 923ba7c2694f22265de8ba203504464500b361e68c3d53af8b0d36c5d60571e1。
- 成品 JSON/Markdown 字节比较：4 份通过；具体 SHA-256 见 results.json。
- 审计阻止事件：[]。
