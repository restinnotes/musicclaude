"""Extend an accepted 1–110 trial through the actual ending; do not erase the achieved fulfillment."""
import copy
import json
import sys
import evo
import synth_v2

if __name__=='__main__':
 src=json.loads((evo.ROOT/f'evaluations/synth/{sys.argv[1]}_op60/run.json').read_text(encoding='utf-8'))
 if src['status']!='middle_passed:S13':raise ValueError('middle trial pending')
 run=synth_v2.Run('C25whole60','op60','g6','C25whole');run.state=copy.deepcopy(src['state']);run.checkpoints=copy.deepcopy(src['checkpoints'])
 sec='S14';entries=[
  ('刚才充分得到的幸福，不会因为身体渐渐平静就变得不真实；已经经历过的亲近、独自仍能感到的快乐，也不必靠持续激动才能保住它们的分量。长久积起的力量终于能够退下，温暖与回望还在，却不再只剩下舍不得停住的冲动。',['S14-B2','S14-B3']),
  ('开头还只是慎重而悬着的期待，如今已有一整段真实体验可以承接：亲近的满足确实发生过，连没有直接安慰时，喜欢也曾在心里继续。以后仍不能保证，却已不能把这一切说成尚未得到的可能；这一刻因此有了可以明确结束的分量，无需把结束拖成期待，也无需以永久保证来证明它曾经真实。',['S14-B1','S14-B4'])]
 deps=['H1','H2','H9','H11','H17','H20','H21','H22','H23']
 run.state[sec]={'extra':[{'id':f'G25e_{i}','text':t,'premise':','.join(deps),'explains':bs,'added':True,'author':'Codex continuation editor','why_added':'以真实达到的满足解释尾声，不写实际起身关门事件。'} for i,(t,bs) in enumerate(entries,1)]}
 pk={'eval':[{'id':m['id'],'note':'保留候选，完整五项候选评估单独复核。'} for m in run.mechs(sec)],
  'chosen':[{'text':t,'from':[f'G25e_{i}'],'depends':deps,'explains':bs} for i,(t,bs) in enumerate(entries,1)],
  'fate':{b:f'第{i}条' for i,(_,bs) in enumerate(entries,1) for b in bs},
  'new_history':[{'text':t,'explains':bs} for t,bs in entries],'conditional':[]}
 run.commit(sec,pk,{'pass':False,'provisional':True});run.status='ending_provisional';run.save()
 msg=run.check_msg(sec,pk);ck=run.call(sec+'_B',msg,'g6',{'sec':sec})
 errors=run.validate_check(sec,pk,ck)
 ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
 if errors:ck['problems']=ck.get('problems',[])+errors
 run.state[sec]['check']=ck;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);run.status='needs_ending_revision'
 if ck['pass']:
  r=run.glob_check(sec);run.checkpoints[sec]=r;run.status='whole_local_global_passed' if r.get('ok') else 'needs_whole_global_revision'
 run.save();print(run.status,json.dumps(ck.get('problems'),ensure_ascii=False),flush=True)
