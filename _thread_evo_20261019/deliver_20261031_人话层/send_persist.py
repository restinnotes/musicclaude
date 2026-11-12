"""10-31: one review request through the MimicGate persistent-standard mode (Temporary Chat OFF, kept in the account
history). gpt-6 / high, text only, single submit, no retry."""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
d = Path(sys.argv[1])
from src.config import Config
prompt = (d / "prompt.txt").read_text(encoding="utf-8")
payload = {"model": "gpt-6", "reasoning_effort": "high", "stream": False, "messages": [{"role": "user", "content": prompt}]}
os.close(os.open(d / "started.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
t0 = time.monotonic(); status = body = err = None
def once():
  global status, body, err
  status = body = err = None
  try:
      req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", data=json.dumps(payload, ensure_ascii=False).encode(),
                                   headers={"Content-Type": "application/json", "Authorization": "Bearer " + Config.API_TOKEN,
                                            "X-MimicGate-Mode": "persistent-standard"})
      with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=3600) as r:
          status = r.status; body = json.loads(r.read().decode())
  except urllib.error.HTTPError as e:
      status = e.code
      try: body = json.loads(e.read().decode())
      except Exception: err = "invalid_error_body"
  except Exception as e:
      err = type(e).__name__ + ": " + str(e)[:300]
for _ in range(40):   # 10-31: 429 busy = gateway queue full, nothing was sent -> wait and retry
    once()
    if not (status == 429 and "busy" in json.dumps(body or {})):
        break
    time.sleep(60)
out = json.dumps({"http_status": status, "body": body, "error": err, "seconds": round(time.monotonic() - t0)}, ensure_ascii=False, indent=1)
if Config.API_TOKEN: out = out.replace(Config.API_TOKEN, "[REDACTED]")
(d / "result.json").write_text(out, encoding="utf-8")
