"""线重写：一组一句，同时做到压缩、独立、和旁边的词是一回事、同段几句不一样。并直接测这四项。全走 gpt3。
python pub18.py write 线来源TAG 新TAG        线重写，词不动
python pub18.py four TAG                     直接测四项
python pub18.py explicit 来源TAG 新TAG       只留词本身明确指向某个声音的音符标记
"""
import json, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3, pub16
from pub2 import G6, JUDGES, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲“边听边看”视频的屏幕文字。每段几组，每组左边一句话（线：一个人经历的事），右边几块短词（听的人当下的感受）。观众边听音乐边扫屏幕。

现在左边的话有三个毛病：写得太满，扫不完；同一段几句都一个样；和右边的词对不上。词不动，请重写左边的话。一组一句，同时做到：

1. 压缩：一眼读完。主组可以长一点，次组更短。下面给了每段的秒数，秒数少的更短。不用分号把几件事连起来。
2. 独立：不看词、不看别的句子，这一句本身读得懂：是谁、怎么了。不用“这”“那”指前面的东西。
3. 和旁边的词是一回事：读完这句再看右边的词，会觉得“难怪有这种感觉”。这句说处境或原因，词说感受。不重复词里的字，不把词里的比喻写进来。
4. 同段几句不一样：几组是这段同时存在的不同东西。说的事不同，说法也不同：可以是陈述一件事、一声自问、一句心里话、一个决定。不要每句都写成“他……，却……”。
5. 跨段接得上：只读每段主组的句子，从头到尾是一件有发展的事。后一段的主句要让人知道它从哪儿来。

比如一段里三组原来是：
“他很想联系对方，却怕打扰，所以一直没开口。”
“他想起以前也这样过，却还是改不了。”
“他盼着对方先来找他，却又怕真的来了不知说什么。”
可以写成：
“他还是没敢联系对方。”
“以前不也这样？”
“要是对方先开口就好了。”

意思都来自定稿的线，不加定稿没有的事。人称和称呼跟定稿一样，不要改。像一个人平平常常讲自己的经历：不用书面词，不站在人物外面讲解，不写格言和工整的对称句，不用套路句式，相邻的句子不要彼此太像。不写小节数。

只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"line":"…"}]}]}，每段每组都要给。

【定稿的线（依据）】
{FINAL}

【现在的屏幕（每段秒数，每组 rank、现在的话、右边的词）】
{CUR}
"""

FOUR = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。屏幕每段几组，每组左边一句话，右边几块短词。

逐组回答：
- glance：这句话一眼读得完吗？是 / 否
- alone：不看右边的词，这句话本身读得懂吗（是谁、怎么了）？懂 / 半懂 / 不懂
- tie：读完这句再看右边的词，你觉得是一回事吗（难怪有这种感觉）？是 / 勉强 / 否

逐段回答：
- hetero：这段几句是在说不同的东西吗，说法也不一样吗？是 / 部分 / 否（只有一组的段写“是”）
- chain：只读这段主组那句，和上一段主组那句接得上吗？能 / 勉强 / 不能（第一段写“能”）

只输出 JSON：{"sections":[{"sec":"S01","hetero":"是","chain":"能","groups":[{"idx":0,"glance":"是","alone":"懂","tie":"是"}]}],"overall":"两三句话：这四件事哪件最差，举例"}

【屏幕】
{SCREEN}
"""

EXP = """视频屏幕上有一些短词，边听音乐边看。只有词本身明确指向音乐里某个声音时，才在音乐动画上给那几个音上色；其余的词只是讲感受，不动音乐。

“明确指向”指观众读到这个词，自然会去听某个声音：比如“钟响”“只剩一个声音”“忽然停住”“高处的声音”“低音压下来”。
不算：讲心情、讲身体、讲比喻的词，比如“累了”“还想要更多”“水波推着往前”“烟花迸开”。

下面列的词里，哪些是明确指向？宁缺毋滥。只输出 JSON：{"keep":["…"]}，照抄词。

{WORDS}
"""


def write(a):
    w, ls, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{ls}.json'); win = pub16.windows(w)
    fin = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    cur = '\n'.join(f"\n### {s['sec']}（{round(win[s['sec']][1]-win[s['sec']][0])} 秒）\n" + '\n'.join(f"idx {i}（{g['rank']}）话：" + ' '.join(l['text'] for l in g.get('lines', [])) + '\n    词：' + ' / '.join(b['text'] for b in g.get('beads', [])) for i, g in enumerate(s['groups'])) for s in d['sections'])
    msg = P.replace('{FINAL}', fin).replace('{CUR}', cur)
    for k in range(3):
        ans = call(f'pub18_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public18-write')
        try:
            N = {s['sec']: {int(g['idx']): g['line'] for g in s['groups']} for s in parse(ans)['sections']}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    t = N.get(s['sec'], {}).get(i)
                    if t:
                        fr = [x for l in g.get('lines', []) for x in l.get('from', [])]; g['lines'] = [{'text': t, 'keys': [], 'from': fr}]
            break
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    else: return False
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True)
    if errs: wr(p.with_suffix('.try.json'), d); return False
    wr(p, d); wr(R2/f'script_{w}_{tag}.json', d); pub16.rate((w, tag)); return True


