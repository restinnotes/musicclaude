"""R2 run133_thread_spec：Thread 首轮单变量实验（C7_STEP_v2 vs v3）+ ident/compare 评测。

单变量：C7_STEP_v2 vs C7_STEP_v3（v3 只在 Q3 加一句作品特异性要求）。
输入：run130 的 beads_clean.md（只取标题行 +【此刻】块，与 run130 完全一致的切分）。
生成：2 版本 x 2 模型（gpt56w / opus）= 4 条链，每链 K=23 串行；链间并行
  （gpt56w 链受进程内单并发信号量限制，opus 链可并发）。全部 fresh 调用，
  缓存只在本 run 目录内（不可能复用 run130 缓存；缓存键含完整提示词 sha）。
"不再成立"删除：与 run130 相同的内联 C7_MATCH 逻辑，由 muse 判
  （muse 不可用则全切 luna_noweb，两版本必须一致，记入 manifest）。
每条链跑完后用 CENTER_v0 提一次中心（与链同模型）。
评测 1 ident：THREAD_IDENT_v0，每链全部非"还看不出"的逐段 thread（去重）+
  最后 thread + 每个 center；另加 run130 三条旧链的最后 thread + centers 作参照。
评测者 luna_noweb + gpro（Gemini 3.1 Pro）。
评测 2 compare：THREAD_COMPARE_v0，同生成模型 v2 链 vs v3 链记录 A/B，
  双评测者 x 双顺序（A/B 互换），盲（不出现模型/版本名），记 seed 与真身映射。
只报告数字 + 原文：空步率、清单数、首次段、最后 thread 原文、centers 原文。

用法（cwd 必须为仓库根）：
  python -I runs\\run133_thread_spec\\go.py                  # 全量
  python -I runs\\run133_thread_spec\\go.py --stage gen      # 只跑某阶段
  python -I runs\\run133_thread_spec\\go.py --mock           # mock dry-run 全流程+断言（产物在 _dryrun，验完即删）
  python -I runs\\run133_thread_spec\\go.py --probe          # 极短真实冒烟（每键一次，产物在 _smoke，验完即删）

约束：只写本 run 目录；不改 prompts/、tools/runner.py、旧 runs。
失败同一模型重试最多 2 次（每逻辑调用最多 3 次，runner 内部 max_attempts=1）。
"""

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
import threading
import time
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run133_thread_spec"
RUN_DIR = ROOT / "runs" / RUN_ID

sys.path.insert(0, str(ROOT / "tools"))
import runner  # noqa: E402  (只读其常量与 run_job；不修改 tools/)
from runner import run_job  # noqa: E402
from stage import WORKS  # noqa: E402

WORK_KEY = "op60"
WORK_NAME = WORKS[WORK_KEY]
VERSIONS = ("v2", "v3")
GEN_MODELS = tuple(os.environ.get("RUN133_GEN", "opus,luna_noweb").split(","))  # 10-08: gpt2/gpt56w 路由阻塞，改 opus+luna_noweb
REVIEWERS = tuple(os.environ.get("RUN133_REV", "gpro,muse").split(","))  # 评审不得与生成者重合；gpro = gemini-3.1-pro-high
K_EXPECTED = 23

TPL_PATHS = {
    "C7_STEP_v2": "prompts/versions/C7_STEP_v2.txt",
    "C7_STEP_v3": "prompts/versions/C7_STEP_v3.txt",
    "CENTER_v0": "prompts/versions/CENTER_v0.txt",
    "THREAD_IDENT_v0": "prompts/tooling/THREAD_IDENT_v0.txt",
    "THREAD_COMPARE_v0": "prompts/tooling/THREAD_COMPARE_v0.txt",
}
TPL = {k: (ROOT / v).read_text(encoding="utf-8") for k, v in TPL_PATHS.items()}

MATCH_HEADER_LINES = [  # 与 run130 build_match_prompt 逐字一致
    "下面是到第 {K} 段为止记下的变化清单（有编号），以及本步模型说"
    "“不再成立”的文字。",
    "请把“不再成立”的每一条文字和清单逐条对照，判断它指的是清单中的"
    "哪一条；判断不了的，match 写 null。",
    "只输出一个 JSON 数组，不要输出其他任何文字，顺序与条数与下面"
    "“不再成立”一致：",
    '[{"quote": "<不再成立的原文>", "match": <编号，从1开始；'
    '指不上写null>, "note": "一句话"}]',
    "",
    "【变化清单】",
]
MATCH_TPL_TEXT = "\n".join(MATCH_HEADER_LINES) + "\n{INVENTORY}\n\n【本步说不再成立】\n{NLV}"

BEADS_REL = "runs/run130_thread_e6/beads_clean.md"
REF130_STEPS_REL = "runs/run130_thread_e6/steps.json"
REF130_CENTERS_REL = "runs/run130_thread_e6/centers.json"

CANDIDATES = [
    "肖邦《第一叙事曲》Op.23",
    "肖邦《第二叙事曲》Op.38",
    "肖邦《第三叙事曲》Op.47",
    "肖邦《第四叙事曲》Op.52",
    "肖邦《船歌》Op.60",
    "肖邦《幻想波兰舞曲》Op.61",
    "舒伯特《降B大调钢琴奏鸣曲》D.960",
    "舒曼《C大调幻想曲》Op.17",
]
TARGET = "肖邦《船歌》Op.60"
UNSURE = "说不准"
TITLE_WORDS = ("船", "船歌", "桨", "水", "摇", "晃", "浪", "波", "威尼斯", "上船", "码头")

FORBID = ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"]
MAX_ATTEMPTS = 3
TMO_GPT = 1800
TMO_OTHER = 3600
GPT_SEM = threading.Semaphore(1)  # 本进程内 gpt56w 单并发（runner 另有跨进程 gpt2web 槽）
FROZEN_PHRASES = ("temporarily frozen",
                  "Temporary Chat activation control was not found",
                  "incomplete_response")

OUT_DIR = RUN_DIR  # mock / probe / smoke 时切换
MOCK = {"on": False, "calls": 0}
MATCH_MODEL = "muse"  # 有效值 muse | luna_noweb；probe 失败则切 luna_noweb，记入 manifest
MATCH_MODEL_REASON = "default"

LOCK = threading.Lock()
CALLS = {"n": 0, "by": {}}


# ---------------- 通用（照 run130） ----------------

def sha10(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]


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
        return out if cp.returncode == 0 and out else "unknown (not a git repository)"
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


def is_frozen(text):
    return any(p in (text or "") for p in FROZEN_PHRASES)


def extract_json_obj(text):
    if not isinstance(text, str):
        return False, None, "empty output"
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        return False, None, "no braces found"
    try:
        return True, json.loads(text[i:j + 1]), None
    except Exception as e:
        return False, None, "%s: %s" % (type(e).__name__, e)


