"""11-09 语病微修：绝对尺度验收里报的“人话”类轻微问题（量词搭配不对、成分残缺、删减后留下的不通），每处只许改最多 4 个字，不许变长超过 2 字，不许改意思。
python fixlang.py SRC NEW     问题取自 r3/s24/openA2_{作品}_*_{SRC}_run*.json 里标准 4 的问题
"""
import copy, difflib, glob, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script

FIX = """下面是一首钢琴曲视频屏幕上的几处文字，评委说读起来有小毛病（例如量词搭配不对、少了成分、删减后留下的不通顺）。每处给了这一行的全文和评委的说法。
请只修语病：每处最多改动四个字，不改意思，不加原来没有的内容，不删画面和心里话；评委说的如果不是语病（只是风格偏好、建议删减、嫌长），原样照抄、不改。

只输出 JSON：{"items":[{"id":"编号","text":"修好的这一行全文"}]}

{ITEMS}
"""
prompt_lint.lint(FIX, 'fixlang.py')


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); rows = []
    for s in scr['sections']:
        for x in s['rows']:
            for it in ([x] if x['kind'] == 'line' else x['items']): rows.append((s['sec'], it))
    todo = {}
    for f in sorted(glob.glob(str(S/f'openA2_{w}_*_{src}_run*.json'))):
        for x in rd(f).get('issues') or []:
            if str(x.get('std')).strip() != '4' or x.get('severity') not in ('轻微', '中等'): continue
            q = (x.get('quote') or '').replace('【', '').replace('】', '').split(' / ')[0].strip()
            if len(q) < 4: continue
            for sec, it in rows:
                if q[:12] in it['text']:
                    k = f"{sec}-{id(it)}"; todo.setdefault(k, [it, []])[1].append(x.get('why') or ''); break
    if not todo: wr(p, scr); to_script(w, new, scr); print(w, new, '没有语病类问题', flush=True); return True
    NL = chr(10); ids = {}; txt = []
    for n, (k, (it, whys)) in enumerate(todo.items(), 1):
        ids[str(n)] = it; txt.append(f"[{n}] 全文：{it['text']}{NL}    评委：{'；'.join(whys)[:300]}")
    r = {}
    for t in range(3):
        try: r = {str(x['id']): (x.get('text') or '').strip() for x in parse(call(f'pub24FL_{w}_{new}' + ('' if not t else f'_r{t}'), FIX.replace('{ITEMS}', NL.join(txt)), G6, 'gpt3s', 'public24-fixlang'))['items']}; break
        except Exception as ex: print('不合格', w, new, repr(ex)[:150], flush=True)
    done = bad = 0
    for i, it in ids.items():
        nt = r.get(i)
        if not nt or nt == it['text']: continue
        ch = sum(max(i2-i1, j2-j1) for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, it['text'], nt).get_opcodes() if tag != 'equal')
        if ch > 4 or len(nt) > len(it['text']) + 2: bad += 1; continue
        print('   ', w, it['text'][:40], '→', nt[:40], flush=True); it['text'] = nt; done += 1
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '语病类问题', len(todo), '处；修了', done, '；改动超限没采用', bad, flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
