"""线的视频形态：顾问提方案（每人一份通用提示词），两首同跑同一提示词，再按看视频的体验测。
python pub23.py adv                 三位顾问提方案，提示词存 r3/l23/prompt_{a}.txt
python pub23.py write CAND [ROUTE]  用某份提示词两首同写，得到 script_{w}_{CAND}.json
python pub23.py show CAND           打印结果和字数
python pub23.py view CAND           扫读体验测：复述主线 + 与 w23 盲比（4 票）
"""
import json, os, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('PUB_WORKS', 'op60,op61')
import pub2, pub3, pub16
from pub2 import G6, G56, JUDGES, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT; L = R3/'l23'; L.mkdir(exist_ok=True)
BASE = os.environ.get('PUB_BASE', 'w23')

ADV = """你是顾问。我们做钢琴曲的“边听边看”视频：下半屏是音乐动画，上半屏每段有几条“线”（一个人经历的一件事）和散开的“珠子”短词（听的人此刻的感受）。观众在听音乐，眼睛是扫屏幕，抓关键词。

【用户刚看完视频的原话】
“感觉你现在这个线还是太啰嗦 然后珠子我们现在的覆盖率理应有七成以上 那我们的线 有可能也要做措施 就是我们现在是用线是连贯的 而珠子是碎裂的词汇 我不确定这种方式合不合理 感觉可能就是线还是太长？有可能一句话里感觉根本不能有逗号和太多修饰？就比如现在抓不到线的要点 在看视频的时候 可能应该要提炼出要点 然后要点中间要能够前后呼应 感觉到有整体性 独立性 不能翻译珠子 ……总而言之最关键的是 我觉得你还是要根据最后看视频的最后体验 然后再去看我们原来所想要达到的效果（比如珠子和线所能达到的 甚至是原稿能达到的）然后看看 这些精细的体验描绘出了多少 会不会有一些我们删掉的东西 比如形容词副词 句子中间的连接部分 其实起到了太关键的作用 我们最后肯定要形成一个平衡 注意力必须最经济”

【大众版标准】
{STD}

【刚测到的事实（两首，两位评委）】
- 线平均 39 字、2.4 个逗号。一条线“真正要让人知道的那一点”平均只有 11 字。这一点落在句子后部的 60–80%，落在句子开头的几乎没有。扫读的人最先看到的是铺垫，要点在最后。
- 评委只认为 2–5% 的字可以白删。铺垫大多在撑因果或感觉：比如“起初还觉得”“这回没急着”“也许”。
- 原稿最精细的体验，主要靠连接转折（约三成）和比喻画面（约三成）撑着，形容词、副词很少（共不到一成）。屏幕上约七成“变粗”。丢了且对扫读损失大的，也主要是连接转折和比喻画面。
- 评委说全曲的线索大致留得住，但前后呼应在屏幕上看不出来，比如“话没出口—反复想说—终于说完”“也许被需要—希望仍被需要—怕不再被需要”。

【试过没用的】
- 按每段秒数压线（压到 54–71%）：不伤大意，但当文章读时单独成立、人话都输给原句，用户也觉得不如原句。例：“前几次想说又收住，对方却一直愿意跟他亲近，这回他不知不觉就忘了藏好喜欢，等察觉时，对方已经看出他有多在乎。”压成“对方一直愿意和他亲近，他不知不觉忘了藏好喜欢。”只是把一句长句删成一句短句，还是铺垫在前，也没有前后呼应。
- 把线拆成多条：零碎、承接弱。
- 把词概括成书面词：失去感觉。
- 轮流放大、时序呈现：用户否定。

【屏幕现状（船歌，节选）】
{SAMPLE}

【请你回答】
1. 判断：线连贯、珠子碎裂这种配合合理吗？线到底该是什么形态？
2. 给一个方案，让观众扫读时抓到每段的要点、感到前后呼应和整体性、线不翻译珠子，同时不丢撑因果和转折的连接。可以改线的形态（比如要点放前面、短句不带逗号、两层字号：要点大字加原句小字、一段线数减少、重复一个词来呼应），由你判断，不必照我的举例。
3. 写一份通用提示词，直接发给写手。提示词不能提任何具体作品的内容，要对任何作品都能用。用这些占位符（照原样写，脚本会替换）：{FINAL} 定稿的线，{SCREEN} 现在的屏幕（每段秒数、每组的线和词），{SOURCE} 原稿珠子。
   写手必须只输出这个 JSON（把它写进提示词）：{"thread":"全曲线索和呼应的计划","sections":[{"sec":"S01","groups":[{"idx":0,"point":"要点，观众一定看到的大字","detail":"可选的小字，不要就写空字符串"}]}]}。每组都要给；point 写空字符串表示这条线不单独显示，它的词并到上一组。

只输出 JSON：{"judgement":"第1问，三五句","plan":"第2问","prompt":"第3问的提示词全文"}
"""

