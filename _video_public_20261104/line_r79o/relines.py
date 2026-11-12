"""【11-08 停用：提示词里有船歌原文（“怕对方嫌自己太黏”“对方有时也需要他”“等真的到了那时再说”），违反准则硬约束 1 泛化，prompt_lint 查出】11-07 V2.03c 从定稿线重写屏幕线（感受碎片不动）。
来由：g68C2Y（压缩线）“为什么”“前后一件事”几乎全输 w23；g68T（线换回定稿原文）这两项赢回来，但“扫得动”从 13:3 变成 3:13。
g68W（在压缩线上每条加 12 字补因果）没用。所以不在压缩线上修，回到定稿线重写：原因、动机、转折留下，重说、修饰、感受已说的删掉。
python relines.py SRC NEW [g6|g56]   例：python relines.py g68C2Y g68RA g6
"""
import copy, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import pub24
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, JUDGES, to_script, lines_text, view_text

RELINES = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿。每段有大字的“线”（一个人经历的事）和小字的“感受碎片”（听的人此刻的感受）。观众边听边扫，每段屏幕只停留写明的秒数。这次只重写线，感受碎片一块都不动（列出来是让你知道下面已经有什么）。

两次对照已经说明问题在哪：
- 现在屏幕上的线是从定稿线压缩来的。扮观众的评委说它好扫、要点清楚，但“知道他为什么这样”“感到前后是一件事”几乎全输给定稿原文：压缩时把原因、动机、转折删掉了。评委原话（〈这一版〉是现在的屏幕，〈旧视频〉是原文长线）：
{VS}
- 把线整个换回定稿原文，“为什么”和“前后是一件事”赢回来了，可“扫得动”从大胜变成大输：原文一条三四十字、几个分句，几秒钟里扫不完。
所以要的是中间：原因留下，长度去掉。

怎么写：
1. 从定稿线写，不要从现在的屏幕线改。先读懂这一段每条定稿线里“为什么”的那一步：他为什么这样想、这样做；和上一段比，是什么让他变了；他想要的和怕的分别是什么。这些是骨头，必须留在屏幕线里，而且要说具体（比如“怕对方嫌自己太黏”），不许并成一个笼统的词（比如“心里不安”）。
2. 能删的只有三种：同一个意思说第二遍；只撑语气的修饰；下面感受碎片已经说出的身体感觉和画面。
3. 一条长定稿线可以拆成两行短线，每行一个意思；两条说同一件事的定稿线可以并成一行。行数按内容定，不追求少。
4. 每行一扫读得完：先说要点，不用逗号串起三四个分句。keys 是放大的关键词（1–2 个，放在前半句，必须是 text 里连续的原字），要选承载原因或转折的词，不只是情绪词。
5. 人话：像一个人平常讲自己的经历，句式多变，相邻行不要彼此太像；不写“他因……而……”这种电报句，不用书面词和格言。
6. 不加定稿没有的事，不把珠子的感受搬进线，人称和称呼不变。每行选一个情绪色（炽热、欢喜、亲密、安心、孤单、不安、悬着），from 写这行依据的定稿线编号。
7. 读完全曲所有线，要能顺着讲出这个人的事：每段开头和上一段接得上。

只输出 JSON：{"sections":[{"sec":"S01","why":"这一段必须留下的原因、动机或转折，一句","lines":[{"text":"…","keys":["…"],"emotion":"…","from":["S01-1"]}]}]}，所有段都要有，按段的顺序。

【定稿的线】
{FINAL}

