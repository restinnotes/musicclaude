"""Repair substantive non-regression failures, not merely the History summaries."""
import copy
import hashlib
import json
import evo
import node2b
import synth_v2

TEXTS={
 'S03':['相伴带来的安慰仍在，他可以安静沉浸，不急着去哪里。但正是已经得到的满足，使他想要的不只眼前这一刻；一想到延续，愿望又碰到不能由自己的喜欢决定的部分。急切会短暂地往前冒出，却找不到能落实的着落；想回到单纯享受，又放不下已经生出的需要，舒服之中才有持续拖住他的暗流。'],
 'S04':[
  '熟悉的温柔再次充满当下时，还能给他最初那种舒服，却带不走后来生出的延续愿望。第一次，他可以单凭正在发生的亲近安心；这一次，亲近越充分，越使那个超出当下的需要变得真切，他反而更难只安住眼前。温柔不再只是又一次满足，也使未获着落的需要更难放下，因此欢喜里多了迫切与酸楚。',
  '充分投入并不能使相伴更有保证，心意越热切，这个差距反而越清楚：想抓牢亲近，能增加的却只是自己的牵动，不能增加对延续的把握。越想靠此刻的好安顿自己，越被它不能代替的答案牵住，所以最明亮、最充分之处仍有失衡、哽住和退缩。'],
 'S05':[
  '初次相伴时，只要亲近正在发生，他就能安心；后来他开始需要它能够延续，最充分的投入却也没让这份需要获得着落。刚才的热切还使他整个人沉在相伴里，一从那阵充盈中露出来，便发现单是眼前的好已不能再像初次那样安顿自己，而继续加大自己的热切也补不上。他才突然独自承受起那个失去依靠的需要，空落下来。',
  '强烈沉浸所用的力气退下来，身体因而可以缓一口气；要让亲近继续的需要却没有解除。轻下来的是用力，并不是已经想通或不再牵挂，所以松动与孤单同时存在。']}
HISTORY={
 'S03':['最初的相伴仍能带来舒服，满足却已生出超出当下的延续愿望；它无法单凭自己的喜欢落实，也无法在回到享受时轻易放下，所以急切和持续的阻力同时存在。'],
 'S04':[
  '第二次亲近仍给得出最初的舒服，却也使已经生出的延续需要更加真切；眼前满足已不能完全容纳这个需要，因而这次的欢喜比第一次更迫切、更难舍。',
  '最充分的投入也未给延续以着落；越想抓牢，越发现只能增加自己的牵动、不能增加对相伴长留的把握，所以热切与失衡、哽住同在。'],
 'S05':[
  '从刚才的充盈中露出时，他发现最初足以安顿自己的当下亲近已不能承托超出当下的需要，而加大热切也补不上；原来的安顿方式失效，留下需要独自承受的空落。',
  '沉浸时的用力退下，身体得以缓气；牵挂并未解除，因此松动与孤单并存，不是想通后主动放下。']}

if __name__=='__main__':
 src=json.loads((evo.ROOT/'evaluations/synth/C25editor4_op60/run.json').read_text(encoding='utf-8'))
 run=synth_v2.Run('C25editor5','op60','g6','C25pilot');run.state=copy.deepcopy(src['state'])
 for sec,ts in TEXTS.items():
  st=run.state[sec]
  for c,t in zip(st['chosen'],ts):c['text']=t
  st['pick']['chosen']=copy.deepcopy(st['chosen'])
  for c,t in zip(st['extra'],ts):c['text']=t
  for c,t in zip(st['hist'],HISTORY[sec]):c['text']=t
  for c,t in zip(st['pick']['new_history'],HISTORY[sec]):c['text']=t
 jobs=[];pending=[]
 for sec in TEXTS:
  pk=run.state[sec]['pick'];msg=run.check_msg(sec,pk)
  rid='editor5_'+sec+'_'+hashlib.sha256(msg.encode()).hexdigest()[:12];pending.append((sec,rid))
  if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'non_regression_depth_repair','sec':sec},w='g6'))
 run.status='depth_revision_pending';run.save();evo.run_parallel(jobs,len(jobs) or 1)
 ok=True
 for sec,rid in pending:
  ck=synth_v2.judge_synth_v3.parse(evo.output(rid));errors=run.validate_check(sec,run.state[sec]['pick'],ck)
  ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
  ck['review_run']=rid
  if errors:ck['problems']=ck.get('problems',[])+errors
  run.state[sec]['check']=ck;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);ok=ok and ck['pass'];print(sec,ck['pass'],ck.get('problems'),flush=True)
 run.status='needs_depth_revision'
 if ok:
  result=run.glob_check('S05');run.checkpoints['S05']=result
  run.status='pilot_passed:S05' if result.get('ok') else 'needs_global_revision:S05'
 run.save();print(run.status,flush=True)
