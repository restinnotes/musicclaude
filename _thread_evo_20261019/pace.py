"""10-27 deadline pacer (user: finish everything within 8 hours, measure speed live and get more aggressive if slow).
Every 10 min: per piece, committed segments of synth P3a, minutes per segment, projected finish; if the later piece is
projected after SYNTH_DUE, raise gpt3 slots by one (runs/gpt3_slots.txt, max 4). One line per tick = one monitor event."""
import json, time
from datetime import datetime
from pathlib import Path
import draft10

ROOT = Path(__file__).resolve().parent
SYNTH_DUE = datetime(2026, 10, 27, 9, 15)
SLOTS = ROOT / "runs" / "gpt3_slots.txt"


def status(w):
    d = ROOT / "evaluations" / "synth" / f"P3a_{w}"
    segs = [x["id"] for x in draft10.segs(w)]
    done = [s for s in segs if (d / f"{s}.json").exists()]
    first = ROOT / "runs" / f"syP3a_{w}_S01_A" / "input.txt"
    return len(done), len(segs), first.stat().st_mtime if first.exists() else None


while True:
    now = time.time(); parts = []; late = False
    for w in ("op60", "op61"):
        n, tot, t0 = status(w)
        if n >= 1 and t0:
            per = (now - t0) / n
            eta = datetime.fromtimestamp(now + per * (tot - n) + 30 * 60)      # +30 min for global checks / back-tracks
            late |= eta > SYNTH_DUE
            parts.append(f"{w} {n}/{tot} {per / 60:.0f}分/段 预计{eta:%H:%M}")
        else:
            parts.append(f"{w} {n}/{tot}")
            late |= n == 0 and datetime.now() > datetime(2026, 10, 27, 4, 30)
    slots = int(SLOTS.read_text().strip()) if SLOTS.exists() else 1
    msg = f"[{datetime.now():%H:%M}] " + "；".join(parts) + f"；gpt3并发{slots}"
    if late and slots < 4:
        slots += 1; SLOTS.write_text(str(slots)); msg += f" → 偏慢，并发提到{slots}"
    elif late:
        msg += " → 偏慢且并发已到上限，需要人工处理"
    print(msg, flush=True)
    time.sleep(600)
