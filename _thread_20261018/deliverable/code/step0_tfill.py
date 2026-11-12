"""Fill independent T research to the same 4-model x int/web x 3 design as A (GPT-6w and GPT-5.6w via gpt3)."""
import shutil
import thr

WORK = "肖邦《船歌》升F大调 Op.60"
P = {"int": (thr.ROOT / "prompts" / "T_int_v2.txt").read_text(encoding="utf-8").replace("{{WORK}}", WORK),
     "web": (thr.ROOT / "prompts" / "T_web_v2.txt").read_text(encoding="utf-8").replace("{{WORK}}", WORK)}
keys = []
for mk, model in (("gpt6w", thr.G6), ("gpt56w", thr.G56)):
    for ch in ("int", "web"):
        for i in (1, 2, 3):
            name = f"T-{mk}-{ch}-{i}"

            def fn(name=name, ch=ch, model=model):
                r = thr.call("tfill", name, P[ch], model=model)
                if r:
                    (thr.INP / "T" / f"{name}.md").write_text(r[0], encoding="utf-8")
                return thr.finish_text("tfill", name, r)
            thr.task("tfill", name, fn, kind="text"); keys.append(("tfill", name))
if __name__ == "__main__":
    thr.run(keys)
