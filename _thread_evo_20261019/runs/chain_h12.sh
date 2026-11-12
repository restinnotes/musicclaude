export THREAD_ROUTE=mimic MG_SLOTS=4 HUMAN_WRITER=argon
python -u v6human.py fixlost b0 h11 h12 > runs/run_hfix_h12.log 2>&1
t=h12
python -u v6human.py find $t > runs/run_hfind_$t.log 2>&1 &
python -u v6alone.py $t > runs/run_alone_$t.log 2>&1 &
python -u v6cov.py $t > runs/run_cov_$t.log 2>&1 &
python -u v6check.py check $t > runs/run_chk_$t.log 2>&1 &
python -u v6fix.py blind $t b0 > runs/run_blind_$t.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind $t b0 > runs/run_blind_${t}_r2.log 2>&1 &
BLIND_REP=3 python -u v6fix.py blind $t b0 > runs/run_blind_${t}_r3.log 2>&1 &
wait
echo ALLDONE > runs/run_h12_done.log
