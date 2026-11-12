"""11-08 迭代准则 I01（DAG2）：开放评审读主线成品，按大众版标准 7 条找问题（只找问题，不打分）。python r3/open_review.py TAG → r3/s24/open_{w}_{j}_{TAG}.json"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blend, prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')
OPEN = """你是评审。下面是一首钢琴曲大众版“边听边看”视频的屏幕稿：普通观众边听边扫，每段屏幕只停留写明的秒数。话里【】中的字放大加亮；“感受”是小字短语；标“到时出现”的只在那几小节出现。

请按下面的标准，只找问题（不打分、不夸），每条问题写清在哪一段、原文、为什么是问题、建议怎么改；再写跨段反复出现的问题。没问题的标准不用硬找。

【标准】
{STD}

只输出 JSON：{"issues":[{"sec":"S05","std":"标准编号 1–7","quote":"原文","why":"一句","better":"建议"}],"cumulative":[{"std":"…","phenomenon":"…","evidence":["S05「…」"],"severity":"严重|中等|轻微"}]}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(OPEN, 'open_review.py')
tag = sys.argv[1]
def one(a):
    w, j, m = a; p = S/f'open_{w}_{j}_{tag}.json'
    if p.exists(): return
    msg = OPEN.replace('{STD}', blend.DAGSTD).replace('{SCREEN}', view_text(w, tag))
    for k in range(3):
        ans = call(f'pub24OR_{w}_{j}_{tag}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-open')
        try: r = parse(ans); assert 'issues' in r; wr(p, r); print(w, j, len(r['issues']), [(c.get('phenomenon', '')[:40], c.get('severity')) for c in r.get('cumulative') or []], flush=True); return
        except Exception as ex: print('不合格', w, j, repr(ex)[:120], flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j, m) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
