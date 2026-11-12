"""run135：新目录四项短/长输入配对健康检查；不复写 run131，不重复水杯题。"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ["MUSIC_WEB_ROUTE"] = "gpt2"
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import gpt2_adapter as A
from execution_integrity import write_json, write_text, sha_file


def main():
    rows = []
    stop = False
    for name in ("short_q", "long_sum"):
        source = ROOT / "runs/run131_gpt2_smoke/prompts" / (name + ".txt")
        prompt = source.read_text(encoding="utf-8-sig")
        marker = "INPUT_COMPLETE_" + name.upper() + "_中文确认"
        prompt += "\n\n编码与完整性检查：完成上面要求后，最后另起一行原样写：" + marker
        for model in ("gpt56w", "gpt6w"):
            job = "run135__%s__%s" % (model, name)
            if stop:
                rows.append({"job_id": job, "status": "skipped_queue_stop"})
                continue
            try:
                meta = A.call_web_gpt(model, prompt, run_id=OUT.name, job_id=job, out_dir=OUT,
                                      timeout=1800, max_attempts=1, use_cache=False)
                text = (OUT / meta["output_file"]).read_text(encoding="utf-8")
                complete = text.rstrip().endswith(marker)
                md = meta.get("cli_metadata") or {}
                completion = md.get("prepared_response_validation") or {}
                healthy = (meta["status"] == "ok" and complete and not text.count("�")
                           and (meta.get("model_evidence") or {}).get("verdict") == "match"
                           and completion.get("successful_assistant_terminal_observed") is True
                           and completion.get("unsupported_work_continuation_observed") is False)
                rows.append({"job_id": job, "model": model, "prompt_name": name,
                             "source": str(source.relative_to(ROOT)).replace("\\", "/"),
                             "source_sha256": sha_file(source), "status": meta["status"],
                             "healthy": healthy, "complete_marker": complete,
                             "server_terminal": completion, "model_evidence": meta.get("model_evidence"),
                             "seconds": meta["seconds"], "chars": len(text),
                             "error": meta.get("error"), "retry_safe": meta.get("retry_safe"),
                             "queue_stop": meta.get("queue_stop"), "meta_file": "meta/" + job + ".json"})
                stop = bool(meta.get("queue_stop"))
                print(job, meta["status"], "healthy=" + str(healthy), flush=True)
            except Exception as e:
                rows.append({"job_id": job, "status": "failed", "error": "%s: %s" % (type(e).__name__, e),
                             "healthy": False})
                stop = True
            write_json(OUT / "health.json", {"run_id": OUT.name, "records": rows})
    healthy = len(rows) == 4 and all(r.get("healthy") for r in rows)
    write_json(OUT / "health.json", {"run_id": OUT.name, "route_healthy": healthy, "records": rows,
                                    "meaning": "路由/长输入/编码完成性，不等于音乐质量或真实推理深度通过"})
    lines = ["# run135 GPT 网页短/长新鲜复测", "", "未重复杯题；旧 run131 只读。每模型各短/长一次，无自动重试。",
             "route_healthy=%s；这是工程证据，不是音乐质量判决。" % healthy, "",
             "| job | status | healthy | end marker | seconds | chars | server verdict |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["job_id"], r["status"], r.get("healthy"), r.get("complete_marker"), r.get("seconds"),
            r.get("chars"), (r.get("model_evidence") or {}).get("verdict")))
    lines += ["", "## 失败事实"] + ["- %s：%s" % (r["job_id"], r["error"]) for r in rows if r.get("error")]
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    write_text(OUT / ("DONE" if healthy else "FAILED"), "all_four_healthy=" + str(healthy))
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
