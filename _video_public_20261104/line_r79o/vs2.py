"""11-08 按 DAG2 标准修订稿（5 条）做的看片盲比：任意两版屏幕稿对比，两种先后顺序各判一次，按配对算。
分项对应标准：扫一眼抓到、连贯不跳、不啰嗦、人话；“定稿内容不丢”评委看不到原稿，另由覆盖测法管。
python vs2.py A B [名]      A、B 是 r3/s24/screen_{w}_{TAG}.json 的 TAG（可带目录前缀 ../line_r80b/r3/s24/ 不支持，先复制过来）
结果 r3/s24/vs2_{w}_{j}_{名}_{seat}.json（seat = A 放在 X 还是 Y）
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pub24 import S, rd, wr, call, parse, JUDGES, WORKS, view_text

VS2 = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。下面是同一首曲子视频屏幕的两个版本，每段屏幕只停留写明的秒数，你还在听音乐。【】中的字放大加亮（话里有，长一点的感受里也可能有）；“感受”是小字短语；标“到时出现”的只在音乐走到那几小节时才出现。

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


import os, prompt_lint
prompt_lint.lint(VS2, 'vs2.py')   # 准则硬约束 1：模板里不许有作品原文，有就不送出

# 11-08 晚 vs3（PUB_VS3=1）：两位顾问问诊（judge_check/coverfine_*）一致认为 fine 只写“细腻具体，不粗糙”，评委实际在比细节多少，
# 和 concise 成了跷跷板（字少的版本 fine 0:8、concise 8:0，字多的反过来）。按大众版标准第 6 条（只问留下的够不够具体）和第 3 条（看信息是否重复）改写两项，
# 整体也允许判“平”（两版一样时不再被迫选一个）。结果另存 vs3_*，不和旧结果混。
VS3 = os.environ.get('PUB_VS3') == '1'
PRE, RID = ('vs3', 'pub24V3') if VS3 else ('vs2', 'pub24V2')
# 11-09 凌晨 vs3b（PUB_VS3B=1，在 vs3 上）：评委提示词把“到时出现”说成“只在那几小节出现”，但渲染器（film_v8.draw_page）是到时出现、之后留到这一屏结束。
# 绝对验收里幻想反复报的中等问题“到时出现的长句读到一半就消失”就是按这个错误前提判的。改成和成片一致；结果另存 vs3b_*。
VS3B = os.environ.get('PUB_VS3B') == '1'
if VS3B:
    PRE, RID = 'vs3b', 'pub24V3b'
    VS2 = VS2.replace("标“到时出现”的只在音乐走到那几小节时才出现。", "标“到时出现”的，音乐走到它对应的那几小节时才出现（那几小节里加亮），之后留在屏幕上，直到这一屏结束。")
    assert '直到这一屏结束' in VS2
if VS3:
    VS2 = VS2.replace("- concise 不啰嗦：每块都有用处，同一个意思、同一种感受不说两遍。", """- concise 不啰嗦：每块都有用处，同一个意思、同一种感受不说两遍。看信息是否重复，不看情绪类别是否相同：几块只是用不同比喻重复同一个画面、身体感觉或情绪质地，没有新东西，就是重复；分别给出不同的画面、身体感觉、情绪层次、原因或转折，即使是同一种情绪，也不算重复。必要的连接、因果、转折不算啰嗦；字数多少不直接决定这一项。""").replace("- fine 感受细腻具体，不粗糙。", """- fine 细腻具体：只看屏幕上实际留下的感受表达是否具体、准确、有辨识度（明确的画面、动作、身体感觉、细微的情绪质地、比喻独有的意思、心里话），有没有被换成笼统的情绪词或泛泛的“声音”“感觉”。不看留了多少条、比喻有几个、字多字少：同一种感受多几个相近的比喻不算更细腻，删掉重复的也不算变粗；一个准确具体的说法就足够。某样内容整个没了，不在这一项扣（那是另一项的事）；只有留下来的说法本身从具体变成笼统，才算变粗。""").replace('"better":"X|Y"', '"better":"X|Y|平"')
    assert 'fine 细腻具体：只看' in VS2 and 'X|Y|平"' in VS2
    prompt_lint.lint(VS2, 'vs2.py VS3')


def one(a):
    w, j, A, B, name, seat = a; p = S/f'{PRE}_{w}_{j}_{name}_{seat}.json'
    if p.exists(): return
    a1, b1 = view_text(w, A), view_text(w, B); x, y = (a1, b1) if seat == 'X' else (b1, a1)
    for k in range(3):
        ans = call(f'{RID}_{w}_{j}_{name}_{seat}'+('' if not k else f'_r{k}'), VS2.replace('{X}', x).replace('{Y}', y), JUDGES[j], 'gpt3s', 'public24-vs2')
        try: r = parse(ans); assert r['better'] in ('X', 'Y', '平'); wr(p, r); return
        except Exception as ex: print('不合格', w, j, name, seat, repr(ex)[:120], flush=True)


def report(name):
    for w in WORKS:
        st = {'A': 0, '敏感': 0, 'B': 0}; dims = {d: [0, 0] for d in DIMS}
        for j in JUDGES:
            px, py = S/f'{PRE}_{w}_{j}_{name}_X.json', S/f'{PRE}_{w}_{j}_{name}_Y.json'
            if not (px.exists() and py.exists()): continue
            rx, ry = rd(px), rd(py)
            sc = (1 if rx['better'] == 'X' else 0 if rx['better'] == '平' else -1) + (1 if ry['better'] == 'Y' else 0 if ry['better'] == '平' else -1)
            st['A' if sc == 2 else 'B' if sc == -2 else '敏感'] += 1
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
