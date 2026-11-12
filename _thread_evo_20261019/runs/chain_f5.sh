export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6cov.py f5 > runs/run_cov_f5.log 2>&1 &
python -u v6alone.py f5 > runs/run_alone_f5.log 2>&1 &
python -u v6check.py check f5 > runs/run_chk_f5.log 2>&1 &
python -u v6fix.py blind f5 > runs/run_blind_f5.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind f5 > runs/run_blind_f5_r2.log 2>&1 &
wait
python v6weave.py f5 > runs/run_weave_f5.log 2>&1
echo ALLDONE >> runs/run_weave_f5.log
