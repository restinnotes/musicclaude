import re, json, sys

def extract(n):
    p = f"D:/musicclaude/_bead_auto_20261016/out/STEP3_response_raw_{n}.md"
    t = open(p, encoding="utf-8").read()
    if n == "A07":
        m = re.search(r"```json(.*?)```", t, re.S)
    else:
        m = re.search(r"<CodeBlock[^>]*>(.*?)</CodeBlock>", t, re.S)
    print(n, "match" if m else "NOMATCH", len(m.group(1)) if m else 0)
    if not m:
        return
    try:
        d = json.loads(m.group(1))
    except Exception as e:
        print(n, "JSONERR", str(e)[:300])
        return
    print(n, "keys:", list(d.keys()))
    json.dump(d, open(f"D:/musicclaude/_bead_auto_20261016/out/STEP3_parsed_{n}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "saved")

for n in ["A07", "A08"]:
    extract(n)
