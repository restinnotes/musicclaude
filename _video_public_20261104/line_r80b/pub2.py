"""大众版第二轮：照内容迭代流程走，起点 r78a。

prepare            从 r78a 取线和珠子，拆要点
rank               独立排序（目的已改：珠子重当下体验），合并后冻结
base               用首版做法在 r78a 上跑一份，作为比较起点（用户已否定这种做法）
open TAG           开放评审，只找问题
advise ROUND       顾问看材料，给诊断和候选（完整提示词）
gen NAME [..]      两首同跑候选
quick TAG BASE     快筛盲比 4 票
fair  TAG BASE     验收盲比 8 票（新版前后座位平衡）
keep  TAG          对照冻结排序，并查有没有编
"""
import json, os, re, sys, difflib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVO = Path('D:/musicclaude/_thread_evo_20261019')
WORKS = os.environ.get('PUB_WORKS', 'op60,op61').split(',')
NAME = {'op60': '船歌', 'op61': '幻想波兰舞曲', 'op52': '第四叙事曲'}
G6, G56 = 'gpt-6-thinking', 'gpt-5-6-thinking'
OUT = ROOT/'r2'; OUT.mkdir(exist_ok=True)
SENT = re.compile(r'[^。！？；]+[。！？；]*[”」』）]*')
DIMS = ['scan', 'string', 'exp', 'whole', 'plain']
DIM_CN = {'scan': '扫得到', 'string': '串得起', 'exp': '讲体验', 'whole': '不像截断、不妨碍理解', 'plain': '人话'}


def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p, x):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=1), encoding='utf-8')
def parse(text):
    # MimicGate 的输出常带 Markdown 转义
    import html
    text = html.unescape(text).replace(chr(92)+chr(10), chr(10)).strip()
    m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.S)
    if m: text = m.group(1)
    return json.JSONDecoder().raw_decode(text[text.find('{'):])[0]


def call(rid, msg, model=G6, route='gpt3s', stage='public2'):
    """生成走 route（写稿 mimic，评审 gpt3s），一条通路失败时换另一条。"""
    sys.path.insert(0, str(EVO)); os.environ.setdefault('JV', '2')
    import evo
    import mg_schedule, time, zlib
    rid = rid + os.environ.get('PUB_RIDSUF', '')   # 11-06：新线的工作副本加后缀，不命中旧线的缓存
    if route == 'gpt3s' and os.environ.get('PUB_SPLIT', '1') == '1' and zlib.crc32(rid.encode()) % 2:
        route = 'gpt4s'   # 11-05 用户：gpt4 修好了，一起用；按调用编号固定分流，重跑时仍走同一账号
    evo.TL.route = route
    for k in range(3):
        try:
            ans = evo.call(rid, msg, model=model, meta={'stage': stage, 'web': True})
        except mg_schedule.CoolingDown as e:
            # 普通冷却只影响 MimicGate；保护信号（suspicious）不换路，直接停
            if 'suspicious' in str(e) or route != 'mimic': raise
            print('MimicGate 冷却，改走 gpt3', rid, flush=True); break
        if ans: return ans
    if route == 'mimic':
        evo.TL.route = 'gpt3s'
        ans = evo.call(rid+'_g3', msg, model=model, meta={'stage': stage, 'web': True})
        evo.TL.route = route
        return ans
    return None


def _new_work_patch():
    """不是主线两首的作品：把它的路径登记进评审用的模块（只在内存里）。"""
    if all(w in ('op60', 'op61') for w in WORKS): return
    sys.path.insert(0, str(EVO)); os.environ.setdefault('JV', '2')
    import covjudge, work_meta
    for w in WORKS:
        m = work_meta.load(w); covjudge.NAME[w] = f"{m['title_zh']}{m['opus']}"; covjudge.STRUCT[w] = m['_dir']/'struct'


_new_work_patch()


