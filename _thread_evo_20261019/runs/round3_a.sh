# 11-02 round 3: writer layers revised by their proposers, on Q1's routes. usage: bash runs/round3_a.sh <scheme> <tag>
export JV=2 MG_ATTEMPTS=5
s=$1; t=$2; L=runs/run_round1.log
python -u pipe.py run schemes/$s.json $t > runs/run_sc_$t.log 2>&1 || python -u pipe.py run schemes/$s.json $t >> runs/run_sc_$t.log 2>&1
rc=$?; echo "$t GEN EXIT $rc $(date)" >> $L
grep -a "字数" runs/run_sc_$t.log | cut -c1-60
if [ $rc -eq 0 ]; then bash runs/meas.sh $t m6w > /dev/null 2>&1; fi
python verdict.py $t | cut -c1-260
grep -a "说清" runs/run_cov2_$t.log | cut -c1-100
grep -a "段成立" runs/run_alone2_$t.log | cut -c1-90
