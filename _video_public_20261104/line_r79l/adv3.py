"""第三轮顾问：拿 w4 的体检结果，问压缩怎样才不伤解释力、珠子怎样拆才读得懂。
python adv3.py ROUND MAIN
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import advise, pub2, pub3
from pub2 import G6, G56, OUT, ROOT, WORKS, call, rd

R3 = pub3.OUT
TRIED = advise.TRIED+"""
- 把一句完整的珠子压短、整屏文字一起显示（d2）：字数只剩三成，但用户觉得珠子和线分不开，读者接不起来。
- 一句一句轮流放大（用户否定：“这个东西就是很时序 就显得很没有必要”）。
- 把珠子拆成散开的词，线写成“我”说的一句短话（w4）：用户说方向可以试，但“压的完全没法读了肯定不行”“解释力 你在压扁的时候可能也会变弱”。体检结果见下。
- 一步写到底时（w2）：词还是长短语，线反而变长，平均 44 字。先压线再单独拆词才压得下来。
- 把词概括成书面词（w3）：“张扬”“不舍”，用户和我都认为失去了感觉。"""
ASK = """【这一轮只想解决的问题】
1. 线怎么压才不伤解释力？现在的结果是字少了，但读者不知道这个人为什么会这样，前后接不上。怎样才算压对了？什么该留、什么可以删？
2. 珠子怎么压才读得懂、又和线对得上？“拆成词”是用户提的一个想法，但不一定是最好的做法，你可以提别的压缩方式。

"""
FMT = """只输出 JSON。每段若干组，每组有线和压缩后的珠子文字；rank 只有一个“主”，其余“次”；emotion 只能是：炽热、欢喜、亲密、安心、孤单、不安、悬着；from 填原文 id；同一颗珠子拆出的几个部分 from 相同。
{"phases":[{"label":"…","emotion":"…","sections":["S01","S02"]}],"sections":[{"sec":"S01","groups":[{"rank":"主","kind":"","emotion":"…","lines":[{"text":"…","keys":[],"from":["S01-1"]}],"beads":[{"text":"…","keys":[],"emotion":"…","from":["S01-B1-p1"]}]}]}]}"""
ADV = [('g6a', G6, 3), ('g6b', G6, 2), ('g56', G56, 2)]


def results(tag):
    rows = []
    d = rd(R3/f'eval_{tag}.json')
    for k, v in d['cov'].items(): rows.append(f"覆盖 {k}：说清 {v['new'].get('说清', 0)}/{v['n']}（定稿 {v['r78a'].get('说清', 0)}），偏弱 {v['new'].get('偏弱', 0)}，没有 {v['new'].get('没有', 0)}")
    t = rd(OUT/f'thread_{tag}.json'); rows.append(f"短版的线和定稿的线盲比（段净胜）：{t['nets']}。alone 是单独读，lean 是不啰嗦，plain 是人话，cover 是接得住珠子。")
    rows += [f"评委 {r['w']} {r['j']}：{r['why'][:400]}" for r in t['rows']]
    for k, v in d['read'].items(): rows.append(f"只看屏幕的观众 {k}：{v['words']} 个词，读不懂 {len(v['unclear'])}，太长 {len(v['too_long'])}，词和话 {v['joint']}，前后接得上 {v['chain']}。{v['overall']}")
    for w in WORKS:
        k = rd(OUT/f'keep_{w}_{tag}.json'); rows.append(f"不能掉 {w}：{k['summary']}")
    return '\n'.join(rows)


def run(rnd, main):
    W0, W1 = WORKS
    msg0 = advise.P.replace('{STD}', pub2.std()).replace('{USER}', (ROOT/'用户判定.md').read_text(encoding='utf-8')).replace('{TRIED}', TRIED).replace('{FORMAT}', FMT)
    msg0 = msg0.replace('{MAIN}', pub2.screen(W0, main)+'\n\n'+pub2.screen(W1, main)).replace('{ISSUES}', results(main)).replace('{LAST}', '（见上）')
    msg0 = msg0.replace('{W0}', pub2.NAME[W0]).replace('{W1}', pub2.NAME[W1]).replace('{SRC0}', pub2.source_matched(W0)).replace('{SRC1}', pub2.source_matched(W1))
    msg0 = msg0.replace('【请你回答】', ASK+'【请你回答】').replace('1. 诊断：现在的文字为什么像截断、为什么音乐描述多、为什么反而妨碍理解？问题出在哪里？', '1. 诊断：现在这版的解释力丢在哪里，词为什么读不懂？问题出在哪里？')

    def one(a):
        j, m, n = a; msg = msg0.replace('{N}', str(n)).replace('{{SOURCE}}', '{SOURCE}').replace('{{PREV}}', '{PREV}')
        ans = call(f'pub3_adv_{rnd}_{j}', msg, m, 'gpt3s', 'public3-advise')
        (OUT/f'adv_{rnd}_{j}.md').write_text(ans or '', encoding='utf-8')
        return j, len(ans or '')
    print(len(msg0), flush=True)
    with ThreadPoolExecutor(3) as ex: print(list(ex.map(one, ADV)), flush=True)
    advise.ADV = ADV
    print(advise.collect(rnd), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); run(sys.argv[1], sys.argv[2])
