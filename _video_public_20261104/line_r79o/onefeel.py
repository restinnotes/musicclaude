"""11-08 晚 “一种感受一个说法”层：在当前比较对象上只改感受行，照大众版标准第 3、6 条：
同一种感受只留一个说法，留下的是最具体、最有辨识度的那个（第 6 条问留下的够不够具体，不问多少）；感受行不写成叠了几个比喻的长句。
话这一行一字不动（放大词、人物的事都不动）。
来由：用户 11-08 晚“你实际做出一个剩余的问题都是很微小的再给我看”；K3M2 开放评审两首都报：感受行长句、一条叠两三个比喻、同一屏相近比喻反复、短停留屏读不完。
python onefeel.py SRC NEW
"""
import copy, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script
import pub16

ONE = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿。普通观众边听边扫，每段屏幕只停留写明的秒数。“话”是大字的一句，讲这个人的事，【】里是放大的关键词；“感受”是小字，用 / 隔开的几块，[ ] 里是这一行的编号，每块前的数字是块号。

请只改感受行，让每屏在停留的几秒里扫得完，同时留下来的感受仍然具体：
1. 一种感受只留一个说法：同一屏里几块（或一块里的几截）在说同一种感受、只是换了比喻，就只留最具体、最有辨识度的那一个（一个画面、一种身体感觉，或一句心里话），其余删掉。不同的感受各留一个，不要为了短把不同的感受并掉。
2. 一块只放一个东西：一块里叠了两三个比喻、又接一句解释的，只留最核心的那一截；不把一句话硬切成两半，也不改成书面词组。
3. 话里已经说出的心理结论，感受里不再说一遍；感受管的是此刻听到、身体感到、心里冒出的那一下。
4. 先讲音乐结构、声部、技法再讲感受的，只留那个感受；但留下来的必须是具体的画面或身体感觉，不许换成“声音”“音乐”“感觉”“情绪”这类空词。帮人对上声音的说法（高处、低处、左手、右手、轻、重、远、近）可以留。
5. 停留短的屏少留，停留长、音乐里发生得多的屏可以多留；没内容的地方不撑。
6. 只能删、拆、换个更短的说法，不加原来没有的画面、事件、结论；疑问仍是疑问，猜测仍是猜测；比喻仍是比喻，不写成这个人真的发生的事。
7. 话行一个字都不改。

只输出改过的感受行（没改的不用列）。每块写明它来自原来的哪几块（块号），删掉的块不用写：
{"rows":[{"row":"S05-r2","items":[{"text":"留下的短语","from":[1]}],"note":"这一行删了什么、为什么"}]}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(ONE, 'onefeel.py')

# 11-08 晚 K8 删过头（幻想感受 2296→517 字，连心里话、不同的感受都删了，还留下“像在……”这种半截）。
# K8b 起（ONEFEEL_CORE=1）：每段列出核心感受（core.py，两位评委独立排出、都判核心的），屏幕上已有的必须留，丢了的换掉次要说法补进来。
CORE = os.environ.get('ONEFEEL_CORE') == '1'
if CORE:
    ONE = ONE.replace("""6. 只能删、拆、换个更短的说法，不加原来没有的画面、事件、结论；""", """6. 不同的感受、心里冒出的话一个都不删；留下的每块要能单独读懂，不留丢了主语或对象的半截（例如只剩“像在……”）。
7. 每段后面列了这一段的“核心感受”（原稿里最主要、最具体的那几条，已经独立排好）。屏幕上已有的核心必须留下（可以换更短的说法，但那个画面、身体感觉、心里话要在）；标“屏幕上丢了”的核心，用一个短说法补进这一屏，换掉同屏次要的说法，补完这一行不能比原来长。
8. 只能删、拆、换个更短的说法、按第 7 条换进核心；不加原稿没有的画面、事件、结论；""").replace("7. 话行一个字都不改。", "9. 话行一个字都不改。")
    assert '9. 话行一个字都不改。' in ONE and '8. 只能删' in ONE
    prompt_lint.lint(ONE, 'onefeel.py CORE')


