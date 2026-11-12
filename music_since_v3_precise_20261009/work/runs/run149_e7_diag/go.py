"""run149_e7_diag：E7 诊断性整篇样稿（Op.60；诊断用，不进 production）。无收据门控、无 COMPLETION_PENDING。

为什么有这个 run：run137/139/142/144/146/148 六版驱动全部卡在 Muse 收据类型绑定 + gpt2 全局 hold 门控，零产出。
本驱动丢掉这些门控，直接把文章和评审结果跑出来。逻辑（切分/历史/解析/统计/盲比/轮换）照抄 run134，只读不改旧文件。

阶段（--stage why|mech|surface|render|compare|report|all；可断点续跑）：
  why     WHY_GATE_v4，k=2..23，HISTORY=历史链到 k-1 的清单；differs=true → [因为前面]
  mech    MECH_v1 生成（gen 模型）+ MECH_AUDIT_v0 双审（luna_noweb、gflash_web）；任一判 manufactured/imported 即丢；存活 → [更深]
  surface E7_SURFACE_v0 逐颗串行；两条独立 chooser 链（gpt56w、opus）并行
  render  每个 chooser：surface__<chooser>__op60.md（内部稿）+ reading__<chooser>__op60.md（读者所见）+ 统计
  compare E7_COMPARE_v0 三方盲比 a=reading__gpt56w / b=run124 生产稿 B 读者视图 / c=run132 重建 V2A+Gemini 基线；
          两个变体（c=gpro_web s3、c=gflash_web s1）；评审 gpt56w/gpt6w/opus/luna_noweb/gflash_web 各 3 次甲乙丙循环轮换；
          另导出 muse_judge_pack.json（Muse 由主会话自己的工具跑，不阻塞完成）
  report  report.md + run_manifest.json + DONE / FAILED

缓存：每次逻辑调用按 (step, 逻辑键, 模型键, 完整提示词 sha256) 记在 cache_<step>.json，只复用解析成功的；
失败调用（含解析失败）最多再试 2 次，每次新 attempt job_id；provider hold（queue_stop）时不再试。
上游（why/mech 生成、gpt56w chooser 链）有失败 → 写 FAILED 并停在该阶段（重跑即续）；评审某一路失败 → 报告列为缺席，不阻塞 DONE。

用法（cwd 为仓库根）：
  set MUSIC_WEB_ROUTE=gpt2 && python -X utf8 -I runs\\run149_e7_diag\\go.py [--stage all] [--gen-model gpt56w]
  python -X utf8 -I runs\\run149_e7_diag\\go.py --mock           # 假 run_job 全流程（临时目录；不碰真实目录）
  python -X utf8 -I runs\\run149_e7_diag\\go.py --smoke --smoke-keys gflash_web,luna_noweb,opus
"""
from __future__ import annotations

import os

os.environ.setdefault("MUSIC_WEB_ROUTE", "gpt2")  # 必须在 import runner 之前（runner 导入时读路由）

import argparse  # noqa: E402
import concurrent.futures as cf  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run149_e7_diag"
RUN_DIR = ROOT / "runs" / RUN_ID
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
import runner  # noqa: E402  (只用 run_job / 常量；不改 tools/)
from stage import WORKS  # noqa: E402
from execution_integrity import canonical_model  # noqa: E402

# ---------------- Opus 许可（只在本进程内放开 opus 一个键；sol/muse 仍走原 check_policy） ----------------
# execution_integrity.check_policy 写的是 10-03 旧约束“禁止新增 Opus”；用户 10-06 已撤销（“你现在可以随便用opus”），
# 10-09 用户评审全阵容含 opus。本 run 只对 "opus" 键豁免，manifest/report 记录此豁免。tools/ 文件不改。
_ORIG_POLICY = runner.check_policy
OPUS_OVERRIDE = {"on": os.environ.get("RUN149_NO_OPUS_OVERRIDE") != "1"}


def _policy149(model_key):
    if model_key == "opus" and OPUS_OVERRIDE["on"]:
        return None
    return _ORIG_POLICY(model_key)


def install_opus_override():
    """只在 main()（真实运行/冒烟）里装；import 时不改 runner，免得影响同进程其他测试。"""
    runner.check_policy = _policy149

WORK_KEY = "op60"
WORK_NAME = WORKS[WORK_KEY]
K_EXPECTED = 23
BEADS_REL = "runs/run130_thread_e6/beads_clean.md"
RUN124_REL = "runs/run124_render/surface__B__gpt56w__op60.md"
RUN124_GEN = "gpt56w"
VARIANTS = {  # 两个 c 变体，各成一组三方盲比
    "c_gpro_s3": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gpro_web__s3.md",
    "c_gflash_s1": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gflash_web__s1.md",
}
VARIANT_GEN = {"c_gpro_s3": "gpro_web", "c_gflash_s1": "gflash_web"}
TPL_PATHS = {
    "WHY_GATE_v4": "prompts/versions/WHY_GATE_v4.txt",
    "MECH_v1": "prompts/tooling/MECH_v1.txt",
    "MECH_AUDIT_v0": "prompts/tooling/MECH_AUDIT_v0.txt",
    "E7_SURFACE_v0": "prompts/versions/E7_SURFACE_v0.txt",
    "E7_COMPARE_v0": "prompts/tooling/E7_COMPARE_v0.txt",
}
TPL = {k: (ROOT / v).read_text(encoding="utf-8") for k, v in TPL_PATHS.items()}
HIST_FILES = {"run130": "runs/run130_thread_e6/steps.json", "run133": "runs/run133_thread_spec/chains.json"}

CFG = {
    "gen": "gpt56w",
    "choosers": ("gpt56w", "opus"),  # 第一个是盲比候选 a 的 chooser
    "auditors": ("luna_noweb", "gflash_web"),
    "judges": ("gpt56w", "gpt6w", "opus", "luna_noweb", "gflash_web"),
    "history": "run130:gpt56w",
}
SEED_COMPARE = 149060
SEED_MUSE = 50
JUDGE_RUNS = 3
POS = ("甲", "乙", "丙")
NEW_ATTEMPTS = 3  # 每次运行每个逻辑调用最多新提交 3 次（= 重试 ≤2）
MAX_ATTEMPT_IDS = 12  # attempt 编号上限（跨多次续跑累计）
WEB_GPT = ("gpt56w", "gpt6w")
TMO_GPT, TMO_OTHER = 1800, 3600
GPT_SEM = threading.Semaphore(1)  # 进程内网页 GPT 单并发（gpt2 适配器另有跨进程槽）
FROZEN = ("temporarily frozen", "Temporary Chat activation control was not found", "incomplete_response")
AUDIT_CLASSES = ("insight", "restatement", "manufactured", "imported")
AUDIT_DROP = ("manufactured", "imported")
ACTIONS = ("更新", "补充", "保持", "沉默")
KIND_ORDER = ("认", "此刻", "因为前面", "更深")
LEAK_PAT = re.compile(r"(?i)(gemini|gpt|claude|opus|luna|gpro|gflash|muse|sonnet|run\d{2,3}|v2a|E7_|ATTN_)")

OUT_DIR = RUN_DIR  # mock 时切换到临时目录
LOCK = threading.Lock()
CALLS = {"n": 0, "by": {}}
RUN_JOB = runner.run_job  # mock 时替换


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


def pmap(fn, args, workers):
    out = [None] * len(args)
    if not args:
        return out
    with cf.ThreadPoolExecutor(max_workers=max(1, min(workers, len(args)))) as ex:
        futs = {ex.submit(fn, a): i for i, a in enumerate(args)}
        for f in cf.as_completed(futs):
            out[futs[f]] = f.result()
    return out


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


# ---------------- 珠子切分（与 run130/run134 一致）+ 条目 ----------------

BEAD_HEAD = re.compile(r"^###\s+(.*)$", re.M)


def split_beads(text):
    ms = list(BEAD_HEAD.finditer(text))
    beads = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        chunk = text[m.start():end]
        title = m.group(1).strip()
        a = chunk.find("【此刻】")
        b = chunk.find("【前后关系候选】", a + 1 if a >= 0 else 0)
        now = "" if a < 0 else chunk[a + len("【此刻】"): b if b >= 0 else len(chunk)]
        lines = [l.strip() for l in now.split("\n") if l.strip()]
        body = title + "\n【此刻】\n" + "\n".join(lines)
        beads.append({"k": i + 1, "title": title, "text": body, "now_lines": lines,
                      "has_now": a >= 0, "has_rel": b >= 0})
    return beads


def now_items(bead):
    """【此刻】块每个 '- ' 条目一条（保留【先后】【另一种理解】等内部标记）；非 '- ' 行并入上一条。"""
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


# ---------------- 历史清单（--history-source loader:chain） ----------------

