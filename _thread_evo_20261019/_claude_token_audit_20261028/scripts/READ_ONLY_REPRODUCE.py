"""Read frozen byte prefixes; reproduce measured ledger and hypothetical scenarios.
Python 3.10+, stdlib only. No model/network calls or production imports/writes.
Usage: python READ_ONLY_REPRODUCE.py --output-dir PATH
Optional: --source-map JSON mapping owner to another local JSONL copy.
Classification is a disclosed audit interpretation, loaded from CLASSIFICATION_MAP.csv.
"""
import argparse, collections, csv, hashlib, io, json, pathlib

KEYS = ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens', 'output_tokens']

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write_csv(p, rows):
    if not rows:
        return
    with p.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def price(model, u):
    i, r, w, o = (u.get(k, 0) for k in KEYS)
    cc = u.get('cache_creation') or {}; w1 = cc.get('ephemeral_1h_input_tokens', 0); w5 = cc.get('ephemeral_5m_input_tokens', 0)
    if w != w1 + w5:
        raise ValueError('Unspecified cache TTL; do not silently assign a rate')
    if model == 'claude-opus-5-5':
        base, out, read = 4, 20, .2
    elif model == 'claude-haiku-5-5':
        base, out, read = (.5, 2.5, .05) if i+r+w > 100000 else (.1, .5, .01)
    else:
        raise ValueError('Unpriced model: '+str(model))
    return {'noncache': i*base/1e6, 'read': r*read/1e6, 'write_1h': w1*2*base/1e6,
            'write_5m': w5*1.25*base/1e6, 'output': o*out/1e6}

