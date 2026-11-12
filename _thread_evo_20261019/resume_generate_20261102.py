"""两套候选并行生成；输出就地检查，测量须待阅读成品后启动。"""
from concurrent.futures import ThreadPoolExecutor

import pipe
from resume_20261102 import ROOT


def run(name, tag):
    spec = pipe.load_spec(ROOT / f"schemes/{name}.json")
    for work in ("op60", "op61"):
        builtins, graph = pipe.work_context(work, "qu")
        print("运行前核对", name, work, "段数", len(graph["segments"]), "珠子字数", len(builtins["BEADS_TEXT"]), flush=True)
        assert graph["segments"] and builtins["BEADS_TEXT"].strip()
    pipe.run(spec, tag, ref="qu")
    print(name, tag, "两首已生成，等待读成品及形态检查", flush=True)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run, name, tag) for name, tag in (("R26G", "r26g"), ("R26T", "r26t"))]
        for future in futures:
            future.result()
