"""Advisory gap diagnosis. It cannot establish or change the eventual selected History."""
import hashlib
import json
import evo
import node2b
import judge_synth_v3 as judge

RULES='''下面是音乐 Thread 新稿池在两位评委严格口径下仍未共同覆盖的听感。请逐颗复核，不能用覆盖率已经进步掩盖真实缺口。
最终 Thread 是一件持续发生的事；多篇全曲稿只提供候选，之后才依据已选历史逐段综合。现在尚无选定历史，因此不要编出一条确定前史来宣称缺口已经解决。
每颗先读原文和现有稿的解释，再判主要属于：池子太窄 / 可以独立保留 / 替代听法 / 珠子本身存疑。写具体理由、现有稿究竟缺了什么。若依赖未来历史选择，注明暂定。
一条珠子里可同时成立的感受要保留，不能将难解释的自动当互斥；角色标签不是重要性排序。原文明确只是音乐材料辨认、或声音比喻的部分，不要强行把它变成心理剧情。时间、记忆和失去的性质可以是心理处境，但不得增补真实往事或事件。
Thread 要解释感受，不能要求复述音响、意象和具体对白。若某种感受在原文属主体验或重要的同时层面，独立保留不足以过关，要指出。给出综合时该如何验收、何时必须退回或补缺；此处不能给候选打虚假通过标签。
只输出JSON：{"gaps":[{"id":"S01-B3","category":"池子太窄","provisional":true,"important":true,"why":"具体判断","missing":"缺什么","acceptance":"综合时怎么检查"}],"overall":"真实缺口和替代读法的区别"}。
'''

if __name__=='__main__':
    source=json.loads((evo.ROOT/'evaluations/continuation_20261025/coverage_audit.json').read_text(encoding='utf-8'))
    inputs=[];jobs=[]
    for work in ('op61',):
        gaps=[{'bead':g['bead'],'examples':g['disagreements'][:3]} for g in source[work]['gaps']]
        msg=RULES+'\n'+json.dumps(gaps,ensure_ascii=False)
        digest=hashlib.sha256(msg.encode()).hexdigest()[:12]
        for mdl in ('g6','g56'):
            rid=f'gap25_{work}_{mdl}_{digest}';inputs.append((work,mdl,rid))
            if not evo.done(rid): jobs.append(node2b.job(rid,msg,{'stage':'gap_diagnosis','work':work},w=mdl))
    evo.run_parallel(jobs,len(jobs) or 1)
    report=[]
    for work,mdl,rid in inputs:
        report.append({'work':work,'judge':mdl,'run':rid,'result':judge.parse(evo.output(rid))})
    (evo.ROOT/'evaluations/continuation_20261025/gap_diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in report:
        print(row['work'],row['judge'],json.dumps(row['result'],ensure_ascii=False),flush=True)
