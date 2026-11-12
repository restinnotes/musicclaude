cd /d/musicclaude/_thread_evo_20261019
fx() { python round79_fix.py $1 r79d --center --max 6 --route $2 > evaluations/r79/fix_$1.log 2>&1; }
fx r79f gpt3s & fx r79g gpt4s & wait
for t in r79f r79g; do grep -c "+ None" evaluations/r79/fix_$t.log; done
ts() { THREAD_ROUTE=$2 python round37_fair.py $1 r79d > evaluations/r79/fair_$1.log 2>&1; THREAD_ROUTE=$2 python round37_floor.py $1 r79d > evaluations/r79/floor_$1.log 2>&1; }
ts r79f gpt4s & ts r79g gpt4s & R79_BASE=r79d python round79_measure.py run2 r79f r79g > evaluations/r79/m_r79fg.log 2>&1 & wait
python -c "
import sys;sys.stdout.reconfigure(encoding='utf-8')
import round37_fair as R, screen_flow as F
F.configure()
for t in ('r79f','r79g'):
    d=R.summary(t,'r79d'); print(t,'vs r79d',d['pass'],d['wins'],d['complete'],d['no_regress'],d['net_sums'])"
for t in r79f r79g; do grep -E "^coverage|^alone" evaluations/r79/floor_$t.log | cut -c1-120; done
R79_BASE=r79d python round79_measure.py sum2 r79f r79g | grep 和
