"""Thread generation runs: prompt version x material condition x segment-clause style x work x repeat.

Every candidate is generated from scratch in a fresh gpt3 (GPT-6 Max) session.
usage: python gen.py <PROMPT_VERSION> <work> <seg_style> <D0,D3,...> <n_repeats> [--workers N]
"""
import argparse, json
import evo, seg

PV = evo.ROOT / "prompt_versions"
DATA = evo.PKG / "02_Bead精简输入"
DFILES = {"D1": "D1_十四段音乐锚点.md", "D2": "D2_十四条主体验.md", "D3": "D3_十四段reader.md", "D4": "D4_五十一条完整Bead.md"}
# Same wrapper for every non-empty condition (from the package's assemble_input.py), so conditions differ only in content.
WRAP = ("\n\n---\n以下是可供核对的额外参考材料（并非必须模仿的文章或固定剧情）。"
        "请优先完成原提示词规定的 Thread 任务；材料只是可参考的局部体验依据。\n\n")


def render(version, work, style):
    d = seg.load(work)
    t = evo.rd(PV / f"{version}.txt").strip()
    return t.replace("{SEG}", seg.clause(d, style)).replace("{WORK_SHORT}", d["short_name"])


def material(cond, work):
    if cond == "D0":
        return ""
    assert work == "op60", "bead materials exist only for op60"
    if cond in DFILES:
        return WRAP + evo.rd(DATA / DFILES[cond]).strip() + "\n"
    p = evo.ROOT / "materials" / f"{cond}.md"   # extra protocols built later (D5, D6, ...)
    return WRAP + evo.rd(p).strip() + "\n"


def message(version, work, style, cond):
    return render(version, work, style) + ("\n" if cond == "D0" else "") + material(cond, work)


def rid(version, work, style, cond, r):
    return f"g_{version}_{work}_{style}_{cond}_r{r}"


def jobs(version, work, style, conds, n):
    out = []
    for r in range(1, n + 1):
        for c in conds:
            i = rid(version, work, style, c, r)
            if evo.done(i):
                continue
            msg = message(version, work, style, c)
            meta = {"stage": "generate", "prompt_version": version, "work": work, "seg_style": style, "condition": c, "repeat": r}
            out.append((i, (lambda i=i, msg=msg, meta=meta: evo.call(i, msg, prompt_text=evo.rd(PV / f"{version}.txt"), meta=meta))))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("version"); ap.add_argument("work"); ap.add_argument("style"); ap.add_argument("conds"); ap.add_argument("n", type=int)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.version == "P0" and a.work == "op60" and a.style == "orig":
        assert render("P0", "op60", "orig") == evo.rd(evo.PKG / "01_提示词与基准" / "P0_纯提示词_直接调用.txt").strip()
    js = jobs(a.version, a.work, a.style, a.conds.split(","), a.n)
    print(f"{len(js)} jobs", flush=True)
    res = evo.run_parallel(js, a.workers)
    print(json.dumps({k: bool(v) for k, v in res.items()}, indent=1))
