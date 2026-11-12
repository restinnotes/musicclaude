"""Node 2 round N7 = N6 + no invented plot in the spine (N6 spines invented keys, letters, gatherings, dialogue).
run ids: n7a_<work>_<src>_r<j> (spine), n7_<work>_<IA|IB>_<src>_r<j>"""
import evo, node2b, node2i

NOPLOT = ("不要编造具体的外部事件、物件、场景或对白（例如一次聚会、一封信、一把钥匙、某人说的一句话）来推动变化。"
          "变化只能发生在这个人的所求、相信、理解和承受之中：他先前得到了什么、以为什么、试着怎样对待这件事，"
          "结果发现了什么，于是此刻所求或所信怎样改变。可以有一个从头到尾不变的、很轻的处境作背景，但它不能产生新事件。")
SPINE = node2i.SPINE.replace("只输出这段文字。", NOPLOT + "只输出这段文字。")
RULES = node2i.RULES.replace("4. 不另编情节、对白、物件或人生事件。", "4. " + NOPLOT)
LAY = node2i.LAY.replace(node2i.RULES, RULES)
assert SPINE != node2i.SPINE and RULES != node2i.RULES and RULES in LAY

if __name__ == "__main__":
    works, jobs = ["op60", "op61"], []
    for w in works:
        for name, s in node2i.srcs(w):
            for j in range(1, (2 if name in ("own", "rs") else 1) + 1):
                rid = f"n7a_{w}_{name}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, node2i.base(w, s) + "\n\n---\n" + (node2i.RESEARCH if name == "rs" else "") + SPINE,
                                           {"stage": "n7_spine", "src": name, "work": w}))
        for j in (1, 2):
            rid = f"n7_{w}_IB_own_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, node2i.base(w, "own").replace(node2i.LAST, RULES + "\n" + node2i.LAST),
                                       {"stage": "n7", "variant": "IB", "work": w}))
    print(len(jobs), "first-wave jobs", flush=True)
    evo.run_parallel(jobs, 14)
    jobs = []
    for w in works:
        for name, s in node2i.srcs(w):
            for j in (1, 2):
                sp, rid = evo.output(f"n7a_{w}_{name}_r{j}"), f"n7_{w}_IA_{name}_r{j}"
                if sp and not evo.done(rid):
                    jobs.append(node2b.job(rid, node2i.base(w, s) + "\n\n---\n" + LAY.replace("{SPINE}", sp),
                                           {"stage": "n7", "variant": "IA", "src": name, "work": w}))
    print(len(jobs), "second-wave jobs", flush=True)
    evo.run_parallel(jobs, 14)
