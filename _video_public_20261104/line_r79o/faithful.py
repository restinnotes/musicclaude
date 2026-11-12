"""11-08（提示词不放具体作品的例子，迭代准则硬约束 1 泛化）DAG2 标准第 4 条“不编、不走样”的测法（硬门槛）。
来由：修线（g68RHL）把疑问改成断言、加了定稿没有的“谁也没法答应永远”，现有门槛全没拦住，是人工发现的。
评委逐段对照定稿（线 + 珠子）和屏幕上的全部文字（大字小字都算），只找改了意思的地方，措辞不同不算。
python faithful.py TAG [TAG...]      → r3/s24/faith_{w}_{j}_{TAG}.json，打印每首严重条数
校准：g68RHL 必须抓到上面几处；g68RHM（改回原意）不该有严重问题。
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pub24 import S, R2, rd, wr, call, parse, JUDGES, WORKS, view_text

FAITH = """下面是一首钢琴曲视频的定稿文字和屏幕稿。定稿有两种：线（一个人经历的一件事）和珠子（听的人此刻的感受）。屏幕稿是给边听边扫的观众看的短版，把两者重新组织过：可以删、可以合并、可以换说法、可以把线和珠子写在同一句里。

请逐段对照，只找屏幕稿“改了意思”的地方。删掉内容不算（那是覆盖的事），换说法、变短、变口语不算。只算下面这些：
1. 疑问变成断言，或断言变成疑问。
2. 猜测、拿不准变成确定，或反过来。
3. 担心、想象变成已经发生。
4. 原因和结果颠倒、接错，或把没有因果的两件事写成因果。
5. 加了定稿没有的事件、画面、动作、动机、结论或判断。
6. 把珠子里的比喻、想象写成这个人真的经历的事。
7. 把定稿里并列的东西写成先后发生，或改了先后顺序。
8. 说法变笼统，丢掉了原来具体的意思。
严重：观众会因此误解这个人在想什么、发生了什么。轻微：意思偏了一点，但不致误解。拿不准的不要报。

只输出 JSON：{"issues":[{"sec":"S13","screen":"屏幕上的原话","source":"定稿里对应的话","type":"上面 1–8 的编号","severity":"严重|轻微","why":"一句"}]}，没有就给空数组。

【定稿的线】
{LINES}

【定稿的珠子】
{BEADS}

【屏幕稿（话 = 大字，【】放大；感受 = 小字）】
{SCREEN}
"""


import prompt_lint
prompt_lint.lint(FAITH, 'faithful.py')   # 准则硬约束 1：模板里不许有作品原文，有就不送出


def src_text(w):
    d = rd(R2/f'{w}_src.json')
    lines = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in d['sections'] for l in s['lines'])
    beads = '\n'.join(f"{s['sec']} [{b['id']}] {b['text']}" for s in d['sections'] for b in s['beads'])
    return lines, beads


def one(a):
    w, j, tag = a; p = S/f'faith_{w}_{j}_{tag}.json'
    if not p.exists():
        lines, beads = src_text(w)
        msg = FAITH.replace('{LINES}', lines).replace('{BEADS}', beads).replace('{SCREEN}', view_text(w, tag))
        for k in range(3):
            ans = call(f'pub24FA2_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-faith')
            try: r = parse(ans); assert isinstance(r.get('issues'), list); wr(p, r); break
            except Exception as ex: print('不合格', w, j, tag, repr(ex)[:150], flush=True)
    if not p.exists(): return None
    return [x for x in rd(p)['issues'] if x.get('severity') == '严重']


def summary(tag):
    for w in WORKS:
        sev = {j: [x for x in rd(S/f'faith_{w}_{j}_{tag}.json')['issues'] if x.get('severity') == '严重'] for j in JUDGES if (S/f'faith_{w}_{j}_{tag}.json').exists()}
        grp = {}
        for j, v in sev.items():
            for x in v: grp.setdefault((x.get('sec'), (x.get('screen') or '').replace('【', '').replace('】', '')[:8]), set()).add(j)
        cons = [k for k, js in grp.items() if len(js) >= 2]   # 11-08 校准：至少两位评委报同一处才算（单个评委零星报的不算）
        print(f"== {tag} {w} 严重条数", {j: len(v) for j, v in sev.items()}, '两位以上评委同报', len(cons), cons[:5], flush=True)
        for j, v in sev.items():
            for x in v: print(f"   {j} {x.get('sec')} 类型{x.get('type')}「{x.get('screen')}」←「{x.get('source')}」 {x.get('why')}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    tags = sys.argv[1:]
    with ThreadPoolExecutor(16) as ex: list(ex.map(one, [(w, j, t) for t in tags for w in WORKS for j in JUDGES]))
    for t in tags: summary(t)
