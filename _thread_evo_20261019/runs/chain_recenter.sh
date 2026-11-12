set -e
unset THREAD_ROUTE; export LO_V=2
L=runs/run_recenter.log; : > $L
python -u v6recenter.py h23 h23c >> $L 2>&1
echo MEASURE >> $L
python -u v6cov.py h23c > runs/run_cov_h23c.log 2>&1 &
LO_TAG=h23c python -u lang_open.py run --gem > runs/run_lo_h23c_gem.log 2>&1 &
python -u v6fix.py blind h23c h23 > runs/run_blind_h23c_h23.log 2>&1
BLIND_REP=2 python -u v6fix.py blind h23c h23 > runs/run_blind_h23c_h23_r2.log 2>&1
python -u v6alone.py h23c > runs/run_alone_h23c.log 2>&1
wait
echo ALLDONE >> $L
