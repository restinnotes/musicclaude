"""11-09 凌晨 绝对尺度的开放评审（两位顾问问诊 judge_check/openrev_* 后的共同方案）。
旧开放评审没有绝对轻重标准，只有跨段问题标轻重；每版都报 5–13 条中等以上，盲比明显更好的版本严重条数不减反增，像是在每版内部重新排轻重。
新版：每条问题都按固定的绝对尺度标轻重（只看对观众的实际影响，不看它是不是这一版最突出的）；只是“还能写得更好”的不算问题；
出现次数多不自动升级；七条标准逐条给结论（过 / 有问题 / 不可评估）；没有达到门槛就写没有。
python r3/openabs.py TAG [轮次标记]     结果 r3/s24/openA_{作品}_{评委}_{TAG}_{轮次}.json
"""
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blend, prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')

OPENA = """你是验收评审。下面是一首钢琴曲大众版“边听边看”视频的屏幕稿：普通观众第一次看，边听边扫，每段屏幕只停留写明的秒数。【】中的字放大加亮（话里有，长一点的感受里也可能有）；“感受”是小字短语；标“到时出现”的，音乐走到它对应的那几小节时才出现（那几小节里加亮），之后留在屏幕上，直到这一屏结束。

请按下面的大众版标准做验收：逐条标准判断它在这份屏幕稿上过没过，再列出确实存在的问题。

【轻重的绝对尺度——只按问题对观众的实际影响判断，不按它是不是这一版里最突出的问题判断】
- 严重：在给定停留时间、第一次看的条件下，普通观众很可能看不懂这个人的关键经历、行动、必要的因果或核心的情绪转折；或者关键文字来不及读到，故事主干断开。
- 中等：主要意思能看懂，但有明确的额外理解成本：要自己补因果、回头看、反复辨认，或者明显打断一次扫读的连贯。
- 轻微：第一次扫读就能看懂，没有实质损失；只是措辞、局部重复、表达精度或节奏上可以更好。
- 不构成问题：只是能想到别的写法、个人偏好、理论上的改进空间，没有可说明的观看损害——这类不要列出来。
规则：
1. 同一把尺子用在任何版本上。一份稿子即使只剩一个问题，它也可能只是轻微。
2. 出现次数多不自动升级：一种轻微问题出现很多次，只有在确实造成累积的阅读负担时才算中等，并说明负担在哪里。
3. 情感留白、需要稍微体会一下的细腻表达，不算理解成本。
4. 第 5 条（定稿内容不丢）需要对照定稿原文，这里没有提供，标“不可评估”，不要因此报问题。
5. 没有达到“轻微”门槛的地方，不用找；某条标准没有问题就写“过”。

【标准】
{STD}

只输出 JSON：{"standards":[{"std":"1","verdict":"过|有问题|不可评估","note":"一句"}],"issues":[{"sec":"S05 或 跨段","std":"标准编号","quote":"原文（跨段的写两三处）","why":"对观众的实际影响是什么","severity":"严重|中等|轻微"}]}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(OPENA, 'openabs.py')


def one(a):
    w, j, m, tag, run = a; p = S/f'openA2_{w}_{j}_{tag}_{run}.json'   # 11-09：openA2 = “到时出现”的描述改成和渲染器一致（到时出现、留到这屏结束）
    if p.exists(): return rd(p)
    msg = OPENA.replace('{STD}', blend.DAGSTD).replace('{SCREEN}', view_text(w, tag))
    for k in range(3):
        ans = call(f'pub24OA2_{w}_{j}_{tag}_{run}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-openabs')
        try: r = parse(ans); assert 'issues' in r; wr(p, r); return r
        except Exception as ex: print('不合格', w, j, tag, run, repr(ex)[:120], flush=True)


def summary(tag, runs):
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                p = S/f'openA2_{w}_{j}_{tag}_{run}.json'   # 11-09：openA2 = “到时出现”的描述改成和渲染器一致（到时出现、留到这屏结束）
                if not p.exists(): row.append('缺'); continue
                r = rd(p); c = Counter(x.get('severity') for x in r.get('issues') or [])
                bad = [s.get('std') for s in r.get('standards') or [] if s.get('verdict') == '有问题']
                row.append(f"严重 {c['严重']}、中等 {c['中等']}、轻微 {c['轻微']}；有问题的标准 {','.join(bad) or '无'}")
            print(f"绝对验收 {tag} {w} {j}： " + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    tags = [t for t in sys.argv[1:] if not t.startswith('run')]; runs = [t for t in sys.argv[1:] if t.startswith('run')] or ['run1']
    jobs = [(w, j, m, t, run) for t in tags for run in runs for w in WORKS for j, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(min(12, len(jobs))) as ex: list(ex.map(one, jobs))
    for t in tags: summary(t, runs)
