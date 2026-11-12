export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6grow.py f6 > runs/run_grow_f6.log 2>&1 &
python -u v6cov.py f6 > runs/run_cov_f6.log 2>&1 &
python -u v6alone.py f6 > runs/run_alone_f6.log 2>&1 &
python -u v6check.py check f6 > runs/run_chk_f6.log 2>&1 &
python -u v6fix.py blind f6 > runs/run_blind_f6.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind f6 > runs/run_blind_f6_r2.log 2>&1 &
wait
python v6weave.py f6 > runs/run_weave_f6.log 2>&1
echo ALLDONE >> runs/run_weave_f6.log
