---
name: opencode2api-deploy-watchdog
description: "Any opencode2api container redeploy must also clear the WARP watchdog seen-events list, or 429s never trigger rotation (Muse stuck at 429)"
metadata:
  node_type: memory
  type: project
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T19:23:23.115Z
---

服务器 azureuser@85.211.196.157 的 `~/opencode2api`（不在 git 下，改动只靠 `rollback/` 目录备份）。重新部署 opencode2api 容器时，除了换镜像、停启 `opencode2api-warp-watchdog.service`，还必须备份并清空 `state/warp-429-seen-events`（正规部署脚本 deploy-warp-sync2.py 就是这么做的）。

**Why:** 2026-09-25 13:35Z 我手动部署 fp-streamfix 镜像时漏了这一步。新容器的 WARP generation 从 0 重新计数，watchdog 按"原因+generation"去重，generation=0 的键早已在 seen 列表里，于是 340 次 429 全被跳过、从不轮换，Muse 连续 6 小时 429。19:22Z 备份到 `rollback/watchdog-seen-reset-20260925T192225Z` 后清空并重启 watchdog，立刻轮换到 generation=1，Muse 恢复。

**How to apply:** Muse 持续 429 时先看 `~/opencode2api/logs/warp-429.log` 是否有 "New classified WARP recovery event"，以及 `docker logs opencode2api | grep warp_rotation_wait` 的 generation；任何容器重建后都检查一次。用户对服务器修复会在聊天里授权，授权后直接执行，不要把命令丢回给用户。相关：[[music-run-cli-invocation]]。
