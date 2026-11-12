"""Nozomi MimicGate route for evo.call (10-27; user: nozomi-mimicgate-20261027, the Pro account, Extra High verified as
the real model without downgrade). Goes through the user's local client (API key stays in Windows DPAPI storage), which
never retries by itself. Accepted only when the page diagnostics confirm temporary + unpersonalized, the prompt was
verified, the response is complete and the selected model / effort are exactly the requested ones.
NZ_EFFORT = xhigh (default) | high;  NZ_SLOTS = requests in flight from this process (default 3)."""
import hashlib, json, os, subprocess, threading, time
import evo

PY = "C:/Users/zuoyi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
CLIENT = "C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/work/nozomi_mimicgate_client.py"
MODEL = {evo.G6: "gpt-6", evo.G56: "gpt-5.6-sol"}
EFFORT = os.environ.get("NZ_EFFORT", "xhigh")
SLOTS = threading.Semaphore(int(os.environ.get("NZ_SLOTS", "3")))


def verified(r, model):
    g = r.get("mimicgate_diagnostics") or {}; m = g.get("model") or {}
    return (bool((g.get("temporary_chat") or {}).get("verified")) and bool((g.get("non_personalized") or {}).get("verified"))
            and g.get("prompt_content_verified") is True and g.get("response_complete") is True
            and m.get("model") == model and m.get("selected_effort") == EFFORT and not m.get("fallback_reason"))


def call(run_id, message, prompt_text, model, meta):
    d = evo.RUNS / run_id
    if evo.want_no_web(meta) and evo.NO_WEB.strip() not in message[-60:]:
        message += evo.NO_WEB
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    inp = d / "input.txt"; inp.write_text(message, encoding="utf-8")
    if meta:
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    nz = MODEL[model]; attempt = 0
    while attempt < 2:
        out = d / f"nz_{attempt}.json"
        with SLOTS:
            started = time.strftime("%Y-%m-%dT%H:%M:%S"); t0 = time.time()
            cp = subprocess.run([PY, CLIENT, "--model", nz, "--effort", EFFORT, "--prompt-file", str(inp), "--output", str(out)],
                                capture_output=True, cwd=os.path.dirname(CLIENT))
        dt = time.time() - t0
        try:
            r = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            r = {}
        err = json.dumps(r.get("error"), ensure_ascii=False) if r.get("error") else cp.stderr.decode("utf-8", "replace")[-600:]
        if "busy" in err.lower() or "429" in err:
            print(f"[{run_id}] nozomi busy, waiting", flush=True); time.sleep(60); continue
        resp = ((r.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        ok = cp.returncode == 0 and resp.strip() and verified(r, nz)
        m = (r.get("mimicgate_diagnostics") or {}).get("model") or {}
        rec = {"run_id": run_id, "attempt": attempt, "account": "nozomi-mimicgate", "route": "nozomi", "started": started,
               "seconds": round(dt), "completed": bool(ok), "model": m.get("model"), "effort": m.get("selected_effort"),
               "effort_label": m.get("selected_effort_label"), "message_chars": len(message),
               "message_sha256": hashlib.sha256(message.encode()).hexdigest(), "meta": meta or {}}
        if ok:
            rec["response_chars"] = len(resp)
            (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "output.txt").write_text(resp, encoding="utf-8"); evo.log(rec)
            print(f"[{run_id}] ok {dt:.0f}s {len(resp)} chars ({rec['effort_label']})", flush=True)
            return resp
        rec["error"] = err[-800:]
        (d / f"call_fail_{attempt}.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8"); evo.log(rec)
        print(f"[{run_id}] FAILED {dt:.0f}s {err[-200:]!r}", flush=True)
        attempt += 1
    return None
