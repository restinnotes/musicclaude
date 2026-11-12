"""11-11 迭代准则 I01 的开放评审（不给标准）。用户 11-09：“评委理由对不对的上标准 这个如果我们硬给她标准 不就是没有起到开放评委的作用吗 我记得开放评委也是必要的？效果很好的？”
旧的 open_review.py 把大众版标准整份给了评审，又只跑到 K10 一轮就停了。这一版不给标准、不给我们的判断，只说明观众和画面，让它按普通读者和挑剔编辑的眼光找最大的问题。只找问题，不打分，不进门槛；它报的问题由我对照标准归类，对不上标准的记下来（可能是标准漏了的）。
python r3/open_free.py TAG → r3/s24/openF_{作品}_{评委}_{TAG}.json
11-11 校准（用户：“开放评审是可以去校准的 比如我们之前提到他现在的第一条建议就不予采纳 可能可以校准 但是不能关啊……也不能把他改成‘不是开放’的评委”）：
仍不给标准、不给检查单；只附几条已经定下、有理由的取舍（OF_V=2，结果 openF2_*）。校准对照：K28b 第一版的头号问题是“没有发生的事”；第二版应不再把它当问题，
但打转、心理分析腔、比喻重复、出戏仍要报得出来——报不出来就是校准过头，退回第一版。
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')
OPEN = """下面是一首钢琴曲“边听边看”视频的屏幕文字稿：普通观众第一次看，边听音乐边扫屏幕，每屏只停留写明的秒数。“话”是大字，“感受”是小字，旁注挂在音符旁边。这些文字想让观众跟着音乐感受到一个人经历的一件事和这一刻的体验。

{DECIDED}请你同时当两个人来读：一个是第一次看的普通观众，一个是挑剔的中文编辑。读完以后，直说这份稿子最让人不舒服、最不对劲的地方是什么，不用客气，也不用面面俱到。
- 先写总的读后感：读下来像什么、哪里读不下去、哪里出戏。
- 再列具体问题，按严重程度从大到小，最多十五条。每条写屏号、原文、问题是什么、观众会怎样。
- 不要打分，不要夸，不要提修改建议以外的客套话。

只输出 JSON：{"overall":"读后感","issues":[{"sec":"S05","quote":"原文","problem":"问题是什么","effect":"观众会怎样","rank":1}]}

【屏幕稿】
{SCREEN}
"""
import os
VER = os.environ.get('OF_V', '3')
DECIDED = """【已经定下的几条取舍（有意的，不要因为这几点本身报问题；但下面括号里说的情况照样要报）】
- 故事不靠外部发生的事、对白、动作来推动，写的是一个人此刻的心理处境，这是有意的。（但处境的性质读不出来、他对别人心思的推断没有依据、心理在原地打转，照样要报。）
- 小字里并列的几种不同听法、不同画面，来自不同听众真实的感受，是有意并列的。（但同一种体验换几个比喻重复说、比喻和此刻的处境对不上、读着出戏，照样要报。）
- 字在画面上怎么出现、留多久、怎么排版，是画面那一层另外处理的；这里只看文字本身。

""" if VER == '2' else ''
PURPOSE = """【它是什么】
屏幕上的字有两个来源：一条“线”，是一个人在这首曲子里经历的一件事，从整首曲子的核心处境长出来，写他此刻怎么了、为什么这样；还有“珠子”，是不同的听众在这一刻听到的感受、画面、比喻。屏幕上把两者揉在一起：“话”（大字）是必看的，只看大字就要明白这一刻他怎么了、为什么；“感受”（小字）是补充，不读也不影响理解。

【它想做到的几件事】
- 只看大字也能顺着读下来，像一个人在往下讲他的事，一步步往深处走，不在几种状态之间来回打转；整首看得出讲的是一件核心的事。
- 读起来像人平常说话，不像心理分析、提纲或格言。
- 感受具体、有画面、有身体感觉，不是笼统的情绪词；小字补的是大字没有的东西，不是把大字换个说法再说一遍。
- 不啰嗦，扫得过来。

【不算缺点】
戏剧化、主观、只讲一个故事；含蓄，不要求补造具体人物、事件、对白或场景；几种不同的听法并列。
你不知道作者改过什么，不要预先假定它有哪些毛病；做得好的不用提，也不要为了凑数挑毛病。上面没说到的问题，只要你作为观众或编辑觉得不对，也照样要说。

"""
# 11-11 第三版：照 11-01 效果好的开放评审（e2e_open.py）的写法校准——告诉它这是什么、想做到什么、哪些不算缺点，不列禁区、不给标准和检查单（用户：“我说的校准是校准开放评委的提示词啊 比如说我们的目的什么的……我担心他现在不开放了”）。第二版的“已定取舍”撤掉。
OPEN = OPEN.replace('{DECIDED}', PURPOSE if VER == '3' else DECIDED)
prompt_lint.lint(OPEN, 'open_free.py')
tag = sys.argv[1]


def one(a):
    w, j, m = a; p = S/f"openF{'' if VER == '1' else VER}_{w}_{j}_{tag}.json"
    if p.exists(): return
    msg = OPEN.replace('{SCREEN}', view_text(w, tag))
    for k in range(3):
        rid = f"pub24OF{'' if VER == '1' else VER}_{w}_{j}_{tag}" + ('' if not k else f'_r{k}')
        if j == 'argon':   # 11-11 用户：Gemini 那一路“argon就行”；Argon 当第三位开放评审的对比试验（只找问题，不当顾问）
            sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); import evo
            ans = evo.call_argon_direct(rid, msg, meta={'stage': 'public24-openfree-argon'})
        else: ans = call(rid, msg, m, 'gpt3s', 'public24-openfree')
        try: r = parse(ans); assert 'issues' in r; wr(p, r); print(w, j, tag, len(r['issues']), '｜', r.get('overall', '')[:200], flush=True); return
        except Exception as ex: print('不合格', w, j, repr(ex)[:120], flush=True)


JS = [('g6', G6), ('g56', G56)] + ([('argon', None)] if os.environ.get('OF_ARGON') else [])
with ThreadPoolExecutor(6) as ex: list(ex.map(one, [(w, j, m) for w in WORKS for j, m in JS]))
