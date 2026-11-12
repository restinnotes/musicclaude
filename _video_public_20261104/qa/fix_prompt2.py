import json, sys
sys.stdout.reconfigure(encoding='utf-8')
t = open(sys.argv[1], encoding='utf-8').read()
i = t.find('"prompt"'); s = t[i:]; s = s[s.find(':')+1:].strip()
assert s[0] == '"'
BS = chr(92); Q = chr(34)
MAP = {'n': '\n', 't': '\t', Q: Q, BS: BS, '/': '/'}
out = []; k = 1; esc = False
while k < len(s):
    c = s[k]
    if esc: out.append(MAP.get(c, c)); esc = False
    elif c == BS: esc = True
    elif c == Q:
        rest = s[k+1:].lstrip()
        if rest.startswith('}') or rest == '': break
        out.append(Q)
    else: out.append(c)
    k += 1
p = ''.join(out); open(sys.argv[2], 'w', encoding='utf-8').write(p)
for n in ('g6', 'g56', 'argon'):
    x = open(f'r3/l23/prompt_{n}.txt', encoding='utf-8').read()
    print(n, len(x), [ph for ph in ('{FINAL}', '{SCREEN}', '{SOURCE}') if ph in x], '有输出格式' if '"point"' in x else '缺格式')
print(p[:600]); print('……'); print(p[-500:])