def scenario(fs, cfg, name, case, p):
    T=sum(f['cost'] for f in fs); K=cfg['context_prefix_tokens']; gross=transfer=0.; attr=collections.defaultdict(float)
    for f in fs:
        c=f['category']; rate=p.get(c,0)
        if c=='E': rate=p['poll'] if f['poll_strict'] else p.get('Eother',0)
        removed=f['cost']*rate; gross+=removed
        u=f['usage']
        if u['cache_creation_input_tokens']>100000 and u['cache_read_input_tokens']<u['cache_creation_input_tokens']:
            transfer+=f['components']['write_1h']*rate
        key=('engineering' if c in ['C','D'] else 'polling' if f['poll_strict'] else
             {'E':'other_execution','F':'aggregation_and_initial_screen','B':'art_review_trial','I':'desktop_simplification'}.get(c,'other'))
        attr[key]+=removed
    n=cfg['packages'][name]*p['factor']
    overhead={'new_delegation':0 if name=='A' else n*(K*.2+800*20+800*8)/1e6,
              'new_result_reading':n*(K*.2+p['packet']*8)/1e6,
              'new_validation':n*(600*20+p['full_review']*12000*8)/1e6,
              'additional_cache_expiry':n*p['expiry']*K*7.8/1e6,
              'context_or_tools_change':{'A':.3,'B':2,'C':5}[name],
              'expected_technical_escalation':n*p['escalation']*1.5,
              'expected_quality_rework':n*p['regression']*5}
    total=T-gross+transfer+sum(overhead.values())
    return dict(scheme=name,case=case,gross_removed=gross,retained_historical_cost=T-gross,
                cold_write_transferred_to_retained=transfer,**overhead,new_total=total,cost_index=100*total/T,
                net_savings_percent=100*(T-total)/T)

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',required=True); ap.add_argument('--source-map')
    args=ap.parse_args(); here=pathlib.Path(__file__).resolve().parent; package=here.parent
    out=pathlib.Path(args.output_dir).resolve()
    if any(part.lower()=='.claude' for part in out.parts): raise ValueError('Output may not be inside .claude')
    prod=pathlib.Path(r'D:\musicclaude').resolve()
    if out==prod: raise ValueError('Specify an independent audit subdirectory')
    out.mkdir(parents=True,exist_ok=True)
    manifest=read_json(package/'SOURCE_MANIFEST.json'); source_map=read_json(pathlib.Path(args.source_map)) if args.source_map else {}
    with (package/'CLASSIFICATION_MAP.csv').open(encoding='utf-8-sig',newline='') as f:
        labels={r['message_id']:r for r in csv.DictReader(f)}
    allgroups={}; attempts={}; refs=set(); provenance=[]
    for s in manifest['token_sources']:
        p=pathlib.Path(source_map.get(s['owner'],s['original_path']))
        if p.resolve()==out or p.resolve().is_relative_to(out): raise ValueError('Output contains a source path')
        with p.open('rb') as f: data=f.read(s['bytes'])
        digest=hashlib.sha256(data).hexdigest()
        if len(data)!=s['bytes'] or digest!=s['sha256']:
            raise ValueError('Frozen prefix hash mismatch: '+s['owner'])
        provenance.append({'owner':s['owner'],'bytes':len(data),'sha256':digest})
        for ln,line in enumerate(io.StringIO(data.decode('utf-8-sig')),1):
            r=json.loads(line)
            if s['owner']=='main' and r.get('type')=='api-request': attempts[r['id']]=(ln,r)
            m=r.get('message',{})
            if r.get('type')!='assistant' or m.get('model')=='<synthetic>' or not m.get('id'): continue
            mid=m['id']; item=allgroups.setdefault(mid,{'owner':s['owner'],'line':ln,'model':m.get('model'),'timestamp':r.get('timestamp',''),'usage':{},'request_ref':''})
            u=m.get('usage',{})
            # Repeated blocks carry cumulative usage; choose complete nonzero usage ONCE.
            if sum(u.get(k,0) for k in KEYS)>sum(item['usage'].get(k,0) for k in KEYS): item['usage']=u
            if r.get('requestRef'): item['request_ref']=r['requestRef']; refs.add(r['requestRef'])
    if set(allgroups)!=set(labels): raise ValueError('Classification map does not match frozen request IDs')
    ledger=[]; fs=[]
    for mid,g in sorted(allgroups.items(),key=lambda kv:(kv[1]['timestamp'],kv[0])):
        u=g['usage']; c=price(g['model'],u); label=labels[mid]; cost=sum(c.values())
        row=dict(message_id=mid,owner=g['owner'],source_first_line=g['line'],timestamp_utc=g['timestamp'],model=g['model'],
                 **{k:u.get(k,0) for k in KEYS},cache_write_1h=u['cache_creation'].get('ephemeral_1h_input_tokens',0),
                 cache_write_5m=u['cache_creation'].get('ephemeral_5m_input_tokens',0),api_equivalent_usd=cost,
                 category=label['category'],confidence=label['confidence'],poll_strict=label['poll_strict'])
        ledger.append(row);fs.append(dict(cost=cost,usage=u,components=c,category=label['category'],poll_strict=label['poll_strict']=='True'))
    write_csv(out/'REPRODUCED_LEDGER.csv',ledger)
    cats=[]
    for cat in 'ABCDEFGHI':
        a=[r for r in ledger if r['category']==cat]
        cats.append(dict(category=cat,requests=len(a),**{k:sum(r[k] for r in a) for k in KEYS},api_equivalent_usd=sum(r['api_equivalent_usd'] for r in a)))
    write_csv(out/'REPRODUCED_CATEGORIES.csv',cats)
    cfg=read_json(package/'SCENARIO_ASSUMPTIONS.json')
    scenarios=[scenario(fs,cfg,n,c,p) for n,cases in cfg['params'].items() for c,p in cases.items()]
    write_csv(out/'REPRODUCED_SCENARIOS.csv',scenarios)
    totals={k:sum(r[k] for r in ledger) for k in KEYS}; total=sum(r['api_equivalent_usd'] for r in ledger)
    expected=manifest['expected_measured_totals']
    assert len(ledger)==expected['requests'] and totals==expected['tokens']
    assert abs(total-expected['api_equivalent_usd'])<1e-7
    unmatched=set(attempts)-refs; assert len(unmatched)==279
    receipt={'source_hashes_validated':provenance,'requests':len(ledger),'tokens':totals,'api_equivalent_usd':total,
             'main_unmatched_attempts':len(unmatched),'production_writes':0,'network_calls':0,'model_calls':0,
             'classification_source':'frozen audit interpretation map; not newly inferred by this script',
             'scenarios_are_assumptions':True}
    (out/'REPRODUCTION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
