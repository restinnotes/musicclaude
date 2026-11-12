"""Frozen text-span correspondence after writing. Never changes source prose."""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import experiment_batch as B
import covjudge

OUT = B.ROOT / 'evaluations/span_links'
PROMPT = '''下面给出已经写定的一段“线”和同段的“珠子”，以及全文供理解前后。
线讲一个人经历的事；珠子讲听音乐时的声音、意象、身体感和心理感受。
请为之后同色标示生成具体文字片段之间的对应关系，只加标注，不改写任何原文。

要求：
1. 每条link指出：线的哪一小部分，与哪颗珠子的哪一小部分情境或感受相近；摘取双方原文中连续、完整而尽量小的意义片段，不省略、不换词、不拼接。支持一处线串起多颗珠子、同颗珠子分属几处线。
2. 这是情境联系，不是两段文字字面相同，也不是说珠子的画面真的发生过。不要因为同含一个情绪词就连线。理由只据已写出的内容，不能把评委推测写成原文字面事实。
3. 珠子的一部分对应得上，不把整颗都当作对应；声音、技法、音乐材料身份、画面细节若没有可对应的人的处境，可以保留不连。演奏条件、互相替代的听法原样保留，不把不同听法拼成人物先后发生的事。
4. 关系标“相近”或“偏弱”。只接得上一部分的，尽量缩小引用范围后再标；仍需明显推断才接得上的标偏弱并说明缺口。没有合适联系的不要凑。
5. 每颗珠子都检查。无任何link的珠子必须列入unlinked并说明为什么；另可把一颗珠子中未被联系覆盖的重要片段列出。声音/意象保留不连，不自动等于线写坏或必须改线。
6. 同一关系不用重复列，片段尽量不重叠。每条最多用一句简短理由，不加新故事。现有逐颗评审只是参考，两位不一致的保留其分歧，不把整颗“说清”理解为每个细节已覆盖。

【全文，仅作上下文】
{CONTEXT}

【本段线，可作为端点的原文】
{LINES}

【本段珠子，可作为端点的原文】
{BEADS}

【两位现有逐颗判定，参考】
{REVIEWS}

只输出JSON：{{"links":[{{"line_id":"原编号","line_quote":"原文连续片段","bead_id":"原编号","bead_quote":"原文连续片段","strength":"相近","why":"情境联系"}}],"unlinked":[{{"bead_id":"原编号","quote":"原文连续片段","reason":"无对应或保留未连部分的原因"}}],"note":"边界或仍需检查处"}}。
引用片段必须能在提供的对应原文字段中逐字找到，不输出改写后的线或珠子。'''


def source(w, tag, sec):
    graph = B.V.graph_of(w, tag)
    segment = next(s for s in graph['segments'] if s['sec'] == sec)
    beads = [b for b in covjudge.beads(w) if b['sec'] == sec]
    reviews = {j: [b for b in (B.V.parse(f'cov2_{w}_{j}_{tag}') or {}).get('beads', []) if b['sec'] == sec] for j in B.F.JUDGES}
    return {'work': w, 'tag': tag, 'sec': sec, 'bars': segment['bars'], 'relation': segment['relation'],
            'lines': [{'id': i['id'], 'text': i['text']} for i in segment['items']], 'beads': beads, 'reviews': reviews}


def render_prompt(d, tag):
    return PROMPT.format(CONTEXT=B.V.view(B.V.graph_of(d['work'], tag)),
                         LINES=B.json_text(d['lines']), BEADS=B.json_text(d['beads']),
                         REVIEWS=B.json_text(d['reviews']))


def prepare(tag, full=False):
    root = OUT / tag
    root.mkdir(parents=True, exist_ok=True)
    tasks = []
    selection = ({w: [s['sec'] for s in B.V.graph_of(w, tag)['segments']] for w in B.F.WORKS}
                 if full else {'op60': ['S01', 'S07', 'S12'], 'op61': ['S01', 'S07', 'S11']})
    for w, sections in selection.items():
        for sec in sections:
            d = source(w, tag, sec)
            rid = f'span1_{tag}_{w}_{sec}_g6'
            msg = render_prompt(d, tag)
            B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', msg)
            B.write_frozen(root / f'{w}_{sec}_source.json', B.json_text(d))
            tasks.append({'work': w, 'sec': sec, 'rid': rid, 'source_sha256': B.digest(B.json_text(d)), 'input_sha256': B.digest(msg)})
    manifest = {'tag': tag, 'scope': 'all sections, both works, identical prompt' if full else 'six-section pilot, both works, identical prompt', 'tasks': tasks}
    B.write_frozen(root / ('full_manifest.json' if full else 'pilot_manifest.json'), B.json_text(manifest))
    return manifest


