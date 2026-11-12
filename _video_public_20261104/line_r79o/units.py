"""11-08 晚 新覆盖测法（两位顾问 GPT-6、GPT-5.6 独立问诊后的共同方案，见 judge_check/coverfine_*）。
大众版标准第 5 条两层：线和珠子里的东西屏幕上拿得到；最核心的不能掉（先独立排出主次再对照）。
旧测法每条珠子要点一样重，且“几种听法只留了一种”直接算部分，等于惩罚第 3 条要求的去重。
新测法：
  第一步（只看原稿，不看任何屏幕稿）：GPT-6 把每段的线和珠子拆成“意思单元”——只是换个比喻再说同一个具体体验的几条并成一个单元；
    给出不同画面、身体感觉、原因、转折、心里话、情绪层次的，各自成单元（同一种大情绪不算重复）。每个单元标 核心 / 重要 / 补充。
    GPT-5.6 再独立审一遍（补漏掉的单元、拆错并的、标出它认为分层不对的）；两位分层不一致取更重的一层。冻结在 r3/s24/units_{作品}.json。
  第二步：每版屏幕稿逐个单元判 留住 / 部分 / 没有；一个单元里几条替代说法，屏幕上留住其中一个具体的就算留住。
  分数：核心留住比例、重要留住比例（各自和 w23 比，按 11-08 测量误差规则）；核心“确认丢失”（过半评委判没有）逐条列出，不许被别的抵消；补充只报告。
python units.py list            建清单（已有就不动）
python units.py judge TAG...    逐单元判（4 位评委），结果 r3/s24/cov3_{作品}_{评委}_{TAG}.json
python units.py score TAG...    打印分数
"""
import os, sys
os.environ.setdefault('PUB_BC_ALL', '1')   # 11-09 晚：覆盖看整屏（大块、小块、旁注）。K23/K24 的流水线没设这个变量，只算了小块，结果作废
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, JUDGES, feel_screen

SPLIT = """下面是一首钢琴曲每一段的原稿：线（一个人经历的事）和珠子（几位听众在这一刻写下的感受，已按句拆成要点，每条有编号）。这份原稿以后要压缩成观众边听边扫的视频屏幕；现在先不管屏幕，只把原稿里的内容理清楚。

请逐段把这一段的内容拆成“意思单元”，再给每个单元分层：
一、拆单元
- 几条要点只是用不同的比喻或说法讲同一个具体体验，没有多出可以分辨的画面、身体感觉、情绪层次或别的信息，就并成一个单元。
- 给出了不同的画面、身体感觉、原因、转折、心里话、音乐线索或情绪层次的，各自成一个单元；不能因为都属于同一种大情绪（比如都是惆怅、都是紧张）就并掉。
- 一条要点里有两样独立的东西，可以拆进两个单元；一条要点也可以同时属于一个单元。
- 线里的原因、转折、人物的事也要拆成单元（编号写线的编号）。
二、分层
- 核心：删掉它，观众对这一刻主要的感受、人物的经历、原因、转折或最有标志性的体验的理解会实质改变。一段可以有几个核心，不要硬只选一个。
- 重要：不是理解主要经历必需的，但提供了独特、换不掉的画面、身体感觉、比喻、心里话。
- 补充：有帮助，但没有明显的独立信息，或可以被别的单元代替。
- 只出现一次、只有一位听众写到的独特体验，不因此就降层。

只输出 JSON：{"units":[{"uid":"S01-u1","sec":"S01","what":"一句话说这个单元是什么（具体到那个画面、身体感觉或转折）","ids":["S01-B1-p2","S01-B3-p1"],"tier":"核心|重要|补充"}]}

【原稿】
{SOURCE}
"""

REVIEW = """下面是一首钢琴曲每一段的原稿（线和珠子要点），以及另一位编辑把它拆成的“意思单元”和分层。请你独立审一遍，只做三件事：
1. 漏掉的：原稿里有独立的画面、身体感觉、原因、转折、心里话、情绪层次，却没有进任何单元，补上。
2. 并错的：几样不同的具体体验被并进了一个单元，拆开；只是换个比喻说同一个具体体验却分成了几个单元的，也指出来并掉。
3. 分层不对的：你认为该是 核心 / 重要 / 补充 中的另一层，写出来和理由。
分层标准：核心 = 删掉它，观众对这一刻主要感受、人物经历、原因、转折或最有标志性的体验的理解会实质改变（一段可以有几个）；重要 = 不是必需，但提供独特、换不掉的画面、身体感觉、比喻、心里话；补充 = 没有明显独立信息，或能被别的单元代替。只出现一次的独特体验不因此降层。

只输出 JSON：{"add":[{"sec":"S01","what":"…","ids":["…"],"tier":"…"}],"split":[{"uid":"S01-u2","into":[{"what":"…","ids":["…"],"tier":"…"}]}],"merge":[{"uids":["S01-u3","S01-u4"],"why":"…"}],"retier":[{"uid":"S01-u1","tier":"…","why":"…"}]}

【原稿】
{SOURCE}

【拆好的单元】
{UNITS}
"""

