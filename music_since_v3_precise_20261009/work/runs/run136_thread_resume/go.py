"""run136：只读 run133 的已冻结 GPT-5.6 前缀；在新目录补完 v2/v3。

这是 prompt 单变量研究，不把历史前缀与 GPT-6 新链混作公平模型对比。
旧 Opus 链仅作参照，缺 Center 不补。评审自评允许，分列、换位；Muse外部T3批。
"""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import sys
from pathlib import Path

os.environ["MUSIC_WEB_ROUTE"] = "gpt2"
os.environ["RUN133_GEN"] = "gpt56w"
os.environ["RUN133_REV"] = "gpt56w,gpt6w,gflash,luna_noweb"
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from execution_integrity import model_evidence, sha_file, sha_text, write_json, write_text, canonical_model
from experiment_calls import call as exact_call

spec = importlib.util.spec_from_file_location("legacy_run133", ROOT / "runs/run133_thread_spec/go.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
L.RUN_ID = OUT.name
L.OUT_DIR = OUT
L.THIS_DIR = OUT  # manifest 的 script 指向本文件，不冒充旧 go.py
L.MATCH_MODEL = "gflash"
L.MATCH_MODEL_REASON = "10-09 frozen match selection, old Muse runner forbidden"
L.GEN_MODELS = ("gpt56w",)
L.REVIEWERS = ("gpt56w", "gpt6w", "gflash", "luna_noweb")
OLD = ROOT / "runs/run133_thread_spec"
FROZEN = []


def legacy_arr(text):
    if not isinstance(text, str):
        return False, None, "empty output"
    try:
        a, b = text.find("["), text.rfind("]")
        val = json.loads(text[a:b + 1])
        return (True, val, None) if isinstance(val, list) else (False, None, "not array")
    except Exception as e:
        return False, None, str(e)


L.extract_json_arr = legacy_arr


def frozen_hit(step, model, prompt, key, parse_fn):
    """明确冻结旧输入，不伪造 exact producer identity。逐个验证正文、prompt和服务端型号。"""
    path = OLD / ("cache_%s.json" % step)
    if step not in ("step", "match") or not path.exists():
        return None
    cache = json.loads(path.read_text(encoding="utf-8"))
    for r in reversed(cache.get("records", [])):
        if r.get("model") != model or r.get("key") != key or not r.get("parse_ok"):
            continue
        if r.get("prompt_sha") != L.sha10(prompt):
            continue
        text = r.get("output")
        good = [a for a in r.get("attempts", []) if a.get("parse_ok") and a.get("status") == "ok"]
        if not isinstance(text, str) or not good:
            continue
        jid = good[-1]["job_id"]
        mp, pp, op = OLD / "meta" / (jid + ".json"), OLD / "prompts" / (jid + ".txt"), OLD / "outputs" / (jid + ".md")
        if not all(p.is_file() for p in (mp, pp, op)):
            continue
        meta = json.loads(mp.read_text(encoding="utf-8"))
        if meta.get("model_key") != model or pp.read_bytes() != prompt.encode("utf-8") or op.read_bytes() != text.encode("utf-8"):
            continue
        if model in ("gpt56w", "gpt6w"):
            ev = model_evidence(meta.get("cli_metadata"), meta.get("requested_model"))
            if ev["verdict"] != "match" or meta.get("response_sha256") != sha_text(text):
                continue
            server_ev = {"verdict": ev["verdict"], "server_slugs": ev["server_slugs"]}
        else:
            # 旧 match meta 无 cli_metadata：无 servermodel 证据，只做正文+prompt bytes 比对。
            server_ev = "none: legacy meta lacks cli_metadata; bytes+hash only"
        parsed, err = parse_fn(text)
        if parsed is None:
            continue
        # 记录 producer 限制，绝不据 HEAD 推断当时未提交源码哈希。
        evidence = {"source_run": OLD.name, "source_job": jid, "model": model,
                    "prompt_sha256": sha_text(prompt), "response_sha256": sha_text(text),
                    "meta_sha256": sha_file(mp), "cache_sha256": sha_file(path),
                    "cli_version_recorded": meta.get("cli_version"),
                    "servermodel_evidence": server_ev if model in ("gpt56w", "gpt6w") else server_ev,
                    "producer_code_hash_at_generation": "not recorded; frozen input, not exact cache proof"}
        FROZEN.append(evidence)
        return dict(r, parsed=parsed, cached=True, frozen_input=evidence, parse_error=err)
    return None


def call(step, core, model, prompt, parse_fn, key, prompt_version, prompt_template, extra=None):
    hit = frozen_hit(step, model, prompt, key, parse_fn)
    if hit:
        L.bump(step, model, "cached")
        return hit
    r = exact_call(OUT, step, core, model, prompt, parse_fn, key, prompt_version,
                   prompt_template, extra, L.WORK_KEY, L.WORK_NAME)
    L.bump(step, model, "cached" if r.get("cached") else "calls")
    if not r["parse_ok"]:
        L.bump(step, model, "failed")
        # 链不能跳过失败步后还继续宣称完整。
        raise RuntimeError("incomplete %s/%s: %s" % (step, core, r.get("parse_error")))
    return r


L.call = call


def generation():
    beads, chains, centers = L.stage_gen(2)
    assert all(len(v) == 23 and all(x.get("parse_ok") for x in v) for v in chains.values())
    assert all(c.get("parse_ok") for c in centers.values())
    write_json(OUT / "frozen_input_manifest.json", {"source": "run133", "records": FROZEN,
        "caveat": "历史前缀只读冻结；不能将这条部分历史链用于新鲜GPT5.6/6公平角色判断"})
    write_text(OUT / "GEN_DONE", "all steps and centers complete; not product acceptance")


def export_muse():
    beads, chains, centers = L.load_gen()
    D = OUT / "muse_review_prompts"
    D.mkdir(exist_ok=True)
    tasks = []
    for order in (0, 1):
        a, b = ("v2", "v3") if order == 0 else ("v3", "v2")
        prompt = L.fill(L.TPL["THREAD_COMPARE_v0"], WORK=L.WORK_NAME, BEADS=L.build_center_beads(beads),
                        A=L.build_chain_record(beads, chains[a + "_gpt56w"], centers[a + "_gpt56w"]),
                        B=L.build_chain_record(beads, chains[b + "_gpt56w"], centers[b + "_gpt56w"]))
        file = "compare_o%d.txt" % order
        write_text(D / file, prompt)
        tasks.append({"id": "compare_o%d" % order, "path": file, "order": order,
                      "mapping": {"A": a, "B": b}, "prompt_sha256": sha_text(prompt)})
    stmts = []
    for v in L.VERSIONS:
        stmts += L.collect_chain_statements(v, "gpt56w", chains[v + "_gpt56w"], centers[v + "_gpt56w"])
    for i, s in enumerate(stmts):
        candidates, seed = L.shuffle_candidates(s["text"])
        p = L.fill(L.TPL["THREAD_IDENT_v0"], CANDIDATES="\n".join("%d. %s" % (j+1,c) for j,c in enumerate(candidates)),
                   STATEMENT=s["text"])
        file = "ident_s%d.txt" % i
        write_text(D / file, p)
        tasks.append({"id": "ident_s%d" % i, "path": file, "stmt_idx": i, "chain": s["chain"],
                      "kind": s["kind"], "text": s["text"], "seed": seed, "prompt_sha256": sha_text(p)})
    write_json(D / "tasks.json", {"tasks": tasks, "transport": "T3 delegate_task, full prompt inline"})


def report():
    L.stage_report()
    integrity = []
    chains = json.loads((OUT / "chains.json").read_text(encoding="utf-8"))["chains"]
    centers = json.loads((OUT / "centers.json").read_text(encoding="utf-8"))["centers"]
    for v in L.VERSIONS:
        rs = chains.get(v + "_gpt56w", [])
        if len(rs) != 23 or not all(r.get("parse_ok") and r.get("match_ok") is not False for r in rs):
            integrity.append("incomplete chain " + v)
        if not (centers.get(v + "_gpt56w") or {}).get("parse_ok"):
            integrity.append("missing center " + v)
    for name in ("ident", "compare"):
        d = json.loads((OUT / (name + ".json")).read_text(encoding="utf-8"))
        if not d.get("records") or not all(r.get("parse_ok") for r in d["records"]):
            integrity.append("incomplete " + name)
    # Muse 是用户要求的独立评审，不以缺席时的报告冒充整轮完成。
    if not (OUT / "muse_reviews.json").is_file():
        integrity.append("Muse pending")
    write_json(OUT / "completion.json", {"complete": not integrity, "missing": integrity,
              "not_production_acceptance": True, "self_review_allowed": True})
    if not integrity:
        write_text(OUT / "DONE", "all declared records complete; not production ready")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("gen", "ident", "compare", "export-muse", "report"))
    a = ap.parse_args()
    stages = [a.stage] if a.stage else ["gen", "ident", "compare", "export-muse", "report"]
    try:
        for s in stages:
            {"gen": generation, "ident": lambda: L.stage_ident(4), "compare": lambda: L.stage_compare(4),
             "export-muse": export_muse, "report": report}[s]()
        L.write_manifest({"stages": stages, "frozen_input": bool(FROZEN), "no_new_opus": True})
        return 0
    except Exception as e:
        write_json(OUT / "failure.json", {"stage": s, "error": "%s: %s" % (type(e).__name__, e)})
        raise


if __name__ == "__main__":
    sys.exit(main())
