import ast, json, os, re
ast.parse(open("pipe.py", encoding="utf-8").read()); print("pipe.py 语法正常")
os.environ["JV"] = "2"
import evo
raw = re.sub(r"\\(\r?\n)", r"\1", (evo.output("scqr_op61_A1") or "").replace("&#x20;", " "))
raw = re.sub(r"\\([\[\]_*`~])", r"\1", raw)
o = json.loads(raw.strip().rstrip("\\").strip())
print(type(o).__name__, len(o), [r.get("route_id") for r in o])
for r in o:
    print("-", r["situation"])
