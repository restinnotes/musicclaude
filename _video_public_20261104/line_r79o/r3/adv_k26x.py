"""11-10 I12：K26 新形态交回提出者（第 2 次起用 RND 环境变量；第 1 次 K26a/K26c，第 2 次 K26a2/K26c2）。K26a（自然句块）→ GPT-6；K26c（短块关系链）→ GPT-5.6。
两版都过退步检查、中等少、core 比碎块好，但覆盖掉到 0.65–0.76（K25a 0.84/0.85），走样各 2 处。
python r3/adv_k26x.py g6|g56 → r3/s24/adv_k26x1_{j}.json；提示词 r3/s24/prompt_K26x1_{j}.txt
"""
import json, sys, re, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56, view_text
from adv_k24r import issues, faith
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)
RND = os.environ.get('RND', '1')
CFG = {'g6': ('g68K26a', 'prompt_K26_g6_1.txt', '自然句块', '大块每屏 ≤3、每块 ≤28 字、最多一个逗号；小块 ≤5、≤28 字、最多一个逗号；主区合计 ≤6 块；主区每秒 ≤3 字'),
       'g56': ('g68K26c', 'prompt_K26_g56_2.txt', '短块关系链', '每块 ≤30 字；大块 ≤5、小块 ≤6；主区总块数按停留 ≤20 秒 4 块、21–30 秒 5 块、更长 6 块；主区每秒 ≤2.5 字')}
TABLE = {'g6': """- K26a（你的方案）：绝对验收中等 13/8（船歌两位评委）、8/5（幻想）；骨架 3.5/3.6、3.8/3.7；覆盖核心 0.65/0.72，重要层 0.45/0.58；走样船歌 S13、S14 两处两位同报；盲比对 K11g：船歌 2/2 稳定胜、幻想 1 稳定胜 1 随座位；分项 big、concise、load 4:0 胜，core 2:1、3:1 胜，fine 船歌 1:3、幻想 0:4 输，human 4:0 输。""",
         'g56': """- K26c（你的方案）：绝对验收中等 8/13（船歌两位评委）、12/13（幻想）；骨架 3.4/3.6、3.6/3.5；覆盖核心 0.73/0.76，重要层 0.47/0.58；走样幻想 S06、S10 两处两位同报；船歌 4 颗珠子没用上；盲比对 K11g：两首都 2/2 稳定胜；分项 big、concise、load 4:0 胜，core 船歌 4:0 胜、幻想 1:1，human 4:0 输。"""}
COMMON = """- 对照 K25a（旧碎块，每块 ≤14 字、不许逗号，没有总量上限）：中等 20/10、12/5；覆盖 0.84/0.85；走样 0；但 core 输 K11g，最密的屏每秒 6.2 字。
- 对照 K11g（整句，旧主线）：中等约 40/首；覆盖 0.83/0.82。
- 关于 human 4:0：我们查出这一项评委测的是“整句还是碎块”而不是措辞——把 K11g 原文一字不改只在标点处切块，human 也是 4:0 输原版。这项在问诊，暂不作依据。不要为了它把块写长、写回整句。"""

