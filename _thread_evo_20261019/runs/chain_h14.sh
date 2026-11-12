export THREAD_ROUTE=mimic MG_SLOTS=4 HUMAN_WRITER=argon
python -u v6human.py fixopen h13 h14 > runs/run_h14_write.log 2>&1
export LO_TAG=h14
python -u lang_open.py run --gem > runs/run_lo_h14_gem.log 2>&1 &
python -u lang_open.py run > runs/run_lo_h14.log 2>&1 &
python -u v6cov.py h14 > runs/run_cov_h14.log 2>&1 &
python -u v6alone.py h14 > runs/run_alone_h14.log 2>&1 &
python -u v6check.py check h14 > runs/run_chk_h14.log 2>&1 &
python -u v6fix.py blind h14 h13 > runs/run_blind_h14.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h14 h13 > runs/run_blind_h14_r2.log 2>&1 &
wait
LO_TAG=h14 python lang_open.py report > runs/run_lo_h14_report.log 2>&1
echo ALLDONE >> runs/run_h14_write.log
