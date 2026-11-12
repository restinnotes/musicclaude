"""R33 生成：沿用 qu 前三步（逐字核对），只跑一个 A4。usage: python round33_gen.py TAG SCHEME [NOTE]
tag 对应 scTAG_work_A4；路由看 THREAD_ROUTE。A4 不复用 qu 结果，同提示词也重新抽样。"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, pipe, screen_flow as F


def one(tag, scheme, w):
    spec = pipe.load_spec(scheme)
    base_spec = pipe.load_spec('schemes/Q15.json')
    builtins, graph = pipe.work_context(w, 'qurefs')
    outputs = {}
    for sid in ('A1', 'A2', 'A3'):
        source = f'scqu_{w}_{sid}'
        if (evo.RUNS / source / 'input.txt').read_text(encoding='utf-8') != pipe.render_step(base_spec, sid, builtins, outputs):
            raise ValueError(f'{source}: input differs')
        outputs[sid] = pipe.call(source, None, 'g6', 'Q15')
    msg = pipe.render_step(spec, 'A4', builtins, outputs)
    pipe.save(w, graph, pipe.call(f'sc{tag}_{w}_A4', msg, 'g6', tag), spec['note'], tag, 'qurefs')


if __name__ == '__main__':
    F.configure()
    tag, scheme = sys.argv[1:3]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: one(tag, scheme, w), F.WORKS))
