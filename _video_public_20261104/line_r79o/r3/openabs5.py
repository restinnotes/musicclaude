"""11-10 晚 绝对验收第五版（评委矫正 judge_check/oa4_renhua：两位顾问 A 轮独立指向同一根因——评委先概括“新知道了什么”，
概括时自己补上了因果、转折，再拿补好的故事去判；从没被要求只读大字、按出现顺序连读、逐对看相邻两块；“像清单、通读不顺不算理由”压住了这类报告）。
改法（两位共同部分）：做法最前面加“原样顺读”；中等尺度加“屏内跳”；不跳问题必须引相邻两块原文；不要求连接词、不许替原文定因果。
其余和第四版相同。
5b（11-10 晚 B 轮两位顾问复核后）：“为什么接在后面”改成“认得出承接线索吗”（两位共同）；单块不像人话扩到搭配、语序、省略；含跨屏相邻；不推测写稿动机；第 1、5 条不重复计分。结果文件 openA5b_*；5a 版的结果是 openA5_*。结果 r3/s24/openA5_{作品}_{评委}_{TAG}_{轮次}.json
python r3/openabs5.py TAG [轮次]；python r3/openabs5.py sum TAG 轮次...
"""
import sys, importlib.util
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blend, prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, view_text
sys.stdout.reconfigure(encoding='utf-8')
_sp = importlib.util.spec_from_file_location('oa4', str(Path(__file__).resolve().parent/'openabs4.py')); oa4 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(oa4)

STEP0 = """【做法】
0. 每一屏先做“大字原样顺读”，再做别的。把这一屏的“话”按观众实际看到的顺序排好（按出现秒数；没写秒数的在最前；同时出现的按列出顺序），暂时不看“感受”和旁注，只读这些大块，原文照读，不改写、不在心里补字。
   - 逐对看相邻两块（含上一屏最后一块和这一屏第一块）：普通观众第一次连着读，认得出两块之间的承接线索吗？承接可以是同一处境的延续、时间推进、转折、因果、并列补充、由前一个念头引出的联想或心理变化，不要求后一块是前一块的结果，也不要求有连接词。
   - 两块各自读得懂，但要观众自己补出原文没交代、又影响理解的前提、因果、指代、时间或场景转换、心理转折，才明白两块为什么这样接，就是“跳”，要报。不能只因为两块讲的是同一个人、同一段关系，就认为接得上；心理上自然的转向、情感留白、并列本身不算跳。
   - 只凭这两块大字本身判断，不能借小字、旁注或你自己补的情节替大字接上；判为接得上时，要指得出原文里支撑这层关系的字。你在概括里用到的“因为”“但”“于是”，回头看原文是否真的写出了这层关系。
   - 再单独看每一块大字：像不像一个人平常讲经历、说感受时会说出口的话。不像的样子不只是心理状态的标签和摘要，也包括搭配、语序或省略不自然，读者得在脑子里补成分、重排语序、翻成正常说法才顺。不要求完整句，不要求第一人称。
   - 这一步查的是读起来的连续和自然，和全曲人物的事往不往前走是两回事；故事清楚抵消不了大字的跳。
"""
SEV = "- 中等：只看大块拼不出这一屏的主要意思；"
SEV_NEW = "- 中等：相邻两块大字各自读得懂，但第一次连着读要观众自己补出原文没交代、又影响理解的关系才接得上（整屏大意概括得出来也不能降为轻微）；单块大字意思猜得出，但说法不像人说出口的话（心理状态的标签或摘要，或搭配、语序、省略不自然，要在脑子里翻成正常说法）；只看大块拼不出这一屏的主要意思；"
RULE = "4. 情感留白、要稍微体会一下的细腻表达，不算理解成本。"
RULE_NEW = RULE + "\n5.“跳”的问题必须引相邻两块大字的原文，写清两块之间缺了什么、观众会在哪里卡住；只指出缺了承接，不替原文规定该是因果还是并列，不推测写稿的人为什么这样写。同一处毛病只报一次：大块拼不出主要意思或人物的变化，算第 1 条；意思拼得出、但相邻两块接得不自然或单块不像人话，算第 5 条。"
OPENA5 = oa4.OPENA3.replace('【做法】\n', STEP0, 1).replace(SEV, SEV_NEW, 1).replace(RULE, RULE_NEW, 1)
assert OPENA5.count('原样顺读') >= 1 and SEV_NEW in OPENA5 and RULE_NEW in OPENA5
import os
V = os.environ.get('OA5V', 'b')   # b = 5b；c = 5c（11-10 晚：5a 四遍都没对第 6 屏大字报任何问题，做法第 0 步没在输出里留痕，评委可以跳过；5c 要求每屏交出逐对顺读结果）
if V == 'c':
    OLD_OUT = '{"screens":[{"sec":"S01","new":"新知道了什么，或“无新东西，重复了第几屏的什么”","issues"'
    NEW_OUT = '{"screens":[{"sec":"S01","read":[{"pair":"前一块原文 → 后一块原文（第一块写上一屏最后一块 → 这一屏第一块）","link":"认得出的承接线索：指出原文里哪几个字撑起这层关系；接不上就写缺了什么、观众在哪里卡住","ok":true}],"speech":[{"quote":"不像人说出口的那一块原文","why":"哪里不像"}],"new":"新知道了什么，或“无新东西，重复了第几屏的什么”","issues"'
    assert OLD_OUT in OPENA5; OPENA5 = OPENA5.replace(OLD_OUT, NEW_OUT, 1)
    OPENA5 = OPENA5.replace('所有屏都要有。', '所有屏都要有；每屏的 read 要把相邻两块逐对写全，ok 为 false 的、speech 里列出的，都要同时写进 issues（按尺度定轻重）。', 1)
PFX = 'openA5' + V
prompt_lint.lint(OPENA5, 'openabs5' + V)


def one(a):
    w, j, m, tag, run = a; p = S/f'{PFX}_{w}_{j}_{tag}_{run}.json'
    if p.exists(): return rd(p)
    msg = OPENA5.replace('{STD}', blend.DAGSTD).replace('{SCREEN}', view_text(w, tag)).replace('{CENTER}', rd(R2/f'{w}_src.json')['center'])
    for k in range(3):
        ans = call(f'pub24OA5{V}_{w}_{j}_{tag}_{run}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-openabs5')
        try: r = parse(ans); assert 'screens' in r; wr(p, r); return r
        except Exception as ex: print('不合格', w, j, tag, run, repr(ex)[:120], flush=True)


def summary(tag, runs):
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                p = S/f'{PFX}_{w}_{j}_{tag}_{run}.json'
                if not p.exists(): row.append('缺'); continue
                iss = oa4.issues(rd(p)); c = Counter(x.get('severity') for x in iss)
                std = Counter(str(x.get('std')) for x in iss if x.get('severity') in ('严重', '中等'))
                row.append(f"严重 {c['严重']}、中等 {c['中等']}、轻微 {c['轻微']}（中等以上按标准 {dict(sorted(std.items()))}）")
            print(f'绝对验收5{V} {tag} {w} {j}： ' + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'sum': summary(sys.argv[2], sys.argv[3:] or ['run1']); sys.exit()
    tag = sys.argv[1]; run = sys.argv[2] if len(sys.argv) > 2 else 'run1'
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j, m, tag, run) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
    summary(tag, [run])
