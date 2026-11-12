"""把一条里中间的句末标点改成逗号（标准：每条一句），文字不动。usage: python round41_oneline.py TAG SOURCE"""
import json, os, re, sys
os.environ.setdefault('JV', '2')
import v6fix as V
tag, source = sys.argv[1:3]
for w in ('op60', 'op61'):
    d = json.loads((V.OUT / f'{w}_{source}.json').read_text(encoding='utf-8'))
    n = 0
    for s in d['graph']['segments']:
        for it in s['items']:
            new = re.sub(r'[。！？](?=.)', '，', it['text'])
            n += new != it['text']
            it['text'] = new
    d['base'] = f'{source}，每条一句规范化 {n} 处'
    (V.OUT / f'{w}_{tag}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f'# {w}｜线（{tag}）\n\n' + V.view(d['graph']), encoding='utf-8')
    print(w, tag, '规范化', n)