# ---------- 素材 ----------
def prepare():
    for w in WORKS:
        lt = os.environ.get('LINE_TAG', 'r78a')   # 11-06：线的版本可换
        graph = rd(EVO/f'evaluations/v6fix/{w}_{lt}.json'); graph = graph.get('graph', graph)
        md = (EVO/f'evaluations/v6fix/合写_{w}_{lt}.md').read_text(encoding='utf-8')
        old = rd(ROOT/f'input/{w}_graph.json'); music = rd(ROOT/f'input/{w}_music.json')
        nodes = {n['text']: n for s in old['segments'] for n in s['nodes']}
        blocks = re.split(r'\n### ', md)[1:]
        assert len(blocks) == len(graph['segments'])
        out = {'work': w, 'center': graph.get('center'), 'sections': []}
        for bi, (g, sold, blk) in enumerate(zip(graph['segments'], old['segments'], blocks)):
            lines = [x['text'] for x in g['items']]
            beads, after = [], -1
            for para in re.split(r'\n\s*\n', blk):
                para = para.strip()
                if para.startswith('>'):
                    txt = re.sub(r'^> ?', '', para, flags=re.M)
                    where = re.search(r'<small>（(.*?)）</small>', txt)
                    txt = re.sub(r'\n?<small>.*?</small>', '', txt).strip()
                    beads.append({'text': txt, 'where': where.group(1) if where else '', 'after': after})
                else:
                    if any(para.startswith(l[:8]) for l in lines): after += 1
            lo, hi = sold['window']; dur = hi-lo; out_b = []
            for i, b in enumerate(beads):
                n = nodes.get(b['text'])
                if n is None:
                    best = difflib.get_close_matches(b['text'], list(nodes), 1, .6); assert best, (w, g['sec'], b['text'][:30]); n = nodes[best[0]]
                bid = f"{g['sec']}-B{i+1}"; pts = []
                for k, m in enumerate(SENT.finditer(b['text'])):
                    t = m.group(0).strip()
                    if not t: continue
                    best = None
                    for ch in n['chunks']:
                        ov = min(m.end(), ch['end'])-max(m.start(), ch['start'])
                        if ov <= 0: continue
                        wins = ch.get('windows') or [ch['window']]; span = sum(y-x for x, y in wins)
                        if best is None or ov > best[0] or (ov == best[0] and span < best[1]): best = (ov, span, wins)
                    wins = best[2] if best else [[lo, hi]]; span = best[1] if best else dur
                    pts.append({'id': f'{bid}-p{k+1}', 'text': t, 'local': span < .5*dur, 'windows': wins})
                out_b.append({'id': bid, 'text': b['text'], 'where': b['where'], 'after': b['after'], 'role': n.get('role'), 'points': pts})
            out['sections'].append({'sec': g['sec'], 'bars': g['bars'], 'window': [lo, hi], 'relation': g.get('relation'),
                                    'lines': [{'id': x['id'], 'text': x['text']} for x in g['items']], 'beads': out_b})
        wr(OUT/f'{w}_src.json', out)
        print(w, '段', len(out['sections']), '线', sum(len(s['lines']) for s in out['sections']), '珠', sum(len(s['beads']) for s in out['sections']),
              '要点', sum(len(b['points']) for s in out['sections'] for b in s['beads']), '局部', sum(p['local'] for s in out['sections'] for b in s['beads'] for p in b['points']))


def source(w, local=True, after=False):
    d = rd(OUT/f'{w}_src.json'); rows = [f"（全曲的中心：{d['center']}）"] if d.get('center') else []
    for s in d['sections']:
        rows.append(f"\n## {s['sec']}（这段音乐约 {round(s['window'][1]-s['window'][0])} 秒）\n线（这一段的几条，多半是一起描述这一段的）：")
        rows += [f"- {x['id']}：{x['text']}" for x in s['lines']]
        rows.append('珠子（听这一段的人写下的当下体验，已按句拆开）：')
        for b in s['beads']:
            for p in b['points']:
                tag = '［局部：只属于这段里靠第%d秒的那几小节］' % round(p['windows'][0][0]-s['window'][0]) if local and p['local'] else ''
                rows.append(f"- {p['id']}{tag}：{p['text']}")
    return '\n'.join(rows)