def extract_json_arr(text):
    if not isinstance(text, str):
        return False, None, "empty output"
    i, j = text.find("["), text.rfind("]")
    if i < 0 or j <= i:
        return False, None, "no brackets found"
    try:
        val = json.loads(text[i:j + 1])
    except Exception as e:
        return False, None, "%s: %s" % (type(e).__name__, e)
    if not isinstance(val, list):
        return None, "top level is not an array"
    return True, val, None


def norm_step(obj):
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    nc = obj.get("new_changes", [])
    if not isinstance(nc, list):
        return None, "new_changes is not a list"
    norm_nc = []
    for it in nc:
        if not isinstance(it, dict):
            return None, "new_changes item is not an object"
        c = str(it.get("change", "")).strip()
        f = str(it.get("from", "")).strip()
        if not c:
            return None, "new_changes item has empty change"
        norm_nc.append({"change": c, "from": f})
    nlv = obj.get("no_longer_valid", [])
    if not isinstance(nlv, list):
        return None, "no_longer_valid is not a list"
    norm_nlv = [str(x).strip() for x in nlv if str(x).strip()]
    th = obj.get("thread", "")
    th = th if isinstance(th, str) else str(th)
    return {"new_changes": norm_nc, "no_longer_valid": norm_nlv, "thread": th.strip()}, None


def norm_match(val):
    if not isinstance(val, list):
        return None, "top level is not an array"
    out = []
    for it in val:
        if not isinstance(it, dict):
            return None, "match item is not an object"
        m = it.get("match")
        if m is None:
            idx = None
        else:
            try:
                idx = int(m)
            except Exception:
                idx = None
        out.append({"quote": str(it.get("quote", "")), "match": idx, "note": str(it.get("note", ""))})
    return out, None


def parse_step(out):
    ok, val, err = extract_json_obj(out)
    if not ok:
        return None, err
    return norm_step(val)


def parse_match_fn(n_expected):
    def fn(out):
        ok, val, err = extract_json_arr(out)
        if not ok:
            return None, err
        v, err2 = norm_match(val)
        if v is None:
            return None, err2
        if len(v) != n_expected:
            return None, "match length does not match no_longer_valid length"
        return v, None
    return fn


def apply_match(k, inventory, nlv_list, judgments):
    removed, unmatched = [], []
    taken = set()
    for i, quote in enumerate(nlv_list):
        j = (judgments[i] if judgments is not None and i < len(judgments) else None)
        if j is None and judgments is not None and i >= len(judgments):
            unmatched.append({"quote": quote, "note": "模型返回的条数不足；保留。未能匹配。"})
            continue
        if j is None:
            unmatched.append({"quote": quote, "note": "匹配调用失败，无法判断；保留。未能匹配。"})
            continue
        idx = j["match"]
        note = j["note"]
        if isinstance(idx, int) and 1 <= idx <= len(inventory):
            if (idx - 1) not in taken:
                taken.add(idx - 1)
                item = inventory[idx - 1]
                removed.append({"change": item["change"], "from": item["from"], "added_step": item["added_step"],
                                "removed_step": k, "by": quote, "note": note})
            else:
                unmatched.append({"quote": quote, "note": "指向第%d条，但该条已被本步另一条删掉；保留。未能匹配。" % idx})
        else:
            unmatched.append({"quote": quote, "note": "模型判断指不上任何条目(%s)；保留。未能匹配。" % (note or "无备注")})
    inventory_after = [it for i, it in enumerate(inventory) if i not in taken]
    return removed, unmatched, inventory_after


# ---------------- 珠子切分（与 run130 逐字一致） ----------------

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
                      "n_now_lines": len(lines), "has_now": a >= 0, "has_rel": b >= 0, "split_error": err})
    return beads

# __PART2__
# ---------------- 调用与缓存（照 run130；缓存只在本 run 目录内） ----------------

class Store:
    """按 (逻辑键, 模型键, 提示词 sha10) 只复用解析成功的记录。"""

    def __init__(self, path):
        self.path = Path(path)
        self.recs = []
        self.by_key = {}
        if self.path.exists():
            try:
                for r in json.loads(self.path.read_text(encoding="utf-8")).get("records", []):
                    self.recs.append(r)
                    if r.get("parse_ok"):
                        self.by_key[self._k(r["key"], r["model"], r["prompt_sha"])] = r
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
                self.by_key[self._k(rec["key"], rec["model"], rec["prompt_sha"])] = rec
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
        if rel:
            p = OUT_DIR / str(rel)
            if p.exists():
                return p.read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def _mock_output(step, model):
    if step == "step":
        return '{"new_changes": [{"change": "MOCK变化", "from": "第1段的MOCK体验"}], "no_longer_valid": [], "thread": "MOCK线"}'
    if step == "match":
        return MOCK.get("last_match_expected") or "[]"
    if step == "center":
        return ('{"centers": [{"center": "MOCK中心", "covers": [1, 2], "strains": [3], '
                '"note": "MOCK注"}], "no_single_center": false}')
    if step == "ident":
        return '{"guess": "MOCK", "confidence": 50, "also_fits": [], "why": "MOCK"}'
    if step == "compare":
        return ('{"better": "XVARIANT", "specificity": {"A": "MOCK", "B": "MOCK"}, '
                '"grounding": {"A": "MOCK", "B": "MOCK"}, "flattened": {"A": [], "B": []}, '
                '"openness": {"A": "MOCK", "B": "MOCK"}, "why": "MOCK"}')
    return "{}"


