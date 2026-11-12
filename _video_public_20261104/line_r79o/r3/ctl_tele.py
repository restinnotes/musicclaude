"""11-10 人造对照 T（只用于校准盲比第五版的 human）：拿一版碎块稿，块数、顺序、意思、from 都不变，只把每块的说法改成电报腔、标签腔、文言式省略、名词堆叠。
python r3/ctl_tele.py 来源TAG 新TAG"""
import json, sys, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script
import fragwrite, glob
MSG = """下面是一份视频屏幕稿（JSON）。这是为了校准评委做的“反面对照”，请把它改成说话不自然的版本：
- 结构完全不变：段、块数、顺序、after、from、bars、at、notes 都照抄。
- 每个 big 和 small 的 text 意思不变、信息不增不减，只把说法改成不像人平常说话的样子：电报式省略（删掉口语里需要的虚词、主语、动词）、四字或文言式压缩、标签式词组、名词堆叠、书面摘要腔。每种都要用到，分散在全篇。长度和原来差不多或更短。
- accent 要改成新 text 里真实存在的一段字（没有就空）。notes 的 text 照抄。
只输出改好的完整 JSON。

"""
def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): return
    cur = sorted(glob.glob(str(S/f'frag_{w}_{src}_try*.json')))[-1]
    for k in range(3):
        try:
            r = parse(call(f'ctltele_{w}_{new}' + ('' if not k else f'_r{k}'), MSG + Path(cur).read_text(encoding='utf-8'), G6, 'gpt3s', 'public24-ctl'))
            scr, bad, miss = fragwrite.convert(w, r); wr(p, scr); to_script(w, new, scr); print(w, new, '好', len(bad), flush=True); return
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True)
if __name__ == '__main__':
    src, new = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [(w, src, new) for w in WORKS]))
