import evo
from pathlib import Path
msg = Path("deliver_20261031_人话层/gpt_review_prompt_inline.txt").read_text(encoding="utf-8")
r = evo.call("rv_f8_h13", msg, model=evo.G6, meta={"stage": "review-f8-vs-h13"})
if r:
    Path("deliver_20261031_人话层/GPT总结_f8到h13.md").write_text("# GPT-6（mimicgate，High）总结：f8 → h13\n\n" + r, encoding="utf-8")
print("OK" if r else "FAILED")
