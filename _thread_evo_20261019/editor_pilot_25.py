"""Agent-authored alternative pilot. Added explanations are explicit, never attributed to old drafts.
Five provisional sections are written in order. Independent checks run in parallel, but acceptance
is atomic and requires every predecessor, every local check and the global check to pass.
"""
import json
import sys
import evo
import node2b
import synth_v2

TEXTS=[
    ['亲近刚刚触动他，他还没弄清自己盼望的究竟是什么。但这份在乎已经让他无法轻率地认定眼前的一切；越感到它有分量，就越谨慎，心意向前去了，人却还不能安心。'],
    ['眼下的相伴让他真切感到，亲近不只是一个尚未落实的愿望。可以安静待在一起而不必急着确认什么，先前的谨慎才暂时松开；正因为已经尝到这份自在，他又舍不得它随时间过去。',
     '越来越愿意亲近，使他的热切一时收不住；但他所珍惜的也包括两个人安静相处的自在，所以心意显露之后，仍愿停在这份温柔里，不急着索取一个确定的结果。'],
    ['亲近已经带来安慰，即使暂时没有新的表示，那份快乐也仍可让他安静沉浸。可他已经舍不得这一刻结束，满足并没有使期待停止；他越想延续眼前的相伴，就越碰到不能由自己的喜欢决定的部分。急切因此会短暂冒出来，心意却找不到能让它安顿的确定。'],
    ['已经尝过亲近的快乐，又在其中碰到无法确定的部分，这一次的温柔才格外难舍。他并非只想比刚才更高兴，而是更想让这份亲近停留；偏偏越珍惜，越不能使时间停下，欢喜便带着急切和酸楚。',
     '想让亲近更长久的心意越强，他就越感到自己的深情不能替两个人把以后确定下来。情意可以充分显露，却不能因显露得充分就获得安稳，所以最热切的时候仍有哽住、悬而未决的一面。'],
    ['刚才热切的相伴已使他不只想得到片刻安慰，还盼它能够继续。可那阵激动退去，想留住它的需要并没有一同退去；原先正在发生的温柔暂时不能再把他整个托住，他才忽然独自承受起这份需要，感到空落、没有依靠。',
     '强烈的激动退下来，也让他终于能缓一口气。这份松动和孤单可以同时存在：轻下来的是刚才的用力，仍放不下的是亲近能否继续。']
]
EXPLAINS=[
    [['S01-B1','S01-B2','S01-B3']],
    [['S02-B1','S02-B2','S02-B4'],['S02-B5']],
    [['S03-B1','S03-B2','S03-B3']],
    [['S04-B1','S04-B3','S04-B4'],['S04-B2']],
    [['S05-B1','S05-B2'],['S05-B3']]
]
DEPENDS=[[],['H1'],['H2'],['H2','H3','H4'],['H4','H5','H6']]
HISTORY=[
    ['亲近已使他在乎，分量越重就越不能轻率认定眼前的一切；他仍说不清这份期待的具体去向。'],
    ['相伴给了他真切的自在和安慰；他已经舍不得这段时间过去。','他愿意让心意显露，也珍惜不必急于确认结果的安静相伴。'],
    ['亲近的快乐仍能安慰他，但想延续这份相伴的期待碰到自己无法决定的部分，使舒服中同时有急切与阻力。'],
    ['再次体验亲近时，先前的安慰与不确定使它更可珍惜，想留住它的愿望更急切。','充分显露心意并不能使以后确定；热切之中仍有悬而未决。'],
    ['相伴的激动暂时退去，但希望亲近继续的需要仍在，他因缺少同样充分的安慰而空落。','激动的减弱让他缓一口气，却没有解除依恋；松动与孤单同时存在。']
]

if __name__=='__main__':
    run=synth_v2.Run('C25editor2' if '--seed-first' in sys.argv else 'C25editor','op60','g6','C25pilot')
    jobs=[];provisional=[]
    for i,texts in enumerate(TEXTS):
        sec=f'S{i+1:02}';base=run.mechs(sec)
        if i==0 and '--seed-first' in sys.argv:
            state=json.loads((evo.ROOT/'evaluations/synth/C25a_op60/S01.json').read_text(encoding='utf-8'))
            if not state['check'].get('pass'): raise ValueError('seed first section is not accepted')
            state['provenance']='C25a S01: g6 author selected M3, checked by calibrated g6; all later provisional sections rechecked with this exact History.'
            run.state[sec]=state
            provisional.append((sec,state['pick'],None))
            continue
        additions=[{'id':f'G25_{n}','text':t,'premise':' + '.join(DEPENDS[i]) or '初段当下处境，无前史',
                    'explains':EXPLAINS[i][n-1],'added':True,'author':'Codex continuation editor',
                    'why_added':'原候选没有完整承担本段相容体验，按综合阶段定向补候选；不归到旧稿名下。'}
                   for n,t in enumerate(texts,1)]
        run.state[sec]={'extra':additions}
        chosen=[{'text':t,'from':[f'G25_{n}'],'depends':DEPENDS[i],'explains':EXPLAINS[i][n-1]} for n,t in enumerate(texts,1)]
        pk={'eval':[{'id':m['id'],'note':'保留原候选供复查，采用下列明确新增机制；本轮不声称所有原候选均不合格。'} for m in base]+[{'id':m['id'],'note':m['why_added']} for m in additions],
            'chosen':chosen,'fate':{b:f'第{n}条' for n,ids in enumerate(EXPLAINS[i],1) for b in ids},
            'new_history':[{'text':t,'explains':EXPLAINS[i][n]} for n,t in enumerate(HISTORY[i])], 'conditional':[]}
        prompt=run.check_msg(sec,pk)
        # All earlier items are provisional. Every review independently sees their original evidence.
        prompt+='\n本轮所有前段都是暂定稿，并非已经验收的事实；请严格核对前段是否支持当前依赖。任何一段失败，依赖它的后段都不能作为成品接受。'
        import hashlib
        digest=hashlib.sha256(prompt.encode()).hexdigest()[:12]
        rid=f'editor25_{sec}_{digest}'
        provisional.append((sec,pk,rid))
        if not evo.done(rid):jobs.append(node2b.job(rid,prompt,{'stage':'agent_editor_pilot','sec':sec},w='g6'))
        run.commit(sec,pk,{'pass':False,'provisional':True})
    run.status='provisional_checks_pending';run.save()
    evo.run_parallel(jobs,len(jobs) or 1)
    all_ok=True
    for sec,pk,rid in provisional:
        ck=run.state[sec]['check'] if rid is None else synth_v2.judge_synth_v3.parse(evo.output(rid))
        errors=run.validate_check(sec,pk,ck)
        ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not errors and not ck.get('problems')
        if errors:ck['problems']=ck.get('problems',[])+errors
        ck['review_run']=rid
        run.state[sec]['check']=ck
        synth_v2.dump(run.dir/f'{sec}.json',run.state[sec])
        all_ok=all_ok and ck['pass']
        print(sec,ck['pass'],ck.get('problems'),flush=True)
    run.status='needs_editor_revision'
    if all_ok:
        glob=run.glob_check('S05');run.checkpoints['S05']=glob
        run.status='pilot_passed:S05' if glob.get('ok') else 'needs_global_revision:S05'
    run.save();print(run.status,flush=True)