def screen(w, tag):
    rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for i, g in enumerate(s['groups']):
            rows.append(f"idx {i}（{g['rank']}）话：" + ' '.join(l['text'] for l in g.get('lines', [])))
            rows.append('    词：' + ' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def four(a):
    w, j, tag = a; p = R3/f'four_{w}_{j}_{tag}.json'
    if not p.exists():
        for k in range(3):
            ans = call(f'pub18F_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), FOUR.replace('{SCREEN}', screen(w, tag)), JUDGES[j], 'gpt3s', 'public18-four')
            try: r = parse(ans); assert r['sections']; wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); gs = [g for s in r['sections'] for g in s.get('groups', [])]
    print(w, j, tag, '一眼', dict(Counter(g.get('glance') for g in gs)), '单独懂', dict(Counter(g.get('alone') for g in gs)), '和词一回事', dict(Counter(g.get('tie') for g in gs)), '段内异质', dict(Counter(s.get('hetero') for s in r['sections'])), '接得上', dict(Counter(s.get('chain') for s in r['sections'])), flush=True)
    print('   ', r.get('overall', '')[:280], flush=True)


def explicit(a):
    w, src, tag = a; p = R3/f'marks_{w}_{tag}.json'; m = rd(R3/f'marks_{w}_{src}.json'); words = sorted({x['text'] for x in m['marks'] if x.get('render')})
    ans = call(f'pub18E_{w}_{tag}', EXP.replace('{WORDS}', '\n'.join(words)), G6, 'gpt3s', 'public18-explicit'); keep = set(parse(ans)['keep'])
    for x in m['marks']:
        if x.get('render') and x['text'] not in keep: x['render'] = False
    wr(p, m); print(w, '明确指向', sorted(keep), flush=True)


# ---------- 人话：标准第 3 条。N09 开放评审 + 句式统计，和定稿同样测 ----------
def lines_of(w, tag):
    if tag == 'FINAL':
        return [(s['sec'], [l['text'] for l in s['lines']]) for s in rd(R2/f'{w}_src.json')['sections']]
    return [(s['sec'], [l['text'] for g in s['groups'] for l in g.get('lines', [])]) for s in rd(R3/f'script_{w}_{tag}.json')['sections']]


def meter(w, tag):
    import re
    T = [t for _, ls in lines_of(w, tag) for t in ls]; n = max(1, len(T))
    heads = Counter(t[:1] for t in T); pair = Counter(t[:2] for t in T)
    adj = sum(a[:1] == b[:1] for _, ls in lines_of(w, tag) for a, b in zip(ls, ls[1:]))
    tp = {'我/他起句': round(sum(t[:1] in '我他' for t in T)/n, 2), '却/条': round(sum(t.count('却') for t in T)/n, 2), '也/条': round(sum(t.count('也') for t in T)/n, 2), '越…越/条': round(sum(len(re.findall('越.{0,10}越', t)) for t in T)/n, 2), '想…又怕/条': round(sum(len(re.findall('想.{0,14}(又|却|可|但).{0,4}怕', t)) for t in T)/n, 2), '分号/条': round(sum(t.count('；') for t in T)/n, 2), '问句/条': round(sum('？' in t for t in T)/n, 2), '同段相邻同起字': adj, '最常见起句': pair.most_common(4), '条数': n, '均字': sum(map(len, T))//n}
    print(w, tag, tp, flush=True); return tp


def lang_one(a):
    w, j, tag = a; p = R3/f'lang_{w}_{j}_{tag}.json'
    if not p.exists():
        tpl = (pub2.EVO/'DAG/prompts/N09_人话_开放评审/模板.txt').read_text(encoding='utf-8')
        text = '\n\n'.join(f"{sec}\n" + '\n'.join(f'- {t}' for t in ls) for sec, ls in lines_of(w, tag))
        msg = tpl.replace('{{', '{').replace('}}', '}').replace('{TEXT}', text)
        if text not in msg: msg += '\n\n'+text
        for k in range(3):
            ans = call(f'pub18L_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public18-lang')
            try: r = parse(ans); wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); cum = r.get('cumulative') or []
    print(w, j, tag, '分', r.get('score') or r.get('overall_score') or r.get('rating'), '局部问题', len(r.get('issues') or []), '累积问题', [(c.get('phenomenon', '')[:30], c.get('severity') or c.get('impact')) for c in cum], flush=True)


def lang(tag):
    for w in WORKS: meter(w, tag)
    with ThreadPoolExecutor(4) as ex: list(ex.map(lang_one, [(w, j, tag) for w in WORKS for j in JUDGES]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'write':
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(write, [(w, sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
    elif c == 'four':
        with ThreadPoolExecutor(4) as ex: list(ex.map(four, [(w, j, sys.argv[2]) for w in WORKS for j in JUDGES]))
    elif c == 'explicit':
        with ThreadPoolExecutor(2) as ex: list(ex.map(explicit, [(w, sys.argv[2], sys.argv[3]) for w in WORKS]))
    elif c == 'lang': lang(sys.argv[2])
