"""11-08 晚 校准用的人造对照（两位顾问建议的已知答案测试）：在比较对象上挑十几块感受，每块后面加一个“意思完全相同、只是换个比喻”的说法，不加任何新信息。
新盲比 vs3 量得对的话：fine 应该平，concise 应该原版赢；新覆盖测法 cov3 两版应该一样。
python r3/dup.py SRC NEW
"""
import copy, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, rd, wr, call, parse, G56, WORKS, to_script

DUP = """下面是一份屏幕稿里的一些感受短语，每条有编号。请为每条写一个“意思完全相同、只是换了比喻或说法”的短语：同一个画面、同一种身体感觉、同一个情绪质地，不多出任何新的画面、原因、转折或心里话，长度和原句差不多。这是用来测试评委的对照材料，要的就是纯粹的重复说法。

只输出 JSON：{"items":[{"id":"编号","dup":"换个说法的短语"}]}

{ITEMS}
"""
prompt_lint.lint(DUP, 'dup.py')


def one(w, src, new):
    p = S/f'screen_{w}_{new}.json'
    if p.exists(): return
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); pick = {}
    for s in scr['sections']:
        for k, x in enumerate(s['rows'], 1):
            if x['kind'] == 'feel' and x['items'] and len(pick) < 16 and k % 2 == 0:
                pick[f"{s['sec']}-r{k}"] = x
    txt = '\n'.join(f"[{rid}] {x['items'][0]['text']}" for rid, x in pick.items())
    r = {i['id']: i['dup'].strip().rstrip('，。、；') for i in parse(call(f'pub24DUP_{w}_{new}', DUP.replace('{ITEMS}', txt), G56, 'gpt3s', 'public24-dup'))['items'] if i.get('dup')}
    n = 0
    for rid, x in pick.items():
        if r.get(rid): x['items'].insert(1, dict(x['items'][0], text=r[rid])); n += 1
    wr(p, scr); to_script(w, new, scr); print(w, new, '加了', n, '个重复说法', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for w in WORKS: one(w, sys.argv[1], sys.argv[2])