# 11-08 晚 K8c 起（ONEFEEL_UNITS=1）：K8b 新盲比简洁 8:0，但细腻 0:8、连贯 0:8；评委说删掉真重复做对了，却连不同的音乐细节、情绪转折也删了；
# 新覆盖 cov3 也显示核心单元确认丢失 26 个（w23 约 11 个）。改成：屏幕上已有的每个意思单元（units.py，过半评委判留住）列出来，一样都不许丢，只许说短；
# 只删同一个单元说第二遍的部分和空泛解释；把音乐变化接到感受、再接到人物的过渡留住。
UNITS = os.environ.get('ONEFEEL_UNITS') == '1'
ONE3 = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿。普通观众边听边扫，每段屏幕只停留写明的秒数。“话”是大字的一句，讲这个人的事，【】里是放大的关键词；“感受”是小字，用 / 隔开的几块，[ ] 里是这一行的编号，每块前的数字是块号。每段后面列了“这一屏已有的内容”：是这一屏现在讲到的一样样具体的东西（画面、身体感觉、音乐变化、情绪转折、心里话），已经由别人独立理好。

请只改感受行，让它更利落、扫得动，但内容一样都不少：
1. “这一屏已有的内容”里的每一样，改完都必须还在；可以换更短的说法，但那个具体的画面、身体感觉、音乐变化、转折、心里话要在，不能换成笼统的情绪词或“声音”“感觉”这类空词。
2. 只删两种东西：同一样内容在这一屏（或一块里）说了第二遍的部分；不增加任何具体内容的空泛解释、总结、抒情套话。
3. 把音乐的变化接到感受、再接到这个人的那些过渡（“忽然”“到这里”“后来”“却”这类先后和转折）留着，它们让观众知道情绪为什么变；不要删成一串互不相连的碎片。
4. 每块要能单独读懂，不留丢了主语或对象的半截；不并成散文式的长句，一块里塞了几样东西读不动的，可以拆成两块。
5. 话里已经说出的心理结论，感受里不再说一遍。
6. 不加原来没有的画面、事件、结论；疑问仍是疑问，猜测仍是猜测；比喻仍是比喻，不写成这个人真的发生的事。
7. 话行一个字都不改。
8. 改完的每一行都要比原来短；只改有重复或空话的行，其余照旧不列。
9. “这一屏已有的内容”只用来核对改完有没有丢东西，不要照它的写法改写，也不要把它里面屏幕上原来没写的细节补进来；不写数字、不写小节号。

只输出改过的感受行（没改的不用列）。每块写明它来自原来的哪几块（块号）：
{"rows":[{"row":"S05-r2","items":[{"text":"改后的短语","from":[1]}],"note":"这一行删了什么重复、为什么"}]}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(ONE3, 'onefeel.py ONE3')
if UNITS: ONE = ONE3   # 11-08 晚 OF3 版照着清单把细节写回去、越改越长（幻想 31 行变长被拒），还抄进小节号；OF4 加第 8、9 条

# 11-08 晚 K8d 起（ONEFEEL_SEL=1）：K8c 要求每样都留，结果几乎删不动（2296→2213），说明 K3M2 长不是因为重复，而是塞了太多不同的东西。
# 旧视频 w23 每首 2500–2700 字、核心覆盖不比 3700 字的 K3M2 差，难点在挑。改成按停留时间给每屏感受字数上限（约 K3M2 的三分之二），
# 列出这一屏已有内容的分层：核心全留，重要的按篇幅挑，能一句带出两样的合起来写，过渡留着。
SEL = os.environ.get('ONEFEEL_SEL') == '1'
SEL_RATIO = float(os.environ.get('ONEFEEL_RATIO', '0.65'))
ONE5 = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿。普通观众边听边扫，每段屏幕只停留写明的秒数。“话”是大字的一句，讲这个人的事，【】里是放大的关键词；“感受”是小字，用 / 隔开的几块，[ ] 里是这一行的编号，每块前的数字是块号。
每段后面列了“这一屏已有的内容”，是这一屏现在讲到的一样样具体的东西，已经由别人独立理好并分了层：（核心）是这一刻最主要、丢了就少一样别处没有的东西；（重要）是独特、换不掉但不是必需的。

