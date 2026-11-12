"""Adopt concrete scope criticisms without converting Center-last into a ban on an initial concern."""
import copy
import hashlib
import json
import evo
import node2b
import synth_v2

if __name__ == '__main__':
    src=json.loads((evo.ROOT/'evaluations/synth/C25editor3_op60/run.json').read_text(encoding='utf-8'))
    run=synth_v2.Run('C25editor4','op60','g6','C25pilot')
    run.state=copy.deepcopy(src['state'])
    texts={
        'S03':['亲近已经带来安慰，那份快乐仍可让他安静沉浸。可他已经舍不得这一刻结束，满足并没有使期待停止；他越想延续眼前的相伴，就越碰到不能由自己的喜欢决定的部分。急切因此会短暂冒出来，心意却找不到能让它安顿的确定。'],
        'S04':[
            '已经尝过亲近的快乐，又在其中碰到无法确定的部分，这一次的温柔才格外难舍。他并非只想比刚才更高兴，而是更想让这份亲近停留；偏偏越珍惜，越不能使时间停下，欢喜便带着急切和酸楚。',
            '想让亲近更长久的心意越强，他就越感到，仅凭此刻的热切，并不能让正在发生的好自行获得延续。情意可以充分显露，却不能因显露得充分就获得安稳，所以最热切的时候仍有哽住、悬而未决的一面。']}
    for sec,ts in texts.items():
        state=run.state[sec]
        for c,t in zip(state['chosen'],ts):c['text']=t
        state['pick']['chosen']=copy.deepcopy(state['chosen'])
        for c,t in zip(state['extra'],ts):c['text']=t
    h='经过前一段想延续亲近却碰到阻力的体验，充分显露心意也不能使眼前的好自行延续；因此第二次的热切不只更强，还与哽住、悬而未决同时存在。'
    run.state['S04']['hist'][1]['text']=h
    run.state['S04']['pick']['new_history'][1]['text']=h
    jobs=[];pending=[]
    for sec in ('S03','S04','S05'):
        pk=run.state[sec]['pick'];msg=run.check_msg(sec,pk)
        rid='editor4_'+sec+'_'+hashlib.sha256(msg.encode()).hexdigest()[:12]
        pending.append((sec,rid))
        if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'scope_revision','sec':sec},w='g6'))
    run.status='scope_revision_pending';run.save()
    evo.run_parallel(jobs,len(jobs) or 1)
    ok=True
    for sec,rid in pending:
        ck=synth_v2.judge_synth_v3.parse(evo.output(rid));errors=run.validate_check(sec,run.state[sec]['pick'],ck)
        ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
        ck['review_run']=rid
        if errors:ck['problems']=ck.get('problems',[])+errors
        run.state[sec]['check']=ck;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);ok=ok and ck['pass']
        print(sec,ck['pass'],ck.get('problems'),flush=True)
    run.status='needs_scope_revision'
    if ok:
        result=run.glob_check('S05');run.checkpoints['S05']=result
        run.status='pilot_passed:S05' if result.get('ok') else 'needs_global_revision:S05'
    run.save();print(run.status,flush=True)
