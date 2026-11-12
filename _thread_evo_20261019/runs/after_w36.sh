while ps -ef | grep -q "[v]6clean.py w35 w36"; do sleep 30; done
export GPT3_GAP=90
python -u v6clean.py w35 w36 op61:S13 op60:S14 > runs/run_clean_w36b.log 2>&1
python -u v6cov.py w36 > runs/run_cov_w36.log 2>&1 &
python -u v6alone.py w36 > runs/run_alone_w36.log 2>&1 &
python -u v6check.py check w36 > runs/run_chk_w36.log 2>&1 &
python -u v6fix.py blind w36 > runs/run_blind_w36.log 2>&1 &
wait; echo ALLDONE >> runs/run_cov_w36.log
