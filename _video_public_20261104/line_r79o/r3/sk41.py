"""11-12 夜 L41 骨架诊断（不进主线）：用户：“我们只是不让他编具体的事情而已吧……有没有可能其实还有能用的东西 只是他现在没搜到……可以让argon来试试”。
L40sk 的骨架十四段里十三段写“没有具体前史可以支撑”。写线提示词的禁令（不新增事件、人物、对白、物件、地点、场景、前史）比用户的规矩（不编具体的事来推动转折；允许一个从头到尾不变的处境）更严。
这里只改骨架：放回一份全篇不变、泛指的处境（givens），每段的理由从它的不同侧面里找；GPT-6 和 Argon 各写 3 条路线。先只比骨架，不往下写线。
python r3/sk41.py → r3/s24/sk41_{作品}_{g6|argon}.json"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019')
os.environ.setdefault('PUB_SRC', 'r2e')
import evo, prompt_lint
from pub24 import S, call, parse, G6, WORKS
sys.stdout.reconfigure(encoding='utf-8')
RUNS = Path('D:/musicclaude/_thread_evo_20261019/runs'); SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes')
OLD = '- 不新增外部事件、人物、对白、物件、地点、场景或前史。'
NEW = '''- 不编具体的事：不得新增某一次具体发生的事件、对白、物件、地点、场景，也不得让别人做出新的具体举动来推动变化。
- 但这个人不是凭空的。在最前面写清一份从头到尾不变的处境（givens）：他和这件事里的人或事是什么关系、平常怎样相处或相待、他一向相信什么、想要什么、手里已经有什么、怕失去什么、他自己是个怎样的人、在这类事上一向怎么做。它们是泛指的、一直如此的状况，不是某一天发生的某件事；从 Center 和这首曲子的整体走向自然推出来；全篇不变，写完之后不得再往里加。条目要多、要具体到能当理由用、彼此不同。
- TARGETS 里 forbidden_imports 禁的是把听感里的画面和想象情节当成真事；这份不变的处境不在禁止之列。'''
OLD2 = '- 理由要具体到只属于这一段'
NEW2 = '''- 理由优先从 givens 的不同侧面里找：同一份处境，在不同的段显出不同的一面，或者几条处境在这一段第一次碰到一起。每段在 uses 里标出用了 givens 的哪几条；全篇尽量把 givens 都用到，不要十几段只靠其中两三条。
- 理由要具体到只属于这一段'''
OLD3 = '- segments：严格按照'
NEW3 = '- givens：全篇不变的处境，每条 {"id":"G1","text":"一句普通话"}。\n- segments：严格按照'
OLD4 = '  - unexplained：'
NEW4 = '  - uses：这一段的理由用到的 givens 编号。\n  - unexplained：'


def prompt(w):
    t = (RUNS/f'scL40sk_{w}_A1'/'prompt.txt').read_text(encoding='utf-8')   # L40sk 实发的骨架提示词（已填好段落、Center、体验性质）
    for a, b in ((OLD, NEW), (OLD2, NEW2), (OLD3, NEW3), (OLD4, NEW4)):
        assert a in t, a; t = t.replace(a, b, 1)
    return t


def one(a):
    w, who = a; p = S/f'sk41_{w}_{who}.json'
    if p.exists(): return
    msg = prompt(w); r = None
    for k in range(3):
        try:
            rid = f'sk41_{w}_{who}' + ('' if not k else f'_r{k}')
            raw = evo.call_argon_direct(rid, msg, meta={'stage': 'sk41'}) if who == 'argon' else call(rid, msg, G6, 'gpt3s', 'sk41')
            r = parse(raw or ''); rs = r.get('routes') or r.get('candidates') or r.get('items'); assert rs and rs[0].get('segments'); break
        except Exception as ex: print('不合格', w, who, repr(ex)[:200], flush=True); r = None
    if not r: return
    p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')


def show():
    for w in WORKS:
        for who in ('g6', 'argon'):
            p = S/f'sk41_{w}_{who}.json'
            if not p.exists(): print(w, who, '没出来'); continue
            r = json.loads(p.read_text(encoding='utf-8')); rs = r.get('routes') or r.get('candidates') or r.get('items')
            for x in rs:
                g = x.get('givens') or r.get('givens') or []; used = {u for s in x['segments'] for u in (s.get('uses') or [])}
                print(w, who, x.get('route_id'), '｜处境', len(g), '条，用到', len(used), '｜说不清的段', sum(bool(s.get('unexplained')) for s in x['segments']), '/', len(x['segments']), '｜', (x.get('situation') or '')[:80])


if __name__ == '__main__':
    t = re.sub(r'\{[A-Z_]+\}', '', NEW + NEW2 + NEW3 + NEW4); print('泛化检查：', prompt_lint.find(t) or '过', flush=True)
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, who) for w in WORKS for who in ('g6', 'argon')]))
    show()
