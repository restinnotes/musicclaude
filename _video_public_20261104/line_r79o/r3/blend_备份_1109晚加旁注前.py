"""11-08 V2.03e 珠子和线真正揉在一起写屏幕稿。
来由：用户 11-08：“注意你这现在应该是要把珠子和线揉在一起的 连贯和散落都是可行的 我看你这个rhp的还是分开来的是什么情况”。
11-06 起的屏幕稿只是排版上下交替，内容仍按来源分开（大字只放线、小字只放珠子，relines 还写了“不把珠子的感受搬进线”）。
这一版每行自己选形态：连贯（一句话，关键词放大）或散落（小字短语）；线的内容、珠子的内容都可以进任何一行。
python blend.py NEW g6|g56      两首同写 → r3/s24/screen_{w}_{NEW}.json（连贯 → kind line，散落 → kind feel，供已有测法和 film_v8 用）
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import pub16
from pub24 import S, R2, R3, rd, wr, call, parse, G6, G56, WORKS, to_script, lines_text

BLEND = """下面是一首钢琴曲大众版“边听边看”视频要用的材料。下半屏是音乐动画，上半屏是文字。观众是普通人，边听边扫，没读过任何原文；每段屏幕只停留写明的秒数。请写这首曲子全曲的屏幕稿。

材料有两种来源，都已定稿：
- 线：一个人经历的一件事（他想要什么、怕什么、为什么变了），把全曲串起来。
- 珠子：听的人此刻心里和身上的感受，带着具体的画面、身体感觉、比喻；有的写明只属于某几小节。

【这一版最重要的一条：珠子和线揉在一起写，不按来源分行】
揉在一起是为了让屏幕内部连贯：观众读起来不在“他的事”和“一堆感受”之间来回跳，感受和这个人的处境挨在一起、接得上，像一回事。同时原来的内容要尽量保住（会测屏幕对定稿线和珠子的覆盖）。
屏幕上每一行自己选一种形态：
- 连贯：一句话，大字，其中 1–2 个关键词放大加亮。
- 散落：几块小字短语，散开排，每块 3–8 个字，不带标点。
两种形态都可以装线的内容，也都可以装珠子的内容，一行里也可以两者都有。例如一句连贯的话，前半是他的顾虑，后半是此刻身上的感受；线的一个要点也可以化成散落的短语，和珠子的短语放在一起。什么内容用什么形态，按观众这几秒里最省力、又最能感到“这个人为什么这样”和“音乐里这一刻的感受”来定，不必一行线一行感受地交替。

【线和珠子定稿时用的标准，屏幕上照样要成立（定稿做到的不能丢）】
{DAGSTD}

【之前几轮试出来的规矩，照做】
1. 因果不能丢：每段要让人知道他此刻为什么这样、和上一段比是什么让他变了。要保留的是关系，不是句法：原因和结果最好在同一句里用“可、却、所以、这才、反而”这类词连上，也可以紧挨着放在相邻两块里，但不能隔开到读者要自己拼。不要为了连贯造出定稿没有的因果，定稿里并列的东西也不要写成先后。连贯的句子一扫读得完，不用分号把几件事串成长句。
2. 不改意思（会专门查）：定稿线里的疑问句仍是疑问句；猜测、拿不准的语气（也许、说不定、还不知道）不写成确定；担心不写成已经发生；具体说法不换成笼统的词；每段的落点、尤其全曲结尾要留住。不加定稿没有的事件、画面、动作、结论，不把珠子的比喻写成他真的经历的事。人物指代要清楚，不产生歧义。
3. 珠子不翻译、不概括：保留珠子自己的具体画面、身体感觉、比喻、心里话、转折，不要换成笼统的情绪词；纯写音乐本身的（声部、和弦、调性）换成它带出的感受，不要术语。同一种感受只留最具体的一个说法；最核心的不能掉，具体的东西尽量都留住。
4. 扫得动：内容密度按停留秒数定，靠重组、去重、突出关键词，不靠按原文顺序截断。下面给了每段秒数和现在视频这一段的字数，只作参照：之前的版本里，停留短的段字一多，评委就说“几秒钟扫不完”。
5. 局部小节：标了“只属于某几小节”的珠子，它的内容尽量写成散落短语，并在 bars 里写明小节（如 12–14），这些短语到那几小节才出现；同一颗珠子的短语放在一起。
6. 人话：完整句、短句、问句、感叹、短语都可以，像一个人平常讲自己的经历，句式多变，相邻两句不要彼此太像；散落的短语也要像人说的，不是书面词，不是把一句话硬切成的半句；不写“他因……而……”这种电报句，不用格言和心理分析。全曲读下来要能顺着讲出这个人的事。
7. 每个连贯行选一个情绪色（炽热、欢喜、亲密、安心、孤单、不安、悬着）。from 写这一行用到的定稿线编号和珠子编号（如 ["S05-2","S05-B1"]）。

