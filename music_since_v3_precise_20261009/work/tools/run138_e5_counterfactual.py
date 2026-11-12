"""run138：固定旧机制输入，仅改变审核的一句删句反事实判据。"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import experiment_calls as calls
from execution_integrity import ArtifactConflict, canonical_model, sha_file, sha_text, write_json, write_text

ROOT = TOOLS.parent
SOURCE = ROOT / "runs/run128_mech_calib"
OUT = ROOT / "runs/run138_e5_counterfactual"
SEED = 20261009
WORKS = {"op52": "肖邦《第四叙事曲》f小调 Op.52", "op60": "肖邦《船歌》升F大调 Op.60"}
EXPECTED = {"op52": 16, "op60": 14}
TEMPLATES = {"v0": ROOT / "prompts/tooling/MECH_AUDIT_v0.txt",
             "v1": ROOT / "prompts/tooling/MECH_AUDIT_v1_counterfactual_20261009.txt"}
GEN_TEMPLATE = ROOT / "prompts/tooling/MECH_v1.txt"
ADDITION = "只有你能指出删掉这条关系而保留全部原体验后，听者会失去哪一种尚未由原体验说出的、有本处依据的理解，才可判 insight，并在 why 中说出该损失；若只是换词、合并或换一个比喻呈现已有理解，判 restatement。"
GOVERNANCE = ('评审纪律补充：戏剧化、笃定、单一故事线本身不扣分，不追求 NONE 或空白率；'
              '只依据本次给出的体验与关系，不把来源模型或长度当证据。'
              '若现有证据确实无法区分类别，可以输出 '
              '{"class":"undetermined","why":"明确指出缺哪份证据"}，不要猜测。')
CLASSES = {"insight", "restatement", "manufactured", "imported", "undetermined"}


def read_utf8(path):
    return Path(path).read_bytes().decode("utf-8")


def legacy_text(path):
    # 历史 sha10 是 read_text 的 universal-newline 内容，不冒充原 byte hash。
    return read_utf8(path).replace("\r\n", "\n").replace("\r", "\n")


def inside(root, rel):
    if not isinstance(rel, str) or not rel:
        raise ArtifactConflict("缺少历史文件路径")
    path = (Path(root) / rel).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ArtifactConflict("历史文件缺失或越界：" + rel)
    return path


def immutable_text(path, text):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != text.encode("utf-8"):
            raise ArtifactConflict("冻结文件不匹配，须新 run：" + str(path))
    else:
        write_text(path, text)


def immutable_json(path, obj):
    path = Path(path)
    if path.exists():
        if json.loads(read_utf8(path)) != obj:
            raise ArtifactConflict("冻结 JSON 不匹配，须新 run：" + str(path))
    else:
        write_json(path, obj)


def json_value(text, expected):
    if not isinstance(text, str):
        raise ValueError("输出不是文本")
    clean = text.strip()
    if clean.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", clean, re.S)
        if not match:
            raise ValueError("JSON fence 不完整")
        clean = match.group(1)
    value = json.loads(clean)
    if not isinstance(value, expected):
        raise ValueError("JSON 顶层类型错误")
    return value


def strict_relations(value, n_items):
    if not isinstance(value, list) or len(value) > 2:
        raise ValueError("关系必须是最多两项的数组")
    result = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("关系项不是对象")
        relation, increment = item.get("relation"), item.get("new_understanding")
        if not isinstance(relation, str) or not relation.strip():
            raise ValueError("relation 为空/非字符串")
        if not isinstance(increment, str) or not increment.strip():
            raise ValueError("new_understanding 为空/非字符串")
        explains = item.get("explains")
        if (not isinstance(explains, list) or len(set(explains)) < 2
                or any(type(x) is not int or not 1 <= x <= n_items for x in explains)):
            raise ValueError("explains 至少两个不同的有效整数，不接受 bool/字符串")
        result.append({"relation": relation.strip(), "explains": sorted(set(explains)),
                       "new_understanding": increment.strip()})
    return result


def parse_audit(text):
    try:
        value = json_value(text, dict)
        if set(value) != {"class", "why"}:
            raise ValueError("审核必须只有 class 与 why")
        if value["class"] not in CLASSES:
            raise ValueError("非法审核类别")
        if not isinstance(value["why"], str) or not value["why"].strip():
            raise ValueError("审核理由为空/非字符串")
        return {"class": value["class"], "why": value["why"].strip()}, None
    except (ValueError, TypeError, KeyError) as exc:
        return None, str(exc)


def verify_templates():
    templates = {key: read_utf8(path) for key, path in TEMPLATES.items()}
    if templates["v1"].count(ADDITION) != 1 or templates["v1"].replace(ADDITION + "\n", "") != templates["v0"]:
        raise ArtifactConflict("审核模板不是只增加冻结的一个句子")
    return templates


def extract_input(prompt, work):
    prefix = "下面是一篇边听边读文字里，关于 " + WORKS[work] + " 中 "
    ending = " 这一处的几条体验，每条已经是独立的一种体验或理解。"
    first = prompt.splitlines()[0]
    if not first.startswith(prefix) or not first.endswith(ending):
        raise ArtifactConflict("旧生成提示词头与作品不匹配")
    mm = first[len(prefix):-len(ending)]
    marker = "【这一处的体验】\n"
    if prompt.count(marker) != 1:
        raise ArtifactConflict("旧 prompt 的体验标记不唯一")
    numbered = prompt.split(marker, 1)[1].rstrip("\n")
    items = []
    for i, line in enumerate(numbered.splitlines(), 1):
        match = re.fullmatch(r"(\d+)\. (.+)", line)
        if not match or int(match.group(1)) != i or not match.group(2).strip():
            raise ArtifactConflict("体验编号不连续/条目不是原冻结单行格式")
        items.append(match.group(2))
    if len(items) < 2:
        raise ArtifactConflict("体验条数不足")
    template = legacy_text(GEN_TEMPLATE)
    filled = template.replace("{{WORK}}", WORKS[work]).replace("{{MM}}", mm).replace("{{ITEMS}}", numbered)
    if filled != prompt:
        raise ArtifactConflict("原 prompt 与冻结 MECH_v1 模板不一致")
    return mm, items


def load_cases(source=SOURCE):
    source = Path(source)
    cache_path = source / "cache_gen.json"
    records = json.loads(read_utf8(cache_path)).get("records")
    if not isinstance(records, list):
        raise ArtifactConflict("历史 cache 缺少 records")
    picked = [r for r in records if r.get("model") == "gpt56w"
              and r.get("prompt_version") == "MECH_v1" and r.get("parse_ok") is True]
    keyed = {}
    for record in picked:
        key = record.get("key")
        if (not isinstance(key, list) or len(key) != 5 or key[0] != "gen"
                or key[1] not in EXPECTED or type(key[2]) is not int or key[3:] != ["v1", "gpt56w"]):
            raise ArtifactConflict("历史生成记录 key 不合法")
        index = (key[1], key[2])
        if index in keyed:
            raise ArtifactConflict("同站存在多个成功记录，不自动选最后一个")
        keyed[index] = record
    wanted = {(w, i) for w, n in EXPECTED.items() for i in range(1, n + 1)}
    if set(keyed) != wanted:
        raise ArtifactConflict("冻结旧生成站集合不完整/多余")
    cases, files = [], {str(cache_path.relative_to(ROOT)): sha_file(cache_path)}
    for (work, station), record in sorted(keyed.items()):
        jid = record.get("output_job_id")
        if not isinstance(jid, str) or Path(jid).name != jid:
            raise ArtifactConflict("非法旧 output_job_id")
        mp = inside(source, "meta/" + jid + ".json")
        meta = json.loads(read_utf8(mp))
        if (meta.get("status") != "ok" or meta.get("model_key") != "gpt56w"
                or meta.get("job_id") != jid or meta.get("work_key") != work
                or meta.get("prompt_version") != "MECH_v1"):
            raise ArtifactConflict("旧 meta 身份/状态不匹配：" + jid)
        extra = meta.get("extra") or {}
        if extra.get("station") != station or extra.get("version") != "v1" or extra.get("gen") != "gpt56w":
            raise ArtifactConflict("旧 meta 站序/版本不匹配")
        pp, op = inside(source, meta.get("prompt_file")), inside(source, meta.get("output_file"))
        prompt, output = legacy_text(pp), legacy_text(op)
        if sha_text(prompt)[:10] != record.get("prompt_sha"):
            raise ArtifactConflict("旧 prompt SHA10 不匹配")
        if meta.get("prompt_sha256") and sha_file(pp) != meta["prompt_sha256"]:
            raise ArtifactConflict("旧 prompt 原字节 SHA256 不匹配")
        if meta.get("response_sha256") and sha_file(op) != meta["response_sha256"]:
            raise ArtifactConflict("旧 output 原字节 SHA256 不匹配")
        mm, items = extract_input(prompt, work)
        parsed = strict_relations(json_value(output, list), len(items))
        if parsed != record.get("parsed"):
            raise ArtifactConflict("重新严格解析的 output 与 cache.parsed 不一致")
        for path in (mp, pp, op):
            files[str(path.relative_to(ROOT))] = sha_file(path)
        for i, relation in enumerate(parsed, 1):
            cases.append({"case_id": "R%03d" % (len(cases) + 1), "work": work,
                          "station": station, "relation_index": i, "mm": mm, "items": items,
                          **relation, "source": {"run": "run128_mech_calib", "job_id": jid,
                          "generator_key": "gpt56w", "recorded_model_name": meta.get("model_name"),
                          "actual_backend_model": "unknown_in_legacy_record",
                          "producer_identity": meta.get("producer_identity"),
                          "identity_limit": "旧冻结输入；当前文件快照 hash 不是历史 exact producer 证明",
                          "meta_sha256": sha_file(mp), "prompt_sha256_snapshot": sha_file(pp),
                          "prompt_sha10_legacy_normalized": record["prompt_sha"],
                          "output_sha256_snapshot": sha_file(op)}})
    return cases, files


def audit_prompt(case, template):
    pairs = {"WORK": WORKS[case["work"]], "MM": case["mm"],
             "ITEMS": "\n".join("[%d] %s" % (i, t) for i, t in enumerate(case["items"], 1)),
             "RELATION": case["relation"] + "——" + case["new_understanding"],
             "EXPLAINS": "、".join(map(str, case["explains"]))}
    prompt = template
    for key, value in pairs.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    if "{{" in prompt:
        raise ValueError("残留占位符")
    return prompt + "\n" + GOVERNANCE + "\n"


def prepare(out=OUT, smoke=False):
    out = Path(out)
    templates = verify_templates()
    cases, files = load_cases()
    full_count = len(cases)
    if smoke:
        # 工程 smoke 的固定两例，不按已知 verdict 挑选。
        cases = [next(c for c in cases if c["work"] == work and c["station"] == 1
                      and c["relation_index"] == 1) for work in sorted(EXPECTED)]
    jobs = []
    for case in cases:
        for version, template in templates.items():
            prompt = audit_prompt(case, template)
            core = "AUDIT138__%s__%s__gflash" % (case["case_id"], version)
            rel = "audit_prompts/" + core + ".txt"
            immutable_text(out / rel, prompt)
            jobs.append({"case_id": case["case_id"], "version": version, "model": "gflash",
                         "core": core, "work": case["work"], "prompt_file": rel,
                         "prompt_sha256": sha_text(prompt),
                         "self_review": canonical_model("gflash") == canonical_model(case["source"]["generator_key"])})
    random.Random(SEED).shuffle(jobs)
    immutable_json(out / "cases.json", cases)
    plan = {"schema": "run138.1", "seed": SEED, "smoke": smoke,
            "scope": "旧生产珠子二阶审核诊断；非新版 canonical E5/production 验收",
            "full_case_count_verified": full_count, "selected_case_count": len(cases),
            "single_variable": ADDITION, "governance_identical": GOVERNANCE,
            "source_files": files, "templates": {str(p.relative_to(ROOT)): sha_file(p) for p in TEMPLATES.values()},
            "generation_template_sha256": sha_file(GEN_TEMPLATE), "driver_sha256": sha_file(__file__),
            "cases_sha256": sha_file(out / "cases.json"), "jobs": jobs,
            "reviewers_pending": {"gpt56w": "run135 queue hold", "gpt6w": "run135 queue hold",
                                  "muse": "T3 外部全文复核待完成", "luna_noweb": "边界独立复核待完成"}}
    immutable_json(out / "plan.json", plan)
    return cases, jobs


def execute_one(out, task):
    prompt = read_utf8(Path(out) / task["prompt_file"])
    if sha_text(prompt) != task["prompt_sha256"]:
        raise ArtifactConflict("冻结审核 prompt 被改动")
    rec = calls.call(out, "audit", task["core"], task["model"], prompt, parse_audit,
                     [task["case_id"], task["version"], task["model"]],
                     "MECH_AUDIT_" + task["version"] + "_governed_20261009",
                     str(TEMPLATES[task["version"]].relative_to(ROOT)),
                     extra={"case_id": task["case_id"], "audit_version": task["version"],
                            "self_review": task["self_review"], "scope": "legacy_input_diagnostic"},
                     work_key=task["work"], work_name=WORKS[task["work"]], max_attempts=2)
    return {**task, "record": rec}


def report(out, cases, jobs, results):
    by_key = {(r["case_id"], r["version"]): r for r in results}
    expected = {(j["case_id"], j["version"]) for j in jobs}
    if len(by_key) != len(results) or not set(by_key).issubset(expected):
        raise ArtifactConflict("审核结果集合重复/越界")
    rows, selected, counts = [], [], {v: Counter() for v in ("v0", "v1")}
    for case in cases:
        audits = {}
        for version in ("v0", "v1"):
            result = by_key.get((case["case_id"], version))
            rec = (result or {}).get("record") or {}
            verdict = rec.get("parsed") if rec.get("parse_ok") is True else None
            audits[version] = {"verdict": verdict, "error": rec.get("parse_error"),
                               "output_file": rec.get("output_file"),
                               "producer_identity": rec.get("producer_identity")}
            counts[version][verdict["class"] if verdict else "missing_or_failed"] += 1
        left, right = (audits[v]["verdict"] for v in ("v0", "v1"))
        changed = bool(left and right and left["class"] != right["class"])
        rows.append({"case_id": case["case_id"], "audits": audits, "class_changed": changed})
        if changed or any(x and x["class"] in {"manufactured", "imported", "undetermined"} for x in (left, right)):
            selected.append(case["case_id"])
    complete = set(by_key) == expected and all(r["record"].get("parse_ok") is True for r in results)
    write_json(Path(out) / "results.json", {"complete": complete, "expected_jobs": len(expected),
               "completed_jobs": sum(r["record"].get("parse_ok") is True for r in results),
               "rows": rows, "counts": {v: dict(c) for v, c in counts.items()},
               "independent_review_case_ids": selected, "production_ready": False})
    lines = ["# run138：单句删句反事实审核诊断", "", "**不切 production；两w及最终独立复核仍缺项。**", "",
             "- 当前输入是 run128 旧珠子的冻结关系，不是新版 canonical 珠子的验收。",
             "- 审核输入/顺序/身份见 plan.json；真实正文与 meta 见新调用目录。",
             "- 完整审核：%s（%d / %d）。" % (complete, sum(r["record"].get("parse_ok") is True for r in results), len(expected)),
             "- 统计仅定位差异，不以 NONE 率、类别数量或多数票判质量胜利。", "",
             "| 案例 | v0 类别与理由 | v1 类别与理由 |", "|---|---|---|"]
    for row in rows:
        values = []
        for v in ("v0", "v1"):
            item = row["audits"][v]
            verdict = item["verdict"]
            text = (verdict["class"] + "：" + verdict["why"]) if verdict else "未完成：" + str(item["error"])
            values.append(text.replace("|", "\\|").replace("\n", "<br>"))
        lines.append("| %s | %s | %s |" % (row["case_id"], *values))
    write_text(Path(out) / "report.md", "\n".join(lines) + "\n")
    return complete


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prepare", action="store_true", help="只核冻结输入与导出任务，不提交模型")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    out = OUT / "smoke" if args.smoke else OUT
    cases, jobs = prepare(out, args.smoke)
    if args.prepare:
        print(json.dumps({"prepared": True, "cases": len(cases), "jobs": len(jobs), "model_submissions": 0}))
        return
    results = []
    # 逐波检查 stop；已经发出的同波调用只回收结果，不谎称可取消服务端。
    workers = max(1, min(8, args.workers))
    stopped = False
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for i in range(0, len(jobs), workers):
            wave = list(pool.map(lambda j: execute_one(out, j), jobs[i:i + workers]))
            results.extend(wave)
            if any(r["record"].get("queue_stop") for r in wave):
                stopped = True
                break
    complete = report(out, cases, jobs, results)
    print(json.dumps({"complete": complete, "queue_stopped": stopped, "production_ready": False}))
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
