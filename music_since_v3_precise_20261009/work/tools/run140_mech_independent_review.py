"""run140：60 条旧关系独立判断包（机械转写，不提交模型）。

范围：run138 cases（run128 旧输入冻结关系）只作 legacy-input E5 单句审核诊断，
非 canonical 新 E5 / 三作品验收。run138 尚 0 真实 audit，
independent_review_case_ids 只是占位；本任务先建立与两条件结果无关的全部 60
关系独立判断包，不泄旧标签、不按 known verdict 挑例、不追 NONE 率。

做法：seed20261009 固定 shuffle 分 5 包（每包 12 case），blindID 单独乱排；
judge 全文只含 WORK 中文名与 MM/items/relation/new_understanding 原文 inline，
每包编号只 bind 当前 case blindID，不让 judge 读文件；完整映射（含 sourceSHA、
原 ID、genCanonical、promptSHA）私存，不进 judge。

用法：
  python tools/run140_mech_independent_review.py --prepare
只写 runs/run140_mech_independent_review/ 下的 plan.json、case_mapping.json、
review_prompts/pack*.txt（immutable，冲突即拒；锁 driver 与全部源字节）。
不执行任何真实请求，model_submissions 恒为 0。

主会话不是音乐内容候选写手；本文件仅机械转写旧文本及评审任务，不做审美裁决。
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from execution_integrity import (ArtifactConflict, canonical_model, sha_file,
                                 sha_text, write_json, write_text)

ROOT = TOOLS.parent
SOURCE_CASES = ROOT / "runs/run138_e5_counterfactual/cases.json"
SOURCE_PLAN = ROOT / "runs/run138_e5_counterfactual/plan.json"
OUT = ROOT / "runs/run140_mech_independent_review"

SEED = 20261009
BLIND_SEED = 20261010
WORKS = {"op52": "肖邦《第四叙事曲》f小调 Op.52", "op60": "肖邦《船歌》升F大调 Op.60"}
EXPECTED_STATIONS = {"op52": 16, "op60": 14}
# run138 输入按原字节 hash 锁；任一字节改动即拒。
EXPECTED_CASES_SHA256 = "8f30ef391dce919fd8c0e5f8c112d7b40a7c5248b1498b575b011d4663ae78aa"
EXPECTED_PLAN_SHA256 = "2e0736d6a8ed621d695b9e134f2cc1e7a24254ed16037f6b2845009a99739fd1"
CLASSES = {"insight", "restatement", "manufactured", "imported", "undetermined"}
PACK_SIZE = 12
N_PACKS = 5

# 评审模板常量（随本任务新建；冻结的 MECH_AUDIT_v0/v1 一字不改）。
# judge 全文禁入：case_id、工号（job_id）、生成 model、来源 run、旧标签、条件名。
REVIEW_TEMPLATE = """你是独立内容核查员，不是生产验收官。
本次是 legacy-input 单句审核诊断：对旧研究文字提出的关系逐条独立复核。
不是新版 canonical E5，也不是三作品验收；结论不切 production，不判质量胜利，不追 NONE 率。

【本包】{{PACK_ID}}，共 {{N_CASES}} 组。每组以 blindID 标识；条目编号只在本组 blindID 内有效。
不要读任何文件，只用本提示词内给出的文字作判断；不要猜原顺序、原编号、来源模型。

【重要前提】
- 每组给出的 WORK 中文名、MM 原文、items 原文、relation 原文、new_understanding 原文，
  全部是待审旧研究文字，不是已核乐谱事实；MM 与 items 只是当时的体验记录，不借外部整曲故事补洞见。
- 不得导入原音频或乐谱未给的内容；四类声音事实若无真实乐谱，只说 input-level 支持；
  semantic imported 不能凭猜整曲判断。
- 不按模型或长度判断；不根据 assertive 叙事贬分。