CHECK = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。每段屏幕只停留写明的秒数。屏幕上“大字”你一定看到，“小字”你多半只瞄一眼，“词”是散开的短词。

看完以后请回答：
1. thread：这首曲子讲了一个什么样的人、什么事？一两句话。
2. sections：逐段写 caught（这段你抓到的那一点，10 字以内，抓不到写“无”）、echo（这段让你想起前面哪一段，写段号；没有写空）、why（你知道他为什么这样吗：能 / 勉强 / 不能）。
3. overall：哪里最吃力，哪里最抓人，两三句。

只输出 JSON：{"thread":"…","sections":[{"sec":"S01","caught":"…","echo":"","why":"能"}],"overall":"…"}

【屏幕】
{SCREEN}
"""

SCORE = """观众只扫屏幕，写下了他从每段抓到的东西。下面的“原稿”是完整的线。请逐段判断他抓到的和原稿这段最核心的那一点是不是一回事：对 / 偏 / 错 / 无。再判断整体：他说的这件事和原稿是不是一件事：对 / 偏 / 错。

只输出 JSON：{"overall":"对","sections":[{"sec":"S01","v":"对"}]}

【观众】
{ANS}

【原稿】
{FINAL}
"""

VS = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。下面是同一首曲子视频屏幕的两个版本。“大字”一定看到，“小字”多半只瞄一眼，“词”是散开的短词，每段屏幕只停留写明的秒数。

如果你是观众，哪个版本让你：扫得动、抓得到每段要点、知道这个人为什么这样、感到前后是一件事、感受细腻不粗糙？不要因为字多或字少本身加减分。

只输出 JSON：{"better":"X|Y","regress":"你选的版本有没有哪里明显不如另一个：有/无，写一句","nets":{"scan":"X|Y|平","point":"X|Y|平","why":"X|Y|平","whole":"X|Y|平","fine":"X|Y|平"},"why":"两三句"}

【X】
{X}

【Y】
{Y}
"""


def final(w): return '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
def source(w): return '\n'.join(f"\n### {s['sec']}\n"+'\n'.join(f"- {b['text']}" for b in s['beads']) for s in rd(R2/f'{w}_src.json')['sections'])


