"""Offline inventory and evidence validation. No model calls."""
import json
from pathlib import Path
import covjudge as c
import draft10
import evo

def audit():
    report={}
    for work in ('op60','op61'):
        beads=c.beads(work)
        valid_ids={b['id'] for b in beads}
        required={b['id'] for b in beads if b['role']!='演奏条件'}
        names=sorted(p.stem for p in draft10.OUT.glob(f'd12*_{work}_*.json'))
        missing=[];bad=[];results={};bar_errors=[]
        for n in names:
            for j in c.JUDGES:
                rid=f'cv_{n}_{j}'
                try:
                    raw=evo.parse_json(evo.output(rid))
                    ids=[b['id'] for b in raw['beads']]
                    if len(set(ids))!=len(ids) or not required<=set(ids) or set(ids)-valid_ids:
                        bad.append({'run':rid,'missing':sorted(required-set(ids)),'unknown':sorted(set(ids)-valid_ids),'duplicate':len(ids)!=len(set(ids))})
                    elif any(b.get('label') not in ('解释了','只提到','没有','相反','跳过') for b in raw['beads']):
                        bad.append({'run':rid,'invalid_label':True})
                    else:
                        results[n,j]={b['id']:b for b in raw['beads']}
                except Exception:
                    missing.append(rid)
        complete=[n for n in names if all((n,j) in results for j in c.JUDGES)]
        covered={bid for bid in required if any(all(results[n,j][bid]['label']=='解释了' for j in c.JUDGES) for n in complete)}
        grounded={bid for bid in required if any(all(results[n,j][bid]['label']=='解释了' and not results[n,j][bid].get('invented') for j in c.JUDGES) for n in complete)}
        gaps=[]
        for b in beads:
            if b['id'] not in required-covered:continue
            examples=[]
            for n in complete:
                rs=[results[n,j][b['id']] for j in c.JUDGES]
                if any(r['label']=='解释了' for r in rs):
                    section=next(s for s in json.loads((draft10.OUT/f'{n}.json').read_text(encoding='utf-8'))['sections'] if s['sec']==b['sec'])
                    examples.append({'source':n,'section':section,'judges':dict(zip(c.JUDGES,rs))})
            gaps.append({'bead':b,'disagreements':examples})
        report[work]={'drafts':len(names),'complete_double_reviews':len(complete),'missing':missing,'invalid_reviews':bad,
                      'strict':len(covered),'grounded_strict':len(grounded),'total':len(required),'gaps':gaps}
    out=evo.ROOT/'evaluations'/'continuation_20261025'
    out.mkdir(exist_ok=True)
    (out/'coverage_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    for w,v in report.items():
        print(w,{k:v[k] for k in ('drafts','complete_double_reviews','strict','grounded_strict','total','missing','invalid_reviews')})
        for g in v['gaps']:
            print(g['bead']['id'],g['bead']['text'])
            for e in g['disagreements'][:2]:
                print(e['source'],e['section']['thread'])
                for j,r in e['judges'].items(): print(j,r['label'],r.get('why'),r.get('invented'))
    return report

if __name__=='__main__':audit()
