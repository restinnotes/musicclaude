"""11-10 盲比第五版（11-10 午 load 按新第 8 条改成只算大块，之后的结果名用 v5b 前缀；由 vs4.py 复制改 human、load；第四版的 human 混进了“整句还是碎块”的格式偏好：K11g 原文只切块 human 也 4:0 输，七个碎块候选全 4:0；GPT-6、GPT-5.6 问诊印证，见 judge_check/vs4human_*）。
原第四版说明：。起因：标准 11-09 晚换成 8 条；vs3b 还是旧分项，K24 对 K11g 的理由里有“完整句子更连贯”“关键词有字号层级更醒目”，
和新标准（一块一种字号；只看大块能明白并串起来）相反（迭代准则第七节：理由对不上标准就查评委）。
改：分项照新标准；如实说明两种格式（整句里放大几个词 / 一块一种字号的碎块），不预设哪种好；“长句通顺”不加分。
校准：K11g 对 K11g 的副本（应全是平或随座位）；K11g 对打转对照 CL（core/alone 应选 K11g）；K11g 对笼统对照 CV（fine 应选 K11g）。
python r3/vs4.py A B 名     结果 r3/s24/vs4_{w}_{j}_{名}_{X|Y}.json（X 座位放 A）；python r3/vs4.py sum 名
"""
import sys, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, JUDGES, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')

VS4 = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。下面是同一首曲子视频屏幕的两个版本，每屏只停留写明的秒数。
两个版本的格式可能不同：有的是整句话、其中几个词【】放大加亮；有的是一块一块的碎块，“话”是大块（整块一样大），“感受”是小块，【】只换颜色。格式本身不加分也不减分，只按观众实际能得到的比较。

按下面几项比较，每项选更好的一边，差不多就判平：
- big 只看大字（放大加亮的词，或大块）：能不能明白这一屏最主要的东西——他此刻怎么了、为什么、最主要的体验——而且一屏屏串得起来。
- small 小字：补得有没有用、挂不挂得上；读了不跳，不读也不影响理解。
- core 全曲扫下来，看得出讲的是这首曲子核心的那件事（核心是：{CENTER}），没有被感受淹没或偏走。
- concise 不啰嗦：同一个意思不说两遍（同一屏大字小字各说一遍、跨屏回来没带新东西都算）；逻辑简单、不绕。一颗珠子里不同的听法不算重复。
- human 语言自然度：只看文字本身是否符合人平常说话的习惯。按屏上出现的顺序理解整串表达，可以结合本屏相邻块和上下屏；视觉上的分块只是排版，不等于句号。碎块可以是自然的短语、分句、承接片段，可以自然省略主语和已经交代过的信息。
  扣分的情况：为了短删掉了口语里实际需要的成分、表达生硬；文言式、书面摘要腔；标签式词组、名词堆叠；搭配、语序、语气不像日常口语；主语、指代或前后关系省略过度，意思恢复不出来。
  不能单独作为扣分理由：一块不是完整句子；一块没有主语；几块要结合上下文理解；不是连续的一整段叙述。完整句子、连接词多不自动更自然；碎块和自然省略也不自动不自然。
  判某一边更不自然，必须指出具体的词语、搭配、语序、语气或省略问题；如果唯一的理由是“完整叙述更自然”“整句更像口语”“碎块不完整”，判平。两版措辞、顺序完全相同、只是分块不同时，human 判平，分块造成的问题放到 load。
- fine 留下来的感受具体、有辨识度，没被说成笼统的情绪词；讲观众此刻的体验，不讲音乐本身。
- load 扫得动（11-10 午标准第 8 条改）：只看大块的观众在停留时间里看得过来——大块的数量、每块长短和停留时间相称，切分落在自然的意群边界、不悬空。小块和旁注是给想多看的人的，不要求在停留时间里读完，不按它们的字数算负担；但它们要在视觉上退后，不能多到让人找不到大块、分不清哪些是必看的。一块里不混字号。整句读起来通顺不等于扫得动。

只输出 JSON：{"better":"X|Y|平","nets":{"big":"X|Y|平","small":"X|Y|平","core":"X|Y|平","concise":"X|Y|平","human":"X|Y|平","fine":"X|Y|平","load":"X|Y|平"},"why":"两三句，每条理由说对应哪一项"}

【X】
{X}

【Y】
{Y}
"""
prompt_lint.lint(VS4, 'vs5')
DIMS = ['big', 'small', 'core', 'concise', 'human', 'fine', 'load']


def one(a):
    w, j, A, B, name, seat = a; p = S/f'vs5_{w}_{j}_{name}_{seat}.json'
    if p.exists(): return
    a1, b1 = view_text(w, A), view_text(w, B); x, y = (a1, b1) if seat == 'X' else (b1, a1)
    msg = VS4.replace('{CENTER}', rd(R2/f'{w}_src.json')['center']).replace('{X}', x).replace('{Y}', y)
    for k in range(3):
        try: r = parse(call(f'pub24V5_{w}_{j}_{name}_{seat}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-vs5')); assert r['better'] in ('X', 'Y', '平'); wr(p, r); return
        except Exception as ex: print('不合格', w, j, name, seat, repr(ex)[:120], flush=True)


def report(name):
    for w in WORKS:
        st = {'A': 0, '敏感': 0, 'B': 0}; dims = {d: [0, 0] for d in DIMS}
        for j in JUDGES:
            px, py = S/f'vs5_{w}_{j}_{name}_X.json', S/f'vs5_{w}_{j}_{name}_Y.json'
            if not (px.exists() and py.exists()): continue
            rx, ry = rd(px), rd(py)
            sc = (1 if rx['better'] == 'X' else 0 if rx['better'] == '平' else -1) + (1 if ry['better'] == 'Y' else 0 if ry['better'] == '平' else -1)
            st['A' if sc == 2 else 'B' if sc == -2 else '敏感'] += 1
            for r, seat in ((rx, 'X'), (ry, 'Y')):
                for d in DIMS:
                    v = (r.get('nets') or {}).get(d)
                    if v in ('X', 'Y'): dims[d][0 if v == seat else 1] += 1
        print(f"盲比5 {name} {w}（A 在前）：稳定选 A {st['A']}、随座位或平 {st['敏感']}、稳定选 B {st['B']}；分项 A:B " + '、'.join(f"{d} {a}:{b}" for d, (a, b) in dims.items()), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'sum': report(sys.argv[2]); sys.exit()
    A, B, name = sys.argv[1:4]
    js = [j for j in JUDGES if j in ('g6', 'g56')]
    with ThreadPoolExecutor(8) as ex: list(ex.map(one, [(w, j, A, B, name, seat) for w in WORKS for j in js for seat in ('X', 'Y')]))
    report(name)
