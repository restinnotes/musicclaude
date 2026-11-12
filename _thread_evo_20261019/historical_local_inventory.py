"""Preserve previous local explanations for final non-regression review, outside the new pool."""
import json
import covjudge
import draft10
import evo

CRITICAL={'op60':['S03','S04','S05','S06','S07','S12','S13'], 'op61':['S02','S13']}

def collect(work):
    records=[];segments=draft10.segs(work)
    for source in covjudge.OLD[work]:
        texts=covjudge.sections(source)
        if len(texts)!=len(segments): raise ValueError(source)
        records.append({'source':source,'sections':{s['id']:t for s,t in zip(segments,texts) if s['id'] in CRITICAL[work]}})
    for letter in 'defg':
        name=('60' if work=='op60' else '61')+letter
        path=evo.ROOT/'evaluations'/'beam'/name/'graph.json'
        if not path.exists(): continue
        data=json.loads(path.read_text(encoding='utf-8'))
        records.append({'source':name,'sections':{s['id']:g for s,g in zip(segments,data['segments']) if s['id'] in CRITICAL[work]}})
    return records

if __name__=='__main__':
    data={work:collect(work) for work in CRITICAL}
    out=evo.ROOT/'evaluations'/'continuation_20261025'/'historical_local_inventory.json'
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print({work:len(records) for work,records in data.items()})
