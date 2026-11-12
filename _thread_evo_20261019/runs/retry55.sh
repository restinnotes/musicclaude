#!/bin/bash
# 10-30 user: "每55分钟retry一次" — one real gpt3 call every 55 min; on success run the whole w30
cd /d/musicclaude/_thread_evo_20261019
while true; do
  sleep 3300
  echo "$(date) probe" >> runs/retry55.log
  PROBE_ONE=1 python -u v6plan2.py w24 w28 w30 >> runs/retry55.log 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then echo "$(date) ok -> full run" >> runs/retry55.log; break; fi
  echo "$(date) failed rc=$rc" >> runs/retry55.log
done
PLAN_PAR=1 python -u v6plan2.py w24 w28 w30 > runs/run_plan2_w30.log 2>&1
echo "$(date) w30 done" >> runs/retry55.log
