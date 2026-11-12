cd /d/musicclaude/_thread_evo_20261019
THREAD_ROUTE=gpt4s python round37_fair.py r79a r78a > evaluations/r79/fair_r79a.log 2>&1 &
THREAD_ROUTE=gpt4s python round79_measure.py run2 r79a r79b > evaluations/r79/m_r79ab2.log 2>&1 &
wait
python -c "
import sys;sys.stdout.reconfigure(encoding='utf-8')
import round37_fair as R, screen_flow as F
F.configure()
for t in ('r79a','r79b'):
    d=R.summary(t,'r78a'); print(t,d['pass'],d['wins'],d['complete'],d['no_regress'],d['net_sums'])
    for r in d['rows']: print('  ',r['w'],r['j'],r['seat'],'新胜' if r['new_win'] else '旧胜','不退步' if r['no_regress'] else '退步',r['net'])"
python round79_measure.py sum2 r79a r79b | grep 和