def source_matched(w):
    """把内容流程里已有的匹配（每颗珠子最接近哪条线，由覆盖评委判定）和珠子角色一起给出。"""
    d = rd(OUT/f'{w}_src.json'); rows = [f"（全曲的中心：{d['center']}）"] if d.get('center') else []
    for s in d['sections']:
        rows.append(chr(10)+f"## {s['sec']}（这段音乐约 {round(s['window'][1]-s['window'][0])} 秒）")
        for i, l in enumerate(s['lines']):
            rows.append(f"第{i+1}组  线 {l['id']}：{l['text']}")
            bs = [b for b in s['beads'] if b['after'] == i]
            if not bs: rows.append('  （这条线没有直接对应的珠子）')
            for b in bs:
                rows.append(f"  珠子 {b['id']}［{b.get('role') or ''}］：")
                for p in b['points']:
                    tag = '［局部：只属于这段里靠第%d秒的那几小节］' % round(p['windows'][0][0]-s['window'][0]) if p['local'] else ''
                    rows.append(f"    - {p['id']}{tag}：{p['text']}")
    return chr(10).join(rows)


# ---------- 独立排序 ----------
RANK = """这是一首器乐作品“边听边读”视频里的文字。
线：一个人在这首曲子里经历的一件事，每段几条，多半是一起描述这一段的。珠子：听这一段的人写下的当下体验，这里已按句拆成要点。

我们要给只会扫一眼屏幕的普通观众做一个短版。你的任务只有一个：判断什么最不能丢，从主要到次要排好。你不写短版，也不考虑篇幅。

珠子的目的是让观众感到“这段听起来心里、身上是什么感觉”。音乐事件本身（哪个声部、什么和声、什么音型）不是重点，除非它就是那个感受的抓手。

每一段：
1. 把珠子要点按感受分组。同一种感受归一组，同一颗珠子的句子可以分到不同组。
2. 组按主次排序，组内要点也按主次排序。每条要点都要出现。
3. 分档。A：丢了，这一段就变成另一回事。B：重要，但同组别的句子能顶上。其余可以丢。A 要少。
4. only_one：观众这段只能记住一条要点，该是哪条。
5. 线的条目同样排序分档。A：丢了，这件事就讲不通或后面接不上。

判断时问自己：观众正听着这段音乐，扫一眼，抓到什么最能让他对上这段的心情，并明白这个人此刻是怎么回事？
不按文采排；写了小节数不等于重要；一段里有几种不同的感受时，每种都要有它最该留的要点。

全曲再做一件事：spine，从线的条目里选少数几条，只读它们也能讲清这件事。

只输出 JSON，id 照抄：
{"sections":[{"sec":"S01","groups":[{"label":"这种感受的几个字","points":["S01-B1-p1"]}],"tier_a":["S01-B1-p1"],"tier_b":["S01-B2-p1"],"only_one":"S01-B1-p1","line_order":["S01-1"],"line_a":["S01-1"]}],"spine":["S01-1"]}

作品文字：
"""
RANKERS = [('g6a', G6), ('g6b', G6), ('g56a', G56), ('g56b', G56)]


