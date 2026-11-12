"""R137 run137_e7_flash_diag：Flash E7 独立诊断（Op.60）。

范围（诊断用，永不进 production）：
- 只做真正独立的 Flash 诊断：gen=gflash、chooser=gflash、
  auditors=(gflash, luna_noweb)、judges=(gflash, luna_noweb)。
- 不称其代替 GPT，不切 production；不是新模型公平赛（prompt/input 全固定）。
- 旧 run134 只读：切分/历史/解析/统计/盲比架构全部复用，不改旧文件；
  调用层改用 tools/experiment_calls.call（旧 Store 不再用）。
- 输入沿用冻结的 run130 Op.60 洁净珠子 + run130:gpt56w 历史清单，不新造候选。
- 三方盲比：a=本稿读者视图 / b=run124 生产稿 B / c=run132 V2A+Gemini 基线两套；
  Op.60 的 c 为重建锚，非原始 V2A 真原稿（报告与 manifest 均声明）。
- 两 w 新鲜公平对照与全阵容最终裁决被 run135 post_submit_ambiguous 全局 hold 阻塞；
  Muse 评审待主会话 T3 派发：缺项明确落 completion，本 run 永不写 DONE。

用法（cwd 为仓库根）：
  python -I runs\\run137_e7_flash_diag\\go.py [--stage why|mech|surface|render|compare|report] [--workers 6]
  python -I runs\\run137_e7_flash_diag\\go.py --mock     # 纯假 run_job 全流程 + 断言（临时目录，验完即删；不碰真实目录，不调 CLI）
约束：只写本 run 目录；不改 prompts/、tools/、旧 runs；stdlib only；不启动真实 runner 冒烟。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run137_e7_flash_diag"
RUN_DIR = ROOT / "runs" / RUN_ID
RUN134_DIR = ROOT / "runs" / "run134_e7_diag"

sys.path.insert(0, str(ROOT / "tools"))
import experiment_calls  # noqa: E402  (新调用层；不修改 tools/)
from execution_integrity import canonical_model  # noqa: E402  (自评 flag 归一化)


def _load_run134():
    spec = importlib.util.spec_from_file_location("run134_go", RUN134_DIR / "go.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run134_go"] = mod
    spec.loader.exec_module(mod)
    return mod


r134 = _load_run134()  # 只读复用：不改旧文件，不用旧 Store/caches

# ---------------- 本诊断固定配置（不接受 CLI/环境覆盖；换模型 = 另开新 run） ----------------
CFG137 = {
    "gen": "gflash",
    "chooser": "gflash",
    "auditors": ("gflash", "luna_noweb"),
    "judges": ("gflash", "luna_noweb"),
    "history": "run130:gpt56w",  # 冻结输入：run130 Op.60 洁净珠子 + 该链历史清单
}
r134.CFG.update(gen=CFG137["gen"], chooser=CFG137["chooser"], history=CFG137["history"],
                auditors=tuple(CFG137["auditors"]), judges=tuple(CFG137["judges"]))
r134.RUN_ID = RUN_ID

OUT_DIR = RUN_DIR  # --mock / 测试时切换为临时目录
CALLS = {"n": 0}  # 本 wrapper 经 experiment_calls.call 的新调用计数（短路命中不计）


def sha256s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def wjson(name, obj):
    p = OUT_DIR / name
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def rjson(name):
    return json.loads((OUT_DIR / name).read_text(encoding="utf-8"))


# ---------------- 自评 flag：canonical 归一化（gflash_web 与 gflash 视为同一模型） ----------------

def cand_gens137(set_name):
    return {"a": sorted({CFG137["gen"], CFG137["chooser"]}),
            "b": [r134.RUN124_GEN],
            "c": [r134.BASELINE_GEN.get(set_name, "?")]}


def self_flag137(set_name, judge):
    cj = canonical_model(judge)
    hits = [c for c, gens in cand_gens137(set_name).items()
            if cj in {canonical_model(g) for g in gens}]
    return ",".join(hits) if hits else "否"


r134.cand_gens = cand_gens137
r134.self_flag = self_flag137


# ---------------- 调用层：experiment_calls.call + wrapper 级断点短路 ----------------

def _resume_hit(step, key, model, prompt):
    """cache_<step>_exact.json 里已有同 key/model/prompt 全文 sha 的 parse_ok 记录即命中。"""
    f = OUT_DIR / ("cache_%s_exact.json" % step)
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None
    h = sha256s(prompt)
    for rec in data.get("records", []):
        if (rec.get("parse_ok") and list(rec.get("key") or []) == list(key)
                and rec.get("model") == model and rec.get("prompt_sha256") == h):
            hit = dict(rec)
            hit["cached"] = True
            return hit
    return None


def call137(step, core, model, prompt, parse_fn, key, prompt_version, extra=None):
    """与 run134.call 同签名；新调用走 experiment_calls.call，同身份解析成功则短路零调用。"""
    key = list(key)
    hit = _resume_hit(step, key, model, prompt)
    if hit is not None:
        return hit
    CALLS["n"] += 1
    rec = experiment_calls.call(
        str(OUT_DIR), step, core, model, prompt, parse_fn, key, prompt_version,
        prompt_template=r134.TPL_PATHS.get(prompt_version, prompt_version),
        extra=dict(extra or {}, diag137=True), work_key=r134.WORK_KEY, work_name=r134.WORK_NAME)
    return rec


r134.call = call137  # stage_* 经此调用；旧 Store/caches 不再使用


# ---------------- 运行 ----------------

def run_stages137(stages, workers):
    r134.OUT_DIR = OUT_DIR
    r134.RUN_ID = RUN_ID
    r134.run_stages([s for s in stages if s != "report"], workers)
    if "report" in stages:
        stage_report137()


def stage_report137():
    r134.OUT_DIR = OUT_DIR
    r134.stage_report()
    p = OUT_DIR / "report.md"
    text = p.read_text(encoding="utf-8")
    text = text.replace("# run134 E7 诊断性整篇样稿（Op.60；诊断用，不进 production）",
                        "# run137 E7 Flash 独立诊断（Op.60；诊断用，不代替 GPT，不进 production）",
                        1)
    S = rjson("surface.json")
    reg, recs = S["items"], S["records"]
    L = ["", "## 7. 屏幕 lifecycle（KEEP/RETIRE/REPLACE/APPEND；locator=条目 uid）", ""]
    for r in recs:
        retired, show = r["retired"], r["show"]
        if retired and show:
            life = "REPLACE"
        elif show:
            life = "APPEND"
        elif retired:
            life = "RETIRE"
        else:
            life = "KEEP"
        L.append("- 第 %d 段 %s：keep=%s show=%s retired=%s" % (
            r["k"], life,
            ",".join(r["keep"]) if r["keep"] else "—",
            ",".join(show) if show else "—",
            ",".join(retired) if retired else "—"))
    L += ["", "## 8. 上屏的主 WHY（[因为前面]/[更深] 全列，不隐藏）", ""]
    n = 0
    for r in recs:
        for u in r["show"]:
            if reg[u]["kind"] in ("因为前面", "更深"):
                n += 1
                L.append("- %s 第 %d 段 %s" % (u, r["k"], r134.tagged(reg[u])))
    if not n:
        L.append("（无）")
    L += ["", "## 9. 缺项与阻塞（缺席绝不写 DONE）", "",
          "- 两 w（gpt56w/gpt6w）新鲜公平对照：缺席（run135 post_submit_ambiguous 全局 hold 阻塞）。",
          "- Muse 评审：缺席（待主会话 T3 派发；盲审包见 `muse_review_pack.json`）。",
          "- 全阵容最终裁决：阻塞（等两 w 解 hold + Muse 评审归位）。",
          "- c 组两套基线均出自 run132 V2A+Gemini 基线；Op.60 为重建锚，非原始 V2A 真原稿。",
          "- 本诊断不代替 GPT，不切 production，不是新模型公平赛。", ""]
    p.write_text(text + "\n".join(L), encoding="utf-8")


# ---------------- 盲审包导出（Muse 待派；two-w 可导出但不提交） ----------------

PACK_SLOTS = (("muse_pending", 900, "PENDING - 待主会话 T3 派发"),
              ("twow_held", 950, "HELD - run135 post_submit_ambiguous 全局 hold，未提交执行"))


def export_packs():
    import random as _random
    sets = r134.compare_inputs()
    packs = {}
    for slot, base, status in PACK_SLOTS:
        tasks = []
        for si, cname in enumerate(sorted(sets)):
            s = sets[cname]
            seed = r134.SEED_COMPARE + 100 * si + base
            order0 = ["a", "b", "c"]
            _random.Random(seed).shuffle(order0)
            for rr in range(r134.JUDGE_RUNS):
                order = order0[rr:] + order0[:rr]
                mapping = dict(zip(r134.POS, order))
                prompt = r134.fill(r134.TPL["E7_COMPARE_v0"], WORK=r134.WORK_NAME,
                                   A=s["texts"][order[0]], B=s["texts"][order[1]], C=s["texts"][order[2]])
                tasks.append({"set": cname, "slot": slot, "run": rr, "seed": seed,
                              "mapping": mapping, "prompt": prompt, "prompt_sha256": sha256s(prompt)})
        pack = {"run_id": RUN_ID, "status": status, "slot": slot,
                "template": "E7_COMPARE_v0", "template_sha256": sha256s(r134.TPL["E7_COMPARE_v0"]),
                "template_path": r134.TPL_PATHS["E7_COMPARE_v0"],
                "work": r134.WORK_NAME, "positions": list(r134.POS),
                "seed_scheme": "SEED_COMPARE + 100*set_index + %d + run（循环轮换）" % base,
                "candidates": {cname: {
                    "a": {"note": "本稿读者视图（gen/chooser=gflash）", "text": s["texts"]["a"]},
                    "b": {"note": "run124 生产稿 B 读者视图（gen=gpt56w）", "text": s["texts"]["b"]},
                    "c": {"note": "run132 V2A+Gemini 基线；Op.60 为重建锚，非原始 V2A 真原稿",
                          "source": s["c_source"], "c_removed_leak_lines": len(s["c_removed_lines"]),
                          "text": s["texts"]["c"]}}
                    for cname, s in sorted(sets.items())},
                "tasks": tasks}
        name = "muse_review_pack.json" if slot == "muse_pending" else "twow_review_pack.json"
        wjson(name, pack)
        packs[slot] = {"file": name, "tasks": len(tasks)}
    return packs


# ---------------- manifest（来源 sha、producer 未知限制、timeout/protect 停理由） ----------------

def write_manifest137(packs):
    r134.OUT_DIR = OUT_DIR
    man = r134.write_manifest({})
    man["script"] = {"runs/%s/go.py" % RUN_ID: sha256s((THIS_DIR / "go.py").read_text(encoding="utf-8")),
                     "runs/run134_e7_diag/go.py (read-only base)": man["script"].get("runs/run134_e7_diag/go.py")}
    stops = {"queue_stop": 0, "meta_error": 0, "frozen_marker": 0, "parse_fail": 0}
    for f in sorted(OUT_DIR.glob("cache_*_exact.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for rec in data.get("records", []):
            for a in rec.get("attempts", []):
                if a.get("queue_stop"):
                    stops["queue_stop"] += 1
                if a.get("meta_error"):
                    stops["meta_error"] += 1
                if "frozen" in str(a.get("parse_error") or ""):
                    stops["frozen_marker"] += 1
            if not rec.get("parse_ok"):
                stops["parse_fail"] += 1
    man["extra"] = {
        "base_run": "run134_e7_diag（只读复用架构；旧文件未改）",
        "config": {"gen": CFG137["gen"], "chooser": CFG137["chooser"],
                   "auditors": list(CFG137["auditors"]), "judges": list(CFG137["judges"]),
                   "history": CFG137["history"]},
        "history_producer": "unknown（run130 steps.json 系历史产物，无 producer identity；只记来源 sha）",
        "reconstruction_note": "c 组两套基线均出自 run132 V2A+Gemini 基线；Op.60 为重建锚，非原始 V2A 真原稿",
        "scope": "Flash E7 独立诊断；不代替 GPT；不切 production；不是新模型公平赛",
        "pending": ["two-w 新鲜公平对照（run135 hold 阻塞）", "Muse 评审（待主会话 T3 派）",
                    "全阵容最终裁决"],
        "stop_reasons": stops,
        "timeouts": {"gflash": 3600, "luna_noweb": 3600},
        "self_flags_canonical": True,
        "new_calls_via_experiment_calls": CALLS["n"],
        "packs": packs,
    }
    wjson("run_manifest.json", man)
    return man


# ---------------- 完整性：按 stage/job/window/每评审严格检查 ----------------

def verify137():
    """返回 (ok, problems)。失败/漏评审/缺包 → 不写 DONE（写 FAILED）；缺两w/Muse → PENDING（永不 DONE）。"""
    problems = []
    try:
        W, M, S = rjson("why.json"), rjson("mech.json"), rjson("surface.json")
    except Exception as e:
        return False, ["缺阶段产物：%s" % e]
    for name in ("render.json", "compare.json", "report.md",
                 "muse_review_pack.json", "twow_review_pack.json"):
        if not (OUT_DIR / name).exists():
            problems.append("缺产物 %s" % name)
    if len(W.get("records", [])) != r134.K_EXPECTED - 1:
        problems.append("why 记录数 %d，期望 %d" % (len(W.get("records", [])), r134.K_EXPECTED - 1))
    problems += ["why k%d 失败：%s" % (r["k"], r.get("parse_error")) for r in W.get("records", [])
                 if not r.get("parse_ok")]
    if len(M.get("records", [])) != r134.K_EXPECTED:
        problems.append("mech 记录数 %d，期望 %d" % (len(M.get("records", [])), r134.K_EXPECTED))
    problems += ["mech k%d 失败" % r["k"] for r in M.get("records", []) if not r.get("parse_ok")]
    if len(S.get("records", [])) != r134.K_EXPECTED:
        problems.append("surface 记录数 %d，期望 %d" % (len(S.get("records", [])), r134.K_EXPECTED))
    problems += ["surface k%d 失败" % r["k"] for r in S.get("records", []) if r.get("failed")]
    try:
        C = rjson("compare.json")
    except Exception as e:
        return False, problems + ["compare.json 不可读：%s" % e]
    n_exp = len(r134.BASELINES) * len(CFG137["judges"]) * r134.JUDGE_RUNS
    if len(C.get("records", [])) != n_exp:
        problems.append("compare 记录数 %d，期望 %d" % (len(C.get("records", [])), n_exp))
    for s in sorted(r134.BASELINES):
        for j in CFG137["judges"]:
            rs = [r for r in C.get("records", []) if r["set"] == s and r["judge"] == j]
            if len(rs) != r134.JUDGE_RUNS:
                problems.append("漏评审 %s/%s：%d 次，期望 %d" % (s, j, len(rs), r134.JUDGE_RUNS))
                continue
            if any(not r.get("parse_ok") for r in rs):
                problems.append("评审失败 %s/%s" % (s, j))
            for c in "abc":  # 三个顺序：每候选在 3 次里各占一次甲/乙/丙
                got = sorted(next(p for p, v in r["mapping"].items() if v == c) for r in rs)
                if got != sorted(r134.POS):
                    problems.append("位置轮换不全 %s/%s/候选%s：%s" % (s, j, c, got))
    if "luna_noweb" not in CFG137["judges"]:
        problems.append("缺独立 Luna 评审")
    for r in C.get("agg", []):  # canonical 自评 flag 抽查
        if r["set"] == "c_gflash_s1" and r["judge"] == "gflash" and r.get("judge_is_generator_of") != "a,c":
            problems.append("canonical 自评 flag 错误：%s" % r)
        if r["judge"] == "luna_noweb" and r.get("judge_is_generator_of") != "否":
            problems.append("Luna 独立性 flag 错误：%s" % r)
    try:
        P = rjson("muse_review_pack.json")
        n_pt = len(r134.BASELINES) * r134.JUDGE_RUNS
        n_tasks = [t for t in P.get("tasks", []) if t["slot"] == "muse_pending"]
        if len(n_tasks) != n_pt:
            problems.append("muse pack 任务数 %d，期望 %d" % (len(n_tasks), n_pt))
    except Exception as e:
        problems.append("muse pack 不可读：%s" % e)
    return (len(problems) == 0), problems


PENDING_TEXT = """stages=%s at %s new_calls=%d
缺项（缺席绝不写 DONE）：
- two-w（gpt56w/gpt6w）新鲜公平对照：缺席（run135 post_submit_ambiguous 全局 hold 阻塞）
- Muse 评审：缺席（待主会话 T3 派发；见 muse_review_pack.json）
- 全阵容最终裁决：阻塞
本诊断不代替 GPT，不切 production，不是新模型公平赛。
"""


def write_completion137(stages):
    ok, problems = verify137()
    for n in ("DONE", "FAILED", "COMPLETION_PENDING"):
        try:
            (OUT_DIR / n).unlink()
        except OSError:
            pass
    if not ok:
        (OUT_DIR / "FAILED").write_text("stages=%s at %s\n%s" % (
            stages, time.strftime("%m-%d %H:%M:%S"), "\n".join(problems)), encoding="utf-8")
        return False, problems
    (OUT_DIR / "COMPLETION_PENDING").write_text(
        PENDING_TEXT % (stages, time.strftime("%m-%d %H:%M:%S"), CALLS["n"]), encoding="utf-8")
    return True, []


STAGES = ("why", "mech", "surface", "render", "compare", "report")


def run_all(out_dir, stages, workers):
    global OUT_DIR
    OUT_DIR = Path(out_dir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r134.OUT_DIR = OUT_DIR
    r134.RUN_ID = RUN_ID
    run_stages137(list(stages), workers)
    packs = {}
    if "report" in stages:
        packs = export_packs()
        write_manifest137(packs)
        return write_completion137(list(stages))
    return True, []


# ---------------- mock（纯假 run_job；临时目录；不碰真实目录，不调 CLI） ----------------

def run_mock137(workers):
    import unittest.mock as _mock
    tmp = Path(tempfile.mkdtemp(prefix="run137_mock_"))
    fake = r134.fake_run_job
    count = {"n": 0}

    def counting_fake(run_dir, job, timeout=3600):
        count["n"] += 1
        return fake(run_dir, job, timeout=timeout)

    import runner as _runner
    global OUT_DIR
    real_out, real_calls = OUT_DIR, CALLS["n"]
    try:
        with _mock.patch.object(_runner, "run_job", counting_fake):
            ok, problems = run_all(tmp, STAGES, workers)
        assert ok, problems
        first = count["n"]
        assert first > 0, "mock 应产生新调用"
        W, M, S = rjson("why.json"), rjson("mech.json"), rjson("surface.json")
        assert len(W["records"]) == r134.K_EXPECTED - 1 and all(r["parse_ok"] for r in W["records"])
        assert len(M["records"]) == r134.K_EXPECTED and all(r["parse_ok"] for r in M["records"])
        assert len(S["records"]) == r134.K_EXPECTED and all(not r["failed"] for r in S["records"])
        C = rjson("compare.json")
        assert len(C["records"]) == len(r134.BASELINES) * len(CFG137["judges"]) * r134.JUDGE_RUNS
        assert all(r["parse_ok"] for r in C["records"])
        assert (OUT_DIR / "COMPLETION_PENDING").exists() and not (OUT_DIR / "DONE").exists()
        man = rjson("run_manifest.json")
        assert man["extra"]["history_producer"].startswith("unknown"), man["extra"]
        assert "stop_reasons" in man["extra"] and "reconstruction_note" in man["extra"]
        # 断点续跑：再跑一遍必须零新调用（wrapper 短路命中）
        with _mock.patch.object(_runner, "run_job", counting_fake):
            ok2, problems2 = run_all(tmp, STAGES, workers)
        assert ok2, problems2
        assert count["n"] == first, "resume 新增调用 %d" % (count["n"] - first)
        print("MOCK137 OK: calls=%d (rerun +0); pending缺项已落 completion；DONE 未写" % first, flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        OUT_DIR, CALLS["n"] = real_out, real_calls
        r134.OUT_DIR, r134.RUN_ID = real_out, RUN_ID
    leftovers = [n for n in ("outputs", "DONE", "FAILED", "COMPLETION_PENDING", "why.json",
                             "cache_why_exact.json") if (RUN_DIR / n).exists()]
    assert not leftovers, "mock 污染真实目录：%s" % leftovers
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES, default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        print("run137 不提供真实 runner 冒烟（离线诊断 run；工程测试只用 --mock）", flush=True)
        return 2
    if a.mock:
        return 0 if run_mock137(a.workers) else 1
    stages = [a.stage] if a.stage else list(STAGES)
    t0 = time.time()
    try:
        ok, problems = run_all(RUN_DIR, stages, a.workers)
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "FAILED").write_text("stages=%s at %s\n%s" % (
            stages, time.strftime("%m-%d %H:%M:%S"), tb), encoding="utf-8")
        return 1
    print("run137 stages=%s ok=%s in %.1fs new_calls=%d" % (
        stages, ok, time.time() - t0, CALLS["n"]), flush=True)
    if not ok:
        print("\n".join(problems), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
