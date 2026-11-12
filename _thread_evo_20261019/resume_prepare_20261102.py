"""只恢复网关转义，校验顾问提示词接口并保存独立候选，不改写提示词内容。"""
import copy
import json
import re

import evo
import pipe
from resume_20261102 import ROOT

NAMES = {"gem": "R26G", "g6": "R26T"}


def prepare(who, name):
    text = evo.output(f"resume20261102_{who}_repair1")
    assert text
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        normalized = re.sub(r"\\\r?\n", "\n", text.replace("&#x20;", " "))
        try:
            data = json.loads(normalized)
        except json.JSONDecodeError:
            data = json.loads(normalized.replace(chr(92) * 2 + '"', chr(92) + '"'))
    files = data["files"]
    original = pipe.load_spec(ROOT / "schemes/Q15.json")
    allowed = {s["prompt_file"] for s in original["steps"]}
    assert files and set(files) <= allowed
    for old, tokens in {
        "Q6_A1.txt": ("{NAME}", "{SECTIONS}", "{CENTER}", "{K}"),
        "Q15_A4.txt": ("{SECTIONS}", "{CENTER}", "{ROUTES}", "{TARGETS}"),
    }.items():
        if old in files:
            assert all(t in files[old] for t in tokens), (who, old, "占位符缺失")
    for body in files.values():
        assert not re.search(r"肖邦|船歌|幻想波兰|Op\.?\s*6[01]|S07|第\s*7\s*段", body, re.I)
    spec = {k: copy.deepcopy(v) for k, v in original.items() if not k.startswith("_")}
    spec["name"] = name
    spec["note"] = f"2026-11-02 接续：{who} 原提出者修正版，以 qu 为比较基准"
    for step in spec["steps"]:
        old = step["prompt_file"]
        if old in files:
            target = ROOT / "schemes" / f"{name}_{step['id']}.txt"
            assert not target.exists(), target
            target.write_text(files[old].rstrip() + "\n", encoding="utf-8")
            step["prompt_file"] = target.name
    target = ROOT / "schemes" / f"{name}.json"
    assert not target.exists(), target
    target.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    pipe.load_spec(target)
    print(name, "接口通过", "改动层", list(files), "理由", data["analysis"], flush=True)


if __name__ == "__main__":
    for who, name in NAMES.items():
        prepare(who, name)
