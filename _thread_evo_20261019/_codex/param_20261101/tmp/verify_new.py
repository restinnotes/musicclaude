import sys, os, json, socket, subprocess, runpy, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(r'D:\musicclaude');T=P/'_thread_evo_20261019';B=P/'_bead_op61_20261020';O=T/'_codex/param_20261101';TMP=O/'tmp'
sys.path[:0]=[str(T),str(B)]
blocked=[]
def deny(*args,**kwargs):blocked.append(str(args[:1]));raise RuntimeError('offline: no process/network')
subprocess.run=deny;subprocess.Popen=deny;os.system=deny;socket.socket.connect=deny;socket.create_connection=deny
import work_meta
base=TMP/'works'; target=base/'op52';target.mkdir(parents=True,exist_ok=True)
d={'key':'op52','composer':'肖邦','title_zh':'《第四叙事曲》','tonality':'f小调','opus':'Op.52',
   'segmentation_source':'临时三段示例','segmentation_source_note':'仅作离线测试，不是正式曲式分段',
   'specificity_candidates':work_meta.load('op61')['specificity_candidates'],'specificity_right':'第四叙事曲 Op.52',
   'seconds_per_measure':3.0,'fix_session':'fresh'}
(target/'work.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
s={'work':'临时测试','short_name':'第四叙事曲','total_measures':30,'boundaries':[1,11,21,31],
   'segments':[{'id':f'S{i+1:02d}','start':i*10+1,'end':i*10+10,'label':f'测试第{i+1}段'} for i in range(3)],'source':{'note':'临时分段'},'method':'offline fixture'}
(target/'segmentation.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
history=TMP/'history52'
def save(stage,seg,value):
    f=history/stage/(seg+'.parsed.json');f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
for row in s['segments']:
    seg=row['id']
    save('pool_v2/pool',seg,{'items':[{'id':'P01','src':'SRC-test','src_range':'1-30','measures':str(row['start'])+'-'+str(row['end']),'type':'感受','quote':'测试原话','experience':'测试体验'}]})
    save('gen_b',seg,{'ladder':[{'k':1,'id':'F1','text':'测试段落听感','measures':str(row['start'])+'-'+str(row['end']),'placement':'stated','relation':[],'sources':[],'also_expressed_by':[]}]})
    save('rev1_b',seg,{'experiences':[]});save('rev2_b',seg,{'missing':[]})
    save('final_b',seg,{'title':'测试标题','reader':'测试正文','beads':[{'role':'主体验','measures':str(row['start']),'text':'测试听感'}]})
save('piece_b','ALL',{'per_segment':[],'repeated_templates':[],'fixes':[],'continuity_issues':[]})
mat=TMP/'material52.json';mat.write_text(json.dumps({'per_draft':[{'core':'临时中心材料'}]*24,'clusters':[{'n':24,'summary':'临时共同理解'}]},ensure_ascii=False),encoding='utf-8')
cand=TMP/'candidates52.json';cand.write_text(json.dumps([{'id':'N1','center':'表达愿望与保持距离相互牵动。'}],ensure_ascii=False),encoding='utf-8')
os.environ['WORKS_ROOT']=str(base);os.environ['WORK']='op52';os.environ['CDV']='2'
renders=TMP/'render52'
def cli(file,args):
    sys.argv=[str(file)]+args
    try:runpy.run_path(str(file),run_name='__main__')
    except SystemExit as e:
        assert e.code in [None,0],(file,e.code)
cli(B/'gen_A/gen.py',['--work','op52','--corpus24','--render-dir',str(renders/'N02')])
cli(B/'chain.py',['render','--work','op52','--history-root',str(history),'--render-dir',str(renders/'N03')])
cli(T/'center_from_A.py',['--work','op52','--render-dir',str(renders/'N04a')])
cli(T/'center_dag.py',['render','--work','op52','--a-json',str(mat),'--candidates-json',str(cand),'--render-dir',str(renders/'N04')])
forbidden=['幻想波兰舞曲','船歌','PTNA','塚田','Op.61','Op.60']
files=list(renders.rglob('*.txt'));fails=[]
for f in files:
    text=f.read_text(encoding='utf-8')
    # Only the specificity candidate-list line is an allowed exception.
    scanned='\n'.join(line for line in text.splitlines() if not line.startswith('作品：'))
    for token in forbidden:
        if token in scanned:fails.append((str(f),token))
    import re
    if re.search(r'\{(?:WORK|WORK_WITH_KEY|COMPOSER|SEGMENTATION_SOURCE|SEGMENTATION_LIST_SOURCE|NSEG_ZH|SEG|MM|LABEL|SEGLIST|SEC|STRUCT_SPEC|REVIEW|POOL|NPOOL|LADDER|PIECE|ALL|PREVIOUS)\}',scanned):fails.append((str(f),'unexpanded token'))
assert not fails,fails
jobs=json.loads((renders/'N02/jobs24.json').read_text(encoding='utf-8'));assert len(jobs)==24 and len({j['name'] for j in jobs})==24
assert all('第四叙事曲' in j['prompt'] and not any(x in j['prompt'] for x in forbidden) for j in jobs)
# Composer too must be a parameter. Use a separate temporary registry entry.
d2=dict(d,key='testcomposer',composer='测试作曲家',title_zh='《测试作品》',opus='作品一',specificity_candidates=[f'候选作品{i}' for i in range(1,11)],specificity_right='候选作品1')
target2=base/'testcomposer';target2.mkdir(exist_ok=True);(target2/'work.json').write_text(json.dumps(d2,ensure_ascii=False),encoding='utf-8');(target2/'segmentation.json').write_text(json.dumps(s,ensure_ascii=False),encoding='utf-8')
import centersel,center_dag
assert '肖邦' not in centersel.spec_for('testcomposer')
assert '肖邦' not in center_dag.render_write('testcomposer',version='2',material=json.loads(mat.read_text(encoding='utf-8')))
# Offline renderer refuses reuse/overwrite.
try:work_meta.write_prompts(renders/'N02',{'A_int_v1.txt':'do not overwrite'})
except FileExistsError:pass
else:raise AssertionError('renderer overwrote an existing file')
assert not blocked,blocked
report={'work':'op52','rendered_prompts':len(files),'job_plan':len(jobs),'forbidden_tokens':forbidden,'failures':fails,'network_or_process_attempts':blocked,'other_composer':'PASS','exclusive_render_writes':'PASS','render_root':str(renders)}
(O/'new_work_test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
