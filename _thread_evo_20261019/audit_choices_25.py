"""Complete the five-field selection audit for explicit editor-added candidates.
This is an acceptance stage, not retrospective attribution to the original drafts.
"""
import hashlib
import json
import sys
import evo
import node2b
import synth_v2

RULE='''你正在复核综合阶段的实际候选选择。新增候选明确由续作编辑提出，不是假称出自早期草稿。原池全部保留。
请对每一条候选逐项判断：解释了哪些当前听感；所需前提在History中是否成立（编号或缺什么）；是否虚构人物设定、前史、外部事件；能否随便放到别段；只是结果改名还是给出原因。
允许固定轻处境、当前心理起点与珠子之外的合理推导；不得把类比实化为具体对白、往事或事件。
再绝对核查当前选择：不是必须选池中唯一最优，但理由必须实际成立、有针对性，不能为机械逐颗覆盖堆心理步骤。若别的候选显示当前漏掉重大体验，判不合格。原稿另读法可以保留而不强并；不能因未选就删候选。判断必须基于完整文字，不擅自替作者删掉缺陷。
problems只填写足以否决当前选择的实质缺陷。非否决性的局限、措辞风险、未穷尽的相容读法另列limitations；改进建议另列suggestions。selection_acceptable为true时problems应为空，不可把明确非否决的内容混进其中。
只输出JSON：{"eval":[{"id":"M1","explains":["S01-B1"],"premise":"H编号或缺什么或初段当下起点","invented":"具体判断","any_segment":false,"result_only":false,"note":"具体价值及局限"}],"selection_acceptable":true,"problems":[],"reason":"具体理由"}。
'''

def audit(tag,work,secs=None):
    data=json.loads((evo.ROOT/f'evaluations/synth/{tag}_{work}/run.json').read_text(encoding='utf-8'))
    run=synth_v2.Run(tag,work,'g6',data.get('pool','C25whole'))
    # Serialized runs use pool_tag in some historical versions. Read the actual manifest directory.
    run.pool='C25pilot' if work=='op60' and tag.startswith('C25editor') else 'C25whole'
    run.state=data['state']
    jobs=[];pending=[]
    for sec in run.state:
        if secs and sec not in secs:continue
        msg=RULE+'\n【History】'+json.dumps(run.history(sec),ensure_ascii=False)+'\n【当前原始听感】'+run.bead_text(sec)+'\n【全部候选】'+run.mech_text(run.mechs(sec))+'\n【当前选择与去处】'+json.dumps(run.state[sec]['pick'],ensure_ascii=False)
        rid='audit_choice_'+work+'_'+sec+'_'+hashlib.sha256(msg.encode()).hexdigest()[:12]
        pending.append((sec,rid))
        if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'selection_five_field_audit','sec':sec,'work':work},w='g6'))
    evo.run_parallel(jobs,len(jobs) or 1)
    reports={}
    for sec,rid in pending:
        r=synth_v2.judge_synth_v3.parse(evo.output(rid))
        expected={m['id'] for m in run.mechs(sec)};es=r.get('eval',[])
        errors=[]
        if len(es)!=len(expected) or {m.get('id') for m in es}!=expected:errors.append('候选评估不完整或有重复')
        if any(not {'id','explains','premise','invented','any_segment','result_only','note'}<=set(m) for m in es):errors.append('五项候选判断不完整')
        bead_ids={b['id'] for b in run.beads if b['sec']==sec and b['role']!='演奏条件'}
        if any(not set(m.get('explains',[]))<=bead_ids for m in es):errors.append('候选评估引用其他段或未知听感')
        r['pass']=r.get('selection_acceptable') is True and not r.get('problems') and not errors
        r['schema_errors']=errors;r['review_run']=rid;reports[sec]=r
        print(sec,r['pass'],r.get('problems'),errors,flush=True)
    suffix='' if not secs else '_'+ '-'.join(secs)
    out=evo.ROOT/f'evaluations/continuation_20261025/choice_audit_{tag}_{work}{suffix}.json'
    synth_v2.dump(out,reports)
    return reports

if __name__=='__main__':audit(sys.argv[1],sys.argv[2],sys.argv[3:] or None)
