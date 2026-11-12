"""把评审结果交回去局部修：线补回解释力，词换掉读不懂的。全走 gpt3。
python pub8.py 来源TAG 新TAG
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, source_matched, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲“边听边看”视频的短版文字，以及它的评审结果。屏幕上每段有几组，每组是一句或几句线（一个人经历的事）和一把散开的词（听的人当下的感受，同一条 from 的词显示在一起）。

评审发现两个问题：
一、线压过头了。和定稿的线比，单独读和接住珠子都明显倒退：有解释力的事实被压成了情绪结论，前后的因果断了，读者不知道这个人为什么会这样。
二、很多词读不懂或太长。常见原因：抽象评语、文学隐喻、音乐术语、离开原句就不懂的半截话。

请局部修，不要整篇重写。

【线】
目标：没读过原文的人，只读线也能明白这个人此刻为什么这样，和上一句怎么接起来。
逐句对照定稿的线，把丢掉的“为什么”和前后的关系补回来，用尽量少的字。可以比现在长，但不要变回定稿的长度，也不要把几件事塞进一句：一件事说不下就拆成两句。
已经够好的句子不动。讲这件事的人写“我”，称呼不变。不加原文没有的事，不把珠子里的比喻写成真的发生的事。

【词】
评委读不懂或嫌长的词，换成能直接感到的说法（身体的感觉、一个具体的画面、一声问），换不了就删。评委说好的留着。没有词的组要补上。
每把词要是这组线的感受面：词和线放在一起，观众能明白为什么这个人会有这些感受。
词或很短的词组，不是半句，没有逗号，除问号外不带标点。同一颗珠子的词 from 保持相同，这样它们才会显示在一起。

分组、rank、emotion、阶段不要动。只输出 JSON，结构和输入完全一样，keys 留空数组。

【现在的短版】
{CUR}

【覆盖评委：这些珠子在线里找不到足够的原因（偏弱 / 没有 / 相反）】
{COV}

【不能掉清单里只留下一部分的】
{KEEP}

【和定稿的线盲比时评委的话】
{VOTES}

【只看屏幕的观众：读不懂、太长的词，以及总体意见】
{READ}

【定稿的线和珠子】
{SRC}
"""


def evidence(w, tag):
    cov = []
    for j in ('g6', 'g56'):
        for x in rd(R3/f'cov_{w}_{j}_{tag}.json')['beads']:
            if x.get('status') != '说清': cov.append(f"{x.get('sec')} {x.get('bead')} {x.get('status')}（{j}）：{x.get('why', '')[:90]}")
    keep = [f"{x['id']}：{x['note'][:100]}" for x in rd(R2/f'keep_{w}_{tag}.json')['items'] if x['verdict'] != '保留']
    votes = [r['why'][:500] for r in rd(R2/f'thread_{tag}.json')['rows'] if r['w'] == w]
    read = []
    for j in ('g6', 'g56'):
        d = rd(R3/f'read_{w}_{j}_{tag}.json'); read.append('总体：'+d.get('overall', ''))
        read += [f"{s['sec']} 读不懂：{'、'.join(s.get('unclear', []))}；太长：{'、'.join(s.get('too_long', []))}；词和话：{s.get('joint')}" for s in d['sections']]
    return map('\n'.join, (cov, keep, votes, read))


def one(a):
    w, src, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d0 = rd(R3/f'script_{w}_{src}.json'); cov, keep, votes, read = evidence(w, src)
    msg = P.replace('{CUR}', json.dumps(d0, ensure_ascii=False)).replace('{COV}', cov).replace('{KEEP}', keep).replace('{VOTES}', votes).replace('{READ}', read).replace('{SRC}', source_matched(w))
    for k in range(3):
        ans = call(f'pub8_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public8-repair')
        try:
            d = pub2.tidy_keys(parse(ans)); errs = pub3.check(w, d)
        except Exception as e:
            print(w, '解析失败', repr(e)[:200], flush=True); continue
        print(w, tag, '问题', len(errs), errs[:4], flush=True)
        wr(p.with_suffix('.try.json'), d)
        if not errs: wr(p, d); return True
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
    pub3.marks(tag)
