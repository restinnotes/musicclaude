"""11-09 晚 碎块形态的写稿（用户 11-09 晚：“一句话里有大字是不是就不对劲啊……一句话里不应该有的字大有的字小……最多粗体 斜体 颜色”；
“拆成碎块这个 我感觉我提了好多遍了”；“扫的动的意思是 光看那些关键的东西 就可以给他把整个在表达什么在脑海里自己拼起来”）。
格式：每屏若干大块（每块一种字号，按顺序连起来就是骨架）+ 挂在大块后的小块（只补骨架拼不出又必须有的）+ 旁注。块内强调只变色（accent）。
写手输出：{"sections":[{"sec":"S01","big":[{"text":"…","accent":"块内要变色的字，可空","emotion":"…","from":["…"],"at":0}],
  "small":[{"text":"…","after":0,"from":["…"],"bars":"","at":0}],"notes":[{"text":"…","from":["…"],"pt":"要点编号或空","bars":"…"}]}]}
转成渲染器格式：每个大块一行 kind=line（keys=[accent]，整屏 uniform=true，只变色不变大），挂在它后面的小块一行 kind=feel。
机械检查（不过就整份交回重写，最多 3 次）：大块 ≤14 字且块里没有逗号、分号、句号（句末问号、感叹号可以）；小块 ≤18 字、没有分号；
每屏大块 ≤5、小块 ≤6；正文不写小节号。
python r3/fragwrite.py NEW 提示词文件 [g6|g56]     （原料用 PUB_SRC）
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint, pub16
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, to_script
import blend
sys.stdout.reconfigure(encoding='utf-8')
EMO = blend.EMO
BAR = re.compile(r'\d+\s*[–\-—~～]?\s*\d*\s*小节|第\s*\d+')


def convert(w, r):
    src = rd(R2/f'{w}_src.json'); secs = [s['sec'] for s in src['sections']]
    assert [x['sec'] for x in r['sections']] == secs, '段不对'
    ids = {l['id'] for s in src['sections'] for l in s['lines']} | {b['id'] for s in src['sections'] for b in s['beads']}
    out = {'uniform': True, 'sections': []}; bad = []; miss = []
    rule = os.environ.get('PUB_FRAG_RULE', '')   # 11-10 K26：nat = 自然句块（GPT-6 方案 1），one = 一屏一句（GPT-6 方案 2）；空 = 旧碎块规则
    BMAX, BN, SMAX, SN = {'nat': (28, 3, 28, 5), 'one': (36, 2, 28, 5), 'chain': (30, 5, 30, 6), 'nat2': (28, 4, 28, 8), 'chain2': (30, 6, 30, 10), 'chain3': (30, 5, 30, 6), 'nat3': (30, 3, 30, 5)}.get(rule, (14, 5, 18, 6))   # nat2、chain2 = 11-10 I12 第 1 次交回后放宽的容量   # chain = GPT-5.6 交回后的“短块关系链”
    if rule in ('std8', 'std9'):   # 11-10 午 标准第 8 条改后：看得过来只算大块。参数由顾问方案给：PUB_FRAG_P=大块字数,大块个数,小块字数,小块个数,大块每秒字数,旁注条数
        P = [float(x) for x in os.environ.get('PUB_FRAG_P', '30,5,30,8,3,5').split(',')]; BMAX, BN, SMAX, SN = int(P[0]), int(P[1]), int(P[2]), int(P[3])
    win = pub16.windows(w)
    for s, s0 in zip(r['sections'], src['sections']):
        big = [b for b in s.get('big') or [] if (b.get('text') or '').strip()]; small = [x for x in s.get('small') or [] if (x.get('text') or '').strip()]
        assert big, f"{s['sec']} 没有大块"
        if len(big) > BN: bad.append(f"{s['sec']} 大块 {len(big)} 个，最多 {BN} 个")
        if len(small) > SN: bad.append(f"{s['sec']} 小块 {len(small)} 个，最多 {SN} 个")
        if rule in ('std8', 'std9'):
            secs = win[s['sec']][1] - win[s['sec']][0]; nb = sum(len(b['text'].strip()) for b in big)
            if nb > secs*P[4] + 8: bad.append(f"{s['sec']} 大块共 {nb} 字，这屏只停 {secs:.0f} 秒，只看大块也看不过来（大块最多约 {int(secs*P[4])} 字）；把次要的挪进小块")
            ns = [n for n in s.get('notes') or [] if (n.get('text') or '').strip()]
            if len(ns) > P[5]: bad.append(f"{s['sec']} 旁注 {len(ns)} 条，最多 {int(P[5])} 条")
        elif rule:
            secs = win[s['sec']][1] - win[s['sec']][0]; nch = sum(len(b['text'].strip()) for b in big) + sum(len(x['text'].strip()) for x in small)
            tmax = {'chain': (4 if secs <= 20 else 5 if secs <= 30 else 6), 'nat2': 10, 'chain2': (8 if secs <= 20 else 10 if secs <= 30 else 12),
                    'chain3': (6 if secs <= 20 else 8 if secs <= 30 else 10), 'nat3': 7}.get(rule, 6)
            rate = {'chain': 2.5, 'nat2': 4.0, 'chain2': 4.0, 'chain3': 3.5, 'nat3': 4.0}.get(rule, 3)
            if rule in ('chain3', 'nat3'):   # 11-10 第 2 次交回：旁注也算进阅读负担
                ns = [n for n in s.get('notes') or [] if (n.get('text') or '').strip()]; nn = sum(len(n['text'].strip()) for n in ns)
                NMAX, NL_ = {'chain3': (4, 30), 'nat3': (3, 24)}[rule]
                if len(ns) > NMAX: bad.append(f"{s['sec']} 旁注 {len(ns)} 条，最多 {NMAX} 条")
                for n in ns:
                    if len(n['text'].strip()) > NL_: bad.append(f"{s['sec']} 旁注超过 {NL_} 字：{n['text'].strip()}")
                nr = {'chain3': 1.0, 'nat3': 0.8}[rule]
                if nn > secs*nr + 6: bad.append(f"{s['sec']} 旁注 {nn} 字，这屏停 {secs:.0f} 秒，最多约 {int(secs*nr)} 字（每秒 {nr} 字）")
                if nch + nn > secs*4.5 + 10: bad.append(f"{s['sec']} 主区加旁注 {nch + nn} 字，这屏停 {secs:.0f} 秒，合计最多约 {int(secs*4.5)} 字（每秒 4.5 字）")
            if len(big) + len(small) > tmax: bad.append(f"{s['sec']} 主区大块小块合计 {len(big) + len(small)} 块，这屏最多 {tmax} 块")
            if nch > secs*rate + 10: bad.append(f"{s['sec']} 主区 {nch} 字，这屏只停 {secs:.0f} 秒，最多约 {int(secs*rate)} 字（每秒 {rate} 字），要合并或删去重复的")
        rows = []
        for i, b in enumerate(big):
            t = b['text'].strip().rstrip('。')
            if len(t) > BMAX: bad.append(f"{s['sec']} 大块超过 {BMAX} 字：{t}")
            if not rule and re.search('[，,；;。]', t): bad.append(f"{s['sec']} 大块里有逗号或分号：{t}")
            if rule in ('nat', 'one', 'nat2', 'nat3', 'std8') and (len(re.findall('[，,]', t)) > 1 or re.search('[；;。]', t)): bad.append(f"{s['sec']} 大块最多一个逗号、不用分号句号：{t}")
            if rule == 'std9' and (len(re.findall('[，,]', t)) > 2 or re.search('[；;。]', t)): bad.append(f"{s['sec']} 大块最多两个逗号、不用分号句号：{t}")   # 11-10 晚：一个逗号的限制逼写手把线的一句话劈成两条各自成块的结论（用户判“不说人话、极其跳跃”）
            if BAR.search(t): bad.append(f"{s['sec']} 写了小节号：{t}")
            fr0 = b.get('from') or []
            if fr0 and all('-B' in f for f in fr0) and '他' in t:   # 11-10：珠子（听者的体验）进大块时被写成“他”的经历，K24 各版反复出现的走样
                bad.append(f"{s['sec']} 这个大块只来自珠子（听的人的体验），却用“他”写成了他的经历；要写成“像……”或不带主语，或者和线的内容合在一起并保住“像”：{t}")
            row = {'kind': 'line', 'text': t, 'keys': [b['accent']] if b.get('accent') and b['accent'] in t else [], 'emotion': b.get('emotion') if b.get('emotion') in EMO else '悬着', 'from': [f for f in b.get('from') or [] if f in ids]}
            if isinstance(b.get('at'), (int, float)) and b['at'] > 0: row['at'] = float(b['at'])
            rows.append(row)
            its = []
            for x in small:
                if int(x.get('after', 0) or 0) != i: continue
                t2 = x['text'].strip().rstrip('。')
                if len(t2) > SMAX: bad.append(f"{s['sec']} 小块超过 {SMAX} 字：{t2}")
                if rule in ('nat', 'one', 'nat2') and len(re.findall('[，,]', t2)) > 1 or rule in ('nat3', 'std8', 'std9') and len(re.findall('[，,]', t2)) > 2: bad.append(f"{s['sec']} 小块最多一个逗号：{t2}")
                if re.search('[；;]', t2): bad.append(f"{s['sec']} 小块里有分号：{t2}")
                if not rule and len(t2) > 16 and not re.search('[，、？！,?!：]', t2): bad.append(f"{s['sec']} 小块超过 16 字却没有任何停顿，读起来连成一串，要用逗号断开：{t2}")   # 11-09 晚：K24b/K24b2 写手把小块的逗号全删了
                if BAR.search(t2): bad.append(f"{s['sec']} 写了小节号：{t2}")
                fr = [f for f in x.get('from') or [] if f in ids]
                it = {'text': t2, 'bead': next((f for f in fr if '-B' in f), fr[0] if fr else ''), 'from': fr, 'bars': x.get('bars') or ''}
                if isinstance(x.get('at'), (int, float)) and x['at'] > 0: it['at'] = float(x['at'])
                its.append(it)
            if its: rows.append({'kind': 'feel', 'items': its})
        pts = {q['id'] for b in s0['beads'] for q in b['points'] if q.get('local')}
        notes = []
        for n in s.get('notes') or []:
            t3 = (n.get('text') or '').strip()
            if not t3: continue
            if len(t3) > 30: bad.append(f"{s['sec']} 旁注超长：{t3}")
            if BAR.search(t3): bad.append(f"{s['sec']} 旁注写了小节号：{t3}")
            if n.get('pt') in pts: notes.append({'text': t3, 'pt': n['pt'], 'bars': '', 'from': [f for f in n.get('from') or [] if f in ids]})
            elif str(n.get('bars') or '').strip(): notes.append({'text': t3, 'bars': str(n['bars']), 'from': [f for f in n.get('from') or [] if f in ids]})
        used = {f for x in rows for f in x.get('from') or []} | {f for x in rows if x['kind'] == 'feel' for i in x['items'] for f in i['from']} | {f for n in notes for f in n['from']}
        miss += [b['id'] for b in s0['beads'] if b['id'] not in used]
        out['sections'].append({'sec': s['sec'], 'rows': rows, **({'notes': notes} if notes else {})})
    return out, bad, miss


def base_json(w, tag):
    """11-10 午：把一版屏幕稿还原成写手的输出格式（大块、挂在后面的小块、旁注），给“只改措辞”“在某版上改”的提示词用（{BASE}）。"""
    out = []
    for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
        big = []; small = []
        for x in s['rows']:
            if x['kind'] == 'line':
                big.append({'text': x['text'], 'accent': (x.get('keys') or [''])[0], 'emotion': x.get('emotion', ''), 'from': x.get('from') or [], **({'at': x['at']} if 'at' in x else {})})
            else:
                for i in x['items']: small.append({'text': i['text'], 'after': max(0, len(big) - 1), 'from': i.get('from') or [], 'bars': i.get('bars') or '', **({'at': i['at']} if 'at' in i else {})})
        out.append({'sec': s['sec'], 'big': big, 'small': small, 'notes': [{'text': n['text'], 'from': n.get('from') or [], 'pt': n.get('pt') or '', 'bars': n.get('bars') or ''} for n in s.get('notes') or []]})
    return json.dumps({'sections': out}, ensure_ascii=False)


def ask(rid, msg, who):
    if who == 'argon':   # 改语言用 Argon（模型分工；用户允许约 100 次，省着用）
        sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); import evo
        return evo.call_argon_direct(rid, msg, meta={'stage': 'public24-frag-argon'})
    return call(rid, msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-frag')


def one(a):
    w, new, pf, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): return True
    tpl = (S/pf).read_text(encoding='utf-8')
    prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|CURRENT|BASE|PLAN|STD)\}', '', tpl), pf)
    if '{STD}' in tpl: tpl = tpl.replace('{STD}', Path('D:/musicclaude/_video_public_20261104/大众版标准.md').read_text(encoding='utf-8').split('## 画面')[0])
    if '{BASE}' in tpl: tpl = tpl.replace('{BASE}', base_json(w, os.environ['PUB_FRAG_BASE']))
    if '{PLAN}' in tpl:   # 两步写稿：第一步（PUB_FRAG_PLAN 指的提示词，可用 PUB_FRAG_PLANWHO 指定谁写）只分配内容，原样填进第二步
        pp = S/f'plan_{w}_{new}.txt'
        if not pp.exists():
            t1 = (S/os.environ['PUB_FRAG_PLAN']).read_text(encoding='utf-8')
            prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|BASE|STD)\}', '', t1), os.environ['PUB_FRAG_PLAN'])
            if '{BASE}' in t1: t1 = t1.replace('{BASE}', base_json(w, os.environ['PUB_FRAG_BASE']))
            t1 = t1.replace('{STD}', Path('D:/musicclaude/_video_public_20261104/大众版标准.md').read_text(encoding='utf-8').split('## 画面')[0])
            t1 = t1.replace('{DAGSTD}', blend.DAGSTD).replace('{BUDGET}', blend.budget(w)).replace('{FINAL}', blend.lines_map(w)).replace('{BEADS}', blend.beads_text(w))
            pl = ask(f'fragplan_{w}_{new}', t1, os.environ.get('PUB_FRAG_PLANWHO', 'g6'))
            assert pl and len(pl) > 500, '第一步没有产出'
            pp.write_text(pl, encoding='utf-8')
        tpl = tpl.replace('{PLAN}', pp.read_text(encoding='utf-8'))
    if '{CURRENT}' in tpl: tpl = tpl.replace('{CURRENT}', blend.current_json(w, os.environ.get('PUB_BL_CUR', 'g68K11g')))
    msg = tpl.replace('{DAGSTD}', blend.DAGSTD).replace('{BUDGET}', blend.budget(w)).replace('{FINAL}', blend.lines_map(w)).replace('{BEADS}', blend.beads_text(w))
    fb = ''
    for k in range(4):
        ans = ask(os.environ.get('PUB_BL_PFX', 'frag')+f'_{w}_{new}'+('' if not k else f'_r{k}'), msg + fb, who)
        try:
            r = parse(ans); scr, bad, miss = convert(w, r)
            (S/f'frag_{w}_{new}_try{k}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
            if bad and k < 3:
                print(w, new, f'第 {k+1} 次机械检查没过 {len(bad)} 处，交回重写', flush=True)
                fb = '\n\n【你上一次的输出没过机械检查，下面这些地方要改；其余照原要求，整份重新输出】\n' + '\n'.join(bad[:40]); continue
            wr(p, scr); to_script(w, new, scr)
            B = [x['text'] for s in scr['sections'] for x in s['rows'] if x['kind'] == 'line']; F = [i['text'] for s in scr['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
            N = [n['text'] for s in scr['sections'] for n in s.get('notes') or []]
            print(w, new, f'大块 {len(B)} 个 {sum(map(len, B))} 字；小块 {len(F)} 个 {sum(map(len, F))} 字；旁注 {len(N)} 条 {sum(map(len, N))} 字；剩余机械问题 {len(bad)}；没用到的珠子 {miss}', flush=True)
            return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    new, pf = sys.argv[1], sys.argv[2]; who = sys.argv[3] if len(sys.argv) > 3 else 'g6'
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, new, pf, who) for w in WORKS])), flush=True)