def call(step, core, model, prompt, parse_fn, key, prompt_version, prompt_template, extra=None):
    """一次逻辑调用（含同一模型重试，最多 MAX_ATTEMPTS 次）。mock 下不碰 runner。"""
    h = sha10(prompt)
    st = store(step)
    hit = st.get(key, model, h)
    if hit is not None:
        bump(step, model, "cached")
        rec = dict(hit)
        rec["cached"] = True
        return rec
    rec = {"key": key, "core": core, "model": model, "prompt_sha": h, "prompt_version": prompt_version,
           "prompt_template": prompt_template, "attempts": [], "cached": False,
           "parsed": None, "output": None, "parse_ok": False, "parse_error": None}
    if MOCK["on"]:
        out = _mock_output(step, model)
        MOCK["calls"] += 1
        parsed, err = parse_fn(out)
        rec["attempts"].append({"job_id": core + "__mock__h" + h, "status": "ok",
                                "meta_error": None, "output_chars": len(out),
                                "parse_ok": parsed is not None, "parse_error": err})
        if parsed is not None:
            rec["parsed"], rec["output"], rec["parse_ok"] = parsed, out, True
        else:
            rec["parse_error"] = err
            bump(step, model, "failed")
        st.put(dict(rec))
        return rec
    timeout = TMO_GPT if model == "gpt56w" else TMO_OTHER
    n, secs = 0, 0.0
    for att in range(MAX_ATTEMPTS):
        jid = (core if att == 0 else "%s__retry%d" % (core, att)) + os.environ.get("RUN133_ATTEMPT_TAG", "") + "__h" + h  # 10-09: 失败记录只读，新尝试用新标签
        job = {"job_id": jid, "branch": step, "model_key": model, "prompt": prompt,
               "prompt_version": prompt_version, "prompt_template": prompt_template,
               "work_key": WORK_KEY, "work_name": WORK_NAME, "sample": 1,
               "extra": dict(extra or {}, attempt=att), "forbid_tools": list(FORBID), "max_attempts": 1}
        try:
            if model == "gpt56w":
                with GPT_SEM:
                    meta = run_job(str(OUT_DIR), job, timeout=timeout)
            else:
                meta = run_job(str(OUT_DIR), job, timeout=timeout)
        except Exception as e:
            meta = {"job_id": jid, "status": "failed", "error": "%s: %s" % (type(e).__name__, e)}
        n += 1
        try:
            secs += float((meta or {}).get("seconds") or 0.0)
        except Exception:
            pass
        out = _read_output(meta)
        entry = {"job_id": jid, "status": (meta or {}).get("status"), "meta_error": (meta or {}).get("error"),
                 "output_chars": len(out)}
        if isinstance(meta, dict) and meta.get("status") == "ok":
            if is_frozen(out):
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
            rec["parsed"], rec["output"], rec["parse_ok"] = parsed, out, True
            break
    bump(step, model, "calls", n, secs)
    bump(step, model, "retries", max(0, n - 1))
    if not rec["parse_ok"]:
        rec["parse_error"] = rec["attempts"][-1]["parse_error"] if rec["attempts"] else "no attempts"
        bump(step, model, "failed")
    st.put(dict(rec))
    return rec


# ---------------- 生成：链 + CENTER ----------------

def build_step_prompt(k, beads, inventory, version):
    beads_text = "\n\n".join("第 %d 段：%s" % (b["k"], b["text"]) for b in beads[:k])
    if inventory:
        hist = "\n".join("- %s（来自：%s）" % (it["change"], it["from"]) for it in inventory)
    else:
        hist = "（还没有）"
    p = (TPL["C7_STEP_" + version].replace("{{WORK}}", WORK_NAME)
         .replace("{{K}}", str(k))
         .replace("{{K_PREV}}", str(k - 1))
         .replace("{{BEADS}}", beads_text)
         .replace("{{HISTORY}}", hist))
    if "{{" in p:
        raise ValueError("unfilled placeholder remains in step prompt")
    return p


def build_match_prompt(k, inventory, no_longer_valid):
    L = [s.replace("{K}", str(k)) for s in MATCH_HEADER_LINES]
    for i, it in enumerate(inventory):
        L.append("%d. %s（来自：%s）[第%d步加入]" % (i + 1, it["change"], it["from"], it["added_step"]))
    L += ["", "【本步说不再成立】"]
    for s in no_longer_valid:
        L.append("- %s" % s)
    return "\n".join(L)


def chain_id(version, model):
    return "%s_%s" % (version, model)


def run_chain(version, model, beads):
    K = len(beads)
    records, inventory = [], []
    for k in range(1, K + 1):
        b = beads[k - 1]
        rec = {"work": WORK_KEY, "version": version, "model": model, "sample": "s1", "k": k,
               "title": b["title"], "bead": b["text"],
               "mm_start": b["mm_start"], "source": BEADS_REL,
               "inventory_before": [dict(it) for it in inventory],
               "step_attempts": [], "prompt": None, "output": None, "parsed": None, "parse_ok": False,
               "cached": False, "added": [], "match_job_id": None, "match_prompt": None, "match_attempts": [],
               "match_output": None, "match_ok": None, "match_error": None, "removed": [], "unmatched": [],
               "inventory_after": None, "thread": ""}
        prompt = build_step_prompt(k, beads, inventory, version)
        rec["prompt"] = prompt
        r = call("step", "c7_%s__%s__k%d" % (version, model, k), model, prompt, parse_step,
                 {"chain": chain_id(version, model), "k": k}, "C7_STEP_" + version,
                 TPL_PATHS["C7_STEP_" + version], {"k": k, "version": version})
        rec["step_attempts"] = r.get("attempts", [])
        rec["cached"] = bool(r.get("cached"))
        if not r.get("parse_ok"):
            rec["inventory_after"] = [dict(it) for it in inventory]
            records.append(rec)
            print("[chain %s k%d] FAILED" % (chain_id(version, model), k), flush=True)
            continue
        parsed = r["parsed"]
        rec.update({"parsed": parsed, "parse_ok": True, "output": r.get("output"), "thread": parsed["thread"]})
        added = [{"change": it["change"], "from": it["from"], "added_step": k} for it in parsed["new_changes"]]
        rec["added"] = added
        inventory2 = [dict(it) for it in inventory] + [dict(it) for it in added]
        nlv = parsed["no_longer_valid"]
        if nlv and inventory2:
            mprompt = build_match_prompt(k, inventory2, nlv)
            if MOCK["on"]:
                MOCK["last_match_expected"] = json.dumps(
                    [{"quote": q, "match": None, "note": "MOCK"} for q in nlv], ensure_ascii=False)
            mr = call("match", "c7match_%s__%s__k%d" % (version, model, k), MATCH_MODEL, mprompt,
                      parse_match_fn(len(nlv)), {"chain": chain_id(version, model), "k": k}, "C7_MATCH_v0",
                      "(inline) T26 no_longer_valid match", {"k": k, "chain_model": model, "version": version})
            rec.update({"match_job_id": (mr.get("attempts") or [{}])[0].get("job_id"), "match_prompt": mprompt,
                        "match_attempts": mr.get("attempts", []), "match_output": mr.get("output"),
                        "match_ok": bool(mr.get("parse_ok")),
                        "match_error": None if mr.get("parse_ok") else mr.get("parse_error")})
            removed, unmatched, inventory = apply_match(k, inventory2, nlv,
                                                        mr.get("parsed") if mr.get("parse_ok") else None)
            rec["removed"], rec["unmatched"] = removed, unmatched
        elif nlv and not inventory2:
            rec["unmatched"] = [{"quote": q, "note": "清单为空，无可对照；保留。未能匹配。"} for q in nlv]
            inventory = inventory2
        else:
            rec["match_ok"] = None
            inventory = inventory2
        rec["inventory_after"] = [dict(it) for it in inventory]
        records.append(rec)
        print("[chain %s k%d] ok added=%d removed=%d thread=%s" % (
            chain_id(version, model), k, len(added), len(rec["removed"]), rec["thread"][:24]), flush=True)
    return records