def base_screen(w):
    win = pub16.windows(w); rows = []
    for s in rd(R3/f'script_{w}_{BASE}.json')['sections']:
        rows.append(f"\n### {s['sec']}（{round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for i, g in enumerate(s['groups']):
            rows.append(f"idx {i} 线：" + ' '.join(l['text'] for l in g.get('lines', []))+'\n   词：' + ' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def adv():
    msg = ADV.replace('{STD}', (pub2.ROOT/'大众版标准.md').read_text(encoding='utf-8').split('## 画面')[0]).replace('{SAMPLE}', '\n'.join(base_screen('op60').split('\n')[:26]))
    def one(a):
        name, fn = a; ans = fn(name, msg); r = parse(ans) or {}
        (L/f'adv_{name}.md').write_text(f"# {name}\n\n## 判断\n{r.get('judgement')}\n\n## 方案\n{r.get('plan')}\n\n## 提示词\n{r.get('prompt')}\n", encoding='utf-8')
        if r.get('prompt'): (L/f'prompt_{name}.txt').write_text(r['prompt'], encoding='utf-8')
        print(name, len(ans or ''), (r.get('judgement') or '')[:300], flush=True)
    sys.path.insert(0, str(pub2.EVO)); import evo
    jobs = [('g6', lambda n, m: call('pub23_adv_g6', m, G6, 'gpt3s', 'public23-adv')), ('g56', lambda n, m: call('pub23_adv_g56', m, G56, 'gpt3s', 'public23-adv')), ('argon', lambda n, m: evo.call_argon_direct('pub23_adv_argon', m, meta={'stage': 'public23-adv'}))]
    with ThreadPoolExecutor(3) as ex: list(ex.map(one, jobs))


REV = """你是顾问。上一轮你给写手的提示词（附在最后）已经两首同跑，并按看视频的体验测了。现在请根据结果改提示词。

【结果】
- 与现在的视频（线是完整长句，没有小字）盲比 4 票：{VOTES}。
- 四位评委分项（新版对旧版）：{NETS}
- 评委原话：
{WHY}
- 只看每条大字第一个标点之前（模拟第一眼），观众抓对的段数（两首×两位评委）：新版 {GL_NEW}，现在的视频 {GL_OLD}。
- 另一位顾问的方案结果相近：{OTHER}

【你这份提示词写出的屏幕（节选）】
{SAMPLE}

【这一轮要解决的】
扫读赢了，但“知道他为什么这样”和“细腻”输了：原因、转折和心理的层次被挪进了小字，或者被压成了重复的口号。用户的要求是平衡：注意力最经济，同时不能丢掉撑着体验的连接和转折。请想清楚：哪些原因必须留在大字里，大字怎样在很短的同时带着原因或转折，小字什么时候值得出现，锚点词怎样呼应而不变成重复口号。

写一份新的通用提示词。规则同上一轮：不提具体作品内容；占位符 {FINAL}、{SCREEN}、{SOURCE} 照原样写；写手只输出 {"thread":"…","sections":[{"sec":"S01","groups":[{"idx":0,"point":"…","detail":"…"}]}]}，每组都给，point 空字符串表示并到上一组。人称和称呼跟定稿一样，不要改成“我”。

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【上一轮的提示词】
{PROMPT}
"""


def votes_of(tag):
    rows = []; nets = Counter(); why = []
    for p in sorted(L.glob(f'vs_*_{tag}_*.json')):
        r = rd(p); seat = r['seat']; w = p.stem.split('_')[1]; j = p.stem.split('_')[2]
        rows.append(('选新' if r['better'] == seat else '选旧'))
        for k, v in (r.get('nets') or {}).items(): nets[k+':'+('新' if v == seat else '旧' if v in 'XY' else '平')] += 1
        why.append(f"- {w} {j}（新版在 {seat}）：{r.get('why')} 不足：{r.get('regress')}")
    return f"{rows.count('选新')}/{len(rows)} 选新", dict(nets), '\n'.join(why)


def glance_sum(tag):
    c = Counter()
    for p in L.glob(f'glance_*_{tag}.json'):
        for x in rd(p)['score']['sections']: c[x.get('v')] += 1
    return dict(c)


def revise(name, tag, other):
    v, n, why = votes_of(tag); ov, on, _ = votes_of(other)
    sample = '\n'.join(lines_view('op60', tag).split('\n')[:40])
    msg = REV.replace('{VOTES}', v).replace('{NETS}', json.dumps(n, ensure_ascii=False)).replace('{WHY}', why).replace('{GL_NEW}', json.dumps(glance_sum(tag), ensure_ascii=False)).replace('{GL_OLD}', json.dumps(glance_sum(BASE), ensure_ascii=False)).replace('{OTHER}', f"{ov}，{json.dumps(on, ensure_ascii=False)}").replace('{SAMPLE}', sample).replace('{PROMPT}', (L/f'prompt_{name}.txt').read_text(encoding='utf-8'))
    if name == 'argon':
        sys.path.insert(0, str(pub2.EVO)); import evo; ans = evo.call_argon_direct(f'pub23_rev_{name}', msg, meta={'stage': 'public23-rev'})
    else: ans = call(f'pub23_rev_{name}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public23-rev')
    (L/f'rev_{name}.md').write_text(ans or '', encoding='utf-8')
    try: r = parse(ans); p = r['prompt']
    except Exception:
        import subprocess; subprocess.run([sys.executable, 'qa/fix_argon_prompt.py'], capture_output=True); r = {'diagnosis': ''}; p = None
    if p: (L/f'prompt_{name}2.txt').write_text(p, encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:400], '提示词', len(p or ''), flush=True)


def apply(w, tag, r):
    d = rd(R3/f'script_{w}_{BASE}.json'); N = {s['sec']: {int(g['idx']): g for g in s['groups']} for s in r['sections']}
    for s in d['sections']:
        keep = []; carry = []
        for i, g in enumerate(s['groups']):
            x = N.get(s['sec'], {}).get(i) or {}; t = (x.get('point') or '').strip()
            fr = [y for l in g.get('lines', []) for y in l.get('from', [])]
            if not t:
                (keep[-1]['beads'] if keep else carry).extend(g.get('beads', []))
                if keep: keep[-1]['lines'][0]['from'] += fr
                continue
            g['lines'] = [{'text': t, 'detail': (x.get('detail') or '').strip(), 'keys': [], 'from': fr}]
            g['beads'] = carry+g.get('beads', []); carry = []; keep.append(g)
        assert keep, s['sec']
        if not any(g['rank'] == '主' for g in keep): keep[0]['rank'] = '主'
        s['groups'] = keep
    d['thread_plan'] = r.get('thread', ''); wr(R3/f'script_{w}_{tag}.json', d); wr(R2/f'script_{w}_{tag}.json', d)


def write_one(a):
    w, cand, route = a; tag = cand; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    tpl = (L/f"prompt_{cand[1:]}.txt").read_text(encoding='utf-8')
    msg = tpl.replace('{FINAL}', final(w)).replace('{SCREEN}', base_screen(w)).replace('{SOURCE}', source(w))
    for k in range(3):
        rid = f'pub23W_{w}_{tag}'+('' if not k else f'_r{k}')
        if route == 'argon':
            sys.path.insert(0, str(pub2.EVO)); import evo; ans = evo.call_argon_direct(rid, msg, meta={'stage': 'public23-write'})
        else: ans = call(rid, msg, G6, route, 'public23-write')
        try: apply(w, tag, parse(ans)); return True
        except Exception as ex: print('不合格', w, tag, repr(ex)[:200], flush=True)
    return False


def first_clause(t):
    m = re.search(r'[，；：。？！]', t); return t if not m else t[:m.start()]


def lines_view(w, tag, full=True):
    """full=False 是“第一眼”：每条大字只看到第一个标点之前，小字看不到。机械代理，偏向要点在前的写法。"""
    win = pub16.windows(w); rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}（屏幕停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for g in s['groups']:
            for l in g.get('lines', []):
                rows.append('大字：'+(l['text'] if full else first_clause(l['text'])))
                if full and l.get('detail'): rows.append('小字：'+l['detail'])
            rows.append('词：'+' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def show(tag, secs=None):
    for w in WORKS:
        d = rd(R3/f'script_{w}_{tag}.json'); L0 = [l for s in d['sections'] for g in s['groups'] for l in g.get('lines', [])]
        print(f'== {w} {tag} 条 {len(L0)} 大字 {sum(len(l["text"]) for l in L0)} 均 {sum(len(l["text"]) for l in L0)//max(1,len(L0))} 逗号/条 {round(sum(len(re.findall("[，；：]", l["text"])) for l in L0)/max(1,len(L0)),2)} 小字 {sum(len(l.get("detail") or "") for l in L0)}')
        print('线索：', d.get('thread_plan', '')[:300])
        for s in d['sections']:
            if secs and s['sec'] not in secs: continue
            print(s['sec'], ' ｜ '.join(l['text']+(f"（{l['detail']}）" if l.get('detail') else '') for g in s['groups'] for l in g.get('lines', [])))


def view_one(a):
    w, j, tag = a[:3]; full = a[3] if len(a) > 3 else True; pre = 'check' if full else 'glance'; p = L/f'{pre}_{w}_{j}_{tag}.json'
    if not p.exists():
        for k in range(3):
            q = f"{'' if full else 'G'}{w}_{j}_{tag}"+('' if not k else f'_r{k}')
            ans = call(f'pub23C_{q}', CHECK.replace('{SCREEN}', lines_view(w, tag, full)), JUDGES[j], 'gpt3s', 'public23-check')
            try:
                r = parse(ans); assert r['sections']
                sc = parse(call(f'pub23S_{q}', SCORE.replace('{ANS}', json.dumps(r, ensure_ascii=False)).replace('{FINAL}', final(w)), JUDGES[j], 'gpt3s', 'public23-score'))
                r['score'] = sc; wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); S = r['sections']; v = Counter(x.get('v') for x in r['score']['sections'])
    print(w, j, tag, '第一眼' if not full else '全看', '抓对', dict(v), '整体', r['score'].get('overall'), '呼应段', sum(bool(x.get('echo')) for x in S), '/', len(S), '知道为什么', dict(Counter(x.get('why') for x in S)), flush=True)
    print('   ', (r.get('thread') or '')[:120], '||', (r.get('overall') or '')[:200], flush=True)


