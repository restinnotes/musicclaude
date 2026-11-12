#!/usr/bin/env bash
# Quota watchdog (user 10-23: "如果没额度了就设置timer让有额度的时候触发继续"): probe gpt3 with a tiny call every 20 min until one
# succeeds, then exit 0 so the caller (a background task) can relaunch the interrupted step; finished calls are skipped on resume.
cd /d/musicclaude/_thread_evo_20261019
for i in $(seq 1 72); do
  id="quota_probe_$(date +%m%d%H%M)"
  if THREAD_GPT=${THREAD_GPT:-gpt3} python -c "
import evo,node2b,sys
node2b.job('$id','请只回复：好',{'stage':'quota_probe'},w='g6')[1]()
sys.exit(0 if evo.done('$id') else 1)" >/dev/null 2>&1; then echo "quota ok at $(date)"; exit 0; fi
  echo "no quota yet ($(date)); retry in 20 min"; sleep 1200
done
echo "gave up after 24h"; exit 1
