"""大众版方向试验：直白短句、异质分组、情绪色、模型看编码决定标哪些音符。全走 gpt3。
python pub3.py write TAG      两首同跑写稿
python pub3.py marks TAG      两首同跑标音符
"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pub2
from pub2 import rd, wr, parse, call, G6, WORKS, source_matched, tidy_keys
ROOT = Path(__file__).resolve().parent; OUT = ROOT/'r3'; OUT.mkdir(exist_ok=True)
EMOTIONS = {'炽热': (235, 84, 72), '欢喜': (243, 184, 78), '亲密': (240, 146, 178), '安心': (108, 208, 164), '孤单': (92, 154, 240), '不安': (172, 132, 240), '悬着': (186, 192, 204)}
EMO_DESC = """炽热（红）：激动、狂喜、愤怒、不顾一切
欢喜（金）：温暖、幸福、满足、明亮
亲密（粉）：贴近、甜、柔情、舍不得
安心（绿）：放松、松一口气、释然、踏实
孤单（蓝）：空落、失落、冷、一个人
不安（紫）：害怕、挣扎、怀疑、堵着
悬着（灰白）：茫然、停住、说不清、还没落下"""

WRITE = """你在给一首钢琴曲做“边听边看”视频的大众版文字。观众在听音乐，眼睛只是扫屏幕，一眼抓几个词。

下面的原文已经按匹配分好组：每段有几条线（一个人经历的一件事），每条线下面是和它意思最接近的珠子（听的人当下的感受，［］里是它在这段的角色）。同一段的几组是这段同时存在的不同侧面，不是时间先后。

请整首一次写完。

【一屏只够扫几眼】
观众在这一屏上眼睛只落几下，每落一下抓到一个念头。你的任务不是把原文逐条缩短，而是替观众挑：这组里什么最打动人就留什么，其余大胆舍掉。原文的大部分句子都不会出现在屏幕上。
一句只放一个念头。不要用逗号、分号把几个念头串成一句；串起来的，留最有力的那个。
同一个感受、同一个比喻只说一遍。几条珠子说的是一种感觉，只留最好的一个说法。
次组比主组更少，只留让人看出“这里还有另一面”的那一点。
最后的“不能掉”清单里的意思要留下（可以换说法，可以并进别的句子）；不在清单里的，按打动人的程度取舍。

【说话方式：直接】
不用写成完整的陈述句。可以是短语、一声感叹、一个问句，像心里闪过的话，一扫就懂。
不要“他感到非常孤单”，要“只剩自己了”。不要“这段音乐让人产生一种失去支撑的感觉”，要“脚下一空”。
线也这样：不用交代语法上的主语和因果，但单独扫到要懂，意思不能走样，语气不能加重或减轻。如果这条线靠前面的经历才成立，留下那点来由。只读线连起来仍是一件有发展的事。
不写格言、不写心理分析、不写工整对称的句子。

【珠子写感受】
写听的人心里、身上的感觉。音乐本身发生了什么不是重点，只在能帮人对上声音时才提，提也只用大白话。
尽量用原珠子里的词和比喻，不要把不同珠子的比喻拼成新比喻，不加原文没有的画面和情节。

【一段里要真的不一样】
以原文的匹配为基础分组。没有珠子的线并进最相关的一组。说的是一回事才合并，同一种感受不要分成两组。
每组标 rank：这段最主要的一组是“主”，只有一个；其余是“次”。主组在屏幕上最大，次组小。
每组写 kind：这组是什么，几个字，比如“主要的感受”“中途变了”“另一面”“另一种听法”“他在怕什么”。不同组要真的是不同的东西。
一段实际有几种不同的东西就几组，发生得少就少。

【情绪色】
屏幕用颜色表达情绪，看到颜色就有感觉。每组一个 emotion，每句珠子也可以有自己的 emotion（和组不同时才写）。只能从下面选，按这句实际的情绪选，不要为了好看换色：
"""+EMO_DESC+"""

