import sys,os,json,types,ast,re,socket,subprocess,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(r'D:\musicclaude');T=P/'_thread_evo_20261019';B=P/'_bead_op61_20261020';O=T/'_codex/param_20261101';TMP=O/'tmp'
sys.path[:0]=[str(T),str(B)]
blocked=[]
def deny(*args,**kwargs):blocked.append(str(args[:1]));raise RuntimeError('no real process or network')
subprocess.run=deny;subprocess.Popen=deny;os.system=deny;socket.socket.connect=deny;socket.create_connection=deny
spec=importlib.util.spec_from_file_location('test_gen',B/'gen_A/gen.py');gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
old=ast.parse((B/'gen_A/gen.py.bak_param20261101').read_text(encoding='utf-8'))
job_ast=ast.Module(body=[n for n in old.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='JOBS' for x in n.targets)],type_ignores=[])
ns={};exec(compile(job_ast,'<old jobs>','exec'),ns);assert gen.JOBS==ns['JOBS'] and len(gen.JOBS)==10
# Test the added 24-job dispatch and exact collection using a mock backend only.
import work_meta
base=TMP/'mock_registry';wd=base/'mock24';wd.mkdir(parents=True,exist_ok=True)
d=dict(work_meta.load('op61'));d={k:v for k,v in d.items() if k not in ['_dir','a_sources','bead_legacy_root','pool_sources','old_center']};d.update(key='mock24',title_zh='《调度测试》',opus='测试编号')
(wd/'work.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');(wd/'segmentation.json').write_text((T/'works/op61/segmentation.json').read_text(encoding='utf-8'),encoding='utf-8')
os.environ['WORKS_ROOT']=str(base);gen.WORK='mock24'
gpts=[];other=[]
def fake_gpt(name,pv,model,prompt_text=None):
    gpts.append((name,pv,model,prompt_text));out=gen.output_dir();out.mkdir(parents=True,exist_ok=True);(out/(name+'.md')).write_text('mock:'+name,encoding='utf-8')
def fake_runner(run_dir,jobs,max_workers,timeout):
    other.extend(jobs);out=Path(run_dir)/'outputs';out.mkdir(parents=True,exist_ok=True)
    for j in jobs:(out/(j['job_id']+'.md')).write_text('mock:'+j['job_id'],encoding='utf-8')
    return [{'status':'ok'} for j in jobs]
gen.run=fake_gpt;sys.modules['runner']=types.SimpleNamespace(run_jobs=fake_runner)
gen.corpus24();assert len(gpts)==12 and len(other)==12
assert len(list((wd/'A').glob('*.md')))==24
for j in gen.corpus_jobs('mock24'):
    assert (wd/'A'/('SRC-'+j['name']+'.md')).read_text(encoding='utf-8')=='mock:'+j['name']
assert all('forbid_tools' in j for j in other if j['branch']=='A-int')
assert all('forbid_tools' not in j for j in other if j['branch']=='A-web')
assert any(n=='gpt56w-int-1' and p.endswith('回答时请不要进行联网搜索。') for n,pv,m,p in gpts)
gen.corpus24();assert len(gpts)==12 and len(other)==12
os.environ.pop('WORKS_ROOT',None)
# Verify the merged A attachment, including order and delimiters.
merged_checks=[]
for w in ['op60','op61']:
    files=sorted(work_meta.source_dir(work_meta.load(w)).glob('SRC-*.md'));assert len(files)==24
    merged='\n\n'.join(f'########## 文件：{f.name} ##########\n\n'+f.read_text(encoding='utf-8') for f in files)
    assert merged==(T/'runs'/f'A_drafts_{w}.md').read_text(encoding='utf-8')
    merged_checks.append(w)
assert not blocked,blocked
result={'default_10_jobs_unchanged':True,'mock_GPT_jobs':len(gpts),'mock_non_GPT_jobs':len(other),'collected_verbatim_sources':24,'second_run_skips_complete_A':True,'A_attachments_exact':merged_checks,'network_or_process_attempts':blocked}
(O/'dispatch_test.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
