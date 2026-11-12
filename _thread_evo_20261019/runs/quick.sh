# 11-02 quick screen without open review (open review only when a version looks worth reading closely). usage: bash runs/quick.sh <scheme> <tag>
export JV=2 MG_ATTEMPTS=5
s=$1; t=$2; L=runs/run_round1.log
python -u pipe.py run schemes/$s.json $t > runs/run_sc_$t.log 2>&1 || python -u pipe.py run schemes/$s.json $t >> runs/run_sc_$t.log 2>&1
rc=$?; echo "$t GEN EXIT $rc $(date)" >> $L
grep -a "字数" runs/run_sc_$t.log | cut -c1-30
if [ $rc -eq 0 ]; then
  python -u v6cov.py $t > runs/run_cov2_$t.log 2>&1 &
  python -u v6alone.py $t > runs/run_alone2_$t.log 2>&1 &
  python -u v6fix.py blind $t m6w > runs/run_blind2_$t.log 2>&1 &
  wait
fi
echo "$t QUICK DONE $(date)" >> $L
python verdict.py $t | cut -c1-260
grep -a "说清" runs/run_cov2_$t.log | cut -c1-90
grep -a "段成立" runs/run_alone2_$t.log | cut -c1-90
