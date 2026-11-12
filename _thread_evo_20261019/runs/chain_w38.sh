export GPT3_GAP=90
python -u v6point.py w37 w38 > runs/run_point_w38.log 2>&1
python -u v6cov.py w38 > runs/run_cov_w38.log 2>&1 &
python -u v6alone.py w38 > runs/run_alone_w38.log 2>&1 &
python -u v6check.py check w38 > runs/run_chk_w38.log 2>&1 &
python -u v6fix.py blind w38 > runs/run_blind_w38.log 2>&1 &
for r in 2 3 4; do BLIND_REP=$r python -u v6fix.py blind w38 > runs/run_blind_w38_r$r.log 2>&1 & done
wait
echo MEASURED >> runs/run_point_w38.log
