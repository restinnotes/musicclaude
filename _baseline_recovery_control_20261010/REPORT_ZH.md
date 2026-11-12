# owned 证据恢复审计报告（只读，无模型调用）

- 审计脚本：`D:/musicclaude/_baseline_recovery_control_20261010/audit_owned_recovery.py`（参数化，`python3 -I` 运行，无网络、无模型请求、无外部调用）
- 机器可读结论：`owned_recovery_audit.json`（同目录）
- 冻结源：`D:/musicclaude/_dl_latest_zip_work`；owned 池：`D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006`（622 个 job-*，其中 gpt-6-thinking 227）
- 安全边界：只读 started/result/submitted/response 与普通诊断（capture-binding-diagnostic、handoff-summary、worker-attestation、console、requests.jsonl 的传输字段）；
  未读取、未输出任何浏览器凭据、token、sealed handoff/ciphertext、session 状态字节、DPAPI 文件内容（仅记录存在性）。
- 绑定键（关键修正）：meta 存的是**原始 prompt 文件 sha**，而 owned job 绑定的是**归一化后 prompt sha**
  （utf-8-sig 解码、CRLF/CR→LF、rstrip；与 `headless_native_provider._validate` 一致）。仅用原始 sha 会得到 0 候选的假阴性。
  候选还要求：model 一致＋started.utc 落在 [meta.utc_start−45s, utc_start+elapsed+30s]。同 prompt 多次调用时，时间窗＋独有 job id 区分，
  不做纯 prompt-hash 硬匹配。

## 一、9 个旧目标：全部“已绑定但未完成”，零可恢复

| 目标 | 归一化 sha（前12） | 窗内候选 ownedjob | 终态 | 结论 |
|---|---|---|---|---|
| trials/gpt6w/A01/r04 | 31a707e4450d | job-01010d58 (09:16:03) | completed=False, phase=post_submit_ambiguous, 无 response.txt, 有 submitted | 不可恢复：答案从不存在 |
| trials/gpt6w/B11/r03 | 401a2d775ddd | job-426cd287 (pre, 无submitted)；job-ef1ef252 (post_submit_ambiguous, 有submitted) | 均为 False，无 response.txt | 不可恢复 |
| trials/gpt6w/B18/r04 | 3d0e9e4fa11b | job-f20ccc7e (pre)；job-7223e410 (post_submit_ambiguous) | 均为 False | 不可恢复 |
| trials/gpt6w/C18/r04 | 869bcb0c37f0 | job-1be65409 (post_submit_ambiguous) | False，无 response.txt | 不可恢复 |
| trials/gpt6w/B23/r01 | 73e7107699c8 | job-567387a3 (post_submit_ambiguous) | False，无 response.txt | 不可恢复 |
| reviews/gpt6w/G_k02_r01_judgegpt6w_AB | c456b7a6b7f6 | job-52b20693 (post_submit_ambiguous) | False | 不可恢复 |
| reviews/gpt6w/D_k23_r05_gengpt56w_judgegpt6w_AB | 80b95d03abc1 | job-d6a8998a (post_submit_ambiguous) | False | 不可恢复 |
| reviews/gpt6w/D_k23_r05_gengpt56w_judgegpt6w_BA | 4879959e2bff | job-04462ff0 (post_submit_ambiguous) | False | 不可恢复 |
| reviews/gpt6w/G_k23_r01_judgegpt6w_BA | 5657b873797d | job-1d889222 (post_submit_ambiguous) | False | 不可恢复 |

共同点（每个候选都已逐项核对 `owned_recovery_audit.json` 内 checks）：
- route=gpt-6-thinking、effort=max、temporary 新会话、native prepare、prompt sha 绑定——**路由五项全对**；
- 但 `completed=False`、`prepared_response_validation` 无 terminal、`response.txt` 不存在、`response_sha` 为空——**恢复四项全缺**。
- post_submit_ambiguous 的 9 个 job 有 `submitted.json`（formal_http_generation 已 POST），console 均为
  `ChatGPT stream ended before completion; partial output was discarded`（服务端流中断、partial 已丢弃，无残留文本）。
  capture-binding-diagnostic 仅证明“请求配对正确”（model/effort/temporary/conduit 均为 true，captured_values_logged=false），
  不含任何答案内容。requests.jsonl 只有传输字段，无正文。
