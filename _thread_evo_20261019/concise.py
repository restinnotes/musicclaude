"""凝练 vs 人话 (user 10-21: still too much filler, e.g. 1–3 bars get a full paragraph; guess: "concise" ~ "plain").
No length targets.  K1 凝练 | K2 人话+凝练 | K3 K2+每段长短相称 | K4 K3+C1具体
ids: pk_<K1..K4>_<thread>_r<j>.  python concise.py seglen <id>... prints per-segment chars."""
import sys
import arts, evo, node2b, plain, segcheck

H = "保留原来的分段标题。只输出重写后的文章。\n\n"
K1 = "凝练地重写下面这篇文章，不损失内容。"
K2 = "用人话、凝练地重写下面这篇文章，不损失内容。"
PROP = "每段的长短要和这一段真正发生了多少相称：这一段没有新的变化，一两句话带过就行；不要为了每段都有话说而凑字。"
C1 = "把抽象的词换成这个人具体在想什么、怕什么、想要什么、在做什么。"
VAR = {"K1": K1 + H, "K2": K2 + H, "K3": K2 + PROP + H, "K4": K2 + PROP + C1 + H}


def seglen(n):
    w = "op60" if "op60" in n else "op61"
    j = segcheck.to_json(arts.clean(evo.output(n)), w)
    return [(s["start"], s["end"], len(s["text"])) for s in j["segments"]] if j else None


if __name__ == "__main__":
    if sys.argv[1:2] == ["seglen"]:
        for n in sys.argv[2:]:
            L = seglen(n); print(n, sum(x[2] for x in L) if L else "parse fail", " ".join(f"{a}-{b}:{c}" for a, b, c in L or []))
        sys.exit()
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(t))
            for v, p in [(k, VAR[k]) for k in ("K3", "K4")]:
                for j in (1, 2):
                    rid = f"pk_{v}_{t}_r{j}"
                    if not evo.done(rid):
                        jobs.append(node2b.job(rid, p + src, {"stage": "concise", "variant": v, "thread": t}))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 4)
