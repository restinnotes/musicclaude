export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6human.py find b0 > runs/run_hfind_b0.log 2>&1
HUMAN_MODE=3 python -u v6human.py write b0 h3 > runs/run_hwrite_h3.log 2>&1 &
HUMAN_MODE=4 python -u v6human.py write b0 h4 > runs/run_hwrite_h4.log 2>&1 &
wait
echo ALLDONE >> runs/run_hwrite_h4.log