def rank():
    def one(job):
        w, n, m = job; p = OUT/f'rank_{w}_{n}.json'
        if p.exists(): return True
        for k in range(3):
            ans = call(f'pub2_rank_{w}_{n}'+('' if not k else f'_r{k}'), RANK+source(w, local=False), m, 'gpt3s', 'public2-rank')
            try:
                d = parse(ans); assert len(d['sections']) == len(rd(OUT/f'{w}_src.json')['sections']); wr(p, d); print(w, n, '完成', flush=True); return True
            except Exception as e: print(w, n, '不合格', repr(e)[:200], flush=True)
        return False
    with ThreadPoolExecutor(4) as ex: print(list(ex.map(one, [(w, n, m) for w in WORKS for n, m in RANKERS])))
    for w in WORKS:
        src = rd(OUT/f'{w}_src.json'); rs = [rd(OUT/f'rank_{w}_{n}.json') for n, _ in RANKERS]; N = len(rs)
        table = {'work': w, 'sections': [], 'spine': [k for k, v in Counter(x for r in rs for x in r.get('spine', [])).most_common() if v >= 2]}
        for s in src['sections']:
            votes, only, pos, lv, lpos = Counter(), Counter(), defaultdict(list), Counter(), defaultdict(list)
            for r in rs:
                x = next(y for y in r['sections'] if y['sec'] == s['sec'])
                order = [p for g in x['groups'] for p in g['points']]
                for i, p in enumerate(order): pos[p].append(i/max(1, len(order)-1))
                for p in x.get('tier_a', []): votes[p] += 1
                for g in x['groups'][:3]:
                    if g['points'] and g['points'][0] not in x.get('tier_a', []): votes[g['points'][0]] += .5
                only[x.get('only_one')] += 1
                for i, l in enumerate(x['line_order']): lpos[l].append(i/max(1, len(x['line_order'])-1))
                for l in x.get('line_a', []): lv[l] += 1
            pts = [p for b in s['beads'] for p in b['points']]
            rows = sorted(({'id': p['id'], 'text': p['text'], 'votes': votes[p['id']], 'only': only[p['id']], 'mean_rank': round(sum(pos[p['id']])/max(1, len(pos[p['id']])), 3) if pos[p['id']] else 1.,
                            'class': 'must' if votes[p['id']] >= N*.75 or only[p['id']] >= 2 else ('should' if votes[p['id']] >= N*.5 else 'free')} for p in pts), key=lambda r: (-r['votes'], r['mean_rank']))
            lrows = sorted(({'id': l['id'], 'text': l['text'], 'votes': lv[l['id']], 'mean_rank': round(sum(lpos[l['id']])/max(1, len(lpos[l['id']])), 3), 'class': 'must' if lv[l['id']] >= N*.75 else 'free'} for l in s['lines']), key=lambda r: (-r['votes'], r['mean_rank']))
            table['sections'].append({'sec': s['sec'], 'points': rows, 'lines': lrows})
        wr(OUT/f'{w}_ranking.json', table)
        print(w, '不能掉：珠子要点', sum(r['class'] == 'must' for t in table['sections'] for r in t['points']), '线', sum(r['class'] == 'must' for t in table['sections'] for r in t['lines']))


def musts(w):
    r = rd(OUT/f'{w}_ranking.json'); rows = []
    for s in r['sections']:
        rows += [{'id': x['id'], 'text': x['text']} for x in s['lines'] if x['class'] == 'must']
        rows += [{'id': x['id'], 'text': x['text']} for x in s['points'] if x['class'] == 'must']
    return rows


# ---------- 统一的稿件格式 ----------
FORMAT = """

【输出格式（固定）】
只输出 JSON。每段一屏，同一屏的内容同时在屏幕上；一屏可以分几组，每组放一条或几条线和相关的珠子。keys 是这句里最该被扫到的词，会高亮，必须逐字取自这句。from 填你用到的原文 id。
{"phases":[{"label":"这一阶段的短语","sections":["S01","S02"]}],"sections":[{"sec":"S01","groups":[{"lines":[{"text":"…","keys":["…"],"from":["S01-1"]}],"beads":[{"text":"…","keys":["…"],"from":["S01-B1-p1"]}]}]}]}
屏幕上不出现小节数和时间。标了［局部］的要点只属于那几小节：用到时它会在那时才出现、并和音乐一起动。"""


def validate(w, d):
    src = rd(OUT/f'{w}_src.json'); errs = []
    secs = {s['sec']: s for s in d.get('sections', [])}
    order = [s['sec'] for s in src['sections']]
    for s in src['sections']:
        r = secs.get(s['sec'])
        if not r: errs.append(f"{s['sec']} 缺失"); continue
        ids = {p['id'] for b in s['beads'] for p in b['points']}|{b['id'] for b in s['beads']}; lids = {l['id'] for l in s['lines']}
        lines = [l for g in r.get('groups', []) for l in g.get('lines', [])]; beads = [b for g in r.get('groups', []) for b in g.get('beads', [])]
        if not lines: errs.append(f"{s['sec']} 没有线")
        if not beads: errs.append(f"{s['sec']} 没有珠子")
        for x, pool in [(l, lids) for l in lines]+[(b, ids|lids) for b in beads]:
            if re.search(r'\d|小节', x.get('text', '')): errs.append(f"{s['sec']} 含定位：{x.get('text')}")
            for k in x.get('keys', []):
                if k not in x.get('text', ''): errs.append(f"{s['sec']} 关键词不在句中：{k} / {x.get('text')}")
            if not x.get('keys'): errs.append(f"{s['sec']} 没标关键词：{x.get('text')}")
            bad = [y for y in x.get('from', []) if y not in pool]
            if bad: errs.append(f"{s['sec']} from 不存在：{bad}")
    if [x for p in d.get('phases', []) for x in p.get('sections', [])] != order: errs.append('阶段没有按顺序覆盖全部段')
    return errs


