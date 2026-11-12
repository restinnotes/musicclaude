cd /d/musicclaude/_thread_evo_20261019
fx() { python round79_fix.py $1 r79b --vs r78a --tight --max 6 --route $2 > evaluations/r79/fix_$1.log 2>&1; }
fx r79d gpt3s & fx r79e gpt4s & wait
for t in r79d r79e; do grep -E "None|^## " evaluations/r79/fix_$t.log | head -5; done
ts() { THREAD_ROUTE=$2 python round37_fair.py $1 r78a > evaluations/r79/fair_$1.log 2>&1; THREAD_ROUTE=$2 python round37_floor.py $1 r78a > evaluations/r79/floor_$1.log 2>&1; }
ts r79d gpt4s & ts r79e gpt4s & python round79_measure.py run2 r79d r79e > evaluations/r79/m_r79de.log 2>&1 & wait
python -c "
import sys;sys.stdout.reconfigure(encoding='utf-8')
import round37_fair as R, screen_flow as F
F.configure()
for t in ('r79d','r79e'):
    d=R.summary(t,'r78a'); print(t,d['pass'],d['wins'],d['complete'],d['no_regress'],d['net_sums'])
    for r in d['rows']: print('  ',r['w'],r['j'],r['seat'],'新胜' if r['new_win'] else '旧胜','不退步' if r['no_regress'] else '退步',r['net'])"
for t in r79d r79e; do grep -E "^coverage|^alone" evaluations/r79/floor_$t.log | cut -c1-120; done
python round79_measure.py sum2 r79d r79e | grep 和
