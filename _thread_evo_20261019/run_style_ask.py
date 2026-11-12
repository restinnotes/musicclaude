import evo
from pathlib import Path
q = Path("runs/style_question.txt").read_text(encoding="utf-8")
jobs = [("sty_g6", lambda: evo.call("sty_g6", q, model=evo.G6, meta={"stage": "style_ask"})),
        ("sty_g56", lambda: evo.call("sty_g56", q, model=evo.G56, meta={"stage": "style_ask"})),
        ("sty_gem", lambda: evo.call_gemini_direct("sty_gem", q, meta={"stage": "style_ask"})),
        ("sty_argon", lambda: evo.call_argon_direct("sty_argon", q, meta={"stage": "style_ask"}))]
evo.run_parallel(jobs, 4)
for r in ("sty_g6", "sty_g56", "sty_gem", "sty_argon"):
    print(r, evo.done(r), len(evo.output(r) or ""))
