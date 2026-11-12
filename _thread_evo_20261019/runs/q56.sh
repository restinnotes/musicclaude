run() { python -u pipe.py run schemes/$1.json $2 > runs/run_sc_$2.log 2>&1 || python -u pipe.py run schemes/$1.json $2 >> runs/run_sc_$2.log 2>&1; rc=$?; echo "$2 GEN EXIT $rc $(date)" >> runs/run_round1.log; [ $rc -eq 0 ] && bash runs/meas.sh $2 m6w >/dev/null 2>&1; }
run Q5 qh &
run Q6 qi &
wait
