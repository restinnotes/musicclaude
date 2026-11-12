"""11-09 凌晨 回补层（成品修补经验：局部修订 + 回补赢）。
K9e（只删感受里多余的小句、修好接缝）新盲比 7/8 稳定选新，连贯、简洁、人话 8:0，但细腻、为什么输，意思单元覆盖丢了 9–12 个核心单元。
这里把“比较对象里留住了、删减后丢了”的核心单元列出来，让模型从被删的小句里挑出承载它们的，原样放回原位（不改一个字），之后再修一次接缝。
python restore.py SRC CUT0 CUTMEASURED NEW0     SRC 原稿屏幕（K3M2）；CUT0 删减后未修接缝、带 orig 的版本（K9e0）；CUTMEASURED 测过意思单元覆盖的版本（K9e）
"""
import copy, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, WORKS, JUDGES, to_script
import cut

RES = """下面是一首钢琴曲视频屏幕稿的删减记录。为了让观众扫得动，删掉了一些感受小句；但评委发现，有几样核心内容（这一刻最主要、丢了就少一样别处没有的东西）因此丢了。

请从“被删的小句”里，挑出承载这些丢了的核心内容的那几个，放回去。要求：
1. 只挑真正承载那样核心内容的小句；一样内容放回一处就够，同样意思的不要放回两个。
2. 宁可少放，不要多放：放回的越少越好，只要每样丢了的核心内容都回来了。
3. 只能原样放回，不能改字。

只输出 JSON：{"restore":[{"id":"小句编号","for":"对应哪一样丢了的核心内容"}]}

【丢了的核心内容（按段）】
{LOST}

【被删的小句（按段）】
{CUTS}
"""
prompt_lint.lint(RES, 'restore.py')


def lost_units(w, src, measured):
    us = {u['uid']: u for u in rd(S/f'units_{w}.json')}
    def kept(t):
        v = {}
        for j in JUDGES:
            p = S/f'cov3_{w}_{j}_{t}.json'
            if p.exists():
                for x in rd(p)['items']: v.setdefault(x['uid'], []).append(x.get('verdict') == '留住')
        return {u: sum(x) > len(x)/2 for u, x in v.items()}
    a, b = kept(src), kept(measured)
    return [us[u] for u in us if us[u]['tier'] == '核心' and a.get(u) and not b.get(u)]


CITED = """下面是一首钢琴曲视频屏幕稿的删减记录。为了让观众扫得动，删掉了一些感受小句。几位评委把“删减版”和“原版”放在一起看，认为删减版更利落，但也点名说删掉了一些真正有辨识度、或者交代了人物为什么这样的内容。评委的原话附在下面。

请从“被删的小句”里，挑出评委点名的那些内容所在的小句，放回去。要求：
1. 只放回评委确实点到的内容（至少一位评委点名；两位以上点到的优先）；评委说是重复、啰嗦的，不放。
2. 每首最多放回 {MAX} 个小句；一样内容放回一处就够。
3. 只能原样放回，不能改字。

只输出 JSON：{"restore":[{"id":"小句编号","for":"对应评委点名的哪一样"}]}

【评委原话】
{WHY}

【被删的小句（按段）】
{CUTS}
"""
prompt_lint.lint(CITED, 'restore.py CITED')


def cited_text(w, cutname, orig):
    """评委在“删减版 对 原版”盲比里写的理由，座位字母换成〈删减版〉〈原版〉。"""
    import re
    out = []
    for j in JUDGES:
        for seat in 'XY':
            p = S/f'vs3_{w}_{j}_{cutname}__{orig}_{seat}.json'
            if not p.exists(): continue
            other = 'Y' if seat == 'X' else 'X'; t = rd(p).get('why') or ''
            t = re.sub(r'(?<![A-Za-z])'+seat+r'(?![A-Za-z])', '〈删减版〉', re.sub(r'(?<![A-Za-z])'+other+r'(?![A-Za-z])', '〈原版〉', t))
            out.append('- ' + t)
    return chr(10).join(out)


