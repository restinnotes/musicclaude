"""Node 2 round N8 (user 10-21). N7 made every segment advance the Center and stated the whole matter in the opening:
its spine asked that every change follow from the last, and its lay rules said "重点是这件事此刻走到了哪一步".
Now: per segment the person may be facing the matter, still unable to say what it is, or absorbed in something else
and not thinking of it (no quota); the opening may stay unclear; a passing feeling stays a passing feeling.
Center = the accepted sentence (sel_<w>.json), given as the organising relation seen in hindsight, not a topic he must
address in every segment. Judge: judge_spec_v3, blocks of 3 new lines + the N7 line as anchor (evals C8<60|61>).
ids: n8a_<w>_r<j> (spine), n8_<w>_r<j> (line).  usage: python line8.py lines | judge"""
import json, subprocess, sys
import evo, gen, node2b, node2i, node2j

W = ("op60", "op61")
R = (1, 2, 3)
OLD = {"op60": "n7_op60_IA_c31_r1", "op61": "n7_op61_IA_c31_r1"}

SPINE = ("先不要分段，也完全不要写音乐（不写声音、旋律、主题、调性、节奏、小节）。请用一段连续的文字（约 1000–1500 字）"
         "写出这条线本身：这首曲子里那件属于人的事，从头到尾怎样发生、怎样变化。要求：\n"
         "1. 他每一刻的心理，都要能由前面已经发生在他身上的事说明——先前得到了什么、相信了什么、试过什么、发现了什么；"
         "不要让任何变化“忽然”从外面降临。\n"
         "2. 他不必每一步都在想那件事，也不必每一步都对它有新的认识。开头他可能还说不清自己在意的究竟是什么；"
         "中间也可能有一段时间沉浸在别的感受里，暂时没去想它。这些时候照样要写出他此刻怎样、为什么此刻能这样。"
         "不要为了贴住那件事，给每一步都安排一次进展或领悟。\n"
         "3. 一时的感受就写成一时的感受，不要写成已经成立的认识；还说不清的，不要替他提前说清。\n"
         "4. 这条线的先后要和上面给定的段落先后对应（你心里知道每一步大致落在哪一段），但文字里不提段落、不提音乐。\n"
         "5. " + node2j.NOPLOT + "\n只输出这段文字。")
RULES = ("写法要求（最重要）：\n"
         "1. 全文必须自己读起来就是一条有先后的连续过程。每一段都从上一段结束时这个人所处的状态写起，"
         "写清此刻他怎样、为什么会这样——理由是前面哪一段的什么经历、已经成立的什么认识。\n"
         "2. 音乐事件不能当原因。不要写“此时音乐忽然……于是他……”“新的主题出现，像是他决定……”“到了第X小节，……”。"
         "不要用音乐描写开头一段。音乐每段最多一句，只能作为一个已经说明了来由的状态的外在样子出现；把所有写音乐的句子删掉，文章仍然应当完整连贯。\n"
         "3. 每段的当下体验不必展开（另有专门的记录负责）。这一段他和那件事是什么关系，就如实写什么：可能正在面对它，"
         "可能还说不清，也可能沉浸在别的感受里、暂时没在想它。不要为了贴住那件事，给每一段都安排一次新的进展或领悟。"
         "这一段真正发生得少，就写得短。\n"
         "4. 一时的感受就写成一时的感受，不要写成已经成立的认识；开头还说不清的，不要提前替他说清。\n"
         "5. " + node2j.NOPLOT + "不写前言，直接从第一段写起。\n")
LAY = ("下面是你此前写出的这条线。现在把它落到上面给定的段落上，写成完整的文章。\n\n" + RULES +
       "\n========== 线 ==========\n{SPINE}\n========== 结束 ==========\n")


def center(w):
    return json.loads((evo.ROOT / "evaluations" / "centers" / f"sel_{w}.json").read_text(encoding="utf-8"))[0]["center"]


def base(w):
    p = gen.render("P0", w, "note")
    assert node2i.LAST in p
    return p.replace(node2i.LAST, f"这一次，Thread 所围绕的那件事（Center）是：{center(w)}\n"
                                  "这是读者回头看整首时，把各段组织起来的那件事；不是他一开始就清楚知道的事，也不是每一段都要回应的题目。\n\n"
                     + node2i.LAST)


def names(w):
    return [f"n8_{w}_r{j}" for j in R]


if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "lines":
        evo.run_parallel([node2b.job(f"n8a_{w}_r{j}", base(w) + "\n\n---\n" + SPINE, {"stage": "n8_spine", "work": w})
                          for w in W for j in R if not evo.done(f"n8a_{w}_r{j}")], 6)
        jobs = []
        for w in W:
            for j in R:
                sp = evo.output(f"n8a_{w}_r{j}")
                if sp and not evo.done(f"n8_{w}_r{j}"):
                    jobs.append(node2b.job(f"n8_{w}_r{j}", base(w) + "\n\n---\n" + LAY.replace("{SPINE}", sp), {"stage": "n8", "work": w}))
        evo.run_parallel(jobs, 6)
        print({n: evo.done(n) for w in W for n in names(w)}, flush=True)
    elif ph == "judge":
        import random
        for w in W:   # every judge sees the 3 new lines + the N7 line together, in 2 different orders
            ns = [n for n in names(w) if evo.done(n)] + [OLD[w]]; plan = {}
            for jn in ("gpt6", "gpt56"):
                for s in (1, 2):
                    m = ns[:]; random.Random(f"C8{w}{jn}{s}").shuffle(m)
                    plan[f"s{s}_{jn}"] = {"judge": jn, "map": {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}}
            d = evo.ROOT / "evaluations" / f"C8{w[2:]}"; d.mkdir(parents=True, exist_ok=True)
            (d / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        procs = [subprocess.Popen([sys.executable, "-u", "calib.py", f"C8{w[2:]}", w, "x", "--judge", "judge_spec_v3", "--workers", "4"],
                                  stdout=open(evo.RUNS / f"C8{w[2:]}.log", "w"), stderr=subprocess.STDOUT) for w in W]
        for p in procs:
            p.wait()
