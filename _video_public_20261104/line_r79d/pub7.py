"""给音乐按情绪上色：模型看可视化编码、每段的词和音符数据，决定哪些声音是什么情绪。全走 gpt3。
python pub7.py TAG      结果写到 r3/colors_{w}_{TAG}.json
"""
import json, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, source_matched, wr
from pub3 import EMOTIONS, EMO_DESC, ENCODING, OUT, bar_table

P = """下面是一首器乐曲视频每段屏幕上的文字、依据的原文，以及音符数据。

"""+ENCODING+"""

现在音乐动画大多只有一种暗色，看不出情绪。请给每段的音乐上色：颜色就是情绪，观众看到音乐图上的不同颜色，就知道这段有几种不同的感受，分别落在哪些声音上。

- 依据这段屏幕上实际有的情绪和原文。一段里有几种情绪，就尽量让人看到几种颜色；真的只有一种就一种，不要为了好看加颜色。
- 怎么分由你看数据决定：可以按音高层（比如上面的声音是一种感受、下面的声音是另一种），可以按小节（这几小节转成另一种情绪），也可以两者都用。要说得通，能指出依据。
- 大部分音都要落进某个颜色，不必每个音都有。同一段的范围之间不要大面积重叠。
- 下面列出的已标音符会盖在你的颜色上。不用重复它们，但不要和它们矛盾。

情绪只能从下面选：
"""+EMO_DESC+"""

只输出 JSON：{"colors":[{"sec":"S01","bars":[1,3],"pitch":[70,102],"emotion":"…","why":"一句话"}]}
bars 是起止小节，pitch 是音高范围（越大越高），不限音高写 null。

【每段屏幕上的文字】
{CUR}

【已标音符】
{MARKS}

【音符数据：每小节】
{BARS}

【原文】
{SRC}
"""


def one(a):
    w, tag = a; p = OUT/f'colors_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(OUT/f'script_{w}_{tag}.json'); m = rd(OUT/f'marks_{w}_{tag}.json')['marks']
    cur = [{'sec': s['sec'], 'groups': [{'emotion': g['emotion'], 'words': [b['text']+(f"（{b['emotion']}）" if b.get('emotion') else '') for b in g.get('beads', [])], 'lines': [l['text'] for l in g.get('lines', [])]} for g in s['groups']]} for s in d['sections']]
    marks = [{'sec': x['sec'], 'text': x['text'], 'bars': x.get('bars'), 'pitch': x.get('pitch')} for x in m if x.get('render') is True]
    msg = P.replace('{CUR}', json.dumps(cur, ensure_ascii=False)).replace('{MARKS}', json.dumps(marks, ensure_ascii=False)).replace('{BARS}', bar_table(w)).replace('{SRC}', source_matched(w))
    for k in range(3):
        ans = call(f'pub7_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public7-colors')
        try:
            r = parse(ans); bad = [x for x in r['colors'] if x.get('emotion') not in EMOTIONS]; assert r['colors'] and not bad, bad[:3]
            wr(p, r); print(w, '上色', len(r['colors']), dict(Counter(x['emotion'] for x in r['colors'])), flush=True); return True
        except Exception as e: print(w, '不合格', repr(e)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1]) for w in WORKS])), flush=True)
