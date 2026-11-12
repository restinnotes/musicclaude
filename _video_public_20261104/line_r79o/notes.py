"""11-09 晚 K21：感受分两处放——上半屏小字只放一眼扫的核心感受短语；对着具体小节、具体声音的细致感受放到可视化旁边的“旁注”，到那几小节才出现。
用户 11-09：“这种 原先那个小节的 然后这种左手的 我觉得应该都是能够去对应到可视化的旁边的吧 可以给可视化的旁边划一块区域啊 我说的细致的不就应该在这里吗 不是一定需要去混到主段落中吧”。
标准第 7 条：“讲观众此刻的体验，音乐本身只在帮人对上声音时才提”——旁注正是帮人对上声音的地方。
用户又说：“我不觉得珠子就天生应该更不重要啊 珠子很有可能就也是为线来offer的前提啊”——大小按这一刻的重要性定，不按来源；大字可以改写、把作为前提的珠子织进去。每屏一次调用：给这一屏现在的大字和小字、这一屏的定稿珠子（带小节），要求：
  上半屏小字：核心感受短语，每块 3–10 字，每屏不超过 秒数/5 块；
  旁注：每条一个“听到什么 + 带出的画面/感受”，约 6–18 字，写明小节（必须在这一屏的小节范围内），每屏不超过 秒数/5 条；
  珠子里有辨识度的内容要么进小字、要么进旁注，不丢（只有重复的可以并掉）。
数据：feel 行照旧（kind feel），旁注放在 section['notes'] = [{"text","bars","from"}]。
python notes.py SRC NEW g6|g56
"""
import copy, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, pub16
from refit import L
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, to_script

NT = """你在改一首钢琴曲大众版“边听边看”视频的一屏。画面：上半屏是文字，下半屏是跟着音乐滚动的音符动画；普通观众第一次看，边听边扫。这一屏停留 {SEC} 秒，对应音乐第 {BARS} 小节。
目标只有两条：一眼扫得过去；扫到的东西串得起来（知道这个人此刻怎么了，感受挂在他的处境上，连成一回事）。

材料有两种：线（这个人经历的事）和珠子（听的人此刻的感受）。两种同样重要：珠子常常就是线的前提——正因为此刻是这种感受，他的事才这样发生。所以什么写大、什么写小，按它在这一刻有多重要定，不按它来自线还是珠子。

屏幕上有三处文字：
- 大字（连贯）：这一刻最要紧的，一句完整、自然的话，1–2 个关键词放大。可以是他的事，也可以把珠子里那个让他的事成立的感受织进来。
- 小字（散落）：挂在某一句大字后面的核心感受，每块是一个画面、一种身体感觉或一句心里话，3–10 个字，像人随口说的。每块放在它所挂的那句大字后面。
- 旁注（新）：下半屏音符动画旁边的一块，对着具体某几小节、具体某个声音（某只手、某条旋律、某个和弦、某次停顿）的细致感受，到那几小节才出现，帮观众把耳朵听到的和画面对上。

请从现在这一屏出发重新组织：
1. 大字以现在的大字为底，可以改写、合并、调整先后，把珠子里作为前提的感受织进去；因果和转折的连接要留着，不压成电报句。这一屏大字一般 1–3 句。
2. 小字这一屏不超过 {MAXN} 块；旁注不超过 {MAXN} 条，每条 6–18 字，写明对应小节（必须在第 {BARS} 小节之内，写成“起–止”）。
3. 线和珠子里有辨识度的东西（原因、转折、画面、身体感觉、比喻、心里话）要么进大字、要么进小字、要么进旁注，不要丢；只有意思重复的可以并掉。尽量用原词，不换成笼统的说法。
4. 不加原来没有的意思；疑问仍是疑问；珠子的比喻仍是比喻（保留“像、仿佛”），不写成这个人真的经历的事；正文里不写小节号。

只输出 JSON：{"rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的字"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["编号"]},{"form":"散落","items":[{"text":"…","from":["编号"],"bars":""}]}],"notes":[{"text":"…","bars":"起–止","from":["珠子编号"]}]}

【这一屏现在的样子】
{CUR}

【这一屏的定稿线和珠子（内容依据，珠子带小节）】
{SRC}
"""
prompt_lint.lint(NT, 'notes.py')


