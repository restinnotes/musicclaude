"""11-09 晚 骨架测（用户 11-09 晚：“扫的动的意思是 光看那些关键的东西 就可以给他把整个在表达什么在脑海里自己拼起来”；
“很可能就是骨架来看他到底是不是独立读的通的”）。标准第 7 条“关键词放大，带着人先看该先看的”一直没有测法，11-05 两层线被读全文的盲比否掉。
两步，两位评委（GPT-6、GPT-5.6）各自做：
  A 拼：评委只看每屏放大的字（按屏上顺序），写出拼出来的意思：每屏这个人此刻怎么了、为什么、什么感受；全曲连起来是一件什么事。
  B 对：另一次调用，拿 A 的复述对照完整屏幕稿，逐屏 0–4 打“拼对了多少”，列拼错的地方。
另报机械数：放大字占全屏字数的比例（防止把整句放大来作弊）。
校准：K11g 两遍（稳定）；对照 SR = K11g 的放大词换成同一行里同长度的随机片段（反面）。
python r3/skeleton.py TAG [轮次]     → r3/s24/skelA_{作品}_{评委}_{TAG}_{轮次}.json、skelB_…
python r3/skeleton.py sum TAG 轮次...
python r3/skeleton.py ctl TAG         生成 TAG+SR 对照
"""
import json, os, sys, random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint, pub16
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, view_text, to_script
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

A = """下面是一首钢琴曲“边听边看”视频的屏幕上被放大加亮的字。普通观众边听边扫，眼睛只抓这些大字。每一屏只给你这些大字，按它们在屏幕上的顺序排；其余的小字你看不到。
请只凭这些大字，在脑子里把它拼起来，写出你拼出来的东西。拼不出来的就写“拼不出”，不要编，也不要用你对这首曲子的任何了解去补。

只输出 JSON：{"screens":[{"sec":"S01","who":"这个人此刻怎么了（一句话）","why":"为什么会这样（拼不出写拼不出）","feel":"什么感受（几个词）"}],"story":"全曲连起来是一件什么事（两三句）"}，所有屏都要有。

{SKEL}
"""
B = """下面是一首钢琴曲“边听边看”视频的完整屏幕稿，以及一位只看了放大加亮字的观众凭这些大字拼出来的理解。
请逐屏对照，判断他拼对了多少：
- 4：这一屏的处境、原因、感受都拼对了，和完整稿说的是一回事。
- 3：主要的拼对了，原因或感受有一项缺了或偏了。
- 2：只拼对一部分，或主要的地方拼偏了。
- 1：基本没拼出来，只有零星的词对上。
- 0：拼反了或完全不相干。
另外列出拼错的地方（把意思拼反了、拼成了别的事）。最后判断他拼出来的全曲故事和完整稿是不是同一件事（0–4）。

只输出 JSON：{"screens":[{"sec":"S01","score":0,"wrong":"拼错的地方（没有写无）"}],"story":0,"story_note":"一句"}，所有屏都要有。

【完整屏幕稿】
{SCREEN}

【只看大字的观众拼出来的】
{RECON}
"""
prompt_lint.lint(A, 'skeleton.A'); prompt_lint.lint(B, 'skeleton.B')


def big(x):
    """一行里被放大的字：话行的 keys；感受块里的 keys；整行都标为放大的（keys 盖住整句）就是整句。"""
    out = []
    if x['kind'] == 'line':
        t = x['text']; ks = [k for k in x.get('keys') or [] if k in t]
        out += sorted(ks, key=lambda k: t.find(k))
    else:
        for i in x.get('items') or []: out += [k for k in i.get('keys') or [] if k in i['text']]
    return out


def skel(w, tag):
    rows = []; tot = 0; bigc = 0
    d = rd(S/f'screen_{w}_{tag}.json')
    for s in d['sections']:
        ks = [x['text'] for x in s['rows'] if x['kind'] == 'line'] if d.get('uniform') else [k for x in s['rows'] for k in big(x)]   # 碎块形态：大块整块就是骨架
        rows.append(f"### {s['sec']}：" + ' ／ '.join(ks) if ks else f"### {s['sec']}：（这一屏没有放大的字）")
        tot += sum(len(x['text']) if x['kind'] == 'line' else sum(len(i['text']) for i in x['items']) for x in s['rows']); bigc += sum(map(len, ks))
    return NL.join(rows), bigc/max(tot, 1)


def one(a):
    w, j, m, tag, run = a; pa = S/f'skelA_{w}_{j}_{tag}_{run}.json'; pb = S/f'skelB_{w}_{j}_{tag}_{run}.json'
    if pb.exists(): return rd(pb)
    sk, _ = skel(w, tag)
    if not pa.exists():
        for k in range(3):
            try: r = parse(call(f'skelA_{w}_{j}_{tag}_{run}' + ('' if not k else f'_r{k}'), A.replace('{SKEL}', sk), m, 'gpt3s', 'public24-skel')); assert r.get('screens'); wr(pa, r); break
            except Exception as ex: print('不合格A', w, j, tag, repr(ex)[:120], flush=True)
        else: return
    ra = rd(pa); rec = NL.join(f"### {x.get('sec')}：处境：{x.get('who')}；原因：{x.get('why')}；感受：{x.get('feel')}" for x in ra['screens']) + NL + '全曲：' + str(ra.get('story'))
    for k in range(3):
        try: r = parse(call(f'skelB_{w}_{j}_{tag}_{run}' + ('' if not k else f'_r{k}'), B.replace('{SCREEN}', view_text(w, tag)).replace('{RECON}', rec), m, 'gpt3s', 'public24-skel')); assert r.get('screens'); wr(pb, r); return r
        except Exception as ex: print('不合格B', w, j, tag, repr(ex)[:120], flush=True)


def summ(tag, runs):
    for w in WORKS:
        _, ratio = skel(w, tag); row = []
        for j in ('g6', 'g56'):
            for run in runs:
                p = S/f'skelB_{w}_{j}_{tag}_{run}.json'
                if not p.exists(): row.append(f'{j}{run} 缺'); continue
                r = rd(p); sc = [float(x['score']) for x in r['screens'] if isinstance(x.get('score'), (int, float))]
                row.append(f"{j}{run} {sum(sc)/len(sc):.2f}（≤2 {sum(1 for x in sc if x <= 2)} 屏，全曲 {r.get('story')}）")
        print(f"骨架测 {tag} {w}（放大字占 {ratio:.0%}）： " + ' ｜ '.join(row), flush=True)


def ctl(tag):
    random.seed(7)
    for w in WORKS:
        d = rd(S/f'screen_{w}_{tag}.json')
        for s in d['sections']:
            for x in s['rows']:
                if x['kind'] == 'line' and x.get('keys'):
                    t = x['text']; nk = []
                    for k in x['keys']:
                        L = len(k); st = random.randint(0, max(0, len(t)-L)); nk.append(t[st:st+L])
                    x['keys'] = nk
        wr(S/f'screen_{w}_{tag}SR.json', d); to_script(w, tag+'SR', d)
    print('对照已生成', tag+'SR')


if __name__ == '__main__':
    if sys.argv[1] == 'sum': summ(sys.argv[2], sys.argv[3:] or ['run1']); sys.exit()
    if sys.argv[1] == 'ctl': ctl(sys.argv[2]); sys.exit()
    tag = sys.argv[1]; run = sys.argv[2] if len(sys.argv) > 2 else 'run1'
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j, m, tag, run) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
    summ(tag, [run])
