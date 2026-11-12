import io, re, sys
txt = io.open(sys.argv[1], encoding='utf-8').read()
parts = re.split(r'^=== 行(\d+) (\S*) ===\n', txt, flags=re.M)
out = io.open(sys.argv[2], 'w', encoding='utf-8')
k = 0
for i in range(1, len(parts), 3):
    ln, ts, body = parts[i], parts[i+1], parts[i+2].strip()
    if body.startswith('<task-notification') or body.startswith('<system-reminder') or body.startswith('<side-sessions') or body.startswith('<local-command') or body.startswith('<command-name') or body.startswith('[Request interrupted') or body.startswith('<scheduled-task') or body.startswith('Caveat'):
        continue
    k += 1
    out.write('=== 行%s %s ===\n%s\n\n' % (ln, ts[:16], body[:2500]))
print(k)
