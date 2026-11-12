"""11-08 迭代准则 I12/I13：接近过线的候选交回原提出者改（同一方案最多 3 次）。
python r3/adv_fix.py TAG 提出者(g6|g56) 原提示词文件 新提示词名      例：python r3/adv_fix.py g68K3 g6 prompt_BLg63.txt BLg63b
"""
import io, os, re, sys, contextlib
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['PUB_BC_ALL'] = '1'
import gate2, prompt_lint
from pub24 import S, R2, rd, call, parse, G6, G56, WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')

FIX = """你是顾问。你上一轮写的写稿提示词（附在最后）已经两首同跑、测完了。它是这一批里最接近过线的，现在交回给你改。

【门槛（大众版标准 7 条的测法）】
- 意思走样：至少两位评委同报一处严重的意思改动（疑问写成断言、担心写成已发生、加了定稿没有的事、珠子比喻写成真事等）就没过。
- 整屏珠子覆盖：屏幕全部文字对定稿珠子要点的严格覆盖（具体的画面、身体感觉、比喻、心里话还在才算），不低于现在的旧视频。
- 看片盲比（对旧视频，两种先后顺序配对，每首 8 次判断）：没有稳定选旧；分项 扫一眼抓到 scan、连贯不跳 flow、不啰嗦 concise、人话 human、知道为什么 why、单独成立 alone、细腻 fine，新版赢的都不少于旧版。

【你这套的结果（如有多版，按先后列出；最后一版是这次交回的）】
{RESULT}

【没过的项的证据】
{EVIDENCE}

请：先一两句诊断没过的原因；再给出改后的完整提示词——保住已经赢的项，只改让它没过的地方，可以大改结构。要求不变：提示词里不放任何具体作品的内容或例子（上面的证据只给你看，不能写进提示词），不写死字数、秒数上限，输出格式和占位符（{{BUDGET}}、{{DAGSTD}}、{{FINAL}}、{{BEADS}}）保持原样。

只输出 JSON：{"diagnosis":"…","prompt":"完整提示词"}。回答时请不要进行联网搜索。

【你上一轮的提示词】
{PROMPT}
"""


def evidence(tag):
    out = []
    pts = {q['id']: (s['sec'], q['text']) for w in WORKS for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads'] for q in b['points']}
    for w in WORKS:
        nf, cons = gate2.faith(w, tag)
        if nf:
            for j in JUDGES:
                for x in rd(S/f'faith_{w}_{j}_{tag}.json')['issues']:
                    if x.get('severity') == '严重' and (x.get('sec'), (x.get('screen') or '').replace('【', '').replace('】', '')[:8]) in cons:
                        out.append(f"- {w} 走样 {x.get('sec')}：屏幕「{x.get('screen')}」← 定稿「{x.get('source')}」：{x.get('why')}")
        b, b0 = gate2.bcov(w, tag), gate2.bcov(w, 'w23')
        if b is not None and b0 is not None and b < b0:
            c = Counter()
            for j in JUDGES:
                for it in rd(S/f'beadcovA_{w}_{j}_{tag}.json')['items']:
                    if it.get('verdict') != '留住': c[it['id']] += 1
            lost = [k for k, n in c.most_common() if n >= 3][:25]
            out.append(f"- {w} 整屏珠子覆盖 {b}（旧视频 {b0}）。至少三位评委判为没留住的珠子要点（节选）：" + '；'.join(f"{pts.get(k, ('?', k))[0]}「{pts.get(k, ('', k))[1][:30]}」" for k in lost))
        full, st, dims = gate2.vs(w, f'{tag}__w23')
        for d, (a, c2) in dims.items():
            if a < c2:
                for j in JUDGES:
                    for seat in 'XY':
                        r = rd(S/f'vs2_{w}_{j}_{tag}__w23_{seat}.json')
                        if (r.get('nets') or {}).get(d) not in (seat, '平', None):
                            old = 'Y' if seat == 'X' else 'X'; t = r.get('why') or ''
                            t = re.sub(r'(?<![A-Za-z])'+seat+r'(?![A-Za-z])', '〈你这版〉', re.sub(r'(?<![A-Za-z])'+old+r'(?![A-Za-z])', '〈旧视频〉', t))
                            out.append(f"- {w} 盲比 {d} 判旧视频赢的理由：{t}")
    return '\n'.join(out)


if __name__ == '__main__':
    tag, who, pf, new = sys.argv[1:5]
    hist = sys.argv[5].split(',') if len(sys.argv) > 5 else []   # 11-08：第二次交回时，把前几版的结果和字数一起给（看清此消彼长）
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for h in hist + [tag]:
            gate2.gate(h)
            for w in WORKS:
                sc = rd(S/f'screen_{w}_{h}.json'); L = [x['text'] for s in sc['sections'] for x in s['rows'] if x['kind'] == 'line']; F = [i['text'] for s in sc['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
                w23 = rd(Path(__file__).resolve().parent/f'script_{w}_w23.json'); n23 = sum(len(l['text']) for s in w23['sections'] for g in s['groups'] for l in g['lines']) + sum(len(b['text']) for s in w23['sections'] for g in s['groups'] for b in g['beads'])
                print(f"   {h} {w} 字数：连贯 {sum(map(len, L))} 字 {len(L)} 行；散落 {sum(map(len, F))} 字 {len(F)} 块（平均每块 {round(sum(map(len, F))/max(1, len(F)), 1)} 字）；整屏共 {sum(map(len, L))+sum(map(len, F))} 字，旧视频 {n23} 字")
    ev = evidence(tag)
    if os.environ.get('ADV_EXTRA'): ev += chr(10) + Path(os.environ['ADV_EXTRA']).read_text(encoding='utf-8')   # 11-08：过了门槛但看片、开放评审发现的问题
    msg = FIX.replace('{RESULT}', buf.getvalue()).replace('{EVIDENCE}', ev).replace('{PROMPT}', (S/pf).read_text(encoding='utf-8'))
    print(len(msg), flush=True)
    ans = call(f'adv_fix_{new}', msg, G6 if who == 'g6' else G56, 'gpt3s', 'public24-adv-fix'); r = parse(ans) or {}
    t = r.get('prompt') or ''
    h = prompt_lint.find(t.replace('{BUDGET}', '').replace('{DAGSTD}', '').replace('{FINAL}', '').replace('{BEADS}', ''))
    (S/f'prompt_{new}.txt').write_text(t, encoding='utf-8')
    print(new, '诊断', (r.get('diagnosis') or '')[:400], '| 占位符', all(k in t for k in ['{BUDGET}', '{FINAL}', '{BEADS}']), '| 泛化', h or '过', flush=True)
