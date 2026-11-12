export THREAD_ROUTE=mimic MG_SLOTS=3 HUMAN_WRITER=argon
HUMAN_MODE=3 python -u v6human.py write b0 h7 > runs/run_hwrite_h7.log 2>&1
HUMAN_MODE=4 python -u v6human.py write b0 h8 > runs/run_hwrite_h8.log 2>&1
echo ALLDONE >> runs/run_hwrite_h8.log
