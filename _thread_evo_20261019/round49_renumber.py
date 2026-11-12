"""条目编号按实际位置重排（增删后编号会有空洞，引用标记会指错），同步 cite 和引用连线；文字、顺序不动。usage: python round49_renumber.py TAG"""
import json, os, sys
os.environ.setdefault('JV', '2')
import v6fix as V
tag = sys.argv[1]
for w in ('op60', 'op61'):
    p = V.OUT / f'{w}_{tag}.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    before = [i['text'] for s in d['graph']['segments'] for i in s['items']]
    mapping = {i['id']: f"{s['sec']}-{k}" for s in d['graph']['segments'] for k, i in enumerate(s['items'], 1)}
    for s in d['graph']['segments']:
        for i in s['items']:
            i['id'] = mapping[i['id']]
            i['cite'] = [mapping[c] for c in i.get('cite', []) if c in mapping]
        s['because'] = [{**b, 'from': mapping.get(b.get('from'), b.get('from')), 'to': mapping.get(b.get('to'), b.get('to'))} for b in s.get('because', [])]
    assert before == [i['text'] for s in d['graph']['segments'] for i in s['items']]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f'# {w}｜线（{tag}）\n\n' + V.view(V.graph_of(w, tag)), encoding='utf-8')
    print(w, tag, '重排', sum(k != v for k, v in mapping.items()), '处，文字不变')
