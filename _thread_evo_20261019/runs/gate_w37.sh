while ps -ef | grep -v grep | grep -q "v6check.py check w37"; do sleep 30; done
export GPT3_GAP=90
python -u gate_v6.py w37 > runs/run_gate_w37.log 2>&1
echo GATEDONE >> runs/run_gate_w37.log