【现在的屏幕（话 = 线，感受 = 碎片；感受不动）】
{SCREEN}
"""
CUT = """补充（11-07 第一次重写时，op60 的线只是把定稿切成了更多短行，总字数和定稿一样，没有删）：
拆成短行本身不减轻负担，观众要扫的字一个没少。每段要真的删：重说、修饰、感受碎片已经说过的身体感觉和画面都删掉，只留事件、原因、动机、转折。下面是每段定稿线和现在屏幕线的字数，新线的字数应落在两者之间，按这一段原因多少定，不要贴着定稿：
{COUNTS}
"""


def counts(w, src):
    th = {s['sec']: sum(len(l['text']) for l in s['lines']) for s in rd(R2/f'{w}_src.json')['sections']}
    return chr(10).join(f"{s['sec']}：定稿 {th[s['sec']]} 字，现在屏幕 {sum(len(x['text']) for x in s['rows'] if x['kind'] == 'line')} 字" for s in rd(S/f'screen_{w}_{src}.json')['sections'])


CUT2 = """补充（11-07 前两次重写的教训）：
- 第一次 op60 只是把定稿切成更多短行，总字数和定稿一样，扫得动大输；
- 第二次要求删字，写手却把短行又并成了带分号的长句（每行近 30 字），扫得动还是大输；
- 两首里过了的那一版：一行一个意思、平均每行十八字左右，总字数约为定稿的八成。
所以两件事都要做到：行要短（一行一个意思，不用分号把两件事并成一行）；总量要真减（删重说、修饰、感受碎片已经说过的身体感觉和画面，只留事件、原因、动机、转折）。下面是每段定稿线和现在屏幕线的字数，新线落在两者之间，按这一段原因多少定，不要贴着定稿：
{COUNTS}
"""


CUT3 = """补充（11-07 几次重写的教训，请照做）：
- 把定稿切成很多一句一意思的短行，总字数不减，扫不动；
- 删字后又把短行并成带分号的长句，也扫不动；
- 行短、总量减到定稿八成左右，扫得动了，可“知道他为什么这样”还是输。评委原话：“短句把话拆得过碎，因果串联不如完整句子顺”“原因和结果被拆到两行，要自己拼”。另有压缩走样：“对方也许需要他”被写成“对方有时也需要他”（猜测变成了事实）；结尾“等真的到了那时再说”被删掉。
所以这次：
1. 一行一个因果，不是一行一个意思。原因和它带出的结果放在同一行，用“可、却、所以、这才、反而、因为、也就”这类词连上；不要把原因放一行、结果放下一行。一行可以有一个逗号，不要用分号把两件事并成一行。
2. 总量仍要减：删重说、修饰、感受碎片已经说过的身体感觉和画面；因果和转折一个不删。
3. 定稿里表示猜测、拿不准的语气（也许、好像、说不定、还不知道）原样保留，不能写成确定的事；每段最后落到哪里（尤其全曲结尾）要保留。
下面是每段定稿线和现在屏幕线的字数，新线落在两者之间，按这一段的因果多少定：
{COUNTS}
"""


CUT4 = CUT3.replace("下面是每段定稿线和现在屏幕线的字数", """4. 上一版照第 1 条写，“为什么”和“前后是一件事”大胜，但每行平均近三十字、常有两个逗号，“扫得动”退到持平。所以这次每行最多一个逗号（一个因果正好一个逗号），超过的拆成两行，每行各自是一个完整的因果或事件；修饰和重说再删干净。
下面是每段定稿线和现在屏幕线的字数""")


EMO = ['炽热', '欢喜', '亲密', '安心', '孤单', '不安', '悬着']


def vs_reasons(w, src):
    out = []
    for pre in ('vs', 'vsR'):
        for q in sorted(S.glob(f'{pre}_{w}_*_{src}_*.json')):
            d = rd(q); seat = q.stem.split('_')[-1]
            if (d.get('nets') or {}).get('why') == seat: continue   # 只要“为什么”判旧版赢的
            old = 'Y' if seat == 'X' else 'X'; t = (d.get('regress') or '') + ' ' + (d.get('why') or '')
            t = re.sub(r'(?<![A-Za-z])'+seat+r'(?![A-Za-z])', '〈这一版〉', re.sub(r'(?<![A-Za-z])'+old+r'(?![A-Za-z])', '〈旧视频〉', t))
            out.append('- ' + t.strip())
    return '\n'.join(out[:8])


def assemble(w, src, res):
    """新线按 from 落到旧线的位置上：每条新线挂在第一条和它共享来源的旧线处；没有共享的，跟在前一条新线后面。感受行原样保留。"""
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); got = {x['sec']: x for x in res['sections']}
    ids_all = {s['sec']: [l['id'] for l in s['lines']] for s in rd(R2/f'{w}_src.json')['sections']}
    for sec in scr['sections']:
        new = got.get(sec['sec'], {}).get('lines') or []; assert new, f"{w} {sec['sec']} 没有线"
        old_idx = [i for i, x in enumerate(sec['rows']) if x['kind'] == 'line']
        anchor = []; last = old_idx[0] if old_idx else 0
        for nl in new:
            fr = set(nl.get('from') or []); hit = [i for i in old_idx if fr & set(sec['rows'][i].get('from') or [])]
            last = hit[0] if hit else last; anchor.append(last)
        rows = []
        for i, x in enumerate(sec['rows']):
            if x['kind'] != 'line': rows.append(x)
            for k, nl in enumerate(new):
                if anchor[k] == i:
                    t = nl['text']; rows.append({'kind': 'line', 'text': t, 'keys': [q for q in nl.get('keys') or [] if q and q in t], 'emotion': nl.get('emotion') if nl.get('emotion') in EMO else '悬着', 'from': [f for f in nl.get('from') or [] if f in ids_all[sec['sec']]]})
        if not old_idx: rows = [{'kind': 'line', 'text': nl['text'], 'keys': [q for q in nl.get('keys') or [] if q in nl['text']], 'emotion': nl.get('emotion') if nl.get('emotion') in EMO else '悬着', 'from': nl.get('from') or []} for nl in new] + rows
        sec['rows'] = rows
    return scr


def one(a):
    w, src, new, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    msg = RELINES.replace('{VS}', vs_reasons(w, src)).replace('{FINAL}', lines_text(w)).replace('{SCREEN}', view_text(w, src))
    cut = {'1': CUT, '2': CUT2, '3': CUT3, '4': CUT4}.get(os.environ.get('PUB_RL_CUT', ''))
    if cut: msg = msg.replace('【定稿的线】', cut.replace('{COUNTS}', counts(w, src)) + chr(10) + '【定稿的线】', 1)
    secs = [s['sec'] for s in rd(S/f'screen_{w}_{src}.json')['sections']]
    for k in range(3):
        ans = call(f'pub24RL_{w}_{new}'+('' if not k else f'_r{k}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-relines')
        try:
            r = parse(ans); assert [x['sec'] for x in r['sections']] == secs, '段不对'
            (S/f'relines_{w}_{new}.json').write_text(__import__('json').dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
            scr = assemble(w, src, r); wr(p, scr); to_script(w, new, scr)
            L = [x['text'] for s in scr['sections'] for x in s['rows'] if x['kind'] == 'line']
            print(w, new, '线', len(L), '行', sum(map(len, L)), '字，均', round(sum(map(len, L))/len(L), 1), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, new, who = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else 'g6')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, new, who) for w in WORKS])), flush=True)
