"""大众版视频稿流程。只读 DAG2 的冻结输入，只写本目录和 evo 的 runs/pub_*。

python pub.py prepare          冻结输入、拆要点、算预算
python pub.py rank             独立排序（每首 4 份）
python pub.py aggregate        合并排序，冻结“不能掉”清单
python pub.py write [tag]      写视频稿
python pub.py check [tag]      机械检查
python pub.py judge [tag]      对照 + 只读线 + 扫读复述
"""
import json, os, re, shutil, sys, threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAG2 = Path('D:/musicclaude/_dag2_video_20261104')
EVO = Path('D:/musicclaude/_thread_evo_20261019')
WORKS = ['op60', 'op61']
SECONDS_PER_ITEM = 6.0
SECONDS_PER_LINE = 18.0
MAX_BEAD = 20
MAX_LINE = 24
MAX_KEY = 10
LOCAL_RATIO = 0.5
SENT = re.compile(r'[^。！？；]+[。！？；]*[”」』）]*')


def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p, x):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=1), encoding='utf-8')
def chars(s): return len(re.sub(r'[\s，。、！？；：“”‘’（）…—,.!?;:"\']', '', s))
def parse(text):
    text = text.strip()
    m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.S)
    if m: text = m.group(1)
    return json.JSONDecoder().raw_decode(text[text.find('{'):])[0]


def evo_call(rid, msg, model='gpt-6-thinking', stage='public-video'):
    os.environ['THREAD_ROUTE'] = 'gpt3s'; os.environ.setdefault('JV', '2')
    sys.path.insert(0, str(EVO))
    import evo
    answer = evo.call(rid, msg, model=model, meta={'stage': stage, 'web': True})
    return answer


# ---------- 冻结输入、拆要点、算预算 ----------
def prepare():
    for w in WORKS:
        for name, src in [(f'{w}.json', DAG2/f'input/{w}.json'), (f'{w}_music.json', DAG2/f'input/{w}_music.json'),
                          (f'{w}_graph.json', DAG2/f'plans/{w}_v2_graph.json')]:
            if not (ROOT/'input'/name).exists():
                shutil.copy2(src, ROOT/'input'/name)
        src = rd(ROOT/f'input/{w}.json'); graph = rd(ROOT/f'input/{w}_graph.json')
        out = {'work': w, 'title': src['title'], 'performer': src.get('performer', ''), 'audio': src['audio'], 'sections': []}
        for s, g in zip(src['segments'], graph['segments']):
            assert s['sec'] == g['sec']
            lo, hi = g['window']; dur = hi-lo
            points = []
            for nd in g['nodes']:
                # 按原文字符位置把每句对回 V2 的局部时间分块
                for i, m in enumerate(SENT.finditer(nd['text'])):
                    t = m.group(0).strip()
                    if not t: continue
                    best = None
                    for ch in nd['chunks']:
                        ov = min(m.end(), ch['end'])-max(m.start(), ch['start'])
                        if ov <= 0: continue
                        wins = ch.get('windows') or [ch['window']]
                        span = sum(b-a for a, b in wins)
                        if best is None or ov > best[0] or (ov == best[0] and span < best[1]):
                            best = (ov, span, wins, ch.get('bars'))
                    wins = best[2] if best else [g['window']]
                    span = best[1] if best else dur
                    local = span < LOCAL_RATIO*dur
                    points.append({'id': f"{nd['id']}-p{i+1}", 'bead': nd['id'], 'text': t, 'windows': wins, 'local': local,
                                   'bars': best[3] if best else None})
            K = len(s['items'])
            lines = max(1, min(K, round(dur/SECONDS_PER_LINE)))
            items = max(lines+2, round(dur/SECONDS_PER_ITEM))
            out['sections'].append({'sec': s['sec'], 'bars': s['bars'], 'window': [lo, hi], 'seconds': round(dur, 1),
                                    'lines': [{'id': x['id'], 'text': x['text']} for x in s['items']], 'points': points,
                                    'budget': {'lines': lines, 'beads': items-lines}})
        wr(ROOT/f'plans/{w}_points.json', out)
        n = sum(len(x['points']) for x in out['sections']); l = sum(p['local'] for x in out['sections'] for p in x['points'])
        b = sum(x['budget']['beads'] for x in out['sections']); ln = sum(x['budget']['lines'] for x in out['sections'])
        print(w, '要点', n, '局部', l, '预算珠子', b, '预算线', ln, '字数上限', b*MAX_BEAD+ln*MAX_LINE, flush=True)


