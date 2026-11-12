set -e
unset THREAD_ROUTE
export LO_V=2 HUMAN_WRITER=argon FIX_LEN=0
L=runs/run_lang3.log; : > $L
# fill judge gaps of the last round + direct blind between the two candidates
python -u v6cov.py q6k >> $L 2>&1 &
python -u v6cov.py h21k >> $L 2>&1 &
python -u v6alone.py h21k > runs/run_alone_h21k.log 2>&1 &
python -u v6fix.py blind q6k h21k > runs/run_blind_q6k_h21k.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind q6k h21k > runs/run_blind_q6k_h21k_r2.log 2>&1 &
LO_TAG=q6k python -u lang_open.py run --gem >> $L 2>&1 &
LO_TAG=h21k python -u lang_open.py run --gem >> $L 2>&1 &
wait
echo FIX >> $L
# language round on top of the boosted lines: N09c (open review -> fix) -> N10 -> N10g guard
lang() { G=$1; python -u v6human.py fixopen $2 $3 >> $L 2>&1; python -u v6cov.py $3 >> $L 2>&1
         GLOSS_TAG=$G python -u v6guard.py fix $2 $3 ${3}g >> $L 2>&1; python -u v6cov.py ${3}g >> $L 2>&1
         python -u v6guard.py revert $2 ${3}g ${3}k >> $L 2>&1; python -u v6cov.py ${3}k >> $L 2>&1; }
( export GLOSS_TAG=d0; lang d0 q6k q7 ) &
( export GLOSS_TAG=; lang "" h21k h22 ) &
wait
echo MEASURE >> $L
for t in q7k h22k; do
  python -u v6alone.py $t > runs/run_alone_$t.log 2>&1 &
  LO_TAG=$t python -u lang_open.py run > runs/run_lo_$t.log 2>&1 &
done
python -u v6fix.py blind q7k q6k > runs/run_blind_q7k_q6k.log 2>&1 &
python -u v6fix.py blind h22k h21k > runs/run_blind_h22k_h21k.log 2>&1 &
python -u v6fix.py blind h22k h17 > runs/run_blind_h22k_h17.log 2>&1 &
wait
python v6weave.py h22k >> $L 2>&1 || true
python v6weave.py q7k >> $L 2>&1 || true
echo ALLDONE >> $L
