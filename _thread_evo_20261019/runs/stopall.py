import os, psutil
me = os.getpid(); par = psutil.Process(me).parent().pid; n = 0
KEYS = ("repair_line.py", "precise.py", "covjudge.py", "mech_check.py", "draft23.py", "synth3.py", "fill3.py", "finalize3.py", "gpt3_cli.py")
for p in psutil.process_iter(["cmdline", "name"]):
    if p.pid in (me, par): continue
    a = p.info["cmdline"] or []
    if not a: continue
    exe = a[0].lower()
    if ("python" in exe and len(a) > 1 and a[1].endswith(KEYS)) or (exe.endswith("cmd.exe") and any("gpt3.cmd" in x for x in a)) \
       or ("node" in exe and any("pro_bridge" in x for x in a)) or ("python" in exe and any("pro_bridge" in x for x in a)):
        try: p.kill(); n += 1
        except Exception: pass
print("这次又停了", n, "个")
left = []
for p in psutil.process_iter(["cmdline"]):
    a = p.info["cmdline"] or []
    if a and (("python" in a[0].lower() and len(a) > 1 and a[1].endswith(KEYS)) or any("pro_bridge" in x for x in a)) and p.pid not in (me, par):
        left.append(a[1] if len(a) > 1 else a[0])
print("还剩:", left or "无")