COV = """下面是一首钢琴曲视频的两份文字。“原稿意思单元”是从原稿（线和听众的感受）里理出来的一个个具体内容，每个单元附了原稿里的说法（有的单元有几种替代说法）；“屏幕上的文字”是视频里实际显示的全部文字（叙事的话和感受短语都算）。

逐个单元判断，这个单元的具体内容在同一段屏幕上的文字里还在不在：
- 留住：那个具体的东西还在（同一个画面、身体感觉、比喻、心里话、原因或转折），说法可以不同、可以更短。单元里有几种替代说法的，屏幕上留住其中任意一个具体的就算留住，不要求每种都在。
- 部分：只剩大意或情绪，具体的画面、身体感觉、比喻、原因或转折没了。
- 没有：屏幕上找不到。
写在叙事的话里还是感受短语里都算。原稿是在讲音乐带出的感受时，那个感受在就算留住；原稿讲的是一个具体的音乐特征，就要那个特征或意思相当的说法在。

只输出 JSON：{"items":[{"uid":"S01-u1","verdict":"留住|部分|没有"}]}，逐个给全。

【屏幕上的文字】
{SCREEN}

【原稿意思单元】
{UNITS}
"""
for t, n in ((SPLIT, 'SPLIT'), (REVIEW, 'REVIEW'), (COV, 'COV')): prompt_lint.lint(t, 'units.py ' + n)
NL = chr(10); ORDER = {'核心': 0, '重要': 1, '补充': 2}


def src_text(w):
    out = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        out.append(NL + '### ' + s['sec'])
        out += [f"线 {l['id']}：{l['text']}" for l in s['lines']]
        for b in s['beads']: out += [f"- {q['id']}：{q['text']}" for q in b['points']]
    return NL.join(out)


def texts(w):
    d = {}
    for s in rd(R2/f'{w}_src.json')['sections']:
        for l in s['lines']: d[l['id']] = l['text']
        for b in s['beads']:
            for q in b['points']: d[q['id']] = q['text']
    return d


def units_text(us, tx, with_src=False):
    out = []
    for u in us:
        line = f"[{u['uid']}]（{u['tier']}）{u['what']}"
        if with_src: line += NL + NL.join(f"    原稿：{tx[i]}" for i in u['ids'] if i in tx)
        else: line += f"  ← {'、'.join(u['ids'])}"
        out.append(line)
    return NL.join(out)


