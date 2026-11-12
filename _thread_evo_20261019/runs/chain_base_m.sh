set -e
unset THREAD_ROUTE
export MG_ATTEMPTS=5 TAG=m LO_V=2 HUMAN_WRITER=argon FIX_LEN=0 WORD_EDITORS=gem,argon GLOSS_TAG=m0 SRCV=4
L=runs/run_base_m.log; echo RESTART >> $L
# baseline (SRCV=4): current DAG + 10-23 draft fix only, new Center
python -u dag_src3.py lines >> $L 2>&1
python -u dag_src3.py judge >> $L 2>&1
python -u dag_src3.py graph >> $L 2>&1
python -u dag_src3.py import >> $L 2>&1
echo DOWNSTREAM >> $L
python -u v6gen.py gloss >> $L 2>&1
WRITE_PLAIN=1 python -u v6gen.py write m0 m1 >> $L 2>&1
LO_TAG=m1 python -u lang_open.py run >> $L 2>&1
LO_TAG=m1 python -u lang_open.py run --gem >> $L 2>&1
python -u v6human.py fixopen m1 m2 >> $L 2>&1
python -u v6cov.py m2 >> $L 2>&1
# N10c two rounds
boost() { python -u v6boost.py fix $1 $2 >> $L 2>&1; python -u v6cov.py $2 >> $L 2>&1; python -u v6boost.py keep $1 $2 $3 >> $L 2>&1; python -u v6cov.py $3 >> $L 2>&1; }
boost m2 m3 m3k
boost m3k m4 m4k
# language round: N09 -> N09c -> N10g -> N09w
LO_TAG=m4k python -u lang_open.py run >> $L 2>&1
LO_TAG=m4k python -u lang_open.py run --gem >> $L 2>&1
python -u v6human.py fixopen m4k m5 >> $L 2>&1; python -u v6cov.py m5 >> $L 2>&1
python -u v6guard.py fix m4k m5 m5g >> $L 2>&1; python -u v6cov.py m5g >> $L 2>&1
python -u v6guard.py revert m4k m5g m5k >> $L 2>&1
python -u v6word.py m5k m6w >> $L 2>&1
echo MEASURE >> $L
# measure the baseline: coverage, standalone, open review (problem finding only)
python -u v6cov.py m6w > runs/run_cov_m6w.log 2>&1 &
LO_TAG=m6w python -u lang_open.py run > runs/run_lo_m6w.log 2>&1 &
LO_TAG=m6w python -u lang_open.py run --gem > runs/run_lo_m6w_gem.log 2>&1 &
python -u v6alone.py m6w > runs/run_alone_m6w.log 2>&1 &
wait
echo ALLDONE >> $L
