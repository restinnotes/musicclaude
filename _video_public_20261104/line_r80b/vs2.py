"""11-08 按 DAG2 标准修订稿（5 条）做的看片盲比：任意两版屏幕稿对比，两种先后顺序各判一次，按配对算。
分项对应标准：扫一眼抓到、连贯不跳、不啰嗦、人话；“定稿内容不丢”评委看不到原稿，另由覆盖测法管。
python vs2.py A B [名]      A、B 是 r3/s24/screen_{w}_{TAG}.json 的 TAG（可带目录前缀 ../line_r80b/r3/s24/ 不支持，先复制过来）
结果 r3/s24/vs2_{w}_{j}_{名}_{seat}.json（seat = A 放在 X 还是 Y）
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pub24 import S, rd, wr, call, parse, JUDGES, WORKS, view_text

VS2 = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。下面是同一首曲子视频屏幕的两个版本，每段屏幕只停留写明的秒数，你还在听音乐。话里【】中的字放大加亮；“感受”是小字短语；标“到时出现”的只在音乐走到那几小节时才出现。

如果你是观众，按下面几项比较（不要因为字多或字少本身加减分，按你在这几秒里实际能得到的来判断）：
- scan 扫一眼就抓到：只扫关键词，也知道这一段是什么感受、这个人此刻怎么了。
- flow 连贯不跳：读起来是一回事，不在“他的事”和“一堆感受”之间来回跳；前后段接得上。
- concise 不啰嗦：每块都有用处，同一个意思、同一种感受不说两遍。
- human 人话：像人说的，句式多变，不书面、不格言，短语不是硬切的半句。
- why 知道这个人为什么这样。
- alone 只扫屏幕也看得出这是一个人有发展的一件事，一步步往前走，不来回绕。
- fine 感受细腻具体，不粗糙。

只输出 JSON：{"better":"X|Y","nets":{"scan":"X|Y|平","flow":"X|Y|平","concise":"X|Y|平","human":"X|Y|平","why":"X|Y|平","alone":"X|Y|平","fine":"X|Y|平"},"why":"两三句"}

【X】
{X}

【Y】
{Y}
"""
DIMS = ['scan', 'flow', 'concise', 'human', 'why', 'alone', 'fine']


import prompt_lint
prompt_lint.lint(VS2, 'vs2.py')   # 准则硬约束 1：模板里不许有作品原文，有就不送出


def one(a):
    w, j, A, B, name, seat = a; p = S/f'vs2_{w}_{j}_{name}_{seat}.json'
    if p.exists(): return
    a1, b1 = view_text(w, A), view_text(w, B); x, y = (a1, b1) if seat == 'X' else (b1, a1)
    for k in range(3):
        ans = call(f'pub24V2_{w}_{j}_{name}_{seat}'+('' if not k else f'_r{k}'), VS2.replace('{X}', x).replace('{Y}', y), JUDGES[j], 'gpt3s', 'public24-vs2')
        try: r = parse(ans); assert r['better'] in 'XY'; wr(p, r); return
        except Exception as ex: print('不合格', w, j, name, seat, repr(ex)[:120], flush=True)


def report(name):
    for w in WORKS:
        st = {'A': 0, '敏感': 0, 'B': 0}; dims = {d: [0, 0] for d in DIMS}
        for j in JUDGES:
            px, py = S/f'vs2_{w}_{j}_{name}_X.json', S/f'vs2_{w}_{j}_{name}_Y.json'
            if not (px.exists() and py.exists()): continue
            rx, ry = rd(px), rd(py); ax, ay = rx['better'] == 'X', ry['better'] == 'Y'
            st['A' if ax and ay else 'B' if not (ax or ay) else '敏感'] += 1
            for r, seat in ((rx, 'X'), (ry, 'Y')):
                for d in DIMS:
                    v = (r.get('nets') or {}).get(d)
                    if v in ('X', 'Y'): dims[d][0 if v == seat else 1] += 1
        print(f"{name} {w}：稳定选 A {st['A']}、位置敏感 {st['敏感']}、稳定选 B {st['B']}；分项 A:B " + '、'.join(f"{d} {a}:{b}" for d, (a, b) in dims.items()), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    A, B = sys.argv[1], sys.argv[2]; name = sys.argv[3] if len(sys.argv) > 3 else f'{A}__{B}'
    with ThreadPoolExecutor(16) as ex: list(ex.map(one, [(w, j, A, B, name, s) for w in WORKS for j in JUDGES for s in 'XY']))
    report(name)