只输出 JSON：{"sections":[{"sec":"S01","rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的字"],"emotion":"…","from":["S01-1","S01-B2"]},{"form":"散落","items":[{"text":"…","from":["S01-B2"],"bars":""}]}]}]}，所有段都要有，按段的顺序。

【每段停留秒数和现在视频的字数（参照）】
{BUDGET}

【定稿的线】
{FINAL}

【定稿的珠子】
{BEADS}
"""
def _std2():
    import re as _re
    NL = chr(10)
    s = open('D:/musicclaude/_video_public_20261104/大众版标准.md', encoding='utf-8').read()
    s = s[s.index('## 内容（屏幕稿）'):s.index('## 画面')].replace('## 内容（屏幕稿）', '').strip()
    s = NL.join(l for l in s.split(NL) if not _re.match(r'^- (和 DAG 的区别|边界)', l))
    return _re.sub(r'（(由|继承|原|和第)[^）]*）', '', s)
DAGSTD = _std2()   # 11-08：标准改版后，写手拿 DAG2 标准的内容 7 条（去掉写给人看的边界说明）
EMO = ['炽热', '欢喜', '亲密', '安心', '孤单', '不安', '悬着']


import prompt_lint
prompt_lint.lint(BLEND, 'blend.py')   # 准则硬约束 1：模板里不许有作品原文，有就不送出


def cap(w):
    """11-09 下午 K15：按停留秒数定每屏字数上限（每秒 PUB_BL_RATE 字，最少 90、最多 300）。K10 不设上限写到 4500–6400 字；K11g 每秒 7 字以上的屏都被报偏密。"""
    r = float(os.environ.get('PUB_BL_RATE', '5.5')); win = pub16.windows(w)
    return {k: max(90, min(300, round(r*(b-a)))) for k, (a, b) in win.items()}


def budget(w):
    if os.environ.get('PUB_BL_RATE'):
        win = pub16.windows(w); c = cap(w)
        big = float(os.environ.get('PUB_BL_BIG', '0'))   # 11-09 K17：大字占比上限。K16b 大字占 80% 以上、小字只剩 429 字，船歌珠子覆盖 0.44（w23 大字 60%、小字 1063 字，0.665）
        if big: return chr(10).join(f"{k}：停留 {round(b-a)} 秒，这一屏最多 {c[k]} 字，其中大字（连贯）最多 {round(c[k]*big)} 字" for k, (a, b) in win.items()) + chr(10) + f"全曲合计最多 {sum(c.values())} 字。"
        return chr(10).join(f"{k}：停留 {round(b-a)} 秒，这一屏最多 {c[k]} 字" for k, (a, b) in win.items()) + chr(10) + f"全曲合计最多 {sum(c.values())} 字。"
    d = rd(R3/f'script_{w}_w23.json'); win = pub16.windows(w)
    return chr(10).join(f"{s['sec']}：停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒，参照 {sum(len(l['text']) for g in s['groups'] for l in g['lines'])+sum(len(b['text']) for g in s['groups'] for b in g['beads'])} 字" for s in d['sections'])


def current_json(w, tag):
    out = []
    for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
        rows = []
        for x in s['rows']:
            if x['kind'] == 'line': rows.append({'form': '连贯', 'text': x['text'], 'keys': x.get('keys') or [], 'emotion': x.get('emotion', ''), 'from': x.get('from') or []})
            else: rows.append({'form': '散落', 'items': [{'text': i['text'], 'from': i.get('from') or ([i['bead']] if i.get('bead') else []), 'bars': i.get('bars') or ''} for i in x['items']]})
        out.append({'sec': s['sec'], 'rows': rows})
    return json.dumps({'sections': out}, ensure_ascii=False)


def _ok(t):
    try: json.loads(t); return True
    except Exception: return False


def lines_map(w):
    """11-09 下午：DAG r2c 起每条线写明对应的珠子（DAG 标准第 4 条），写稿时一起给，方便把感受织进对应的处境。"""
    return chr(10).join(f"{s['sec']} {l['id']}：{l['text']}" + (f"（对应珠子：{'、'.join(l['beads'])}）" if l.get('beads') else '') for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])


def beads_text(w):
    out = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        out.append(f"\n### {s['sec']}（小节 {s['bars']}）")
        for b in s['beads']:
            loc = any(p['local'] for p in b['points'])
            out.append(f"[{b['id']}]（小节 {b['where']}{'，只属于这几小节' if loc else ''}）{b['text']}")
    return chr(10).join(out)


def convert(w, r):
    src = rd(R2/f'{w}_src.json'); secs = [s['sec'] for s in src['sections']]
    got = [x['sec'] for x in r['sections']]; assert got == secs, f'段不对 {got[:3]}'
    ids = {l['id'] for s in src['sections'] for l in s['lines']} | {b['id'] for s in src['sections'] for b in s['beads']}
    out = {'sections': []}; miss = []
    for s, s0 in zip(r['sections'], src['sections']):
        rows = []
        for x in s.get('rows') or []:
            if x.get('form') == '散落':
                its = [{'text': re.sub(r'[，。、；！？,.!?;]+$', '', i['text'].strip()), 'bead': next((f for f in (i.get('from') if isinstance(i.get('from'), list) else [i.get('from')]) if f in ids), s0['beads'][0]['id'] if s0['beads'] else ''), 'from': [f for f in (i.get('from') if isinstance(i.get('from'), list) else [i.get('from')]) if f in ids], 'bars': i.get('bars') or ''} for i in x.get('items') or [] if (i.get('text') or '').strip()]
                if its: rows.append({'kind': 'feel', 'items': its})
            elif (x.get('text') or '').strip():
                t = x['text'].strip()
                rows.append({'kind': 'line', 'text': t, 'keys': [k for k in x.get('keys') or [] if k and k in t][:2], 'emotion': x.get('emotion') if x.get('emotion') in EMO else '悬着', 'from': [f for f in x.get('from') or [] if f in ids]})
        assert rows, f"{s['sec']} 没有内容"   # 11-08：一段全是散落也可以（连贯和散落都可行）
        used = {f for x in rows for f in (x.get('from') or [])} | {f for x in rows if x['kind'] == 'feel' for i in x['items'] for f in [i['bead']]+i.get('from', [])}
        miss += [b['id'] for b in s0['beads'] if b['id'] not in used]
        out['sections'].append({'sec': s['sec'], 'rows': rows})
    return out, miss


def one(a):
    w, new, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    tpl = BLEND
    if os.environ.get('PUB_BL_PROMPT'):   # 11-08：顾问给的写稿提示词（I02），发出前同样过泛化检查
        tpl = (S/os.environ['PUB_BL_PROMPT']).read_text(encoding='utf-8')
        prompt_lint.lint(tpl.replace('{BUDGET}', '').replace('{DAGSTD}', '').replace('{FINAL}', '').replace('{BEADS}', ''), os.environ['PUB_BL_PROMPT'])
    if '{CURRENT}' in tpl:   # 11-09 K18：顾问路线 B（以当前最好版为底逐屏重组），当前版用 PUB_BL_CUR 指定，转成和输出相同的格式
        tpl = tpl.replace('{CURRENT}', current_json(w, os.environ.get('PUB_BL_CUR', 'g68K11g')))
    msg = tpl.replace('{DAGSTD}', DAGSTD).replace('{BUDGET}', budget(w)).replace('{FINAL}', lines_map(w)).replace('{BEADS}', beads_text(w))
    for k in range(3):
        ans = call(f'pub24BL2_{w}_{new}'+('' if not k else f'_r{k}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-blend')
        try:
            try: r = parse(ans)
            except Exception:   # 11-09 K17：长输出两次都只是结尾少了“]}”，先试补全括号再判不合格
                body = ans[ans.index('{'):ans.rindex('}')+1]; r = next((json.loads(body+x) for x in (']}', '}]}', ']}]}') if _ok(body+x)), None)
                if r is None: raise
            scr, miss = convert(w, r)
            (S/f'blend_{w}_{new}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
            wr(p, scr); to_script(w, new, scr)
            rows = [x for s in scr['sections'] for x in s['rows']]; L = [x['text'] for x in rows if x['kind'] == 'line']; F = [i['text'] for x in rows if x['kind'] == 'feel' for i in x['items']]
            mixed = sum(1 for x in rows if x['kind'] == 'line' and any('-B' in f for f in x['from']) and any('-B' not in f for f in x['from']))
            print(w, new, '连贯', len(L), '行', sum(map(len, L)), '字；散落', len(F), '块', sum(map(len, F)), '字；连贯行里线+珠子都有的', mixed, '；没用到的珠子', miss, flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    new, who = sys.argv[1], sys.argv[2]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, new, who) for w in WORKS])), flush=True)
