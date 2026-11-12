"""11-08 晚 只删不改的成品修补层（迭代准则“成品修补回路”：只在比较对象上局部改）。
这一晚的证据：
- 只删整句多余的话、留下的字一个不动，能赢（K8c 船歌新盲比 4/4 稳定选新、七项不输）；
- 压缩改写会丢质感（K8h、K8j 三种覆盖都没丢内容，细腻却 0:8）；删掉心里话和“却”字转折会丢“为什么”（K8c 幻想、K8g 幻想）；把连着的心理过程拆开会丢连贯（K8g 幻想 S03）。
- 开放评审剩下的严重/中等问题，多数能靠删整句解决：跨屏重复交代的话、相邻两屏重复的感受清单、先讲乐评的半句、扩成故乡家园的半句、“也有人听见”这种跳出人物的说法、“到时出现”里次要的半句、短停留屏里话太长。
做法：屏幕上每一行（话和感受）按标点切成小句并编号，模型只能回答删哪几个编号，不能改写任何字。机械保护：放大的关键词所在小句、心里话短块（20 字以内的感受块）、“却/可/但”带出的转折小句、引号里的念头，一律不许删；一行话至少留一个小句。
python cut.py SRC NEW
"""
import copy, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, rd, wr, call, parse, G6, WORKS, JUDGES, to_script
import pub16

CUT = """下面是一首钢琴曲大众版“边听边看”视频的屏幕稿。普通观众边听边扫，每段屏幕只停留写明的秒数。“话”是大字，讲这个人的事；“感受”是小字。每一行已经按标点切成小句，每个小句前有编号。标“不能删”的小句不许删。

评审读了这份屏幕稿，挑出了下面这些问题。请只用“删掉整个小句”的办法解决它们：你只能回答删哪些编号，不能改写、不能加字。
删什么：
1. 同一层意思在前面的屏已经交代过、这里只是再说一遍的小句（话和感受都算）；同一屏里换个比喻把同一种感受再说一遍的小句。
2. 先讲音乐结构、声部、技法、乐评，却没有帮观众对上声音、也没有带出感受的小句。
3. 把人物的具体处境扩成宽泛主题（例如故乡、家园、集体、人生道理）的小句；跳出人物、改成“也有人听见”“你”这类旁观口吻的小句。
4. 短停留的屏、标“到时出现”的感受里，次要的、解释性的小句。
不删什么：
- 每一样不同的具体东西（画面、身体感觉、音乐变化带出的感受、原因、转折、心里话）都至少要留一处；删了会让人看不懂人物为什么这样、接下来为什么那样的，不删。
- 删完后这一行剩下的小句要能连成通顺的话（不要删掉主语、只剩半句）；拿不准就不删。
- 宁可少删，不要多删。

只输出 JSON：{"cut":[{"id":"S05-r2-i1-c3","why":"对应哪条问题"}]}

【评审挑出的问题】
{ISSUES}

【屏幕稿】
{SCREEN}
"""
prompt_lint.lint(CUT, 'cut.py')
SPL = re.compile(r'([^，。；：？！,;?!]+[，。；：？！,;?!]?)')


def clauses(t):
    return [c for c in SPL.findall(t) if c.strip()]


def protected(c, row, item, keys):
    LONG = int(os.environ.get('CUT_LONG', '0'))   # 11-09 K12：只在超过 LONG 字的长感受块里删（K11f 绝对验收反复报“小字感受是多层长句、扫不完”）
    if LONG and (row['kind'] == 'line' or len(item['text']) <= LONG): return '短块或话'
    if row['kind'] == 'line' and any(k in c for k in keys): return '放大词'
    if row['kind'] == 'feel' and len(item['text']) <= 20: return '心里话短块'
    s = c.strip()
    if '却' in s or s.startswith(('可', '但')): return '转折'
    if re.search('[“"]', s): return '心里话'
    return ''


