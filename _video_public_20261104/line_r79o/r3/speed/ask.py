import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pub24 import call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
D = Path(__file__).parent; msg = (D/'CASE.md').read_text(encoding='utf-8')
def one(a):
    name, m, route = a; ans = call(f'speed_adv_{name}', msg, m, route, 'public24-speed'); (D/f'ans_{name}.json').write_text(ans or '', encoding='utf-8'); print(name, len(ans or ''), flush=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6, 'gpt3s'), ('g56', G56, 'gpt4s')]))
