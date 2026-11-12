export GPT3_GAP=90
python -u gate_v6.py w38 > runs/run_gate_w38.log 2>&1
echo GATEDONE >> runs/run_gate_w38.log
