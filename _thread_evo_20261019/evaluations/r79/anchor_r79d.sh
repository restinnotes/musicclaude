cd /d/musicclaude/_thread_evo_20261019
THREAD_ROUTE=gpt4s python round37_fair.py r79d r49b > evaluations/r79/fair_r79d_r49b.log 2>&1 &
THREAD_ROUTE=gpt3s python round37_floor.py r79d r49b > evaluations/r79/floor_r79d_r49b.log 2>&1 &
R79_BASE=r49b python round79_measure.py run2 r79d > evaluations/r79/m_r79d_r49b.log 2>&1 &
wait
python -c "
import sys;sys.stdout.reconfigure(encoding='utf-8')
import round37_fair as R, screen_flow as F
F.configure(); d=R.summary('r79d','r49b'); print('r79d vs r49b',d['pass'],d['wins'],d['complete'],d['no_regress'],d['net_sums'])
for r in d['rows']: print('  ',r['w'],r['j'],r['seat'],'新胜' if r['new_win'] else '旧胜','不退步' if r['no_regress'] else '退步',r['net'])"
grep -E "^coverage|^alone" evaluations/r79/floor_r79d_r49b.log | cut -c1-150
R79_BASE=r49b python round79_measure.py sum2 r79d | grep 和
