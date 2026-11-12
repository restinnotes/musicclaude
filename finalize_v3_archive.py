from pathlib import Path
import json,csv,hashlib,zipfile,datetime
p=Path(r'D:\musicclaude\music_since_v3_precise_20261009')
catalog=json.loads((p/'conversation_logs/thread_catalog.json').read_text(encoding='utf-8'))
index=['# 对话索引','', '共 61 个线程：2 个主对话，59 个子代理。001_continued.md 补充最新主对话。','']
for i,t in enumerate(catalog,1):
    index.append(f"- [{t['title']}]({i:03d}.md) — `{t['threadId']}`")
(p/'conversation_logs/INDEX.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
scope=json.loads((p/'SCOPE.json').read_text(encoding='utf-8'))
readme=f'''# 1008 v3 之后的工作与对话记录

起点：2026-10-08T21:59:51.241Z，安装提交 6ec7f5a；差异相对安装前提交 1b53c78，包含安装本身。终点提交：{scope['head']}。

- work/：此后提交改动的当前文件、run131–run150 实验文件，以及起点后创建或修改的未跟踪/忽略文件。
- git_changes/：此阶段的提交清单、二进制差异补丁和增量 Git bundle。bundle 需要原仓库中已有基点 1b53c78，不能单独克隆成完整旧仓库。
- conversation_logs/：2 个主对话、59 个子代理的可读消息记录；INDEX.md 是索引。001.md 是当前分支，046.md 是最初主对话；001_continued.md 补充本轮打包期间的消息。activity/ 是上次中断前已导出的部分详细活动，不代表所有工具活动均已导出。
- memory_updates/：本阶段修改的项目记忆。
- 原始 1008 v3 ZIP。
- WORK_FILE_MANIFEST.csv：工作文件来源、纳入原因、大小、SHA-256。
- OMITTED_FILES.json：按此前要求排除的乐谱页局部截图。

范围规则和统计见 SCOPE.json。work/ 是增量工作文件集合，保留原路径，并非旧项目全量副本。失败、作废和未完成的本阶段实验一并保留，不表示已经验收。
'''
(p/'README.md').write_text(readme,encoding='utf-8')
rows=list(csv.DictReader((p/'WORK_FILE_MANIFEST.csv').open(encoding='utf-8-sig')))
for r in rows:
    f=p/r['path']
    assert f.stat().st_size==int(r['bytes']),r['path']
    assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],r['path']
files=sorted(x for x in p.rglob('*') if x.is_file())
with (p/'ARCHIVE_FILE_MANIFEST.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['path','bytes','sha256'])
    for x in files:w.writerow([x.relative_to(p).as_posix(),x.stat().st_size,hashlib.sha256(x.read_bytes()).hexdigest()])
z=p.with_suffix('.zip')
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as a:
    for x in sorted(p.rglob('*')):
        if x.is_file():a.write(x,x.relative_to(p).as_posix())
with zipfile.ZipFile(z) as a:
    assert a.testzip() is None
    entries=len(a.infolist())
sha=hashlib.sha256(z.read_bytes()).hexdigest()
z.with_suffix('.zip.sha256').write_text(sha+'  '+z.name+'\n',encoding='ascii')
print(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'entries':entries,'work_files_verified':len(rows),'sha256':sha,'scope':scope},ensure_ascii=False))