def tidy_keys(d):
    """关键词偶尔不是逐字子串，取最长公共片段。只影响高亮。"""
    for s in d.get('sections', []):
        for g in s.get('groups', []):
            for x in g.get('lines', [])+g.get('beads', []):
                out = []
                for k in x.get('keys', []):
                    if k in x['text']: out.append(k); continue
                    m = difflib.SequenceMatcher(None, k, x['text'], autojunk=False).find_longest_match()
                    if m.size >= 2: out.append(x['text'][m.b:m.b+m.size])
                x['keys'] = out
    return d


def mark(x):
    t = x['text']
    for k in sorted(x.get('keys', []), key=len, reverse=True):
        if k and f'【{k}】' not in t: t = t.replace(k, f'【{k}】', 1)
    return t


def screen(w, tag):
    """评委看到的样子：逐屏，【】是高亮词。"""
    d = rd(OUT/f'script_{w}_{tag}.json'); meta = rd(OUT/f'meta_{tag}.json') if (OUT/f'meta_{tag}.json').exists() else {}
    first = meta.get('order', '珠子在前'); src = {s['sec']: s for s in rd(OUT/f'{w}_src.json')['sections']}; rows = []
    for s in d['sections']:
        rows.append(f"\n【{s['sec']} 这一屏】")
        loc = {p['id'] for b in src[s['sec']]['beads'] for p in b['points'] if p['local']}
        for g in s['groups']:
            ls = ['线：'+mark(l) for l in g.get('lines', [])]
            bs = [('珠（到那几小节才出现）：' if any(y in loc for y in b.get('from', [])) and all(y in loc for y in b.get('from', [])) else '珠：')+mark(b) for b in g.get('beads', [])]
            rows += (bs+ls) if first == '珠子在前' else (ls+bs)
    return '\n'.join(rows)


def gen(name):
    """两首同跑。candidates/NAME.json：{order, steps:[提示词,…]}，{SOURCE} 是原文，{PREV} 是上一步输出。"""
    c = rd(OUT/f'candidates/{name}.json'); wr(OUT/f'meta_{name}.json', {'order': c.get('order', '珠子在前'), 'hypothesis': c.get('hypothesis', '')})
    def one(w):
        p = OUT/f'script_{w}_{name}.json'
        if p.exists(): return True
        prev = ''
        for i, step in enumerate(c['steps']):
            srcf = source_matched if c.get('matched') else source
            body = step.replace('{SOURCE}', srcf(w)).replace('{PREV}', prev)
            if i == len(c['steps'])-1: body += FORMAT
            ans = call(f'pub2_gen_{w}_{name}_s{i}', body, G6, 'gpt3s', 'public2-gen')
            if not ans: print(w, name, '无返回', flush=True); return False
            prev = ans
        errs = None
        for k in range(3):
            try:
                d = tidy_keys(parse(prev)); errs = validate(w, d)
            except Exception as e:
                errs = [f'JSON 解析失败：{e}']; d = None
            if not errs:
                wr(p, d); print(w, name, '完成', flush=True); return True
            print(w, name, '检查未过', errs[:4], flush=True)
            prev = call(f'pub2_gen_{w}_{name}_fix{k}', c['steps'][-1].replace('{SOURCE}', (source_matched if c.get('matched') else source)(w)).replace('{PREV}', '')+FORMAT+'\n\n上一次输出没过机械检查，修好这些问题，其余不动，输出完整 JSON：\n'+'\n'.join(errs)+'\n\n上一次输出：\n'+(prev or ''), G6, 'gpt3s', 'public2-gen')
            if not prev: return False
        return False
    with ThreadPoolExecutor(2) as ex: return all(ex.map(one, WORKS))


