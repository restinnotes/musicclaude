cd /d/musicclaude/_thread_evo_20261019
t1() { THREAD_ROUTE=$2 python round37_fair.py $1 r78a > evaluations/r79/fair_$1.log 2>&1; THREAD_ROUTE=$2 python round37_floor.py $1 r78a > evaluations/r79/floor_$1.log 2>&1; }
t1 r79a gpt3s & t1 r79b gpt4s &
python round79_measure.py run2 r79a r79b > evaluations/r79/m_r79ab.log 2>&1 &
wait
for t in r79a r79b; do head -1 evaluations/r79/fair_$t.log | cut -c1-200; grep -v "^\[" evaluations/r79/fair_$t.log | sed -n 2,9p | cut -c1-120; grep -E "^coverage|^alone" evaluations/r79/floor_$t.log | cut -c1-200; done
python round79_measure.py sum2 r79a r79b
