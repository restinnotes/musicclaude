"""Offline work metadata shared by N02/N03/N04. No model imports or I/O at import time."""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(key, works_root=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
        raise ValueError(f"invalid work key: {key!r}")
    base = Path(works_root or os.environ.get("WORKS_ROOT") or ROOT / "works")
    d = json.loads((base / key / "work.json").read_text(encoding="utf-8"))
    for field in ("composer", "title_zh", "tonality", "opus", "segmentation_source",
                  "specificity_candidates", "specificity_right", "seconds_per_measure", "fix_session"):
        if not d.get(field):
            raise ValueError(f"{key}: missing {field}")
    if d.get("key", key) != key:
        raise ValueError(f"{key}: work.json key mismatch")
    cs = d["specificity_candidates"]
    if not isinstance(cs, list) or len(cs) < 2 or len(set(cs)) != len(cs) or d["specificity_right"] not in cs:
        raise ValueError(f"{key}: candidates must be unique and contain specificity_right")
    if d["fix_session"] not in ("fresh", "resume") or d["seconds_per_measure"] <= 0:
        raise ValueError(f"{key}: invalid fix_session/seconds_per_measure")
    d = dict(d, key=key, _dir=base / key)
    return d


def name(d, with_key=False):
    return d["composer"] + d["title_zh"] + (d["tonality"] + " " if with_key else "") + d["opus"]


def segmentation(d):
    s = json.loads((d["_dir"] / "segmentation.json").read_text(encoding="utf-8"))
    rows = s["segments"]
    end = 0
    for i, row in enumerate(rows, 1):
        if row["id"] != f"S{i:02d}" or row["start"] != end + 1 or row["end"] < row["start"]:
            raise ValueError("segmentation must have consecutive Sxx ids and closed, contiguous ranges")
        end = row["end"]
    if not rows or end != s["total_measures"] or s["boundaries"] != [x["start"] for x in rows] + [end + 1]:
        raise ValueError("segmentation boundaries/total_measures disagree")
    return s


def chinese_number(n):
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n < 100:
        return (digits[n // 10] if n >= 20 else "") + "十" + (digits[n % 10] if n % 10 else "")
    return str(n)


def values(d, s=None):
    s = s or segmentation(d)
    n = chinese_number(len(s["segments"]))
    source = d["segmentation_source"]
    return {"WORK": name(d), "WORK_WITH_KEY": name(d, True), "COMPOSER": d["composer"],
            "SEGMENTATION_SOURCE": source + "冻结" + n + "段",
            "SEGMENTATION_LIST_SOURCE": source + "冻结的" + n + "段", "NSEG_ZH": n}


def replace(text, params):
    # One pass: never reinterpret placeholders appearing in quoted model/source text.
    return re.sub(r"\{([A-Z_]+)\}", lambda m: str(params.get(m[1], m[0])), text)


def render(text, d, s=None):
    return replace(text, values(d, s))


def source_dir(d):
    return Path(d.get("a_sources") or d["_dir"] / "A")


def selected(default=("op60", "op61"), work=None):
    value = work or os.environ.get("WORK")
    return value.split(",") if value else list(default)


def write_prompts(directory, prompts):
    """Exclusive output, so offline checks cannot overwrite historical evidence."""
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    for filename, text in prompts.items():
        with (out / filename).open("x", encoding="utf-8", newline="\n") as f:
            f.write(text)
