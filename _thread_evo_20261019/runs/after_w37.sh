export GPT3_GAP=90
python -u v6cov.py w37 > runs/run_cov_w37.log 2>&1 &
python -u v6alone.py w37 > runs/run_alone_w37.log 2>&1 &
python -u v6check.py check w37 > runs/run_chk_w37.log 2>&1 &
python -u v6fix.py blind w37 > runs/run_blind_w37.log 2>&1 &
wait; echo ALLDONE >> runs/run_cov_w37.log
