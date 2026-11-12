import re, json

t = open("D:/musicclaude/_bead_auto_20261016/out/STEP3_response_raw_b1.md", encoding="utf-8").read()
m = re.search(r"<CodeBlock[^>]*>(.*?)</CodeBlock>", t, re.S)
print("b1 match" if m else "b1 NOMATCH", len(m.group(1)) if m else 0)
d = json.loads(m.group(1))
print("b1 keys:", list(d.keys()))
json.dump(d, open("D:/musicclaude/_bead_auto_20261016/out/STEP3_parsed_b1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# count refs
tot = 0
for k, v in d.items():
    if isinstance(v, dict):
        for kk, vv in v.items():
            tot += len(vv)
    else:
        tot += len(v)
print("b1 total refs:", tot)
# unique unit ids
ids = set()
def walk(o):
    if isinstance(o, str) and re.fullmatch(r"A0\d-U\d+", o):
        ids.add(o)
    elif isinstance(o, list):
        for x in o:
            walk(x)
    elif isinstance(o, dict):
        for x in o.values():
            walk(x)
walk(d)
print("b1 unique units:", len(ids))
