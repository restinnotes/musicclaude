"""Music-fact check of selected articles (GPT-6 Max via gpt3, web allowed). Separate from literary judging.
usage: python mcheck.py <work> <name,...>   (names are run ids, or B0)
"""
import json, sys
import arts, evo, seg

work, names = sys.argv[1], sys.argv[2].split(",")
d = seg.load(work)
tpl = evo.rd(evo.ROOT / "prompts" / "music_check_v1.md")
out = evo.ROOT / "evaluations" / "music"; out.mkdir(parents=True, exist_ok=True)
jobs = []
for n in names:
    text = arts.b0() if n == "B0" else arts.clean(evo.output(n))
    f = out / f"{n}.md"; f.write_text(text, encoding="utf-8")
    msg = tpl.replace("{FILE}", "article.md").replace("{WORK}", d["work"]).replace("{TOTAL}", str(d["total_measures"]))
    a = out / n; a.mkdir(exist_ok=True); af = a / "article.md"; af.write_text(text, encoding="utf-8")
    rid = f"m_{n}"
    jobs.append((rid, lambda rid=rid, msg=msg, af=af: evo.call(rid, msg, prompt_text=tpl, attach=[af], meta={"stage": "music_check"})))
evo.run_parallel(jobs, 6)
rows = {}
for n in names:
    r = evo.output(f"m_{n}")
    if r:
        try:
            rows[n] = evo.parse_json(r)
        except Exception as e:
            print(n, "parse fail", e)
sf = out / f"summary_{work}.json"
summ = json.loads(sf.read_text(encoding="utf-8")) if sf.exists() else {}
summ.update({k: (v.get("summary") or {}) | {"invented": v.get("invented_bars_or_sections")} for k, v in rows.items()})
sf.write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in rows.items():
    print(k, v.get("summary"))
