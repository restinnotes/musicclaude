"""10-29 gate before calling the user (user: "你每次迭代到你觉得可以交付之前 都要开一个gpt3的新对话问他 相较于v6 有没有出问题
然后我们的三个问题有没有改善 （当然你珠子关系图也要给他）直到说大致可用了再给我").
Fresh gpt3 conversations (gpt-6 and 5.6, max). Attachments: the user's 10-29 ChatGPT conversation (tool calls and code blocks
removed, so it reads as the discussion), and a zip with v6, the repaired line, the bead graphs, the joined product and the blind
regression check. Both "结论：大致可用" -> call the user; otherwise keep fixing what they point at.
ids: gatev6_<T>_<j>.  usage: python gate_v6.py <T> -> reviews/交付前评定_v6修补_<T>.md"""
import re, shutil, sys, zipfile
import evo, v6fix as V

SRC = evo.ROOT / "reviews" / "chatgpt-分析问题解决方法-20261029.md"
CLEAN = evo.ROOT / "reviews" / "chatgpt-分析问题解决方法-20261029_对话正文.md"
ASK = ("附件一是我和 ChatGPT 关于这个项目的对话记录（去掉了工具调用），请通读，尤其是最后一部分：我们定下的三个问题"
       "（P1 覆盖率不足、P2 啰嗦废话、P3 不说人话），以及在 v6 的基础上修补的方向。"
       "附件二是这一轮的结果：v6 原线的关系图、在 v6 上修补后的新线关系图、两首曲子的珠子关系图、新线和珠子结合后的成品，以及新线和 v6 的匿名盲评记录、v6 好内容固定清单的逐条核对、新线和 v6 各自的珠子覆盖逐颗判定。"
       "请说清楚：1. 新线相较于 v6 有没有出问题——有没有丢掉 v6 已经说清的好内容，有没有新的毛病；2. 三个问题各自有没有改善，举具体段落；"
       "3. 用户后来又补了两点要求，请一并判断：线单独拿出来、不看珠子，自己读下来要成立（每段他此刻为什么这样，前因在线里看得出来），不能只是在翻译珠子；"
       "目标是一篇文章用最少的人话把所有珠子解释清楚——覆盖、不啰嗦、说人话、线自己站得住，这四点不是此消彼长的，要同时做到；"
       "4. 现在大致可不可用。不必完美。最后单独一行写“结论：大致可用”或“结论：不可用”。")


def clean_chat():
    if CLEAN.exists():
        return CLEAN
    s = SRC.read_text(encoding="utf-8")
    parts = re.split(r"\n(?=## (?:You|ChatGPT|tool:[^\n]*) — )", s)
    out = []
    for p in parts:
        if p.startswith("## tool:"):
            continue
        if p.startswith("## ChatGPT"):
            head, _, body = p.partition("\n")
            body = re.sub(r"```.*?```", "", body, flags=re.S)
            body = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith(('{"path"', "> [container", "> ```")))
            if not body.strip():
                continue
            p = head + "\n" + body
        out.append(p.strip())
    CLEAN.write_text("\n\n".join(out), encoding="utf-8")
    return CLEAN


