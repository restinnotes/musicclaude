import json, sys, io
src, out, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with io.open(src, encoding='utf-8', errors='replace') as f, io.open(out, 'w', encoding='utf-8') as o:
    for i, line in enumerate(f):
        ln = i + 1
        if ln < lo: continue
        if ln > hi: break
        try: d = json.loads(line)
        except Exception: continue
        if d.get('type') not in ('assistant', 'user') or d.get('isSidechain'): continue
        c = d.get('message', {}).get('content')
        if not isinstance(c, list): continue
        for b in c:
            if not isinstance(b, dict): continue
            if b.get('type') == 'tool_use':
                inp = b.get('input', {})
                s = inp.get('command') or inp.get('file_path') or json.dumps(inp, ensure_ascii=False)
                extra = ''
                if b.get('name') in ('Write',): extra = '\n--内容--\n' + inp.get('content', '')[:5000]
                if b.get('name') in ('Edit',): extra = '\n--新--\n' + inp.get('new_string', '')[:1500]
                o.write('### 行%d 调用 %s\n%s%s\n\n' % (ln, b.get('name'), s[:2500], extra))
            elif b.get('type') == 'tool_result':
                cc = b.get('content')
                if isinstance(cc, list): cc = '\n'.join(x.get('text', '') for x in cc if isinstance(x, dict))
                o.write('--- 行%d 结果\n%s\n\n' % (ln, (cc or '')[:2500]))
