import re, json

BASE = "D:/musicclaude/music_work_since_1008v3_20261009/runs"
FILES = {
 "A01": ("run106_gpt56_material/outputs/A-int__A_int_v1__gpt56w__op60__s1.md", r"^### mm\. "),
 "A03": ("run115_facts/outputs/A-int__A_int_v1f__gflash__op60__s1.md", r"^### 第.{1,4}阶段"),
 "A04": ("run115_facts/outputs/A-int__A_int_v1f__muse__op60__s1.md", r"^\*\*mm\."),
 "A05": ("run32_opus_sol/outputs/A-int__A_int_v1__opus__op60__s1.md", r"^## \d+\. "),
 "A06": ("run40_grok/outputs/A-int__A_int_v1__grok__op60__s1.md", r"^\*\*mm\. "),
}
for uid, (rel, pat) in FILES.items():
    txt = open(f"{BASE}/{rel}", encoding="utf-8").read()
    lines = txt.split("\n")
    idx = [i for i, l in enumerate(lines) if re.match(pat, l.strip())]
    print(f"===== {uid} {rel.split('/')[-1]}: {len(idx)} sections =====")
    for k, i in enumerate(idx):
        end = idx[k+1] if k+1 < len(idx) else len(lines)
        body = "\n".join(lines[i:end])
        print(f"--- sec{k} line{i}: {lines[i][:90]!r} chars={len(body)}")
    pre = "\n".join(lines[:idx[0]]) if idx else txt
    print(f"### preamble chars={len(pre)} head={pre[:120]!r}")
