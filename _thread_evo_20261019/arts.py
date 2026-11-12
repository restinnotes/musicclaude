"""Article normalization for blind reading: strip ChatGPT canvas markup, keep the text exactly otherwise."""
import re, glob
import evo


def clean(t):
    t = re.sub(r"<WritingBlock[^>]*>", "", t); t = t.replace("</WritingBlock>", "")
    t = re.sub(r"<text[^>]*>(.*?)</text>", r"\1", t, flags=re.S)
    t = re.sub(r"</?[a-zA-Z][^>]*>", "", t)
    t = re.sub(r"\s*【turn\d+\w*】", "", t)          # web-search citation markers
    return t.strip() + "\n"


def b0():
    t = evo.rd(evo.PKG / "01_提示词与基准" / "B0_成功范例_水面从来不答应静止.md")
    i = t.index("这篇 Thread 将围绕")       # drop the package's own title + provenance note
    return clean(t[i:])


def pool(patterns):
    out = {}
    for pat in patterns:
        for d in sorted(glob.glob(str(evo.RUNS / pat))):
            p = evo.RUNS / d / "output.txt"
            if p.exists():
                out[d.replace("\\", "/").split("/")[-1]] = clean(evo.rd(p))
    return out