def collect(tag, full=False):
    import msvcrt
    os.environ['THREAD_ROUTE'] = 'gpt3s'
    B.F.configure()
    manifest = json.loads((OUT / tag / ('full_manifest.json' if full else 'pilot_manifest.json')).read_text(encoding='utf-8'))
    with (OUT / tag / 'receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def one(t):
            rid = t['rid']
            msg = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
            assert B.digest(msg) == t['input_sha256']
            if not B.evo.done(rid):
                answer = B.evo.call(rid, msg, model=B.evo.G6, meta={'stage': 'span-link-pilot', 'web': True})
                if not answer:
                    return {**t, 'status': 'incomplete_inspect_receiver'}
            return {**t, 'status': 'full_read_required'}
        with ThreadPoolExecutor(max_workers=2) as pool:
            rows = list(pool.map(one, manifest['tasks']))
        (OUT / tag / ('full_collection_result.json' if full else 'collection_result.json')).write_text(B.json_text({'terminal': True, 'tasks': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)


def locate(text, quote):
    if not quote or text.count(quote) != 1:
        raise ValueError(f'quote absent or ambiguous: {quote!r}')
    start = text.index(quote)
    return {'start': start, 'end': start + len(quote), 'quote': quote}


def validated(task, tag):
    rid = task['rid']
    d = json.loads((OUT / tag / f"{task['work']}_{task['sec']}_source.json").read_text(encoding='utf-8'))
    assert B.digest(B.json_text(d)) == task['source_sha256']
    current = source(task['work'], tag, task['sec'])
    if B.digest(B.json_text(current)) != task['source_sha256']:
        raise ValueError('current source differs from the frozen annotation source')
    frozen_input = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
    if (B.digest(frozen_input) != task['input_sha256']
            or B.digest(render_prompt(current, tag)) != task['input_sha256']):
        raise ValueError('annotation input or full-work context changed')
    repair_path = OUT / tag / f"{task['work']}_{task['sec']}_repair.json"
    if repair_path.exists():
        repair = json.loads(repair_path.read_text(encoding='utf-8'))
        assert repair['original_run'] == rid and repair['original_input_sha256'] == task['input_sha256']
        assert B.digest(B.evo.output(rid)) == repair['original_output_sha256']
        rid = repair['rid']
        revised_input = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
        if (B.digest(revised_input) != repair['input_sha256']
                or revised_input != frozen_input + repair['review_suffix']):
            raise ValueError('annotation repair input changed')
    if not B.reviewed(rid):
        raise ValueError('full read required')
    answer = B.V.parse(rid)
    lines = {i['id']: i['text'] for i in d['lines']}
    beads = {i['id']: i['text'] for i in d['beads']}
    links, unlinked, seen = [], [], set()
    for link in answer['links']:
        if link['strength'] not in ('相近', '偏弱'):
            raise ValueError('invalid relationship strength')
        a = locate(lines[link['line_id']], link['line_quote'])
        b = locate(beads[link['bead_id']], link['bead_quote'])
        key = (link['line_id'], a['start'], a['end'], link['bead_id'], b['start'], b['end'])
        if key in seen:
            raise ValueError('duplicate link')
        seen.add(key)
        links.append({**link, 'line_span': a, 'bead_span': b,
                      'id': B.digest(B.json_text((tag, d['work'], task['source_sha256'], key)))[:16]})
    for item in answer['unlinked']:
        unlinked.append({**item, 'span': locate(beads[item['bead_id']], item['quote'])})
    if set(beads) - {i['bead_id'] for i in links + unlinked}:
        raise ValueError('bead not inspected')
    return {**d, 'links': links, 'unlinked': unlinked, 'note': answer.get('note'), 'source_sha256': task['source_sha256'],
            'model_run': rid, 'model_output_sha256': B.digest(B.evo.output(rid))}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare', 'collect'))
    p.add_argument('tag')
    p.add_argument('--all', action='store_true', help='All sections of both works; exact cached pilot responses are reused')
    a = p.parse_args()
    if a.action == 'prepare':
        print(B.json_text(prepare(a.tag, a.all)))
    else:
        collect(a.tag, a.all)
