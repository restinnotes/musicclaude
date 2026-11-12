export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6cov.py f7 > runs/run_cov_f7.log 2>&1 &
python -u v6alone.py f7 > runs/run_alone_f7.log 2>&1 &
python -u v6check.py check f7 > runs/run_chk_f7.log 2>&1 &
wait
python v6weave.py f7 > runs/run_weave_f7.log 2>&1
echo ALLDONE >> runs/run_weave_f7.log
