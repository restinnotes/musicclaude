#!/usr/bin/env bash
# 10-24: after the 429, gpt4 answers tiny probes but hands every long answer to a websocket topic the bridge does not
# follow (INCOMPLETE_RESPONSE ~50 s). A tiny probe therefore proves nothing: probe hourly with one real pending D12 draft
# (one message per hour), and once a long answer completes, run the resume chain.
cd /d/musicclaude/_thread_evo_20261019
export THREAD_GPT=${THREAD_GPT:-gpt4} PYTHONUNBUFFERED=1
sleep 3600   # first let the rolling hour clear: retries after the 429 kept the account over its hourly budget
for i in $(seq 1 24); do
  tag=$(date +%m%d%H%M)
  if EVO_ATTEMPTS=1 python - <<PY
import sys, evo, node2b, draft12 as d
rid = "d12s6_op61_r2"   # a real pending draft: if it completes, draft12.py later just parses it
node2b.job(rid, d.msg("op61", "s"), {"stage": "d12", "work": "op61", "lens": "s", "probe": "$tag"}, w="g6")[1]()
sys.exit(0 if evo.done(rid) else 1)
PY
  then echo "long answer ok at $(date)"; bash resume_d12.sh; exit 0; fi
  echo "long answers still cut off ($(date)); retry in 60 min"; sleep 3600
done
echo "gave up after 24h"; exit 1
