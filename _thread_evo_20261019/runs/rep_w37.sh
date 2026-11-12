export GPT3_GAP=90
for r in 2 3 4; do BLIND_REP=$r python -u v6fix.py blind w37 > runs/run_blind_w37_r$r.log 2>&1 & done
wait; echo ALLDONE >> runs/run_blind_w37_r4.log
