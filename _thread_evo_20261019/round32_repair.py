"""R32 局部修订：拿主线成品和开放评审（I01 的产物），只改评审指出的地方，其余条目一字不动。
脚本套用改动并查形态；不经人手。 usage: python round32_repair.py TAG SOURCE MODEL light|deep [--workers N]"""
import copy, glob, json, os, re, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, pipe, screen_flow as F, v6fix as V

RULES = {
'ten': """这次最多改 10 条（改写、合并、删除都算），只挑最值得改的：
一、跨段重复：同一个心理动作（比如一次次想靠近又收住、一次次眼前好却怕留不住）在好几段里落点相同的，只留真正有变化的；同一个认识已经说清楚的，后面不再重新说。
二、结尾前后：刚做出的决定不要在下一段原样再做一遍；最后一段要比前一段多走一步。
三、像在分析心理的句子（“不是……而是……”、替他总结的话）：换成他会说的话。
已经成立的发展链（发现了什么 → 因此怕什么 → 因此决定什么）不能断，关键转折要保留，不要把一段删薄。""",
'careful': """这次重点解决三件事：
一、同一个意思跨段重复（比如一次次舍不得、一次次想靠近又收住）：只留真正有变化的那几次，每次都要比上一次多走一步；没有多走一步的就删或换成这一段独有的东西。
二、像在分析心理的句子：换成他会说的话，念头直接说出来。
三、评审指出的转折没有来由：在前面已有的条目里带出一点前因。
但已经成立的发展链（发现了什么 → 因此怕什么 → 因此决定什么）不能断：改或删之后，后面那一步的来由仍要读得出来；关键转折和最后的决定要保留。删的比改的少，宁可改也不要把一段删薄。""",
'light': """改动要少：只动至少两位评审都指出的地方，或被评为严重的地方；单个评审的个人偏好不动。""",
'deep': """这次可以动得多一些：如果若干段在原地打转，可以把它们的条目重新分配任务，让每段只留下这一段真正不同的东西，但每条仍是这个人平常说话的口气。""",
}
PROMPT = """下面是一条“线”：一个人在这首曲子里经历的一件事，按音乐段落分段写成条目；后面是另一批人听这段音乐写下的听感记录（珠子），以及几位读者对这条线的评审。

这条线的口气已经是目前最好的：平常、具体，像一个人在讲自己的事。你的任务是保住这种口气，修掉评审指出的毛病。

{RULE}

可以做的改动，优先级从高到低：
1. 删掉一条（它只是重说前面已经说过的，或把走过的心理动作再走一遍）；
2. 把相邻两条合成一句；
3. 重写一条。重写时用这个人平常会说的话，写他此刻具体在乎什么、怕什么，少用“需要、依恋、亲近、安心、归属”这类概括词，也不要替他总结心理；
4. 某处转折没有铺垫时，可以在前面已有的条目里顺手带出一点前因，不另加事件。

边界：
- 没有改动的条目一字不动，不要顺手润色；
- 不新增事件、前史、对白、物件、第三人和对方的新举动；
- 不把珠子里的画面和情节写成真的发生的事；每段的主要听感仍要在这一段找得到情境相近的原因；
- 每段 2–4 条，每条一句；不要加长全文；
- 评审的建议只是参考，不要照抄它的句子；
- 不必解决所有问题，改不好的就留着。

【线】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

【评审】
{REVIEWS}

只输出 JSON：
{{"edits":[{{"id":"S03-2","op":"delete"}},{{"id":"S05-1","op":"replace","text":"新的一句"}}],"note":"一句话说改了什么"}}"""


def reviews(w, source='qurefs'):
    out = []
    for f in sorted(glob.glob(f'runs/eo2_afterr30_{w}_{source}_*')):
        d = V.parse(os.path.basename(f))
        if d:
            out.append({'problems': d.get('problems'), 'top3': d.get('top3')})
    return json.dumps(out, ensure_ascii=False, indent=0)


def apply_edits(w, tag, source, answer, note):
    g = copy.deepcopy(V.graph_of(w, source))
    edits = {}
    for e in answer.get('edits', []):
        # 模型把“相邻两条合成一句”写成 A+B：把合句放在 A，删掉 B。
        ids = re.split(r'[+＋,，、]', e['id'])
        edits[ids[0]] = {**e, 'id': ids[0]}
        for other in ids[1:]:
            edits[other] = {'id': other, 'op': 'delete'}
    known = {i['id'] for s in g['segments'] for i in s['items']}
    if set(edits) - known:
        print('未知编号', set(edits) - known, flush=True)
    gone = set()
    for s in g['segments']:
        keep = []
        for it in s['items']:
            e = edits.get(it['id'])
            if e and e.get('op') == 'delete':
                gone.add(it['id']); continue
            if e and e.get('op') == 'replace':
                it['text'] = e['text']; it['key'] = e['text'][:8]
            keep.append(it)
        s['items'] = keep
        if not 2 <= len(keep) <= 4:
            raise ValueError(f'{w} {s["sec"]}: {len(keep)} 条，违反每段 2–4 条')
    for s in g['segments']:
        for it in s['items']:
            it['cite'] = [c for c in it.get('cite', []) if c not in gone]
    V.tidy(g)
    rows = json.loads((V.OUT / f'{w}_{source}.json').read_text(encoding='utf-8'))['rows']
    (V.OUT / f'{w}_{tag}.json').write_text(json.dumps({'graph': g, 'rows': rows, 'base': note}, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f"# {w}｜线（{tag}）\n\n" + V.view(g), encoding='utf-8')
    n = sum(len(i['text']) for s in g['segments'] for i in s['items'])
    print(w, tag, '字', n, '改', sum(e.get('op') == 'replace' for e in edits.values()), '删', len(gone), flush=True)


def one(tag, source, model, rule, w):
    g = V.graph_of(w, source)
    msg = PROMPT.format(RULE=RULES[rule], LINE=V.view(g, ids=True), BEADS=V.beads(w), REVIEWS=reviews(w))
    answer = pipe.call(f'sc{tag}_{w}_A5', msg, model, tag)
    apply_edits(w, tag, source, answer, f'{source} 局部修订（{model}/{rule}）')


if __name__ == '__main__':
    F.configure()
    tag, source, model, rule = sys.argv[1:5]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(lambda w: one(tag, source, model, rule, w), F.WORKS):
            pass
