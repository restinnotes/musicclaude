"""Filler removal by sentence deletion only (no rewriting). GPT-6 via gpt3; the script verifies that the output
is the input with whole sentences removed (order kept) and reports how much was cut.
usage: python trim.py <name,...> [v1|v2]
  v1: deletion by rules only;  v2: also protects sentences the alignment table marks as 回指/铺垫/thread_only
outputs runs/t_<name>/ (v1) or runs/tv2_<name>/ (v2); evaluations/trim/<name>[_v2].md
"""
import json, re, sys
import arts, evo

OUT = evo.ROOT / "evaluations" / "trim"
SPLIT = re.compile(r"(?<=[。！？!?”」])|\n")


def sents(t):
    return [s.strip() for s in SPLIT.split(t) if s and s.strip()]


def norm(s):
    return re.sub(r"\s", "", s)


def is_deletion(src, out):
    a = [norm(s) for s in sents(src)]; b = [norm(s) for s in sents(out)]
    i = 0; bad = []
    for s in b:
        j = i
        while j < len(a) and a[j] != s:
            j += 1
        if j == len(a):          # not found in order: flag it, but keep the cursor where it was
            bad.append(s); continue
        i = j + 1
    return bad


def protected(n):
    aj = json.loads((evo.ROOT / "evaluations" / "align" / f"{n}.json").read_text(encoding="utf-8"))
    ps = [l["thread_quote"] for s in aj["segments"] for l in s.get("links", []) if l.get("type") in ("回指", "铺垫")]
    ps += [q for s in aj["segments"] for q in s.get("thread_only", [])]
    return list(dict.fromkeys(ps))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1].split(",")
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    tpl = evo.rd(evo.ROOT / "prompts" / f"trim_{ver}.md")
    pre = "t" if ver == "v1" else "tv2"
    src = {n: (arts.b0() if n == "B0" else arts.clean(evo.output(n))) for n in names}
    prot = {n: (protected(n) if ver == "v2" else []) for n in names}
    msgs = {n: tpl.replace("{TEXT}", src[n]).replace("{PROTECT}", "\n".join(f"- {p}" for p in prot[n])) for n in names}
    evo.run_parallel([(f"{pre}_{n}", (lambda n=n: evo.call(f"{pre}_{n}", msgs[n], prompt_text=tpl, meta={"stage": "trim", "version": ver, "source": n})))
                      for n in names], 6)
    for n in names:
        o = evo.output(f"{pre}_{n}")
        if not o:
            print(n, "no output"); continue
        o = arts.clean(o); bad = is_deletion(src[n], o)
        cut = 1 - len(norm(o)) / max(1, len(norm(src[n])))
        kept = set(norm(s) for s in sents(o))
        removed = [s for s in sents(src[n]) if norm(s) not in kept]
        lost = [p for p in prot[n] if norm(p) not in norm(o)]
        suffix = "" if ver == "v1" else "_" + ver
        (OUT / f"{n}{suffix}.md").write_text(
            f"# 删废话（{ver}）：{n}\n\n- 删去 {cut:.0%} 字数；非逐字保留的句子 {len(bad)} 句（应为 0）；受保护但被删的引文 {len(lost)} 条\n\n## 删掉的句子\n\n"
            + "\n".join(f"- {s}" for s in removed) + "\n\n## 删后全文\n\n" + o, encoding="utf-8")
        print(n, f"cut {cut:.0%}", "non-verbatim", len(bad), "protected lost", len(lost))
