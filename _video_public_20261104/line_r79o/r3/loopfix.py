"""11-12 晚 打转的局部修改（两位顾问 I02 一致的第一步：只改评审点名的重复句，其他不动；diag_loop_noev_*.json）。
用户定死“不加事件”。GPT-6 按评审原话 + 顾问点名的位置改线（r2e → r2LF1）：每组重复只在一处完整表达，其余处改成它带来的后果或当下具体体验，或删掉重复的半句；
不加事、不留空段、不改未点名的条。GPT-5.6 独立检查（加没加事、意思变没变、重复去掉没有）。提示词是通用的，作品内容只出现在材料里。
python r3/loopfix.py → r2LF1/{作品}_src.json；r3/s24/loopfix_check_{作品}.json"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
OUT = R2.parent/'r2LF1'; OUT.mkdir(exist_ok=True)
NAME = {'op60': '船歌', 'op61': '幻想波兰舞曲'}

FIX = """下面是一条“线”：一个人在一首钢琴曲里经历的一件心事，按音乐分段，每段几条，每条一句。屏幕上的大字就是线的原话。
读者普遍说它“原地打转”：同一个认识、决定、担心隔几段又被当成新的说一遍。下面附了审读的原话和两位顾问指出的具体位置。

请只改被点名的那几条，其余所有条目一字不改：
- 每一组重复，只在一处完整说出来（顾问建议了放在哪里就放在哪里）；其余几处不再重新宣布、重新发现、重新追问，改成这件事在这时带来的后果、他实际怎么做，或者此刻的具体感受；实在没有别的可写，就只留下这一条里不重复的那半句。
- 分清楚：实际发生的（对方实际怎样）、他的猜测、他的希望、一时涌上来的冲动、已经定下的决定、一直在的担心。不要把猜测写成事实，不要把一时的冲动写成定下的决定。
- 绝对不加任何事件、前史、对白、物件、新人物，不改变原来的意思和人物关系；每段的条数不变，不留空条。
- 改过的句子像一个人平常讲自己的经历，不要心理分析腔、不要总结道理；长度和原句差不多。

只输出 JSON：{"changed":[{"id":"S07-1","old":"原句","new":"新句","why":"改了什么"}]}（只列改过的条）

【审读原话】
{LOOPS}

【顾问指出的位置】
{SPOTS}

【线】
{LINE}
"""

CHECK = """下面是一条“线”改动前后的对照（只列改过的条），以及改后的整条线。请独立检查，只输出 JSON：
{"added_events":["改后新加了原来没有的事件、动作、对白、物件、人物的条目编号和原因"],"meaning_changed":["意思或人物关系被改变的条目编号和原因"],"repeats_left":["改后整条线里，同一个认识、决定、担心仍然在两处以上被重新宣布的，写出位置"],"verdict":"通过|不通过"}
没有就给空数组。“通过”= 没有新加事件、没有改变意思。

【改动】
{DIFF}

【改后的整条线】
{LINE}
"""


def line_text(src):
    return '\n'.join(f"### {s['sec']}\n" + '\n'.join(f"- {l['id']}：{l['text']}" for l in s['lines']) for s in src['sections'])


def loops(w):
    out = []
    for j in ('g6', 'g56', 'argon'):
        p = S/f'openF3_{w}_{j}_g68CTRLsk2F.json'
        if p.exists():
            for x in rd(p)['issues']:
                if any(k in x['problem'] for k in ('打转', '重复', '循环', '反复', '失忆', '又一次', '再次')): out.append(f"- {x.get('sec','')}：{x['problem'][:500]}")
    return '\n'.join(out)


def spots(w):
    out = []
    g6 = rd(S/'diag_loop_noev_g6.json').get('q5_first_minimal_change', {}).get('targeted_edits', {}).get(NAME[w], [])
    g56 = rd(S/'diag_loop_noev_g56.json').get('first_minimal_change', {}).get('target_spots', {}).get(NAME[w], '')
    out += [f'- 顾问一：{x}' for x in g6]; out.append(f'- 顾问二：{g56}')
    return '\n'.join(out)


def one(w):
    src = rd(R2/f'{w}_src.json'); ids = {l['id'] for s in src['sections'] for l in s['lines']}
    msg = FIX.replace('{LOOPS}', loops(w)).replace('{SPOTS}', spots(w)).replace('{LINE}', line_text(src))
    r = None
    for k in range(3):
        try: r = parse(call(f'loopfix1_{w}' + ('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'loopfix')); assert all(c['id'] in ids for c in r['changed']); break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); r = None
    if not r: return
    new = copy.deepcopy(src); ch = {c['id']: c['new'].strip() for c in r['changed']}
    for s in new['sections']:
        for l in s['lines']:
            if l['id'] in ch: l['text'] = ch[l['id']]
    (OUT/f'{w}_src.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')
    print(w, '改了', len(ch), '条', flush=True)
    for c in r['changed']: print(f"  {c['id']}｜原：{c['old']}｜新：{c['new']}｜{c.get('why','')}", flush=True)
    diff = '\n'.join(f"- {c['id']}｜原：{c['old']}｜新：{c['new']}" for c in r['changed'])
    ck = parse(call(f'loopfix1chk_{w}', CHECK.replace('{DIFF}', diff).replace('{LINE}', line_text(new)), G56, 'gpt3s', 'loopfix-check'))
    (S/f'loopfix_check_{w}.json').write_text(json.dumps(ck, ensure_ascii=False, indent=1), encoding='utf-8')
    print(w, '检查：', json.dumps(ck, ensure_ascii=False)[:800], flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))