def source_block(w, locals_tag=False):
    d = rd(ROOT/f'plans/{w}_points.json'); rows = []
    for s in d['sections']:
        rows.append(f"\n## {s['sec']}（这段音乐 {round(s['seconds'])} 秒）\n线：")
        rows += [f"- {x['id']}：{x['text']}" for x in s['lines']]
        rows.append('珠子要点：')
        for p in s['points']:
            tag = ''
            if locals_tag and p['local']:
                at = round(p['windows'][0][0]-s['window'][0])
                tag = f"［局部，这段第{at}秒起］"
            rows.append(f"- {p['id']}{tag}：{p['text']}")
    return d, '\n'.join(rows)


# ---------- 独立排序 ----------
RANK = """这是一首器乐作品“边听边读”视频里的文字。
线：一个人在这首曲子里经历的一件事，每段几条。珠子：逐段的听感记录，这里已按句拆成要点。

我们要给只会扫一眼的普通观众做一个短版。你的任务只有一个：判断什么最不能丢，从主要到次要排好。你不写短版，也不用考虑字数。

每一段请这样做：
1. 先把珠子要点按听感分组。同一种听感归一组，同一颗珠子的句子可以分到不同组。
2. 组按主次排序，组内要点也按主次排序。每条要点都要出现一次。
3. 给要点分档。A：丢了，这一段就变成另一回事。B：重要，但同组别的句子能顶上。没列进 A、B 的就是可以丢的。A 要少。
4. 选 only_one：这段观众只能记住一条要点，该是哪条。
5. 线的条目同样排序分档。A：丢了，这件事就讲不通或后面接不上。

判断主次时问自己：观众正听着这段音乐，扫一眼，记住哪句最能让他对上这段的声音和心情？
- 不按文采排。漂亮比喻、写了小节数的句子不自动更重要。
- 一段里有几种不同的听感时，不要把它们压成一种，每种都要有自己最该留的要点。

全曲再做一件事：spine，从线的条目里选不超过 8 条，只读这几条也能讲清这件事。

只输出 JSON，id 必须照抄：
{"sections":[{"sec":"S01","groups":[{"label":"这种听感的几个字","points":["S01-B1-p1"]}],"tier_a":["S01-B1-p1"],"tier_b":["S01-B2-p1"],"only_one":"S01-B1-p1","line_order":["S01-1"],"line_a":["S01-1"]}],"spine":["S01-1"]}

作品文字：
"""
RANKERS = [('g6a', 'gpt-6-thinking'), ('g6b', 'gpt-6-thinking'), ('g56a', 'gpt-5-6-thinking'), ('g56b', 'gpt-5-6-thinking')]


def rank():
    def one(job):
        w, name, model = job
        _, block = source_block(w)
        msg = RANK+block
        # 句末随机差异靠模型本身；相同提示词要能区分记录，所以 run id 不同，正文相同
        for attempt in range(3):
            rid = f'pub_20261104_rank_{w}_{name}'+('' if attempt == 0 else f'_r{attempt}')
            ans = evo_call(rid, msg, model, 'public-rank')
            if not ans: continue
            try:
                d = parse(ans); check_rank(w, d); wr(ROOT/f'runs/rank_{w}_{name}.json', d); print(w, name, '完成', flush=True); return True
            except Exception as e:
                print(w, name, '格式不合格', repr(e)[:300], flush=True)
        return False
    jobs = [(w, n, m) for w in WORKS for n, m in RANKERS if not (ROOT/f'runs/rank_{w}_{n}.json').exists()]
    with ThreadPoolExecutor(4) as ex: print(list(ex.map(one, jobs)))


