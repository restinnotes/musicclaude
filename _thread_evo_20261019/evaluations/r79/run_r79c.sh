cd /d/musicclaude/_thread_evo_20261019
python round79_fix.py r79c r79b --vs r78a --route gpt4s > evaluations/r79/fix_r79c.log 2>&1
grep -v "^\[sc" evaluations/r79/fix_r79c.log | head -40 | cut -c1-200
THREAD_ROUTE=gpt4s python round37_fair.py r79c r78a > evaluations/r79/fair_r79c.log 2>&1 &
THREAD_ROUTE=gpt4s python round37_floor.py r79c r78a > evaluations/r79/floor_r79c.log 2>&1 &
python round79_measure.py run2 r79c > evaluations/r79/m_r79c.log 2>&1 &
wait
python -c "
import sys;sys.stdout.reconfigure(encoding='utf-8')
import round37_fair as R, screen_flow as F
F.configure(); d=R.summary('r79c','r78a'); print('r79c',d['pass'],d['wins'],d['complete'],d['no_regress'],d['net_sums'])
for r in d['rows']: print('  ',r['w'],r['j'],r['seat'],'新胜' if r['new_win'] else '旧胜','不退步' if r['no_regress'] else '退步',r['net'])"
grep -E "^coverage|^alone" evaluations/r79/floor_r79c.log | cut -c1-150
python round79_measure.py sum2 r79c | grep 和
