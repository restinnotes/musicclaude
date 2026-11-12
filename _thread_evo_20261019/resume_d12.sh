#!/usr/bin/env bash
# After gpt4 returned HTTP 429 (10-23 ~22:53Z): wait for quota, then finish D12 drafts, their coverage, and the synth-check calibration.
cd /d/musicclaude/_thread_evo_20261019
export THREAD_GPT=${THREAD_GPT:-gpt4} PYTHONUNBUFFERED=1
bash quota_wait.sh || exit 1
python draft12.py >> runs/D12.log 2>&1
python covjudge.py run "d12*" > runs/COV7.log 2>&1
python calib_synth.py > runs/CALS.log 2>&1
echo "resume done $(date)"