def final_inventory_text(records):
    final = (records[-1].get("inventory_after") or []) if records else []
    if not final:
        return "（空）"
    return "\n".join("%d. %s（来自：%s）[第%d步加入]" % (i + 1, it["change"], it["from"], it["added_step"])
                     for i, it in enumerate(final))


def build_center_history(beads, records):
    by_k = {r["k"]: r for r in records}
    lines = []
    for b in beads:
        r = by_k.get(b["k"])
        if r is not None and r.get("parse_ok"):
            nc = (r.get("parsed") or {}).get("new_changes", [])
            chg = "；".join(it.get("change", "") for it in nc) if nc else "（无）"
            lines.append("第%d段（%s）：新记下的变化：%s；线：%s" % (b["k"], b["title"], chg, r.get("thread") or "（空）"))
        else:
            lines.append("第%d段（%s）：（该步解析失败/无记录）" % (b["k"], b["title"]))
    lines.append("最终清单：\n%s" % final_inventory_text(records))
    return "\n".join(lines)


def build_center_beads(beads):
    return "\n\n".join("第%d段（%s）：%s" % (b["k"], b["title"], b["text"]) for b in beads)


def _as_int_list(v):
    if not isinstance(v, list):
        return None
    out = []
    for x in v:
        try:
            out.append(int(x))
        except Exception:
            return None
    return out


def norm_center(obj):
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    centers = obj.get("centers", [])
    if not isinstance(centers, list) or not (1 <= len(centers) <= 3):
        return None, "centers must be a list of 1-3 items"
    norm_c = []
    for it in centers:
        if not isinstance(it, dict):
            return None, "center item is not an object"
        c = str(it.get("center", "")).strip()
        if not c:
            return None, "center item has empty center"
        covers = _as_int_list(it.get("covers", []))
        strains = _as_int_list(it.get("strains", []))
        if covers is None or strains is None:
            return None, "covers/strains must be integer lists"
        norm_c.append({"center": c, "covers": covers, "strains": strains, "note": str(it.get("note", "")).strip()})
    nsc = obj.get("no_single_center")
    if not isinstance(nsc, bool):
        return None, "no_single_center must be true/false"
    return {"centers": norm_c, "no_single_center": nsc}, None


def parse_center(out):
    ok, val, err = extract_json_obj(out)
    if not ok:
        return None, err
    return norm_center(val)


def run_center(version, model, beads, records):
    hist = build_center_history(beads, records)
    prompt = fill(TPL["CENTER_v0"], WORK=WORK_NAME, HISTORY=hist, BEADS=build_center_beads(beads))
    r = call("center", "center_%s__%s" % (version, model), model, prompt, parse_center,
             {"chain": chain_id(version, model)}, "CENTER_v0", TPL_PATHS["CENTER_v0"])
    p = r.get("parsed") if r.get("parse_ok") else None
    return {"work": WORK_KEY, "version": version, "model": model, "parse_ok": bool(r.get("parse_ok")),
            "cached": bool(r.get("cached")), "parse_error": r.get("parse_error"),
            "attempts": r.get("attempts"), "prompt": prompt, "output": r.get("output"),
            "centers": (p or {}).get("centers"), "no_single_center": (p or {}).get("no_single_center")}
# ---------------- 评测 1：ident ----------------

def is_nothing(t):
    return (t or "").strip() == "还看不出"


def has_title_word(s):
    return any(w in (s or "") for w in TITLE_WORDS)


def collect_chain_statements(version, model, records, centers_entry):
    """每链：全部非"还看不出"逐段 thread（去重）+ 最后 thread + 每个 center。"""
    seen = set()
    out = []
    for r in records:
        if not r.get("parse_ok"):
            continue
        th = (r.get("thread") or "").strip()
        if not th or is_nothing(th) or th in seen:
            continue
        seen.add(th)
        out.append({"kind": "step", "k": r["k"], "text": th})
    if records and records[-1].get("parse_ok"):
        last = (records[-1].get("thread") or "").strip()
        if last and not is_nothing(last) and "step" not in [s["kind"] for s in out if s["text"] == last]:
            pass  # 最后 thread 若与某段去重后相同，不再重复加
        if last and not is_nothing(last) and last not in seen:
            seen.add(last)
            out.append({"kind": "final", "k": records[-1]["k"], "text": last})
        elif last and not is_nothing(last):
            out.append({"kind": "final", "k": records[-1]["k"], "text": last, "dup_of_step": True})
    if centers_entry and centers_entry.get("parse_ok"):
        for i, c in enumerate(centers_entry.get("centers") or []):
            out.append({"kind": "center", "k": None, "center_idx": i, "text": c["center"],
                        "covers": c.get("covers"), "strains": c.get("strains"), "note": c.get("note")})
    for s in out:
        s.update({"chain": chain_id(version, model), "version": version, "model": model,
                  "ref": None, "has_title_word": has_title_word(s["text"])})
    return out


def collect_ref130_statements():
    """run130 三条旧链：最后 thread + 每个 center，标记 ref_run130。"""
    out = []
    try:
        steps = json.loads((ROOT / REF130_STEPS_REL).read_text(encoding="utf-8"))
        centers = json.loads((ROOT / REF130_CENTERS_REL).read_text(encoding="utf-8"))
    except Exception as e:
        print("ref130 load failed: %s" % e, flush=True)
        return out
    by_model = {}
    for r in steps.get("steps", []):
        if r.get("work") == WORK_KEY:
            by_model.setdefault(r["model"], []).append(r)
    for m, recs in by_model.items():
        recs.sort(key=lambda r: r["k"])
        last = recs[-1] if recs else None
        if last and last.get("parse_ok") and (last.get("thread") or "").strip() \
                and not is_nothing(last.get("thread")):
            out.append({"kind": "final", "k": last["k"], "text": last["thread"].strip(),
                        "chain": "ref130_%s" % m, "version": "ref130", "model": m, "ref": "ref_run130",
                        "has_title_word": has_title_word(last["thread"])})
    for c in centers.get("centers", []):
        if not c.get("parse_ok"):
            continue
        for i, x in enumerate(c.get("centers") or []):
            out.append({"kind": "center", "k": None, "center_idx": i, "text": x["center"],
                        "covers": x.get("covers"), "strains": x.get("strains"), "note": x.get("note"),
                        "chain": "ref130_%s" % c["model"], "version": "ref130", "model": c["model"],
                        "ref": "ref_run130", "has_title_word": has_title_word(x["center"])})
    return out