# ---------- 比较起点 ----------
def base():
    import pub
    for w in WORKS:
        p = OUT/f'script_{w}_base0.json'
        if p.exists(): continue
        src = rd(OUT/f'{w}_src.json')
        lim = '\n'.join(f"{s['sec']}：线最多 {max(1, min(len(s['lines']), round((s['window'][1]-s['window'][0])/18)))} 句，珠子最多 {max(2, round((s['window'][1]-s['window'][0])/6)-max(1, min(len(s['lines']), round((s['window'][1]-s['window'][0])/18))))} 句" for s in src['sections'])
        ans = call(f'pub2_base0_{w}', pub.WRITE+source(w)+'\n\n各段上限：\n'+lim, G6, 'gpt3s', 'public2-base')
        o = parse(ans); out = {'phases': o['phases'], 'sections': []}
        for s in o['sections']:
            gs = []
            for bt in s['beats']:
                l = bt.get('line'); gs.append({'lines': [{'text': l['text'], 'keys': [l.get('key', '')], 'from': l.get('from', [])}] if l else [], 'beads': [{'text': b['text'], 'keys': [], 'from': b.get('from', [])} for b in bt['beads']]})
            out['sections'].append({'sec': s['sec'], 'groups': gs})
        wr(p, out)
    wr(OUT/'meta_base0.json', {'order': '珠子在前', 'hypothesis': '首版做法：按字数和句数上限压缩'})


# ---------- 开放评审 ----------
AUDIENCE = """观众在听音乐，眼睛是在扫屏幕，不是专心读。人扫的时候很快，抓的是关键词，不是一句句读完；【】里的词在屏幕上是高亮的。一屏的内容同时在屏幕上。"""
OPEN = """下面是一首钢琴曲视频“大众版”的文字，逐屏列出。

"""+AUDIENCE+"""

这个大众版要做到：
{STD}

请只找问题，不要提修改方案，也不用打分。每个问题写清在哪一屏、哪句（引原文）、问题是什么、严重程度（严重/中等/轻微）。整体性的问题也要说，比如整份读下来像什么。

只输出 JSON：{"issues":[{"where":"S03 或 整体","quote":"…","kind":"…","severity":"严重|中等|轻微","why":"…"}],"overall":"三四句话说整体印象"}

【大众版】
{SCREEN}

【它依据的原文】
{SOURCE}
"""


def std():
    t = (ROOT/'大众版标准.md').read_text(encoding='utf-8')
    return t[t.index('## 要达到的目的'):t.index('## 画面')].replace('## 要达到的目的', '').strip()


def open_review(tag):
    def one(job):
        w, j, m = job; p = OUT/f'open_{w}_{tag}_{j}.json'
        if p.exists(): return
        ans = call(f'pub2_open_{w}_{tag}_{j}', OPEN.replace('{STD}', std()).replace('{SCREEN}', screen(w, tag)).replace('{SOURCE}', source(w, local=False)), m, 'gpt3s', 'public2-open')
        wr(p, parse(ans))
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j, m) for w in WORKS for j, m in [('g6', G6), ('g56', G56)]]))
    for w in WORKS:
        for j in ['g6', 'g56']:
            d = rd(OUT/f'open_{w}_{tag}_{j}.json'); c = Counter(i.get('severity') for i in d['issues'])
            print(w, j, dict(c), d.get('overall', '')[:400], flush=True)


# ---------- 盲比 ----------
BLIND = """下面是一首钢琴曲（{NAME}）视频“大众版”文字的两个版本 X 和 Y，顺序随机，逐屏列出。还有它们依据的原文。

"""+AUDIENCE+"""

这个大众版要做到：
{STD}

请逐屏比较，每个判断写一句理由，填 X / Y / 差不多：
1. scan（扫得到）：只扫高亮的词和最先看到的话，哪一版更快知道这一段是什么感受、这个人此刻是怎么回事？
2. string（串得起）：扫的时候，哪一版更能让人感到这些感受和这个人的处境是一回事？
3. exp（讲体验）：哪一版的珠子更是在说听的人心里、身上的感觉，而不是在报告音乐里发生了什么？
4. whole（不像截断、不妨碍理解）：哪一版更像为扫读重新组织过的东西，而不是原文截短？有没有造出原文没有的先后，让人反而看不明白？
5. plain（人话）：哪一版更像平常说话，不像格言、心理分析或文案？
6. lost：一版里有、另一版丢了的核心内容。没有就留空。不要因为字多或字少本身判输赢。

最后整体判断：哪一版更好；如果用 Y 取代 X，算不算实质退步；用 X 取代 Y 呢。

【X】
{X}

【Y】
{Y}

【原文】
{SOURCE}

只输出 JSON：
{"sections":[{"sec":"S01","scan":"X","scan_why":"…","string":"Y","string_why":"…","exp":"差不多","exp_why":"…","whole":"X","whole_why":"…","plain":"Y","plain_why":"…","lost_in_X":[],"lost_in_Y":[]}],"better":"Y","better_why":"…","Y_replacing_X_regress":"否","X_replacing_Y_regress":"是"}
"""
JUDGES = {'g6': G6, 'g56': G56}
if os.environ.get('PUB_JREP') == '1':   # 11-06：同样的线人话分前后差 0.5、盲比差 2 票；加一组重复评委（同模型、不同调用编号），样本翻倍
    JUDGES.update({'g6r': G6, 'g56r': G56})
