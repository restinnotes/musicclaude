"""11-10 傍晚 意思单元的重要性评分（用户：“最后大字小字不是要看重要程度吗 那这个应该有一个评分的吧……之后有可能再扩充规模 引入新的东西 然后可能去筛掉一批评分最低的”）。
已有的分层（units2.py）只有 核心/重要/补充 三档，补充几乎没有，低的一头分不开，也没有喂给写手。
这里给每个单元一个 1–10 的分，并要求每段内排出先后（不许并列一大片）。两位各自独立打，取平均；差 4 分以上的标出来。
只判内容本身有多重要，不判放哪（讲音乐的照样打分，位置另算）。结果 r3/s24/uscore_{作品}.json。
python unitscore.py            打分并汇总
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, WORKS, JUDGES
from units import texts, src_text
from units2 import utext
NL = chr(10)

SCORE = """下面是一首钢琴曲每一段的原稿：线（一个人经历的一件事）和珠子（几位听众在这一刻写下的感受），后面是从原稿里拆好的“意思单元”。这份原稿以后要做成观众边听边扫的视频屏幕，一段一屏，放得下的有限：最重要的进大字，其次进小字，排在最后的可能不放。

请给每个单元打一个重要性分（1–10），只看内容本身，不看它将来放在哪个位置：
- 9–10：没有它，这一段主要在讲什么就立不住（他此刻怎么了、为什么、关键的转折），或者这一刻最主要的体验就没了。
- 7–8：不是骨架，但少了它这一段明显变薄：一个别的单元替代不了的画面、身体感觉、比喻、心里话，或一种不同的听法。
- 4–6：有自己的内容，值得有，但少了它这一段的理解和主要体验基本不变。
- 1–3：对别的单元的轻微展开或重复强调、放在哪里都成立的道理、边际价值很低的细节。
要求：
- 每一段内部要拉开：同一段里 9–10 分的只给真正立不住的那几个；不要一大片同分。每段至少要有明显低于其他单元的。
- 讲音乐本身的单元同样按上面打分。只出现一次、只有一位听众写到，不因此加分或减分。
- 再给每个单元一个它在本段里的名次 rank（1 最重要，不并列）。

只输出 JSON，逐个给全：{"units":[{"uid":"S01-u1","score":8,"rank":2}]}

【原稿】
{SOURCE}

【意思单元】
{UNITS}
"""
prompt_lint.lint(SCORE, 'unitscore.SCORE')


def one(a):
    w, j = a; p = S/f'uscore_{w}_{j}.json'
    if p.exists(): return rd(p)
    us = rd(S/f'units_{w}.json'); tx = texts(w); ids = {u['uid'] for u in us}
    msg = SCORE.replace('{SOURCE}', src_text(w)).replace('{UNITS}', utext(us, tx))
    for k in range(3):
        try:
            it = [x for x in parse(call(f'pub24US_{w}_{j}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-uscore'))['units'] if x.get('uid') in ids and isinstance(x.get('score'), (int, float))]
            assert len(it) >= 0.95*len(ids), len(it); wr(p, {'units': it}); return {'units': it}
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j) for w in WORKS for j in JUDGES]))
    for w in WORKS:
        sc = {j: {x['uid']: x for x in rd(S/f'uscore_{w}_{j}.json')['units']} for j in JUDGES}; js = list(JUDGES)
        u2 = {u['uid']: u for u in rd(S/f'units2_{w}.json')}; out = []
        for u in rd(S/f'units_{w}.json'):
            v = [sc[j].get(u['uid'], {}).get('score') for j in js]; v = [x for x in v if x is not None]
            if not v: continue
            out.append({'uid': u['uid'], 'sec': u['sec'], 'what': u['what'], 'ids': u['ids'], 'score': round(sum(v)/len(v), 1), 'scores': v,
                        'gap': max(v) - min(v), 'tier': u2[u['uid']]['tier'], 'music': u2[u['uid']]['music_any']})
        wr(S/f'uscore_{w}.json', out)
        from collections import Counter
        hist = Counter(int(x['score']) for x in out)
        print(w, '单元', len(out), '分布', dict(sorted(hist.items())), '两位差 4 分以上', sum(x['gap'] >= 4 for x in out), flush=True)
        for t in ('核心', '争议核心', '重要', '重要或补充', '补充'):
            g = [x['score'] for x in out if x['tier'] == t]
            if g: print(f"   {t}：{len(g)} 个，平均 {sum(g)/len(g):.1f}，最低 {min(g)}，最高 {max(g)}")
        low = sorted(out, key=lambda x: x['score'])[:8]
        for x in low: print('   最低：', x['uid'], x['score'], x['what'][:50])
