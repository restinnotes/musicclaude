set -e
unset THREAD_ROUTE
: > runs/run_boost2.log
roundA() { GLOSS_TAG=d0 python -u v6boost.py fix $1 $2 >> runs/run_boost2.log 2>&1; python -u v6cov.py $2 >> runs/run_boost2.log 2>&1; GLOSS_TAG=d0 python -u v6boost.py keep $1 $2 $3 >> runs/run_boost2.log 2>&1; python -u v6cov.py $3 >> runs/run_boost2.log 2>&1; }
roundB() { GLOSS_TAG= python -u v6boost.py fix $1 $2 >> runs/run_boost2.log 2>&1; python -u v6cov.py $2 >> runs/run_boost2.log 2>&1; GLOSS_TAG= python -u v6boost.py keep $1 $2 $3 >> runs/run_boost2.log 2>&1; python -u v6cov.py $3 >> runs/run_boost2.log 2>&1; }
( roundA q4k q5 q5k; roundA q5k q6 q6k ) &
( roundB h19k h20 h20k; roundB h20k h21 h21k ) &
wait
echo MEASURE >> runs/run_boost2.log
for t in q6k h21k; do
  python -u v6alone.py $t > runs/run_alone_$t.log 2>&1 &
  LO_TAG=$t LO_V=2 python -u lang_open.py run > runs/run_lo_$t.log 2>&1 &
  python -u v6fix.py blind $t h17 > runs/run_blind_$t.log 2>&1 &
  BLIND_REP=2 python -u v6fix.py blind $t h17 > runs/run_blind_${t}_r2.log 2>&1 &
done
wait
python v6weave.py q6k >> runs/run_boost2.log 2>&1 || true
python v6weave.py h21k >> runs/run_boost2.log 2>&1 || true
echo ALLDONE >> runs/run_boost2.log
