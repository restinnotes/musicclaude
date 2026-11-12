"""11-11 深夜 I12：L34g563（GPT-5.6，只改写稿：全曲语义去重）判“接近”，交回提出者一次。
python r3/handback_g563.py → r3/s24/prompt_L34g563b.txt
"""
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, rd, call, parse, G56
sys.stdout.reconfigure(encoding='utf-8')

ASK = """你是顾问。你上一轮出的屏幕稿写法（L34 方案三：只改写稿，全曲语义去重，附在最后）已经两首同跑、测完。它是这一批六套里唯一有正面证据的，判“接近”，现在交回给你改一次（只这一次）。

【正面证据（不许丢）】
- 开放评审（三位、两首）：当前主线 K28b 六份里五份把“原地打转”排第一；你这套只有两份排第一，船歌 GPT-6 一份打转已不在前三。
- 盲比对固定锚点 K11g：幻想两位评委都稳定选你这套（主线 K28b 做不到），人话 human 0:2 赢；船歌两位随座位（平）。
- 大字的人话问题和主线持平（船歌 4 对 5，幻想 1 对 1）。

【没过的两处】
1. 绝对验收中等问题 34（主线 K28b 26），多出来的几乎全在第 5 条人话，而且全在小字：小字人话问题船歌 8（主线 4）、幻想 7（主线 3）。原因：主线写法规定“小块原样保留，只有两种情况才动”，并有字数和出现时间的规则（这一屏大块合起来不超过停留秒数乘 3、每块最多 40 字最多两个逗号、at 第一块 0 之后每块间隔 3–5 秒、accent/emotion/from 怎么填）；你的写法没有保留这些，小字被重写，评委逐条报出生造、书面、一块塞几层的问题（例子见下）。
2. 盲比船歌“核心看得出”core 两位都输 K11g（4:0）。去重时可能把船歌核心那件事最关键的那几句也当重复删了；第一次出现的地方要保留得足够完整，让只看大字的人看得出核心。

【这次只改什么】
- 保留你的全曲命题账本和去重规则（这是打转降下来的原因）。
- 把主线写法里关于小块、旁注、字数、出现时间、accent/emotion/from 的规则原样放回（见下面“主线写法”），小块原样保留。
- 对“核心”：账本里属于核心那件事的命题，第一次出现时用线的原话完整放进大字，不为去重删它的关键分句。
- 不许退步：打转的排名、幻想的盲比、大字的人话。

只输出 JSON：{"analysis":"你怎么改、为什么","prompt":"改后的完整写稿提示词"}。占位符必须原样保留：{BUDGET} {DAGSTD} {FINAL} {BEADS} {BASE}，输出格式不能变。提示词里不放具体作品的内容或例子。回答时请不要进行联网搜索。

【小字人话问题（绝对验收原话，节选）】
{ISSUES}

【船歌盲比 core 输的理由（节选）】
{CORE}

【你的写法（L34 方案三，原文）】
{MINE}

【主线写法（K28b，原文）】
{MAIN}
"""


def issues():
    out = []
    for op in ('op60', 'op61'):
        sc = rd(S/f'screen_{op}_g68L34g563.json')
        small = [i['text'] for s in sc['sections'] for r in s['rows'] if r['kind'] != 'line' for i in r.get('items', [])]
        for j in ('g6', 'g56'):
            for s in rd(S/f'openA5b_{op}_{j}_g68L34g563_run1.json')['screens']:
                for i in s['issues']:
                    q = i['quote'].replace('【', '').replace('】', '')
                    if i['std'] == '5' and i['severity'] != '轻微' and any(q[:6] in t for t in small):
                        out.append(f"- {op} {s['sec']}「{i['quote']}」：{i['why']}")
    return '\n'.join(out)


def core():
    out = []
    for f in sorted(S.glob('vs5_op60_*_v5bg68L34g563_*.json')):
        d = rd(f); seat = f.stem[-1]; anchor = seat   # _X 文件里 X 是锚点 K11g，_Y 文件里 Y 是锚点
        mine = 'Y' if seat == 'X' else 'X'
        out.append(f"- （这份里 {anchor} 是锚点 K11g，{mine} 是你这套）core 判给 {d['nets'].get('core')}；理由：{d.get('why', '')}")
    return '\n'.join(out) or '（无原文，按分项结果）'


if __name__ == '__main__':
    msg = (ASK.replace('{ISSUES}', issues()).replace('{CORE}', core())
           .replace('{MINE}', (S/'prompt_L34g563.txt').read_text(encoding='utf-8')).replace('{MAIN}', (S/'prompt_K28b.txt').read_text(encoding='utf-8')))
    print('材料', len(msg), '字', flush=True)
    for k in range(3):
        try:
            r = parse(call('hb_L34g563' + ('' if not k else f'_r{k}'), msg, G56, 'gpt3s', 'dag-advisor')); assert r.get('prompt'); break
        except Exception as ex: print('不合格', repr(ex)[:150], flush=True); r = None
    if not r: sys.exit(1)
    p = r['prompt']
    print('分析：', r.get('analysis'))
    print('缺占位符：', [x for x in ('{BUDGET}', '{DAGSTD}', '{FINAL}', '{BEADS}', '{BASE}') if x not in p] or '无')
    print('泛化检查：', prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', p)) or '过')
    (S/'prompt_L34g563b.txt').write_text(p, encoding='utf-8')