def check_rank(w, d):
    src = rd(ROOT/f'plans/{w}_points.json')
    secs = {s['sec']: s for s in d['sections']}
    for s in src['sections']:
        r = secs[s['sec']]
        want = {p['id'] for p in s['points']}; got = [x for g in r['groups'] for x in g['points']]
        assert set(got) <= want, (s['sec'], set(got)-want)
        missing = want-set(got)
        assert len(missing) <= max(1, len(want)//5), (s['sec'], 'missing', missing)
        assert set(r['line_order']) <= {x['id'] for x in s['lines']}


def aggregate():
    for w in WORKS:
        src = rd(ROOT/f'plans/{w}_points.json'); ranks = [rd(ROOT/f'runs/rank_{w}_{n}.json') for n, _ in RANKERS]
        N = len(ranks); table = {'work': w, 'rankers': N, 'sections': [], 'spine': []}
        spine = Counter(x for r in ranks for x in r.get('spine', []))
        table['spine'] = [k for k, v in spine.most_common() if v >= (N+1)//2]
        for s in src['sections']:
            votes = Counter(); only = Counter(); pos = defaultdict(list); lvotes = Counter(); lpos = defaultdict(list); glabels = []
            for r in ranks:
                sec = next(x for x in r['sections'] if x['sec'] == s['sec'])
                order = [p for g in sec['groups'] for p in g['points']]
                for i, p in enumerate(order): pos[p].append(i/max(1, len(order)-1))
                for p in sec.get('tier_a', []): votes[p] += 1
                # 每种听感最该留的一条也计一票，防止重点全落在同一种听感上
                for g in sec['groups'][:3]:
                    if g['points'] and g['points'][0] not in sec.get('tier_a', []): votes[g['points'][0]] += .5
                only[sec.get('only_one')] += 1
                glabels.append([g['label'] for g in sec['groups']])
                for i, l in enumerate(sec['line_order']): lpos[l].append(i/max(1, len(sec['line_order'])-1))
                for l in sec.get('line_a', []): lvotes[l] += 1
            ps = {p['id']: p for p in s['points']}
            rows = []
            for pid, p in ps.items():
                score = votes[pid]; mean = sum(pos[pid])/len(pos[pid]) if pos[pid] else 1
                rows.append({'id': pid, 'text': p['text'], 'votes': score, 'only': only[pid], 'mean_rank': round(mean, 3), 'local': p['local'],
                             'class': 'must' if (score >= N*.75 or only[pid] >= 2) else ('should' if score >= N*.5 else 'free')})
            rows.sort(key=lambda r: (-r['votes'], r['mean_rank']))
            lrows = [{'id': x['id'], 'text': x['text'], 'votes': lvotes[x['id']], 'mean_rank': round(sum(lpos[x['id']])/max(1, len(lpos[x['id']])), 3),
                      'class': 'must' if lvotes[x['id']] >= N*.75 else 'free'} for x in s['lines']]
            lrows.sort(key=lambda r: (-r['votes'], r['mean_rank']))
            table['sections'].append({'sec': s['sec'], 'budget': s['budget'], 'points': rows, 'lines': lrows, 'group_labels': glabels})
        wr(ROOT/f'plans/{w}_ranking_frozen.json', table)
        for t in table['sections']:
            print(w, t['sec'], '预算珠子', t['budget']['beads'], '不能掉', sum(r['class'] == 'must' for r in t['points']), '应留', sum(r['class'] == 'should' for r in t['points']), '线预算', t['budget']['lines'], '线不能掉', sum(r['class'] == 'must' for r in t['lines']), flush=True)


# ---------- 写视频稿 ----------
WRITE = """这是一首器乐作品“边听边读”视频的文字：线是一个人在这首曲子里经历的一件事，珠子是逐段的听感。原文太长，观众读不完。请把整首一次写成给大众看的短版。观众边听边扫一眼屏幕，不会专心读。

屏幕上的节奏是一拍一拍的：先亮一两句短珠子，这是观众正听到的；然后落下一句短线，这是他为什么会这样。读完珠子再读到线，要有“原来是这样”的感觉。线把这几句珠子串起来。

【短珠子】
- 每句不超过 20 字，一句只说一件听得到或感受得到的事。
- 尽量用原珠子的词。不加原文没有的画面和情节，不写小节数和时间。
- 直接说，不要格言，不要工整对称，不要解释你在做什么。“仿佛”“像”能省就省。
- 一段里有几种不同的听感时，不要压成一种。

【短线】
- 每句一句话，不超过 24 字，平常话，主语清楚。
- 只用原线的内容，可以合并几条，但不要新编事件、前史和对白。不要把珠子里的画面和比喻变成线里真的发生的事。
- 扫到任何一句，单独也能懂，不依赖上一句才看得懂。
- 只读线，从头到尾连起来仍然是一件有发展的事。每句线之间要接得上，这是整首一次写的原因。原线每条性质不同（有的讲发生了什么，有的讲反应，有的讲怕什么），你要让它们读起来是一条连续的路。
- 每句线选 key：句中最要紧的连续几个字（不超过 10 字，逐字取自这句线）。它会高亮，并进入旁边的提纲。

【局部要点】
标了［局部］的要点，只在音乐的那几小节才成立。用到它们时，同一段里要按小节从前到后摆，别的珠子和线摆在它们前后。听得出来的转折优先保留。

【阶段】
最后把整首分成 5–6 个阶段，每个阶段给一个不超过 10 字的 label。只读这些 label，要能看出这件事的走向。

【分量】
每段后面给了上限：线几句、珠子几句。这是上限，这段发生得少就写得少。短段只能留最要紧的。

只输出 JSON。from 填你用到的 id（线填线的 id，珠子填要点 id），可以多个。一拍里 beads 有 1–4 句：
{"phases":[{"label":"…","sections":["S01","S02"]}],"sections":[{"sec":"S01","beats":[{"beads":[{"text":"…","from":["S01-B1-p1"]}],"line":{"text":"…","key":"…","from":["S01-1"]}}]}]}

作品文字：
"""


def write_block(w):
    d, block = source_block(w, True)
    lim = '\n'.join(f"{s['sec']}：线最多 {s['budget']['lines']} 句，珠子最多 {s['budget']['beads']} 句" for s in d['sections'])
    return d, block+'\n\n各段上限：\n'+lim


def write(tag='a', model='gpt-6-thinking'):
    def one(w):
        _, block = write_block(w)
        msg = WRITE+block; errors = None; base = f'pub_20261104_write_{w}_{tag}'
        for attempt in range(4):
            rid = base+('' if attempt == 0 else f'_fix{attempt}')
            body = msg if errors is None else msg+'\n\n你上一版没过机械检查，请整首重写并修好这些问题：\n'+'\n'.join(errors)+'\n\n上一版：\n'+json.dumps(last, ensure_ascii=False)
            ans = evo_call(rid, body, model, 'public-write')
            if not ans: print(w, tag, '无返回', flush=True); continue
            try: last = parse(ans)
            except Exception as e:
                errors = [f'JSON 解析失败：{e}']; last = {}; continue
            errors = check_script(w, last)
            hard = [e for e in errors if not e.startswith('提示')]
            wr(ROOT/f'runs/script_{w}_{tag}.json', last); wr(ROOT/f'qa/script_{w}_{tag}_check.json', errors)
            print(w, tag, f'第{attempt+1}次', '问题', len(hard), hard[:6], flush=True)
            if not hard: return True
            errors = hard
        return False
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, WORKS)))


