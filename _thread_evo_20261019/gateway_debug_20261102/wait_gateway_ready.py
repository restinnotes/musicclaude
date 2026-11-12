"""Bounded, read-only readiness check before resuming any model submission."""
import subprocess,time

check=['docker','exec','-w','/app','yi-mimicgate-20261002','python','/app/state/gateway-fix-20261102/check_idle.py']
started=time.monotonic()
while time.monotonic()-started<120:
    result=subprocess.run(check,capture_output=True,text=True,encoding='utf-8',timeout=15)
    if result.returncode==0:
        print('GATEWAY_READY',result.stdout.strip(),flush=True)
        break
    time.sleep(2)
else:
    raise SystemExit('Gateway did not become ready; no model request was dispatched')
