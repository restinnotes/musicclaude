import sys, os, socket, subprocess, importlib.util, json, hashlib, random, ast
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(r'D:\musicclaude'); T=P/'_thread_evo_20261019'; B=P/'_bead_op61_20261020'; O=T/'_codex/param_20261101'
sys.path[:0]=[str(T),str(B)]
blocked=[]
def deny(*args,**kwargs):
    blocked.append(str(args[:1])); raise RuntimeError('offline audit forbids process/network')
subprocess.run=deny; subprocess.Popen=deny; os.system=deny
socket.socket.connect=deny; socket.create_connection=deny

def mod(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def text(f):return Path(f).read_text(encoding='utf-8-sig')
rows=[]; allprompts={}
def check(group,label,got,want,ref=''):
    ok=got==want
    row=dict(group=group,label=label,ok=ok,reference=str(ref),sha256=hashlib.sha256(got.encode('utf-8')).hexdigest())
    if not ok:
        k=next((i for i,(a,b) in enumerate(zip(got,want)) if a!=b),min(len(got),len(want)))
        row.update(offset=k,actual=got[max(0,k-45):k+100],expected=want[max(0,k-45):k+100],lengths=[len(got),len(want)])
    rows.append(row)
    if not ok: print('DIFF',group,label,row)

import work_meta, chain, centersel, center_dag, center_from_A, evo
Agen=mod(B/'gen_A/gen.py','param_gen')
for w in ['op60','op61']:
    chain.configure(w); d=work_meta.load(w)
    for pv in ['A_int_v1','A_web_v2']:
        ref=B/'gen_A'/f'{pv}.op61.txt' if w=='op61' else P/'music_work_since_1008v3_20261009/prompts/versions'/f'{pv}.txt'
        want=text(ref).replace('{{WORK}}',work_meta.name(d,True))
        got=Agen.render(pv,w);check('N02 baseline',w+pv,got,want,ref)
        allprompts[w+'.'+pv]=got
        if w=='op61':
            ref=next((T/'DAG/prompts').glob('N02*/'+('模板_int.txt' if pv=='A_int_v1' else '模板_web.txt')))
            check('DAG snapshot',w+pv,got,text(ref),ref)
    legacy=P/('_bead_op61_20261020' if w=='op61' else '_bead_saturation_20261018')
    old=mod(legacy/'sat.py','original_sat_'+w)
    rt=chain.production_runtime()
    captures={}
    def capture(st,sg,prompt_text,attach=(),session=None):
        captures[(st,sg)]=(prompt_text,session,bool(attach));return None
    for m in [old,rt]:
        m.call=capture;m.sources_zip=lambda:Path('sources.zip')
    for s in chain.SEGS:
        rt.t_pool(s); rt.t_gen_b(s);rt.t_rev1_b(s);rt.t_rev2_b(s);rt.t_final_b(s);rt.parameterized_fix(s)
    rt.t_piece('final_b','piece_b')
    newcap=dict(captures);captures.clear()
    for s in chain.SEGS:
        if w=='op61':old.t_pool(s)
        else:
            tpl=text(P/'bead_chain/prompts/pool_v2.md')
            capture('pool_v2/pool',s,old.fill(tpl,s),[Path('sources.zip')])
        old.t_gen_b(s);old.t_rev1_b(s);old.t_rev2_b(s);old.t_final_b(s)
        if w=='op61':old.t_fix_fresh(s)
        else:old.t_fix(s,'piece_b','gen_b','final2_b')
    old.t_piece('final_b','piece_b')
    for (st,sg),(prompt,session,attach) in newcap.items():
        check('N03 before-after',w+'/'+st+'/'+sg,prompt,captures[(st,sg)][0],legacy/'sat.py')
        assert (session,attach)==captures[(st,sg)][1:],(w,st,sg,'session/attachment changed')
        allprompts[w+'.'+st.replace('/','_')+'.'+sg]=prompt
        if st=='pool_v2/pool' and w=='op60':
            ref=P/'bead_chain/runs/final/pool'/f'{sg}.prompt.txt'
        else:ref=legacy/'runs'/st/f'{sg}.prompt.txt'
        if ref.exists():check('N03 historical',w+'/'+st+'/'+sg,prompt,text(ref),ref)
    
    if w=='op60':
        # Actual Op.60 whole-piece/fix runs used the final and chosen histories.
        for m in [rt,old]:
            captures.clear()
            m.t_piece('final','piece');m.t_piece('chosen','piece_c')
            for seg in ['S08','S13','S14']:m.t_fix(seg)
            for seg in ['S03','S06','S07','S12']:m.t_fix_c(seg)
            if m is rt:extra_new=dict(captures)
            else:extra_old=dict(captures)
        for (stage,seg),(msg,session,attach) in extra_new.items():
            check('N03 before-after',w+'/'+stage+'/'+seg,msg,extra_old[(stage,seg)][0],legacy/'sat.py')
            assert (session,attach)==extra_old[(stage,seg)][1:]
            ref=legacy/'runs'/stage/f'{seg}.prompt.txt'
            check('N03 historical',w+'/'+stage+'/'+seg,msg,text(ref),ref)
    for f in (B/'prompts').glob('*.param.md'):
        ref=(P/'bead_chain/prompts'/f.name.replace('.param','')) if w=='op60' and f.name.startswith('pool') else legacy/'prompts'/f.name.replace('.param','')
        check('N03 templates',w+'/'+f.name,chain.template(f.name.replace('.param.md','')),text(ref),ref)
    # N04 before-after + real prompts (historical randomized candidate ordering).
    oldcs=mod(T/'centersel.py.bak_param20261101','original_cs') if False else None
    oldglobals={}
    exec(compile(text(T/'centersel.py.bak_param20261101'),'<old-centersel>','exec'),oldglobals)
    check('N04 constants',w+'/SPEC',centersel.spec_for(w),oldglobals['SPEC'],T/'centersel.py.bak_param20261101')
    check('N04 constants',w+'/FIT',centersel.FIT,oldglobals['FIT'],T/'centersel.py.bak_param20261101')
    ref=T/'runs'/f'cA_{w}'/'input.txt'
    check('N04 historical',w+'/N04a',center_from_A.render(w),text(ref),ref)
    allprompts[w+'.N04a']=center_from_A.render(w)
    for v in ['', '2']:
        got=center_dag.render_write(w,version=v)
        oldglobals={};exec(compile(text(T/'center_dag.py.bak_param20261101'),'<old-center-dag>','exec'),oldglobals)
        tpl=oldglobals['WRITE2' if v=='2' else 'WRITE']
        expected=tpl.format(WORK=work_meta.name(d),CLUSTERS=oldglobals['clusters'](w),CORES=oldglobals['cores'](w))
        check('N04 before-after',w+'/write'+v,got,expected,T/'center_dag.py.bak_param20261101')
        ref=T/'runs'/f'cdw{v}_{w}'/'input.txt'
        if ref.exists():check('N04 historical',w+'/write'+v,got+evo.NO_WEB,text(ref),ref)
        allprompts[w+'.N04b'+v]=got
    for jn in ['gpt6','gpt56']:
        pp=oldglobals['pool'](w);random.Random(f'cdf{w}{jn}').shuffle(pp)
        got=centersel.fit_for(w)+'\n'.join(f"{c['id']}：{c['center']}" for c in pp)
        ref=T/'runs'/f'cdf_{w}_{jn}'/'input.txt'
        if ref.exists():check('N04 historical',w+'/cdf_'+jn,got+evo.NO_WEB,text(ref),ref)
        allprompts[w+'.N04d'+jn]=got
# Snapshot templates from DAG
for node,var in [('N04a',center_from_A.P),('N04b',center_dag.WRITE2.replace('{COMPOSER}','肖邦')),('N04c',centersel.SPEC),('N04d',centersel.FIT)]:
    ref=next((T/'DAG/prompts').glob(node+'*/模板.txt'));check('DAG snapshot',node,var,text(ref),ref)
for stage,node in [('pool_v2','N03a'),('gen_v1','N03b'),('rev1_v1','N03c'),('rev2_v1','N03d'),('final_v2','N03e'),('piece_v1','N03f'),('fix_v1','N03g'),('struct_spec_v1','N03_')]:
    chain.configure('op61');ref=next((T/'DAG/prompts').glob(node+'*/模板.md'));check('DAG snapshot',stage,chain.template(stage),text(ref),ref)
    refdir=ref.parent
    for actual in refdir.glob('实发*'):
        key='op61.'+{'pool_v2':'pool_v2_pool','gen_v1':'gen_b','rev1_v1':'rev1_b','rev2_v1':'rev2_b','final_v2':'final_b'}.get(stage,'NONE')+'.S01'
        if key in allprompts:check('DAG actual',stage,allprompts[key],text(actual),actual)

# Joint N04c test, both versions, all judge/sample permutations.
for version in ['', '2']:
    center_dag.V=version
    for jn in ['gpt6','gpt56']:
        for sample in [1,2]:
            items=[{'id':f"{w}:{c['id']}",'center':c['center']} for w in ['op60','op61'] for c in center_dag.pool(w)]
            random.Random(f'cds{jn}{sample}').shuffle(items)
            got=center_dag.spec_template(['op60','op61'])+'\n'.join(f"C{i+1}：{x['center']}" for i,x in enumerate(items))+evo.NO_WEB
            ref=T/'runs'/f'cds{version}_{jn}_{sample}'/'input.txt'
            if ref.exists():check('N04 historical','joint/spec'+version+jn+str(sample),got,text(ref),ref)
    for w in ['op60','op61']:
        for jn in ['gpt6','gpt56']:
            pp=center_dag.pool(w);random.Random(f'cdf{w}{jn}').shuffle(pp)
            got=centersel.fit_for(w)+'\n'.join(f"{x['id']}：{x['center']}" for x in pp)+evo.NO_WEB
            ref=T/'runs'/f'cdf{version}_{w}_{jn}'/'input.txt'
            if ref.exists():check('N04 historical',w+'/fit'+version+jn,got,text(ref),ref)
# Old centersel actually-issued spec/fit inputs (10-21, before the transport suffix).
for jn in ['gpt6','gpt56']:
    for sample in [1,2]:
        items=[{'id':f"{w}:{c['id']}",'center':c['center']} for w in ['op60','op61'] for c in json.loads(text(T/'evaluations/centersel'/f'pool_{w}.json'))]
        random.Random(f'spec{jn}{sample}').shuffle(items)
        got=centersel.SPEC+'\n'.join(f"C{i+1}：{x['center']}" for i,x in enumerate(items))
        ref=T/'runs'/f'csp_{jn}_{sample}'/'input.txt'
        if ref.exists():check('centersel historical','spec'+jn+str(sample),got,text(ref),ref)
        if jn=='gpt56' and sample==1:
            ref=next((T/'DAG/prompts').glob('N04c*/实发.txt'));check('DAG actual','N04c',got,text(ref),ref)
for w in ['op60','op61']:
    for jn in ['gpt6','gpt56']:
        pp=json.loads(text(T/'evaluations/centersel'/f'pool_{w}.json'));random.Random(f'fit{w}{jn}').shuffle(pp)
        got=centersel.fit_for(w)+'\n'.join(f"{x['id']}：{x['center']}" for x in pp)
        ref=T/'runs'/f'cfit_{w}_{jn}'/'input.txt'
        if ref.exists():check('centersel historical',w+'/fit'+jn,got,text(ref),ref)
        if w=='op61' and jn=='gpt6':
            ref=next((T/'DAG/prompts').glob('N04d*/实发_op61.txt'));check('DAG actual','N04d',got,text(ref),ref)
ref=next((T/'DAG/prompts').glob('N04a*/实发_op61.txt'));check('DAG actual','N04a',center_from_A.render('op61'),text(ref),ref)
ref=next((T/'DAG/prompts').glob('N04b*/实发_op61.txt'));check('DAG actual','N04b',center_dag.render_write('op61',version='2')+evo.NO_WEB,text(ref),ref)
# Original A prompt files actually passed to historical tools.
for w in ['op60','op61']:
    for run in ['run05_saturation','run08_final_models','run106_gpt56_material']:
        for ref in (P/'music_work_since_1008v3_20261009/runs'/run/'prompts').glob(f'A-*__*__*__{w}__s*.txt'):
            parts=ref.stem.split('__')
            if parts[1] not in ['A_int_v1','A_web_v2'] or parts[2] not in ['gflash','gflash_web','luna','luna_noweb','gpt56w','gpt6w']:continue
            check('N02 historical',str(ref.relative_to(P)),Agen.render(parts[1],w)+work_meta.load(w).get('a_job_suffixes',{}).get(parts[2].replace('_web','').replace('_noweb','')+'-'+parts[0].split('-')[-1]+'-'+parts[4][1:],''),text(ref),ref)
for meta in (B/'gen_A/out').glob('*.meta.json'):
    data=json.loads(text(meta));ref=Path(data['job_directory'])/'prompt.txt'
    if ref.exists():check('N02 historical',meta.stem,Agen.render('A_int_v1' if '-int-' in data['name'] else 'A_web_v2','op61').rstrip(),text(ref),ref)
assert not blocked,blocked
(O/'comparison.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
from collections import Counter
print('COUNTS',Counter((r['group'],r['ok']) for r in rows))
print('prompts generated',len(allprompts),'differences',sum(not r['ok'] for r in rows))
