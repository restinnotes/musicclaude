"""11-07 盲比顺序交换实验（两位顾问问诊后一致建议：X、Y 标签和内容不变，只把出现先后对调）。
原盲比：先 【X】 后 【Y】。这里：先 【Y】 后 【X】，标签和内容同原座位。结果 s24/vsR_{w}_{j}_{tag}_{seat}.json。
配对看：同一评委、同一座位，两种先后都选新=稳定选新；都选旧=稳定选旧；换顺序就变=位置敏感。
python vs_order.py TAG [TAG...]
"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub24
from pub24 import S, rd, wr, call, parse, view_text, VS, JUDGES, WORKS

VSR = VS.replace('【X】\n{X}\n\n【Y】\n{Y}', '【Y】\n{Y}\n\n【X】\n{X}')
assert VSR != VS


def one(a):
    w, j, tag, seat = a; p = S/f'vsR_{w}_{j}_{tag}_{seat}.json'
    if not p.exists():
        a1, b1 = view_text(w, tag), view_text(w, 'w23'); x, y = (a1, b1) if seat == 'X' else (b1, a1)
        for k in range(3):
            ans = call(f'pub24VR_{w}_{j}_{tag}_{seat}'+('' if not k else f'_r{k}'), VSR.replace('{X}', x).replace('{Y}', y), JUDGES[j], 'gpt3s', 'public24-vsR')
            try: r = parse(ans); assert r['better'] in ('X', 'Y'); wr(p, {'seat': seat, **r}); break
            except Exception as ex: print('不合格', repr(ex)[:150], flush=True)


def report(tag):
    out = {}
    for w in WORKS:
        st = {'稳定选新': 0, '稳定选旧': 0, '位置敏感': 0}; first = [0, 0]; why = [0, 0]
        for j in JUDGES:
            for seat in 'XY':
                a, b = S/f'vs_{w}_{j}_{tag}_{seat}.json', S/f'vsR_{w}_{j}_{tag}_{seat}.json'
                if not (a.exists() and b.exists()): continue
                ra, rb = rd(a), rd(b); na, nb = ra['better'] == seat, rb['better'] == seat
                st['稳定选新' if na and nb else '稳定选旧' if not (na or nb) else '位置敏感'] += 1
                # 后出现的那一版是否被选：原顺序后出现的是 Y，交换后后出现的是 X
                first[0] += (ra['better'] == 'X') + (rb['better'] == 'Y'); first[1] += 2
                for r in (ra, rb): why[0] += (r.get('nets') or {}).get('why') == seat; why[1] += 1
        out[w] = st
        print(tag, w, st, '| 先出现的版本被选', f'{first[0]}/{first[1]}', '| “为什么”一项新版赢', f'{why[0]}/{why[1]}', flush=True)
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); tags = sys.argv[1:]
    with ThreadPoolExecutor(12) as ex: list(ex.map(one, [(w, j, t, s) for t in tags for w in WORKS for j in JUDGES for s in 'XY']))
    for t in tags: report(t)
