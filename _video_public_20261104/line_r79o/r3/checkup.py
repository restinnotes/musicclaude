"""11-11 体检：用户这几天指出过的问题，逐条在当前版本上查一遍（用户：“我担心还有一些其他问题 我不指出来或者现在不体检一次就还会有问题的”）。
条目从 `_dag2_video_20261104/要求清单.md` 里用户的原话归纳，写成通用的检查项（不放具体作品的内容）；只用来查成品，不进写手提示词。
每项让评委列出全部出现的地方（屏号、原文、为什么），两位各查一遍；两位都报的同一屏算“确认”。
python r3/checkup.py TAG     → r3/s24/check_{作品}_{评委}_{TAG}.json
python r3/checkup.py sum TAG [TAG2 ...]
"""
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')

ITEMS = [
    ('U1', '大字单独读，不像一个正常人平常会说出口的话：像给心理状态贴标签、像摘要、电报腔、书面词，或搭配、语序、省略别扭，要在脑子里翻成正常说法'),
    ('U2', '一屏的大字按出现顺序连着读，不像一个人在往下讲：一条条各自成立的结论，前后接不上，要观众自己补出关系'),
    ('U3', '像把原来一句话截断或硬切开：半句、断在不该断的地方、读着像被剪掉了一截'),
    ('U4', '按来源泾渭分明：大字全是“他的事”，小字全是“一堆感受”，两边读起来是两回事'),
    ('U5', '主区（大字或小字）在讲音乐本身（声部、左右手、和弦、音型、像什么乐器、旋律怎么走），而不是观众此刻的体验'),
    ('U6', '相邻几屏重复：几乎同样的感受、画面或事实又说一遍，没有带出新东西'),
    ('U7', '只看大字，这一屏在停留时间里看不过来：大字太多、太长'),
    ('U8', '小字多到让人找不到大字、分不清哪些是必看的'),
    ('U9', '感受被压成笼统的情绪词或抽象词，原来具体的画面、身体感觉、比喻、心里话没了'),
    ('U10', '一屏里的几块用出现先后造出了本来没有的先后（并列的东西读成了时间顺序）'),
    ('U11', '只看大字拼不出这一屏在讲什么：他此刻怎么了、为什么'),
    ('U12', '全曲读下来，人物在几种状态之间来回打转，看不出事情怎么一步步往前走'),
    ('U13', '一块里塞了两层以上的意思，一眼读不完'),
    ('U14', '指代不清：“他”“对方”“那”“这”指谁、指什么，要回头找'),
    ('U15', '正文里出现小节号、时间、乐理术语'),
]
NL = chr(10)
CHK = """下面是一首钢琴曲“边听边看”视频的屏幕文字稿：普通观众第一次看，边听边扫，每屏只停留写明的秒数。“话”是大字（必看），“感受”是小字（补充），旁注挂在音符旁边、到时出现。

下面是一张检查单，每一项是之前看过这类稿子的人指出过的毛病。请逐项检查这份稿子：这项毛病在哪些屏出现了，全部列出来（屏号、原文、一句话为什么）。没有就写空列表，不要硬找；有就列全，不要只举一两个例子。只检查，不打分，不提建议。

【检查单】
{ITEMS}

只输出 JSON：{"checks":[{"id":"U1","hits":[{"sec":"S05","quote":"原文","why":"一句话"}]}]}，每一项都要有。

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(CHK, 'checkup.py')


def one(a):
    w, j, m, tag = a; p = S/f'check_{w}_{j}_{tag}.json'
    if p.exists(): return rd(p)
    msg = CHK.replace('{ITEMS}', NL.join(f'{i}：{t}' for i, t in ITEMS)).replace('{SCREEN}', view_text(w, tag))
    for k in range(3):
        ans = call(f'pub24CK_{w}_{j}_{tag}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-checkup')
        try: r = parse(ans); assert 'checks' in r; wr(p, r); return r
        except Exception as ex: print('不合格', w, j, tag, repr(ex)[:120], flush=True)


def summary(tags):
    for w in WORKS:
        print('==', w)
        rows = {}
        for tag in tags:
            h = {}
            for j in ('g6', 'g56'):
                p = S/f'check_{w}_{j}_{tag}.json'
                h[j] = {c['id']: {x.get('sec') for x in c.get('hits') or []} for c in rd(p)['checks']} if p.exists() else None
            rows[tag] = h
        print('检查项'.ljust(6), ' ｜ '.join(f'{t}（甲/乙/两位都报的屏）' for t in tags))
        for i, txt in ITEMS:
            cells = []
            for tag in tags:
                h = rows[tag]
                if not h['g6'] or not h['g56']: cells.append('缺'); continue
                a, b = h['g6'].get(i, set()), h['g56'].get(i, set())
                cells.append(f"{len(a)}/{len(b)}/{len(a & b)} {''.join(sorted(s[1:] + ' ' for s in a & b if s)).strip()}")
            print(i.ljust(4), txt[:24].ljust(24), ' ｜ '.join(cells))


if __name__ == '__main__':
    if sys.argv[1] == 'sum': summary(sys.argv[2:]); sys.exit()
    tag = sys.argv[1]
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j, m, tag) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
    summary([tag])