现在的感受写得太多，观众在停留的几秒里扫不完。请重写每一屏的感受行，篇幅控制在每段标题里写的字数以内：
1. 先保核心：标（核心）的每一样，改完都要在（话里已经讲到的不用在感受里重复）。
2. 再挑重要的：按剩下的篇幅，留最具体、最有辨识度、最能帮观众对上此刻音乐的那几样；放不下的舍掉。
3. 能用一个短句同时带出两样的，就合起来写，比如音乐怎么变接上身体怎么感到；但不并成散文式的长句，一块只讲一个画面或一个转折加它的感受。
4. 留着把音乐的变化接到感受、再接到这个人的过渡（“忽然”“到这里”“后来”“却”），观众要知道情绪为什么变；不要删成一串互不相连的碎片。
5. 留下的说法要具体：是那个画面、那种身体感觉、那句心里话，不换成笼统的情绪词或“声音”“感觉”这类空词。每块单独读得懂，不留丢了主语或对象的半截。
6. 话里已经说出的心理结论，感受里不再说一遍；同一样东西不说两遍。
7. 只从这一屏原来的感受和“已有的内容”里取材，不加原来没有的画面、事件、结论；疑问仍是疑问，猜测仍是猜测；比喻仍是比喻，不写成这个人真的发生的事。不写数字、不写小节号。
8. 话行一个字都不改。

每个感受行都要输出（行号照原来的），每块写明主要来自原来的哪几块（块号）：
{"rows":[{"row":"S05-r2","items":[{"text":"短语","from":[1]}]}]}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(ONE5, 'onefeel.py ONE5')
if SEL: ONE = ONE5

# 11-08 晚 K8e（ONEFEEL_KEEPTHOUGHT=1，在 OF4 基础上）：K8c 船歌新盲比 4/4 稳定选新、七项不输；幻想 3/4 稳定选旧，评委都指出删掉或改笼统了几句心里话和转折
# （“如果当时……”“是不是还可以……”被改成“念头越往前赶”；“害怕还在，脚却已经往前走了”“委屈和火气都在”“却更像抵抗得累了”被删）。
# 加一条：心里话、自问、“却……”带出的转折原样留；再机械检查：原来引号里的话改后必须还在，不在就退回原样。
KEEPT = os.environ.get('ONEFEEL_KEEPTHOUGHT') == '1'
GUARD = os.environ.get('ONEFEEL_GUARD') == '1'
if KEEPT and SEL:   # 11-08 晚 K8h：K8d 新盲比 7/8 稳定选新，但人话、细腻、为什么输——删了像人说话的心里话，又把具体画面压成四字词组
    ONE = ONE.replace("8. 话行一个字都不改。", "8. 话行一个字都不改。" + chr(10) + "9. 心里冒出的话（引号里的念头、一句自问、一句对自己说的话、像人随口说出的一句感受）原样保留，不删、不改写成概括，篇幅先让给它们。" + chr(10) + "10. 不要把具体的画面压成四字词组或书面短语；宁可少留一样，也要把留下的那样说完整、说成人话。")
    assert '10. 不要把具体的画面' in ONE
    prompt_lint.lint(ONE, 'onefeel.py SEL KEEPT')
elif KEEPT:
    ONE = ONE.replace("不写数字、不写小节号。\n", "不写数字、不写小节号。\n10. 心里冒出的话（引号里的念头、一句自问、一句对自己说的话）和“却……”“可……”带出的转折，一个字都不删、不改写成概括；它们是这一屏最具体的东西。\n", 1)
    assert '10. 心里冒出的话' in ONE
    prompt_lint.lint(ONE, 'onefeel.py KEEPT')


def unit_lines(w, src, sec):
    from pub24 import JUDGES
    us = [u for u in rd(S/f'units_{w}.json') if u['sec'] == sec]; votes = {}; nj = 0
    for j in JUDGES:
        p = S/f'cov3_{w}_{j}_{src}.json'
        if p.exists():
            nj += 1
            for x in rd(p)['items']: votes[x['uid']] = votes.get(x['uid'], 0) + (x.get('verdict') == '留住')
    return [f"  - " + (f"（{u['tier']}）" if SEL else '') + u['what'] for u in us if votes.get(u['uid'], 0) > nj/2 and (not SEL or u['tier'] in ('核心', '重要'))]


def core_lines(w, src, sec):
    from pub24 import R2, JUDGES
    core = set(rd(S/f'core_{w}.json')['core']); lost = {}; nj = 0
    for j in JUDGES:
        p = S/f'beadcovA_{w}_{j}_{src}.json'
        if p.exists():
            nj += 1
            for x in rd(p)['items']:
                if x['id'] in core and x.get('verdict') != '留住': lost[x['id']] = lost.get(x['id'], 0) + 1
    out = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        if s['sec'] == sec:
            out += [f"  - {q['text']}" + ('（屏幕上丢了）' if lost.get(q['id'], 0) > nj/2 else '') for b in s['beads'] for q in b['points'] if q['id'] in core]
    return out


