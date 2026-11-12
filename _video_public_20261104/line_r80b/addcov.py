"""11-08 补覆盖层：在一版扫读和其余盲比分项都赢、只差整屏珠子覆盖的屏幕稿上，只补被评委判为没留住的珠子要点，补成短短语，其余一字不动。
来由：K3 盲比七项全赢、没有走样，只差覆盖（op60 0.60 对 0.67，op61 0.71 对 0.75）；交回顾问让写手自己补覆盖（K3b、K3c），写手一补就把整屏写到旧视频的两倍，不啰嗦 0:8。
python addcov.py SRC NEW
"""
import copy, json, os, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
os.environ['PUB_BC_ALL'] = '1'
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, WORKS, JUDGES, to_script

ADD = """下面是一首钢琴曲大众版“边听边看”视频屏幕稿里的几段。观众边听边扫，每段只停留写明的秒数。每段有几行：“话”是大字的一句；“感受”是小字短语，[ ] 里是编号。
评委说这几段丢了一些珠子（听的人此刻的感受）里的具体东西，列在每段后面。请只做一件事：把其中最值得留下的补回去。

怎么补：
1. 补成短短语，一块一个画面、一种身体感觉或一句心里话，口语，不是书面词，也不是把一句话切成两半；不加标点。
2. 优先补具体的画面、身体感觉、比喻、心里话；只剩情绪或纯写音乐本身的，不补。和屏幕上已有的意思相近的，不补。
3. 一段补几块按停留秒数定：停留短的段少补，宁可不补也不要让这一屏扫不完。
4. 只能加，不改、不删已有的任何字。补的短语放进已有的某个感受行（写那一行的编号），挨着和它同一颗珠子的短语。
5. 珠子里的比喻就当比喻写，不写成这个人真的发生的事。

只输出 JSON：{"add":[{"sec":"S05","row":"S05-r2","text":"短语","from":"S05-B1"}]}

{SECS}
"""
prompt_lint.lint(ADD, 'addcov.py')


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json'))
    pts = {q['id']: (s['sec'], b['id'], q['text']) for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads'] for q in b['points']}
    c = Counter()
    for j in JUDGES:
        for it in rd(S/f'beadcovA_{w}_{j}_{src}.json')['items']:
            if it.get('verdict') != '留住': c[it['id']] += 1
    lost = {}
    for k, n in c.items():
        if n >= 2 and k in pts: lost.setdefault(pts[k][0], []).append(k)
    import pub16
    win = pub16.windows(w); txt = []; rows = {}
    for s in scr['sections']:
        if s['sec'] not in lost: continue
        txt.append(f"\n### {s['sec']}（停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for k, x in enumerate(s['rows'], 1):
            if x['kind'] == 'line': txt.append('话：' + x['text'])
            else:
                rid = f"{s['sec']}-r{k}"; rows[rid] = x; txt.append(f"感受 [{rid}]：" + ' / '.join(i['text'] for i in x['items']))
        txt.append('丢了的：' + '；'.join(f"（{pts[q][1]}）{pts[q][2]}" for q in lost[s['sec']]))
    msg = ADD.replace('{SECS}', '\n'.join(txt))
    for t in range(3):
        ans = call(f'pub24AC_{w}_{new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-addcov')
        try:
            r = parse(ans); n = 0
            for x in r.get('add') or []:
                row = rows.get(x.get('row')); tx = (x.get('text') or '').strip().rstrip('，。、；')
                if row is None or not tx: continue
                bead = x.get('from') or (row['items'][0]['bead'] if row['items'] else '')
                k = max([q for q, i in enumerate(row['items']) if i.get('bead') == bead] or [len(row['items'])-1])
                row['items'].insert(k+1, {'text': tx, 'bead': bead, 'bars': ''}); n += 1
            wr(p, scr); to_script(w, new, scr)
            print(w, new, '补了', n, '块；丢了的要点', sum(map(len, lost.values())), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, new = sys.argv[1], sys.argv[2]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, new) for w in WORKS])), flush=True)
