"""10-29 (user: "当前版本的最后的zip包呢"): zip this round (PLAN_20261026, 10-26 → now) in package 3's layout:
00_先读我 / 01_过程总览 / 02_起点与原始聊天 / 03_最终产物 / 04_项目快照 / 05_归档校验. Run dirs of the round without .bin;
user messages pulled from the session transcript (system and task notifications dropped).
usage: python pack_round.py -> C:/Users/zuoyi/Downloads/Thread_包4_<date>.zip"""
import csv, glob, hashlib, io, json, os, re, time, zipfile
from pathlib import Path
import evo

ROOT = evo.ROOT
T0 = time.mktime((2026, 10, 26, 0, 0, 0, 0, 0, -1))
TS0 = "2026-10-26"
NAME = f"Thread_包{os.environ.get('PACK_N', '4')}_{time.strftime('%Y%m%d')}"
LIGHT = os.environ.get("PACK_LIGHT") == "1"          # phone upload limit 30 MiB: no run dirs (the index csv stays)
OUT = Path("C:/Users/zuoyi/Downloads") / f"{NAME}{'_轻量版' if LIGHT else ''}.zip"
SESSION = Path("C:/Users/zuoyi/.claude/projects/D--musicclaude/7c623294-a1ea-40eb-b513-ae6588ad2c39.jsonl")
CODE = ["evo.py", "gpt3_call.py", "mg_call.py", "node2b.py", "draft10.py", "draft21.py", "draft22.py", "draft23.py", "covjudge.py", "local_check.py",
        "pool4.py", "tlabel.py", "frame.py", "synth.py", "synth3.py", "fill3.py", "finalize3.py", "recheck_p3a.py", "mech_check.py", "precise.py",
        "repair_line.py", "split_judge.py", "calib_mg.py", "seq_repair.py", "graph_split.py", "final_eval.py", "center_fix.py", "join.py", "join11.py",
        "beadgraph2.py", "beadview.py", "deliver_halfdone.py", "deliver_p8p9.py", "deliver_final.py", "graph7.py", "tgraph4.py", "stateinc.py",
        "watchdog.py", "pack_round.py", "gate_review.py", "PLAN_20261029.md", "THREAD_SPEC.md", "PLAN_20261026.md", "PLAN_解释池_20261023.md"]
EVAL = ["seq8", "split", "repair", "precise", "precise_bridge", "mech", "graph7", "beadgraph", "pool/P26", "pool/P27", "pool/P27t", "pool/P28"]


def user_messages():
    out = []
    for line in open(SESSION, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "user" or (d.get("timestamp") or "") < TS0:
            continue
        c = d.get("message", {}).get("content")
        texts = [c] if isinstance(c, str) else [x.get("text", "") for x in c or [] if isinstance(x, dict) and x.get("type") == "text"]
        for t in texts:
            t = (t or "").strip()
            if not t or t.startswith(("<system-reminder>", "<task-notification>", "<local-command", "<command-", "Caveat:", "This session is being continued")) \
                    or "SYSTEM NOTIFICATION" in t[:200]:
                continue
            t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S).strip()
            if t:
                out.append(f"[{d['timestamp'][:19]}Z]\n{t}\n")
    return out


def session_since():
    return "".join(line for line in open(SESSION, encoding="utf-8", errors="replace")
                   if (json.loads(line).get("timestamp") or "9") >= TS0) if SESSION.exists() else ""


def run_index(dirs):
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["run_id", "阶段", "线路", "模型", "开始", "秒", "成功", "输入字数", "回答字数", "失败记录数"])
    for d in sorted(dirs):
        p = Path(d); meta = {}; log = {}
        try:
            meta = json.loads((p / "meta.json").read_text(encoding="utf-8"))
        except Exception:
            pass
        try:
            log = json.loads((p / "call.log").read_text(encoding="utf-8"))
        except Exception:
            pass
        inp = (p / "input.txt").read_text(encoding="utf-8", errors="replace") if (p / "input.txt").exists() else ""
        outp = (p / "output.txt").read_text(encoding="utf-8", errors="replace") if (p / "output.txt").exists() else ""
        w.writerow([p.name, meta.get("stage", ""), log.get("route", log.get("account", "")), log.get("model", ""), log.get("started", ""),
                    log.get("seconds", ""), "是" if (p / "output.txt").exists() else "否", len(inp), len(outp), len(list(p.glob("call_fail_*")))])
    return buf.getvalue()