def _hist_run130(arg):
    d = json.loads((ROOT / HIST_FILES["run130"]).read_text(encoding="utf-8"))
    recs = [r for r in d["steps"] if r.get("model") == arg and r.get("work") == WORK_KEY]
    return HIST_FILES["run130"], {r["k"]: r.get("inventory_after") or [] for r in recs}


def _hist_run133(arg):
    d = json.loads((ROOT / HIST_FILES["run133"]).read_text(encoding="utf-8"))
    return HIST_FILES["run133"], {r["k"]: r.get("inventory_after") or [] for r in d["chains"][arg]}


HISTORY_LOADERS = {"run130": _hist_run130, "run133": _hist_run133}


def load_history(source):
    name, _, arg = source.partition(":")
    if name not in HISTORY_LOADERS:
        raise ValueError("unknown history source %r (known: %s)" % (source, ", ".join(HISTORY_LOADERS)))
    rel, inv = HISTORY_LOADERS[name](arg)
    missing = [k for k in range(1, K_EXPECTED) if k not in inv]
    if missing:
        raise RuntimeError("history %s missing steps %s" % (source, missing))
    return rel, inv


def history_text(inventory):
    if not inventory:
        return "（还没有）"
    return "\n".join("- %s（来自：%s）" % (it["change"], it["from"]) for it in inventory)


# ---------------- 调用与缓存 ----------------

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.recs, self.by_key = [], {}
        if self.path.exists():
            for r in json.loads(self.path.read_text(encoding="utf-8")).get("records", []):
                self.recs.append(r)
                if r.get("parse_ok"):
                    self.by_key[self._k(r["key"], r["model"], r["prompt_sha256"])] = r

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


def bump(step, model, field, n=1, secs=0.0):
    with LOCK:
        d = CALLS["by"].setdefault("%s|%s" % (step, model),
                                   {"calls": 0, "retries": 0, "cached": 0, "failed": 0, "seconds": 0.0})
        d[field] = d.get(field, 0) + n
        if field == "calls":
            CALLS["n"] += n
            d["seconds"] = round(d["seconds"] + secs, 1)


def _read_rel(rel):
    try:
        if rel and (OUT_DIR / str(rel)).is_file():
            return (OUT_DIR / str(rel)).read_bytes().decode("utf-8", "replace")
    except Exception:
        pass
    return ""


def _judge_output(out, parse_fn):
    if any(p in out for p in FROZEN):
        return None, "frozen/activation/incomplete marker in output"
    try:
        return parse_fn(out)
    except Exception as e:
        return None, "parser %s: %s" % (type(e).__name__, e)


def call(step, core, model, prompt, parse_fn, key, prompt_version, extra=None):
    """一次逻辑调用。同 (step,key,model,prompt sha) 解析成功即复用；否则逐个 attempt 编号提交，最多新提交 3 次。"""
    h = sha256s(prompt)
    key = [RUN_ID, step] + list(key)
    st = store(step)
    hit = st.get(key, model, h)
    if hit is not None:
        bump(step, model, "cached")
        return dict(hit, cached=True)
    rec = {"key": key, "core": core, "model": model, "prompt_sha256": h, "prompt_version": prompt_version,
           "prompt_template": TPL_PATHS.get(prompt_version, prompt_version), "attempts": [], "cached": False,
           "parsed": None, "output": None, "output_file": None, "parse_ok": False, "parse_error": None,
           "queue_stop": False}
    timeout = TMO_GPT if model in WEB_GPT else TMO_OTHER
    new, secs = 0, 0.0
    for att in range(MAX_ATTEMPT_IDS):
        jid = "%s__h%s__a%d" % (core, h[:12], att)
        mp = OUT_DIR / "meta" / (jid + ".json")
        prior = mp.exists() or (OUT_DIR / "prompts" / (jid + ".txt")).exists() \
            or (OUT_DIR / "outputs" / (jid + ".md")).exists()
        if prior:  # 早先运行留下的 attempt：成功就直接解析复用，失败/残缺就跳过该编号
            try:
                meta = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
            except Exception:
                meta = {}
            out = _read_rel(meta.get("output_file")) if meta.get("status") == "ok" else ""
            if out.strip():
                parsed, err = _judge_output(out, parse_fn)
            else:
                parsed, err = None, "prior attempt: %s" % (meta.get("error") or "incomplete (no meta)")
            rec["attempts"].append({"job_id": jid, "status": meta.get("status") or "incomplete", "prior": True,
                                    "parse_ok": parsed is not None, "parse_error": err,
                                    "output_file": meta.get("output_file")})
            if parsed is not None:
                rec.update(parsed=parsed, output=out, parse_ok=True, output_file=meta.get("output_file"),
                           parse_error=None)
                break
            continue
        if new >= NEW_ATTEMPTS:
            break
        new += 1
        job = {"job_id": jid, "branch": step, "model_key": model, "prompt": prompt,
               "prompt_version": prompt_version, "prompt_template": rec["prompt_template"],
               "work_key": WORK_KEY, "work_name": WORK_NAME, "sample": 1,
               "extra": dict(extra or {}, attempt=att, run=RUN_ID),
               "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
               "max_attempts": 1}
        try:
            if model in WEB_GPT:
                with GPT_SEM:
                    meta = RUN_JOB(str(OUT_DIR), job, timeout=timeout)
            else:
                meta = RUN_JOB(str(OUT_DIR), job, timeout=timeout)
        except Exception as e:
            meta = {"job_id": jid, "status": "failed", "error": "%s: %s" % (type(e).__name__, e)}
        meta = meta or {}
        try:
            secs += float(meta.get("seconds") or 0.0)
        except Exception:
            pass
        out = _read_rel(meta.get("output_file")) if meta.get("status") == "ok" else ""
        if meta.get("status") == "ok":
            parsed, err = _judge_output(out, parse_fn)
        else:
            parsed, err = None, "run failed: %s" % (meta.get("error"),)
        entry = {"job_id": jid, "status": meta.get("status"), "meta_error": meta.get("error"),
                 "queue_stop": bool(meta.get("queue_stop")), "output_chars": len(out),
                 "output_file": meta.get("output_file"), "parse_ok": parsed is not None, "parse_error": err,
                 "seconds": meta.get("seconds")}
        rec["attempts"].append(entry)
        log("%s %s %s a%d ok=%s %s" % (step, model, core, att, parsed is not None, (err or "")[:200]))
        if parsed is not None:
            rec.update(parsed=parsed, output=out, parse_ok=True, output_file=meta.get("output_file"),
                       parse_error=None)
            break
        if meta.get("queue_stop"):
            rec["queue_stop"] = True  # provider hold：不再试，等人处理后续跑
            break
    bump(step, model, "calls", new, secs)
    bump(step, model, "retries", max(0, new - 1))
    if not rec["parse_ok"]:
        rec["parse_error"] = rec["attempts"][-1]["parse_error"] if rec["attempts"] else "no attempts left"
        bump(step, model, "failed")
    st.put(dict(rec))
    return rec


# ---------------- 1. why ----------------

def build_why_prompt(k, beads, hist_inv):
    beads_text = "\n\n".join("第 %d 段：%s" % (b["k"], b["text"]) for b in beads[:k])
    return fill(TPL["WHY_GATE_v4"], WORK=WORK_NAME, K=k, K_PREV=k - 1, BEADS=beads_text,
                HISTORY=history_text(hist_inv))


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
        r = call("why", "why__%s__k%02d" % (gen, k), gen, prompt, parse_why,
                 [CFG["history"], k], "WHY_GATE_v4", {"k": k, "history": CFG["history"]})
        p = r.get("parsed") or {}
        return {"k": k, "title": beads[k - 1]["title"], "model": gen, "parse_ok": bool(r.get("parse_ok")),
                "cached": bool(r.get("cached")), "parse_error": r.get("parse_error"),
                "queue_stop": bool(r.get("queue_stop")), "differs": p.get("differs"), "sentence": p.get("sentence"),
                "history_n": len(inv[k - 1]), "prompt_sha256": r.get("prompt_sha256"),
                "prompt_chars": len(prompt), "output_file": r.get("output_file"), "attempts": r.get("attempts")}

    recs = pmap(one, list(range(2, K_EXPECTED + 1)), workers)
    wjson("why.json", {"run_id": RUN_ID, "gen_model": gen, "history_source": CFG["history"],
                       "history_file": hist_rel, "records": recs})
    return recs


# ---------------- 2. mech（生成 + 双审，逐珠流水） ----------------

