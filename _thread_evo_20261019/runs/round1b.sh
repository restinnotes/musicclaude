# 11-02 round 1 restart with fixed prompts: P1 (tag pb), Q1 (tag qb), via pipe.py; JV=2 judges; blind x4 vs m6w
export JV=2 MG_ATTEMPTS=5
L=runs/run_round1.log; echo "START-B $(date)" >> $L
measure() {
  python -u v6cov.py $1 > runs/run_cov2_$1.log 2>&1 &
  python -u v6alone.py $1 > runs/run_alone2_$1.log 2>&1 &
  ( E2E_TAG=$1 python -u e2e_open.py run > runs/run_eo2_$1.log 2>&1; E2E_TAG=$1 python -u e2e_open.py run --gem >> runs/run_eo2_$1.log 2>&1 ) &
  python -u v6fix.py blind $1 m6w > runs/run_blind2_$1.log 2>&1 &
  wait
}
run_one() {  # spec tag
  python -u pipe.py run schemes/$1.json $2 > runs/run_sc_$2.log 2>&1; rc=$?
  echo "$2 GEN EXIT $rc $(date)" >> $L
  if [ $rc -eq 0 ]; then measure $2; echo "$2 MEASURED $(date)" >> $L; fi
}
run_one P1 pb &
run_one Q1 qb &
wait
echo "ROUND1B DONE $(date)" >> $L
