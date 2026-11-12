#!/usr/bin/env bash
# One iteration round for one piece: beam (graph) -> join -> joinjudge -> head-to-head (v6, previous round, this round) -> advisor.
# A failed step waits for quota (quota_wait.sh) and retries; finished calls are skipped on resume.
# usage: bash round.sh <T> <op60|op61> <prevT or ->   (env: THREAD_GPT, BEAM_*)
cd /d/musicclaude/_thread_evo_20261019
T=$1; W=$2; PREV=$3; LOG=runs/ROUND_$T.log
step() { for try in 1 2 3; do python -u "$@" >> $LOG 2>&1 && return 0; echo "step failed: $* (try $try)" >> $LOG; bash quota_wait.sh >> $LOG 2>&1; done; return 1; }
step beam.py all $T $W || exit 1
step join.py $T $W || exit 1
step joinjudge.py $T $W || exit 1
if [ "$PREV" != "-" ]; then step headtohead.py $W v6,$PREV,$T || exit 1; else step headtohead.py $W v6,$T || exit 1; fi
step advisor.py $T $W || exit 1
echo "ROUND DONE $T" >> $LOG