def vs_one(a):
    w, j, tag, seat = a; p = L/f'vs_{w}_{j}_{tag}_{seat}.json'; base = os.environ.get('VS_BASE', BASE)
    if not p.exists():
        a1, b1 = lines_view(w, tag), lines_view(w, base); x, y = (a1, b1) if seat == 'X' else (b1, a1)
        for k in range(3):
            ans = call(f'pub23V_{w}_{j}_{tag}_vs{base}_{seat}'+('' if not k else f'_r{k}'), VS.replace('{X}', x).replace('{Y}', y), JUDGES[j], 'gpt3s', 'public23-vs')
            try: r = parse(ans); assert r['better']; wr(p, {'seat': seat, **r}); break
            except Exception as ex: print('不合格', repr(ex)[:150], flush=True)
    r = rd(p); new = r['better'] == seat
    print(w, j, seat, '选新' if new else '选旧', {k: ('新' if v == seat else '旧' if v in 'XY' else '平') for k, v in (r.get('nets') or {}).items()}, '|', (r.get('regress') or '')[:80], '|', (r.get('why') or '')[:160], flush=True)
    return new


def view(tag):
    jobs = [(w, j, tag, f) for f in (False, True) for w in WORKS for j in JUDGES]
    with ThreadPoolExecutor(4) as ex: list(ex.map(view_one, jobs))
    n = int(os.environ.get('VS_N', '8'))
    jobs = [(w, 'g6', tag, 'X') for w in WORKS]+[(w, 'g56', tag, 'Y') for w in WORKS]+([(w, 'g6', tag, 'Y') for w in WORKS]+[(w, 'g56', tag, 'X') for w in WORKS] if n == 8 else [])
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(vs_one, jobs))
    print(tag, '选新', sum(res), '/', len(res), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'adv': adv()
    elif c == 'revise':
        with ThreadPoolExecutor(2) as ex: list(ex.map(lambda a: revise(*a), [('argon', 'Largon', 'Lg56'), ('g56', 'Lg56', 'Largon')]))
    elif c == 'write':
        route = sys.argv[3] if len(sys.argv) > 3 else 'gpt3s'
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(write_one, [(w, sys.argv[2], route) for w in WORKS])), flush=True)
        show(sys.argv[2])
    elif c == 'show': show(sys.argv[2], sys.argv[3:] or None)
    elif c == 'view': view(sys.argv[2])
    elif c == 'base':
        with ThreadPoolExecutor(4) as ex: list(ex.map(view_one, [(w, j, BASE, f) for f in (False, True) for w in WORKS for j in JUDGES]))
