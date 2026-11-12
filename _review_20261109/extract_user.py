import json, sys, io
src = sys.argv[1]; out = sys.argv[2]
n = 0; kept = 0
types = {}
with io.open(src, encoding='utf-8', errors='replace') as f, io.open(out, 'w', encoding='utf-8') as o:
    for i, line in enumerate(f):
        n += 1
        try:
            d = json.loads(line)
        except Exception:
            continue
        t = d.get('type'); types[t] = types.get(t, 0) + 1
        if t != 'user': continue
        if d.get('isSidechain') or d.get('isMeta'): continue
        m = d.get('message', {})
        c = m.get('content')
        texts = []
        if isinstance(c, str): texts.append(c)
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get('type') == 'text':
                    texts.append(b.get('text', ''))
        txt = '\n'.join(texts).strip()
        if not txt: continue
        kept += 1
        o.write('=== 行%d %s ===\n%s\n\n' % (i + 1, d.get('timestamp', ''), txt[:6000]))
print(n, kept, types)
