"""Persist the independently explained bodily facet, and recheck every changed context."""
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import evo
import synth_v2

if __name__=='__main__':
    src=json.loads((evo.ROOT/'evaluations/synth/C25op61body_op61/run.json').read_text(encoding='utf-8'))
    run=synth_v2.Run('C25op61body2','op61','g6','C25whole')
    run.state=copy.deepcopy(src['state']);run.checkpoints={'S03':copy.deepcopy(src['checkpoints']['S03'])}
    st=run.state['S04']
    st['hist'][1]['explains']=['S04-B2','S04-B4']
    body=st['chosen'][2]
    st['hist'].append({'id':'H9b','sec':'S04','text':body['text'],'explains':['S04-B3']})
    st['pick']['new_history']=[{k:h[k] for k in ('text','explains')} for h in st['hist']]
    st['local_supplement_scope']='身体侧面的独立原因完整写入H9b；H9仅承担反刍。后续全部实际检查输入已改变，逐段重新检查，不复用旧结论。原有历史ID保留，防止不必要的引用错位。'
    run.status='bodily_pressure_history_revision_pending'
    for i in range(4,14):run.state[f'S{i:02}']['check']={'pass':False,'provisional':True}
    run.save()
    def local(sec):
        s=run.state[sec]
        ck=run.call(sec+'_B',run.check_msg(sec,s['pick']),'g6',{'sec':sec,'step':'history-recheck'})
        errors=run.validate_check(sec,s['pick'],ck)
        ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
        if errors:ck['problems']=ck.get('problems',[])+errors
        return ck
    # All these reviews read the same fully specified provisional story. Acceptance waits for all.
    with ThreadPoolExecutor(max_workers=13) as ex:
        fs={ex.submit(local,f'S{i:02}'):('local',f'S{i:02}') for i in range(4,14)}
        fs.update({ex.submit(run.glob_check,s):('global',s) for s in ('S07','S11','S13')})
        for f in as_completed(fs):
            kind,sec=fs[f];r=f.result()
            if kind=='local':
                run.state[sec]['check']=r;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec])
                print(sec,r['pass'],json.dumps(r.get('problems',[]),ensure_ascii=False),flush=True)
            else:run.checkpoints[sec]=r
            run.save()
    good=all(s['check'].get('pass') for s in run.state.values()) and all(g.get('ok') and not g.get('problems') for g in run.checkpoints.values())
    run.status='op61_global_passed' if good else 'needs_history_revision'
    run.save()
    synth_v2.dump(run.dir/'dependency_recheck_receipt.json',{'new_history':'H9b: S04 bodily temporal pressure independent of rumination','rechecked_local':list(run.state)[3:],'rechecked_global':['S07','S11','S13'],'unchanged_prefix':['S01','S02','S03'],'earlier_failed_versions_preserved':['C25op61classified','C25op61body']})
    print(run.status,flush=True)
