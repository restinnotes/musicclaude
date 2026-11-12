export THREAD_ROUTE=mimic MG_SLOTS=4 HUMAN_WRITER=argon LO_V=2 FIX_LEN=0
python -u v6human.py fixopen h15 h16 > runs/run_h16.log 2>&1
python -u v6fix.py blind h16 h13 > runs/run_blind_h16.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h16 h13 > runs/run_blind_h16_r2.log 2>&1 &
wait
python -u v6human.py fixlost h13 h16 h17 >> runs/run_h16.log 2>&1
export LO_TAG=h17
python -u lang_open.py run --gem > runs/run_lo_h17_gem.log 2>&1 &
python -u lang_open.py run > runs/run_lo_h17.log 2>&1 &
python -u v6cov.py h17 > runs/run_cov_h17.log 2>&1 &
python -u v6alone.py h17 > runs/run_alone_h17.log 2>&1 &
python -u v6check.py check h17 > runs/run_chk_h17.log 2>&1 &
python -u v6fix.py blind h17 h13 > runs/run_blind_h17.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h17 h13 > runs/run_blind_h17_r2.log 2>&1 &
wait
echo ALLDONE >> runs/run_h16.log
