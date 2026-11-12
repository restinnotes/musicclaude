# 11-02 round 1 (迭代准则): judges JV=2; re-measure baseline m6w; quick-screen schemes P and Q (gen -> measure -> blind x4 vs m6w)
export JV=2 MG_ATTEMPTS=5
L=runs/run_round1.log; echo "START $(date)" >> $L
measure() {  # $1 tag
  python -u v6cov.py $1 > runs/run_cov2_$1.log 2>&1 &
  python -u v6alone.py $1 > runs/run_alone2_$1.log 2>&1 &
  ( E2E_TAG=$1 python -u e2e_open.py run > runs/run_eo2_$1.log 2>&1; E2E_TAG=$1 python -u e2e_open.py run --gem >> runs/run_eo2_$1.log 2>&1 ) &
  if [ "$1" != m6w ]; then
    python -u v6fix.py blind $1 m6w > runs/run_blind2_$1.log 2>&1 &
  fi
  wait
}
( measure m6w; echo "BASE MEASURED $(date)" >> $L ) &
( SCHEME=P TAG=pa python -u schemes.py run > runs/run_sc_pa.log 2>&1; echo "PA GEN EXIT $? $(date)" >> $L; measure pa; echo "PA MEASURED $(date)" >> $L ) &
( SCHEME=Q TAG=qa python -u schemes.py run > runs/run_sc_qa.log 2>&1; echo "QA GEN EXIT $? $(date)" >> $L; measure qa; echo "QA MEASURED $(date)" >> $L ) &
wait
echo "ROUND1 DONE $(date)" >> $L
