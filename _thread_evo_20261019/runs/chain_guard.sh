set -e
unset THREAD_ROUTE
export HUMAN_WRITER=argon LO_V=2
python -u v6cov.py h13g h17g > runs/run_guard.log 2>&1
python -u v6guard.py fix h13g h17g h18 >> runs/run_guard.log 2>&1
python -u v6cov.py h18 >> runs/run_guard.log 2>&1
python -u v6guard.py revert h13g h18 h18k >> runs/run_guard.log 2>&1
python -u v6cov.py h18k >> runs/run_guard.log 2>&1
python -u v6alone.py h18k > runs/run_alone_h18k.log 2>&1 &
python -u v6fix.py blind h18k h13 > runs/run_blind_h18k.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind h18k h13 > runs/run_blind_h18k_r2.log 2>&1 &
LO_TAG=h18k python -u lang_open.py run > runs/run_lo_h18k.log 2>&1 &
LO_TAG=h18k python -u lang_open.py run --gem > runs/run_lo_h18k_gem.log 2>&1 &
wait
echo ALLDONE >> runs/run_guard.log
