"""Node 2 round D9 (user 10-23, PLAN_逐段构建线_20261023.md step 1b). Drafting still sees no beads. The N8 drafts invented
psychological plot (17–39: expects -> talks himself out of it -> relaxes -> finds he still wants -> doubts), and four parts of
the N8 prompt plausibly push that way: a spine written with no music at all, then laid on the segments; "试过什么、发现了什么"
in the spine rule and in NOPLOT; the five accumulation kinds read as plot templates; a Center fixed in advance.
Two corrected variants, no Center given:
  L (甲, listen): one call, segment by segment; first the feeling of this segment in one line, then why he feels it now,
                  the reason only from his earlier experience (music never the reason).
  S (乙, spine) : keeps N8's two calls (music-free spine -> lay on segments) with only the inducing rules replaced.
ids: d9L_<w>_r<j>, d9Sa_<w>_r<j> (spine), d9S_<w>_r<j>.  usage: python draft9.py [L|S|all]"""
import sys
import evo, gen, node2b

W = ("op60", "op61")
R = (1, 2, 3)

NOPLOT = ("不要编造具体的外部事件、物件、场景或对白（例如一次聚会、一封信、一把钥匙、某人说的一句话）来推动变化。"
          "变化只发生在这个人心里。可以有一个从头到尾不变的、很轻的处境作背景，但它不能产生新事件。")
PLAIN = ("一个理由能说清，就不要拆成几步。一段里可以没有新的变化，只是前面感受的延续、加深或再次出现。\n"
         "不要靠心理动作推动故事：劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心——只有这一段的感受非它不能解释时才写。\n"
         "上面列的几种“理解的积累”只是参考，不必用。\n")

L_RULES = ("---\n写法要求：\n"
           "1. 按上面的分段逐段写。每段先用一行写出这一段音乐让人感受到的是什么（以“感受：”开头，一句话），"
           "再写他为什么此刻会有这种感受（以“为什么：”开头）。理由只能来自前面已经发生在他身上的事；"
           "音乐的变化不能当理由，不写“音乐忽然……于是他……”。\n"
           "2. " + PLAIN.replace("\n", "\n   ").rstrip() + "\n"
           "3. " + NOPLOT + "\n"
           "4. 用普通人一遍就能听懂的话。不写前言，直接从第一段写起。\n")

S_SPINE = ("先不要分段，也完全不要写音乐（不写声音、旋律、主题、调性、节奏、小节）。请用一段连续的文字（约 1000–1500 字）"
           "写出这条线本身：这首曲子里那件属于人的事，从头到尾怎样发生、怎样变化。要求：\n"
           "1. 他每一刻的心理，都要能由前面已经发生在他身上的事说明；不要让任何变化“忽然”从外面降临。\n"
           "2. 他不必每一步都在想那件事。开头他可能还说不清自己在意的究竟是什么；中间也可能有一段时间沉浸在别的感受里，暂时没去想它。\n"
           "3. " + PLAIN.replace("\n", "\n   ").rstrip() + "\n"
           "4. 一时的感受就写成一时的感受，不要写成已经成立的认识；还说不清的，不要替他提前说清。\n"
           "5. 这条线的先后要和上面给定的段落先后对应，但文字里不提段落、不提音乐。\n"
           "6. " + NOPLOT + "\n只输出这段文字。")
S_RULES = ("写法要求（最重要）：\n"
           "1. 全文自己读起来是一条有先后的连续过程。每一段写清此刻他怎样、为什么会这样——理由来自前面已经发生在他身上的事。\n"
           "2. 音乐事件不能当原因。不要写“此时音乐忽然……于是他……”“到了第X小节，……”。音乐每段最多一句，只能作为一个已经说明了来由的状态的外在样子出现。\n"
           "3. " + PLAIN.replace("\n", "\n   ").rstrip() + " 这一段真正发生得少，就写得短。\n"
           "4. 一时的感受就写成一时的感受，不要写成已经成立的认识。\n"
           "5. " + NOPLOT + "不写前言，直接从第一段写起。\n")
S_LAY = ("下面是你此前写出的这条线。现在把它落到上面给定的段落上，写成完整的文章。\n\n" + S_RULES +
         "\n========== 线 ==========\n{SPINE}\n========== 结束 ==========\n")


def base(w):
    return gen.render("P0", w, "note")


if __name__ == "__main__":
    ph = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = []
    if ph in ("L", "all"):
        jobs += [node2b.job(f"d9L_{w}_r{j}", base(w) + "\n\n" + L_RULES, {"stage": "d9L", "work": w})
                 for w in W for j in R if not evo.done(f"d9L_{w}_r{j}")]
    if ph == "LC":   # isolation cell (user 10-23 asked whether the N8 Center itself drives the back-and-forth): L rules + N8's Center
        import line8
        jobs += [node2b.job(f"d9LC_{w}_r{j}", line8.base(w) + "\n\n" + L_RULES, {"stage": "d9LC", "work": w})
                 for w in W for j in R if not evo.done(f"d9LC_{w}_r{j}")]
    if ph in ("S", "all"):
        jobs += [node2b.job(f"d9Sa_{w}_r{j}", base(w) + "\n\n---\n" + S_SPINE, {"stage": "d9S_spine", "work": w})
                 for w in W for j in R if not evo.done(f"d9Sa_{w}_r{j}")]
    evo.run_parallel(jobs, 12)
    if ph in ("S", "all"):
        jobs = [node2b.job(f"d9S_{w}_r{j}", base(w) + "\n\n---\n" + S_LAY.replace("{SPINE}", evo.output(f"d9Sa_{w}_r{j}")),
                           {"stage": "d9S", "work": w})
                for w in W for j in R if evo.done(f"d9Sa_{w}_r{j}") and not evo.done(f"d9S_{w}_r{j}")]
        evo.run_parallel(jobs, 6)
    print({f"{v}_{w}_r{j}": evo.done(f"{v}_{w}_r{j}") for v in ("d9L", "d9S") for w in W for j in R}, flush=True)
