---
name: gpt56-web-route
description: "GPT-5.6 via ChatGPT Web (gpt2agent-safechain) — how to call it and the user's degradation-detection rule (cup-matching probe, >3 min, answer 8)"
metadata:
  node_type: memory
  type: project
  originSessionId: 92476755-b11c-4869-8156-9f3da1650d78
  modified: 2026-09-26T17:11:33.462Z
---

> 10-08 status: historical reference. Muse now goes through T3 delegate_task ([[delegation-split]]); web GPT is being migrated to the `gpt2` CLI (not yet verified — check notes/ACTIVE_HANDOFF.md). Routes below are dated evidence, not current facts.

用户对 GPT-5.6 寄予厚望（2026-09-26），要求把它塞进所有当前/实验中的链路，每个至少 3 份，只收集证据、不做下一轮迭代。

- **调用：** D:\musicclaude\gpt2agent-safechain（ChatGPT 网页额度，复用本机 ~/.codex/auth.json 登录）。项目侧入口 `tools/chatgpt_run.py`，用 `D:\musicclaude\gpt2agent-safechain\.venv-local\Scripts\python.exe` 运行（仓库自带 .venv 指向不存在的解释器）。只用 `gpt-5-6-thinking` + `thinking_effort=max`，**不用 -wm 变体**。每账号一把锁、请求间隔 ≥5 s；加压力要靠多账号（另一个 CODEX_HOME），不是单账号并发。
- **降智判定（用户规定）：** 任务异常快（<60 s）或服务端 slug 不对只算"疑似"；疑似后用固定的水杯配对题复测——正常应 >3 分钟且答案为 8。复测不过才是高置信度降智 → 停队列；复测通过则保留那份快速产出、继续。账号保护信号（403/429/挑战/冷却）立即停。
- **联网：** 网页端关不掉搜索，用户说不必关；非联网任务末尾加"回答时请不要进行联网搜索。"（记为 harness_suffix），provider meta 记录 web_citations。
- **仓库补丁（2026-09-26）：** vendor/gpt2agent/frontend.py 列表 append 改为展开（content_references 补丁曾导致解析失败）；provider 结果 meta 增加 web_citations / search_result_groups。40 项离线测试通过。

- **2026-09-26 晚实测（D:\musicclaude\webchat-nodegrade）：** 同一水杯题，Chrome 官方 → thinking/无工具/答 8；非浏览器客户端全部降智：safechain+team Codex token（6 / 拒答，coding 或 data analysis）、ai-stack 老 gpt2agent（上周正常那份，09-26 18:22 答 6）、safechain+plus **网页** token（E1，44 s，ContainerTool/coding，答错）。body 已与 Chrome 对齐 → 凭证来源、账号、代码版本、端点均已排除；剩下的只有真浏览器才产生的信号（Sentinel/Turnstile/PoW、Cloudflare 指纹、客户端版本）。用户确认 plus/team 账号本身都不降智，别再猜账号。Codex 官方通道不提供 5.6（"not supported when using Codex with a ChatGPT account"）。我拒绝做绕过 Turnstile/指纹这类反机器人检测的工作。plus 网页 token 放在 ~/.codex-web/auth.json（源文件在桌面 current.txt，含 sessionToken）。

**Why:** 用户实测没有降智，指出我用 15 s 回复就判降智不对，给出了水杯题作为高置信度判据。

**How to apply:** 续跑 run31_gpt56 时直接重新启动同一 jobs.json（已完成的跳过，提交边界不明的不重提）。相关：[[music-run-cli-invocation]]、[[stop-when-conclusive]]。
