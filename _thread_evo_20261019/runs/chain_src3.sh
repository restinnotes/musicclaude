set -e
unset THREAD_ROUTE
export MG_ATTEMPTS=5 TAG=e LO_V=2 HUMAN_WRITER=argon FIX_LEN=0 WORD_EDITORS=gem,argon GLOSS_TAG=e0
L=runs/run_src3.log; echo RESTART >> $L
# N05 v3 / N06 v5 with the new Center
python -u dag_src3.py lines >> $L 2>&1
python -u dag_src3.py judge >> $L 2>&1
python -u dag_src3.py graph >> $L 2>&1
python -u dag_src3.py import >> $L 2>&1
echo DOWNSTREAM >> $L
python -u v6gen.py gloss >> $L 2>&1
WRITE_PLAIN=1 python -u v6gen.py write e0 e1 >> $L 2>&1
LO_TAG=e1 python -u lang_open.py run >> $L 2>&1
LO_TAG=e1 python -u lang_open.py run --gem >> $L 2>&1
python -u v6human.py fixopen e1 e2 >> $L 2>&1
python -u v6cov.py e2 >> $L 2>&1
# N10c two rounds
boost() { python -u v6boost.py fix $1 $2 >> $L 2>&1; python -u v6cov.py $2 >> $L 2>&1; python -u v6boost.py keep $1 $2 $3 >> $L 2>&1; python -u v6cov.py $3 >> $L 2>&1; }
boost e2 e3 e3k
boost e3k e4 e4k
# language round: N09 -> N09c -> N10g -> N09w
LO_TAG=e4k python -u lang_open.py run >> $L 2>&1
LO_TAG=e4k python -u lang_open.py run --gem >> $L 2>&1
python -u v6human.py fixopen e4k e5 >> $L 2>&1; python -u v6cov.py e5 >> $L 2>&1
python -u v6guard.py fix e4k e5 e5g >> $L 2>&1; python -u v6cov.py e5g >> $L 2>&1
python -u v6guard.py revert e4k e5g e5k >> $L 2>&1
python -u v6word.py e5k e6w >> $L 2>&1
echo MEASURE >> $L
# 11-01 user: judge the e2e product by open questions only, no comparison with another line
python -u v6cov.py e6w > runs/run_cov_e6w.log 2>&1 &
LO_TAG=e6w python -u lang_open.py run > runs/run_lo_e6w.log 2>&1 &
LO_TAG=e6w python -u lang_open.py run --gem > runs/run_lo_e6w_gem.log 2>&1 &
python -u v6alone.py e6w > runs/run_alone_e6w.log 2>&1 &
wait
echo ALLDONE >> $L
