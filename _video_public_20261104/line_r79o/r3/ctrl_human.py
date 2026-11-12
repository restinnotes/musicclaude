"""11-12 人话诊断（I02a 先验证原因）：开放评审一直报大字“像心理分析报告”（给情绪贴标签、解释每个感受、“这份亲近”“眼下的好”这类抽象名词），盲比人话船歌输 K11g。
假设：腔调来自线的原话（大字只切不改，线怎么说屏上就怎么说）。验证：让 Argon（改语言的写手）把 r2e 的线一条对一条只改说法、不改意思，变成人平常讲经历的话；
同一份 K28b 写稿，看开放评审还报不报分析腔、盲比人话能不能不输 K11g。成立 → 人话在写线（DAG）那一层修；不成立 → 问题在写稿或珠子。
python r3/ctrl_human.py → r2CTRLh/{作品}_src.json
"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import R2, rd, parse, WORKS
sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); import evo
sys.stdout.reconfigure(encoding='utf-8')
OUT = R2.parent/'r2CTRLh'; OUT.mkdir(exist_ok=True)

ASK = """下面是一条“线”：一个人在一首钢琴曲里经历的一件心事，按音乐分段，每段几条，每条一句。普通读者读了说：它像心理分析报告，不像一个人在讲自己的事——每种情绪都要点名、解释原因、再确认一遍；爱用抽象的说法（“这份亲近”“眼下的好”“原有的自在”“往回藏”这类），读的人得自己翻译成平常话。

请一条对一条改说法，让它像一个人平常跟朋友讲自己经历时会说的话：
- 只改说法，不改意思：每条讲的事、心里的变化、前后顺序、因为所以都不变；不加新的事、动作、对白、物件、前史；不删掉任何一层意思。
- 少用抽象名词当主语或宾语（“这份……”“那种……感”“眼下的……”），换成具体在做什么、想什么、怕什么。
- 不替情绪下定义、不总结道理；能直接说出来的感受就直接说，不绕。
- 少用否定句（“不是……而是……”“没有……”）和“越……越……”；句式不要一个模子。
- 每条一句，长度和原句差不多，不超过原句的 1.2 倍。
- 条目数、编号必须和原线完全一样。

只输出 JSON：{"segments":[{"sec":"S01","items":[{"id":"S01-1","text":"…"}]}]}

原线：
{LINE}
"""


def one(w):
    src = rd(R2/f'{w}_src.json')
    line = '\n'.join(f"### {s['sec']}\n" + '\n'.join(f"- {l['id']}：{l['text']}" for l in s['lines']) for s in src['sections'])
    got = None
    for k in range(3):
        try:
            r = parse(evo.call_argon_direct(f'ctrlhuman_{w}' + ('' if not k else f'_r{k}'), ASK.replace('{LINE}', line), meta={'stage': 'ctrl-human'}) or '')
            got = {it['id']: it['text'] for s in r['segments'] for it in s['items']}
            assert all(l['id'] in got for s in src['sections'] for l in s['lines']); break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); got = None
    if not got: return
    new = copy.deepcopy(src)
    for s in new['sections']:
        for l in s['lines']: l['text'] = got[l['id']].strip()
    (OUT/f'{w}_src.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')
    for s, s0 in zip(new['sections'], src['sections']):
        for l, l0 in zip(s['lines'], s0['lines']): print(w, l['id'], '｜原：', l0['text'], '｜改：', l['text'], flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))