def screen_text(w, scr, src=None):
    win = pub16.windows(w); out = []
    for s in scr['sections']:
        budget = round(SEL_RATIO*sum(len(i['text']) for x in s['rows'] if x['kind'] == 'feel' for i in x['items']))
        out.append(f"\n### {s['sec']}（停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒" + (f"；感受改完一共不超过约 {budget} 字" if SEL else '') + "）")
        for k, x in enumerate(s['rows'], 1):
            rid = f"{s['sec']}-r{k}"
            if x['kind'] == 'line':
                t = x['text']
                for kk in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(kk, f'【{kk}】', 1)
                out.append(f"话：{t}")
            else: out.append(f"感受 [{rid}]：" + ' / '.join(f"{n}. {i['text']}" for n, i in enumerate(x['items'], 1)))
        if CORE and src: out += ['这一段的核心感受：'] + core_lines(w, src, s['sec'])
        if (UNITS or SEL) and src: out += ['这一屏已有的内容：'] + unit_lines(w, src, s['sec'])
    return '\n'.join(out)


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json'))
    msg = ONE.replace('{SCREEN}', screen_text(w, scr, src if (CORE or UNITS or SEL) else None))
    rows = {f"{s['sec']}-r{k}": x for s in scr['sections'] for k, x in enumerate(s['rows'], 1) if x['kind'] == 'feel'}
    for t in range(3):
        ans = call(f'pub24OF{("7" if KEEPT else "5") if SEL else ("6" if KEEPT else "4") if UNITS else "2" if CORE else ""}_{w}_{os.environ.get("ONEFEEL_RIDTAG") or new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-onefeel')
        try:
            r = parse(ans); n = grow = 0; before = sum(len(i['text']) for x in rows.values() for i in x['items'])
            for e in r.get('rows') or []:
                x = rows.get(e.get('row'))
                if x is None or not isinstance(e.get('items'), list): continue
                old = x['items']; its = []
                for it in e['items']:
                    tx = str(it.get('text') or '').strip().rstrip('，。、；')
                    fr = [int(f) for f in (it.get('from') or []) if str(f).isdigit() and 1 <= int(f) <= len(old)]
                    if not tx: continue
                    base = old[fr[0]-1] if fr else old[0]
                    its.append(dict(base, text=tx))
                if not its and old: its = []   # 整行删光也允许（话已经说到了），但下面不许变长
                if sum(len(i['text']) for i in its) > sum(len(i['text']) for i in old): grow += 1; continue
                if KEEPT:   # 引号里的心里话改后必须还在
                    import re as _re
                    qs = [q for i in old for q in _re.findall(r'[“"]([^”"]{2,})[”"]', i['text'])]; nt = ''.join(i['text'] for i in its)
                    if any(q.strip('…。，') not in nt for q in qs): grow += 1; continue
                if GUARD:   # 11-08 晚 K8f：K8e 幻想几行整行砍到一块（玻璃罩、摇篮曲、那扇门都删了），船歌删了一句心里话；短块（多半是心里话）必须还在，一行最多删四成
                    import difflib as _dl, re as _re2
                    nt = ''.join(i['text'] for i in its)
                    def _kept(t): return _dl.SequenceMatcher(None, t, nt).find_longest_match(0, len(t), 0, len(nt)).size >= 0.6*len(t.replace(' ', ''))
                    if any(len(i['text']) <= 20 and not _kept(i['text']) for i in old) or (not SEL and len(nt) < 0.6*sum(len(i['text']) for i in old)): grow += 1; continue
                    if os.environ.get('ONEFEEL_GUARD2') == '1':   # 11-08 晚 K8g 幻想输：删了“害怕还在，脚却已经往前走了”“却更像抵抗得累了”这类转折，又把一段连着的心理过程拆成三块
                        segs = [g for i in old for g in _re2.split('[；。，;,]', i['text']) if len(g) >= 4 and (('却' in g) or g.startswith(('可', '但')))]
                        if any(not _kept(g) for g in segs) or len(its) > len(old): grow += 1; continue
                x['items'] = its; n += 1
            for s in scr['sections']: s['rows'] = [x for x in s['rows'] if x['kind'] == 'line' or x['items']]
            after = sum(len(i['text']) for s in scr['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items'])
            wr(p, scr); to_script(w, new, scr)
            print(w, new, '改了', n, '行；变长没采用', grow, f'；感受字数 {before} → {after}', '；小节号', gate2.barnums(w, new), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
