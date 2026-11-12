"""11-09 晚 绝对验收第四版（11-09 晚标准换成 8 条后：编号对上新标准、给评委 Center 一句话判第 3 条、调用编号前缀换 OA4）。以下是第三版的说明：
11-09 晚 绝对验收第三版（迭代准则第七节：两位顾问 adv_k22_{g6,g56} 的 measure_fix 独立指向同一根因——旧版读全文、尺度太松，
没有逐屏逐条判，线打转、按来源分开、跨屏重复、小字讲音乐本身都漏掉；K11g 8 次只报 4 条中等，用户估内容三成）。
改法（两位的共同部分）：逐屏、逐条标准判；每屏先写“相对前面新增了什么”；结构性问题明确定为中等或严重，不许降为轻微；
每条非轻微问题写屏号、原文、标准编号；禁止“像清单”“通读不顺”这类无法核对的评语。扫读的最终判断仍以截图评委为准。
校准：K11g 两遍（同版稳定）+ 只改一处的人造对照（ctl.py）：CL 后半几屏的话换成前面的话（打转）、CS 每屏先全部话后全部感受（分开）、
CN 删掉讲音乐本身的小字（正向）、CV 小字全换成笼统情绪词（不细腻）。
python r3/openabs3.py TAG [轮次]    结果 r3/s24/openA3_{作品}_{评委}_{TAG}_{轮次}.json
python r3/openabs3.py sum TAG 轮次...
"""
import sys, os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blend, prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')

OPENA3 = """你是验收评审。下面是一首钢琴曲大众版“边听边看”视频的屏幕稿：普通观众第一次看，边听边扫（扫得很快、抓关键词），每屏只停留写明的秒数。“话”是大字，【】中的字更大更亮；“感受”是小字短块；标“到时出现”或“第几秒出现”的，到那时才出现，之后留到这一屏结束。
目标只有一句：一眼要能扫过去，读起来要能串起来——扫的人顺着一屏屏看下来，看得出这个人的事怎么一步步往前走，感受和他的处境是一回事。

请按下面的标准逐屏验收。

【做法】
1. 从第一屏开始按顺序看。每一屏先写一句：和前面所有屏相比，这一屏让观众新知道了什么（他的处境、认识、愿望、顾虑或选择有什么新变化）；没有新东西就写“无新东西，重复了第几屏的什么”。
2. 再按标准 1、2、4、5、7、8 逐条看这一屏，列出确实存在的问题（第 6 条要对照定稿原文，这里不评）。“话”是大块，“感受”是小块，“旁注”在可视化旁边。
3. 最后看全曲：顺着读下来，这个人的事是在往深处走，还是在几种状态之间来回打转；同一个意思、同一个事实是不是跨屏反复出现却没有带出新东西（原料里不同的理解、不同层的体验不算重复）；按标准第 3 条，看得出讲的是不是这首曲子的核心（核心是：{CENTER}）。

【轻重的绝对尺度】
- 严重：看不出这个人此刻为什么这样、关键转折看不出；人物往哪走辨认不出；这一屏基本读不出人物的事；这一屏的“他的事”和“感受”明显是两回事、按来源分成两块，读起来来回跳；意思错误（疑问写成断言、猜测写成确定、听的人的比喻写成他真的经历的事）；整屏在停留时间里根本扫不完。
- 中等：只看大块拼不出这一屏的主要意思；意思还在，但要观众费力推理或回头看；一条里挤了两层以上意思的长句（大块小块都算）；一块里有的字大有的字小；这一屏相对前面没有新东西，或人物在打转；同一屏或跨屏重复同一种感受、同一个事实；体验被说成笼统的情绪词；某一块和旁边的内容接不上；小字在讲音乐本身（声部、左右手、和弦、技法、调性），而不是观众此刻的体验；块太多或太密，扫的时候抓不到重点；不像人平常说话（书面腔、心理分析、格言、工整对称句、句子彼此太像）。
- 轻微：不影响理解和扫读的个别措辞、标点、一处非核心的小重复。
规则：
1. 同一把尺子用在任何版本上；剩下的问题都轻微的版本，就照实写都轻微。
2. 结构性问题（大块拼不出意思、打转、分开、跨屏重复、多层长句、主区讲音乐本身）不许降为轻微。
3. 每条中等以上的问题都要写屏号、原文（跨屏的写两三处）、违反的标准编号和对观众的具体影响；“像清单”“像摘录”“通读不顺”这类说法不算理由——短语、半句、清单式排列本身不是问题，只看扫不扫得到、串不串得起来。
4. 情感留白、要稍微体会一下的细腻表达，不算理解成本。

【标准】
{STD}

只输出 JSON：{"screens":[{"sec":"S01","new":"新知道了什么，或“无新东西，重复了第几屏的什么”","issues":[{"std":"标准编号","quote":"原文","why":"对观众的具体影响","severity":"严重|中等|轻微"}]}],"whole":[{"std":"标准编号","quote":"跨屏的两三处原文","why":"…","severity":"严重|中等|轻微"}],"verdict":"一句话：离“剩下的问题都轻微”还差什么"}，所有屏都要有。

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(OPENA3, 'openabs4')


def one(a):
    w, j, m, tag, run = a; p = S/f'openA4_{w}_{j}_{tag}_{run}.json'
    if p.exists(): return rd(p)
    msg = OPENA3.replace('{STD}', blend.DAGSTD).replace('{SCREEN}', view_text(w, tag)).replace('{CENTER}', rd(R2/f'{w}_src.json')['center'])
    for k in range(3):
        ans = call(f'pub24OA4_{w}_{j}_{tag}_{run}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-openabs3')
        try: r = parse(ans); assert 'screens' in r; wr(p, r); return r
        except Exception as ex: print('不合格', w, j, tag, run, repr(ex)[:120], flush=True)


def issues(r):
    return [dict(x, sec=s.get('sec')) for s in r.get('screens') or [] for x in s.get('issues') or []] + [dict(x, sec='全曲') for x in r.get('whole') or []]


def summary(tag, runs):
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                p = S/f'openA4_{w}_{j}_{tag}_{run}.json'
                if not p.exists(): row.append('缺'); continue
                r = rd(p); iss = issues(r); c = Counter(x.get('severity') for x in iss)
                std = Counter(str(x.get('std')) for x in iss if x.get('severity') in ('严重', '中等'))
                nonew = sum(1 for s in r.get('screens') or [] if str(s.get('new', '')).startswith('无'))
                row.append(f"严重 {c['严重']}、中等 {c['中等']}、轻微 {c['轻微']}（中等以上按标准 {dict(sorted(std.items()))}；无新东西 {nonew} 屏）")
            print(f'绝对验收4 {tag} {w} {j}： ' + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'sum': summary(sys.argv[2], sys.argv[3:] or ['run1']); sys.exit()
    tag = sys.argv[1]; run = sys.argv[2] if len(sys.argv) > 2 else 'run1'
    jobs = [(w, j, m, tag, run) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, jobs))
    summary(tag, [run])
