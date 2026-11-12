"""11-11 深夜 I11 校准开放评审（正面对照）：30 来个版本里“原地打转”都排前三，要先确认评审能分清“真不打转”。
让 GPT-6 把 r2e 的线改成一条明显一步步往前、不回头的线（为校准，允许加小的外部事件——这是对照，不是候选），条目数、编号、对应珠子不变。
python r3/ctrl_fwd.py → r2CTRLf/{作品}_src.json；之后 pipe_K27one 写稿 + 快筛，只看开放评审的打转是否消失。
"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import R2, rd, call, parse, G6, WORKS
sys.stdout.reconfigure(encoding='utf-8')
MODE = 'x' if os.environ.get('CTRL_X') else 'n' if os.environ.get('CTRL_N') else 'e' if os.environ.get('CTRL_E') else 'f'
OUT = R2.parent/f'r2CTRL{MODE}'; OUT.mkdir(exist_ok=True)

ASK = """这是一个给评委做校准用的对照，不是正式稿。

下面是一条“线”：一个人在一首钢琴曲里经历的一件事，按音乐分段，每段几条。读者普遍反映它“原地打转”：同一个领悟、同一个决定、同一个担心隔几段又被当成新的说一遍，人物在几种状态之间来回。

请把它改写成一条**明显一步步往前走、绝不回头**的线：
- 每一条都必须带来前面没有的新东西：新的事、新的行动、新的后果、新的认识。已经成立的认识和决定，后面只能写它带来的结果，不能再宣布、再怀疑、再确认。
{EVENTS}
- 人物、核心处境（Center）不变；整体情感方向尽量贴着原线每段的情绪（原线每段的情绪是跟着音乐的）。
- 语言像一个人平常讲自己的经历，不要心理分析腔。
- 条目数、每条的编号必须和原线完全一样（一条对一条改写），每条一句、不超过 45 字。

只输出 JSON：{"segments":[{"sec":"S01","items":[{"id":"S01-1","text":"…"}]}]}

Center：{CENTER}

原线：
{LINE}
"""


EV_F = '- 为了让它确实往前走，允许加入小的外部事件（对方说了一句什么、做了一个动作、两人去了哪里、收到一个消息等），一段最多一件。'
EV_E = '''- 为了让它确实往前走，允许全曲加入 3–5 件真实发生的事，只放在音乐情绪真正转折的段落（看原线情绪在哪里明显转向）。事的分量要和那一段音乐相称：是会改变两人关系或人物处境的事，不是买早饭、记日历、做家务、上课这类流水账日常；从核心处境自然推出来，不加新的重要人物；前后因果交代清楚，不要太顺。
- 其余段落不加事件：写这几件事发生之后人物的处境和体验怎样变化（身体、注意力、和对方相处的样子），每段都比上一段往前一点，不再回头重新挣扎同一个问题。'''
EV_N = '''- 不加任何外部事件、新动作、新对白、新物件、前史：只用原线里已经有的东西。往前走只能靠心里真正的新一步——第一次明白的事、第一次做的决定、前面的决定在之后带来的结果、对同一件事第一次有了不同的理解。原线里同一个心思隔几段又出现的，改成写它在这时带来的变化或结果，或者只写当下的体验质地（身体、注意力），不再重新宣布、重新怀疑、重新确认。'''
EV = {'n': EV_N, 'e': EV_E, 'f': EV_F, 'x': ''}[MODE]
ASK_X = '''这是一个给评委做校准用的对照，不是正式稿。

下面是一条“线”：一个人在一首钢琴曲里经历的一件心事，按音乐分段，每段几条。

请只做一件事：挑全曲 3–5 个音乐情绪明显转折的段落，在每个这样的段落里，把其中一条换成一件真实发生的事（分量和那段音乐相称，会改变两人关系或人物处境，从核心处境自然推出来，不加新的重要人物）。
其余所有条目一字不改，原样照抄——包括那些重复前面心思的句子，也不要删、不要改、不要让它们“往前走”。
条目数、每条的编号必须和原线完全一样，每条一句、不超过 45 字。

只输出 JSON：{"segments":[{"sec":"S01","items":[{"id":"S01-1","text":"…"}]}]}

Center：{CENTER}

原线：
{LINE}
'''
if MODE == 'x': ASK = ASK_X
if MODE == 'n': ASK = ASK.replace('新的事、新的行动、新的后果、新的认识', '新的认识、新的决定、前面的事带来的新结果')


def one(w):
    src = rd(R2/f'{w}_src.json')
    line = '\n'.join(f"### {s['sec']}\n" + '\n'.join(f"- {l['id']}：{l['text']}" for l in s['lines']) for s in src['sections'])
    r = None
    for k in range(3):
        try:
            r = parse(call(({'n': 'ctrlnoev_', 'e': 'ctrlev_', 'f': 'ctrlfwd_', 'x': 'ctrlxev_'}[MODE] + w) + ('' if not k else f'_r{k}'), ASK.replace('{EVENTS}', EV).replace('{CENTER}', src['center']).replace('{LINE}', line), G6, 'gpt3s', 'ctrl'))
            got = {it['id']: it['text'] for s in r['segments'] for it in s['items']}
            assert all(l['id'] in got for s in src['sections'] for l in s['lines']); break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); r = None
    if not r: return
    new = copy.deepcopy(src)
    for s in new['sections']:
        for l in s['lines']: l['text'] = got[l['id']].strip()
    (OUT/f'{w}_src.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')
    for s in new['sections']: print(w, s['sec'], ' / '.join(l['text'] for l in s['lines']), flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))
