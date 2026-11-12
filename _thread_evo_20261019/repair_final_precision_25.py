"""Restore independently identified content; never alter historical reviews."""
import copy,json,hashlib
import finish_thread_25 as f
import evo,synth_v2

key='C25whole60_op60'
p=f.OUT/(key+'_plain.json')
backup=f.OUT/(key+'_plain_before_final_precision.json')
if backup.exists():raise ValueError('Already applied')
raw=p.read_bytes();backup.write_bytes(raw)
g=json.loads(raw);ix={i['id']:i for s in g['segments'] for i in s['items']}
changes=[]
for iid,text in {
 'I15':'先前即使已想延续，眼前亲近仍能暂时安定；如今越充分，延续需要越真切，反而难安住眼前。',
 'I31':'热切退下后，他更清楚自己仍想亲近对方；能独自快乐，并没有消除安静里的拉扯。',
 'I60':'此前越想充分表明心意、越因无法保证以后而哽住的热切，此刻部分释放，以后仍无答案。',
 'I64':'眼前的好已多于原先索求的一个答案，心思才不再只绕着自己的所得，而被丰盛吸引。',
 'I66':'眼前越丰盛越难放开，狂喜里同时有恳求与心疼，几乎分不清想笑还是想哭。',
}.items():
 changes.append({'id':iid,'before':ix[iid]['text'],'after':text});ix[iid]['text']=text
ix['I66']['explains']=['S12-B2','S12-B3']
removed=[]
drop={('I5','I15'),('I7','I17'),('I29','I36'),('I6','I37'),('I49','I51'),('I49','I64'),('I68','I69')}
for s in g['segments']:
 keep=[]
 for a in s['because']:
  if (a['from'],a['to']) in drop:removed.append({'sec':s['sec'],**a})
  else:keep.append(a)
 s['because']=keep
next(s for s in g['segments'] if s['sec']=='S07')['because'].extend([
 {'from':'I5','to':'I36','rel':'提供理由','how':'相伴曾使谨慎暂松，构成这里已经体验过安稳的实际前提。'},
 {'from':'I28','to':'I36','rel':'提供理由','how':'独自也能体会温柔，是与相伴安稳同时带到这里的另一种真实经验。'}])
next(s for s in g['segments'] if s['sec']=='S13')['because'].append(
 {'from':'I34','to':'I69','rel':'提供理由','how':'温柔早已积成舍不得抽身的热度；满足确实来到，也不会立即消去这份依恋。'})
source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
f.validate(g,source);synth_v2.dump(p,g)
synth_v2.dump(f.OUT/(key+'_final_precision_receipt.json'),{
 'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'restored':changes,'removed_arrows':removed,
 'main_disposition':'Adopt specific lost increments from the late independent review. Do not adopt cross-work scope errors, paraphrase-only reading of 改写, forced insertion of alternatives, or follows for mere references. All raw verdicts preserved.',
 'S12_B2':'I63/I64 preserve value beyond personal gain; I66 jointly carries ecstatic joy and painful pleading without inventing an actual reunion, embrace, tears, or laughter.',
 'source_unchanged':True,'center_basis_unchanged':True})
print('final precision repaired',len(changes),'texts;',len(removed),'arrows removed')
