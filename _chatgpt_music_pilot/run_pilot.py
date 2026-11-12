from pathlib import Path
import subprocess,json,time,hashlib,datetime,sys,os
root=Path(r"D:\musicclaude\_chatgpt_music_pilot")
out=root/"results";out.mkdir(parents=True,exist_ok=True)
for j in ["A01","B02","C02"]:
 for model,slug in [("gpt-6-thinking","gpt6w"),("gpt-5-6-thinking","gpt56w")]:
  infile=root/(j+".txt")
  fhash=hashlib.sha256(infile.read_bytes()).hexdigest()
  prefix=out/(j+"__"+slug)
  if prefix.with_suffix(".json").exists(): print("SKIP",j,slug,flush=True);continue
  cmd=[r"D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd","ask","--file",str(infile),"--model",model,"--json"]
  started=time.time()
  try:
   r=subprocess.run(cmd,capture_output=True,encoding="utf-8",errors="replace",timeout=900)
   prefix.with_suffix(".json").write_text(r.stdout,encoding="utf-8")
   prefix.with_suffix(".stderr.txt").write_text(r.stderr,encoding="utf-8")
   try:
    data=json.loads(r.stdout.strip().lstrip("\ufeff"))
    success=(r.returncode==0 and data.get("completed") is True and bool(data.get("response")))
    meta=data.get("metadata",{})
    resp_len=len(data.get("response") or "")
    replyhash=meta.get("response_sha256")
    effort=meta.get("thinking_effort")
    route=meta.get("model")
   except Exception as e:
    success=False;resp_len=0;replyhash=None;effort=None;route=None
   info={"job":j,"model_requested":model,"model_reported":route,"effort":effort,"success":success,"returncode":r.returncode,"seconds":round(time.time()-started,2),"response_chars":resp_len,"response_sha256":replyhash,"prompt_sha256":fhash,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
   prefix.with_suffix(".meta.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
   print("DONE",json.dumps(info,ensure_ascii=False),flush=True)
  except Exception as e:
   err={"job":j,"model":model,"error":str(e),"seconds":round(time.time()-started,2)}
   prefix.with_suffix(".error.json").write_text(json.dumps(err,ensure_ascii=False),encoding="utf-8")
   print("ERROR",json.dumps(err,ensure_ascii=False),flush=True)
print("PILOT_FINISHED",flush=True)