- 原 CLI exit=1 如实保留，未伪造 exit=0；原证据未动；无重提交、无删锁、无覆盖。
- 恢复置信边界：**高置信“无可恢复答案”**——不是因为 raw 为空，而是因为绑定 job 的终态证据完整且明确否定
  （completed=False＋无 response.txt＋中断原因明确）。若未来出现同窗 completed=True 的新 job，才可重跑本脚本复核。

## 二、新批 33 项（UTC 22:24:20 启动，终态 22:26:53，33/33 未捕获结果）

- **A01r03（retry_presubmit，exit=0，153.2s，stdout/stderr 空）：已恢复。**
  绑定 `job-e68d5a90d19f4ff9b170caec0b2c501c`（started 22:24:23.24 = meta start +3.07s）七要素齐全：
  gpt-6-thinking / max / temporary / provider_interface / native / isolated / prompt sha 绑定一致；
  completed=True、terminal=True、work_cont=False；response.txt 15428 字节、sha `5aeb3933…002928` 与 result 一致、非空；
  有 submitted marker（22:24:35.08）。已落盘：
  - `SUPPLEMENTAL_RECOVERED_FROM_OWNED_EVIDENCE__A01r03_retry_presubmit.txt`（答案正文）
  - 同名 `.meta.json`（元数据，明确 `RECOVERED_FROM_OWNED_EVIDENCE=true`、`not_original_runner_success=true`，
    原 CLI exit=0/stdout 空如实保留，原 meta 不动）。
  注意：该答案是 A01 批次正文（batch_id A01），非旧 9 目标中任何一项的替代。
- **其余 32 项（exit=1，stdout/stderr 空，elapsed 1.5–15s）：缺证明状态，不做结论。**
  归一化绑定排查：32 项在各自时间窗内**零 ownedjob 候选**（job 池在 22:23:20 后仅新增 1 个，即上面的 A01r03 job）。
  但这只能证明“owned 池无记录”，不能证明“未触及 provider”——launcher 层失败（如隐藏窗口 flags 导致输出丢失、
  子进程委派异常）同样产生零 job。launcher flags 问题仅列为**根因候选**，未予证实。
  32 项保持 `failure_or_ambiguous`，原 meta（含 scheduler=`baseline_parallel_control_20261010/pipeline.py`、
  scheduler_mode=retry_presubmit、worker、provider_job_directory=null）全部保留，不改、不重发。
  如需 pre_submit 重分类，必须先由 launcher 侧给出独立证据（进程创建记录/窗口日志），再以
  `pre_submit_reclassification` supplement 形式单列，同样不改原 meta。

## 三、给独立 validator 的接入说明

1. 复跑：`python3 -I audit_owned_recovery.py --frozen D:/musicclaude/_dl_latest_zip_work --runs D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006 --out <空目录>`；
   预期 `targets=9, recoverable=0`。脚本只读；DPAPI/凭据类文件从不打开内容。
2. 抽查任一候选：对照 `started.json`（model/effort/temporary/prompt_sha256/utc）与 `result.json`
   （completed/provider_phase/metadata.prepared_response_validation）及 `response.txt`/`submitted.json` 存在性。
3. A01r03 恢复校验：`sha256sum SUPPLEMENTAL…A01r03_retry_presubmit.txt` 应为
   `5aeb3933dc2f5f48345ccfc5d9ab60353985ec748677b792b13614a6e0029282`，与源 job 的 result.json 一致。
4. review manifest 已从 88 增至 97：本次恢复目标仍是旧 id，不受新增行影响；如需扩 audit，用 `--targets` 传入新 id 列表即可。
