# Delegate a bounded task file to Muse (opencode --standalone), resume on dropped sessions, log transcript.
import json, subprocess, sys, time, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MODEL = "opencode2api/muse-spark-1.3-contributor-free#xhigh"
DONE = "【任务完成】"
FOOTER = f"\n\n---\n严格按上面的要求做，不要自行扩大范围或改变方案；遇到要求之外的决策点就停下在汇报里说明。全部完成并写好汇报后，最后单独输出一行：{DONE}\n"
RESUME = f"上一轮会话在任务完成前中断了。先检查当前文件和运行状态，从中断处接着做完，不要重复已完成部分。完成后最后单独输出一行：{DONE}"

def run_round(argv, text, log):
    r = subprocess.run(argv, input=text.encode("utf-8"), capture_output=True, cwd=ROOT, timeout=14400)
    out, err = r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")
    session, texts = None, []
    for line in out.splitlines():
        try: o = json.loads(line)
        except Exception: continue
        session = session or o.get("sessionID") or (o.get("part") or {}).get("sessionID")
        p = o.get("part") or {}
        if p.get("type") == "text" and p.get("text"): texts.append(p["text"])
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"\n===== round @ {time.strftime('%Y-%m-%d %H:%M:%S')} exit={r.returncode} session={session}\n{out}\n---STDERR---\n{err}")
    return r.returncode, session, "\n".join(texts)

def main():
    task = ROOT / sys.argv[1]
    log = task.with_suffix(".log"); log.write_text("", encoding="utf-8")
    base = [shutil.which("opencode"), "run", "--standalone", "--auto", "--format", "json", "--model", MODEL]
    code, session, text = run_round(base, task.read_text(encoding="utf-8") + FOOTER, log)
    rounds = 1
    while DONE not in text and session and rounds <= 6:
        if '"status":429' in log.read_text(encoding="utf-8")[-4000:]: time.sleep(120)
        code, _, more = run_round(base + ["--session", session], RESUME, log)
        text += "\n" + more; rounds += 1
    print(f"{'done' if DONE in text else 'incomplete'} rounds={rounds} session={session} exit={code}")
    print(text[-3000:])

if __name__ == "__main__":
    main()