def build_mech_prompt(title, items):
    return fill(TPL["MECH_v1"], WORK=WORK_NAME, MM=title,
                ITEMS="\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(items)))


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
    return fill(TPL["MECH_AUDIT_v0"], WORK=WORK_NAME, MM=title,
                ITEMS="\n".join("[%d] %s" % (i + 1, t) for i, t in enumerate(items)),
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


def judge_relation(verdicts, auditors):
    """verdicts: {auditor: class|'audit_failed'}。返回 (survives, drop_reason)。
    规则（照任务书字面）：任一家判 manufactured/imported 即丢，其余保留。某家审核调用失败不算“判丢”：
    只要至少一家给出有效判定且没人判丢就保留，但标 audit_incomplete（报告单列）；两家都失败则丢。"""
    dropped = [a for a in auditors if verdicts.get(a) in AUDIT_DROP]
    failed = [a for a in auditors if verdicts.get(a) in (None, "audit_failed")]
    if dropped:
        return False, "dropped by %s" % ",".join(dropped)
    if len(failed) == len(auditors):
        return False, "all audits failed"
    return True, ("audit_incomplete: %s failed" % ",".join(failed)) if failed else None


def stage_mech(workers):
    beads = load_beads()
    gen = CFG["gen"]
    auditors = tuple(CFG["auditors"])
    audits_all = []

    def audit_one(t):
        k, gi, au, rel = t
        b = beads[k - 1]
        prompt = build_audit_prompt(b["title"], now_items(b), rel)
        r = call("audit", "audit__%s__k%02d__r%d" % (au, k, gi), au, prompt, parse_audit,
                 [k, gi, gen, rel["relation"]], "MECH_AUDIT_v0", {"k": k, "gidx": gi, "auditor": au})
        return {"k": k, "gidx": gi, "auditor": au, "parse_ok": bool(r.get("parse_ok")),
                "class": (r.get("parsed") or {}).get("class"), "why": (r.get("parsed") or {}).get("why"),
                "parse_error": r.get("parse_error"), "queue_stop": bool(r.get("queue_stop")),
                "output_file": r.get("output_file")}

    def gen_one(b):
        items = now_items(b)
        if len(items) < 2:
            return {"k": b["k"], "title": b["title"], "model": gen, "n_items": len(items),
                    "skipped": "fewer than 2 items", "relations": [], "parse_ok": True}
        prompt = build_mech_prompt(b["title"], items)
        r = call("mech", "mech__%s__k%02d" % (gen, b["k"]), gen, prompt, parse_mech_fn(len(items)),
                 [b["k"]], "MECH_v1", {"k": b["k"]})
        rels = [dict(x) for x in (r.get("parsed") or [])]
        tasks = [(b["k"], gi, au, rel) for gi, rel in enumerate(rels) for au in auditors]
        av = pmap(audit_one, tasks, len(tasks) or 1)  # 本珠两家审核并行，与其他珠的 gen 流水重叠
        with LOCK:
            audits_all.extend(av)
        for gi, rel in enumerate(rels):
            mine = [a for a in av if a["gidx"] == gi]
            verdicts = {a["auditor"]: (a["class"] if a["parse_ok"] else "audit_failed") for a in mine}
            surv, reason = judge_relation(verdicts, auditors)
            rel.update(verdicts=verdicts, audit_why={a["auditor"]: a["why"] for a in mine},
                       survives=surv, drop_reason=reason)
        return {"k": b["k"], "title": b["title"], "model": gen, "n_items": len(items),
                "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
                "parse_error": r.get("parse_error"), "queue_stop": bool(r.get("queue_stop")),
                "relations": rels, "output_file": r.get("output_file"), "attempts": r.get("attempts")}

    gens = pmap(gen_one, beads, workers)
    audits_all.sort(key=lambda a: (a["k"], a["gidx"], a["auditor"]))
    wjson("mech.json", {"run_id": RUN_ID, "gen_model": gen, "auditors": list(auditors),
                        "records": gens, "audits": audits_all})
    return gens


# ---------------- 3. surface（逐颗串行；多 chooser 链并行） ----------------

def build_candidates(beads, why_recs, mech_recs):
    """每颗珠子的候选：[认] 标题 / [此刻] 各条 / [因为前面] / [更深]；本珠内编号 1..n。"""
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
        for gi, rel in enumerate((mc.get(k) or {}).get("relations") or []):
            if rel.get("survives"):
                L.append({"uid": "k%02d_mech%d" % (k, gi), "kind": "更深", "text": rel["relation"],
                          "meta": {"new_understanding": rel.get("new_understanding"),
                                   "explains": rel.get("explains"), "verdicts": rel.get("verdicts")}})
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
            m = (re.fullmatch(r"[Ss]\s*(\d+)", s) or re.fullmatch(r"(\d+)", s)) if s_prefix \
                else re.fullmatch(r"(\d+)", s)
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


def apply_surface(screen, parsed, cands):
    """screen: 上一段屏幕 uid 列表；parsed: 解析后的 JSON；cands: 本珠候选（id 从 1 起）。
    新屏幕 = keep 的 S 项 + show 的新项；未 keep 的旧项 = 撤下（retired）。"""
    keep = [screen[i - 1] for i in parsed["keep"]]
    show = [cands[i - 1]["uid"] for i in parsed["show"]]
    retired = [u for u in screen if u not in keep]
    new_screen = keep + [u for u in show if u not in keep]
    a = parsed["action"]
    mismatch = ((a == "保持" and bool(show or retired)) or (a == "沉默" and bool(new_screen)) or
                (a in ("补充", "更新") and not show))
    return {"keep": keep, "show": show, "retired": retired, "screen_after": new_screen,
            "expand": [cands[i - 1]["uid"] for i in parsed["expand"]],
            "recap": [cands[i - 1]["uid"] for i in parsed["recap"]], "action_mismatch": bool(mismatch)}


def run_chain(chooser, beads, cands, reg):
    screen, recs = [], []
    for b in beads:
        k = b["k"]
        C = cands[k]
        sc_items = [reg[u] for u in screen]
        prompt = build_surface_prompt(b["title"], sc_items, C)
        r = call("surface", "surf__%s__k%02d" % (chooser, k), chooser, prompt,
                 parse_surface_fn(len(sc_items), len(C)), [chooser, k], "E7_SURFACE_v0",
                 {"k": k, "chooser": chooser})
        rec = {"k": k, "title": b["title"], "time": time_of(b["title"]), "chooser": chooser,
               "screen_before": list(screen), "candidates": [it["uid"] for it in C],
               "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
               "parse_error": r.get("parse_error"), "queue_stop": bool(r.get("queue_stop")),
               "output_file": r.get("output_file"), "attempts": r.get("attempts"),
               "prompt_sha256": r.get("prompt_sha256")}
        if not r.get("parse_ok"):
            rec.update(action=None, keep=list(screen), show=[], retired=[], screen_after=list(screen),
                       expand=[], recap=[], why="", failed=True, action_mismatch=False)
            log("surface %s k%d FAILED — screen unchanged" % (chooser, k))
        else:
            p = r["parsed"]
            rec.update(apply_surface(screen, p, C), action=p["action"], why=p["why"], failed=False)
            screen = rec["screen_after"]
            log("surface %s k%d %s keep=%d show=%d retired=%d screen=%d" % (
                chooser, k, p["action"], len(rec["keep"]), len(rec["show"]), len(rec["retired"]), len(screen)))
        recs.append(rec)
    return recs


def stage_surface(_workers):
    beads = load_beads()
    cands = build_candidates(beads, rjson("why.json")["records"], rjson("mech.json")["records"])
    reg = {it["uid"]: it for L in cands.values() for it in L}
    choosers = list(CFG["choosers"])
    chains = dict(zip(choosers, pmap(lambda c: run_chain(c, beads, cands, reg), choosers, len(choosers))))
    wjson("surface.json", {"run_id": RUN_ID, "choosers": choosers, "items": reg,
                           "chains": {c: {"chooser": c, "records": chains[c]} for c in choosers}})
    return chains


# ---------------- 4. render + 统计 ----------------

KIND_TAG = re.compile(r"^\[[^\]\n]{1,8}\]\s*")


def reader_view_from_screens(steps):
    """steps: [{time, screen:[text...]}] → [{time, new, status, n_screen, screen_chars}]。"""
    prev, out = [], []
    for s in steps:
        cur = s["screen"]
        new = [t for t in cur if t not in prev]
        gone = [t for t in prev if t not in cur]
        status = "new" if new else "unchanged" if not gone else "removed_only" if cur else "cleared"
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


READING_HEAD = "# 边听边读（屏幕上新出现的内容）\n\n"


def view_stats(view):
    return {"n_steps": len(view), "n_new_lines": sum(len(s["new"]) for s in view),
            "new_chars": sum(len(t) for s in view for t in s["new"]),
            "status": dict(Counter(s["status"] for s in view)),
            "mean_screen": round(sum(s["n_screen"] for s in view) / len(view), 2) if view else 0}


def convert_run124(text=None):
    """run124 生产稿 B → 读者视图步骤：只取每站“屏幕”行，去掉 [kind] 标签；动作/why/规则/模型名都不要。"""
    text = (ROOT / RUN124_REL).read_text(encoding="utf-8") if text is None else text
    secs = list(re.finditer(r"^## 第\s*(\d+)\s*站\s*(.*)$", text, re.M))
    steps = []
    for i, m in enumerate(secs):
        end = secs[i + 1].start() if i + 1 < len(secs) else len(text)
        body = text[m.end():end]
        nxt = re.search(r"^## ", body, re.M)
        if nxt:
            body = body[:nxt.start()]
        screen, on = [], False
        for l in body.split("\n"):
            if l.startswith("- 屏幕"):
                on = True
                continue
            if on:
                if l.startswith("  - "):
                    screen.append(KIND_TAG.sub("", l[4:].strip()))
                elif l.strip():
                    on = False
        steps.append({"time": re.sub(r"^\d+\.\s*", "", m.group(2).strip()), "screen": screen})
    if not steps or not any(s["screen"] for s in steps):
        raise RuntimeError("run124 conversion found no screen lines")
    return steps


def chain_stats(recs, reg):
    ok = [r for r in recs if not r.get("failed")]
    acts = Counter(r["action"] for r in ok)
    stints, cur = [], {}
    for r in recs:
        for u in r["screen_after"]:
            cur.setdefault(u, r["k"])
        for u in list(cur):
            if u not in r["screen_after"]:
                stints.append((u, cur.pop(u), r["k"] - 1))
    for u, k0 in cur.items():
        stints.append((u, k0, recs[-1]["k"]))
    longest = max(stints, key=lambda s: (s[2] - s[1], -s[1])) if stints else None
    return {
        "n_beads": len(recs), "n_failed": len(recs) - len(ok),
        "actions": {a: acts.get(a, 0) for a in ACTIONS},
        "action_mismatch": sum(1 for r in ok if r.get("action_mismatch")),
        "mean_screen_items": round(sum(len(r["screen_after"]) for r in recs) / len(recs), 2) if recs else 0,
        "total_onscreen_chars": sum(len(reg[u]["text"]) for r in recs for u in r["screen_after"]),
        "total_shown_chars": sum(len(reg[u]["text"]) for r in recs for u in r["show"]),
        "retired_count": sum(len(r["retired"]) for r in recs),
        "onscreen_by_kind": {k: sum(1 for r in recs for u in r["screen_after"] if reg[u]["kind"] == k)
                             for k in KIND_ORDER},
        "shown_by_kind": {k: sum(1 for r in recs for u in r["show"] if reg[u]["kind"] == k) for k in KIND_ORDER},
        "staleness_hist": dict(sorted(Counter(k1 - k0 + 1 for _u, k0, k1 in stints).items())),
        "longest_streak": ({"uid": longest[0], "from_k": longest[1], "to_k": longest[2],
                            "beads": longest[2] - longest[1] + 1, "text": tagged(reg[longest[0]])}
                           if longest else None),
    }


def render_internal(chooser, recs, reg):
    L = ["# E7 诊断稿 内部视图（Op.60；chooser=%s；诊断用，不进 production）" % chooser, ""]
    for r in recs:
        L += ["## 第 %d 段 %s" % (r["k"], r["title"]), "",
              "- action：%s%s" % (r["action"] or "（解析失败，屏幕沿用）",
                                  "（与 keep/show 不一致）" if r.get("action_mismatch") else ""),
              "- why：%s" % (r.get("why") or ""),
              "- 屏幕（%d 条）：" % len(r["screen_after"])]
        L += ["  - %s%s" % ("【新】" if u in r["show"] else "", tagged(reg[u])) for u in r["screen_after"]] \
            or ["  - （空）"]
        L.append("- 撤下（%d 条）：" % len(r["retired"]))
        L += ["  - %s（第 %d 段上屏）" % (tagged(reg[u]), reg[u]["k"]) for u in r["retired"]] or ["  - （无）"]
        L += ["- 展开可看 %d 条；曲终回顾 %d 条" % (len(r["expand"]), len(r["recap"])), ""]
    return "\n".join(L)


def stage_render(_workers):
    S = rjson("surface.json")
    reg = S["items"]
    out = {"run_id": RUN_ID, "choosers": S["choosers"], "per_chooser": {}}
    for c in S["choosers"]:
        recs = S["chains"][c]["records"]
        (OUT_DIR / ("surface__%s__op60.md" % c)).write_text(render_internal(c, recs, reg), encoding="utf-8")
        view = reader_view_from_screens([{"time": r["time"], "screen": [reg[u]["text"] for u in r["screen_after"]]}
                                         for r in recs])
        (OUT_DIR / ("reading__%s__op60.md" % c)).write_text(READING_HEAD + reader_md(view), encoding="utf-8")
        out["per_chooser"][c] = {"surface_md": "surface__%s__op60.md" % c, "reading_md": "reading__%s__op60.md" % c,
                                 "stats": chain_stats(recs, reg), "reader_view": view_stats(view)}
    view_b = reader_view_from_screens(convert_run124())
    (OUT_DIR / "reading__run124B__op60.md").write_text(READING_HEAD + reader_md(view_b), encoding="utf-8")
    out["run124B"] = {"reading_md": "reading__run124B__op60.md", "reader_view": view_stats(view_b)}
    wjson("render.json", out)
    return out


# ---------------- 5. compare（三方盲比；每评审 3 次循环轮换） ----------------

def body_of(md):
    return re.sub(r"\A# [^\n]*\n+", "", md).strip()


def strip_ids(text):
    keep, removed = [], []
    for l in text.split("\n"):
        (removed if LEAK_PAT.search(l) else keep).append(l)
    return "\n".join(keep).strip(), removed


def compare_inputs():
    a_chooser = CFG["choosers"][0]
    a_raw = body_of((OUT_DIR / ("reading__%s__op60.md" % a_chooser)).read_text(encoding="utf-8"))
    b_raw = body_of((OUT_DIR / "reading__run124B__op60.md").read_text(encoding="utf-8"))
    a, a_rm = strip_ids(a_raw)
    b, b_rm = strip_ids(b_raw)
    sets = {}
    for cname, rel in VARIANTS.items():
        c, c_rm = strip_ids((ROOT / rel).read_text(encoding="utf-8"))
        sets[cname] = {"texts": {"a": a, "b": b, "c": c}, "c_source": rel,
                       "removed_lines": {"a": a_rm, "b": b_rm, "c": c_rm}}
    return sets


def rotations(seed):
    """3 次循环轮换：每个候选在 3 次里各占一次甲/乙/丙。返回 [mapping{位置:候选}]。"""
    base = ["a", "b", "c"]
    random.Random(seed).shuffle(base)
    return [dict(zip(POS, base[r:] + base[:r])) for r in range(JUDGE_RUNS)]


def compare_prompt(texts, mapping):
    return fill(TPL["E7_COMPARE_v0"], WORK=WORK_NAME, A=texts[mapping["甲"]], B=texts[mapping["乙"]],
                C=texts[mapping["丙"]])


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
        p = next((c for c in str(x).strip() if c in POS), None)
        if p is None or p in norm:
            return None, "bad ranking entry %r" % (x,)
        norm.append(p)
    res = {"ranking": norm, "why": str(obj.get("why", "")).strip()}
    for k in ("best_moments", "worst_moments", "hindsight", "only_here"):
        res[k] = obj.get(k)
    return res, None


def compare_tasks(sets, judges):
    tasks = []
    for si, cname in enumerate(sorted(sets)):
        s = sets[cname]
        for ji, judge in enumerate(judges):
            seed = SEED_COMPARE + 100 * si + ji
            for rr, mapping in enumerate(rotations(seed)):
                tasks.append({"set": cname, "c_source": s["c_source"], "judge": judge, "run": rr, "seed": seed,
                              "mapping": mapping, "prompt": compare_prompt(s["texts"], mapping)})
    return tasks


def cand_gens(set_name):
    return {"a": sorted({CFG["gen"], CFG["choosers"][0]}), "b": [RUN124_GEN], "c": [VARIANT_GEN.get(set_name, "?")]}


def self_flag(set_name, judge):
    cj = canonical_model(judge)
    hits = [c for c, gens in cand_gens(set_name).items() if cj in {canonical_model(g) for g in gens}]
    return ",".join(hits) if hits else "否"


def _agg(rs):
    ok = [r for r in rs if r["parse_ok"]]
    out = {"n": len(rs), "n_ok": len(ok)}
    for c in "abc":
        ranks = [r["ranking_true"].index(c) + 1 for r in ok]
        out["mean_rank_" + c] = round(sum(ranks) / len(ranks), 2) if ranks else None
        out["first_" + c] = sum(1 for r in ok if r["ranking_true"][0] == c)
    out["first_by_pos"] = dict(Counter(r["ranking_pos"][0] for r in ok))
    firsts = [r["ranking_true"][0] for r in ok]
    top = Counter(firsts).most_common(1)
    out["first_consistency"] = ("%d/%d（%s）" % (top[0][1], len(firsts), top[0][0])) if top else "—"
    out["full_order_consistency"] = ("%d/%d" % (Counter(tuple(r["ranking_true"]) for r in ok).most_common(1)[0][1],
                                                len(ok))) if ok else "—"
    out["rankings"] = ["".join(r["ranking_true"]) if r["parse_ok"] else "×" for r in sorted(rs, key=lambda x: x["run"])]
    return out


def aggregate(recs, judges):
    rows = []
    for s in sorted(set(r["set"] for r in recs)):
        rs_s = [r for r in recs if r["set"] == s]
        for j in list(judges) + sorted(set(r["judge"] for r in rs_s) - set(judges)):
            rs = [r for r in rs_s if r["judge"] == j]
            if rs:
                rows.append({"set": s, "judge": j, "self_judge": self_flag(s, j), **_agg(rs)})
        rows.append({"set": s, "judge": "ALL", "self_judge": "—", **_agg(rs_s)})
        indep = [r for r in rs_s if self_flag(s, r["judge"]) == "否"]
        rows.append({"set": s, "judge": "ALL-非自评", "self_judge": "—", **_agg(indep)})
    return rows


def missing_judges(recs, judges):
    out = []
    for s in sorted(VARIANTS):
        for j in judges:
            rs = [r for r in recs if r["set"] == s and r["judge"] == j]
            n_ok = sum(1 for r in rs if r["parse_ok"])
            if n_ok < JUDGE_RUNS:
                errs = sorted({str(r.get("parse_error"))[:160] for r in rs if not r["parse_ok"]})
                out.append({"set": s, "judge": j, "n_ok": n_ok, "n": JUDGE_RUNS, "errors": errs})
    return out


def export_muse_pack(sets):
    tasks = []
    for si, cname in enumerate(sorted(sets)):
        seed = SEED_COMPARE + 100 * si + SEED_MUSE
        for rr, mapping in enumerate(rotations(seed)):
            p = compare_prompt(sets[cname]["texts"], mapping)
            tasks.append({"variant": cname, "run": rr, "seed": seed, "mapping": mapping,
                          "prompt": p, "prompt_sha256": sha256s(p)})
    pack = {"run_id": RUN_ID, "judge": "muse (T3 delegate_task claude-proxy/muse-spark-1.3-contributor-free xhigh)",
            "note": "每个 task 用新的 clientRequestId 单独发 prompt 全文；不续聊。结果可写入 muse_judge_results.json："
                    "{\"results\":[{\"variant\":..., \"run\":0, \"ranking\":[\"甲\",\"乙\",\"丙\"], \"raw_file\":...}]}，"
                    "之后 `--stage report` 会把 Muse 作为额外评审并入报告。不阻塞 DONE。",
            "template": TPL_PATHS["E7_COMPARE_v0"], "template_sha256": sha256s(TPL["E7_COMPARE_v0"]),
            "positions": list(POS), "seed_scheme": "SEED_COMPARE + 100*variant_index + %d；3 次循环轮换" % SEED_MUSE,
            "candidates_note": {"a": "本稿读者视图（chooser=%s）" % CFG["choosers"][0], "b": "run124 生产稿 B 读者视图",
                                "c": "run132 V2A+Gemini 重建基线（非原始 V2A 真原稿）"},
            "tasks": tasks}
    wjson("muse_judge_pack.json", pack)
    return pack


def stage_compare(workers):
    sets = compare_inputs()
    d = OUT_DIR / "compare_inputs"
    d.mkdir(exist_ok=True)
    for name, s in sets.items():
        for who, t in s["texts"].items():
            (d / ("%s__%s.md" % (name, who))).write_text(t + "\n", encoding="utf-8")
    export_muse_pack(sets)
    tasks = compare_tasks(sets, CFG["judges"])

    def one(t):
        r = call("compare", "cmp__%s__%s__r%d" % (t["set"], t["judge"], t["run"]), t["judge"], t["prompt"],
                 parse_compare, [t["set"], t["judge"], t["run"], t["mapping"]], "E7_COMPARE_v0",
                 {"set": t["set"], "run": t["run"], "mapping": t["mapping"]})
        p = r.get("parsed") or {}
        rank_true = [t["mapping"][x] for x in p["ranking"]] if r.get("parse_ok") else None
        return dict({k: v for k, v in t.items() if k != "prompt"},
                    prompt_chars=len(t["prompt"]), parse_ok=bool(r.get("parse_ok")), cached=bool(r.get("cached")),
                    parse_error=r.get("parse_error"), queue_stop=bool(r.get("queue_stop")),
                    output_file=r.get("output_file"), prompt_sha256=r.get("prompt_sha256"),
                    ranking_pos=p.get("ranking"), ranking_true=rank_true, why=p.get("why"),
                    only_here=p.get("only_here"), best_moments=p.get("best_moments"),
                    worst_moments=p.get("worst_moments"), hindsight=p.get("hindsight"))

    recs = pmap(one, tasks, max(workers, len(CFG["judges"])))
    wjson("compare.json", {"run_id": RUN_ID, "judges": list(CFG["judges"]), "agg": aggregate(recs, CFG["judges"]),
                           "missing": missing_judges(recs, CFG["judges"]),
                           "removed_lines": {n: {w: len(v) for w, v in s["removed_lines"].items()}
                                             for n, s in sets.items()},
                           "records": recs})
    return recs


def muse_records():
    """把主会话回填的 muse_judge_results.json 映射成 compare 记录格式（可选）。"""
    f = OUT_DIR / "muse_judge_results.json"
    pf = OUT_DIR / "muse_judge_pack.json"
    if not f.exists() or not pf.exists():
        return []
    pack = json.loads(pf.read_text(encoding="utf-8"))
    tmap = {(t["variant"], t["run"]): t for t in pack["tasks"]}
    out = []
    for res in json.loads(f.read_text(encoding="utf-8")).get("results", []):
        t = tmap.get((res.get("variant"), res.get("run")))
        if not t:
            continue
        rk = res.get("ranking")
        ok = isinstance(rk, list) and sorted(rk) == sorted(POS)
        out.append({"set": t["variant"], "judge": "muse", "run": t["run"], "seed": t["seed"],
                    "mapping": t["mapping"], "parse_ok": ok, "parse_error": None if ok else "bad ranking",
                    "ranking_pos": rk if ok else None,
                    "ranking_true": [t["mapping"][x] for x in rk] if ok else None,
                    "output_file": res.get("raw_file")})
    return out


# ---------------- 6. report + manifest ----------------

def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def upstream_problems():
    """阻塞性上游失败（gen 链与主 chooser 链）。"""
    probs = []
    if (OUT_DIR / "why.json").exists():
        W = rjson("why.json")
        if len(W["records"]) != K_EXPECTED - 1:
            probs.append("why 记录 %d/%d" % (len(W["records"]), K_EXPECTED - 1))
        probs += ["why k%d 失败：%s" % (r["k"], r.get("parse_error")) for r in W["records"] if not r["parse_ok"]]
    if (OUT_DIR / "mech.json").exists():
        M = rjson("mech.json")
        probs += ["mech k%d 失败：%s" % (r["k"], r.get("parse_error")) for r in M["records"] if not r["parse_ok"]]
    if (OUT_DIR / "surface.json").exists():
        S = rjson("surface.json")
        c0 = S["choosers"][0]
        probs += ["surface %s k%d 失败：%s" % (c0, r["k"], r.get("parse_error"))
                  for r in S["chains"][c0]["records"] if r.get("failed")]
    return probs


def stage_report():
    S = rjson("surface.json")
    reg = S["items"]
    R = rjson("render.json")
    W = rjson("why.json")
    M = rjson("mech.json")
    C = rjson("compare.json") if (OUT_DIR / "compare.json").exists() else {"records": [], "missing": [],
                                                                            "judges": list(CFG["judges"])}
    mrecs = muse_records()
    recs_all = C["records"] + mrecs
    judges_all = list(C["judges"]) + (["muse"] if mrecs else [])
    agg = aggregate(recs_all, judges_all) if recs_all else []
    c0 = S["choosers"][0]
    L = ["# run149 E7 诊断性整篇样稿（Op.60；诊断用，不进 production）", "",
         "- 生成（why/mech）：`%s`；chooser 链：%s；MECH 审核：%s；评审：%s；历史清单：`%s`" % (
             W["gen_model"], "、".join("`%s`" % c for c in S["choosers"]), "、".join(M["auditors"]),
             "、".join(judges_all), W["history_source"]),
         "- MUSIC_WEB_ROUTE=`%s`；opus 键本进程豁免旧“禁新 Opus”check_policy：%s（用户 10-06/10-09 授权）" % (
             os.environ.get("MUSIC_WEB_ROUTE"), "是" if OPUS_OVERRIDE["on"] else "否"),
         "- c 候选来自 run132 V2A+Gemini **重建**基线（Op.60 无原始 V2A 稿；重建 ≠ 原稿）。",
         "- 本报告只列脚本算出的数字与原文路径，不做审美裁决。", "",
         "## 1. 上游", "",
         "- why：%d 颗中 differs=true %d、false %d、失败 %d" % (
             len(W["records"]), sum(1 for r in W["records"] if r["parse_ok"] and r["differs"]),
             sum(1 for r in W["records"] if r["parse_ok"] and not r["differs"]),
             sum(1 for r in W["records"] if not r["parse_ok"])),
         "- mech：生成关系 %d 条（生成失败 %d 颗），双审后存活 %d 条" % (
             sum(len(r["relations"]) for r in M["records"]), sum(1 for r in M["records"] if not r["parse_ok"]),
             sum(1 for r in M["records"] for x in r["relations"] if x.get("survives"))),
         "- 审核判定分布：%s" % "；".join(
             "%s %s" % (au, json.dumps(dict(Counter((a["class"] if a["parse_ok"] else "audit_failed")
                                                   for a in M["audits"] if a["auditor"] == au)), ensure_ascii=False))
             for au in M["auditors"]), ""]
    # 2. 屏幕统计
    cs = S["choosers"]
    L += ["## 2. 屏幕统计（每条 chooser 链）", "", "| 指标 | %s |" % " | ".join(cs), "|---|%s" % ("---|" * len(cs))]
    st = {c: R["per_chooser"][c]["stats"] for c in cs}
    rows = [("动作 更新/补充/保持/沉默", lambda s: "/".join(str(s["actions"][a]) for a in ACTIONS)),
            ("解析失败段数", lambda s: s["n_failed"]), ("动作与 keep/show 不一致", lambda s: s["action_mismatch"]),
            ("平均屏幕条数", lambda s: s["mean_screen_items"]), ("屏幕总字数（逐段累加）", lambda s: s["total_onscreen_chars"]),
            ("新上屏总字数", lambda s: s["total_shown_chars"]), ("撤下条数", lambda s: s["retired_count"]),
            ("在屏条目按类型（逐段累加）", lambda s: json.dumps(s["onscreen_by_kind"], ensure_ascii=False)),
            ("新上屏按类型", lambda s: json.dumps(s["shown_by_kind"], ensure_ascii=False)),
            ("停留段数分布", lambda s: json.dumps(s["staleness_hist"], ensure_ascii=False))]
    for name, fn in rows:
        L.append("| %s | %s |" % (name, " | ".join(cell(fn(st[c])) for c in cs)))
    L.append("")
    for c in cs:
        ls = st[c]["longest_streak"]
        if ls:
            L.append("- %s 最长连续在屏：%d 段（第 %d–%d 段）：%s" % (c, ls["beads"], ls["from_k"], ls["to_k"], ls["text"]))
    L += ["- 读者视图：%s；run124 B：%s" % (
        "；".join("%s %s" % (c, json.dumps(R["per_chooser"][c]["reader_view"], ensure_ascii=False)) for c in cs),
        json.dumps(R["run124B"]["reader_view"], ensure_ascii=False)), ""]
    # 3. 盲比
    L += ["## 3. 三方盲比（a=reading__%s，b=run124 生产稿 B 读者视图，c=run132 重建基线）" % c0, "",
          "候选背后的模型：a=%s；b=%s；c=gpro 变体 %s / gflash 变体 %s。“自评”列标出评审是哪个候选的生成模型"
          "（canonical 归一，gflash_web=gflash）。名次序列按 3 次轮换的顺序列出（真候选字母，第一名在前）。" % (
              "、".join(cand_gens("")["a"]), RUN124_GEN, VARIANT_GEN["c_gpro_s3"], VARIANT_GEN["c_gflash_s1"]), "",
          "| 变体 | 评审 | 自评 | ok/n | 三次名次 | 平均名次 a | b | c | 第一 a/b/c | 第一名一致 | 全序一致 | 第一按位置 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in agg:
        L.append("| %s | %s | %s | %d/%d | %s | %s | %s | %s | %d/%d/%d | %s | %s | %s |" % (
            r["set"], r["judge"], r["self_judge"], r["n_ok"], r["n"], " ".join(r["rankings"]) if r["judge"] not in (
                "ALL", "ALL-非自评") else "—", r["mean_rank_a"], r["mean_rank_b"], r["mean_rank_c"],
            r["first_a"], r["first_b"], r["first_c"], r["first_consistency"], r["full_order_consistency"],
            cell(json.dumps(r["first_by_pos"], ensure_ascii=False))))
    if not agg:
        L.append("| — | （无评审结果） | | | | | | | | | | |")
    miss = C.get("missing") or []
    L += ["", "缺席/不完整评审（不阻塞 DONE）：" + ("无" if not miss else "")]
    for m in miss:
        L.append("- %s / %s：%d/%d 成功；%s" % (m["set"], m["judge"], m["n_ok"], m["n"], "；".join(m["errors"]) or "—"))
    L.append("- Muse：%s" % ("已并入（muse_judge_results.json）" if mrecs else
                             "未并入；盲审包 `muse_judge_pack.json`（主会话自行派发，不阻塞）"))
    rm = C.get("removed_lines") or {}
    if rm:
        L.append("- 去身份时删掉的行数：%s" % json.dumps(rm, ensure_ascii=False))
    L += ["", "评审原文：", ""]
    for r in recs_all:
        L.append("- %s / %s / 第%d次 映射=%s → %s：`%s`" % (
            r["set"], r["judge"], r["run"] + 1, json.dumps(r["mapping"], ensure_ascii=False),
            "".join(r["ranking_true"]) if r["parse_ok"] else "失败(%s)" % cell(str(r.get("parse_error"))[:120]),
            ("runs/%s/%s" % (RUN_ID, r["output_file"])) if r.get("output_file") else "—"))
    # 4. 撤下示例
    recs0 = S["chains"][c0]["records"]
    L += ["", "## 4. 撤下示例（%s 链，5 条，均匀抽取）" % c0, ""]
    ret = [(r["k"], u) for r in recs0 for u in r["retired"]]
    pick = [ret[int(i * (len(ret) - 1) / 4)] for i in range(5)] if len(ret) >= 5 else ret
    for k, u in pick:
        L.append("- 第 %d 段撤下（第 %d 段上屏）：%s" % (k, reg[u]["k"], tagged(reg[u])))
    if not pick:
        L.append("（无撤下）")
    L += ["", "## 5. 上屏的 [因为前面] / [更深]（%s 链）" % c0, ""]
    n = 0
    for r in recs0:
        for u in r["show"]:
            if reg[u]["kind"] in ("因为前面", "更深"):
                n += 1
                L.append("- 第 %d 段 %s" % (r["k"], tagged(reg[u])))
    if not n:
        L.append("（无）")
    probs = upstream_problems()
    other = ["surface %s k%d 失败" % (c, r["k"]) for c in cs[1:] for r in S["chains"][c]["records"] if r.get("failed")]
    other += ["audit %s k%d r%d 失败：%s" % (a["auditor"], a["k"], a["gidx"], a.get("parse_error"))
              for a in M["audits"] if not a["parse_ok"]]
    L += ["", "## 6. 失败与缺项", ""] + (["- 阻塞：" + p for p in probs] + ["- 非阻塞：" + p for p in other] or ["（无）"])
    L += ["", "## 7. 文件", "",
          "- 内部稿 %s；读者视图 %s；run124 读者视图 `reading__run124B__op60.md`；三方输入 `compare_inputs/`" % (
              "、".join("`surface__%s__op60.md`" % c for c in cs), "、".join("`reading__%s__op60.md`" % c for c in cs)),
          "- 提示词/原始输出：`prompts/`、`outputs/`、`meta/`；逻辑调用日志 `cache_*.json`；哈希 `run_manifest.json`；"
          "Muse 盲审包 `muse_judge_pack.json`", ""]
    (OUT_DIR / "report.md").write_text("\n".join(L), encoding="utf-8")
    return agg


def write_manifest(extra):
    outs = {}
    for p in sorted(OUT_DIR.rglob("*")):
        rel = p.relative_to(OUT_DIR)
        if not p.is_file() or p.suffix == ".tmp" or any(x.startswith("_") or x == "__pycache__" for x in rel.parts):
            continue
        if p.name in ("run_manifest.json", "run.log", "DONE", "FAILED"):
            continue
        outs[str(rel).replace("\\", "/")] = sha256_file(p)
    hist_rel = HIST_FILES.get(CFG["history"].partition(":")[0])
    inputs = [BEADS_REL, RUN124_REL] + list(VARIANTS.values()) + ([hist_rel] if hist_rel else [])
    keys = {CFG["gen"], *CFG["choosers"], *CFG["auditors"], *CFG["judges"]}
    man = {"run_id": RUN_ID, "git_head": git_commit(), "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "script": {"runs/%s/go.py" % RUN_ID: sha256_file(THIS_DIR / "go.py")},
           "templates": {v: sha256_file(ROOT / v) for v in TPL_PATHS.values()},
           "inputs": {k: sha256_file(ROOT / k) for k in inputs if (ROOT / k).exists()},
           "models": {"gen": CFG["gen"], "choosers": list(CFG["choosers"]), "auditors": list(CFG["auditors"]),
                      "judges": list(CFG["judges"]), "model_names": {k: runner.MODEL_NAMES.get(k, k) for k in sorted(keys)}},
           "history_source": CFG["history"],
           "env": {"MUSIC_WEB_ROUTE": os.environ.get("MUSIC_WEB_ROUTE"), "GPT2_KEYS": list(runner.GPT2_KEYS),
                   "MG_KEYS": list(runner.MG_KEYS)},
           "opus_policy_override": {"on": OPUS_OVERRIDE["on"], "scope": "only model key 'opus' in this process",
                                    "reason": "user 10-06 '你现在可以随便用opus'; user 10-09 full judge panel incl. opus; "
                                              "execution_integrity.check_policy still carries the 10-03 rule"},
           "candidate_generators": {s: cand_gens(s) for s in VARIANTS},
           "reconstruction_note": "c = run132 V2A+Gemini reconstructed baseline for Op.60, not an original V2A output",
           "compare": {"seed_base": SEED_COMPARE, "runs_per_judge": JUDGE_RUNS, "positions": list(POS),
                       "muse_seed_offset": SEED_MUSE},
           "extra": extra or {}, "outputs": outs}
    wjson("run_manifest.json", man)
    return man


def snapshot_calls():
    with LOCK:
        return {"n": CALLS["n"], "by": {k: dict(v) for k, v in CALLS["by"].items()}}


# ---------------- 运行 ----------------

STAGES = ("why", "mech", "surface", "render", "compare", "report")


class UpstreamFailed(RuntimeError):
    pass


def _gate(after):
    probs = upstream_problems()
    if probs:
        raise UpstreamFailed("阶段 %s 后上游有失败（重跑即续）：\n%s" % (after, "\n".join(probs)))


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
    if "why" in stages or "mech" in stages:
        _gate("why/mech")
    if "surface" in stages:
        stage_surface(workers)
        _gate("surface")
    if "render" in stages:
        stage_render(workers)
    if "compare" in stages:
        stage_compare(workers)
    if "report" in stages:
        stage_report()


def finish(stages, t0):
    """写 manifest + DONE/FAILED。返回 (ok, text)。"""
    for n in ("DONE", "FAILED"):
        try:
            (OUT_DIR / n).unlink()
        except OSError:
            pass
    calls = snapshot_calls()
    if "report" not in stages:
        write_manifest({"calls": calls, "stages": stages, "partial": True})
        return True, "stages=%s ok (no DONE: report stage not run)" % stages
    C = rjson("compare.json") if (OUT_DIR / "compare.json").exists() else {"records": [], "missing": []}
    n_ok = sum(1 for r in C["records"] if r["parse_ok"])
    probs = upstream_problems()
    if not n_ok:
        probs.append("没有任何评审结果")
    write_manifest({"calls": calls, "stages": stages, "missing_judges": C.get("missing"), "problems": probs})
    stamp = time.strftime("%m-%d %H:%M:%S")
    if probs:
        txt = "stages=%s at %s\n%s\n" % (stages, stamp, "\n".join(probs))
        (OUT_DIR / "FAILED").write_text(txt, encoding="utf-8")
        return False, txt
    miss = ["%s/%s %d/%d" % (m["set"], m["judge"], m["n_ok"], m["n"]) for m in C.get("missing") or []]
    txt = "stages=%s at %s new_calls=%d judge_ok=%d/%d %.0fs\nmissing judges: %s\n" % (
        stages, stamp, calls["n"], n_ok, len(C["records"]), time.time() - t0, "；".join(miss) or "none")
    (OUT_DIR / "DONE").write_text(txt, encoding="utf-8")
    return True, txt


def run_all(out_dir, stages, workers):
    global OUT_DIR
    OUT_DIR = Path(out_dir)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STORES.clear()
    t0 = time.time()
    try:
        run_stages(stages, workers)
    except UpstreamFailed as e:
        write_manifest({"calls": snapshot_calls(), "stages": stages, "failed": str(e)})
        (OUT_DIR / "FAILED").write_text("stages=%s at %s\n%s\n" % (stages, time.strftime("%m-%d %H:%M:%S"), e),
                                        encoding="utf-8")
        try:
            (OUT_DIR / "DONE").unlink()
        except OSError:
            pass
        return False, str(e)
    return finish(stages, t0)


# ---------------- mock ----------------

MOCK = {"calls": 0, "by_model": Counter()}


def fake_run_job(run_dir, job, timeout=3600):
    run_dir = Path(run_dir)
    for d in ("prompts", "outputs", "meta"):
        (run_dir / d).mkdir(parents=True, exist_ok=True)
    br, ex, p, model = job["branch"], job.get("extra") or {}, job["prompt"], job["model_key"]
    k, att = ex.get("k", 0), ex.get("attempt", 0)
    jid = job["job_id"]
    with LOCK:
        MOCK["calls"] += 1
        MOCK["by_model"][model] += 1
    assert not (run_dir / "meta" / (jid + ".json")).exists(), "job id reused: " + jid
    status, err, qs = "ok", None, False
    if br == "why":
        out = json.dumps({"differs": k % 3 != 0, "sentence": ("MOCK因为前面k%d" % k) if k % 3 else "无"},
                         ensure_ascii=False)
        if k == 4 and att == 0:
            status, err, out = "failed", "exit 1: mock transient", ""  # 运行失败 → 重试
    elif br == "mech":
        out = json.dumps([{"relation": "MOCK更深A k%d" % k, "explains": [1, 2], "new_understanding": "MOCK"},
                          {"relation": "MOCK更深B k%d" % k, "explains": [1, 3], "new_understanding": "MOCK"}]
                         if k % 2 else [], ensure_ascii=False)
    elif br == "audit":
        bad = ex.get("gidx") == 1 and model == "gflash_web"
        out = json.dumps({"class": "manufactured" if bad else "insight", "why": "MOCK"}, ensure_ascii=False)
    elif br == "surface":
        if k == 3 and att == 0:
            out = "not json at all"  # 解析失败 → 重试
        else:
            head, _, tail = p.partition("【这一段可以给读者的内容】")
            n_s = len(re.findall(r"^S\d+\. ", head, re.M))
            lines = re.findall(r"^(\d+)\. \[([^\]]+)\]", tail, re.M)
            if k % 5 == 0 and n_s:
                obj = {"action": "保持", "keep": ["S%d" % i for i in range(1, n_s + 1)], "show": []}
            else:
                pick = min(1 if ex.get("chooser") == "gpt56w" else 2, len(lines) - 1)
                show = [int(lines[pick][0])] + [int(i) for i, kind in lines if kind in ("因为前面", "更深")][:1]
                obj = {"action": "补充" if n_s else "更新",
                       "keep": ["S%d" % i for i in range(1, n_s + 1) if i % 2 == 0 and i <= 4], "show": show}
            obj.update({"expand": [1], "recap": [], "why": "MOCK"})
            out = json.dumps(obj, ensure_ascii=False)
    elif br == "compare":
        body = p.split("【甲】", 1)[1]
        for bad in ("gpt56w", "run124", "run122", "Gemini", "gpro", "[此刻]", "[更深]", "action", "why："):
            assert bad not in body, "compare prompt leaks %r" % bad
        if model == "gpt6w":  # 模拟某一路评审整路不可用（provider hold）
            status, err, qs, out = "failed", "gpt2 queue held: mock", True, ""
        else:
            out = json.dumps({"ranking": ["乙", "甲", "丙"], "why": "MOCK", "best_moments": {}, "worst_moments": {},
                              "hindsight": {}, "only_here": {}}, ensure_ascii=False)
    else:
        out = "好"
    (run_dir / "prompts" / (jid + ".txt")).write_text(p, encoding="utf-8")
    (run_dir / "outputs" / (jid + ".md")).write_text(out, encoding="utf-8")
    meta = {"job_id": jid, "status": status, "error": err, "queue_stop": qs, "seconds": 0.0, "model_key": model,
            "output_file": "outputs/%s.md" % jid, "extra": ex}
    (run_dir / "meta" / (jid + ".json")).write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return meta


def run_mock(workers=6, keep_dir=None):
    """全流程假调用（临时目录），断言关键性质；返回 (ok, info)。"""
    global OUT_DIR, RUN_JOB
    tmp = Path(keep_dir) if keep_dir else Path(tempfile.mkdtemp(prefix="run149_mock_"))
    real_before = sorted(p.name for p in RUN_DIR.iterdir()) if RUN_DIR.exists() else []
    saved = (OUT_DIR, RUN_JOB)
    RUN_JOB = fake_run_job
    MOCK.update(calls=0, by_model=Counter())
    CALLS.update(n=0, by={})
    info = {}
    try:
        ok, txt = run_all(tmp, list(STAGES), workers)
        assert ok, txt
        first = MOCK["calls"]
        W, Mj, S = rjson("why.json"), rjson("mech.json"), rjson("surface.json")
        assert len(W["records"]) == K_EXPECTED - 1 and all(r["parse_ok"] for r in W["records"])
        w4 = next(r for r in W["records"] if r["k"] == 4)
        assert len(w4["attempts"]) == 2 and w4["attempts"][0]["status"] == "failed", "run-failure retry not exercised"
        assert len(Mj["records"]) == K_EXPECTED and all(r["parse_ok"] for r in Mj["records"])
        rels = [x for r in Mj["records"] for x in r["relations"]]
        assert any(x["survives"] for x in rels) and any(not x["survives"] for x in rels)
        assert all(set(x["verdicts"]) == set(CFG["auditors"]) for x in rels)
        for c in CFG["choosers"]:
            rs = S["chains"][c]["records"]
            assert len(rs) == K_EXPECTED and all(not r["failed"] for r in rs), c
            assert len(rs[2]["attempts"]) == 2, "k3 parse-retry not exercised"
        assert S["chains"]["gpt56w"]["records"][0]["show"] != S["chains"]["opus"]["records"][0]["show"]
        R = rjson("render.json")
        for c in CFG["choosers"]:
            st = R["per_chooser"][c]["stats"]
            assert st["retired_count"] > 0 and st["actions"]["保持"] > 0 and st["longest_streak"], st
            rd = (OUT_DIR / ("reading__%s__op60.md" % c)).read_text(encoding="utf-8")
            assert "（屏幕不变）" in rd and "[此刻]" not in rd and "S1" not in rd and "MOCK因为前面" in rd
            assert (OUT_DIR / ("surface__%s__op60.md" % c)).exists()
        Cj = rjson("compare.json")
        nj = len(CFG["judges"])
        assert len(Cj["records"]) == len(VARIANTS) * nj * JUDGE_RUNS
        assert all(r["parse_ok"] == (r["judge"] != "gpt6w") for r in Cj["records"])
        assert {m["judge"] for m in Cj["missing"]} == {"gpt6w"}
        for s in VARIANTS:
            for j in CFG["judges"]:
                rs = [r for r in Cj["records"] if r["set"] == s and r["judge"] == j]
                for c in "abc":
                    assert sorted(next(p for p, v in r["mapping"].items() if v == c) for r in rs) == sorted(POS)
        fl = {(r["set"], r["judge"]): r["self_judge"] for r in Cj["agg"]}
        assert fl[("c_gpro_s3", "gpt56w")] == "a,b" and fl[("c_gflash_s1", "gflash_web")] == "c"
        assert fl[("c_gpro_s3", "gflash_web")] == "否" and fl[("c_gpro_s3", "luna_noweb")] == "否"
        pack = rjson("muse_judge_pack.json")
        assert len(pack["tasks"]) == len(VARIANTS) * JUDGE_RUNS
        assert all("【甲】" in t["prompt"] for t in pack["tasks"])
        rep = (OUT_DIR / "report.md").read_text(encoding="utf-8")
        assert "gpt6w" in rep and "缺席" in rep and "重建" in rep and "撤下示例" in rep
        assert (OUT_DIR / "DONE").exists() and not (OUT_DIR / "FAILED").exists()
        man = rjson("run_manifest.json")
        assert man["env"]["MUSIC_WEB_ROUTE"] and man["inputs"] and man["templates"]
        # Muse 回填 → 报告并入
        (OUT_DIR / "muse_judge_results.json").write_text(json.dumps({"results": [
            {"variant": t["variant"], "run": t["run"], "ranking": ["丙", "甲", "乙"]} for t in pack["tasks"]]},
            ensure_ascii=False), encoding="utf-8")
        ok_r, _ = run_all(tmp, ["report"], workers)
        assert ok_r and "| muse |" in (OUT_DIR / "report.md").read_text(encoding="utf-8")
        # 断点续跑：再跑全流程 → 新调用只来自仍缺席的 gpt6w（每次续跑每个逻辑调用至多 1 次，因 queue_stop）
        STORES.clear()
        ok2, txt2 = run_all(tmp, list(STAGES), workers)
        assert ok2, txt2
        extra = MOCK["calls"] - first
        assert extra == len(VARIANTS) * JUDGE_RUNS, "resume made %d new calls (expected only gpt6w retries)" % extra
        info = {"calls_first": first, "calls_rerun": extra, "by_model": dict(MOCK["by_model"]),
                "max_prompt_chars": {"why": max(r["prompt_chars"] for r in W["records"]),
                                     "compare": max(r["prompt_chars"] for r in Cj["records"])},
                "stats_gpt56w": {k: R["per_chooser"]["gpt56w"]["stats"][k]
                                 for k in ("actions", "retired_count", "mean_screen_items")}}
        print("MOCK149 OK: %s" % json.dumps(info, ensure_ascii=False), flush=True)
    finally:
        if not keep_dir:
            shutil.rmtree(tmp, ignore_errors=True)
        STORES.clear()
        OUT_DIR, RUN_JOB = saved
    real_after = sorted(p.name for p in RUN_DIR.iterdir()) if RUN_DIR.exists() else []
    assert real_before == real_after, "mock touched real run dir"
    return True, info


def run_smoke(keys, timeout):
    """每个键一次极短真实调用；产物在 _smoke/（manifest 不收）。"""
    global OUT_DIR
    saved = OUT_DIR
    OUT_DIR = RUN_DIR / "_smoke"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%m%d%H%M%S")

    def one(key):
        job = {"job_id": "smoke__%s__%s" % (key, stamp), "branch": "smoke", "model_key": key, "prompt": "只回复：好",
               "prompt_version": "smoke", "prompt_template": "(smoke)", "work_key": WORK_KEY, "work_name": WORK_NAME,
               "sample": 1, "extra": {"smoke": True, "run": RUN_ID},
               "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
               "max_attempts": 1}
        t0 = time.time()
        try:
            meta = runner.run_job(str(OUT_DIR), job, timeout=timeout)
            return key, {"status": meta.get("status"), "error": meta.get("error"),
                         "reply": _read_rel(meta.get("output_file"))[:80], "seconds": round(time.time() - t0, 1)}
        except Exception as e:
            return key, {"status": "exception", "error": "%s: %s" % (type(e).__name__, e)}

    try:
        res = dict(pmap(one, list(keys), len(keys)))
        (OUT_DIR / ("smoke_%s.json" % stamp)).write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                        encoding="utf-8")
    finally:
        OUT_DIR = saved
    print(json.dumps(res, ensure_ascii=False, indent=1), flush=True)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES + ("all",), default="all")
    ap.add_argument("--gen-model", default=CFG["gen"])
    ap.add_argument("--choosers", default=",".join(CFG["choosers"]))
    ap.add_argument("--auditors", default=",".join(CFG["auditors"]))
    ap.add_argument("--judges", default=",".join(CFG["judges"]))
    ap.add_argument("--history-source", default=CFG["history"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--smoke-keys", default="gflash_web,luna_noweb,opus")
    ap.add_argument("--smoke-timeout", type=int, default=600)
    a = ap.parse_args(argv)
    CFG.update(gen=a.gen_model, history=a.history_source,
               choosers=tuple(x for x in a.choosers.split(",") if x),
               auditors=tuple(x for x in a.auditors.split(",") if x),
               judges=tuple(x for x in a.judges.split(",") if x))
    if a.mock:
        ok, _ = run_mock(a.workers)
        return 0 if ok else 1
    install_opus_override()
    if a.smoke:
        run_smoke([k for k in a.smoke_keys.split(",") if k], a.smoke_timeout)
        return 0
    stages = list(STAGES) if a.stage == "all" else [a.stage]
    log("run149 start stages=%s route=%s gen=%s choosers=%s judges=%s" % (
        stages, os.environ.get("MUSIC_WEB_ROUTE"), CFG["gen"], CFG["choosers"], CFG["judges"]))
    try:
        ok, txt = run_all(RUN_DIR, stages, a.workers)
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        (RUN_DIR / "FAILED").write_text("stages=%s at %s\n%s" % (stages, time.strftime("%m-%d %H:%M:%S"), tb),
                                        encoding="utf-8")
        try:
            write_manifest({"calls": snapshot_calls(), "stages": stages, "exception": tb[-2000:]})
        except Exception:
            pass
        return 1
    log("run149 %s: %s" % ("DONE" if ok else "FAILED", txt.strip()))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
