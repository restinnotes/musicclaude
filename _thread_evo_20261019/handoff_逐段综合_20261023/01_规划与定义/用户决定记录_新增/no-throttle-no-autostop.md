---
name: no-throttle-no-autostop
description: "10-23 user — don't add concurrency caps or automatic account-stop flags to the GPT pipeline; switch accounts instead"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7c623294-a1ea-40eb-b513-ae6588ad2c39
  modified: 2026-10-23T14:55:47.694Z
---

User (2026-10-23), after gpt3 returned UPSTREAM_UNUSUAL_ACTIVITY and I added a THREAD_MAX_PAR cap plus a runs/ACCOUNT_STOP_<acct> flag that auto-skipped every later call: "不要并发上限也不要自动停用标记什么的". They pointed me to the other account instead ("gpt4可用").

**Why:** the user manages account health themselves. Throttling slows the experiments, and a sticky auto-stop flag silently kills runs.

**How to apply:**
- Keep the pipeline unthrottled.
- When an account shows protection signals, stop the current calls, tell the user, and switch THREAD_GPT to the account they name. Don't build caps or flags into evo.py/round.sh.
- Still check the cup probe once per account before relying on it.

This partly supersedes the "stop immediately on account-protection signals" line in [[gpt56-web-route]]. Related: [[gpt3-web-cli]].
