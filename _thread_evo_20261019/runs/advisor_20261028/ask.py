"""10-28：把实验结果打包，请 gpt3 上的两位顾问（gpt-6、gpt-5.6）各自独立判断方向。"""
import sys, glob
sys.path.insert(0, "D:/musicclaude/_thread_evo_20261019")
import evo, gpt3_call
from concurrent.futures import ThreadPoolExecutor
A = evo.RUNS / "advisor_20261028"
brief = (A / "brief.txt").read_text(encoding="utf-8")
att = [str(p) for p in sorted(A.iterdir()) if p.suffix in (".txt", ".md") and p.name not in ("brief.txt",)]
print("附件:", [p.split("\\")[-1].split("/")[-1] for p in att], flush=True)
def one(tag, model):
    rid = f"adv20261028_{tag}"; (evo.RUNS / rid).mkdir(exist_ok=True)
    r = gpt3_call.call(rid, brief, None, model, {"stage": "advisor", "attach": att, "web": True})
    (A / f"answer_{tag}.txt").write_text(r or "（没有回答）", encoding="utf-8"); return tag, bool(r)
with ThreadPoolExecutor(2) as ex:
    print(list(ex.map(lambda x: one(*x), [("g6", "gpt-6-thinking"), ("g56", "gpt-5-6-thinking")])), flush=True)
