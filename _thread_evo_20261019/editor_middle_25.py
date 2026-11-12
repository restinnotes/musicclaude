"""Conditional 40–110 continuation. Only starts after the first pilot and non-regression gate.
Every proposal is a marked new synthesis candidate, not an alleged quotation from a source draft.
Written in order using only the preceding provisional History; checked as an atomic trial.
"""
import copy
import hashlib
import json
import sys
import evo
import node2b
import synth_v2

ROWS=[
 ('S06',[
  ('刚才失去的是被眼前温柔包围的安稳，已经得到的美好却仍留在他心里。亲近此刻不能给他同样的安慰，它留下的余温却仍会使他快乐；这时他能够独自体会它细小、清澈的好。这与有人托住自己的快乐不同：快乐已成为自己的感受，也因此带着别人无法完全陪同的孤单。',['S06-B1','S06-B3']),
  ('牵挂并没有因这份安静而消失。正因为不再被刚才的热切填满，他更能感到温柔怎样留在自己身上，也更清楚自己仍想亲近那个人；能独自感到美好，并不等于已经不再需要相伴，所以安静仍有拉扯。',['S06-B2'])],['H2','H4','H7','H8']),
 ('S07',[
  ('独自体会亲近留下的温柔，并没有使他远离那个人。那份快乐越真切，身体也越记得相伴曾带来的满足，想要再次靠近的愿望因此更直接。先前可以安静回味的感受，此刻变成舍不得抽身的热度；沉浸本身就有快感，又使他难以只停在回味里。',['S07-B1','S07-B2']),
  ('这一次的热切已经包含两种真实经验：相伴会让人安稳，独自回味也会令人快乐。可不论哪一种，都不能让眼前的时间停住；他并未失去美好，却已经舍不得它正在过去。',['S07-B3'])],['H2','H7','H9','H10']),
 ('S08',[
  ('他已经真切尝到，相伴之外，单是心里仍能这样喜欢、身体仍能这样感到快乐，也有自己的幸福。于是此刻的舒畅不必等到关系的以后有了保证才成立；正在鲜活地喜欢与被生活触动，就足以使他高兴，连先前的急切也有了轻盈和玩心。',['S08-B1','S08-B2']),
  ('这份轻快不是从未有过牵挂的无忧。他已经经历过热情退后、温柔留在心里的时候，所以快乐尚未散尽，就知道自己还会想念此刻；正在享受和已经不舍，不必先后发生。',['S08-B3'])],['H9','H10','H11','H12']),
 ('S09',[
  ('刚才的快乐曾让他暂时不再等待保证，如今热度仍在，却没有一个已经确定、能够继续抵达的结果。不是那份喜悦突然变假，而是他还想继续，又不能凭刚才的尽兴替下一刻作答；向前的冲动便凝在这里，注意反而更集中，心里仍有未落定的余响。',['S09-B1','S09-B2','S09-B3']),
  ('不过，独自感到温柔、又能如此尽兴的经历已经说明，值得珍惜的并不只有自己得到多少亲近。那个人的存在、已经共同度过的时刻、自己仍能感到的快乐，都不因疑问未解而失去价值；渴望虽还悬着，暂时也不再占满全部心思。',['S09-B4'])],['H1','H9','H11','H13','H14']),
 ('S10',[
  ('亲近的以后仍没有答案，已经经历过的相伴、想念与快乐却都是真的。刚才那阵安静没有抹去它们，反而让它们不再只围着一个尚未确定的结果打转；这些已经存在的美好本身就能打动他，心里的热切因此不必一直绷成索求，身体也跟着松开。轻下来的不是在乎，而是非得先有保证才能安心感受的负担。',['S10-B1','S10-B3','S10-B4'])],['H2','H9','H13','H15','H16']),
 ('S11',[
  ('熟悉的亲近再次真切起来时，他已有过失去直接安慰的空落，也有过独自仍能快乐的经验。因此同样的温柔不再独自承担替他保证全部幸福的任务，他能更充分地投入；但正因这些经历都在，温柔也承受着舍不得与心疼，浓烈到几乎难以容下。',['S11-B1','S11-B2','S11-B3']),
  ('24–34时，他越想把心意充分表明，越因这不能保证以后而哽住。如今他已经经历过，不先得到保证也能真切地快乐，所以充分感受自己的深情本身就有了价值；此前被“能否长久”悬住的一部分热切，终于获得释放。这还没有替关系的以后作答。',['S11-B4'])],['H5','H6','H7','H9','H13','H17']),
 ('S12',[
  ('最初有人相伴、使心安稳的幸福，与40–61以来独自在心里仍能感到的鲜活快乐，此刻一同充满这份重新真切的亲近。亲近不再只负责使他安心，独自的快乐也不再只是心里的余温；他感到那个人本身、共同经历的时间、自己仍能鲜活地喜欢，都有不能被一个结果替代的分量。眼前正在经历的好已经多于原先索求的一个答案，心思才不再围着自己得到多少打转，整个人都被这份丰盛吸引。',['S12-B1','S12-B2']),
  ('可是能在此刻如此充分地感受，并不等于以后也已确定。先前想延续相伴的期待还在，越丰盛就越难轻轻放开，欢喜中仍有恳求与牵扯；直到这份情感真正充分地展开，悬着的力量才得到释放。得到的是此刻充分经历这份幸福，并不是从此没有不舍。',['S12-B3'])],['H2','H5','H9','H11','H13','H16','H17','H18','H19']),
 ('S13',[
  ('刚刚充分经历的幸福已经真实得到，长久积起的依恋却不会在得到的瞬间一同平息。40–61时尚可独自慢慢回味的温柔，如今和眼前充分的亲近一起涌来；身体仍被这份分量牵动，越感到刚才确实抵达，越舍不得让它就此过去，所以释放之后仍止不住地向前。',['S13-B1','S13-B3']),
  ('亲近与自己的深情都如此真切，才更使他感到，任何一份真切都不能替时间和另一个人决定以后。悲伤从已经得到的幸福内部生出来，并不推翻它；能够尽情感受的满足还在，不能把这一刻永远留下的酸楚也在，两者都无法被轻轻带过。',['S13-B2','S13-B4'])],['H1','H9','H11','H18','H19','H20','H21'])
]

