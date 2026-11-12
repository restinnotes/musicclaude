import json
import calib_synth as old
import calib_synth_v2 as v2
import judge_synth_v3 as judge
import synth
import evo
import node2b


def cases():
    for key,(sec,hist,text,want,why) in old.CASES.items():
        hist=[dict(h) for h in hist]
        if key=='60d_S04':
            hist[1]['text']='他真实享受到亲近带来的快乐；亲近越显珍贵，他越不忍它转瞬即逝，期待也渐渐成了盼这份亲近长久。'
        # The comfortable explanation is locally valid, but must fail coverage of urgency + undercurrent.
        yield key,sec,hist,text,(True if key=='60e_S03' else want)


if __name__=='__main__':
    r=synth.Run('calib3','op60','g6','none');jobs=[]
    for key,sec,hist,text,want in cases():
        msg=judge.message('op60',sec,hist,[{'text':text}],r.bead_text(sec))
        for mdl in ('g6','g56'):
            rid=f'cs3_{key}_{mdl}'
            if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'calib_synth_v3','case':key},w=mdl))
    evo.run_parallel(jobs,len(jobs) or 1)
    report=[]
    for key,sec,hist,text,want in cases():
        for mdl in ('g6','g56'):
            try:
                raw=evo.output(f'cs3_{key}_{mdl}');v=judge.parse(raw)
                hit=v['mechanisms'][0]['usable'] is want
                if key=='60e_S03':
                    coverage={b['id']:b for b in v['coverage']}
                    hit=hit and v['section_pass'] is False and all(coverage.get(b,{}).get('status')=='missing' for b in ('S03-B2','S03-B3'))
                report.append({'case':key,'judge':mdl,'expected_local_usable':want,'correct':hit,'result':v})
            except Exception as exc:
                report.append({'case':key,'judge':mdl,'correct':False,'error':str(exc)})
    path=evo.ROOT/'evaluations'/'synth'/'calibration_v3.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in report:print(r['case'],r['judge'],r['correct'],r.get('result',{}).get('mechanisms',r.get('error')))
    print(sum(r['correct'] for r in report),'/',len(report),'correct')
