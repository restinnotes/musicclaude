# run150 = run134 rerun after false-positive queue holds voided run134 (10-09)
"""R2 run150_e7_diag：E7 诊断性整篇样稿（Op.60，诊断用，永不进 production）。

阶段（每段可单独重跑；缓存键 = ("run150", 阶段, 逻辑键) + 模型键 + 完整提示词 sha256；只缓存解析成功；
每逻辑调用最多 3 次 = 重试 ≤2，runner 内部 max_attempts=1）：
  why     WHY_GATE_v4，k=2..23；HISTORY = 历史链到 k-1 为止的清单（run130 拼法）；differs=true → [因为前面]
  mech    MECH_v1 生成（每颗珠子）+ MECH_AUDIT_v0 双审核；任一家判 manufactured/imported 即丢；存活 → [更深]
  surface E7_SURFACE_v0 逐颗串行；新屏幕 = keep 的 S 项 + show 的新项；未 keep 的 S 项 = 撤下
  render  surface__<chooser>__op60.md（内部稿）+ reading__<chooser>__op60.md（读者所见）+ 统计
  compare E7_COMPARE_v0 三方盲比：(a) 本稿读者视图 / (b) run124 生产稿 B 读者视图 / (c) run132 V2A+Gemini 基线
          两套 c（gpro_web s3、gflash_web s1）；每评审 3 次，位置甲乙丙循环轮换；记 seed 与映射
  report  report.md + run_manifest.json + DONE/FAILED
why 与 mech 互不依赖（全量时并行）；surface 需要两者。

用法（cwd 为仓库根）：
  python -I runs\\run150_e7_diag\\go.py [--gen-model gpt56w] [--chooser gpt56w] [--stage why|mech|surface|render|compare|report]
        [--auditors luna_noweb,gpro] [--judges luna_noweb,gpro_web,gpt6w] [--history-source run130:gpt56w] [--workers 6]
  python -I runs\\run150_e7_diag\\go.py --mock     # 假 run_job 全流程 + 断言（临时目录，验完即删）
  python -I runs\\run150_e7_diag\\go.py --smoke    # 极短真实冒烟（产物留在 _smoke/）
环境：MUSIC_WEB_ROUTE 未设时本脚本设为 gpt2（gpt56w/gpt6w 走 gpt2_adapter）；也可用 RUN134_GEN / RUN134_CHOOSER /
  RUN134_AUDITORS / RUN134_JUDGES / RUN134_HISTORY 覆盖默认值。实际所用模型键写入 run_manifest.json。
约束：只写本 run 目录；不改 prompts/、tools/runner.py、旧 runs；stdlib only。
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from collections import Counter
from pathlib import Path

os.environ.setdefault("MUSIC_WEB_ROUTE", "gpt2")  # 必须在 import runner 之前（runner 在导入时读路由）

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run150_e7_diag"
RUN_DIR = ROOT / "runs" / RUN_ID
sys.path.insert(0, str(ROOT / "tools"))
import runner  # noqa: E402  (只读常量与 run_job；不修改 tools/)
from stage import WORKS  # noqa: E402

WORK_KEY = "op60"
WORK_NAME = WORKS[WORK_KEY]
K_EXPECTED = 23
BEADS_REL = "runs/run130_thread_e6/beads_clean.md"
RUN124_REL = "runs/run124_render/surface__B__gpt56w__op60.md"
RUN124_GEN = "gpt56w"  # run124 生产稿 B 的生成/选择模型（文件名 surface__B__gpt56w）
BASELINE_GEN = {"c_gpro_s3": "gpro_web", "c_gflash_s1": "gflash_web"}
BASELINES = {  # 两套 (c)，分别成一组三方比较
    "c_gpro_s3": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gpro_web__s3.md",
    "c_gflash_s1": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gflash_web__s1.md",
}
TPL_PATHS = {
    "WHY_GATE_v4": "prompts/versions/WHY_GATE_v4.txt",
    "MECH_v1": "prompts/tooling/MECH_v1.txt",
    "MECH_AUDIT_v0": "prompts/tooling/MECH_AUDIT_v0.txt",
    "E7_SURFACE_v0": "prompts/versions/E7_SURFACE_v0.txt",
    "E7_COMPARE_v0": "prompts/tooling/E7_COMPARE_v0.txt",
}
TPL = {k: (ROOT / v).read_text(encoding="utf-8") for k, v in TPL_PATHS.items()}

CFG = {  # main() 用 CLI/env 覆盖
    "gen": os.environ.get("RUN134_GEN", "gpt56w"),
    "chooser": os.environ.get("RUN134_CHOOSER", "gpt56w"),
    "auditors": tuple(os.environ.get("RUN134_AUDITORS", "luna_noweb,gpro").split(",")),
    "judges": tuple(os.environ.get("RUN134_JUDGES", "gpt56w,gpt6w,opus,luna_noweb,gpro_web").split(",")),
    "history": os.environ.get("RUN134_HISTORY", "run130:gpt56w"),
}
SEED_COMPARE = 134060
JUDGE_RUNS = 3
POS = ("甲", "乙", "丙")
FORBID = ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"]
MAX_ATTEMPTS = 3  # 重试 ≤2
WEB_GPT = ("gpt56w", "gpt6w")
TMO_GPT, TMO_OTHER = 1800, 3600
GPT_SEM = threading.Semaphore(1)  # 进程内网页 GPT 单并发（runner 另有跨进程 gpt2web 槽）
FROZEN = ("temporarily frozen", "Temporary Chat activation control was not found", "incomplete_response")
AUDIT_CLASSES = ("insight", "restatement", "manufactured", "imported")
AUDIT_DROP = ("manufactured", "imported")
ACTIONS = ("保持", "补充", "更新", "沉默")
KIND_ORDER = ("认", "此刻", "因为前面", "更深")
LEAK_PAT = re.compile(r"(?i)(gemini|gpt|claude|opus|luna|gpro|gflash|muse|sonnet|run\d{2,3}|v2a|E7_|ATTN_)")

OUT_DIR = RUN_DIR  # mock / smoke 时切换
MOCK = {"on": False, "calls": 0}
LOCK = threading.Lock()
CALLS = {"n": 0, "by": {}}
RUN_JOB = runner.run_job  # mock 时替换为假 run_job


# ---------------- 通用 ----------------

def sha256s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        cp = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, cwd=str(ROOT), timeout=30,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = cp.stdout.decode("utf-8", "replace").strip()
        return out if cp.returncode == 0 and out else "unknown"
    except Exception as e:
        return "unknown (%s)" % type(e).__name__


def fill(tpl, **kv):
    out = tpl
    for k, v in kv.items():
        out = out.replace("{{" + k + "}}", str(v))
    if re.search(r"\{\{[A-Z_]+\}\}", out):
        raise ValueError("unfilled placeholder remains")
    return out


def bump(step, model, field, n=1, secs=0.0):
    with LOCK:
        d = CALLS["by"].setdefault("%s|%s" % (step, model),
                                   {"calls": 0, "retries": 0, "cached": 0, "failed": 0, "seconds": 0.0})
        d[field] = d.get(field, 0) + n
        if field == "calls":
            CALLS["n"] += n
            d["seconds"] = round(d["seconds"] + secs, 1)


def extract_json_obj(text):
    if not isinstance(text, str) or not text.strip():
        return False, None, "empty output"
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        return False, None, "no braces found"
    try:
        return True, json.loads(text[i:j + 1]), None
    except Exception as e:
        return False, None, "%s: %s" % (type(e).__name__, e)


def extract_json_arr(text):
    if not isinstance(text, str) or not text.strip():
        return False, None, "empty output"
    i, j = text.find("["), text.rfind("]")
    if i < 0 or j <= i:
        return False, None, "no brackets found"
    try:
        val = json.loads(text[i:j + 1])
    except Exception as e:
        return False, None, "%s: %s" % (type(e).__name__, e)
    if not isinstance(val, list):
        return False, None, "top level is not an array"
    return True, val, None


def wjson(name, obj):
    p = OUT_DIR / name
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def rjson(name):
    return json.loads((OUT_DIR / name).read_text(encoding="utf-8"))


# ---------------- 珠子切分（与 run130 split_beads 逐字一致）+ 条目 ----------------

BEAD_HEAD = re.compile(r"^###\s+(.*)$", re.M)


def mm_start_of(title):
    m = re.search(r"m{1,2}\.\s*(\d+)", title or "") or re.search(r"(\d+)", title or "")
    return int(m.group(1)) if m else None


def split_beads(text):
    """按 '### ' 切珠子；给 Thread 的文字 = 标题行 +【此刻】块（不含【前后关系候选】）。"""
    ms = list(BEAD_HEAD.finditer(text))
    beads = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        chunk = text[m.start():end]
        title = m.group(1).strip()
        a = chunk.find("【此刻】")
        b = chunk.find("【前后关系候选】", a + 1 if a >= 0 else 0)
        err = None
        if a < 0:
            now = ""
            err = "缺【此刻】"
        else:
            now = chunk[a + len("【此刻】"): b if b >= 0 else len(chunk)]
            if b < 0:
                err = "缺【前后关系候选】（此刻块取到珠子末尾）"
        lines = [l.strip() for l in now.split("\n") if l.strip()]
        body = title + "\n【此刻】\n" + "\n".join(lines)
        beads.append({"k": i + 1, "title": title, "text": body, "mm_start": mm_start_of(title),
                      "n_now_lines": len(lines), "has_now": a >= 0, "has_rel": b >= 0, "split_error": err,
                      "now_lines": lines})
    return beads


def now_items(bead):
    """【此刻】块里每个 '- ' 条目一条（保留内部标记如【先后】【另一种理解】）；非 '- ' 行并入上一条。"""
    items = []
    for l in bead["now_lines"]:
        if l.startswith("- "):
            items.append(l[2:].strip())
        elif items:
            items[-1] = items[-1] + " " + l
        else:
            items.append(l)
    return [x for x in items if x]


def time_of(title):
    m = re.match(r"^\s*(m{1,2}\.\s*\d+(?:\s*[–\-—]\s*\d+)?)", title or "")
    return m.group(1) if m else (title or "").split(" ")[0]


def load_beads():
    beads = split_beads((ROOT / BEADS_REL).read_text(encoding="utf-8"))
    if len(beads) != K_EXPECTED:
        raise RuntimeError("beads=%d expected %d" % (len(beads), K_EXPECTED))
    return beads


# ---------------- 历史清单来源（可插拔） ----------------

def _hist_run130(arg):
    rel = "runs/run130_thread_e6/steps.json"
    d = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    recs = [r for r in d["steps"] if r.get("model") == arg and r.get("work") == WORK_KEY]
    return rel, {r["k"]: r.get("inventory_after") or [] for r in recs}


def _hist_run133(arg):
    rel = "runs/run133_thread_spec/chains.json"
    d = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    recs = d["chains"][arg]
    return rel, {r["k"]: r.get("inventory_after") or [] for r in recs}


HISTORY_LOADERS = {"run130": _hist_run130, "run133": _hist_run133}


def load_history(source):
    """source = '<loader>:<chain>'；返回 (rel_path, {k: 第 k 步之后的清单})。"""
    name, _, arg = source.partition(":")
    if name not in HISTORY_LOADERS:
        raise ValueError("unknown history source %r (known: %s)" % (source, ", ".join(HISTORY_LOADERS)))
    rel, inv = HISTORY_LOADERS[name](arg)
    missing = [k for k in range(1, K_EXPECTED) if k not in inv]
    if missing:
        raise RuntimeError("history %s missing steps %s" % (source, missing))
    return rel, inv


def history_text(inventory):
    """与 run130/run119 传给下一步的 HISTORY 拼法一致。"""
    if not inventory:
        return "（还没有）"
    return "\n".join("- %s（来自：%s）" % (it["change"], it["from"]) for it in inventory)


# ---------------- 调用与缓存 ----------------

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.recs, self.by_key = [], {}
        if self.path.exists():
            try:
                for r in json.loads(self.path.read_text(encoding="utf-8")).get("records", []):
                    self.recs.append(r)
                    if r.get("parse_ok"):
                        self.by_key[self._k(r["key"], r["model"], r["prompt_sha256"])] = r
            except Exception:
                pass

    @staticmethod
    def _k(key, model, h):
        return (json.dumps(key, sort_keys=True, ensure_ascii=False), model, h)

    def get(self, key, model, h):
        return self.by_key.get(self._k(key, model, h))

    def put(self, rec):
        with LOCK:
            self.recs.append(rec)
            if rec.get("parse_ok"):
                self.by_key[self._k(rec["key"], rec["model"], rec["prompt_sha256"])] = rec
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"run_id": RUN_ID, "records": self.recs}, ensure_ascii=False, indent=1),
                           encoding="utf-8")
            tmp.replace(self.path)


STORES = {}


def store(step):
    with LOCK:
        if step not in STORES:
            STORES[step] = Store(OUT_DIR / ("cache_%s.json" % step))
        return STORES[step]


def _read_output(meta):
    try:
        rel = (meta or {}).get("output_file")
        if rel and (OUT_DIR / str(rel)).exists():
            return (OUT_DIR / str(rel)).read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def call(step, core, model, prompt, parse_fn, key, prompt_version, extra=None):
    """一次逻辑调用（同一模型最多 MAX_ATTEMPTS 次）。返回 rec。"""
    h = sha256s(prompt)
    key = ["run150", step] + list(key)
    st = store(step)
    hit = st.get(key, model, h)
    if hit is not None:
        bump(step, model, "cached")
        rec = dict(hit)
        rec["cached"] = True
        return rec
    rec = {"key": key, "core": core, "model": model, "prompt_sha256": h, "prompt_version": prompt_version,
           "prompt_template": TPL_PATHS.get(prompt_version, prompt_version), "attempts": [], "cached": False,
           "parsed": None, "output": None, "output_file": None, "parse_ok": False, "parse_error": None}
    timeout = TMO_GPT if model in WEB_GPT else TMO_OTHER
    n, secs = 0, 0.0
    for att in range(MAX_ATTEMPTS):
        jid = (core if att == 0 else "%s__retry%d" % (core, att)) + "__h" + h[:10]
        job = {"job_id": jid, "branch": step, "model_key": model, "prompt": prompt,
               "prompt_version": prompt_version, "prompt_template": rec["prompt_template"],
               "work_key": WORK_KEY, "work_name": WORK_NAME, "sample": 1,
               "extra": dict(extra or {}, attempt=att), "forbid_tools": list(FORBID), "max_attempts": 1}
        try:
            if model in WEB_GPT:
                with GPT_SEM:
                    meta = RUN_JOB(str(OUT_DIR), job, timeout=timeout)
            else:
                meta = RUN_JOB(str(OUT_DIR), job, timeout=timeout)
        except Exception as e:
            meta = {"job_id": jid, "status": "failed", "error": "%s: %s" % (type(e).__name__, e)}
        n += 1
        try:
            secs += float((meta or {}).get("seconds") or 0.0)
        except Exception:
            pass
        out = _read_output(meta)
        entry = {"job_id": jid, "status": (meta or {}).get("status"), "meta_error": (meta or {}).get("error"),
                 "output_chars": len(out), "output_file": (meta or {}).get("output_file")}
        if isinstance(meta, dict) and meta.get("status") == "ok":
            if any(p in out for p in FROZEN):
                parsed, err = None, "frozen/activation/incomplete marker in output"
            else:
                parsed, err = parse_fn(out)
        else:
            parsed, err = None, "run failed: %s" % ((meta or {}).get("error"))
        entry["parse_ok"] = parsed is not None
        entry["parse_error"] = err
        rec["attempts"].append(entry)
        print("[%s %s %s] att%d ok=%s %s" % (step, model, core, att, parsed is not None, err or ""), flush=True)
        if parsed is not None:
            rec.update({"parsed": parsed, "output": out, "parse_ok": True, "output_file": entry["output_file"]})
            break
    bump(step, model, "calls", n, secs)
    bump(step, model, "retries", max(0, n - 1))
    if not rec["parse_ok"]:
        rec["parse_error"] = rec["attempts"][-1]["parse_error"] if rec["attempts"] else "no attempts"
        bump(step, model, "failed")
    st.put(dict(rec))
    return rec


def pmap(fn, args, workers):
    out = [None] * len(args)
    with cf.ThreadPoolExecutor(max_workers=max(1, min(workers, len(args) or 1))) as ex:
        futs = {ex.submit(fn, a): i for i, a in enumerate(args)}
        for f in cf.as_completed(futs):
            out[futs[f]] = f.result()
    return out


# ---------------- 第 1 段：why（WHY_GATE_v4） ----------------

def build_why_prompt(k, beads, hist_inv):
    beads_text = "\n\n".join("第 %d 段：%s" % (b["k"], b["text"]) for b in beads[:k])
    p = (TPL["WHY_GATE_v4"].replace("{{WORK}}", WORK_NAME)
         .replace("{{K}}", str(k))
         .replace("{{K_PREV}}", str(k - 1))
         .replace("{{BEADS}}", beads_text)
         .replace("{{HISTORY}}", history_text(hist_inv)))
    if "{{" in p:
        raise ValueError("unfilled placeholder remains in why prompt")
    return p


def parse_why(out):
    ok, obj, err = extract_json_obj(out)
    if not ok:
        return None, err
    d = obj.get("differs") if isinstance(obj, dict) else None
    if isinstance(d, str) and d.strip().lower() in ("true", "false"):
        d = d.strip().lower() == "true"
    if not isinstance(d, bool):
        return None, "differs is not a bool"
    s = obj.get("sentence", "")
    s = (s if isinstance(s, str) else str(s)).strip()
    if d and (not s or s == "无"):
        return None, "differs=true but sentence empty"
    return {"differs": d, "sentence": s}, None


def stage_why(workers):
    beads = load_beads()
    hist_rel, inv = load_history(CFG["history"])
    gen = CFG["gen"]

    def one(k):
        prompt = build_why_prompt(k, beads, inv[k - 1])
        r = call("why", "why150__%s__k%02d" % (gen, k), gen, prompt, parse_why,
                 [CFG["history"], k], "WHY_GATE_v4", {"k": k, "history": CFG["history"]})
        p = r.get("parsed") or {}
        return {"k": k, "title": beads[k - 1]["title"], "model": gen, "parse_ok": bool(r.get("parse_ok")),
                "cached": bool(r.get("cached")), "parse_error": r.get("parse_error"),
                "differs": p.get("differs"), "sentence": p.get("sentence"),
                "history_n": len(inv[k - 1]), "prompt_sha256": r.get("prompt_sha256"),
                "output_file": r.get("output_file"), "attempts": r.get("attempts")}

    recs = pmap(one, list(range(2, K_EXPECTED + 1)), workers)
    wjson("why.json", {"run_id": RUN_ID, "gen_model": gen, "history_source": CFG["history"],
                       "history_file": hist_rel, "records": recs})
    return recs


# ---------------- 第 2 段：mech（MECH_v1 + MECH_AUDIT_v0） ----------------

def build_mech_prompt(title, items):
    numbered = "\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(items))
    return fill(TPL["MECH_v1"], WORK=WORK_NAME, MM=title, ITEMS=numbered)


def parse_mech_fn(n_items):
    def fn(out):
        ok, val, err = extract_json_arr(out)
        if not ok:
            return None, err
        if len(val) > 2:
            return None, "more than 2 relations (%d)" % len(val)
        res = []
        for i, it in enumerate(val):
            if not isinstance(it, dict):
                return None, "item %d is not an object" % i
            rel = str(it.get("relation", "")).strip()
            if not rel:
                return None, "item %d has empty relation" % i
            ex = it.get("explains", [])
            if not isinstance(ex, list):
                return None, "item %d explains is not a list" % i
            nums = []
            for e in ex:
                try:
                    v = int(e)
                except Exception:
                    continue
                if 1 <= v <= n_items and v not in nums:
                    nums.append(v)
            if not nums:
                return None, "item %d explains has no valid item numbers" % i
            res.append({"relation": rel, "explains": sorted(nums),
                        "new_understanding": str(it.get("new_understanding", "")).strip()})
        return res, None
    return fn


def build_audit_prompt(title, items, rel):
    item_lines = "\n".join("[%d] %s" % (i + 1, t) for i, t in enumerate(items))
    return fill(TPL["MECH_AUDIT_v0"], WORK=WORK_NAME, MM=title, ITEMS=item_lines,
                RELATION="%s——%s" % (rel["relation"], rel["new_understanding"]),
                EXPLAINS="、".join(str(e) for e in rel["explains"]))


def parse_audit(out):
    ok, val, err = extract_json_obj(out)
    if not ok:
        return None, err
    cls = str((val or {}).get("class", "")).strip().lower() if isinstance(val, dict) else ""
    if cls not in AUDIT_CLASSES:
        return None, "bad class: %r" % (val.get("class") if isinstance(val, dict) else val,)
    why = val.get("why", "")
    return {"class": cls, "why": (why if isinstance(why, str) else str(why)).strip()}, None


def stage_mech(workers):
    beads = load_beads()
    gen = CFG["gen"]

    def gen_one(b):
        items = now_items(b)
        if len(items) < 2:
            return {"k": b["k"], "skipped": "fewer than 2 items", "relations": [], "parse_ok": True}
        prompt = build_mech_prompt(b["title"], items)
        r = call("mech", "mech150__%s__k%02d" % (gen, b["k"]), gen, prompt, parse_mech_fn(len(items)),
                 [b["k"]], "MECH_v1", {"k": b["k"]})
        return {"k": b["k"], "title": b["title"], "model": gen, "n_items": len(items),
                "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
                "parse_error": r.get("parse_error"), "relations": r.get("parsed") or [],
                "output_file": r.get("output_file"), "attempts": r.get("attempts")}

    gens = pmap(gen_one, beads, workers)
    tasks = []
    for g in gens:
        for gi, rel in enumerate(g["relations"]):
            for au in CFG["auditors"]:
                tasks.append((g["k"], gi, au, rel))

    def audit_one(t):
        k, gi, au, rel = t
        b = beads[k - 1]
        prompt = build_audit_prompt(b["title"], now_items(b), rel)
        r = call("audit", "audit150__k%02d__r%d__%s" % (k, gi, au), au, prompt, parse_audit,
                 [k, gi, gen, rel["relation"]], "MECH_AUDIT_v0", {"k": k, "gidx": gi, "auditor": au})
        return {"k": k, "gidx": gi, "auditor": au, "parse_ok": bool(r.get("parse_ok")),
                "class": (r.get("parsed") or {}).get("class"), "why": (r.get("parsed") or {}).get("why"),
                "parse_error": r.get("parse_error"), "output_file": r.get("output_file")}

    audits = pmap(audit_one, tasks, workers)
    by = {}
    for a in audits:
        by.setdefault((a["k"], a["gidx"]), []).append(a)
    for g in gens:
        for gi, rel in enumerate(g["relations"]):
            av = by.get((g["k"], gi), [])
            verdicts = {a["auditor"]: (a["class"] if a["parse_ok"] else "audit_failed") for a in av}
            whys = {a["auditor"]: a["why"] for a in av}
            failed = [au for au, c in verdicts.items() if c == "audit_failed"]
            dropped_by = [au for au, c in verdicts.items() if c in AUDIT_DROP]
            rel.update({"verdicts": verdicts, "audit_why": whys,
                        "survives": not dropped_by and not failed and len(verdicts) == len(CFG["auditors"]),
                        "drop_reason": (("dropped by %s" % ",".join(dropped_by)) if dropped_by else
                                        ("audit failed: %s" % ",".join(failed)) if failed else None)})
    wjson("mech.json", {"run_id": RUN_ID, "gen_model": gen, "auditors": list(CFG["auditors"]),
                        "records": gens, "audits": audits})
    return gens


# ---------------- 第 3 段：surface（E7_SURFACE_v0 逐颗串行） ----------------

def build_candidates(beads, why_recs, mech_recs):
    """每颗珠子的候选：[认] 标题 / [此刻] 各条 / [因为前面] / [更深]。返回 {k: [item...]}。"""
    wy = {r["k"]: r for r in why_recs}
    mc = {r["k"]: r for r in mech_recs}
    out = {}
    for b in beads:
        k = b["k"]
        L = [{"uid": "k%02d_hd" % k, "kind": "认", "text": b["title"], "meta": {}}]
        for i, t in enumerate(now_items(b), 1):
            L.append({"uid": "k%02d_now%02d" % (k, i), "kind": "此刻", "text": t, "meta": {"item_no": i}})
        w = wy.get(k)
        if w and w.get("parse_ok") and w.get("differs") and w.get("sentence") and w["sentence"] != "无":
            L.append({"uid": "k%02d_why" % k, "kind": "因为前面", "text": w["sentence"], "meta": {}})
        m = mc.get(k) or {}
        for gi, rel in enumerate(m.get("relations") or []):
            if rel.get("survives"):
                L.append({"uid": "k%02d_mech%d" % (k, gi), "kind": "更深", "text": rel["relation"],
                          "meta": {"new_understanding": rel.get("new_understanding"),
                                   "explains": rel.get("explains"), "verdicts": rel.get("verdicts"),
                                   "audit_why": rel.get("audit_why")}})
        for i, it in enumerate(L, 1):
            it["k"] = k
            it["id"] = i
        out[k] = L
    return out


def tagged(it):
    return "[%s] %s" % (it["kind"], it["text"])


def build_surface_prompt(title, screen_items, cands):
    screen = "（空）" if not screen_items else "\n".join(
        "S%d. %s" % (i + 1, tagged(it)) for i, it in enumerate(screen_items))
    items = "\n".join("%d. %s" % (it["id"], tagged(it)) for it in cands)
    return fill(TPL["E7_SURFACE_v0"], WORK=WORK_NAME, MM=title, SCREEN=screen, ITEMS=items)


def parse_surface_fn(n_screen, n_items):
    def ids(v, lo, hi, s_prefix):
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("not a list")
        out = []
        for x in v:
            s = str(x).strip()
            if s_prefix:
                m = re.fullmatch(r"[Ss]\s*(\d+)", s) or re.fullmatch(r"(\d+)", s)
            else:
                m = re.fullmatch(r"(\d+)", s)
            if not m:
                raise ValueError("bad id %r" % (x,))
            iv = int(m.group(1))
            if not lo <= iv <= hi:
                raise ValueError("id %r out of range %d..%d" % (x, lo, hi))
            if iv not in out:
                out.append(iv)
        return out

    def fn(out):
        ok, obj, err = extract_json_obj(out)
        if not ok:
            return None, err
        if not isinstance(obj, dict):
            return None, "top level is not an object"
        a = str(obj.get("action", "")).strip()
        if a not in ACTIONS:
            return None, "unknown action %r" % (obj.get("action"),)
        try:
            keep = ids(obj.get("keep"), 1, n_screen, True)
            show = ids(obj.get("show"), 1, n_items, False)
            expand = ids(obj.get("expand"), 1, n_items, False)
            recap = ids(obj.get("recap"), 1, n_items, False)
        except ValueError as e:
            return None, "ids: %s" % e
        why = obj.get("why", "")
        return {"action": a, "keep": keep, "show": show, "expand": expand, "recap": recap,
                "why": (why if isinstance(why, str) else str(why)).strip()}, None
    return fn


def stage_surface(_workers):
    beads = load_beads()
    why = rjson("why.json")["records"]
    mech = rjson("mech.json")["records"]
    cands = build_candidates(beads, why, mech)
    reg = {it["uid"]: it for L in cands.values() for it in L}
    chooser = CFG["chooser"]
    screen = []  # uid 列表
    recs = []
    for b in beads:
        k = b["k"]
        sc_items = [reg[u] for u in screen]
        C = cands[k]
        prompt = build_surface_prompt(b["title"], sc_items, C)
        r = call("surface", "surf150__%s__k%02d" % (chooser, k), chooser, prompt,
                 parse_surface_fn(len(sc_items), len(C)), [chooser, k], "E7_SURFACE_v0", {"k": k})
        rec = {"k": k, "title": b["title"], "time": time_of(b["title"]), "chooser": chooser,
               "screen_before": list(screen), "candidates": [it["uid"] for it in C],
               "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
               "parse_error": r.get("parse_error"), "output_file": r.get("output_file"),
               "attempts": r.get("attempts"), "prompt_sha256": r.get("prompt_sha256")}
        if not r.get("parse_ok"):
            rec.update({"action": None, "keep": list(screen), "show": [], "retired": [], "screen_after": list(screen),
                        "expand": [], "recap": [], "why": "", "failed": True})
            print("[surface k%d] FAILED — screen unchanged" % k, flush=True)
        else:
            p = r["parsed"]
            keep = [screen[i - 1] for i in p["keep"]]
            show = [C[i - 1]["uid"] for i in p["show"]]
            retired = [u for u in screen if u not in keep]
            new_screen = keep + [u for u in show if u not in keep]
            mismatch = ((p["action"] == "保持" and (show or retired)) or
                        (p["action"] == "沉默" and new_screen) or
                        (p["action"] in ("补充", "更新") and not show))
            rec.update({"action": p["action"], "keep": keep, "show": show, "retired": retired,
                        "screen_after": new_screen, "expand": [C[i - 1]["uid"] for i in p["expand"]],
                        "recap": [C[i - 1]["uid"] for i in p["recap"]], "why": p["why"],
                        "action_mismatch": bool(mismatch), "failed": False})
            screen = new_screen
            print("[surface k%d] %s keep=%d show=%d retired=%d screen=%d" % (
                k, p["action"], len(keep), len(show), len(retired), len(screen)), flush=True)
        recs.append(rec)
    wjson("surface.json", {"run_id": RUN_ID, "chooser": chooser, "items": reg, "records": recs})
    return recs


# ---------------- 第 4 段：render + 统计 ----------------

KIND_TAG = re.compile(r"^\[[^\]\n]{1,8}\]\s*")


def reader_text(it):
    return it["text"]  # 读者所见：不带 [kind] 标签；条目内部标记照原文


def reader_view_from_screens(steps):
    """steps: [{time, screen:[text...]}] → 读者视图结构 [{time, new:[...], status}]。"""
    prev, out = [], []
    for s in steps:
        cur = s["screen"]
        new = [t for t in cur if t not in prev]
        gone = [t for t in prev if t not in cur]
        if new:
            status = "new"
        elif not gone:
            status = "unchanged"
        elif cur:
            status = "removed_only"
        else:
            status = "cleared"
        out.append({"time": s["time"], "new": new, "status": status, "n_screen": len(cur),
                    "screen_chars": sum(len(t) for t in cur)})
        prev = cur
    return out


def reader_md(view):
    L = []
    for s in view:
        L += ["### %s" % s["time"], ""]
        if s["status"] == "new":
            L += ["- %s" % t for t in s["new"]]
        elif s["status"] == "unchanged":
            L.append("（屏幕不变）")
        elif s["status"] == "removed_only":
            L.append("（无新内容；部分旧内容撤下）")
        else:
            L.append("（屏幕清空）")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def view_stats(view):
    return {"n_steps": len(view), "n_new_lines": sum(len(s["new"]) for s in view),
            "new_chars": sum(len(t) for s in view for t in s["new"]),
            "status": dict(Counter(s["status"] for s in view)),
            "mean_screen": round(sum(s["n_screen"] for s in view) / len(view), 2) if view else 0}


def convert_run124():
    """run124 生产稿 B → 读者视图：只取每站屏幕行（含【听】小标题行），去掉 [kind] 标签、动作/why/规则/模型名。"""
    text = (ROOT / RUN124_REL).read_text(encoding="utf-8")
    secs = list(re.finditer(r"^## 第\s*(\d+)\s*站\s*(.*)$", text, re.M))
    steps = []
    for i, m in enumerate(secs):
        end = secs[i + 1].start() if i + 1 < len(secs) else len(text)
        body = text[m.end():end]
        nxt = re.search(r"^## ", body, re.M)  # 汇总段（展开可看/曲终回顾）不属于屏幕
        if nxt:
            body = body[:nxt.start()]
        lines = body.split("\n")
        screen, on = [], False
        for l in lines:
            if l.startswith("- 屏幕"):
                on = True
                continue
            if on:
                if l.startswith("  - "):
                    screen.append(KIND_TAG.sub("", l[4:].strip()))
                elif l.strip():
                    on = False
        time_ = re.sub(r"^\d+\.\s*", "", m.group(2).strip())
        steps.append({"time": time_, "screen": screen})
    if not steps or not any(s["screen"] for s in steps):
        raise RuntimeError("run124 conversion found no screen lines")
    return steps


def stage_render(_workers):
    S = rjson("surface.json")
    reg, recs, chooser = S["items"], S["records"], S["chooser"]
    # 内部稿
    L = ["# E7 诊断稿 内部视图（Op.60；chooser=%s；诊断用，不进 production）" % chooser, ""]
    for r in recs:
        L += ["## 第 %d 段 %s" % (r["k"], r["title"]), "",
              "- action：%s%s" % (r["action"] or "（解析失败，屏幕沿用）",
                                  "（与 keep/show 不一致）" if r.get("action_mismatch") else ""),
              "- why：%s" % (r.get("why") or ""),
              "- 屏幕（%d 条）：" % len(r["screen_after"])]
        L += ["  - %s%s" % ("【新】" if u in r["show"] else "", tagged(reg[u])) for u in r["screen_after"]] or ["  - （空）"]
        L.append("- 撤下（%d 条）：" % len(r["retired"]))
        L += ["  - %s（第 %d 段上屏）" % (tagged(reg[u]), reg[u]["k"]) for u in r["retired"]] or ["  - （无）"]
        L.append("- 展开可看 %d 条；曲终回顾 %d 条" % (len(r["expand"]), len(r["recap"])))
        L.append("")
    (OUT_DIR / ("surface__%s__op60.md" % chooser)).write_text("\n".join(L), encoding="utf-8")
    # 读者视图
    steps = [{"time": r["time"], "screen": [reader_text(reg[u]) for u in r["screen_after"]]} for r in recs]
    view_a = reader_view_from_screens(steps)
    (OUT_DIR / ("reading__%s__op60.md" % chooser)).write_text(
        "# 边听边读（屏幕上新出现的内容）\n\n" + reader_md(view_a), encoding="utf-8")
    steps_b = convert_run124()
    view_b = reader_view_from_screens(steps_b)
    (OUT_DIR / "reading__run124B__op60.md").write_text(
        "# 边听边读（屏幕上新出现的内容）\n\n" + reader_md(view_b), encoding="utf-8")
    # 统计
    ok = [r for r in recs if not r.get("failed")]
    acts = Counter(r["action"] for r in ok)
    shown_kind = Counter(reg[u]["kind"] for r in recs for u in r["show"])
    stints, cur = [], {}
    for r in recs:
        for u in r["screen_after"]:
            cur.setdefault(u, r["k"])
        for u in list(cur):
            if u not in r["screen_after"]:
                stints.append((u, cur.pop(u), r["k"] - 1))
    for u, k0 in cur.items():
        stints.append((u, k0, recs[-1]["k"]))
    lens = [k1 - k0 + 1 for _u, k0, k1 in stints]
    longest = max(stints, key=lambda s: s[2] - s[1]) if stints else None
    stats = {
        "n_beads": len(recs), "n_failed": len(recs) - len(ok),
        "actions": {a: acts.get(a, 0) for a in ACTIONS},
        "action_mismatch": sum(1 for r in ok if r.get("action_mismatch")),
        "mean_screen_items": round(sum(len(r["screen_after"]) for r in recs) / len(recs), 2),
        "total_screen_chars_summed_over_beads": sum(len(reader_text(reg[u])) for r in recs for u in r["screen_after"]),
        "total_shown_chars": sum(len(reader_text(reg[u])) for r in recs for u in r["show"]),
        "retired_count": sum(len(r["retired"]) for r in recs),
        "shown_by_kind": {k: shown_kind.get(k, 0) for k in KIND_ORDER},
        "candidates_by_kind": dict(Counter(it["kind"] for it in reg.values())),
        "staleness_hist": dict(sorted(Counter(lens).items())),
        "longest_stint": ({"uid": longest[0], "from_k": longest[1], "to_k": longest[2],
                           "beads": longest[2] - longest[1] + 1, "text": tagged(reg[longest[0]])}
                          if longest else None),
        "reader_view_a": view_stats(view_a), "reader_view_b_run124": view_stats(view_b),
    }
    wjson("render.json", {"run_id": RUN_ID, "chooser": chooser, "stats": stats,
                          "reading_a": "reading__%s__op60.md" % chooser,
                          "reading_b": "reading__run124B__op60.md", "view_a": view_a, "view_b": view_b})
    return stats


# ---------------- 第 5 段：compare（E7_COMPARE_v0 三方盲比） ----------------

def body_of(md):
    return re.sub(r"\A# [^\n]*\n+", "", md).strip()


def sanitize_baseline(text):
    keep, removed = [], []
    for l in text.split("\n"):
        (removed if LEAK_PAT.search(l) else keep).append(l)
    return "\n".join(keep).strip(), removed


def compare_inputs():
    R = rjson("render.json")
    a = body_of((OUT_DIR / R["reading_a"]).read_text(encoding="utf-8"))
    b = body_of((OUT_DIR / R["reading_b"]).read_text(encoding="utf-8"))
    sets = {}
    for cname, rel in BASELINES.items():
        c, removed = sanitize_baseline((ROOT / rel).read_text(encoding="utf-8"))
        sets[cname] = {"texts": {"a": a, "b": b, "c": c}, "c_source": rel, "c_removed_lines": removed}
    for s in sets.values():
        for who, t in s["texts"].items():
            m = LEAK_PAT.search(t)
            if m:
                raise RuntimeError("candidate %s leaks identity mark %r" % (who, m.group(0)))
    return sets


def parse_compare(out):
    ok, obj, err = extract_json_obj(out)
    if not ok:
        return None, err
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    rk = obj.get("ranking")
    if not isinstance(rk, list) or len(rk) != 3:
        return None, "ranking must be a list of 3"
    norm = []
    for x in rk:
        s = str(x).strip()
        p = next((c for c in s if c in POS), None)
        if p is None or p in norm:
            return None, "bad ranking entry %r" % (x,)
        norm.append(p)
    res = {"ranking": norm, "why": str(obj.get("why", "")).strip()}
    for k in ("best_moments", "worst_moments", "hindsight", "only_here"):
        res[k] = obj.get(k)
    return res, None


def compare_tasks():
    sets = compare_inputs()
    tasks = []
    for si, (cname, s) in enumerate(sorted(sets.items())):
        for ji, judge in enumerate(CFG["judges"]):
            seed = SEED_COMPARE + 100 * si + ji
            base = ["a", "b", "c"]
            random.Random(seed).shuffle(base)
            for rr in range(JUDGE_RUNS):
                order = base[rr:] + base[:rr]  # 循环轮换：每个候选在 3 次里各占一次甲/乙/丙
                mapping = dict(zip(POS, order))
                prompt = fill(TPL["E7_COMPARE_v0"], WORK=WORK_NAME, A=s["texts"][order[0]],
                              B=s["texts"][order[1]], C=s["texts"][order[2]])
                tasks.append({"set": cname, "c_source": s["c_source"], "judge": judge, "run": rr,
                              "seed": seed, "mapping": mapping, "prompt": prompt})
    return sets, tasks


def stage_compare(workers):
    sets, tasks = compare_tasks()
    for name, s in sets.items():
        d = OUT_DIR / "compare_inputs"
        d.mkdir(exist_ok=True)
        for who, t in s["texts"].items():
            (d / ("%s__%s.md" % (name, who))).write_text(t + "\n", encoding="utf-8")

    def one(t):
        r = call("compare", "cmp150__%s__%s__r%d" % (t["set"], t["judge"], t["run"]), t["judge"], t["prompt"],
                 parse_compare, [t["set"], t["judge"], t["run"], t["mapping"]], "E7_COMPARE_v0",
                 {"set": t["set"], "run": t["run"], "mapping": t["mapping"]})
        p = r.get("parsed") or {}
        rank_true = [t["mapping"][x] for x in p["ranking"]] if r.get("parse_ok") else None
        return {k: v for k, v in t.items() if k != "prompt"} | {
            "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
            "parse_error": r.get("parse_error"), "output_file": r.get("output_file"),
            "prompt_sha256": r.get("prompt_sha256"), "ranking_pos": p.get("ranking"),
            "ranking_true": rank_true, "why": p.get("why"), "only_here": p.get("only_here"),
            "best_moments": p.get("best_moments"), "worst_moments": p.get("worst_moments"),
            "hindsight": p.get("hindsight")}

    recs = pmap(one, tasks, workers)
    wjson("compare.json", {"run_id": RUN_ID, "judges": list(CFG["judges"]), "agg": aggregate(recs),
                           "records": recs})
    return recs


def _agg(rs):
    ok = [r for r in rs if r["parse_ok"]]
    out = {"n": len(rs), "n_ok": len(ok)}
    for c in "abc":
        ranks = [r["ranking_true"].index(c) + 1 for r in ok]
        out["mean_rank_" + c] = round(sum(ranks) / len(ranks), 2) if ranks else None
        out["first_" + c] = sum(1 for r in ok if r["ranking_true"][0] == c)
    out["first_by_pos"] = dict(Counter(r["ranking_pos"][0] for r in ok))
    return out


def cand_gens(set_name):
    """每个候选背后的模型键（用于标记自评）。"""
    return {"a": sorted({CFG["gen"], CFG["chooser"]}), "b": [RUN124_GEN], "c": [BASELINE_GEN.get(set_name, "?")]}


def self_flag(set_name, judge):
    hits = [c for c, gens in cand_gens(set_name).items() if judge in gens]
    return ",".join(hits) if hits else "否"


def aggregate(recs):
    rows = []
    for s in sorted(set(r["set"] for r in recs)):
        rs_s = [r for r in recs if r["set"] == s]
        for j in CFG["judges"]:
            rs = [r for r in rs_s if r["judge"] == j]
            a = _agg(rs)
            firsts = [r["ranking_true"][0] for r in rs if r["parse_ok"]]
            top = Counter(firsts).most_common(1)
            a["first_consistency"] = ("%d/%d（%s）" % (top[0][1], len(firsts), top[0][0])) if top else "—"
            a["full_order_consistency"] = ("%d/%d" % (Counter(tuple(r["ranking_true"]) for r in rs if r["parse_ok"])
                                                       .most_common(1)[0][1], len(firsts))) if firsts else "—"
            rows.append({"set": s, "judge": j, "judge_is_generator_of": self_flag(s, j), **a})
        rows.append({"set": s, "judge": "ALL", "judge_is_generator_of": "—", **_agg(rs_s)})
    return rows


# ---------------- 第 6 段：report + manifest ----------------

def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def stage_report():
    S = rjson("surface.json")
    reg, recs = S["items"], S["records"]
    R = rjson("render.json")
    st = R["stats"]
    W = rjson("why.json")
    M = rjson("mech.json")
    C = rjson("compare.json") if (OUT_DIR / "compare.json").exists() else {"agg": [], "records": []}
    L = ["# run150 E7 诊断性整篇样稿（Op.60；诊断用，不进 production）", "",
         "- 生成（why/mech）：`%s`；chooser：`%s`；MECH 审核：%s；评审：%s；历史清单来源：`%s`"
         % (W["gen_model"], S["chooser"], "、".join(M["auditors"]), "、".join(C.get("judges") or CFG["judges"]),
            W["history_source"]),
         "- 只报告脚本算出的数字与原文，不做审美裁决。", "",
         "## 1. 上游", "",
         "- why：%d 颗中 differs=true %d、false %d、解析失败 %d" % (
             len(W["records"]), sum(1 for r in W["records"] if r["parse_ok"] and r["differs"]),
             sum(1 for r in W["records"] if r["parse_ok"] and not r["differs"]),
             sum(1 for r in W["records"] if not r["parse_ok"])),
         "- mech：生成关系 %d 条（解析失败 %d 颗），审核后存活 %d 条" % (
             sum(len(r["relations"]) for r in M["records"]), sum(1 for r in M["records"] if not r["parse_ok"]),
             sum(1 for r in M["records"] for x in r["relations"] if x.get("survives"))), "",
         "## 2. 屏幕统计（%s）" % S["chooser"], "",
         "| 指标 | 值 |", "|---|---|"]
    for k, v in st.items():
        if k in ("reader_view_a", "reader_view_b_run124", "longest_stint"):
            continue
        L.append("| %s | %s |" % (k, cell(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)))
    ls = st.get("longest_stint")
    if ls:
        L += ["", "最长停留：%d 颗（第 %d–%d 段）：%s" % (ls["beads"], ls["from_k"], ls["to_k"], ls["text"])]
    L += ["", "读者视图对照：本稿 %s；run124 B %s" % (json.dumps(st["reader_view_a"], ensure_ascii=False),
                                                 json.dumps(st["reader_view_b_run124"], ensure_ascii=False)), ""]
    L += ["## 3. 三方盲比（a=本稿读者视图，b=run124 生产稿 B，c=V2A+Gemini 基线）", "",
          "候选生成模型：a=%s；b=%s；c=gpro 组 %s / gflash 组 %s。“评审=生成者”列标出该评审是哪个候选的生成模型（自评可查）。"
          % ("、".join(cand_gens("")["a"]), RUN124_GEN, BASELINE_GEN["c_gpro_s3"], BASELINE_GEN["c_gflash_s1"]), "",
          "| 组 | 评审 | 评审=生成者 | ok/n | 平均名次 a | b | c | 第一 a/b/c | 第一名一致 | 全序一致 | 第一按位置 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in C["agg"]:
        L.append("| %s | %s | %s | %d/%d | %s | %s | %s | %d/%d/%d | %s | %s | %s |" % (
            r["set"], r["judge"], r.get("judge_is_generator_of", ""), r["n_ok"], r["n"], r["mean_rank_a"], r["mean_rank_b"], r["mean_rank_c"],
            r["first_a"], r["first_b"], r["first_c"], r.get("first_consistency", ""),
            r.get("full_order_consistency", ""), json.dumps(r["first_by_pos"], ensure_ascii=False)))
    L += ["", "评审原文：", ""]
    for r in C["records"]:
        L.append("- %s / %s / 第%d次 映射=%s → %s：`%s`" % (
            r["set"], r["judge"], r["run"] + 1, json.dumps(r["mapping"], ensure_ascii=False),
            r["ranking_true"] if r["parse_ok"] else "解析失败(%s)" % r["parse_error"],
            "runs/%s/%s" % (RUN_ID, r["output_file"]) if r.get("output_file") else "—"))
    L += ["", "## 4. 撤下示例（5 条）", ""]
    ret = [(r["k"], u) for r in recs for u in r["retired"]]
    pick = [ret[int(i * (len(ret) - 1) / 4)] for i in range(5)] if len(ret) >= 5 else ret
    for k, u in pick:
        L.append("- 第 %d 段撤下（第 %d 段上屏）：%s" % (k, reg[u]["k"], tagged(reg[u])))
    if not pick:
        L.append("（无撤下）")
    L += ["", "## 5. 上屏的 [因为前面] / [更深]", ""]
    n = 0
    for r in recs:
        for u in r["show"]:
            if reg[u]["kind"] in ("因为前面", "更深"):
                n += 1
                L.append("- 第 %d 段 %s" % (r["k"], tagged(reg[u])))
    if not n:
        L.append("（无）")
    L += ["", "## 6. 文件", "",
          "- 内部稿 `surface__%s__op60.md`；读者视图 `%s`；run124 读者视图 `%s`；三方输入 `compare_inputs/`"
          % (S["chooser"], R["reading_a"], R["reading_b"]),
          "- 全部提示词/原始输出在 `prompts/`、`outputs/`、`meta/`；缓存 `cache_*.json`；哈希见 `run_manifest.json`", ""]
    (OUT_DIR / "report.md").write_text("\n".join(L), encoding="utf-8")
    return str(OUT_DIR / "report.md")


def write_manifest(extra):
    outs = {}
    for p in sorted(OUT_DIR.rglob("*")):
        rel = p.relative_to(OUT_DIR)
        if not p.is_file() or p.suffix == ".tmp" or any(x.startswith("_") for x in rel.parts):
            continue
        if p.name in ("run_manifest.json", "run.log", "DONE", "FAILED"):
            continue
        outs[str(rel).replace("\\", "/")] = sha256_file(p)
    hist_name = CFG["history"].partition(":")[0]
    hist_rel = {"run130": "runs/run130_thread_e6/steps.json",
                "run133": "runs/run133_thread_spec/chains.json"}.get(hist_name)
    inputs = {BEADS_REL: BEADS_REL, RUN124_REL: RUN124_REL}
    inputs.update({v: v for v in BASELINES.values()})
    if hist_rel:
        inputs[hist_rel] = hist_rel
    man = {"run_id": RUN_ID, "git_head": git_commit(),
           "script": {"runs/%s/go.py" % RUN_ID: sha256_file(THIS_DIR / "go.py")},
           "templates": {v: sha256_file(ROOT / v) for v in TPL_PATHS.values()},
           "inputs": {k: sha256_file(ROOT / k) for k in inputs if (ROOT / k).exists()},
           "models": {"gen": CFG["gen"], "chooser": CFG["chooser"], "auditors": list(CFG["auditors"]),
                      "judges": list(CFG["judges"]),
                      "model_names": {k: runner.MODEL_NAMES.get(k, k) for k in
                                      {CFG["gen"], CFG["chooser"], *CFG["auditors"], *CFG["judges"]}}},
           "history_source": CFG["history"],
           "env": {"MUSIC_WEB_ROUTE": os.environ.get("MUSIC_WEB_ROUTE"), "GPT2_KEYS": list(runner.GPT2_KEYS),
                   "MG_KEYS": list(runner.MG_KEYS)},
           "candidate_generators": {s: cand_gens(s) for s in BASELINES},
           "compare": {"seed_base": SEED_COMPARE, "runs_per_judge": JUDGE_RUNS, "positions": list(POS)},
           "extra": extra or {}, "outputs": outs}
    wjson("run_manifest.json", man)
    return man


def snapshot_calls():
    with LOCK:
        return {"n": CALLS["n"], "by": {k: dict(v) for k, v in CALLS["by"].items()}}


STAGES = ("why", "mech", "surface", "render", "compare", "report")


def run_stages(stages, workers):
    if "why" in stages and "mech" in stages:
        with cf.ThreadPoolExecutor(max_workers=2) as ex:
            fw, fm = ex.submit(stage_why, workers), ex.submit(stage_mech, workers)
            fw.result()
            fm.result()
    elif "why" in stages:
        stage_why(workers)
    elif "mech" in stages:
        stage_mech(workers)
    if "surface" in stages:
        stage_surface(workers)
    if "render" in stages:
        stage_render(workers)
    if "compare" in stages:
        stage_compare(workers)
    if "report" in stages:
        stage_report()


# ---------------- mock：假 run_job ----------------

def fake_run_job(run_dir, job, timeout=3600):
    run_dir = Path(run_dir)
    for d in ("prompts", "outputs", "meta"):
        (run_dir / d).mkdir(parents=True, exist_ok=True)
    br, ex, p = job["branch"], job.get("extra") or {}, job["prompt"]
    k, att = ex.get("k", 0), ex.get("attempt", 0)
    MOCK["calls"] += 1
    if br == "why":
        out = json.dumps({"differs": k % 3 != 0, "sentence": ("MOCK因为前面k%d" % k) if k % 3 else "无"},
                         ensure_ascii=False)
    elif br == "mech":
        out = json.dumps([{"relation": "MOCK更深A k%d" % k, "explains": [1, 2], "new_understanding": "MOCK"},
                          {"relation": "MOCK更深B k%d" % k, "explains": [1, 3], "new_understanding": "MOCK"}]
                         if k % 2 else [], ensure_ascii=False)
    elif br == "audit":
        bad = ex.get("gidx") == 1 and ex.get("auditor") == CFG["auditors"][-1]
        out = json.dumps({"class": "manufactured" if bad else "insight", "why": "MOCK"}, ensure_ascii=False)
    elif br == "surface":
        if k == 3 and att == 0:
            out = "not json at all"  # 测试解析失败重试
        else:
            head, _, tail = p.partition("【这一段可以给读者的内容】")
            n_s = len(re.findall(r"^S\d+\. ", head, re.M))
            lines = re.findall(r"^(\d+)\. \[([^\]]+)\]", tail, re.M)
            if k % 5 == 0 and n_s:
                obj = {"action": "保持", "keep": ["S%d" % i for i in range(1, n_s + 1)], "show": []}
            else:
                show = [int(lines[1][0])] + [int(i) for i, kind in lines if kind in ("因为前面", "更深")][:1]
                obj = {"action": "补充" if n_s else "更新",
                       "keep": ["S%d" % i for i in range(1, n_s + 1) if i % 2 == 0 and i <= 4], "show": show}
            obj.update({"expand": [1], "recap": [], "why": "MOCK"})
            out = json.dumps(obj, ensure_ascii=False)
    elif br == "compare":
        for bad in ("gpt56w", "run124", "Gemini", "gpro", "[此刻]", "[更深]"):
            assert bad not in p.split("【甲】", 1)[1], "compare prompt leaks %r" % bad
        out = json.dumps({"ranking": ["乙", "甲", "丙"], "why": "MOCK", "best_moments": {}, "worst_moments": {},
                          "hindsight": {}, "only_here": {}}, ensure_ascii=False)
    else:
        out = "好"
    jid = job["job_id"]
    (run_dir / "prompts" / (jid + ".txt")).write_text(p, encoding="utf-8")
    (run_dir / "outputs" / (jid + ".md")).write_text(out, encoding="utf-8")
    meta = {"job_id": jid, "status": "ok", "error": None, "seconds": 0.0, "model_key": job["model_key"],
            "output_file": "outputs/%s.md" % jid, "extra": ex}
    (run_dir / "meta" / (jid + ".json")).write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return meta


def run_mock(workers):
    global OUT_DIR, RUN_JOB
    tmp = Path(tempfile.mkdtemp(prefix="run150_mock_"))
    OUT_DIR, RUN_JOB = tmp, fake_run_job
    STORES.clear()
    MOCK.update(on=True, calls=0)
    try:
        run_stages(STAGES, workers)
        first = MOCK["calls"]
        W, M, S = rjson("why.json"), rjson("mech.json"), rjson("surface.json")
        assert len(W["records"]) == K_EXPECTED - 1 and all(r["parse_ok"] for r in W["records"])
        assert len(M["records"]) == K_EXPECTED and all(r["parse_ok"] for r in M["records"])
        surv = [x for r in M["records"] for x in r["relations"] if x["survives"]]
        dead = [x for r in M["records"] for x in r["relations"] if not x["survives"]]
        assert surv and dead, "mock audit should both keep and drop"
        assert len(S["records"]) == K_EXPECTED and all(not r["failed"] for r in S["records"])
        assert len(S["records"][2]["attempts"]) == 2, "k3 retry not exercised"
        kinds = Counter(S["items"][u]["kind"] for r in S["records"] for u in r["show"])
        assert kinds["此刻"] and kinds["因为前面"] and kinds["更深"], kinds
        R = rjson("render.json")
        assert R["stats"]["retired_count"] > 0 and R["stats"]["actions"]["保持"] > 0
        for f in ("surface__%s__op60.md" % CFG["chooser"], "reading__%s__op60.md" % CFG["chooser"],
                  "reading__run124B__op60.md"):
            assert (OUT_DIR / f).exists(), f
        rd = (OUT_DIR / ("reading__%s__op60.md" % CFG["chooser"])).read_text(encoding="utf-8")
        assert "（屏幕不变）" in rd and "[此刻]" not in rd and "MOCK因为前面" in rd
        Cj = rjson("compare.json")
        assert len(Cj["records"]) == len(BASELINES) * len(CFG["judges"]) * JUDGE_RUNS
        assert all(r["parse_ok"] for r in Cj["records"])
        for s in BASELINES:  # 每个候选在每位评审的 3 次里各占一次甲/乙/丙
            for j in CFG["judges"]:
                rs = [r for r in Cj["records"] if r["set"] == s and r["judge"] == j]
                for c in "abc":
                    assert sorted(next(p for p, v in r["mapping"].items() if v == c) for r in rs) == sorted(POS)
        assert (OUT_DIR / "report.md").exists()
        fl = {(r["set"], r["judge"]): r["judge_is_generator_of"] for r in Cj["agg"]}
        if "gpt56w" in CFG["judges"] and CFG["gen"] == "gpt56w":
            assert fl[("c_gpro_s3", "gpt56w")] == "a,b", fl
        if "gpro_web" in CFG["judges"]:
            assert fl[("c_gpro_s3", "gpro_web")] == "c" and fl[("c_gflash_s1", "gpro_web")] == "否", fl
        write_manifest({"mock": True})
        # 断点续跑：再跑一遍必须零新调用
        STORES.clear()
        run_stages(STAGES, workers)
        assert MOCK["calls"] == first, "resume made %d new calls" % (MOCK["calls"] - first)
        print("MOCK OK: calls=%d (rerun +0); why=%d mech_rel=%d(survive %d) surface=%d stats=%s; compare=%d"
              % (first, len(W["records"]), len(surv) + len(dead), len(surv), len(S["records"]),
                 json.dumps({k: R["stats"][k] for k in ("actions", "retired_count", "mean_screen_items",
                                                         "shown_by_kind", "staleness_hist")}, ensure_ascii=False),
                 len(Cj["records"])), flush=True)
        print("--- run124 reader view head ---\n" +
              (OUT_DIR / "reading__run124B__op60.md").read_text(encoding="utf-8")[:600], flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        STORES.clear()
        MOCK["on"] = False
        OUT_DIR, RUN_JOB = RUN_DIR, runner.run_job
    leftovers = [n for n in ("outputs", "DONE", "FAILED", "why.json", "cache_why.json") if (RUN_DIR / n).exists()]
    assert not leftovers, "mock left files in real run dir: %s" % leftovers
    return True


def run_smoke(keys, timeout):
    """极短真实冒烟；产物留在 _smoke/。"""
    global OUT_DIR
    OUT_DIR = RUN_DIR / "_smoke"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%m%d%H%M%S")

    def one(key):
        job = {"job_id": "smoke__%s__%s" % (key, stamp), "branch": "smoke", "model_key": key, "prompt": "只回复：好",
               "prompt_version": "smoke", "prompt_template": "(smoke)", "work_key": WORK_KEY,
               "work_name": WORK_NAME, "sample": 1, "extra": {"smoke": True}, "forbid_tools": list(FORBID),
               "max_attempts": 1}
        t0 = time.time()
        try:
            meta = runner.run_job(str(OUT_DIR), job, timeout=timeout)
            out = _read_output(meta)
            return key, {"status": meta.get("status"), "error": meta.get("error"), "reply": out[:80],
                         "seconds": round(time.time() - t0, 1)}
        except Exception as e:
            return key, {"status": "exception", "error": "%s: %s" % (type(e).__name__, e)}

    res = dict(pmap(one, list(keys), len(keys)))
    (OUT_DIR / ("smoke_%s.json" % stamp)).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_DIR = RUN_DIR
    print(json.dumps(res, ensure_ascii=False, indent=1), flush=True)
    return res


def main():
    global OUT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES, default=None)
    ap.add_argument("--gen-model", default=CFG["gen"])
    ap.add_argument("--chooser", default=CFG["chooser"])
    ap.add_argument("--auditors", default=",".join(CFG["auditors"]))
    ap.add_argument("--judges", default=",".join(CFG["judges"]))
    ap.add_argument("--history-source", default=CFG["history"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--smoke", "--probe", action="store_true")
    ap.add_argument("--smoke-keys", default="opus,luna_noweb,gpro_web,gflash_web")
    ap.add_argument("--smoke-timeout", type=int, default=600)
    a = ap.parse_args()
    CFG.update(gen=a.gen_model, chooser=a.chooser, history=a.history_source,
               auditors=tuple(x for x in a.auditors.split(",") if x),
               judges=tuple(x for x in a.judges.split(",") if x))
    # 用户 10-09：生成者可以评自己的产出；报告里按评审单列，并标出"评审 == 某候选的生成模型"。
    if a.mock:
        return 0 if run_mock(a.workers) else 1
    if a.smoke:
        run_smoke([k for k in a.smoke_keys.split(",") if k], a.smoke_timeout)
        return 0
    OUT_DIR = RUN_DIR
    for n in ("DONE", "FAILED"):
        try:
            (RUN_DIR / n).unlink()
        except OSError:
            pass
    stages = [a.stage] if a.stage else list(STAGES)
    t0 = time.time()
    try:
        run_stages(stages, a.workers)
        write_manifest({"calls": snapshot_calls(), "stages": stages})
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        (RUN_DIR / "FAILED").write_text("stages=%s at %s\n%s" % (stages, time.strftime("%m-%d %H:%M:%S"), tb),
                                        encoding="utf-8")
        try:
            write_manifest({"calls": snapshot_calls(), "stages": stages, "failed": True})
        except Exception:
            pass
        return 1
    failed = sum(v.get("failed", 0) for v in CALLS["by"].values())
    if "report" in stages:
        (RUN_DIR / "DONE").write_text("stages=%s at %s calls=%d failed_logical=%d" % (
            stages, time.strftime("%m-%d %H:%M:%S"), CALLS["n"], failed), encoding="utf-8")
    print("run150 stages=%s done in %.1fs calls=%d failed_logical=%d" % (stages, time.time() - t0, CALLS["n"], failed),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
