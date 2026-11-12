# 11-02 round 3: hand qg/qh/qi results back to whoever proposed that writer layer; each returns revised prompts (or gives up)
export JV=2 MG_ATTEMPTS=5
L=runs/run_round1.log
( python -u advisor_followup2.py Q5 qh g6  Q7 > runs/run_fu_qh.log 2>&1; echo "fu qh DONE $(date)" >> $L ) &
( python -u advisor_followup2.py Q6 qi gem Q8 > runs/run_fu_qi.log 2>&1; echo "fu qi DONE $(date)" >> $L ) &
wait
echo "round3 fu all done $(date)" >> $L
