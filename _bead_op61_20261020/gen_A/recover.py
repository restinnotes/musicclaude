"""Parse saved gpt3 stdout (gen.py crashed on a regex typo after the calls returned) into out/<name>.md + meta.json."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent / "out"
for so in sorted(D.glob("*.stdout.bin")):
    name = so.name[:-len(".stdout.bin")]
    if (D / f"{name}.md").exists():
        continue
    try:
        j = json.loads(so.read_bytes().decode("utf-8"))
    except Exception as e:
        print(f"[{name}] unparseable stdout: {e}"); continue
    md = j.get("metadata") or {}
    if not (j.get("completed") is True and j.get("response")):
        print(f"[{name}] NOT COMPLETED"); continue
    meta = {"name": name, "model": md.get("model"), "effort": md.get("thinking_effort"),
            "temporary": md.get("temporary"), "unpersonalized": md.get("unpersonalized"),
            "job_directory": md.get("job_directory")}
    job = Path(md.get("job_directory") or "")
    if (job / "result.json").exists():
        jr = json.loads((job / "result.json").read_text(encoding="utf-8"))
        meta.update(tools_used=jr.get("toolsUsed"), elapsed_seconds=jr.get("elapsed_seconds"))
    (D / f"{name}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (D / f"{name}.md").write_text(j["response"], encoding="utf-8")
    print(f"[{name}] ok {meta['model']}/{meta['effort']} tools={meta.get('tools_used')} {len(j['response'])}ch")
