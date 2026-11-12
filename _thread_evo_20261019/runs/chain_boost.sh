set -e
unset THREAD_ROUTE
export GLOSS_TAG=d0 LO_V=2 HUMAN_WRITER=argon FIX_LEN=0
: > runs/run_boost.log
# A: the decided DAG on both works, one product: N08 plain (p1) -> N09b -> N09 open review + fix -> N10c boost -> keep
( HUMAN_MODE=6 python -u v6human.py write p1 q2 >> runs/run_boost.log 2>&1
  LO_TAG=q2 python -u lang_open.py run >> runs/run_boost.log 2>&1
  LO_TAG=q2 python -u lang_open.py run --gem >> runs/run_boost.log 2>&1
  python -u v6human.py fixopen q2 q3 >> runs/run_boost.log 2>&1
  python -u v6cov.py q3 >> runs/run_boost.log 2>&1
  python -u v6boost.py fix q3 q4 >> runs/run_boost.log 2>&1
  python -u v6cov.py q4 >> runs/run_boost.log 2>&1
  python -u v6boost.py keep q3 q4 q4k >> runs/run_boost.log 2>&1 ) &
# B: boost on the current best product h17 (gpt3-judged coverage h17g already there)
( GLOSS_TAG= python -u v6boost.py fix h17g h19 >> runs/run_boost.log 2>&1
  python -u v6cov.py h19 >> runs/run_boost.log 2>&1
  GLOSS_TAG= python -u v6boost.py keep h17g h19 h19k >> runs/run_boost.log 2>&1 ) &
wait
echo MEASURE >> runs/run_boost.log
for t in q4k h19k; do
  python -u v6cov.py $t > runs/run_cov_$t.log 2>&1 &
  python -u v6alone.py $t > runs/run_alone_$t.log 2>&1 &
  LO_TAG=$t python -u lang_open.py run > runs/run_lo_$t.log 2>&1 &
  python -u v6fix.py blind $t h17 > runs/run_blind_$t.log 2>&1 &
  BLIND_REP=2 python -u v6fix.py blind $t h17 > runs/run_blind_${t}_r2.log 2>&1 &
done
wait
python v6weave.py q4k >> runs/run_boost.log 2>&1 || true
python v6weave.py h19k >> runs/run_boost.log 2>&1 || true
echo ALLDONE >> runs/run_boost.log
