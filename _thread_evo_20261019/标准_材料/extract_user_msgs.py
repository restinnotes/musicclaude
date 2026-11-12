"""11-02: pull every genuine user message from the Claude transcripts since 10-18, chronological, deduped (resumed
sessions replay earlier turns). Skips tool results, system reminders, compaction summaries, task notifications."""
import json, glob, os, re, sys
from pathlib import Path
D = Path(os.path.expanduser("~/.claude/projects/D--musicclaude"))
seen = {}; out = []
for f in sorted(D.glob("*.jsonl")):
    if f.stat().st_mtime < 1760716800 - 86400 * 1:   # rough: files touched before ~10-17 skipped
        continue
    for line in open(f, encoding="utf-8", errors="replace"):
        try: r = json.loads(line)
        except Exception: continue
        if r.get("type") != "user" or r.get("isMeta") or r.get("isCompactSummary"):
            continue
        c = (r.get("message") or {}).get("content")
        if isinstance(c, list):
            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
        if not isinstance(c, str):
            continue
        t = c.strip()
        if not t or t.startswith(("<system-reminder>", "<task-notification>", "<command-", "<local-command", "This session is being continued", "[SYSTEM NOTIFICATION", "Caveat:")):
            continue
        t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S).strip()
        if not t or len(t) < 2:
            continue
        key = t[:200]
        ts = r.get("timestamp", "")
        if key in seen:
            continue
        seen[key] = ts; out.append((ts, f.stem[:8], t))
out.sort()
P = Path(__file__).with_name("user_msgs_since_1018.md")
with open(P, "w", encoding="utf-8") as fo:
    for ts, s, t in out:
        if ts < "2026-10-18":
            continue
        fo.write(f"### {ts[:16].replace('T', ' ')}  [{s}]\n{t}\n\n")
print(len([o for o in out if o[0] >= "2026-10-18"]), "条", P.stat().st_size // 1000, "KB")