【关键词】keys：只扫这些词也能明白大意，逐字取自这句。整句都短时可以是整句。

【阶段】把整首分成几个阶段，每个 label 用直白的几个字，只读 label 能看出这件事的走向，并标 emotion。

只输出 JSON，from 填用到的原文 id。屏幕上不出现小节数和时间。
{"phases":[{"label":"…","emotion":"…","sections":["S01","S02"]}],"sections":[{"sec":"S01","groups":[{"rank":"主","kind":"…","emotion":"…","lines":[{"text":"…","keys":["…"],"from":["S01-1"]}],"beads":[{"text":"…","keys":["…"],"emotion":"…","from":["S01-B1-p1"]}]}]}]}

原文：
"""

ENCODING = """屏幕下方的音乐动画这样编码声音：
- 横轴是时间：中央是现在，右边是马上要响的，左边是刚响过的。
- 纵轴是音高：越高的音越靠上。
- 圆的大小是音的长短；线把同一声部前后的音连起来。
- 程序可以把一段时间内、一个音高范围内的音染成某句文字的颜色，它们会从右边过来、经过中央。其余的音保持暗淡。"""

MARKS = """下面是一首器乐曲视频的短文字，以及音符数据。

"""+ENCODING+"""

请逐句判断：这句文字在音乐动画上要不要标音符，标哪些。

只有观众能在动画上真的对上时才标：
- 句子说的是可以认出来的声音（高处、低处、只剩一条旋律、密集涌上来、停住了、很长的一个音……），并且在数据里能找到。
- 位置依据原文：原文写了这句属于某几小节的，就用那几小节；没写位置的，只能用这段的范围，或者在数据上确实能认出来的那几小节。认不出就不标，不要猜。
- 音高范围要收窄到句子说的那部分：说高处就只标高音，说低处就只标低音。
- 范围要窄到观众看得出“是这些音”：一大片时间里所有音都亮等于没标。只有说的就是全部声音、而且只占很短一段（比如突然停住、只剩一个音）时才可以不限音高。
纯粹讲心情、对不上具体声音的句子不标（render 填 false）。不必每段都标。

只输出 JSON，text 照抄：{"marks":[{"sec":"S01","text":"…","render":true,"bars":[1,3],"pitch":[70,102],"why":"一句话"},{"sec":"S01","text":"…","render":false,"why":"一句话"}]}
pitch 是音高数字（越大越高），不限音高写 null。

【短文字及其依据的原文】
{BEADS}