def check_script(w, d):
    src = rd(ROOT/f'plans/{w}_points.json'); errs = []
    secs = {s['sec']: s for s in d.get('sections', [])}
    all_lines = []
    for s in src['sections']:
        r = secs.get(s['sec'])
        if not r: errs.append(f"{s['sec']} 缺失"); continue
        ids = {p['id']: p for p in s['points']}; lids = {x['id'] for x in s['lines']}
        beads = [b for bt in r['beats'] for b in bt['beads']]; lines = [bt['line'] for bt in r['beats'] if bt.get('line')]
        if len(lines) > s['budget']['lines']: errs.append(f"{s['sec']} 线 {len(lines)} 句，超过上限 {s['budget']['lines']}")
        if len(beads) > s['budget']['beads']: errs.append(f"{s['sec']} 珠子 {len(beads)} 句，超过上限 {s['budget']['beads']}")
        if not lines: errs.append(f"{s['sec']} 没有线")
        last = -1
        for b in beads:
            if chars(b['text']) > MAX_BEAD: errs.append(f"{s['sec']} 珠子过长（{chars(b['text'])} 字）：{b['text']}")
            if re.search(r'\d|小节|第[一二三四五六七八九十]+[段拍]', b['text']): errs.append(f"{s['sec']} 珠子含定位：{b['text']}")
            bad = [x for x in b.get('from', []) if x not in ids]
            if bad or not b.get('from'): errs.append(f"{s['sec']} 珠子 from 不对：{b['text']} {bad}")
            loc = [ids[x] for x in b.get('from', []) if x in ids and ids[x]['local']]
            if loc:
                t = min(p['windows'][0][0] for p in loc); e = max(p['windows'][-1][1] for p in loc)
                # 时间窗有重叠不算颠倒；只有这句整段都早于前一句的起点才算
                if e < last-.5: errs.append(f"{s['sec']} 局部要点顺序颠倒：{b['text']}")
                last = max(last, t)
        for bt in r['beats']:
            l = bt.get('line')
            if not l: continue
            all_lines.append(l['text'])
            if chars(l['text']) > MAX_LINE: errs.append(f"{s['sec']} 线过长（{chars(l['text'])} 字）：{l['text']}")
            if l.get('key') and (l['key'] not in l['text'] or chars(l['key']) > MAX_KEY): errs.append(f"{s['sec']} key 不合格：{l['key']} / {l['text']}")
            if not l.get('key'): errs.append(f"{s['sec']} 缺 key：{l['text']}")
            bad = [x for x in l.get('from', []) if x not in lids]
            if bad or not l.get('from'): errs.append(f"{s['sec']} 线 from 不对：{l['text']} {bad}")
            if len(bt['beads']) > 4: errs.append(f"{s['sec']} 一拍超过 4 句珠子")
    secset = [s['sec'] for s in src['sections']]; ph = [x for p in d.get('phases', []) for x in p['sections']]
    if ph != secset: errs.append('阶段没有按顺序覆盖全部段')
    if not 4 <= len(d.get('phases', [])) <= 7: errs.append('阶段数不在 5–6')
    for p in d.get('phases', []):
        if chars(p['label']) > MAX_KEY: errs.append(f"阶段 label 过长：{p['label']}")
    return errs


