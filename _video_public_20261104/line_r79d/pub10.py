"""跑顾问的候选：两首同一套提示词，按大众版的格式输出，再做轻体检（线盲比 + 只看屏幕的观众）。
python pub10.py 候选名…
"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3, pub_eval
from adv3 import FMT
from pub2 import G6, WORKS, call, parse, rd, source_matched, tidy_keys, wr


def gen(name):
    c = rd(pub2.OUT/f'candidates/{name}.json')

    def one(w):
        p = pub3.OUT/f'script_{w}_{name}.json'
        if p.exists(): return True
        prev = ''
        for i, step in enumerate(c['steps']):
            body = step.replace('{SOURCE}', source_matched(w)).replace('{PREV}', prev)
            if i == len(c['steps'])-1: body += '\n\n'+FMT
            prev = call(f'pub10_{w}_{name}_s{i}', body, G6, 'gpt3s', 'public10-gen')
            if not prev: print(w, name, '无返回', flush=True); return False
        for k in range(3):
            try:
                d = tidy_keys(parse(prev)); errs = pub3.check(w, d)
            except Exception as e:
                errs = [f'JSON 解析失败：{e}']; d = None
            print(w, name, '第', k+1, '次，问题', len(errs), errs[:4], flush=True)
            if not errs: wr(p, d); return True
            prev = call(f'pub10_{w}_{name}_fix{k}', '下面的输出没过检查。修好这些问题，其余不动，输出完整 JSON。\n'+'\n'.join(errs)+'\n\n'+FMT+'\n\n上一次输出：\n'+(prev or ''), G6, 'gpt3s', 'public10-gen')
        return False
    with ThreadPoolExecutor(2) as ex: ok = all(ex.map(one, WORKS))
    if ok: pub_eval.run(name, lite=True)
    return ok


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(3) as ex: print(list(zip(sys.argv[1:], ex.map(gen, sys.argv[1:]))), flush=True)