【音符数据：每小节】
{BARS}
"""


def write(tag):
    def one(w):
        p = OUT/f'script_{w}_{tag}.json'
        if p.exists(): return True
        keep = '\n'.join(f"- {x['id']}：{x['text']}" for x in pub2.musts(w))
        msg = WRITE+source_matched(w)+'\n\n【不能掉清单】\n'+keep; errs = None; prev = None
        for k in range(3):
            body = msg if errs is None else msg+'\n\n上一次输出没过检查，修好这些，其余不动，输出完整 JSON：\n'+'\n'.join(errs)+'\n\n上一次输出：\n'+(prev or '')
            prev = call(f'pub3_write_{w}_{tag}'+('' if not k else f'_fix{k}'), body, G6, 'gpt3s', 'public3-write')
            if not prev: continue
            try: d = tidy_keys(parse(prev)); errs = check(w, d)
            except Exception as e: errs = [f'JSON 解析失败：{e}']; continue
            print(w, tag, '第', k+1, '次，问题', len(errs), errs[:5], flush=True)
            wr(p.with_suffix('.try.json'), d)
            if not errs: wr(p, d); return True
        return False
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, WORKS)), flush=True)


def check(w, d):
    src = rd(pub2.OUT/f'{w}_src.json'); errs = []; secs = {s['sec']: s for s in d.get('sections', [])}
    for s in src['sections']:
        r = secs.get(s['sec'])
        if not r: errs.append(f"{s['sec']} 缺失"); continue
        if sum(g.get('rank') == '主' for g in r['groups']) != 1: errs.append(f"{s['sec']} 主组不是正好一个")
        for g in r['groups']:
            if g.get('emotion') not in EMOTIONS: errs.append(f"{s['sec']} 情绪不在列表：{g.get('emotion')}")
            for b in g.get('beads', []):
                if b.get('emotion') and b['emotion'] not in EMOTIONS: errs.append(f"{s['sec']} 情绪不在列表：{b['emotion']}")
            for x in g.get('lines', [])+g.get('beads', []):
                if re.search(r'\d|小节', x['text']): errs.append(f"{s['sec']} 含定位：{x['text']}")
        if not any(g.get('lines') for g in r['groups']): errs.append(f"{s['sec']} 没有线")
        if not any(g.get('beads') for g in r['groups']): errs.append(f"{s['sec']} 没有珠子")
    if [x for p in d.get('phases', []) for x in p.get('sections', [])] != [s['sec'] for s in src['sections']]: errs.append('阶段没有按顺序覆盖全部段')
    return errs


def bar_table(w):
    m = rd(ROOT/f'input/{w}_music.json'); bars = sorted((int(a), b) for a, b in (m['bars'].items() if isinstance(m['bars'], dict) else m['bars']))
    src = rd(pub2.OUT/f'{w}_src.json'); rows = []
    notes = m['notes']
    for i, (b, t) in enumerate(bars):
        end = bars[i+1][1] if i+1 < len(bars) else m['dur']
        ps = sorted(n['p'] for n in notes if t <= n['s'] < end)
        sec = next((s['sec'] for s in src['sections'] if s['window'][0] <= t < s['window'][1]), '')
        if not ps: rows.append(f"{sec} 第{b}小节 {end-t:.1f}秒 无音"); continue
        hi = ps[int(len(ps)*.85)]; lo = ps[int(len(ps)*.15)]
        rows.append(f"{sec} 第{b}小节 {end-t:.1f}秒 {len(ps)}个音 音高{ps[0]}–{ps[-1]} 下方多在{lo}以下 上方多在{hi}以上")
    return '\n'.join(rows)


def marks(tag):
    def one(w):
        p = OUT/f'marks_{w}_{tag}.json'
        if p.exists(): return True
        d = rd(OUT/f'script_{w}_{tag}.json'); src = {s['sec']: s for s in rd(pub2.OUT/f'{w}_src.json')['sections']}; rows = []
        for s in d['sections']:
            pts = {x['id']: (x, b) for b in src[s['sec']]['beads'] for x in b['points']}
            rows.append(f"\n{s['sec']}（小节 {src[s['sec']]['bars']}）")
            for g in s['groups']:
                for b in g.get('beads', []):
                    orig = [pts[x] for x in b.get('from', []) if x in pts]
                    loc = {o[1]['where'] for o in orig if o[1].get('where')}
                    rows.append(f"- 「{b['text']}」原文：{' '.join(o[0]['text'] for o in orig)[:260]}（原文标的范围：{'、'.join(sorted(loc)) or '全段'}）")
        msg = MARKS.replace('{BEADS}', '\n'.join(rows)).replace('{BARS}', bar_table(w))
        for k in range(3):
            ans = call(f'pub3_marks_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public3-marks')
            try: r = parse(ans); assert r['marks']; wr(p, r); print(w, '标音符', sum(x.get('render') is True for x in r['marks']), '/', len(r['marks']), flush=True); return True
            except Exception as e: print(w, '不合格', repr(e)[:200], flush=True)
        return False
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, WORKS)), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c, t = sys.argv[1], sys.argv[2]
    if c == 'write': write(t)
    elif c == 'marks': marks(t)