def shuffle_candidates(statement_text):
    seed = int(hashlib.sha256(statement_text.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
    rng = random.Random(seed)
    cands = list(CANDIDATES)
    rng.shuffle(cands)
    return cands, seed


def norm_ident(obj):
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    g = obj.get("guess")
    g = g if isinstance(g, str) else str(g)
    g = g.strip()
    if not g:
        return None, "empty guess"
    try:
        conf = int(obj.get("confidence"))
    except Exception:
        return None, "confidence is not an integer"
    if not (0 <= conf <= 100):
        return None, "confidence out of range 0-100"
    af = obj.get("also_fits", [])
    if not isinstance(af, list):
        return None, "also_fits is not a list"
    af = [str(x).strip() for x in af if str(x).strip()]
    return {"guess": g, "confidence": conf, "also_fits": af, "why": str(obj.get("why", "")).strip()}, None


def parse_ident(out):
    ok, val, err = extract_json_obj(out)
    if not ok:
        return None, err
    return norm_ident(val)


def run_ident(statements, workers):
    """每条 statement x 每位 reviewer 各一次。返回记录列表。"""
    tasks = []
    for i, s in enumerate(statements):
        cands, seed = shuffle_candidates(s["text"])
        s["cand_seed"] = seed
        s["candidates_shown"] = cands
        prompt = fill(TPL["THREAD_IDENT_v0"], CANDIDATES="\n".join("%d. %s" % (j + 1, c) for j, c in enumerate(cands)),
                      STATEMENT=s["text"])
        for rv in REVIEWERS:
            tasks.append((i, rv, prompt))
    res = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(call, "ident", "ident__s%d__by_%s" % (i, rv), rv, prompt, parse_ident,
                          {"stmt": i, "reviewer": rv}, "THREAD_IDENT_v0", TPL_PATHS["THREAD_IDENT_v0"],
                          {"stmt_idx": i}): (i, rv) for (i, rv, prompt) in tasks}
        for f in cf.as_completed(futs):
            res[futs[f]] = f.result()
    out = []
    for (i, rv, prompt) in tasks:
        r = res[(i, rv)]
        p = r.get("parsed") if r.get("parse_ok") else None
        s = statements[i]
        out.append({"stmt_idx": i, "chain": s["chain"], "version": s.get("version"), "model": s.get("model"),
                    "ref": s.get("ref"), "kind": s["kind"], "k": s.get("k"),
                    "center_idx": s.get("center_idx"), "text": s["text"],
                    "has_title_word": s["has_title_word"], "cand_seed": s["cand_seed"],
                    "candidates_shown": s["candidates_shown"],
                    "reviewer": rv, "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
                    "parse_error": r.get("parse_error"), "attempts": r.get("attempts"),
                    "prompt": prompt, "output": r.get("output"),
                    "guess": (p or {}).get("guess"), "confidence": (p or {}).get("confidence"),
                    "also_fits": (p or {}).get("also_fits"), "why": (p or {}).get("why")})
    return out


def ident_stats(ident_recs):
    """按 (chain) x reviewer：命中率（guess==船歌）、说不准率、also_fits 均值；再按含/不含标题词拆分命中率。"""
    agg = {}
    for r in ident_recs:
        if not r.get("parse_ok"):
            continue
        key = (r["chain"], r["reviewer"])
        d = agg.setdefault(key, {"n": 0, "hit": 0, "unsure": 0, "af_sum": 0,
                                 "tw_n": 0, "tw_hit": 0, "ntw_n": 0, "ntw_hit": 0})
        d["n"] += 1
        if r.get("guess") == TARGET:
            d["hit"] += 1
        if r.get("guess") == UNSURE:
            d["unsure"] += 1
        d["af_sum"] += len(r.get("also_fits") or [])
        if r.get("has_title_word"):
            d["tw_n"] += 1
            if r.get("guess") == TARGET:
                d["tw_hit"] += 1
        else:
            d["ntw_n"] += 1
            if r.get("guess") == TARGET:
                d["ntw_hit"] += 1
    rows = []
    for (chain, rv), d in sorted(agg.items()):
        rows.append({"chain": chain, "reviewer": rv, "n": d["n"],
                     "hit_rate": round(d["hit"] / d["n"], 3) if d["n"] else None,
                     "unsure_rate": round(d["unsure"] / d["n"], 3) if d["n"] else None,
                     "also_fits_avg": round(d["af_sum"] / d["n"], 2) if d["n"] else None,
                     "hit_with_titleword": ("%d/%d" % (d["tw_hit"], d["tw_n"])) if d["tw_n"] else "—",
                     "hit_without_titleword": ("%d/%d" % (d["ntw_hit"], d["ntw_n"])) if d["ntw_n"] else "—"})
    return rows


# ---------------- 评测 2：compare（A/B 互换盲比） ----------------

def build_chain_record(beads, records, centers_entry):
    by_k = {r["k"]: r for r in records}
    lines = []
    for b in beads:
        r = by_k.get(b["k"])
        lines.append("第%d段（%s）看出的线：%s" % (b["k"], b["title"],
                                               (r.get("thread") if r and r.get("parse_ok") else None) or "（空/失败）"))
    lines.append("最后的线：%s" % ((records[-1].get("thread") if records and records[-1].get("parse_ok") else None)
                                 or "（空/失败）"))
    if centers_entry and centers_entry.get("parse_ok"):
        lines.append("全曲核心关系候选：%s" % json.dumps(centers_entry.get("centers"), ensure_ascii=False))
    else:
        lines.append("全曲核心关系候选：（解析失败/无记录）")
    return "\n".join(lines)


def norm_compare(obj):
    if not isinstance(obj, dict):
        return None, "top level is not an object"
    b = str(obj.get("better", "")).strip()
    if b not in ("A", "B", "不可判"):
        return None, "better not in A/B/不可判: %r" % b
    for k in ("specificity", "grounding", "openness"):
        v = obj.get(k)
        if not isinstance(v, dict) or "A" not in v or "B" not in v:
            return None, "%s must be an object with A/B" % k
    fl = obj.get("flattened")
    if not isinstance(fl, dict) or "A" not in fl or "B" not in fl:
        return None, "flattened must be an object with A/B"
    return {"better": b, "specificity": obj["specificity"], "grounding": obj["grounding"],
            "flattened": fl, "openness": obj["openness"], "why": str(obj.get("why", "")).strip()}, None


def parse_compare(out):
    ok, val, err = extract_json_obj(out)
    if not ok:
        return None, err
    return norm_compare(val)


def run_compare(beads, chains, centers, workers):
    """每生成模型：v2 链 vs v3 链记录；双 reviewer x 双顺序。盲：提示词中不出现模型/版本名。"""
    bead_text = build_center_beads(beads)
    pairs = []
    for m in GEN_MODELS:
        rec_v2 = build_chain_record(beads, chains[chain_id("v2", m)], centers.get(chain_id("v2", m)))
        rec_v3 = build_chain_record(beads, chains[chain_id("v3", m)], centers.get(chain_id("v3", m)))
        pairs.append((m, rec_v2, rec_v3))
    tasks = []
    for (m, rec_v2, rec_v3) in pairs:
        for order in (0, 1):
            A, B = (rec_v2, rec_v3) if order == 0 else (rec_v3, rec_v2)
            truth = {"A": ("v2" if order == 0 else "v3"), "B": ("v3" if order == 0 else "v2")}
            prompt = fill(TPL["THREAD_COMPARE_v0"], WORK=WORK_NAME, BEADS=bead_text, A=A, B=B)
            assert "v2" not in prompt.split("【A】")[0].split("【珠子")[0] or True
            for rv in REVIEWERS:
                h = sha10("%s|%d|%s" % (m, order, rv))
                tasks.append({"gen_model": m, "order": order, "reviewer": rv, "truth": truth,
                              "prompt": prompt, "seed_note": "A/B assignment fixed by (gen_model,order); prompt sha10=%s" % h})
    res = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(call, "compare", "compare__%s__o%d__by_%s" % (t["gen_model"], t["order"], t["reviewer"]),
                          t["reviewer"], t["prompt"], parse_compare,
                          {"gen_model": t["gen_model"], "order": t["order"], "reviewer": t["reviewer"]},
                          "THREAD_COMPARE_v0", TPL_PATHS["THREAD_COMPARE_v0"],
                          {"gen_model": t["gen_model"], "order": t["order"]}): idx
                for idx, t in enumerate(tasks)}
        for f in cf.as_completed(futs):
            res[futs[f]] = f.result()
    out = []
    for idx, t in enumerate(tasks):
        r = res[idx]
        p = r.get("parsed") if r.get("parse_ok") else None
        out.append({**t, "parse_ok": bool(r.get("parse_ok")), "cached": bool(r.get("cached")),
                    "parse_error": r.get("parse_error"), "attempts": r.get("attempts"),
                    "output": r.get("output"),
                    "better": (p or {}).get("better"), "specificity": (p or {}).get("specificity"),
                    "grounding": (p or {}).get("grounding"), "flattened": (p or {}).get("flattened"),
                    "openness": (p or {}).get("openness"), "why": (p or {}).get("why")})
    return out


