set -e
unset THREAD_ROUTE
export LO_V=2 HUMAN_WRITER=argon FIX_LEN=0 WORD_EDITORS=gem,argon
L=runs/run_final.log; : > $L
# 1. measure h23 (and the DAG line q8w): coverage, open review, standalone
python -u v6cov.py h23 >> $L 2>&1 &
python -u v6cov.py q8w >> $L 2>&1 &
LO_TAG=h23 python -u lang_open.py run > runs/run_lo_h23.log 2>&1 &
LO_TAG=q8w python -u lang_open.py run > runs/run_lo_q8w.log 2>&1 &
wait
echo PHASE2 >> $L
python -u v6alone.py h23 > runs/run_alone_h23.log 2>&1 &
python -u v6fix.py blind h23 h17 > runs/run_blind_h23_h17.log 2>&1 &
python -u v6fix.py blind q8w h23 > runs/run_blind_q8w_h23.log 2>&1 &
# 2. one more language loop on both lines: N09c -> N10 -> N10g -> N09w
lang() { python -u v6human.py fixopen $1 $2 >> $L 2>&1; python -u v6cov.py $2 >> $L 2>&1
         python -u v6guard.py fix $1 $2 ${2}g >> $L 2>&1; python -u v6cov.py ${2}g >> $L 2>&1
         python -u v6guard.py revert $1 ${2}g ${2}k >> $L 2>&1
         python -u v6word.py ${2}k $3 >> $L 2>&1; }
( export GLOSS_TAG=; lang h23 h24 h25w ) &
( export GLOSS_TAG=d0; lang q8w q9 q10w ) &
wait
echo PHASE3 >> $L
python -u v6cov.py h25w >> $L 2>&1 &
python -u v6cov.py q10w >> $L 2>&1 &
LO_TAG=h25w python -u lang_open.py run > runs/run_lo_h25w.log 2>&1 &
LO_TAG=q10w python -u lang_open.py run > runs/run_lo_q10w.log 2>&1 &
wait
python -u v6fix.py blind h25w h23 > runs/run_blind_h25w_h23.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h25w h23 > runs/run_blind_h25w_h23_r2.log 2>&1 &
python -u v6fix.py blind q10w h25w > runs/run_blind_q10w_h25w.log 2>&1 &
python -u v6alone.py h25w > runs/run_alone_h25w.log 2>&1 &
wait
WEAVE_FALLBACK=h23 python v6weave.py h25w >> $L 2>&1 || true
echo ALLDONE >> $L
