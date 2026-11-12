"""10-31: one review request to ChatGPT through the MimicGate NORMAL (persistent, non-temporary) path with a zip attached,
so the chat stays in the user's history. Single submit, no retry."""
import base64, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
d = Path(sys.argv[1])
from src.config import Config
prompt = (d / "prompt.txt").read_text(encoding="utf-8")
z = base64.b64encode((d / "gpt_review_pack.zip").read_bytes()).decode()
payload = {"model": "gpt-5.6-sol", "reasoning_effort": "xhigh", "stream": False,
           "messages": [{"role": "user", "content": [{"type": "text", "text": prompt},
                        {"type": "file", "file": {"filename": "gpt_review_pack.zip", "file_data": z, "mime_type": "application/zip"}}]}]}
claim = os.open(d / "started.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600); os.close(claim)
t0 = time.monotonic(); status = body = err = None
try:
    req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", data=json.dumps(payload, ensure_ascii=False).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + Config.API_TOKEN,
                                          "X-MimicGate-Thread-Mode": "fresh"})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=3600) as r:
        status = r.status; body = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    status = e.code
    try: body = json.loads(e.read().decode())
    except Exception: err = "invalid_error_body"
except Exception as e:
    err = type(e).__name__ + ": " + str(e)[:300]
out = json.dumps({"http_status": status, "body": body, "error": err, "seconds": round(time.monotonic() - t0)}, ensure_ascii=False, indent=1)
out = out.replace(Config.API_TOKEN, "[REDACTED]") if Config.API_TOKEN else out
(d / "result.json").write_text(out, encoding="utf-8")