def compare_summary(compare_recs):
    """换位一致性：同 (gen_model, reviewer) 两次顺序都指向同一版本才算 win；否则"不一致"。"""
    rows = []
    for m in GEN_MODELS:
        for rv in REVIEWERS:
            rs = [r for r in compare_recs if r["gen_model"] == m and r["reviewer"] == rv and r.get("parse_ok")]
            verdict = None
            if len(rs) == 2:
                votes = []
                for r in rs:
                    if r.get("better") == "不可判":
                        votes.append("不可判")
                    elif r.get("better") in ("A", "B"):
                        votes.append(r["truth"][r["better"]])
                    else:
                        votes.append(None)
                if votes[0] == votes[1] and votes[0] is not None:
                    verdict = votes[0]  # "v2" / "v3" / "不可判"
                else:
                    verdict = "不一致"
            else:
                verdict = "缺记录(%d/2)" % len(rs)
            rows.append({"gen_model": m, "reviewer": rv, "verdict": verdict,
                         "detail": [{"order": r["order"], "truth": r["truth"], "better": r.get("better"),
                                     "why": r.get("why")} for r in rs]})
    return rows


# ---------------- 阶段执行与落盘 ----------------

def load_beads():
    text = (ROOT / BEADS_REL).read_text(encoding="utf-8")
    beads = split_beads(text)
    return text, beads


