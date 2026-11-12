"""R31 生成：同一提示词重抽 Q15 写线层，以及“只删不改”节点。都从 qu 的前三步出发。
usage: python round31_gen.py [--workers N]
只删节点的结果由脚本套用，文字一字不动；每段至少留 2 条。"""
import copy, json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, pipe, screen_flow as F, v6fix as V

BASE = 'qurefs'
DELETE = """下面是一条“线”：一个人在这首曲子里经历的一件事，按音乐段落分段写成条目，后面附着另一批人听这段音乐写下的听感记录（珠子）。线和珠子会排在一起给读者看。

你只能决定删掉哪些条目。不能改任何一个字，不能合并，不能调整顺序。

连着从头读到尾，找出这样的条目：它只是把前面已经说过的意思再说一遍，或把前面已经走过的心理动作再走一遍，读者读到它没有得到新东西；或者它在替人物总结，前后的条目已经让人明白了。
删之前逐条核对：
- 删掉后，前后两条读起来还接得上，后文提到的东西不会没有着落；
- 这一段至少还留 2 条；
- 这一段某颗珠子的感受，如果只有这一条能给它一个情境相近的原因，就不删；
- 一条虽然和前面相近，但它标志着人物走到了新的地方（做了决定、看法变了、代价变了），就不删。
没有该删的就不删，不要凑数。删得少而准，比删得多更好。

【线】
{LINE}

【珠子】
{BEADS}

只输出 JSON：{{"delete":[{{"id":"S03-2","why":"它重复了哪一条的什么"}}]}}"""


def apply_delete(w, tag, source, answer, model):
    g = copy.deepcopy(V.graph_of(w, source))
    wanted, skipped, applied = {d['id'] for d in answer.get('delete', [])}, [], []
    known = {i['id'] for s in g['segments'] for i in s['items']}
    skipped += sorted(wanted - known)
    for s in g['segments']:
        for it in list(s['items']):
            if it['id'] in wanted:
                if len(s['items']) <= 2:
                    skipped.append(it['id']); continue
                s['items'].remove(it); applied.append(it['id'])
    gone = set(applied)
    for s in g['segments']:
        for it in s['items']:
            it['cite'] = [c for c in it.get('cite', []) if c not in gone]
    V.tidy(g)
    rows = json.loads((V.OUT / f'{w}_{source}.json').read_text(encoding='utf-8'))['rows']
    note = f'{source} 只删不改（{model}），删 {len(applied)} 条'
    (V.OUT / f'{w}_{tag}.json').write_text(json.dumps({'graph': g, 'rows': rows, 'base': note}, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f"# {w}｜线（{tag}）\n\n" + V.view(g), encoding='utf-8')
    print(w, tag, '删', applied, '未执行', skipped, flush=True)


def delete_job(tag, source, model, w):
    g = V.graph_of(w, source)
    rid = f'sc{tag}_{w}_A5'
    msg = DELETE.format(LINE=V.view(g, ids=True), BEADS=V.beads(w))
    apply_delete(w, tag, source, pipe.call(rid, msg, model, tag), model)


def resample_job(tag, w):
    spec = pipe.load_spec('schemes/Q15.json')
    builtins, graph = pipe.work_context(w, BASE)
    outputs = {}
    for sid in ('A1', 'A2', 'A3'):
        source = f'scqu_{w}_{sid}'
        if (evo.RUNS / source / 'input.txt').read_text(encoding='utf-8') != pipe.render_step(spec, sid, builtins, outputs):
            raise ValueError(f'{source}: input differs, refuse to reuse')
        outputs[sid] = pipe.call(source, None, 'g6', 'Q15')
    msg = pipe.render_step(spec, 'A4', builtins, outputs)
    if (evo.RUNS / f'scqu_{w}_A4' / 'input.txt').read_text(encoding='utf-8') != msg:
        raise ValueError('A4 input differs from qu, refuse')
    pipe.save(w, graph, pipe.call(f'sc{tag}_{w}_A4', msg, 'g6', tag), f'Q15 同提示词重抽 {tag}', tag, BASE)


def main():
    F.configure()
    jobs = [(delete_job, ('round31_del6', BASE, 'g6', w)) for w in F.WORKS]
    jobs += [(delete_job, ('round31_del56', BASE, 'g56', w)) for w in F.WORKS]
    jobs += [(resample_job, (f'round31_qus{n}', w)) for n in (1, 2, 3) for w in F.WORKS]
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 2
    def run(job):
        fn, args = job
        try:
            fn(*args); return args, 'ok'
        except Exception as e:
            print('FAILED', args, e, flush=True); return args, str(e)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for r in pool.map(run, jobs):
            print(r, flush=True)


if __name__ == '__main__':
    main()
