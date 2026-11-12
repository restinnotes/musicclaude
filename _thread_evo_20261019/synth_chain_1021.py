"""(Restored 10-23 from the session transcript after synth.py was reused for the pool synthesis; chain_synth.sh now calls this file.)
Should the Thread, like the beads, be run several times and synthesized? (user 10-21)
Per Center: 4 independent N7 lines -> step inventories -> one synthesized causal chain -> line written from the chain.
All five lines then get the same C1 concrete rewrite and are judged blind together (judge_line_v6).
phases: gen | inv | syn | c1      ids: n8a_/n8_<work>_<c>_r<j>, inv_<line>, syn_<work>_<c>, n8_<work>_<c>_syn, pc_C1_<line>_r1
"""
import json, sys
import arts, concrete, evo, node2b, node2i, node2j, plain, seg, stepcheck

CENTERS = {"op60": ("c6", "s60:6"), "op61": ("c4", "s61:4")}
R = (1, 2, 3, 4)
SYN = ("下面是关于同一件事的 {K} 份“因果步骤清单”，来自 {K} 次独立写作，都按同样的段落（{SEG}）展开。这件事（Center）是：{C}\n\n"
       "请综合出一条最好的因果链：\n- 每段 1–4 步，按段落顺序；\n- 优先选更具体、更属于这首曲子、与前后更一致的步骤；可以合并、调整措辞；\n"
       "- 不要把互相矛盾的步骤拼在一起：如果几份清单在某处走向不同，选一条走下去，并让后面的步骤与它一致；\n"
       "- 整条链必须自己推动自己：每一步由前面已经发生的事推出，不靠音乐事件，不编外部事件、物件或对白。\n"
       "只输出一个 ```json 代码块：{\"steps\": [{\"segment\": \"…\", \"because\": \"…\", \"so\": \"…\"}]}\n\n{LISTS}")


def lines(w):
    c = CENTERS[w][0]
    return [f"n8_{w}_{c}_r{j}" for j in R]


if __name__ == "__main__":
    ph = sys.argv[1]; jobs = []
    if ph == "gen":
        for w, (c, s) in CENTERS.items():
            for j in R:
                if not evo.done(f"n8a_{w}_{c}_r{j}"):
                    jobs.append(node2b.job(f"n8a_{w}_{c}_r{j}", node2i.base(w, s) + "\n\n---\n" + node2j.SPINE, {"stage": "n8_spine", "work": w}))
        evo.run_parallel(jobs, 8); jobs = []
        for w, (c, s) in CENTERS.items():
            for j in R:
                sp = evo.output(f"n8a_{w}_{c}_r{j}")
                if sp and not evo.done(f"n8_{w}_{c}_r{j}"):
                    jobs.append(node2b.job(f"n8_{w}_{c}_r{j}", node2i.base(w, s) + "\n\n---\n" + node2j.LAY.replace("{SPINE}", sp), {"stage": "n8", "work": w}))
        evo.run_parallel(jobs, 8)
    elif ph == "inv":
        for w in CENTERS:
            for t in lines(w):
                if not evo.done(f"inv_{t}"):
                    jobs.append((f"inv_{t}", (lambda t=t: evo.call(f"inv_{t}", stepcheck.INV + arts.clean(evo.output(t)), prompt_text=stepcheck.INV, meta={"stage": "step_inventory"}))))
        evo.run_parallel(jobs, 8)
    elif ph == "syn":
        for w, (c, s) in CENTERS.items():
            cen = json.loads((evo.ROOT / "evaluations" / "centers" / f"{s.split(':')[0]}.json").read_text(encoding="utf-8"))[int(s.split(':')[1]) - 1]["center"]
            lists = "\n\n".join(f"========== 清单 {k} ==========\n" + json.dumps(evo.parse_json(evo.output(f"inv_{t}")), ensure_ascii=False, indent=1)
                                for k, t in enumerate(lines(w), 1))
            d = seg.load(w); rng = "、".join(f"{x['start']}–{x['end']}" for x in d["segments"])
            msg = SYN.replace("{K}", "4").replace("{SEG}", rng).replace("{C}", cen).replace("{LISTS}", lists)
            r = evo.call(f"syn_{w}_{c}", msg, prompt_text=SYN, meta={"stage": "synth_chain"})
            chain = "\n".join(f"【{x['segment']}】因为{x['because']}，所以{x['so']}" for x in evo.parse_json(r)["steps"])
            evo.call(f"n8_{w}_{c}_syn", node2i.base(w, s) + "\n\n---\n" + node2j.LAY.replace("{SPINE}", chain),
                     prompt_text=node2j.LAY, meta={"stage": "synth_write", "work": w})
    elif ph == "c1":
        for w, (c, s) in CENTERS.items():
            for t in lines(w) + [f"n8_{w}_{c}_syn"]:
                rid = f"pc_C1_{t}_r1"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, concrete.VAR["C1"].replace("{N}", str(plain.N[w])) + arts.clean(evo.output(t)), {"stage": "concrete", "variant": "C1", "thread": t}))
        evo.run_parallel(jobs, 8)
