export THREAD_ROUTE=mimic MG_SLOTS=3
HUMAN_FULL=1 python -u v6human.py write g1 h2 > runs/run_hwrite_h2.log 2>&1
python -u v6human.py find h2 > runs/run_hfind_h2.log 2>&1 &
python -u v6alone.py h2 > runs/run_alone_h2.log 2>&1 &
python -u v6cov.py h2 > runs/run_cov_h2.log 2>&1 &
python -u v6check.py check h2 > runs/run_chk_h2.log 2>&1 &
python -u v6fix.py blind h2 > runs/run_blind_h2.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h2 > runs/run_blind_h2_r2.log 2>&1 &
wait
python v6weave.py h2 > runs/run_weave_h2.log 2>&1
echo ALLDONE >> runs/run_weave_h2.log
