"""11-02: package the deliverable for the user: 只看线 + 合写 for each named version, the progress table, the prompts. usage: python runs/_deliver.py <dir name> <tag:label> ...  (run from the project root)"""
import os, re, shutil, sys, zipfile
from pathlib import Path
os.environ["JV"] = "2"
sys.path.insert(0, ".")
import v6fix as V

out = Path(sys.argv[1]); out.mkdir(exist_ok=True)
for arg in sys.argv[2:]:
    tag, label = arg.split(":")
    txt = [f"# {label}（版本 {tag}）只看线", ""]
    for w in ("op60", "op61"):
        txt += [f"## {'《船歌》Op.60' if w == 'op60' else '《幻想波兰舞曲》Op.61'}", "", V.view(V.graph_of(w, tag), center=True), ""]
    (out / f"{label}_只看线.md").write_text("\n".join(txt), encoding="utf-8")
    for w in ("op60", "op61"):
        p = V.OUT / f"合写_{w}_{tag}.md"
        if p.exists():
            shutil.copy(p, out / f"{label}_合写_{w}.md")
for f in ("进度表.md",):
    text = Path(f).read_text(encoding="utf-8")
    for p in ("evaluations/", "schemes/"):
        text = text.replace(f"]({p}", f"](../{p}")
    text = re.sub(r"\]\(([A-Za-z][A-Za-z0-9_]*\.py)\)", r"](../\1)", text)
    for name in ("DAG.md", "试验记录.md", "标准.md", "迭代准则.md", "STATUS.md", "VERSIONS.md"):
        text = text.replace(f"]({name})", f"](../{name})")
    (out / f).write_text(text, encoding="utf-8")
zp = Path.home() / "Downloads" / f"{out.name}.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(out.iterdir()):
        z.write(f, f"{out.name}/{f.name}")
print(out, "->", zp, [f.name for f in sorted(out.iterdir())])
