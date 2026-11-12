# usage: bash runs/meas.sh <tag> [blindbase=m6w]   JV=2 measurements; safe to re-run (finished calls are reused)
export JV=2 MG_ATTEMPTS=5
t=$1; b=${2:-m6w}
python -u v6cov.py $t > runs/run_cov2_$t.log 2>&1 &
python -u v6alone.py $t > runs/run_alone2_$t.log 2>&1 &
( E2E_TAG=$t python -u e2e_open.py run > runs/run_eo2_$t.log 2>&1; E2E_TAG=$t python -u e2e_open.py run --gem >> runs/run_eo2_$t.log 2>&1 ) &
if [ "$t" != "$b" ] && [ "$b" != none ]; then python -u v6fix.py blind $t $b > runs/run_blind2_$t.log 2>&1 & fi
wait
echo "$t MEASURED $(date)" >> runs/run_round1.log