def main():
    dirs = [d for d in glob.glob(str(ROOT / "runs" / "*")) if os.path.isdir(d) and os.path.getmtime(d) >= T0]
    files = {}                                             # arcname -> bytes or Path

    def add(arc, src):
        files[f"{NAME}/{arc}"] = src
    add("00_先读我.md", ROOT / "deliver_20261028" / "包4_先读我.md")
    add("01_过程总览/01_逐步过程与结论（计划与记录）.md", ROOT / "PLAN_20261026.md")
    add("01_过程总览/02_原计划逐项落实情况.md", ROOT / "deliver_20261028" / "包4_原计划逐项落实情况.md")
    add("01_过程总览/03_模型调用索引.csv", ("\ufeff" + run_index(dirs)).encode("utf-8"))
    add("02_起点与原始聊天/01_用户原话_20261026起.txt", "\n".join(user_messages()).encode("utf-8"))
    add("02_起点与原始聊天/02_会话记录_20261026起.jsonl", session_since().encode("utf-8"))
    for f in ("成品_线与珠子关系图_Op60_Op61.md",):
        add(f"03_最终产物/{f}", ROOT / "deliver_20261028" / f)
    for f in glob.glob(str(ROOT / "evaluations" / "seq8" / "P8*_op6*.*")) + glob.glob(str(ROOT / "evaluations" / "seq8" / "center8_*.json")) \
            + glob.glob(str(ROOT / "evaluations" / "seq8" / "final_eval8_summary.md")) + glob.glob(str(ROOT / "evaluations" / "seq8" / "order_final8.json")):
        add(f"03_最终产物/线_JSON与终评/{Path(f).name}", Path(f))
    for f in glob.glob(str(ROOT / "deliverable" / "bead_graph" / "Op6*_珠子图*.md")):
        add(f"03_最终产物/珠子图/{Path(f).name}", Path(f))
    for f in glob.glob(str(ROOT / "deliver_20261028" / "*.md")):
        if "包4_" not in f and "成品_" not in f:
            add(f"03_最终产物/本轮中途交付（已被成品取代）/{Path(f).name}", Path(f))
    for f in glob.glob(str(ROOT / "reviews" / "*.md")):        # 10-29 user: the ChatGPT review conversation and every gate result go in each package
        add(f"02_起点与原始聊天/外部评审/{Path(f).name}", Path(f))
    for f in CODE:
        if (ROOT / f).exists():
            add(f"04_项目快照/代码与计划/{f}", ROOT / f)
    for e in EVAL:
        for f in glob.glob(str(ROOT / "evaluations" / e / "**" / "*"), recursive=True):
            if os.path.isfile(f):
                add(f"04_项目快照/evaluations/{Path(f).relative_to(ROOT / 'evaluations').as_posix()}", Path(f))
    for d in ([] if LIGHT else dirs):
        for root, _, fs in os.walk(d):
            for f in fs:
                if not f.endswith(".bin"):
                    p = Path(root) / f
                    add(f"04_项目快照/runs/{p.relative_to(ROOT / 'runs').as_posix()}", p)
    sums = []
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for arc, src in files.items():
            data = src if isinstance(src, bytes) else Path(src).read_bytes()
            z.writestr(arc, data); sums.append(f"{hashlib.sha256(data).hexdigest()}  {arc}")
        z.writestr(f"{NAME}/05_归档校验/sha256.txt", "\n".join(sums))
    print(OUT, len(files), "个文件，", round(OUT.stat().st_size / 1e6, 1), "MB；run 目录", len(dirs), flush=True)


if __name__ == "__main__":
    main()
