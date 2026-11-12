"""11-10 晚 评分尺子的第二项：同一刻之内的异质性（用户：“体验本身在某一刻的异质性”；“构成整个精神体验和理解的互斥”；标准第 4、6 条：
同一个意思不说两遍；原料里不同的理解、不同层的体验各自都要在；先独立排出主次）。
unitscore.py 给的是每个单元各打各的“分量”；这里判每个单元在本段里的“独有程度”：同段里和它最接近的是哪一个、是不是同一样东西、它多出了什么。
跨段回到同一种感受是“来回”的问题，不在这里判。两位各自独立判；结果 r3/s24/hetero_{作品}_{评委}.json，合并 r3/s24/ruler_{作品}.json。
python hetero.py            判并合并（要先有 uscore_*）
python hetero.py show op60 S06     看一段
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, WORKS, JUDGES
from units import texts, src_text
from units2 import utext
NL = chr(10)

HET = """下面是一首钢琴曲每一段的原稿：线（一个人经历的一件事）和珠子（几位听众在这一刻写下的感受），后面是从原稿里拆好的“意思单元”。每一段是一个时刻。一个时刻的体验和理解由几样不同质的东西构成（他此刻的处境、原因、一种感受、它在身上的样子、一个画面、一句心里话、另一种不同的听法……）；有的单元各自撑起不同的一样，有的单元撑的是同一样东西的又一个样子。

请逐个单元判断它在本段之内的独有程度。只和同一段的其他单元比，不和别的段比。
对每个单元：
1. near：同一段里和它最接近的那个单元的编号（说的东西最像、最可能互相替代的）。实在没有接近的就写空。
2. rel：它和 near 的关系，三选一：
   - 同一样：两个说的是同一个具体体验或同一层意思，只是换了画面或说法；有了 near，这个单元给这一刻添的东西很少。
   - 部分：有一半是同一样，但它多出了 near 没有的一层（不同的身体感觉、不同的情绪色彩、不同的理解角度、程度的变化）。
   - 不同：它撑起的是这一刻里另一样东西；near 替代不了它。
   不同的画面如果让人感到的是不同的东西，算“不同”或“部分”，不要因为都属于同一种大情绪就判“同一样”；几种不同的听法（“也可以听成……”）互相算“不同”。
3. adds：一句话写它比 near 多出了什么；rel 是“同一样”时写“无”或极短。
4. uniq：独有程度 1–5（5 = 这一刻里只有它带来这一样；1 = 有它没它，这一刻的体验构成不变）。

只输出 JSON，逐个给全：{"units":[{"uid":"S01-u1","near":"S01-u3","rel":"同一样|部分|不同","adds":"…","uniq":4}]}

【原稿】
{SOURCE}

【意思单元】
{UNITS}
"""
prompt_lint.lint(HET, 'hetero.HET')
REL = ('同一样', '部分', '不同')


def one(a):
    w, j = a; p = S/f'hetero_{w}_{j}.json'
    if p.exists(): return rd(p)
    us = rd(S/f'units_{w}.json'); tx = texts(w); ids = {u['uid'] for u in us}
    msg = HET.replace('{SOURCE}', src_text(w)).replace('{UNITS}', utext(us, tx))
    for k in range(3):
        try:
            it = [x for x in parse(call(f'pub24UH_{w}_{j}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-hetero'))['units'] if x.get('uid') in ids and x.get('rel') in REL]
            assert len(it) >= 0.95*len(ids), len(it); wr(p, {'units': it}); return {'units': it}
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


def merge(w):
    js = list(JUDGES); h = {j: {x['uid']: x for x in rd(S/f'hetero_{w}_{j}.json')['units']} for j in js}
    sc = {x['uid']: x for x in rd(S/f'uscore_{w}.json')} if (S/f'uscore_{w}.json').exists() else {}
    out = []; agree_rel = agree_near = n = same_both = 0
    for u in rd(S/f'units_{w}.json'):
        v = [h[j].get(u['uid']) for j in js]
        if not all(v): continue
        n += 1; rels = [x['rel'] for x in v]; nears = [x.get('near') or '' for x in v]
        agree_rel += rels[0] == rels[1]; agree_near += nears[0] == nears[1]; same_both += all(r == '同一样' for r in rels)
        uq = [x.get('uniq') for x in v if isinstance(x.get('uniq'), (int, float))]
        out.append({'uid': u['uid'], 'sec': u['sec'], 'what': u['what'], 'ids': u['ids'], 'weight': sc.get(u['uid'], {}).get('score'), 'weights': sc.get(u['uid'], {}).get('scores'),
                    'uniq': round(sum(uq)/len(uq), 1) if uq else None, 'uniqs': uq, 'rel': rels, 'near': nears, 'adds': [x.get('adds') for x in v],
                    'same': all(r == '同一样' for r in rels) and nears[0] == nears[1], 'tier': sc.get(u['uid'], {}).get('tier'), 'music': sc.get(u['uid'], {}).get('music')})
    wr(S/f'ruler_{w}.json', out)
    from collections import Counter
    print(w, '单元', n, '｜两位关系一致', f'{agree_rel/n:.2f}', '｜最接近的那个一致', f'{agree_near/n:.2f}', '｜两位都判“同一样”', same_both, '其中指的还是同一个', sum(x['same'] for x in out),
          '｜关系分布', dict(Counter(r for x in out for r in x['rel'])), flush=True)
    d = [abs(x['uniqs'][0] - x['uniqs'][1]) for x in out if len(x['uniqs']) == 2]
    print('   独有程度两位相差：平均', round(sum(d)/len(d), 2), '；差 2 以上', sum(x >= 2 for x in d), '个', flush=True)
    return out


def show(w, sec):
    for x in rd(S/f'ruler_{w}.json'):
        if x['sec'] != sec: continue
        print(f"{x['uid']}｜分量 {x['weight']} {x['weights']}｜独有 {x['uniq']} {x['uniqs']}｜{x['rel']}｜最接近 {x['near']}｜{'音乐｜' if x['music'] else ''}{x['what'][:60]}")
        if x['rel'][0] != '不同' or x['rel'][1] != '不同': print('        多出：', ' ／ '.join(str(a)[:50] for a in x['adds']))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) > 1 and sys.argv[1] == 'show': show(sys.argv[2], sys.argv[3]); sys.exit()
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j) for w in WORKS for j in JUDGES]))
    for w in WORKS: merge(w)