def build_one(w):
    p = S/f'units_{w}.json'
    if p.exists(): return rd(p)
    tx = texts(w); src = src_text(w)
    for t in range(3):
        try:
            us = parse(call(f'pub24UN_{w}' + ('' if not t else f'_r{t}'), SPLIT.replace('{SOURCE}', src), G6, 'gpt3s', 'public24-units'))['units']
            us = [dict(u, ids=[i for i in u.get('ids') or [] if i in tx]) for u in us if u.get('tier') in ORDER]
            assert len(us) > 20; break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); us = None
    wr(S/f'units0_{w}.json', us)
    for t in range(3):
        try:
            rv = parse(call(f'pub24UNR_{w}' + ('' if not t else f'_r{t}'), REVIEW.replace('{SOURCE}', src).replace('{UNITS}', units_text(us, tx)), G56, 'gpt3s', 'public24-units')); break
        except Exception as ex: print('不合格 审', w, repr(ex)[:150], flush=True); rv = {}
    wr(S/f'unitsR_{w}.json', rv)
    by = {u['uid']: u for u in us}; n = {'add': 0, 'split': 0, 'merge': 0, 'retier': 0}
    for x in rv.get('retier') or []:   # 分层不一致取更重的一层
        u = by.get(x.get('uid'))
        if u and x.get('tier') in ORDER and ORDER[x['tier']] < ORDER[u['tier']]: u['tier'] = x['tier']; n['retier'] += 1
    for x in rv.get('split') or []:
        u = by.get(x.get('uid'))
        if not u or not x.get('into'): continue
        for k, v in enumerate(x['into'], 1):
            if v.get('tier') not in ORDER: continue
            nu = {'uid': f"{u['uid']}s{k}", 'sec': u['sec'], 'what': v.get('what') or u['what'], 'ids': [i for i in v.get('ids') or [] if i in tx] or u['ids'],
                  'tier': min(v['tier'], u['tier'], key=ORDER.get)}
            by[nu['uid']] = nu
        del by[u['uid']]; n['split'] += 1
    for x in rv.get('merge') or []:
        g = [by[i] for i in x.get('uids') or [] if i in by]
        if len(g) < 2 or len({u['sec'] for u in g}) > 1: continue
        g[0]['ids'] = sorted({i for u in g for i in u['ids']}); g[0]['tier'] = min((u['tier'] for u in g), key=ORDER.get)
        g[0]['what'] = '；'.join(u['what'] for u in g)
        for u in g[1:]: del by[u['uid']]
        n['merge'] += 1
    for k, x in enumerate(rv.get('add') or [], 1):
        if x.get('tier') in ORDER and x.get('sec'):
            by[f"{x['sec']}-a{k}"] = {'uid': f"{x['sec']}-a{k}", 'sec': x['sec'], 'what': x.get('what') or '', 'ids': [i for i in x.get('ids') or [] if i in tx], 'tier': x['tier']}; n['add'] += 1
    us = sorted(by.values(), key=lambda u: (u['sec'], u['uid'])); wr(p, us)
    from collections import Counter
    print(w, '单元', len(us), dict(Counter(u['tier'] for u in us)), '审改', n, flush=True)
    return us


def judge(a):
    w, j, t = a; p = S/f'cov3_{w}_{j}_{t}.json'
    if p.exists(): return rd(p)
    us = rd(S/f'units_{w}.json'); tx = texts(w); ids = {u['uid'] for u in us}
    msg = COV.replace('{SCREEN}', feel_screen(w, t)).replace('{UNITS}', units_text([dict(u, tier='') for u in us], tx, True).replace('（）', ''))
    for k in range(3):
        try:
            it = [x for x in parse(call(f'pub24C3_{w}_{j}_{t}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-cov3'))['items'] if x.get('uid') in ids]
            assert len(it) >= 0.9*len(ids); wr(p, {'items': it}); return it
        except Exception as ex: print('不合格', w, j, t, repr(ex)[:150], flush=True)


def score(w, t):
    us = rd(S/f'units_{w}.json'); tier = {u['uid']: u['tier'] for u in us}; per = {k: [] for k in ORDER}; votes = {}
    js = [j for j in JUDGES if (S/f'cov3_{w}_{j}_{t}.json').exists()]
    for j in js:
        v = {x['uid']: x.get('verdict') for x in rd(S/f'cov3_{w}_{j}_{t}.json')['items']}
        for k in ORDER:
            uu = [u for u in tier if tier[u] == k]; per[k].append(sum(v.get(u) == '留住' for u in uu)/max(1, len(uu)))
        for u in tier: votes.setdefault(u, []).append(v.get(u))
    avg = {k: (round(sum(x)/len(x), 3) if x else None) for k, x in per.items()}
    lost = [u for u in tier if tier[u] == '核心' and sum(x == '没有' for x in votes.get(u, [])) > len(js)/2]
    part = [u for u in tier if tier[u] == '核心' and u not in lost and sum(x != '留住' for x in votes.get(u, [])) > len(js)/2]
    return avg, lost, part, len(js)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cmd, tags = sys.argv[1], sys.argv[2:]
    if cmd == 'list':
        with ThreadPoolExecutor(2) as ex: list(ex.map(build_one, WORKS))
    elif cmd == 'judge':
        jobs = [(w, j, t) for t in tags for w in WORKS for j in JUDGES]
        with ThreadPoolExecutor(min(16, len(jobs))) as ex: list(ex.map(judge, jobs))
    if cmd in ('judge', 'score'):
        for t in tags:
            for w in WORKS:
                avg, lost, part, nj = score(w, t)
                print(f"{t} {w}（{nj} 位）：核心 {avg['核心']}、重要 {avg['重要']}、补充 {avg['补充']}；核心确认丢失 {len(lost)} {lost[:6]}；核心过半判不全 {len(part)}", flush=True)