if RND == '2':
    CFG = {'g6': ('g68K26a2', 'prompt_K26x1_g6.txt', '自然句块（第 1 次交回后放宽容量）', '大块 ≤4、小块 ≤8、合计 ≤10、主区每秒 ≤4 字'),
           'g56': ('g68K26c2', 'prompt_K26x1_g56.txt', '短块关系链（第 1 次交回后放宽容量）', '大块 ≤6、小块 ≤10、合计按停留 8/10/12、主区每秒 ≤4 字')}
    TABLE = {'g6': """- K26a2（你改过的方案）：中等 12/13（船歌两位评委）、13/17（幻想）；骨架 3.9/3.4、3.9/3.9；覆盖核心 0.76/0.87（上一版 0.65/0.72）；走样 0；盲比（第五版）船歌 1 位稳定选 K11g、幻想随座位；human 两首 4:0 输，core 3:1、1:1，fine 1:3、2:2。最密的屏连旁注每秒 5.8–6.6 字。""",
             'g56': """- K26c2（你改过的方案）：中等 18/20（船歌两位评委）、19/19（幻想），其中标准 4（不啰嗦）各 7–10 条、标准 5（人话）各 3–6 条，比上一版 8/13、12/13 多；骨架 3.7/3.7、4.0/4.0；覆盖核心 0.87/0.91（上一版 0.73/0.76，已达到旧视频水平）；走样船歌 S14 一处两位同报；盲比（第五版）两首都没有稳定输，幻想 1 位稳定选 K26c2；human 两首 4:0 输，core 2:0 输，fine 1:3、0:4。最密的屏连旁注每秒 6.8–7.1 字。"""}
    COMMON = """- 盲比评委换了第五版：human 只看措辞（不再因为不是整句扣分；校准过：K11g 原文只切块判平，同块改成电报腔的对照稳定输）。在第五版下 human 仍然 4:0 输，所以是真输——评委点的都是具体措辞（见下）。
- 对照 K11g（整句，旧主线）：中等约 40/首；覆盖 0.83/0.82。
- 这一轮的两个主要问题：①措辞为了短被压坏（删掉口语必需的成分、名词堆叠、搭配生硬）；②内容找回来了，但屏变密、重复变多（concise 中等增加）。目标是三样一起：内容保持现在的水平、每块是人平常会说的完整说法、每屏看得过来。"""


def human_why(tag):
    import glob as g
    out = []
    for f in sorted(g.glob(str(S/f'vs5_op6*_v5{tag}_*.json'))):
        w = rd(Path(f)).get('why') or ''
        i = w.find('human')
        if i >= 0: out.append('- ' + w[i:i + 260].replace(NL, ' '))
    return NL.join(out) or '（无）'


def dense(tag):
    from pub24 import R2
    import pub16
    out = []
    for w, nm in (('op60', '船歌'), ('op61', '幻想')):
        win = pub16.windows(w)
        for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
            n = sum(len(x['text']) for x in s['rows'] if x['kind'] == 'line') + sum(len(i['text']) for x in s['rows'] if x['kind'] == 'feel' for i in x['items'])
            nn = sum(len(x['text']) for x in s.get('notes') or []); sec = win[s['sec']][1] - win[s['sec']][0]
            if (n + nn)/sec > 4.5: out.append(f"- {nm} {s['sec']}：停 {sec:.0f} 秒，主区 {n} 字、旁注 {nn} 字，合计每秒 {(n + nn)/sec:.1f} 字")
    return NL.join(out) or '（无）'


def lost(tag):
    out = []
    for w, nm in (('op60', '船歌'), ('op61', '幻想')):
        us = {u['uid']: u for u in rd(S/f'units_{w}.json')}; votes = {}
        for j in ('g6', 'g56'):
            p = S/f'cov3_{w}_{j}_{tag}.json'
            if p.exists():
                for x in rd(p).get('items') or []: votes.setdefault(x['uid'], []).append(x.get('verdict'))
        for u, v in votes.items():
            if us.get(u, {}).get('tier') == '核心' and sum(1 for x in v if x == '没有')*2 > len(v): out.append(f"- {nm} {us[u]['sec']}：{us[u]['what']}")
    return NL.join(out)


ASK = """你上一轮当顾问，诊断主因是形态，并出了“{NAME}”方案（提示词附在最后）。写手（GPT-6）照它把两首都写了。请看结果，判断方向对不对；方向对就给改过的完整提示词。

【结果（两首，船歌 / 幻想）】
{TABLE}
{COMMON}

{MAIN}

【第五版盲比评委关于 human 的原话（措辞问题）】
{HUMAN}

【连旁注算、每秒超过 4.5 字的屏】
{DENSE}

【两位验收评委逐屏报的中等问题（摘要；标准编号见大众版标准）】
{ISSUES}

【意思走样（要改）】
{FAITH}

【这一版的稿子（船歌）】
{SCREEN60}

要求：
- 提示词里不放任何具体作品的内容或例子；写“这首钢琴曲”。占位符和输出格式不变（{{BUDGET}}、{{DAGSTD}}、{{FINAL}}、{{BEADS}}；输出 big / small / notes）。
- 守住用户硬要求：一块一种字号、块内强调只变色；碎块，不回到成段连贯读；只看大块能拼出整件事并串起来；不写音乐术语、调性、左右手、小节号（小节只写在 bars 字段）；一颗珠子里不同的听法都要在。
- 机械检查规则如有改动，在 checks 里写清所有数字。
只输出 JSON：{"verdict":"方向对|不行","changes":"改了哪几处、对应哪类问题","checks":"机械检查规则（全部数字）","prompt":"完整提示词"}。回答时请不要进行联网搜索。

【你上一轮的提示词】
{PROMPT}
"""


