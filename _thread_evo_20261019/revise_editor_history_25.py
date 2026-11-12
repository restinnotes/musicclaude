"""Repair provenance and causal History summaries; keep original results and check actual changed sections."""
import copy
import hashlib
import json
import evo
import node2b
import synth_v2

if __name__=='__main__':
    before=json.loads((evo.ROOT/'evaluations/synth/C25editor2_op60/run.json').read_text(encoding='utf-8'))
    run=synth_v2.Run('C25editor3','op60','g6','C25pilot');run.state=copy.deepcopy(before['state'])
    run.state['S03']['pick']['chosen'][0]['depends']=['H1','H2']
    run.state['S03']['chosen']=run.state['S03']['pick']['chosen']
    changes={
      'S04':[
       '最初的亲近使他放松，随后的不确定却使他知道仅仅喜欢不能让相伴长留；再次享受亲近时，安慰与这份警觉一同在场，因而比初次更舍不得、更急切。',
       '他的心意已比先前更充分地显露，但自己的深情不能独自把两个人的以后确定下来，所以热切之中仍然悬着。'],
      'S05':[
       '想让亲近继续的需要仍在，眼前直接而充分的温柔却暂时不再给他同样的安慰；他突然独自承受起原先被温柔包裹的需要，因此空落、没有依靠。',
       '此前抓紧当下的强烈用力退下来，使他能缓一口气；希望亲近继续的牵挂并没有解除，所以松动与孤单同时存在。']}
    for sec,texts in changes.items():
        for h,t in zip(run.state[sec]['hist'],texts):h['text']=t
        for h,t in zip(run.state[sec]['pick']['new_history'],texts):h['text']=t
    jobs=[];inputs=[]
    for sec in ('S03','S04','S05'):
        pk=run.state[sec]['pick'];msg=run.check_msg(sec,pk)
        digest=hashlib.sha256(msg.encode()).hexdigest()[:12];rid=f'editor3_{sec}_{digest}'
        inputs.append((sec,rid))
        if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'history_summary_repair','sec':sec},w='g6'))
    run.status='history_revision_pending';run.save()
    evo.run_parallel(jobs,len(jobs) or 1)
    ok=True
    for sec,rid in inputs:
        pk=run.state[sec]['pick'];ck=synth_v2.judge_synth_v3.parse(evo.output(rid));errors=run.validate_check(sec,pk,ck)
        ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
        ck['review_run']=rid
        if errors:ck['problems']=ck.get('problems',[])+errors
        run.state[sec]['check']=ck;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);ok=ok and ck['pass']
        print(sec,ck['pass'],ck.get('problems'),flush=True)
    run.status='needs_history_revision'
    if ok:
        result=run.glob_check('S05');run.checkpoints['S05']=result
        run.status='pilot_passed:S05' if result.get('ok') else 'needs_global_revision:S05'
    run.save();print(run.status,flush=True)