def plain(w, tag):
    d = rd(ROOT/f'runs/script_{w}_{tag}.json'); rows = []
    for s in d['sections']:
        rows.append(f"\n【{s['sec']}】")
        for bt in s['beats']:
            for b in bt['beads']: rows.append('珠：'+b['text'])
            if bt.get('line'): rows.append('线：'+bt['line']['text'])
    return d, '\n'.join(rows)


# ---------- 验收 ----------
JUDGE_KEEP = """这是一首器乐作品视频的文字。原文很长，下面有一份已经冻结的“不能掉”清单，是独立排序得出的；还有给大众看的短版。请逐条对照。

对清单里每一条，判断短版有没有把这个意思留下来：保留 / 部分 / 丢失。意思留下就算，不要求原词。部分和丢失要说明缺了什么，保留要写出短版里对应的那句。

再查短版里有没有原文没有的内容：新编的事件、画面、情节，或者把珠子里的比喻写成线里真的发生的事。逐条列出，附原文依据为什么不支持。没有就写空。

只输出 JSON：
{"items":[{"id":"…","verdict":"保留|部分|丢失","where":"短版对应句或空","note":"…"}],"added":[{"text":"短版的句子","why":"…"}],"summary":"两三句话说最大的损失"}

"""
JUDGE_THREAD = """下面是一首器乐作品视频里一条线的全部句子，一个人在这首曲子里经历的一件事。每句不超过 24 字，观众只会扫一眼。请只凭这些句子评审：
1. 连着读，每句接得上前一句吗？指出接不上的具体位置。
2. 是不是一件有发展的事，而不是在原地重复？指出重复的地方。
3. 随便扫到一句，单独能懂吗？指出离开上下文看不懂的句子。
4. 像不像一个人平常讲自己的经历？指出像格言、心理分析、抽象、工整对称的句子。
5. 只有问题才列，严重程度分 严重 / 中等 / 轻微。不要提修改方案。

只输出 JSON：{"issues":[{"kind":"接不上|重复|单独不懂|不像人话","severity":"…","quote":"…","why":"…"}],"score":0到10,"summary":"两三句话"}

线：
"""
JUDGE_GLANCE = """假设你在听一首钢琴曲，屏幕下方是音符动画，上方不时冒出一句短文字。你没有专心读，只是一边听一边扫一眼。下面就是你扫到的全部文字，按出现顺序排列（“珠”是说此刻听到什么，“线”是这个人的经历）。这些是你唯一的信息。

看完请回答：
1. 用五六句话复述：这个人经历了一件什么事？从哪里开始，中间怎么变，到哪里结束？
2. 逐段用一句话说：这段音乐听起来是什么感觉？
3. 你在哪些地方感到跟不上、看不懂，或者珠和线对不上？逐条列出。

只输出 JSON：{"story":"…","sections":[{"sec":"S01","felt":"…"}],"lost":[{"where":"S03","quote":"…","why":"…"}]}

文字：
"""
JUDGE_RECALL = """下面是观众只扫了一遍短文字后的复述，以及独立排序冻结的“不能掉”要点。逐条判断：只凭这份复述，这条要点的意思有没有传到观众那里？到了 / 部分 / 没到。只判复述写出来的内容，不要帮它补。

只输出 JSON：{"items":[{"id":"…","verdict":"到了|部分|没到"}],"summary":"两三句话"}

"""