if os.environ.get('PUB_JREP') == '2':   # 11-07：门槛边上差一两票的分项（同一套线“为什么”在 9:5 和 5:9 之间晃），再加一组重复评委，样本 ×1.5
    JUDGES.update({'g6r': G6, 'g56r': G56, 'g6s': G6, 'g56s': G56})


def vote(w, j, tag, bs, seat):
    p = OUT/f'vote_{w}_{j}_{tag}_vs{bs}_{seat}.json'
    if not p.exists():
        a, b = screen(w, bs), screen(w, tag); x, y = (b, a) if seat == 'newX' else (a, b)
        msg = BLIND.replace('{NAME}', NAME[w]).replace('{STD}', std()).replace('{X}', x).replace('{Y}', y).replace('{SOURCE}', source(w, local=False))
        for k in range(3):
            ans = call(f'pub2_vote_{w}_{j}_{tag}_vs{bs}_{seat}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public2-blind')
            try:
                d = parse(ans); assert d['better'] in ('X', 'Y', '差不多') and d['sections']; wr(p, d); break
            except Exception as e: print('票不合格', w, j, repr(e)[:150], flush=True)
    if not p.exists(): return None
    d = rd(p); new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
    return {'w': w, 'j': j, 'seat': seat, 'new_win': d['better'] == new, 'no_regress': d.get(f'{new}_replacing_{old}_regress') == '否',
            'net': {k: sum((s.get(k) == new)-(s.get(k) == old) for s in d['sections']) for k in DIMS}, 'why': d.get('better_why', '')}


QUICK = [('op60', 'g6', 'newX'), ('op60', 'g56', 'newY'), ('op61', 'g6', 'newY'), ('op61', 'g56', 'newX')] if len(WORKS) == 2 else [(w, j, s) for w in WORKS for j, s in [('g6', 'newX'), ('g56', 'newY'), ('g6', 'newY'), ('g56', 'newX')]]
FAIR = [(w, j, s) for w in WORKS for j in JUDGES for s in ['newX', 'newY']]


def compare(tag, bs, jobs, need):
    with ThreadPoolExecutor(min(4, len(jobs))) as ex: rows = [r for r in ex.map(lambda a: vote(a[0], a[1], tag, bs, a[2]), jobs) if r]
    nets = {k: sum(r['net'][k] for r in rows) for k in DIMS}; wins = sum(r['new_win'] for r in rows); nr = sum(r['no_regress'] for r in rows)
    by = {w: sum(r['new_win'] for r in rows if r['w'] == w) for w in WORKS}
    ok = len(rows) == len(jobs) and wins >= need and all(v >= 0 for v in nets.values()) and all(v >= len(jobs)/4 for v in by.values())
    res = {'tag': tag, 'base': bs, 'votes': len(rows), 'wins': wins, 'no_regress': nr, 'nets': nets, 'by_work': by, 'pass': ok, 'rows': rows}
    wr(OUT/f'cmp_{tag}_vs{bs}_{len(jobs)}.json', res)
    print(tag, 'vs', bs, '过' if ok else '未过', f'{wins}/{len(rows)}', '不退步', nr, nets, '分首', by, flush=True)
    return res


# ---------- 线不能倒退：用内容迭代的盲比提示词，比短版的线和定稿的线 ----------
THREAD_DIMS = ['alone', 'lean', 'plain', 'cover']


