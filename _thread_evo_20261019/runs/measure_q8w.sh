unset THREAD_ROUTE; export LO_V=2
until grep -q "ln3_op61_r3': True" runs/run_src3.log 2>/dev/null || grep -q "DOWNSTREAM" runs/run_src3.log; do sleep 30; done
python -u v6cov.py q8w > runs/run_cov_q8w.log 2>&1
LO_TAG=q8w python -u lang_open.py run --gem > runs/run_lo_q8w_gem.log 2>&1 &
python -u v6fix.py blind q8w h23 > runs/run_blind_q8w_h23.log 2>&1
BLIND_REP=2 python -u v6fix.py blind q8w h23 > runs/run_blind_q8w_h23_r2.log 2>&1
wait; echo Q8W_DONE >> runs/run_cov_q8w.log