def layout(w, scr):
    win = pub16.windows(w); out = []; table = {}
    for s in scr['sections']:
        out.append(f"\n### {s['sec']}（停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for k, x in enumerate(s['rows'], 1):
            items = [x] if x['kind'] == 'line' else x['items']
            for n, it in enumerate(items, 1):
                parts = []
                cs = clauses(it['text'])
                for m, c in enumerate(cs, 1):
                    cid = f"{s['sec']}-r{k}-i{n}-c{m}"; pr = protected(c, x, it, x.get('keys') or [])
                    # 11-08 晚 K9：删了“却”字转折前面那一句，剩下没头的“独处时心头却泛酸”；转折的前一句也保护
                    if not pr and m < len(cs) and ('却' in cs[m] or cs[m].strip().startswith(('可', '但', '也', '才', '就', '还'))) and os.environ.get('CUT_V2') == '1': pr = '转折前句'
                    table[cid] = (x, it, m, pr); parts.append(f"<{cid}{'·不能删' if pr else ''}>{c}")
                lab = '话' if x['kind'] == 'line' else ('感受（到时出现）' if it.get('pt') or it.get('bars') else '感受')
                out.append(f"{lab}：" + ''.join(parts))
    return '\n'.join(out), table


def issues_text(w, src):
    out = []
    if os.environ.get('CUT_ISSUES') == 'openA2':   # 11-09：用绝对尺度验收报的问题（中等和轻微）
        import glob
        for f in sorted(glob.glob(str(S/f'openA2_{w}_*_{src}_run*.json'))):
            for x in rd(f).get('issues') or []:
                if x.get('severity') in ('中等', '轻微'): out.append(f"- （{x.get('severity')}）{x.get('sec')}「{(x.get('quote') or '')[:60]}」：{x.get('why')}")
        return chr(10).join(out)
    for j in ('g6', 'g56'):
        p = S/f'open_{w}_{j}_{src}.json'
        if not p.exists(): continue
        r = rd(p)
        for c in r.get('cumulative') or []:
            if c.get('severity') in ('严重', '中等'): out.append(f"- 跨段（{c.get('severity')}）{c.get('phenomenon')}")
        for x in r.get('issues') or []: out.append(f"- {x.get('sec')}「{(x.get('quote') or '')[:60]}」：{x.get('why')}")
    return '\n'.join(out)


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json'))
    text, table = layout(w, scr)
    msg = CUT.replace('{ISSUES}', issues_text(w, src)).replace('{SCREEN}', text)
    for t in range(3):
        ans = call(f'pub24CUT_{w}_{os.environ.get("CUT_RIDTAG") or new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-cut')
        try:
            r = parse(ans); want = [x.get('id') for x in r.get('cut') or []]
            drop = {}; refused = 0
            for cid in want:
                if cid not in table: continue
                x, it, m, pr = table[cid]
                if pr: refused += 1; continue
                if os.environ.get('CUT_FEELONLY') == '1' and x['kind'] == 'line': continue   # 11-08 晚 K9d：删话里的小句，为什么 0:8、覆盖垮掉；只删感受
                drop.setdefault(id(it), set()).add(m)
            n = 0
            for s in scr['sections']:
                for x in s['rows']:
                    items = [x] if x['kind'] == 'line' else x['items']
                    for it in items:
                        ms = drop.get(id(it))
                        if not ms: continue
                        cs = clauses(it['text']); keep = [c for m, c in enumerate(cs, 1) if m not in ms]
                        if x['kind'] == 'line' and not keep: continue   # 一行话至少留一个小句
                        nt = ''.join(keep).strip().lstrip('，。；：,;')
                        nt = re.sub('[，；：,;]$', '', nt) + ('。' if x['kind'] == 'line' and nt and not re.search('[。？！?!]$', nt) else '')
                        it.setdefault('orig', it['text']); it['text'] = nt; n += len(cs) - len(keep)
                    if x['kind'] == 'feel': x['items'] = [i for i in x['items'] if i['text'].strip()]
                s['rows'] = [x for x in s['rows'] if x['kind'] == 'line' or x['items']]
            wr(p, scr); to_script(w, new, scr)
            L = lambda sc: sum(len(x['text']) if x['kind'] == 'line' else sum(len(i['text']) for i in x['items']) for s in sc['sections'] for x in s['rows'])
            print(w, new, '删了', n, '个小句；受保护没删', refused, f'；整屏字数 {L(rd(S/f"screen_{w}_{src}.json"))} → {L(scr)}', '；小节号', gate2.barnums(w, new), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


SEAM = """下面是一首钢琴曲视频屏幕上的几行字。每行给了“原文”和“删减后”：删减是为了让观众扫得动，删掉了一些重复或次要的小句，但有的地方删出了断口——前后逻辑接不上、主语没了、转折没了前提、半句悬空。
请逐行检查“删减后”：
1. 读得通、意思和原文一致的，原样照抄。
2. 有断口的，只用两种办法修：把原文里被删的那个小句原样放回来；或者加最多四个字把前后接上。不许改写别的字，不许加原文没有的意思。

只输出 JSON：{"items":[{"id":"编号","text":"修好的这一行"}]}

{ITEMS}
"""
prompt_lint.lint(SEAM, 'cut.py SEAM')


def seam(a):
    """python cut.py seam SRC CUT NEW：对删过的行修断口"""
    import difflib
    w, src, cutt, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    o = rd(S/f'screen_{w}_{src}.json'); scr = copy.deepcopy(rd(S/f'screen_{w}_{cutt}.json')); todo = {}
    for sc in scr['sections']:   # 11-08 晚：删减时每行记下原文（orig），一一对应，不再按相似度猜
        cl = [it for x in sc['rows'] for it in ([x] if x['kind'] == 'line' else x['items'])]
        for k, it in enumerate(cl):
            if it.get('orig') and it['orig'] != it['text']: todo[f"{sc['sec']}-{k}"] = ({'text': it['orig']}, it)
    NL = chr(10)
    txt = NL.join(f"[{bid}]{NL}  原文：{a_['text']}{NL}  删减后：{b_['text']}" for bid, (a_, b_) in todo.items())
    r = {}
    for t in range(3):
        try: r = {x['id']: (x.get('text') or '').strip() for x in parse(call(f'pub24SEAM_{w}_{new}' + ('' if not t else f'_r{t}'), SEAM.replace('{ITEMS}', txt), G6, 'gpt3s', 'public24-seam'))['items']}; break
        except Exception as ex: print('不合格', w, new, repr(ex)[:150], flush=True)
    fixed = bad = 0
    for bid, (a_, b_) in todo.items():
        nt = r.get(bid)
        if not nt or nt == b_['text']: continue
        extra = sum(j2 - j1 for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a_['text'], nt).get_opcodes() if tag in ('insert', 'replace'))
        if extra > 4 or len(nt) > len(a_['text']): bad += 1; continue
        b_['text'] = nt; fixed += 1
    for sc in scr['sections']:
        for x in sc['rows']:
            for it in ([x] if x['kind'] == 'line' else x['items']): it.pop('orig', None)
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '删过的行', len(todo), '；修了断口', fixed, '；修法不合规没采用', bad, flush=True); return True


if __name__ == '__main__' and sys.argv[1] == 'seam':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(seam, [(w, sys.argv[2], sys.argv[3], sys.argv[4]) for w in WORKS])), flush=True)
    sys.exit()

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