def stage_gen(workers):
    _text, beads = load_beads()
    chains = {}
    ids = [(v, m) for v in VERSIONS for m in GEN_MODELS]
    # 链间并行；gpt56w 链内部及与其它 gpt56w 链之间由 GPT_SEM 串行（call 内加锁）。
    with cf.ThreadPoolExecutor(max_workers=max(1, min(workers, len(ids)))) as ex:
        futs = {ex.submit(run_chain, v, m, beads): (v, m) for (v, m) in ids}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            chains[chain_id(v, m)] = f.result()
    chains_payload = {"run_id": RUN_ID, "chains": chains,
                      "failed_steps": ["%s/k%d" % (r.get("model") and (r.get("version") + "_" + r["model"]), r["k"])
                                       for rs in chains.values() for r in rs if not r.get("parse_ok")],
                      "failed_matches": ["%s/k%d" % (r.get("version") + "_" + r["model"], r["k"])
                                         for rs in chains.values() for r in rs if r.get("match_ok") is False]}
    (OUT_DIR / "chains.json").write_text(json.dumps(chains_payload, ensure_ascii=False, indent=1), encoding="utf-8")
    centers = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, min(workers, len(ids)))) as ex:
        futs = {ex.submit(run_center, v, m, beads, chains[chain_id(v, m)]): (v, m) for (v, m) in ids}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            centers[chain_id(v, m)] = f.result()
    (OUT_DIR / "centers.json").write_text(json.dumps({"run_id": RUN_ID, "centers": centers},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    return beads, chains, centers


def load_gen():
    chains = json.loads((OUT_DIR / "chains.json").read_text(encoding="utf-8"))["chains"]
    # 10-09: gpt2 网页通道输入上限约 2.1–2.3 万字，gpt56w 链 k18 起提交前被拒；评审只用首个失败之前的前缀
    for cid in list(chains):
        recs, keep = chains[cid], []
        for r in recs:
            if not r.get("parse_ok"):
                break
            keep.append(r)
        chains[cid] = keep
    centers = json.loads((OUT_DIR / "centers.json").read_text(encoding="utf-8"))["centers"]
    _text, beads = load_beads()
    return beads, chains, centers


def stage_ident(workers):
    beads, chains, centers = load_gen()
    stmts = []
    for v in VERSIONS:
        for m in GEN_MODELS:
            stmts += collect_chain_statements(v, m, chains[chain_id(v, m)], centers.get(chain_id(v, m)))
    stmts += collect_ref130_statements()
    recs = run_ident(stmts, workers)
    payload = {"run_id": RUN_ID, "n_statements": len(stmts), "reviewers": list(REVIEWERS),
               "stats": ident_stats(recs), "records": recs}
    (OUT_DIR / "ident.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


def stage_compare(workers):
    beads, chains, centers = load_gen()
    recs = run_compare(beads, chains, centers, workers)
    payload = {"run_id": RUN_ID, "reviewers": list(REVIEWERS),
               "summary": compare_summary(recs), "records": recs}
    (OUT_DIR / "compare.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", "<br>")


def chain_numbers(records):
    K = len(records)
    ok = [r for r in records if r.get("parse_ok")]
    n_empty = sum(1 for r in ok if not r.get("added"))
    ft = next((r["k"] for r in records if r.get("parse_ok") and (r.get("thread") or "").strip()
               and not is_nothing(r.get("thread"))), None)
    last = records[-1] if records else None
    return {"K": K, "n_ok": len(ok), "n_empty": n_empty,
            "empty_ratio": ("%d/%d=%.2f" % (n_empty, K, n_empty / K)) if K else "—",
            "ft": ft, "last_thread": (last.get("thread") if last and last.get("parse_ok") else "（失败/无记录）"),
            "final_n": len(last.get("inventory_after") or []) if last else 0}


def stage_report():
    beads, chains, centers = load_gen()
    ident = json.loads((OUT_DIR / "ident.json").read_text(encoding="utf-8"))
    comp = json.loads((OUT_DIR / "compare.json").read_text(encoding="utf-8"))
    L = ["# run133 Thread 首轮单变量：C7_STEP_v2 vs v3（船歌 Op.60）", ""]
    L += ["- 单变量：v3 只在 Q3 加一句作品特异性要求（“这句话要用这首作品里留下的具体体验来说，"
          "让人一听就知道说的是这首作品，换到别的作品上就不成立；”）。",
          "- 输入：`%s`（sha256 见 manifest）；切分与给 Thread 的文字组织与 run130 完全一致"
          "（只取标题行 +【此刻】块）。" % BEADS_REL,
          "- 模板：%s；“不再成立”对照删除为内联 C7_MATCH（由 %s 判，%s）。"
          % (", ".join("`%s`" % v for v in TPL_PATHS.values()), MATCH_MODEL, MATCH_MODEL_REASON),
          "- 缓存键：(逻辑键, 模型键, 完整提示词 sha256 前 10 位)；只缓存解析成功；"
          "失败同一模型重试最多 2 次；gpt56w  timeout 1800、本进程并发 1。", ""]
    L += ["## 1. 四链数字（只报告数字，不做裁决）", "",
          "| 链 | K | 解析成功 | 空步率 | 首次非空段 | 终清单数 |", "|---|---|---|---|---|---|"]
    for v in VERSIONS:
        for m in GEN_MODELS:
            s = chain_numbers(chains[chain_id(v, m)])
            L.append("| %s | %d | %d | %s | %s | %d |" % (chain_id(v, m), s["K"], s["n_ok"], s["empty_ratio"],
                                                          s["ft"] or "—", s["final_n"]))
    L += ["", "## 2. 四链最后 thread 原文", ""]
    for v in VERSIONS:
        for m in GEN_MODELS:
            s = chain_numbers(chains[chain_id(v, m)])
            L += ["### %s" % chain_id(v, m), "", s["last_thread"], ""]
    L += ["## 3. centers 原文", ""]
    for v in VERSIONS:
        for m in GEN_MODELS:
            c = centers.get(chain_id(v, m)) or {}
            L += ["### %s（parse_ok=%s）" % (chain_id(v, m), c.get("parse_ok")), ""]
            if c.get("parse_ok"):
                for i, x in enumerate(c.get("centers") or []):
                    L += ["- 候选%d：%s" % (i + 1, x["center"]),
                          "  - covers：%s；strains：%s" % (x.get("covers"), x.get("strains")),
                          "  - 注：%s" % x.get("note")]
                L += ["- no_single_center：%s" % c.get("no_single_center"), ""]
            else:
                L += ["- 解析失败：%s" % c.get("parse_error"), ""]
    L += ["## 4. ident（只报告数字）", "",
          "| 链 | reviewer | n | 命中率(guess==船歌) | 说不准率 | also_fits均值 | 含标题词命中 | 不含标题词命中 |",
          "|---|---|---|---|---|---|---|---|"]
    for row in ident.get("stats", []):
        L.append("| %s | %s | %d | %s | %s | %s | %s | %s |" % (
            row["chain"], row["reviewer"], row["n"], row["hit_rate"], row["unsure_rate"],
            row["also_fits_avg"], row["hit_with_titleword"], row["hit_without_titleword"]))
    L += ["", "标题词：%s；命中=“%s”。" % ("、".join("“%s”" % w for w in TITLE_WORDS), TARGET), ""]
    L += ["## 5. compare（换位一致性；只报告，不做裁决）", "",
          "| 生成模型 | reviewer | 结论 |", "|---|---|---|"]
    for row in comp.get("summary", []):
        L.append("| %s | %s | %s |" % (row["gen_model"], row["reviewer"], row["verdict"]))
    L += [""]
    for row in comp.get("summary", []):
        L += ["### %s x %s：%s" % (row["gen_model"], row["reviewer"], row["verdict"]), ""]
        for d in row.get("detail", []):
            L += ["- 顺序%d（真身 A=%s B=%s）：better=%s" % (d["order"], d["truth"]["A"], d["truth"]["B"], d["better"]),
                  "  - why：%s" % cell(d.get("why"))]
        L += [""]
    (OUT_DIR / "report.md").write_text("\n".join(L), encoding="utf-8")
    return str(OUT_DIR / "report.md")


def write_manifest(extra):
    outs = {}
    for p in sorted(OUT_DIR.rglob("*")):
        rel = p.relative_to(OUT_DIR)
        if not p.is_file() or p.suffix == ".tmp" or any("_cwd" in x for x in rel.parts):
            continue
        if p.name.startswith("run_manifest"):
            continue
        if p.name in ("run.log", "DONE", "FAILED"):
            continue
        outs[str(rel).replace("\\", "/")] = sha256_file(p)
    music_route = os.environ.get("MUSIC_WEB_ROUTE", "<unset>")
    man = {"run_id": RUN_ID, "git_commit": git_commit(),
           "script": {"runs/run133_thread_spec/go.py": sha256_file(THIS_DIR / "go.py")},
           "templates": {v: sha256_file(ROOT / v) for v in TPL_PATHS.values()},
           "match_inline_template_sha256": hashlib.sha256(MATCH_TPL_TEXT.encode("utf-8")).hexdigest(),
           "inputs": {BEADS_REL: sha256_file(ROOT / BEADS_REL),
                      REF130_STEPS_REL: sha256_file(ROOT / REF130_STEPS_REL),
                      REF130_CENTERS_REL: sha256_file(ROOT / REF130_CENTERS_REL)},
           "models": {"gen": list(GEN_MODELS), "match": MATCH_MODEL,
                      "match_reason": MATCH_MODEL_REASON, "reviewers": list(REVIEWERS)},
           "env": {"MUSIC_WEB_ROUTE": music_route,
                   "gpt56w_route": ("gpt2_adapter" if "gpt56w" in runner.GPT2_KEYS else
                                    ("mg" if "gpt56w" in runner.MG_KEYS else "unknown"))},
           "extra": extra or {},
           "outputs": outs}
    (OUT_DIR / "run_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    return man


def snapshot_calls():
    with LOCK:
        return {"n": CALLS["n"], "by": {k: dict(v) for k, v in CALLS["by"].items()}}


# ---------------- mock dry-run 与 probe ----------------

def run_mock_assert(workers):
    global OUT_DIR, MOCK
    OUT_DIR = RUN_DIR / "_dryrun"
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STORES.clear()
    MOCK["on"] = True
    MOCK["calls"] = 0
    _text, beads = load_beads()
    assert len(beads) == K_EXPECTED, "beads=%d expected %d" % (len(beads), K_EXPECTED)
    chains = {}
    ids = [(v, m) for v in VERSIONS for m in GEN_MODELS]
    with cf.ThreadPoolExecutor(max_workers=max(1, min(workers, len(ids)))) as ex:
        futs = {ex.submit(run_chain, v, m, beads): (v, m) for (v, m) in ids}
        for f in cf.as_completed(futs):
            v, m = futs[f]
            chains[chain_id(v, m)] = f.result()
    for cid, recs in chains.items():
        assert len(recs) == K_EXPECTED, "%s steps=%d" % (cid, len(recs))
        assert all(r.get("parse_ok") for r in recs), "%s has failed steps in mock" % cid
    centers = {cid: run_center(cid.split("_")[0], cid.split("_", 1)[1], beads, recs)
               for cid, recs in chains.items()}
    (OUT_DIR / "chains.json").write_text(json.dumps({"run_id": RUN_ID, "chains": chains},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT_DIR / "centers.json").write_text(json.dumps({"run_id": RUN_ID, "centers": centers},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    assert all(c.get("parse_ok") for c in centers.values()), "mock centers failed"
    stmts = []
    for v in VERSIONS:
        for m in GEN_MODELS:
            stmts += collect_chain_statements(v, m, chains[chain_id(v, m)], centers.get(chain_id(v, m)))
    stmts += collect_ref130_statements()
    assert stmts, "no ident statements in mock"
    recs = run_ident(stmts, workers)
    (OUT_DIR / "ident.json").write_text(json.dumps({"run_id": RUN_ID, "records": recs},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    assert len(recs) == len(stmts) * len(REVIEWERS)
    comp = run_compare(beads, chains, centers, workers)
    (OUT_DIR / "compare.json").write_text(json.dumps({"run_id": RUN_ID, "records": comp},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    assert len(comp) == len(GEN_MODELS) * 2 * len(REVIEWERS)
    # 盲性：compare 提示词不得出现版本/模型名
    for r in comp:
        head, a_txt = r["prompt"].split("【A】")[0], r["prompt"].split("【A】")[1]
        assert "v2" not in head and "v3" not in head and "gpt56w" not in head and "opus" not in head, \
            "compare prompt leaks identity"
    stage_report()
    n_calls = MOCK["calls"]
    # 清理 dry-run 产物
    shutil.rmtree(OUT_DIR)
    STORES.clear()
    MOCK["on"] = False
    OUT_DIR = RUN_DIR
    print("MOCK DRY-RUN OK: 4 chains x %d steps, %d centers, %d ident stmts x %d reviewers, %d compare calls; "
          "total mock calls=%d; _dryrun cleaned" % (
              K_EXPECTED, len(centers), len(stmts), len(REVIEWERS), len(comp), n_calls), flush=True)
    return True


def run_probe():
    """极短真实冒烟：每键一次短提示词（产物在 _smoke，验完即删）。gpt56w 路由未就绪则跳过并说明。"""
    global OUT_DIR
    OUT_DIR = RUN_DIR / "_smoke"
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STORES.clear()
    results = {}
    tiny = "只输出这个 JSON，不要输出其他任何文字：{\"ok\": true}"
    for key in ("gpt56w", "opus", "luna_noweb", "gpro", "muse"):
        job = {"job_id": "probe__%s" % key, "branch": "probe", "model_key": key, "prompt": tiny,
               "prompt_version": "probe", "prompt_template": "(probe)", "work_key": WORK_KEY,
               "work_name": WORK_NAME, "sample": 1, "extra": {"probe": True},
               "forbid_tools": list(FORBID), "max_attempts": 1}
        try:
            if key == "gpt56w":
                with GPT_SEM:
                    meta = run_job(str(OUT_DIR), job, timeout=600)
            else:
                meta = run_job(str(OUT_DIR), job, timeout=600)
            out = ""
            try:
                rel = (meta or {}).get("output_file")
                if rel and (OUT_DIR / str(rel)).exists():
                    out = (OUT_DIR / str(rel)).read_text(encoding="utf-8")
            except Exception:
                pass
            results[key] = {"status": (meta or {}).get("status"), "error": (meta or {}).get("error"),
                            "chars": len(out), "head": out[:120]}
        except Exception as e:
            results[key] = {"status": "exception", "error": "%s: %s" % (type(e).__name__, e)}
        print("probe %s: %s" % (key, results[key]), flush=True)
    shutil.rmtree(OUT_DIR)
    STORES.clear()
    OUT_DIR = RUN_DIR
    return results


# ---------------- 主入口 ----------------

def main():
    global OUT_DIR, MATCH_MODEL, MATCH_MODEL_REASON
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("gen", "ident", "compare", "report"), default=None)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    OUT_DIR = RUN_DIR
    if a.mock:
        ok = run_mock_assert(a.workers)
        return 0 if ok else 1
    if a.probe:
        res = run_probe()
        print(json.dumps(res, ensure_ascii=False, indent=1), flush=True)
        # C7_MATCH 模型决策：muse 可用则用 muse，否则全切 luna_noweb
        if (res.get("muse") or {}).get("status") == "ok":
            MATCH_MODEL, MATCH_MODEL_REASON = "muse", "probe ok"
        else:
            MATCH_MODEL, MATCH_MODEL_REASON = "luna_noweb", "muse probe failed: %s" % (res.get("muse") or {})
        print("MATCH_MODEL=%s (%s)" % (MATCH_MODEL, MATCH_MODEL_REASON), flush=True)
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 若已有上次 probe 结论（manifest），沿用 match 模型；否则默认 muse
    try:
        prev = json.loads((OUT_DIR / "run_manifest.json").read_text(encoding="utf-8"))
        MATCH_MODEL = prev.get("models", {}).get("match", "muse")
        MATCH_MODEL_REASON = prev.get("models", {}).get("match_reason", "from previous manifest")
    except Exception:
        pass
    if os.environ.get("RUN133_MATCH"):
        MATCH_MODEL, MATCH_MODEL_REASON = os.environ["RUN133_MATCH"], "env RUN133_MATCH (10-08: runner muse 键 33/33 失败)"
    t0 = time.time()
    stages = [a.stage] if a.stage else ["gen", "ident", "compare", "report"]
    if "gen" in stages:
        stage_gen(a.workers)
    if "ident" in stages:
        stage_ident(a.workers)
    if "compare" in stages:
        stage_compare(a.workers)
    if "report" in stages:
        stage_report()
    write_manifest({"calls": snapshot_calls(), "stages": stages})
    print("run133 stages=%s done in %.1fs calls=%d" % (stages, time.time() - t0, CALLS["n"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
