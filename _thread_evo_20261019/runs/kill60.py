import os, time, psutil
me = os.getpid()
def py(p, name):
    a = p.info["cmdline"] or []
    return len(a) > 1 and "python" in a[0].lower() and a[1].endswith(name)
def procs():
    return [p for p in psutil.process_iter(["cmdline", "pid", "ppid"]) if p.pid != me and py(p, "synth3.py") and "op60" in p.info["cmdline"][2:]]
def inflight():
    return any(py(p, "gpt3_cli.py") and "syP4a_op60" in " ".join(p.info["cmdline"]) for p in psutil.process_iter(["cmdline"]))
t0 = time.time()
while inflight() and time.time() - t0 < 1500:
    time.sleep(1)
for p in procs():
    par = psutil.Process(p.info["ppid"])
    print("kill subshell", par.pid, par.name(), "and", p.pid, p.info["cmdline"][1:], "inflight", inflight(), round(time.time() - t0), "s", flush=True)
    if par.name().lower().startswith("bash"):
        par.kill()
    p.kill()
