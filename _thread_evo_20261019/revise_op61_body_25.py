"""Repair the independently identified distinction between rumination and bodily temporal pressure.
The new facet is local: no new downstream premise is introduced. Exact downstream checker inputs
are compared, not assumed unchanged. Global checks are repeated because the full selected story changes.
"""
import copy
import json
from concurrent.futures import ThreadPoolExecutor
import evo
import synth_v2

if __name__=='__main__':
 src=json.loads((evo.ROOT/'evaluations/synth/C25op61classified_op61/run.json').read_text(encoding='utf-8'))
 old=synth_v2.Run('C25op61classified','op61','g6','C25whole');old.state=copy.deepcopy(src['state'])
 run=synth_v2.Run('C25op61body','op61','g6','C25whole');run.state=copy.deepcopy(src['state']);run.checkpoints=copy.deepcopy(src['checkpoints'])
 sec='S04';st=run.state[sec]
 text='前一段才让他重新感到生活曾可以轻松、亲近，此刻这份温暖又如此鲜活，能停留其中的时间却不由他。过去已经回不来，连眼下重新感到的亲近也还在经过；他越舍不得它消散，越感到自己正被时间带走，身体先紧起来，仿佛还没来得及停留就已不得不向前。这股催迫不必等到反复自问才出现。'
 candidate={'id':'G25q_3','text':text,'premise':'H2：过去不能变为现在；H7：刚重新感到轻松、亲近，却更痛感与眼前的距离。','explains':['S04-B3'],'added':True,'author':'Codex continuation editor','why_added':'独立候选复核指出B3的身体时间压力被B4的心理盘旋吞并；补当下机制，不造身体奔跑事件或新前史。'}
 st['extra'].append(candidate)
 st['chosen'][1]['explains']=['S04-B2','S04-B4']
 st['chosen'].append({'text':text,'from':['G25q_3'],'depends':['H2','H7'],'explains':['S04-B3']})
 st['pick']['chosen']=copy.deepcopy(st['chosen']);st['pick']['fate']['S04-B3']='第3条：身体感到眼下这份亲近也在被时间带走，不等于脑中反复追问没有结果；不是实际奔跑或新发生的外部事件。'
 st['pick']['eval'].append({'id':'G25q_3','explains':['S04-B3'],'premise':candidate['premise'],'invented':'无新外部事件或具体往事；身体催迫是当下对美好仍在经过的反应。','any_segment':False,'result_only':False,'note':'温暖刚重新鲜活且过去不能回来，使此刻可停留的时间更迫切；区别于找替代结果的反刍。仍需独立复核。'})
 st['local_supplement_scope']='第三条补足本段身体侧面，保留前述回忆与反刍所建立的原有History；不把每个并存感受都变成推动未来的新增心理步骤。'
 unchanged=[]
 for later in [f'S{i:02}' for i in range(5,14)]:
  if old.check_msg(later,old.state[later]['pick'])!=run.check_msg(later,run.state[later]['pick']):raise ValueError('downstream checker input changed: '+later)
  unchanged.append(later)
 st['check']={'pass':False,'provisional':True}
 run.status='bodily_pressure_revision_pending';run.save()
 ck=run.call('S04_B',run.check_msg('S04',st['pick']),'g6',{'sec':'S04'})
 errors=run.validate_check('S04',st['pick'],ck)
 ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
 if errors:ck['problems']=ck.get('problems',[])+errors
 st['check']=ck;synth_v2.dump(run.dir/'S04.json',st)
 run.status='needs_bodily_pressure_revision'
 if ck['pass']:
  with ThreadPoolExecutor(max_workers=3) as ex:rs=list(ex.map(run.glob_check,('S07','S11','S13')))
  for point,result in zip(('S07','S11','S13'),rs):run.checkpoints[point]=result
  run.status='op61_global_passed' if all(r.get('ok') for r in rs) else 'needs_body_global_revision'
 run.dependency_precision={'unchanged_downstream_checker_inputs':unchanged,'reason':'选中的下游解释、所读History、原始依据及提示逐字相同，故原检查按相同输入复用；新全局关系另重查。'}
 run.save()
 # save() intentionally keeps the runtime schema stable; this receipt is separate.
 synth_v2.dump(run.dir/'dependency_reuse_receipt.json',run.dependency_precision)
 print(run.status,json.dumps(ck.get('problems'),ensure_ascii=False),flush=True)