【统一判据全文】
根据可辨时间材料依据、独特有效听者体验、信息增量、具体性、前缀诚实、语义保真、
作品特异性和实际阅读效果，逐条判断。
戏剧化、笃定、因果写满、单一故事线本身不扣分；
只有缺证据、矛盾、压住关键独立解释、重复灌水才扣分。
NONE 或 NOCHANGE 合法（删掉关系而理解确无损失时，在 loss_if_deleted 写 NOCHANGE 并说明理由），
但不为空白目标删真价值。
必须原文引证（quoted_items、quoted_relation），能说出支持与反例；
证据不足以区分时判 undetermined 并说清缺哪份证据，不要猜测。

【五类只能选一种】
- insight：它确实同时解释了它说的那几条体验；删掉它而保留全部原体验后，
  听者会失去一种原体验尚未说出的、有本处依据的理解（必须在 loss_if_deleted 说出该损失，并以 sourcequotes 作证）。
- restatement：只是把那几条合并、换词或换比喻再说一遍，没有多出理解；不能只用新比喻不同证明新机制。
- manufactured：听起来深刻，但本处体验并不支持，是硬造出来的深度。
- imported：主要来自对整曲的外部整体叙事，而不是本处已有的体验。
- undetermined：现有证据确实无法区分类别，说清缺哪份证据。

【表达价值单列】
允许 relation 的机制是 restatement，但它的 vivid anchor 仍有独立表达价值。
单列 retain_anchor=true/false/undetermined 并写 anchor_reason；
不能因判重复就直接抹掉语言价值，也不能因语言生动就把 restatement 升成 insight。

【输出】
只输出一个完整 JSON 对象，不要前言尾言：
{"pack_id": "{{PACK_ID}}", "reviews": [{"blind_id": "<本包内 blindID>", "verdict": "insight|restatement|manufactured|imported|undetermined", "why": "非空，至少一句话", "quoted_items": [[<条目号>, "<原文逐字>"]], "quoted_relation": "<relation 原文逐字>", "loss_if_deleted": "删掉该关系而保留全部原体验后失去的理解；确无损失写 NOCHANGE 并说明", "retain_anchor": true, "anchor_reason": "非空", "evidence_limit": "只到 input-level 为止的证据边界，非空"}]}
reviews 必须恰好 {{N_CASES}} 条，blind_id 恰为本包集合且唯一；
quoted_items 须覆盖该关系声称解释的全部条目号且逐字相符；缺 quote 不算通过。