def rng(b):
    m = re.findall(r'\d+', str(b)); return (int(m[0]), int(m[-1])) if m else None


def show(s):
    out = []
    for x in s['rows']:
        if x['kind'] == 'line': out.append('大字：' + x['text'])
        else: out.append('小字：' + ' / '.join(i['text'] for i in x['items']))
    return chr(10).join(out)


def one(a):
    w, src, new, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); win = pub16.windows(w); s0 = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}

    def fix(k):
        s = scr['sections'][k]; dur = win[s['sec']][1]-win[s['sec']][0]; src0 = s0[s['sec']]
        lo, hi = rng(src0['bars']); maxn = max(2, round(dur/5))
        msg = (NT.replace('{SEC}', str(round(dur))).replace('{BARS}', src0['bars']).replace('{MAXN}', str(maxn)).replace('{CUR}', show(s))
               .replace('{SRC}', chr(10).join([f"线 {l['id']}：{l['text']}" for l in src0['lines']] + [f"珠子 {b['id']}（小节 {b['where']}）：{b['text']}" for b in src0['beads']])))
        for t in range(3):
            try:
                r = parse(call(f'notes_{w}_{s["sec"]}_{new}' + ('' if not t else f'_r{t}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-notes'))
                from refit import conv_rows
                rows = conv_rows(w, {'sections': [{'sec': s['sec'], 'rows': r.get('rows') or []}]})
                notes = [x for x in r.get('notes') or [] if (x.get('text') or '').strip()]
                feel = [i for x in rows if x['kind'] == 'feel' for i in x['items']]
                if not any(x['kind'] == 'line' for x in rows): raise ValueError('没有大字')
                if any(len(x['text']) > 14 for x in feel): raise ValueError('小字块太长 ' + max((x['text'] for x in feel), key=len))
                if any(len(x['text']) > 24 for x in notes): raise ValueError('旁注太长 ' + max((x['text'] for x in notes), key=len))
                if len(feel) > maxn+1 or len(notes) > maxn+1: raise ValueError(f'块数太多 小字{len(feel)} 旁注{len(notes)} / {maxn}')
                for x in notes:
                    b = rng(x.get('bars'))
                    if not b or b[0] < lo or b[1] > hi or b[0] > b[1]: raise ValueError(f"旁注小节不在本屏 {x.get('bars')}（{src0['bars']}）")
                    x['bars'] = f'{b[0]}–{b[1]}'
                if re.search(r'\d+\s*小节', ''.join(x['text'] for x in feel+notes) + ''.join(x['text'] for x in rows if x['kind'] == 'line')): raise ValueError('正文里写了小节号')
                s['rows'] = rows; items = feel
                s['notes'] = [{'text': x['text'].strip().rstrip('，。、；'), 'bars': x['bars'], 'from': x.get('from') or []} for x in notes]
                return f"{s['sec']} 小字 {len(items)} 块、旁注 {len(s['notes'])} 条"
            except Exception as ex: print('不合格', w, s['sec'], repr(ex)[:150], flush=True)
        return f"{s['sec']} 没改成"
    with ThreadPoolExecutor(8) as ex: log = [x for x in ex.map(fix, range(len(scr['sections']))) if x]
    wr(p, scr); to_script(w, new, scr)
    top = sum(L(s) for s in scr['sections']); nt = sum(len(x['text']) for s in scr['sections'] for x in s.get('notes') or [])
    print(w, new, '；'.join(log), f'；上半屏 {top} 字、旁注 {nt} 字', flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
