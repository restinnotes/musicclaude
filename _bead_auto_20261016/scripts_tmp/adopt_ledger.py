# -*- coding: utf-8 -*-
"""Adoption ledger: 3 rounds per (allowed model, route) for Op.60 A pool.
Historical picks resolved from inventory_A2.json; new picks from research_fill meta.
Run twice: once before fills complete (PENDING markers), once after."""
import json, os, hashlib, sys
sys.stdout.reconfigure(encoding="utf-8")

INV = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\inventory_A2.json", encoding="utf-8"))
ROOT = r"D:\musicclaude\music_work_since_1008v3_20261009"
FILL = r"D:\musicclaude\_bead_auto_20261016\research_fill"
OUT = r"D:\musicclaude\_bead_auto_20261016\out"

def sha_of(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def pick_hist(run, branch, mk, pv, sample):
    got = [r for r in INV if not r.get("orphan") and r.get("work") == "op60"
           and r.get("run") == run and r.get("branch") == branch and r.get("model_key") == mk
           and r.get("prompt_version") == pv and str(r.get("sample")) == str(sample) and r.get("status") == "ok"]
    assert len(got) == 1, f"pick_hist ambiguous/missing: {run} {branch} {mk} {pv} {sample} -> {len(got)}"
    return got[0]

# Creatures of the plan: group = (group_id, [hist picks], [fill picks])
GROUPS = [
 ("gflash-int", [("run05_saturation","A-int","gflash","A_int_v1","1"),
                 ("run05_saturation","A-int","gflash","A_int_v1","2"),
                 ("run05_saturation","A-int","gflash","A_int_v1","3")], []),
 ("gpro-int",   [("run08_final_models","A-int","gpro","A_int_v1","1"),
                 ("run08_final_models","A-int","gpro","A_int_v1","2"),
                 ("run44_gpro","A-int","gpro","A_int_v1","1")], []),
 ("muse-int",   [("run08_final_models","A-int","muse","A_int_v1","1"),
                 ("run08_final_models","A-int","muse","A_int_v1","2"),
                 ("run37_pool_novelty","A-int","muse","A_int_v1","3")], []),
 ("luna-int",   [("run08_final_models","A-int","luna_noweb","A_int_v1","1"),
                 ("run08_final_models","A-int","luna_noweb","A_int_v1","2")],
                 [("A-int__A_int_v1__luna__op60__f1")]),
 ("gpt56w-int", [("run106_gpt56_material","A-int","gpt56w","A_int_v1","1")],
                 [("A-int__A_int_v1__gpt56w__op60__f1"), ("A-int__A_int_v1__gpt56w__op60__f2")]),
 ("gpt6w-int",  [],
                 [("A-int__A_int_v1__gpt6w__op60__f1"), ("A-int__A_int_v1__gpt6w__op60__f2"), ("A-int__A_int_v1__gpt6w__op60__f3")]),
 ("gflash-web", [("run08_final_models","A-web","gflash_web","A_web_v2","1"),
                 ("run08_final_models","A-web","gflash_web","A_web_v2","2"),
                 ("run37_pool_novelty","A-web","gflash_web","A_web_v2","3")], []),
 ("gpro-web",   [("run08_final_models","A-web","gpro_web","A_web_v2","1"),
                 ("run08_final_models","A-web","gpro_web","A_web_v2","2"),
                 ("run44_gpro","A-web","gpro_web","A_web_v2","1")], []),
 ("muse-web",   [("run08_final_models","A-web","muse_web","A_web_v2","1"),
                 ("run08_final_models","A-web","muse_web","A_web_v2","2"),
                 ("run37_pool_novelty","A-web","muse_web","A_web_v2","3")], []),
 ("luna-web",   [("run05_saturation","A-web","luna","A_web_v2","1"),
                 ("run05_saturation","A-web","luna","A_web_v2","2"),
                 ("run05_saturation","A-web","luna","A_web_v2","3")], []),
 ("gpt56w-web", [("run106_gpt56_material","A-web","gpt56w","A_web_v2","1")],
                 [("A-web__A_web_v2__gpt56w__op60__f1"), ("A-web__A_web_v2__gpt56w__op60__f2")]),
 ("gpt6w-web",  [],
                 [("A-web__A_web_v2__gpt6w__op60__f1"), ("A-web__A_web_v2__gpt6w__op60__f2"), ("A-web__A_web_v2__gpt6w__op60__f3")]),
]

# allowed models / excluded families
ALLOWED = {"gflash","gpro","muse","luna","luna_noweb","gpt56w","gpt6w","gflash_web","gpro_web","muse_web"}
EXCLUDED_FAMILIES = ["grok","opus","sonnet","sol","sol61","gpt56_web"]

adopted = []
kept = []
for gid, hists, fills in GROUPS:
    rounds = []
    for (run, br, mk, pv, smp) in hists:
        r = pick_hist(run, br, mk, pv, smp)
        rounds.append({"kind": "historical", "run": run, "sample": smp})
    n = 0
    for i, (run, br, mk, pv, smp) in enumerate(hists):
        r = pick_hist(run, br, mk, pv, smp)
        n += 1
        outp = r["out_path"]
        adopted.append({
            "src_id": f"SRC-{gid}-{n}", "group": gid, "kind": "historical",
            "run": run, "sample": smp, "round_in_group": n,
            "branch": r["branch"], "channel": "int" if gid.endswith("-int") else "web",
            "model_key": r["model_key"], "model_name": r["model_name"],
            "prompt_version": r["prompt_version"],
            "path": outp, "path_rel": os.path.relpath(outp, r"D:\musicclaude"),
            "sha256": sha_of(outp), "chars": r["real_chars"],
            "started": r.get("started"), "seconds": r.get("seconds"),
            "meta_rel": os.path.relpath(r.get("meta") and os.path.join(ROOT, "runs", run, "meta", r["meta"]), r"D:\musicclaude") if r.get("meta") else None,
        })
    for fn in fills:
        n += 1
        mp = os.path.join(FILL, "meta", fn + ".json")
        op = os.path.join(FILL, "outputs", fn + ".md")
        if os.path.isfile(mp):
            m = json.load(open(mp, encoding="utf-8-sig"))
            adopted.append({
                "src_id": f"SRC-{gid}-{n}", "group": gid, "kind": "fill",
                "job_id": fn, "round_in_group": n, "branch": m.get("branch"),
                "channel": "int" if gid.endswith("-int") else "web",
                "model_key": m.get("model_key"), "model_name": m.get("model_cli") or m.get("harness"),
                "prompt_version": m.get("prompt_version"),
                "path": m.get("output_file") and os.path.join(FILL, m["output_file"]),
                "sha256": sha_of(op), "chars": m.get("output_chars"),
                "started": m.get("started"), "seconds": m.get("seconds"),
                "meta_rel": os.path.relpath(mp, r"D:\musicclaude"),
            })
        else:
            adopted.append({
                "src_id": f"SRC-{gid}-{n}", "group": gid, "kind": "fill",
                "job_id": fn, "round_in_group": n, "pending": True,
                "channel": "int" if gid.endswith("-int") else "web",
                "path": op, "sha256": None, "chars": None,
            })

# kept-not-adopted: ok historical rounds in allowed families not in adopted set
adopted_keys = {(a.get("run"), a.get("branch"), a.get("model_key"), a.get("prompt_version"), str(a.get("sample"))) for a in adopted if a.get("run")}
for r in INV:
    if r.get("orphan") or r.get("work") != "op60" or r.get("status") != "ok" or not r.get("branch", "").startswith("A-"):
        continue
    br = r.get("branch")
    if not (br.startswith("A-int") or br.startswith("A-web") or br.startswith("A-orig")):
        continue
    mk = r.get("model_key") or ""
    if mk not in ALLOWED and not any(mk.startswith(e) for e in EXCLUDED_FAMILIES):
        continue
    key = (r.get("run"), br, mk, r.get("prompt_version"), str(r.get("sample")))
    if key in adopted_keys or mk not in ALLOWED:
        continue
    if br.startswith("A-orig"):
        kind = "V2A基线参照"
    else:
        kind = "kept-archive"
    kept.append({
        "group_role": kind, "run": r.get("run"), "branch": br,
        "model_key": mk, "model_name": r.get("model_name"),
        "prompt_version": r.get("prompt_version"), "sample": r.get("sample"),
        "chars": r.get("real_chars"), "started": r.get("started"),
        "path_rel": os.path.relpath(r["out_path"], r"D:\musicclaude") if r.get("out_path") else None,
        "sha256": r.get("sha"),
    })

kept.sort(key=lambda x: (x["group_role"], str(x["model_key"]), str(x["sample"])))
json.dump({"adopted": adopted, "kept_and_exclude": kept}, open(os.path.join(OUT, "A36_LEDGER.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

pending = [a for a in adopted if a.get("pending")]
hdr = [
 "# A36 采用台账（Op.60 固定分段 A Pool / 2026-10-16）",
 "",
 "采用规则：每 (允许模型, 研究路线) 恰好 3 份成功且来源可核实的独立轮次；同一输出副本按 sha 去重不算新轮；",
 "同一家族不同版本不互相顶替（gflash36/37 各自存档不计入 gflash 三轮）；V2A 基线单独保留为质量参照，不入 Pool、不混算轮次；",
 "允许模型本轮 = Gemini(3.8-flash/3.1-pro)、Muse、Luna(gpt-6-luna)、GPT-w(gpt-5.6 与 gpt-6 分别标注)；排除：Grok、Opus、Sonnet、旧 Sol。",
 "",
 "## 一、采用 36 份",
 "",
 "| SRC | 组 | 类型 | run/任务 | 模型名 | prompt版 | 轮 | 字符 | 路径 | sha256(前12) |",
 "|---|---|---|---|---|---|---|---|---|---|",
]
for a in adopted:
    hdr.append("| {src_id} | {group} | {kind} | {runjob} | {mn} | {pv} | #{r} | {ch} | {pth} | {sha} |".format(
        src_id=a["src_id"], group=a["group"], kind=a.get("kind"),
        runjob=(a.get("run","") + " s" + str(a.get("sample",""))) if a.get("run") else (a.get("job_id","") + (" (PENDING)" if a.get("pending") else "")),
        mn=a.get("model_name") or "", pv=a.get("prompt_version") or "", r=a.get("round_in_group"),
        ch=a.get("chars") if a.get("chars") is not None else "—",
        pth=a.get("path") and os.path.relpath(a["path"], r"D:\musicclaude") or "",
        sha=(a.get("sha256") or "")[:12]))
hdr += [
 "",
 "注：fill 名称 fN = 本轮补齐文件；gpt56w 组的 run106 s1 为第 1 轮，fill f1/f2 为第 2/3 轮（通道已在下表注明）。",
 "",
 "## 二、保留归档（未采用原件全部保留）",
 "",
 "| 角色 | run | 分支 | 模型 | prompt版 | s | 字符 | 路径 |",
 "|---|---|---|---|---|---|---|---|",
]
for k in kept:
    hdr.append("| {gr} | {run} | {br} | {mk} | {pv} | {s} | {ch} | {pth} |".format(
        gr=k["group_role"], run=k.get("run",""), br=k["branch"], mk=k.get("model_key") or "",
        pv=k.get("prompt_version") or "", s=k.get("sample"), ch=k.get("chars"),
        pth=k.get("path_rel") or ""))
hdr += [
 "",
 f"PENDING 补齐轮数：{len(pending)}（见下）",
]
for p in pending:
    hdr.append(f"- PENDING: {p['group']} {p['job_id']}")
open(os.path.join(OUT, "A36_LEDGER.md"), "w", encoding="utf-8").write("\n".join(hdr))
print(f"adopted={len(adopted)} pending={len(pending)} kept={len(kept)}")
print("written A36_LEDGER.json / .md")