def musts(w):
    r = rd(ROOT/f'plans/{w}_ranking_frozen.json'); rows = []
    for s in r['sections']:
        rows += [{'id': x['id'], 'text': x['text']} for x in s['lines'] if x['class'] == 'must']
        rows += [{'id': x['id'], 'text': x['text']} for x in s['points'] if x['class'] == 'must']
    return rows


def judge(tag='a'):
    def run(job):
        w, name, model, msg = job
        p = ROOT/f'runs/judge_{w}_{tag}_{name}.json'
        if p.exists(): return rd(p)
        for attempt in range(3):
            ans = evo_call(f'pub_20261104_judge_{w}_{tag}_{name}'+('' if not attempt else f'_r{attempt}'), msg, model, 'public-judge')
            if not ans: continue
            try: d = parse(ans); wr(p, d); return d
            except Exception as e: print(w, name, '解析失败', e, flush=True)
        return None
    jobs = []
    for w in WORKS:
        d, text = plain(w, tag); _, block = source_block(w)
        m = json.dumps(musts(w), ensure_ascii=False)
        lines = '\n'.join(bt['line']['text'] for s in d['sections'] for bt in s['beats'] if bt.get('line'))
        jobs += [(w, 'keep', 'gpt-6-thinking', JUDGE_KEEP+'【不能掉清单】\n'+m+'\n\n【原文】'+block+'\n\n【短版】'+text),
                 (w, 'thread_g6', 'gpt-6-thinking', JUDGE_THREAD+lines),
                 (w, 'thread_g56', 'gpt-5-6-thinking', JUDGE_THREAD+lines),
                 (w, 'glance', 'gpt-6-thinking', JUDGE_GLANCE+text)]
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(run, jobs))
    for w in WORKS:
        g = rd(ROOT/f'runs/judge_{w}_{tag}_glance.json')
        run((w, 'recall', 'gpt-6-thinking', JUDGE_RECALL+'【复述】\n'+json.dumps(g, ensure_ascii=False)+'\n\n【要点】\n'+json.dumps(musts(w), ensure_ascii=False)))
    summary(tag)


def summary(tag='a'):
    out = {}
    for w in WORKS:
        keep = rd(ROOT/f'runs/judge_{w}_{tag}_keep.json'); recall = rd(ROOT/f'runs/judge_{w}_{tag}_recall.json')
        c = Counter(x['verdict'] for x in keep['items']); r = Counter(x['verdict'] for x in recall['items'])
        th = [rd(ROOT/f'runs/judge_{w}_{tag}_{n}.json') for n in ['thread_g6', 'thread_g56']]
        out[w] = {'对照': dict(c), '新增内容': len(keep.get('added', [])), '扫读后传到': dict(r), '线评分': [t.get('score') for t in th],
                  '线严重问题': sum(i.get('severity') == '严重' for t in th for i in t['issues']), '线中等问题': sum(i.get('severity') == '中等' for t in th for i in t['issues'])}
    wr(ROOT/f'qa/judge_summary_{tag}.json', out); print(json.dumps(out, ensure_ascii=False, indent=1))


