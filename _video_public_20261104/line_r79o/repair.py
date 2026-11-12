"""11-08 DAG2 成品修补层（迭代准则“成品修补回路”第 1 条：只在当前主线上局部改）：按开放评审挑出的问题，逐处改屏幕稿，其余一字不动。
做法照 DAG 的经验：局部修订赢、整篇重写输；只改不删具体内容、改后不变长；守护清单里的内容不许删。
python repair.py SRC NEW [GUARD_TAG...]     读 r3/s24/open_{w}_{j}_{SRC}.json；GUARD_TAG 指定从哪些盲比里收集“删了算退步”的守护内容（可省）
"""
import copy, json, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, R2, rd, wr, call, parse, G6, WORKS, JUDGES, to_script
import pub16

REP = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿：普通观众边听边扫，每段屏幕只停留写明的秒数。“话”是大字的一句，【】里是放大加亮的关键词；“感受”是小字短语，用 / 隔开，[ ] 里是这一行的编号。
评审读了这份屏幕稿，挑出了下面这些问题。请只在出问题的地方局部改，其余一字不动。

【大众版标准（评审依据）】
{STD}

怎么改：
1. 先判断每条问题是否成立：评审有时会误判（比如把定稿本来就有的疑问、拿不准的语气当成毛病，或建议加定稿没有的事）。不成立的不改，在 skip 里写一句原因。
2. 成立的，只改那一行；能改几个字就不改整句。修人话、修啰嗦时只换说法、去重复，不删具体的画面、身体感觉、比喻、心里话和因果；同一行改后不比原来长，也不要短很多（只删真正重复的字）。
3. 不改意思：疑问仍是疑问，猜测、拿不准的语气不写成确定，担心不写成已经发生，具体说法不换成笼统的词；不加定稿没有的事件、画面、动作、结论；珠子的比喻不写成他真的经历的事。
4. 正文里不写小节号或“第几小节”这类位置说明。
5. 下面“守护”里列的内容，别的读者说过删了就是退步，不许删、不许改淡。
6. 话这一行改了，keys 也要给（照抄新 text 里连续的字，1–2 个）；感受行改了，给出整行改后的全部短语，块数可以变，但不能把一行改成长句。

只输出 JSON：{"edits":[{"row":"S05-r1","text":"改后的话（只对话行）","keys":["…"],"items":["改后的短语（只对感受行）"],"fix":"对应哪条问题、怎么改的"}],"skip":[{"issue":"…","why":"…"}]}

【守护】
{GUARD}

【评审挑出的问题】
{ISSUES}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(REP, 'repair.py')
import os
SHR = float(os.environ.get('REP_SHRINK', '0')); KEEPK = os.environ.get('REP_KEEPKEYS') == '1'   # 11-08：改后至少保留原长的这个比例（0 = 不限）


def screen_text(w, scr):
    win = pub16.windows(w); out = []
    for s in scr['sections']:
        out.append(f"\n### {s['sec']}（停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for k, x in enumerate(s['rows'], 1):
            rid = f"{s['sec']}-r{k}"
            if x['kind'] == 'line':
                t = x['text']
                for kk in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(kk, f'【{kk}】', 1)
                out.append(f"话 [{rid}]：{t}")
            else: out.append(f"感受 [{rid}]：" + ' / '.join(i['text'] for i in x['items']))
    return '\n'.join(out)


def issues_text(w, src):
    out = []
    for j in JUDGES:
        p = S/f'open_{w}_{j}_{src}.json'
        if not p.exists(): continue
        r = rd(p)
        for x in r.get('issues') or []: out.append(f"- {x.get('sec')}（标准 {x.get('std')}）「{x.get('quote')}」：{x.get('why')} 建议：{x.get('better')}")
        for c in r.get('cumulative') or []:
            if (c.get('severity') or '') in ('严重', '中等'): out.append(f"- 跨段（标准 {c.get('std')}，{c.get('severity')}）{c.get('phenomenon')}；例：{'；'.join(c.get('evidence') or [])[:200]}")
    return '\n'.join(out)


def guard_text(w, tags):
    out = []
    for t in tags:
        for j in JUDGES:
            for seat in 'XY':
                p = S/f'vs2_{w}_{j}_{t}_{seat}.json'
                if p.exists():
                    r = rd(p); lost = r.get('lost') or r.get('regress') or []
                    out += [f"- {x}" for x in (lost if isinstance(lost, list) else [lost]) if x]
    return '\n'.join(out[:40]) or '（无）'


def one(a):
    w, src, new, guards = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json'))
    std = open('D:/musicclaude/_video_public_20261104/大众版标准.md', encoding='utf-8').read()
    std = std[std.index('## 内容（屏幕稿）'):std.index('## 画面')]
    msg = REP.replace('{STD}', std).replace('{GUARD}', guard_text(w, guards)).replace('{ISSUES}', issues_text(w, src)).replace('{SCREEN}', screen_text(w, scr))
    if KEEPK: msg = msg.replace('6. 话这一行改了，keys 也要给（照抄新 text 里连续的字，1–2 个）', '6. 话里【】放大的关键词一个字都不许改、不许删，只改它周围的字；keys 照原样给')
    rows = {f"{s['sec']}-r{k}": x for s in scr['sections'] for k, x in enumerate(s['rows'], 1)}
    for t in range(3):
        ans = call(f'pub24RP{"2" if SHR else ""}{"K" if KEEPK else ""}_{w}_{new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-repair')
        try:
            r = parse(ans); n = grow = 0
            for e in r.get('edits') or []:
                x = rows.get(e.get('row'))
                if x is None: continue
                if x['kind'] == 'line' and (e.get('text') or '').strip():
                    tx = e['text'].strip()
                    if len(tx) > len(x['text']) + 2 or len(tx) < len(x['text'])*SHR: grow += 1; continue   # 改后不变长（容 2 字）；11-08 K3NR 修补删得太多（覆盖 0.48），也不许缩太多
                    if KEEPK and not all(k in tx for k in x.get('keys') or []): grow += 1; continue   # 11-08 K3NR2 船歌扫得动 0:8：放大词保持原样，改动不许动到放大词
                    x['text'] = tx; x['keys'] = ([k for k in x.get('keys') or [] if k in tx] if KEEPK else ([k for k in (e.get('keys') or []) if k and k in tx][:2] or [k for k in x.get('keys') or [] if k in tx])); n += 1
                elif x['kind'] == 'feel' and e.get('items'):
                    its = [str(i).strip().rstrip('，。、；') for i in e['items'] if str(i).strip()]
                    o = sum(len(i['text']) for i in x['items'])
                    if sum(map(len, its)) > o + 2 or sum(map(len, its)) < o*SHR: grow += 1; continue
                    old = x['items']; bead = old[0].get('bead') if old else ''
                    # 新短语按顺序沿用原块的珠子和到时信息（块数变了就按位置就近）
                    x['items'] = [dict(old[min(len(old)-1, round(q*len(old)/max(1, len(its))))], text=tx) if old else {'text': tx, 'bead': bead, 'bars': ''} for q, tx in enumerate(its)]; n += 1
            wr(p, scr); to_script(w, new, scr)
            print(w, new, '改了', n, '处；变长没采用', grow, '；跳过', len(r.get('skip') or []), '；小节号', gate2.barnums(w, new), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, new = sys.argv[1], sys.argv[2]; guards = sys.argv[3:]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, new, guards) for w in WORKS])), flush=True)