【各组材料】
{{CASES_BLOCK}}
"""


def read_utf8(path):
    return Path(path).read_bytes().decode("utf-8")


def immutable_text(path, text):
    path = Path(path)
    raw = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() != raw:
            raise ArtifactConflict("冻结文件不匹配，须新 run：" + str(path))
    else:
        write_text(path, text)


def immutable_json(path, obj):
    path = Path(path)
    if path.exists():
        try:
            current = json.loads(read_utf8(path))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ArtifactConflict("冻结 JSON 已损坏，须新 run：" + str(path)) from exc
        if current != obj:
            raise ArtifactConflict("冻结 JSON 不匹配，须新 run：" + str(path))
    else:
        write_json(path, obj)


def strict_case(case):
    """核每 case 类型；explains 先逐个验 strict int（拒 bool），再判去重后至少两个。"""
    if not isinstance(case, dict):
        raise ValueError("case 不是对象")
    work = case.get("work")
    if work not in EXPECTED_STATIONS:
        raise ValueError("work 非法")
    station = case.get("station")
    if type(station) is not int or not 1 <= station <= EXPECTED_STATIONS[work]:
        raise ValueError("station 非法")
    relation_index = case.get("relation_index")
    if type(relation_index) is not int or relation_index not in (1, 2):
        raise ValueError("relation_index 非法")
    items = case.get("items")
    if (not isinstance(items, list) or len(items) < 2
            or any(not isinstance(t, str) or not t.strip() for t in items)):
        raise ValueError("items 须是至少两条非空字符串")
    for key in ("relation", "new_understanding", "mm"):
        value = case.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(key + " 为空/非字符串")
    explains = case.get("explains")
    if not isinstance(explains, list):
        raise ValueError("explains 不是数组（不接受 set 嵌套）")
    for x in explains:
        if type(x) is not int or not 1 <= x <= len(items):
            raise ValueError("explains 至少两个不同的有效 strict int，不接受 bool/字符串/越界")
    if len(set(explains)) < 2:
        raise ValueError("explains 至少两个不同的有效 strict int")
    source = case.get("source")
    if not isinstance(source, dict):
        raise ValueError("source 不是对象")
    return {"explains": sorted(set(explains))}


def load_and_validate(source_cases=SOURCE_CASES, source_plan=SOURCE_PLAN):
    source_cases, source_plan = Path(source_cases), Path(source_plan)
    if not source_cases.is_file() or not source_plan.is_file():
        raise ArtifactConflict("run138 输入文件缺失")
    if sha_file(source_cases) != EXPECTED_CASES_SHA256:
        raise ArtifactConflict("run138 cases.json 原字节 hash 不匹配")
    if sha_file(source_plan) != EXPECTED_PLAN_SHA256:
        raise ArtifactConflict("run138 plan.json 原字节 hash 不匹配")
    cases = json.loads(source_cases.read_bytes().decode("utf-8"))
    if not isinstance(cases, list) or len(cases) != 60:
        raise ArtifactConflict("case 总数不是 60")
    counts = Counter((c.get("work"), c.get("station")) for c in cases)
    for work, n_station in EXPECTED_STATIONS.items():
        for station in range(1, n_station + 1):
            if counts.get((work, station)) != 2:
                raise ArtifactConflict("站组成不是每站 2 条：%s st%d" % (work, station))
    if Counter(c.get("work") for c in cases) != Counter({"op52": 32, "op60": 28}):
        raise ArtifactConflict("两作品条数不是 op52=32/op60=28")
    seen = set()
    for case in cases:
        strict_case(case)
        cid = case.get("case_id")
        if not isinstance(cid, str) or cid in seen:
            raise ArtifactConflict("case_id 缺失/重复")
        seen.add(cid)
    return cases


def build_packs(cases, seed=SEED, blind_seed=BLIND_SEED):
    """seed 固定 shuffle 分 5 包；blindID 单独乱排，不泄 original 顺序。"""
    order = list(range(len(cases)))
    random.Random(seed).shuffle(order)
    blinds = ["B%03d" % i for i in range(1, len(cases) + 1)]
    random.Random(blind_seed).shuffle(blinds)
    packs, mapping = [], []
    for k, idx in enumerate(order):
        case = cases[idx]
        pack_no = k // PACK_SIZE + 1
        pack_id = "pack%02d" % pack_no
        blind_id = blinds[k]
        packs_entry = {"blind_id": blind_id, "original_case_id": case["case_id"],
                       "work": case["work"], "station": case["station"],
                       "relation_index": case["relation_index"], "mm": case["mm"],
                       "items": list(case["items"]), "relation": case["relation"],
                       "new_understanding": case["new_understanding"],
                       "explains": list(case["explains"])}
        if len(packs) < pack_no:
            packs.append({"pack_id": pack_id, "cases": []})
        packs[pack_no - 1]["cases"].append(packs_entry)
        source = case["source"]
        mapping.append({"blind_id": blind_id, "pack_id": pack_id,
                        "original_case_id": case["case_id"], "work": case["work"],
                        "station": case["station"], "relation_index": case["relation_index"],
                        "mm_sha256": sha_text(case["mm"]),
                        "items_sha256": [sha_text(t) for t in case["items"]],
                        "relation_sha256": sha_text(case["relation"]),
                        "new_understanding_sha256": sha_text(case["new_understanding"]),
                        "explains": list(case["explains"]),
                        "source": dict(source),
                        "gen_canonical": canonical_model(source.get("generator_key", ""))})
    for pack in packs:
        if len(pack["cases"]) != PACK_SIZE:
            raise ArtifactConflict("分包不是每包 12 case")
    return packs, mapping


def render_pack_prompt(pack):
    blocks = []
    for entry in pack["cases"]:
        lines = ["【案例 blindID=%s】" % entry["blind_id"],
                 "WORK：" + WORKS[entry["work"]],
                 "MM（待审旧文字，非乐谱事实）：" + entry["mm"],
                 "体验（待审旧文字）："]
        lines += ["[%d] %s" % (i, t) for i, t in enumerate(entry["items"], 1)]
        lines.append("它说自己解释了第 %s 条。" % "、".join(map(str, entry["explains"])))
        lines.append("待审关系：" + entry["relation"])
        lines.append("它声称的新理解：" + entry["new_understanding"])
        blocks.append("\n".join(lines))
    prompt = (REVIEW_TEMPLATE.replace("{{PACK_ID}}", pack["pack_id"])
              .replace("{{N_CASES}}", str(len(pack["cases"])))
              .replace("{{CASES_BLOCK}}", "\n\n".join(blocks) + "\n"))
    for token in ("{{PACK_ID}}", "{{N_CASES}}", "{{CASES_BLOCK}}"):
        if token in prompt:
            raise ValueError("残留占位符：" + token)
    # judge 全文禁入身份信息；模板与转写均不得带入。
    forbidden = ["MECH128", "AUDIT138", "run128", "run138", "gpt56w",
                 "producer_identity", "unknown_in_legacy_record",
                 "recorded_model_name", "MECH_AUDIT", "MECH_v1"]
    for token in forbidden:
        if token.lower() in prompt.lower():
            raise ValueError("judge 全文泄漏禁入信息：" + token)
    if re.search(r"R0\d\d", prompt):
        raise ValueError("judge 全文泄漏原 case_id")
    return prompt


def parse_review(text, pack):
    """只收完整 JSON（框内完整 JSON 亦可）；拒前言尾言/重复键/id 越界/schema 不符。

    返回 (parsed, None) 或 (None, err)。缺 quote 不算通过。
    """
    try:
        if not isinstance(text, str):
            raise ValueError("输出不是文本")
        clean = text.strip()
        if clean.startswith("```"):
            match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", clean, re.S)
            if not match:
                raise ValueError("JSON fence 不完整")
            clean = match.group(1)

        def hook(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError("重复键：" + str(key))
                obj[key] = value
            return obj

        value = json.loads(clean, object_pairs_hook=hook)
        if not isinstance(value, dict):
            raise ValueError("顶层必须是对象")
        if set(value) != {"pack_id", "reviews"}:
            raise ValueError("顶层只能有 pack_id 与 reviews")
        if value["pack_id"] != pack["pack_id"]:
            raise ValueError("pack_id 不匹配")
        reviews = value["reviews"]
        if not isinstance(reviews, list) or len(reviews) != len(pack["cases"]):
            raise ValueError("reviews 必须是 %d 项数组" % len(pack["cases"]))
        by_blind = {c["blind_id"]: c for c in pack["cases"]}
        if len(by_blind) != len(pack["cases"]):
            raise ValueError("pack 内 blind_id 重复")
        wanted = {"blind_id", "verdict", "why", "quoted_items", "quoted_relation",
                  "loss_if_deleted", "retain_anchor", "anchor_reason", "evidence_limit"}
        seen = set()
        for item in reviews:
            if not isinstance(item, dict):
                raise ValueError("review 项不是对象")
            if set(item) != wanted:
                raise ValueError("review schema 键不符")
            blind_id = item["blind_id"]
            if blind_id in seen:
                raise ValueError("blind_id 重复：" + str(blind_id))
            seen.add(blind_id)
            case = by_blind.get(blind_id)
            if case is None:
                raise ValueError("blind_id 越界：" + str(blind_id))
            if item["verdict"] not in CLASSES:
                raise ValueError("非法 verdict")
            for key in ("why", "loss_if_deleted", "anchor_reason", "evidence_limit"):
                if not isinstance(item[key], str) or not item[key].strip():
                    raise ValueError(key + " 为空/非字符串")
            quoted = item["quoted_items"]
            if not isinstance(quoted, list) or not quoted:
                raise ValueError("quoted_items 须是非空数组")
            cited = set()
            for pair in quoted:
                if not isinstance(pair, list) or len(pair) != 2:
                    raise ValueError("quoted_items 须是 [integer, text] 对")
                num, txt = pair
                if type(num) is not int or not 1 <= num <= len(case["items"]):
                    raise ValueError("quoted_items 序号非法")
                if not isinstance(txt, str) or txt != case["items"][num - 1]:
                    raise ValueError("quoted_items 原串不符")
                cited.add(num)
            if not set(case["explains"]).issubset(cited):
                raise ValueError("quoted_items 未覆盖全部 explains")
            if not isinstance(item["quoted_relation"], str) or item["quoted_relation"] != case["relation"]:
                raise ValueError("quoted_relation 原串不符")
            anchor = item["retain_anchor"]
            if not (anchor is True or anchor is False or anchor == "undetermined"):
                raise ValueError("retain_anchor 须是 true/false/undetermined")
        if seen != set(by_blind):
            raise ValueError("blind_id 集合不完整")
        return value, None
    except (ValueError, TypeError, AttributeError) as exc:
        return None, str(exc)


def prepare(out=OUT):
    out = Path(out)
    cases = load_and_validate()
    packs, mapping = build_packs(cases)
    for pack in packs:
        prompt = render_pack_prompt(pack)
        rel = "review_prompts/%s.txt" % pack["pack_id"]
        immutable_text(out / rel, prompt)
        digest = sha_text(prompt)
        pack["prompt_file"] = rel
        pack["prompt_sha256"] = digest
        for entry in mapping:
            if entry["pack_id"] == pack["pack_id"]:
                entry["prompt_file"] = rel
                entry["prompt_sha256"] = digest
    mapping_sorted = sorted(mapping, key=lambda m: m["blind_id"])
    immutable_json(out / "case_mapping.json",
                   {"seed": SEED, "blind_seed": BLIND_SEED,
                    "private": "完整映射私存，不进 judge",
                    "entries": mapping_sorted})
    plan = {"schema": "run140.1", "seed": SEED, "blind_seed": BLIND_SEED,
            "scope": ("legacy-input E5 单句审核诊断：run138 冻结 60 关系独立复核；"
                      "非 canonical 新 E5 / 三作品验收；独立内容核查，不切 production"),
            "source_inputs": {"cases.json": EXPECTED_CASES_SHA256,
                              "plan.json": EXPECTED_PLAN_SHA256,
                              "cases_bytes": len((ROOT / "runs/run138_e5_counterfactual/cases.json").read_bytes()),
                              "plan_bytes": len((ROOT / "runs/run138_e5_counterfactual/plan.json").read_bytes())},
            "case_count": len(cases), "composition": {"op52": 32, "op60": 28, "per_station": "每站2条"},
            "packs": [{"pack_id": p["pack_id"], "prompt_file": p["prompt_file"],
                       "prompt_sha256": p["prompt_sha256"],
                       "blind_ids": [c["blind_id"] for c in p["cases"]]} for p in packs],
            "case_mapping_sha256": sha_file(out / "case_mapping.json"),
            "template_sha256": sha_text(REVIEW_TEMPLATE),
            "driver_sha256": sha_file(Path(__file__).resolve()),
            "model_submissions": 0, "production_ready": False,
            "reviewers_planned": {"muse": "separate 独立一份，不平均不多数",
                                  "luna": "separate 独立一份，不平均不多数",
                                  "rule": "外部 producer 按实际 transport 真实记录；工程 mock 自评不算真 review"},
            "holds_untouched": "run135 queue hold 等缺项照留，本任务不清 hold、不补造 twowheld"}
    immutable_json(out / "plan.json", plan)
    return {"cases": len(cases), "packs": len(packs), "model_submissions": 0,
            "files": [p["prompt_file"] for p in packs] + ["case_mapping.json", "plan.json"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prepare", action="store_true", help="只核冻结输入与导出任务，不提交模型")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    if not args.prepare:
        print(json.dumps({"prepared": False, "model_submissions": 0,
                          "note": "仅支持 --prepare；不执行真实请求"}, ensure_ascii=False))
        raise SystemExit(2)
    summary = prepare(args.out)
    print(json.dumps({"prepared": True, **summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