def one(a):
    w, src, cut0, measured, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{cut0}.json')); table = {}; bysec = {}
    if os.environ.get('RESTORE_V2'):
        # 11-09：删减时整块删光的感受会从数据里消失，回补看不到它（评委点名最多的整块心里话因此永远回不来）。
        # V2 以原稿屏幕（src）的结构为底：每一块找删减版里对应的现状（按 orig 或原文对上），整块删掉的现状记为空，也能回补。
        base = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); cutsc = {x['sec']: x for x in scr['sections']}
        for s in base['sections']:
            now = {}
            for x in cutsc[s['sec']]['rows']:
                for it in ([x] if x['kind'] == 'line' else x['items']): now.setdefault(it.get('orig') or it['text'], it['text'])
            for x in s['rows']:
                for it in ([x] if x['kind'] == 'line' else x['items']):
                    o = it['text']; it['orig'] = o; it['text'] = now.get(o, '' if x['kind'] == 'feel' else o)
        scr = base
    for s in scr['sections']:
        for k, x in enumerate(s['rows'], 1):
            for n, it in enumerate([x] if x['kind'] == 'line' else x['items'], 1):
                if not it.get('orig') or it['orig'] == it['text']: continue
                cs = cut.clauses(it['orig'])
                for m, c in enumerate(cs, 1):
                    core_c = c.strip().rstrip('，。；：,;')
                    if core_c and core_c not in it['text']:
                        cid = f"{s['sec']}-r{k}-i{n}-c{m}"; table[cid] = (it, m); bysec.setdefault(s['sec'], []).append(f"  <{cid}>{c}")
    if os.environ.get('RESTORE_CITED'):   # 11-09：按评委在盲比里点名的丢失内容回补（K9f 按覆盖清单回补，幻想只放回 5 句、几乎没用）
        NL = chr(10)
        cuts = NL.join(f"### {k}{NL}" + NL.join(v) for k, v in sorted(bysec.items()))
        msg = CITED.replace('{MAX}', os.environ.get('RESTORE_MAX', '8')).replace('{WHY}', chr(10).join(cited_text(w, m, src) for m in (os.environ.get('RESTORE_FROM') or measured).split(','))).replace('{CUTS}', cuts)
        lost = []
    else:
        lost = lost_units(w, src, measured)
    ls = {}
    for u in lost: ls.setdefault(u['sec'], []).append(f"  - {u['what']}")
    if not os.environ.get('RESTORE_CITED'): msg = RES.replace('{LOST}', '\n'.join(f"### {k}\n" + '\n'.join(v) for k, v in sorted(ls.items()))).replace('{CUTS}', '\n'.join(f"### {k}\n" + '\n'.join(v) for k, v in sorted(bysec.items())))
    for t in range(3):
        try:
            r = parse(call(f'pub24RES{"C" if os.environ.get("RESTORE_CITED") else ""}{"2" if os.environ.get("RESTORE_V2") else ""}_{w}_{new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-restore')); break
        except Exception as ex: print('不合格', w, new, repr(ex)[:150], flush=True); r = {}
    back = {}
    for x in r.get('restore') or []:
        if x.get('id') in table: it, m = table[x['id']]; back.setdefault(id(it), (it, set()))[1].add(m)
    n = 0
    for it, ms in back.values():
        cs = cut.clauses(it['orig']); txt = it['text']
        keep = [c for m, c in enumerate(cs, 1) if m in ms or c.strip().rstrip('，。；：,;') in txt]
        nt = ''.join(keep).strip().lstrip('，。；：,;')
        import re
        it['text'] = re.sub('[，；：,;]$', '', nt); n += len(ms)
    for s in scr['sections']:
        for x in s['rows']:
            if x['kind'] == 'feel': x['items'] = [i for i in x['items'] if i['text'].strip()]
        s['rows'] = [x for x in s['rows'] if x['kind'] == 'line' or x['items']]
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '丢了的核心单元', len(lost), '；被删小句', len(table), '；放回', n, flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, *sys.argv[1:5]) for w in WORKS])), flush=True)