def package(T):
    d = evo.ROOT / "reviews" / f"v6修补_{T}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    v6dir = evo.ROOT / "deliverable" / "thread_v6"; bg = evo.ROOT / "deliverable" / "bead_graph"
    for w, W in (("op60", "Op60"), ("op61", "Op61")):
        shutil.copy(v6dir / f"{W}_关系图.md", d / f"01_v6_{W}_关系图.md")
        shutil.copy(V.OUT / f"{w}_{T}.md", d / f"02_新线_{W}_关系图.md")
        shutil.copy(bg / f"{W}_珠子图.md", d / f"03_珠子关系图_{W}.md")
    shutil.copy(V.OUT / f"成品_线与珠子关系图_{T}.md", d / "04_成品_新线与珠子结合.md")
    for f in (V.OUT / f"blind_{T}.md",):
        if f.exists():
            shutil.copy(f, d / "05_回退检查_和v6匿名盲评.md")
    for src, dst in ((V.OUT / f"checklist_{T}.md", "06_回退检查_v6好内容固定清单逐条核对.md"),
                     (V.OUT / f"cov_{T}.md", "07_珠子覆盖_新线逐颗判定.md"), (V.OUT / "cov_v6.md", "07b_珠子覆盖_v6逐颗判定_对照.md"),
                     (V.OUT / f"alone_{T}.md", "08_线单独读_与复述珠子判定.md"), (V.OUT / "alone_v6.md", "08b_线单独读_v6对照.md")):
        if src.exists():
            shutil.copy(src, d / dst)
    (d / "00_说明.md").write_text(
        "# 这一轮是什么\n\n"
        "- 01：v6 原线关系图（10-21 用户整体认可方向的版本；✦ 是当时的内部标签）。\n"
        "- 02：在 v6 上逐段修补后的新线。形式同 v6：Center 不改；每段标他和 Center 的关系；→ 段内由上一条引出；← 指回前面某段的某一条；⟲ 前面仍在起作用的。"
        "新线不再显示 ✦ 标签。\n"
        "- 03：珠子关系图（逐字原文，未改动）。\n"
        "- 04：新线和珠子结合：每屏是线的条目和它说明的珠子条目。\n"
        "- 05：新线和 v6 的匿名盲评（gpt-6、5.6，随机顺序），逐段比 覆盖 / 啰嗦 / 人话，并列出两个方向各丢了什么。\n"
        "- 06：回退检查的固定清单：两位诊断评审列出的 v6 实质好内容合并成一份清单，两位评委逐条判 保留 / 更好地取代 / 丢失。\n"
        "- 07 / 07b：珠子覆盖的绝对数：评委只看一版线和全部珠子，逐颗判 说清 / 偏弱 / 相反 / 没有；07b 是 v6 用同一把尺子的结果。\n"
        "- 08 / 08b：线单独读：评委只拿到线（没有珠子），判每段此刻的原因是否成立、每条是原因还是描写、箭头是否必要；另一次对照珠子逐条判 自己的原因 / 复述珠子 / 两者都有。\n\n"
        "新线是怎么来的（底稿始终是 v6，Center 不改）：\n"
        "1. w2：v6 整首一次修补。输入 v6 全曲、两首珠子、两位评审对 v6 的逐段诊断（P1 覆盖 / P2 啰嗦 / P3 人话 / 值得保留的内容）；之后逐段核对（越界、箭头前因、不看珠子能否读懂、有没有丢 v6 的实质内容），再整首退改一次。\n"
        "2. w3、w4：在上一轮基础上，按“和 v6 匿名盲评”列出的“新版丢了 v6 的内容”整首再修。\n"
        "3. w5 起：只对仍丢着内容的段落逐段聚焦重修（每段一次调用，看 v6 全曲、前面各段、这一段 v6 原样和珠子、要找回的内容），其余段沿用上一轮；w6 按上一次交付前评定的意见再逐段重修。\n"
        "4. w20–w24：按分段排序评比和重复盲评，逐段在候选之间挑，找回被反复点名丢掉的 v6 内容（上一次交付前评定两位都“大致可用”）。\n"
        "5. 之后针对用户新提的“线要自己站得住、不翻译珠子、用更少的话”：试过只删复述（w27，覆盖掉了）、先列原因再写（w30，变抽象、覆盖掉了）、"
        "以 w24 为底逐段只删真正重复的部分（w31，接成长句、箭头过多），之后的轮次在此基础上守住 v6 的短条目形式。\n"
        "所以文件标题里的 w 编号指的是第几轮新线，它们都是从 v6 修来的。\n", encoding="utf-8")
    zp = evo.ROOT / "reviews" / f"v6修补_{T}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(d.iterdir()):
            z.write(f, f"v6修补_{T}/{f.name}")
    return zp


def main(T):
    chat = clean_chat(); zp = package(T)
    ask = ASK if (V.OUT / f"blind_{T}.md").exists() else ASK.replace("以及新线和 v6 的匿名盲评记录、", "以及（这一轮和 v6 的匿名盲评在另外进行，不在包里）")
    jobs = [(rid, (lambda rid=rid, m=m: evo.call(rid, ask, prompt_text=ask, model=m, meta={"stage": "gate-v6", "attach": [str(chat), str(zp)]})))
            for j, m in V.JUDGES.items() for rid in [f"gatev6_{T}_{j}"] if not evo.done(rid)]
    evo.run_parallel(jobs, 2)
    out, ok = [f"# 交付前评定：v6 修补 {T}", "", f"对话记录：{chat.name}", f"包：{zp.name}", ""], []
    for j in V.JUDGES:
        r = evo.output(f"gatev6_{T}_{j}") or "（没有返回）"
        ok.append("结论：大致可用" in r.replace(" ", "").replace("**", ""))
        out += [f"## {'gpt-6' if j == 'g6' else 'gpt-5.6'}", "", r, ""]
    fn = evo.ROOT / "reviews" / f"交付前评定_v6修补_{T}.md"
    fn.write_text("\n".join(out), encoding="utf-8")
    print("两位都大致可用" if all(ok) else f"没过：{ok}", "->", fn, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
