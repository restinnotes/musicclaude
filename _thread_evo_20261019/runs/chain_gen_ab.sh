set -e
unset THREAD_ROUTE
export GLOSS_TAG=d0 LO_V=2 HUMAN_WRITER=argon FIX_LEN=0
: > runs/run_gen_ab.log
( WRITE_PLAIN=1 python -u v6gen.py write d0 p1 >> runs/run_gen_ab.log 2>&1 ) &
( python -u v6gen.py writeseg d0 s1 >> runs/run_gen_ab.log 2>&1 ) &
wait
for t in p1 s1; do ( LO_TAG=$t python -u lang_open.py run >> runs/run_gen_ab.log 2>&1; LO_TAG=$t python -u lang_open.py run --gem >> runs/run_gen_ab.log 2>&1 ) & done
wait
python -u v6human.py fixopen p1 p2 >> runs/run_gen_ab.log 2>&1 &
python -u v6human.py fixopen s1 s2 >> runs/run_gen_ab.log 2>&1 &
wait
echo MEASURE >> runs/run_gen_ab.log
for t in p2 s2 d3g; do
  python -u v6cov.py $t > runs/run_cov_$t.log 2>&1 &
  python -u v6alone.py $t > runs/run_alone_$t.log 2>&1 &
  LO_TAG=$t python -u lang_open.py run > runs/run_lo_$t.log 2>&1 &
done
for t in p2 s2; do
  python -u v6fix.py blind $t d3 > runs/run_blind_${t}.log 2>&1 &
  BLIND_REP=2 python -u v6fix.py blind $t d3 > runs/run_blind_${t}_r2.log 2>&1 &
done
wait
echo ALLDONE >> runs/run_gen_ab.log