MAIN1 = """【主要问题：内容丢了】覆盖评委（逐个意思单元查屏幕上有没有，含旁注）判“确认丢失”的核心单元：
{LOST}
其中一部分是讲音乐本身的（声音、调、小节、乐句），这些应该在旁注里留住，不算主区的事；但也有真正的故事和体验（他意识到什么、心里的转折、具体的身体感觉）被删了。另有很多“部分留住”：大意在，具体的那一层没了。
你方案里的总量上限（{CAPS}）可能是主因：为了守住上限，写手把具体内容删了，而不是把重复和铺垫删了。可以改上限的数字（写清楚新的数字和理由），也可以改写法；目标是内容回到接近 K25a 的水平，同时守住你的方案在 core、big、load 上的好处。"""
MAIN2 = """【这一轮的问题】
1. 措辞（human）：第五版评委点出的都是为了短把话压坏——删掉口语里必需的动词、补语、“觉得”“心里”之类，名词堆在一起，搭配生硬。每块要是人平常会完整说出口的话（可以省主语，但不能省成电报）。
2. 密度和重复（concise、load）：内容回来了，但有的屏连旁注每秒 6–7 字，验收评委报“不啰嗦”的中等问题多了。要删的是同一意思在大块、小块、旁注里各说一遍，以及跨屏回来没带新东西的，不是删具体内容。
3. 走样（如有）：见下。
仍然确认丢失的核心单元（覆盖评委）：
{LOST}
请在不降低现在覆盖的前提下改这三样。可以调整容量数字（写清楚）。"""


def main(j):
    tag, pf, name, caps = CFG[j]; p = S/f'adv_k26x{RND}_{j}.json'
    if not p.exists():
        msg = (ASK.replace('{MAIN}', MAIN2 if RND == '2' else MAIN1).replace('{NAME}', name).replace('{TABLE}', TABLE[j]).replace('{COMMON}', COMMON).replace('{LOST}', lost(tag)).replace('{CAPS}', caps)
               .replace('{ISSUES}', issues(tag)).replace('{HUMAN}', human_why(tag) if RND == '2' else '（无）').replace('{DENSE}', dense(tag) if RND == '2' else '（无）').replace('{FAITH}', faith(tag) or '（无）').replace('{SCREEN60}', view_text('op60', tag)).replace('{PROMPT}', (S/pf).read_text(encoding='utf-8')))
        print('材料', j, len(msg), flush=True); r = None
        for k in range(3):
            try: r = parse(call(f'adv_k26x{RND}_{j}' + ('' if not k else f'_r{k}'), msg, G56 if j == 'g56' else G6, 'gpt3s', 'public24-adv')); assert r.get('prompt'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); tpl = r['prompt'].replace('{{', '{').replace('}}', '}').replace('\\"', '"').replace('S01-L1', 'S01-1')
    (S/f'prompt_K26x{RND}_{j}.txt').write_text(tpl, encoding='utf-8')
    try: prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS)\}', '', tpl), f'prompt_K26x{RND}_{j}'); print(j, '泛化检查过', flush=True)
    except SystemExit as ex: print(j, '泛化检查没过', ex, flush=True)
    print(f"== {j} {r.get('verdict')}：{r.get('changes', '')[:1500]}\n检查：{r.get('checks', '')[:1500]}", flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
