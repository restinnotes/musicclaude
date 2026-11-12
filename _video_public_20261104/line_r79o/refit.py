"""11-09 下午 K15：写稿后逐屏查字数上限（blend.cap，按停留秒数）。超过上限 1.1 倍的屏，交回写手按“挑内容”重写这一屏：
给它这一屏的定稿线和珠子、它自己写的这一屏、前后两屏，要求在上限内重新挑（整条舍弃次要内容，不压缩改写留下的）。
和 dense.py 的区别：dense 只在已有文字上删和并；这里可以回到定稿重新挑，避免“压成电报句”。
python refit.py SRC NEW g6|g56
"""
import copy, json, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, blend
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, to_script

RF = """你在写一首钢琴曲大众版“边听边看”视频的屏幕稿。下半屏是音乐动画，上半屏是文字；普通观众边听边扫。下面这一屏你写超了：停留 {SEC} 秒，最多 {CAP} 字，你写了 {NOW} 字。请重写这一屏，不超过 {CAP} 字。

怎么改：
1. 回到这一屏的定稿线和珠子重新挑：先保人物这一刻的处境、为什么、和上一屏比什么变了；再保这一段最核心的那种感受里最具体的说法、人物的心里话和疑问；其余珠子挑一两条最独特的，整条照用原来的说法。
2. 装不下的整条舍弃，不要用压缩改写来减字：不把具体画面缩成四字词组，不把几层意思挤进一个长句，不写省掉主语和连接词的电报句。
3. 意思不走样：疑问仍是疑问，担心不写成已发生；珠子里的比喻、想象和可能的听法保留原来的框架，不写成他真的经历的事；不加定稿没有的内容；不写小节号。
4. 和前后两屏接得上，不重复前一屏已经说过的。
5. 形态照旧：连贯（一句话，大字，1–2 个关键词放大）或散落（几块短语，每块 3–12 字）；只属于某几小节的珠子写成散落并填 bars。

只输出 JSON：{"rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的字"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["编号"]},{"form":"散落","items":[{"text":"…","from":["编号"],"bars":""}]}]}

【前一屏（你写的）】
{PREV}

【这一屏（你写的，超了）】
{CUR}

【后一屏（你写的）】
{NEXT}

【这一屏的定稿线】
{LINES}

【这一屏的定稿珠子】
{BEADS}
"""
prompt_lint.lint(RF, 'refit.py')
TOL = float(os.environ.get('REFIT_TOL', '1.1'))


def L(s): return sum(len(x['text']) if x['kind'] == 'line' else sum(len(i['text']) for i in x['items']) for x in s['rows'])


def show(s):
    if not s: return '（无）'
    out = []
    for x in s['rows']:
        if x['kind'] == 'line': out.append('连贯：' + x['text'])
        else: out.append('散落：' + ' / '.join(i['text'] + (f"（{i['bars']}）" if i.get('bars') else '') for i in x['items']))
    return chr(10).join(out)


def one(a):
    w, src, new, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); cap = blend.cap(w); s0 = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}
    import pub16; win = pub16.windows(w); secs = scr['sections']; log = []
    orig = copy.deepcopy(secs)   # 11-09：用户要求按提速办法跑，超上限的屏并行重写；前后屏都取写手原稿

    def fix(k):
        s = secs[k]; now = L(s); c = cap[s['sec']]
        if now <= c*TOL: return None
        src0 = s0[s['sec']]
        msg = (RF.replace('{SEC}', str(round(win[s['sec']][1]-win[s['sec']][0]))).replace('{CAP}', str(c)).replace('{NOW}', str(now))
               .replace('{PREV}', show(orig[k-1] if k else None)).replace('{CUR}', show(orig[k])).replace('{NEXT}', show(orig[k+1] if k+1 < len(orig) else None))
               .replace('{LINES}', chr(10).join(f"{l['id']}：{l['text']}" for l in src0['lines']))
               .replace('{BEADS}', chr(10).join(f"[{b['id']}]{'（只属于小节 '+b['where']+'）' if any(q['local'] for q in b['points']) else ''}{b['text']}" for b in src0['beads'])))
        for t in range(3):
            try:
                r = parse(call(f'refit_{w}_{s["sec"]}_{new}' + ('' if not t else f'_r{t}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-refit'))
                rows = conv_rows(w, {'sections': [{'sec': s['sec'], 'rows': r['rows']}]})
                if L({'rows': rows}) > c*TOL: raise ValueError(f"仍然超 {L({'rows': rows})}/{c}")
                s['rows'] = rows; return f"{s['sec']} {now}→{L(s)}/{c}"
            except Exception as ex: print('不合格', w, s['sec'], repr(ex)[:150], flush=True)
        return f"{s['sec']} 没改成（{now}/{c}）"
    with ThreadPoolExecutor(8) as ex: log = [x for x in ex.map(fix, range(len(secs))) if x]
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '超上限的屏：', '；'.join(log) or '无', '；全曲', sum(L(s) for s in secs), '/', sum(cap.values()), flush=True); return True


def conv_rows(w, one_sec):
    """借 blend.convert 的行转换，只转一屏（convert 要求全部段，这里临时补空段后取出）。"""
    src = rd(R2/f'{w}_src.json'); sec = one_sec['sections'][0]['sec']
    full = {'sections': [{'sec': x['sec'], 'rows': one_sec['sections'][0]['rows'] if x['sec'] == sec else [{'form': '连贯', 'text': '占位'}]} for x in src['sections']]}
    out, _ = blend.convert(w, full)
    return next(x for x in out['sections'] if x['sec'] == sec)['rows']


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
