"""Blind validation of direct usability; old incomplete positive remains a diagnostic, not relabeled."""
import hashlib
import json
import calib_synth_v3 as prior
import judge_synth_v3 as judge
import synth
import evo
import node2b


if __name__=='__main__':
    run=synth.Run('calib4','op60','g6','none');jobs=[];inputs=[]
    for key,sec,hist,text,want in prior.cases():
        msg=judge.message('op60',sec,hist,[{'text':text}],run.bead_text(sec))
        digest=hashlib.sha256(msg.encode()).hexdigest()[:12]
        for mdl in ('g6','g56'):
            rid=f'cs4_{key}_{mdl}_{digest}'
            inputs.append((key,mdl,rid,want))
            if not evo.done(rid): jobs.append(node2b.job(rid,msg,{'stage':'calib_synth_v4','case':key},w=mdl))
    evo.run_parallel(jobs,len(jobs) or 1)
    report=[]
    for key,mdl,rid,want in inputs:
        try:
            result=judge.parse(evo.output(rid))
            hit=result['mechanisms'][0]['usable'] is want
            if key=='60e_S03':
                coverage={b['id']:b for b in result['coverage']}
                hit=hit and result['section_pass'] is False and all(coverage.get(b,{}).get('status')=='missing' for b in ('S03-B2','S03-B3'))
            report.append({'case':key,'judge':mdl,'run':rid,'expected':want,'correct':hit,
                           'definitive':key!='d9L_S05','result':result})
        except Exception as exc:
            report.append({'case':key,'judge':mdl,'run':rid,'correct':False,'definitive':key!='d9L_S05','error':str(exc)})
    path=evo.ROOT/'evaluations'/'synth'/'calibration_v4.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for row in report: print(row['case'],row['judge'],row['correct'],'definitive=',row['definitive'],row.get('result',{}).get('mechanisms',row.get('error')),flush=True)
    scored=[r for r in report if r['definitive']]
    print(sum(r['correct'] for r in scored),'/',len(scored),'definitive correct')
