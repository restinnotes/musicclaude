import json, sys, io
src, out, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with io.open(src, encoding='utf-8', errors='replace') as f, io.open(out, 'w', encoding='utf-8') as o:
    for i, line in enumerate(f):
        ln = i + 1
        if ln < lo: continue
        if ln > hi: break
        try: d = json.loads(line)
        except Exception: continue
        t = d.get('type')
        if t not in ('assistant', 'user'): continue
        if d.get('isSidechain'): continue
        c = d.get('message', {}).get('content')
        if isinstance(c, str): c = [{'type': 'text', 'text': c}]
        for b in c or []:
            if isinstance(b, dict) and b.get('type') == 'text' and b.get('text', '').strip():
                tx = b['text'].strip()
                if t == 'user' and (tx.startswith('<task-notif') or tx.startswith('<system-rem')): continue
                if tx.startswith('This session is being continued'): tx = tx[:200]
                o.write('=== %s 行%d %s ===\n%s\n\n' % ('用户' if t == 'user' else '助手', ln, d.get('timestamp', '')[:16], tx[:3000]))
