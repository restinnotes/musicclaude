"""Calibrate synth.py's B check (PLAN_解释池_20261023.md 六-1 step 2) on segments whose verdict is already settled:
negatives the user or the ChatGPT review called out, positives they singled out. Each case gives the check the same
inputs it gets in synth.py (History with what each item explained, the segment's beads, the chosen text).
Pass = every negative fails and every positive passes, with a reason that names the known problem.
ids: cs_<case>_<judge>.  usage: python calib_synth.py"""
import json
import evo, node2b, synth

H = lambda *xs: [{"id": f"H{i + 1}", "sec": s, "text": t, "explains": e} for i, (s, t, e) in enumerate(xs)]
CASES = {
    # negatives
    "v7_S01": ("S01", [], "心里的愿望比他平日允许自己的更深，令他有些迟疑。过去，他总能及时收手，既尝到快乐，也知道自己还管得住欲望；所以眼下，他格外在意自己还能不能停下。",
               False, "编出过去的习惯与性格"),
    "60e_S02": ("S02", H(("S01", "他心里有份说不清指向何处的期待，连自己也不知道究竟在盼什么。", ["S01-B1"])),
                "那份模糊的盼望在亲近中初次有了方向，因此他尝到温柔的满足。", False, "抽象，说不清为什么"),
    "60e_S03": ("S03", H(("S01", "他心里有份说不清指向何处的期待，连自己也不知道究竟在盼什么。", ["S01-B1"]),
                         ("S02", "那份模糊的盼望在亲近中初次有了方向，他尝到温柔的满足。", ["S02-B1"])),
                "刚才的满足让他浑身放松，心头也松快，只静静享受眼前的惬意。", False, "漏掉暗流与急切"),
    "60e_S04": ("S04", H(("S01", "他心里有份说不清指向何处的期待。", ["S01-B1"]), ("S02", "期待在亲近中有了方向，他尝到温柔的满足。", ["S02-B1"]),
                         ("S03", "满足之后他浑身放松，静静享受眼前的惬意。", ["S03-B1"])),
                "轻松片刻后，熟悉的亲近再现，他更想把心意放深些。喜欢得更深，让他感到畅快，亲近也像唤醒了他更多活力。", False, "只说结果，没有机制"),
    "r6_S02": ("S02", H(("S01", "有句话忽然快到嘴边，他想到对方或许会听懂，心里一亮，又怕被听得太重；他把话留在心里，因为眼下的自在也很珍贵。", ["S01-B2"])),
               "那句话安静地留着，他渐渐敢享受对方的亲近，心里竟比刚才还要轻松。他真想多待一会儿，心里一阵发热，又为时间正在过去而发酸。",
               False, "把听感里的比喻（话到嘴边）写成他身上真有一句话"),
    "n8_S04": ("S04", H(("S02", "他尝到亲近带来的满足，开始相信这份亲近是真的。", ["S02-B1"]),
                        ("S03", "尝过满足后，他开始盼望更多，心里添了一点想确认对方心意的紧张。", ["S03-B2", "S03-B3"])),
               "他不愿因为这点紧张破坏先前的快乐，于是提醒自己，真正珍惜一个人并不是凡事都要得到相应的表示；这样一想，他真的轻松起来，更愿意付出，甚至相信只要不提出要求，就可以尽情地爱，也不会失去什么。",
               False, "自我开导的心理故事，没解释迫切与握紧"),
    # positives
    "60d_S04": ("S04", H(("S01", "他心里生出想靠近某个人的愿望，却说不清自己究竟在期待什么。", ["S01-B2"]),
                         ("S02", "亲近的可能越显珍贵，他越不忍它转瞬即逝；期待也渐渐成了盼这份亲近长久。", ["S02-B1", "S02-B4"]),
                         ("S03", "亲近带来的留恋让他静静沉浸在期待里。", ["S03-B1"])),
                "先前的满足让他更珍惜这份亲近；越享受其中，他越舍不得它结束，欢喜里也添了急切。", True, ""),
    "60f_S04": ("S04", H(("S01", "心里像少了些什么，让他隐约觉得在等着什么，却说不清究竟是什么。", ["S01-B1"]),
                         ("S02", "亲近让无名的等待有了方向，欢喜里有些酸涩。", ["S02-B1", "S02-B4"]),
                         ("S03", "亲近已带来真实欢喜，此刻他享受着靠近本身。", ["S03-B1"])),
                "亲近带来的欢喜已如此真切，他开始舍不得这一刻过去，温柔里生出急切。", True, ""),
    "d9L_S05": ("S05", H(("S02", "他尝过亲近带来的安慰。", ["S02-B1"]), ("S03", "满足之后，更深的所求并没有因此消失。", ["S03-B3"]),
                         ("S04", "第二次的亲近让他更投入，也更清楚自己还想要更多。", ["S04-B1"])),
                "原有的满足不再够用，而别的可能还不能成为依靠，所以心里一下子空落、悬着，有一点孤单。", True, ""),
}


def pick_of(text):
    return {"chosen": [{"text": text, "depends": [], "explains": []}], "fate": {}, "new_history": []}


if __name__ == "__main__":
    r = synth.Run("calib", "op60", "g6", "none")
    jobs, msgs = [], {}
    for k, (sec, hist, text, _, _) in CASES.items():
        r.state = {}
        if hist:
            r.state["S00"] = {"hist": hist}
            r.history = lambda upto, hist=hist: hist
        else:
            r.history = lambda upto: []
        msgs[k] = r.check_msg(sec, pick_of(text))
        for j in ("g6", "g56"):
            if not evo.done(f"cs_{k}_{j}"):
                jobs.append(node2b.job(f"cs_{k}_{j}", msgs[k], {"stage": "calib_synth", "case": k}, w=j))
    evo.run_parallel(jobs, 18)
    ok = 0; n = 0
    for k, (sec, _, _, want, why) in CASES.items():
        for j in ("g6", "g56"):
            try:
                v = evo.parse_json(evo.output(f"cs_{k}_{j}"))
            except Exception:
                print(k, j, "parse fail"); continue
            n += 1; hit = bool(v.get("pass")) == want; ok += hit
            print(f"{'✓' if hit else '✗'} {k:8} {j:4} pass={v.get('pass')} 应为{want} {why} | {(v.get('reason') or '')[:110]}")
    print(f"{ok}/{n} correct")
