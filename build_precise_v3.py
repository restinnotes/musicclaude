import os, re, csv, json, shutil, hashlib, subprocess, datetime, pathlib
ROOT=pathlib.Path(r'D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924')
OUT=pathlib.Path(r'D:\musicclaude\music_since_v3_precise_20261009')
BASE='1b53c78'
CUTOFF=datetime.datetime.fromisoformat('2026-10-08T21:59:51.241+00:00').timestamp()
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)
tracked=set(git('ls-files','-z').decode('utf-8').split('\0'))
changed=set(git('diff','--name-only','-z',BASE,'HEAD').decode('utf-8').split('\0'))- {''}
selection={p:'git_diff_since_before_v3_install' for p in changed if (ROOT/p).is_file()}
skip={'.git','__pycache__','.pytest_cache','node_modules','.venv'}
omitted=[]
for parent,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in skip]
    for name in files:
        p=pathlib.Path(parent)/name
        rel=p.relative_to(ROOT).as_posix()
        if rel in selection: continue
        if name.endswith(('.pyc','.lock')): continue
        match=re.match(r'runs/run(\d+)(?:_|/)',rel)
        st=p.stat()
        if match and 131<=int(match.group(1))<=150:
            selection[rel]='new_experiment_run131_to_run150'
        elif rel not in tracked and max(st.st_ctime,st.st_mtime)>=CUTOFF:
            # Local score-page crops were explicitly declined by the user.
            if re.match(r'(kopp_ex.*\.png|tools/page.*\.png)$',rel):
                omitted.append({'path':rel,'reason':'user_declined_score_page_crops'})
            else: selection[rel]='untracked_or_ignored_created_or_modified_after_start'
rows=[]
for rel,reason in sorted(selection.items()):
    src=ROOT/rel; dst=OUT/'work'/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists() or dst.stat().st_size != src.stat().st_size or dst.stat().st_mtime != src.stat().st_mtime:
        shutil.copy2(src,dst)
    rows.append({'path':'work/'+rel,'source':str(src),'reason':reason,'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(OUT/'git_changes').mkdir(exist_ok=True)
(OUT/'git_changes'/'since_v3.patch').write_bytes(git('diff','--binary',BASE,'HEAD'))
(OUT/'git_changes'/'commits.txt').write_bytes(git('log','--reverse','--format=%H %ai %s',BASE+'..HEAD'))
subprocess.run(['git','bundle','create',str(OUT/'git_changes'/'since_v3.bundle'),'master','^'+BASE],cwd=ROOT,check=True,capture_output=True)
shutil.copy2(pathlib.Path(r'D:\musicclaude\music_work_since_1008v3_20261009')/'musicclaude_claude_muse_autonomous_20261008_v3.zip',OUT/'musicclaude_claude_muse_autonomous_20261008_v3.zip')
# Include only memory files touched during this work; preserve their external source paths.
memroot=pathlib.Path(r'C:\Users\zuoyi\.claude\projects\D--musicclaude\memory')
if memroot.exists():
    for src in memroot.rglob('*'):
        if src.is_file() and max(src.stat().st_ctime,src.stat().st_mtime)>=CUTOFF:
            rel='memory_updates/'+src.relative_to(memroot).as_posix(); dst=OUT/rel
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
            rows.append({'path':rel,'source':str(src),'reason':'project_memory_touched_after_start','bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
with (OUT/'WORK_FILE_MANIFEST.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['path','source','reason','bytes','sha256']);writer.writeheader();writer.writerows(rows)
(OUT/'OMITTED_FILES.json').write_text(json.dumps(omitted,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'base_before_install':BASE,'v3_install':'6ec7f5a','head':git('rev-parse','HEAD').decode().strip(),'start_utc':'2026-10-08T21:59:51.241Z','commits':len(git('rev-list',BASE+'..HEAD').splitlines()),'work_files':len(rows),'work_bytes':sum(r['bytes'] for r in rows),'selection_reasons':{reason:sum(r['reason']==reason for r in rows) for reason in sorted({r['reason'] for r in rows})},'omitted_score_crops':len(omitted)}
(OUT/'SCOPE.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
