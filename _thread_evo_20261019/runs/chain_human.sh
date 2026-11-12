true
export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6human.py find w38 f8 g1 > runs/run_hfind_base.log 2>&1
python -u v6human.py write g1 h1 > runs/run_hwrite_h1.log 2>&1
python -u v6human.py find h1 > runs/run_hfind_h1.log 2>&1 &
python -u v6alone.py h1 > runs/run_alone_h1.log 2>&1 &
python -u v6cov.py h1 > runs/run_cov_h1.log 2>&1 &
python -u v6check.py check h1 > runs/run_chk_h1.log 2>&1 &
python -u v6drift.py h1 > runs/run_drift_h1.log 2>&1 &
python -u v6fix.py blind h1 > runs/run_blind_h1.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h1 > runs/run_blind_h1_r2.log 2>&1 &
wait
python v6weave.py h1 > runs/run_weave_h1.log 2>&1
echo ALLDONE >> runs/run_weave_h1.log