REVISE = """下面是你（或同事）写的短版，已经被检查过。请整首改一遍，输出完整的新版，格式不变。

规则和之前一样，另外三条这次要特别做到：
1. 一句珠子只说一件事。上一版常把两件事用逗号拼成一句，from 一口气写五六个要点，观众扫一眼抓不住。一句 from 最好不超过 3 个。两件都要紧就拆成两句，上限还有余量。
2. 局部句钉在音乐的那一秒，放不下的问题要靠调整前后的句子解决。每句至少要占 4 秒，所以钉在段尾的句子后面不能再排很多句。
3. 只读线要连得上，线之间不要每句都以“他”开头、一个句式到底。不要加新内容，也别为了改而改，没问题的句子保留。
4. 下面有些意见嫌没交代具体事件、这个人是谁、离开了什么。这些不要补：这件事本来就不编具体事件和人物。只修接不上和看不懂。

要修的问题：
"""


def schedule_errors(w, tag):
    import film_pub
    _, items, _ = film_pub.schedule(w, tag)
    pts = {s['sec']: s for s in rd(ROOT/f'plans/{w}_points.json')['sections']}
    errs = []
    for x in items:
        if abs(x.get('drift', 0)) > 2:
            lo, hi = pts[x['sec']]['window']
            errs.append(f"{x['sec']}（这段 {round(hi-lo)} 秒）：“{x['text']}”应在这段第 {round(x['anchor']-lo)} 秒出现，但前后句子太挤，偏了 {abs(x['drift']):.0f} 秒")
    return errs


def revise(spec):
    """spec 形如 op60=a,op61=b：每首选一个样本，结合评审交回修改，得到 tag r1。"""
    picks = dict(x.split('=') for x in spec.split(','))
    def one(w):
        tag = picks[w]; old = rd(ROOT/f'runs/script_{w}_{tag}.json')
        keep = rd(ROOT/f'runs/judge_{w}_{tag}_keep.json'); glance = rd(ROOT/f'runs/judge_{w}_{tag}_glance.json')
        must = {x['id']: x['text'] for x in musts(w)}
        rows = []
        for it in keep['items']:
            if it['verdict'] != '保留': rows.append(f"不能掉的要点没留够（{it['verdict']}）：{must.get(it['id'], it['id'])}。{it.get('note','')}")
        rows += [f"原文没有的内容：{x['text']}。{x['why']}" for x in keep.get('added', [])]
        for n in ['thread_g6', 'thread_g56']:
            for i in rd(ROOT/f'runs/judge_{w}_{tag}_{n}.json')['issues']:
                if i.get('severity') in ('严重', '中等'): rows.append(f"只读线：{i['kind']}：“{i['quote']}”。{i['why']}")
        rows += [f"扫读时跟不上：{x['where']} “{x.get('quote','')}”。{x['why']}" for x in glance.get('lost', [])]
        rows += ['时间放不下：'+e for e in schedule_errors(w, tag)]
        _, block = write_block(w)
        msg = WRITE+block+chr(10)*2+REVISE+chr(10).join('- '+r for r in rows)+chr(10)*2+'上一版：'+chr(10)+json.dumps(old, ensure_ascii=False)
        last = old; errors = None
        for attempt in range(3):
            body = msg if errors is None else msg+chr(10)*2+'上一次改完没过机械检查，修好这些再输出：'+chr(10)+chr(10).join(errors)+chr(10)*2+'你改的那一版：'+chr(10)+json.dumps(last, ensure_ascii=False)
            ans = evo_call(f'pub_20261104_revise_{w}_{tag}'+('' if not attempt else f'_fix{attempt}'), body, 'gpt-6-thinking', 'public-revise')
            if not ans: continue
            try: last = parse(ans)
            except Exception as e: errors = [f'JSON 解析失败：{e}']; continue
            errors = [e for e in check_script(w, last) if not e.startswith('一拍')]
            wr(ROOT/f'runs/script_{w}_r1.json', last)
            print(w, '修改第', attempt+1, '次，问题', len(errors), errors[:5], flush=True)
            if not errors: return True
        return False
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, WORKS)))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cmd = sys.argv[1]; arg = sys.argv[2:]
    if cmd == 'prepare': prepare()
    elif cmd == 'rank': rank()
    elif cmd == 'aggregate': aggregate()
    elif cmd == 'write': write(*(arg or ['a']))
    elif cmd == 'check':
        for w in WORKS: print(w, check_script(w, rd(ROOT/f"runs/script_{w}_{arg[0] if arg else 'a'}.json")))
    elif cmd == 'judge': judge(*(arg or ['a']))
    elif cmd == 'summary': summary(*(arg or ['a']))
    elif cmd == 'revise': revise(arg[0])