if __name__=='__main__':
    seedtag=sys.argv[1]
    seed=json.loads((evo.ROOT/f'evaluations/synth/{seedtag}_op60/run.json').read_text(encoding='utf-8'))
    if seed['status']!='pilot_passed:S05':raise ValueError('first pilot has not passed its local/global gate')
    # Main agent must explicitly pass the accepted pilot review file after reading its reasons.
    gate=json.loads((evo.ROOT/sys.argv[2]).read_text(encoding='utf-8'))
    if gate.get('decision')!='accept':raise ValueError('non-regression gate not accepted')
    run=synth_v2.Run('C25middle','op60','g6','C25whole')
    for sec,state in seed['state'].items():
        a=json.loads((synth_v2.synth.POOL/'C25pilot/op60'/f'{sec}.json').read_text(encoding='utf-8'))
        b=json.loads((synth_v2.synth.POOL/'C25whole/op60'/f'{sec}.json').read_text(encoding='utf-8'))
        if a['source_hash']!=b['source_hash']:raise ValueError('seed pool changed')
        run.state[sec]=copy.deepcopy(state)
    run.checkpoints=copy.deepcopy(seed['checkpoints']);jobs=[];inputs=[]
    for sec,entries,deps in ROWS:
        base=run.mechs(sec)
        extra=[{'id':f'G25m_{i}','text':t,'premise':','.join(deps),'explains':ids,'added':True,
                'author':'Codex continuation editor','why_added':'按已选历史补充局部候选；明确新增，不假称来自旧稿。'} for i,(t,ids) in enumerate(entries,1)]
        run.state[sec]={'extra':extra}
        chosen=[{'text':t,'from':[f'G25m_{i}'],'depends':deps,'explains':ids} for i,(t,ids) in enumerate(entries,1)]
        pk={'eval':[{'id':m['id'],'note':'原候选永久保留；此处另写明确新增解释，不以未选中为删除理由。'} for m in base+extra],
            'chosen':chosen,'fate':{bid:f'第{i}条' for i,(_,ids) in enumerate(entries,1) for bid in ids},
            'new_history':[{'text':t,'explains':ids} for t,ids in entries],'conditional':[]}
        if sec=='S06':pk['fate']['S06-B4']='另一种听法：本轮采用欲望热度暂退、独自体会余温的理解；保留更贴身的感官沉醉读法，不把它强并进此刻已经安静的心理状态。'
        if sec=='S10':pk['fate']['S10-B2']='独立保留：轻细明亮的音响和意象仍有其感受价值，当前的舒展机制与之相容；不把每一串音符或细雨比喻另编成心理事件。'
        msg=run.check_msg(sec,pk)+'\n前段均为暂定稿，请连同原始依据核查。任何前段失败，下游不能作为成品接受。'
        digest=hashlib.sha256(msg.encode()).hexdigest()[:12];rid=f'editor_mid_{sec}_{digest}'
        inputs.append((sec,pk,rid))
        if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'middle_atomic_trial','sec':sec},w='g6'))
        run.commit(sec,pk,{'pass':False,'provisional':True})
    run.status='middle_provisional';run.save()
    evo.run_parallel(jobs,len(jobs) or 1)
    ok=True
    for sec,pk,rid in inputs:
        ck=synth_v2.judge_synth_v3.parse(evo.output(rid));errors=run.validate_check(sec,pk,ck)
        ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
        if errors:ck['problems']=ck.get('problems',[])+errors
        ck['review_run']=rid;run.state[sec]['check']=ck
        synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);ok=ok and ck['pass']
        print(sec,ck['pass'],ck.get('problems'),flush=True)
    run.status='needs_middle_revision'
    if ok:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as ex:
            results=list(ex.map(run.glob_check,('S08','S11','S13')))
        for sec,result in zip(('S08','S11','S13'),results):run.checkpoints[sec]=result
        run.status='middle_passed:S13' if all(r.get('ok') for r in results) else 'needs_middle_global_revision'
    run.save();print(run.status,flush=True)