def thread_view(w, tag):
    rows = []
    if tag == 'FINAL':
        for s in rd(OUT/f'{w}_src.json')['sections']:
            rows.append(f"### {s['sec']}")
            rows += [f"- {l['text']}" for l in s['lines']]
    else:
        for s in rd(OUT/f'script_{w}_{tag}.json')['sections']:
            rows.append(f"### {s['sec']}")
            rows += [f"- {l['text']}" for g in s['groups'] for l in g.get('lines', [])]
    return chr(10).join(rows)


def thread_vote(w, j, tag, seat):
    p = OUT/f'tvote_{w}_{j}_{tag}_{seat}.json'
    if not p.exists():
        sys.path.insert(0, str(EVO)); os.environ.setdefault('JV', '2')
        import v6fix as V, covjudge
        a, b = thread_view(w, 'FINAL'), thread_view(w, tag); x, y = (b, a) if seat == 'newX' else (a, b)
        msg = V.BLIND2.format(NAME=covjudge.NAME[w], WHAT=V.WHAT2, X=x, Y=y, BEADS=V.beads(w))
        for k in range(3):
            ans = call(f'pub2_tvote_{w}_{j}_{tag}_{seat}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public2-thread')
            try:
                d = parse(ans); assert d['sections']; wr(p, d); break
            except Exception as e: print('票不合格', w, j, repr(e)[:150], flush=True)
    if not p.exists(): return None
    d = rd(p); new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
    return {'w': w, 'j': j, 'seat': seat, 'new_win': d.get('better') == new, 'net': {k: sum((s.get(k) == new)-(s.get(k) == old) for s in d['sections']) for k in THREAD_DIMS}, 'why': d.get('better_why', '')}


def thread_check(tag):
    """短版必然更短，整体谁好不作判定；人话、不啰嗦、单独成立的净胜不能为负，覆盖放宽。"""
    with ThreadPoolExecutor(4) as ex: rows = [r for r in ex.map(lambda a: thread_vote(a[0], a[1], tag, a[2]), QUICK) if r]
    nets = {k: sum(r['net'][k] for r in rows) for k in THREAD_DIMS}
    ok = len(rows) == 4 and all(nets[k] >= 0 for k in ['alone', 'lean', 'plain'])
    wr(OUT/f'thread_{tag}.json', {'tag': tag, 'pass': ok, 'nets': nets, 'rows': rows})
    print(tag, '线对定稿', '不退步' if ok else '退步', nets, flush=True)
    return ok


# ---------- 对照 ----------
KEEP = """这是一首钢琴曲视频的文字。下面有一份已冻结的“不能掉”清单（独立排序得出）和给大众看的短版。逐条对照：短版有没有把这个意思留下来：保留 / 部分 / 丢失。意思留下就算，不要求原词。部分和丢失要说明缺了什么。

再查短版里有没有原文没有的内容：新编的事件、画面、情节，或把珠子里的比喻写成线里真的发生的事。逐条列出，没有就留空。

只输出 JSON：{"items":[{"id":"…","verdict":"保留|部分|丢失","note":"…"}],"added":[{"text":"…","why":"…"}],"summary":"两三句话"}

【不能掉清单】
{MUST}

【原文】
{SOURCE}

【短版】
{SCREEN}
"""


def keep(tag):
    def one(w):
        p = OUT/f'keep_{w}_{tag}.json'
        if not p.exists():
            wr(p, parse(call(f'pub2_keep_{w}_{tag}', KEEP.replace('{MUST}', json.dumps(musts(w), ensure_ascii=False)).replace('{SOURCE}', source(w, local=False)).replace('{SCREEN}', screen(w, tag)), G6, 'gpt3s', 'public2-keep')))
        d = rd(p); c = Counter(x['verdict'] for x in d['items']); print(w, tag, dict(c), '新增', len(d.get('added', [])), d.get('summary', '')[:300], flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c, a = sys.argv[1], sys.argv[2:]
    if c == 'prepare': prepare()
    elif c == 'rank': rank()
    elif c == 'base': base()
    elif c == 'open': open_review(a[0])
    elif c == 'gen':
        with ThreadPoolExecutor(8) as ex: print(list(zip(a, ex.map(gen, a))))
    elif c == 'quick': compare(a[0], a[1], QUICK, 3)
    elif c == 'fair': compare(a[0], a[1], FAIR, 6)
    elif c == 'keep': keep(a[0])
    elif c == 'thread': thread_check(a[0])
