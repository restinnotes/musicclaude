"""Preserve source candidates, reject contrary explanations, validate mechanism partition.
No old D9/N8/B0 drafts enter this pool. Pool tag is immutable and records exact source hashes.
"""
import hashlib
import json
import sys
import pool
import evo
import draft10
import node2b
import covjudge


def all_candidates(work, names):
    """Read all reviewed sections before filtering, so contrary rejections stay auditable."""
    out={}; beads=covjudge.beads(work)
    for name in names:
        reviews=[covjudge.result(name,j) for j in covjudge.JUDGES]
        if not all(reviews):
            raise ValueError(f'{name}: incomplete coverage review')
        draft=json.loads((draft10.OUT/f'{name}.json').read_text(encoding='utf-8'))
        for section in draft['sections']:
            ids=[b['id'] for b in beads if b['sec']==section['sec'] and b['role']!='演奏条件']
            labels={bid:[r[bid]['label'] for r in reviews] for bid in ids}
            strict=[bid for bid in ids if labels[bid]==['解释了','解释了']]
            out.setdefault(section['sec'],[]).append({'src':name,'feel':section['feel'],
                'thread':section['thread'],'used':section.get('used') or '无','new':section.get('new') or [],
                'explains':strict,'partly':[bid for bid in ids if '解释了' in labels[bid] and bid not in strict],
                'opposite':[bid for bid in ids if labels[bid]==['相反','相反']],
                'review_evidence':{bid:dict(zip(covjudge.JUDGES,[r[bid] for r in reviews])) for bid in ids}})
    return out


def build(tag, work, patterns, sections=None):
    candidates = all_candidates(work, pool.drafts(work, patterns))
    if sections:
        candidates = {k:v for k,v in candidates.items() if k in sections}
    # A direction called contrary by both judges cannot become a History premise just because
    # other beads in the same section outnumber it. Keep the rejected source in the audit.
    rejected = {sec:[c for c in cs if c['opposite']] for sec,cs in candidates.items()}
    candidates = {sec:[c for c in cs if not c['opposite']] for sec,cs in candidates.items()}
    out = pool.OUT / tag / work
    out.mkdir(parents=True, exist_ok=True)
    manifests = {sec:hashlib.sha256(json.dumps(cs, ensure_ascii=False, sort_keys=True).encode()).hexdigest() for sec,cs in candidates.items()}
    manifest = {"work":work,"patterns":patterns,"candidate_hashes":manifests,"excluded_contrary":rejected}
    mp = out / 'manifest.json'
    if mp.exists() and json.loads(mp.read_text(encoding='utf-8')) != manifest:
        raise ValueError('Pool tag already contains different source candidates; use a new tag')
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),encoding='utf-8')
    jobs=[]
    for sec,cs in candidates.items():
        if not cs:
            raise ValueError(f'{work} {sec}: empty pool')
        rid=f'pl{tag}_{work}_{sec}_{manifests[sec][:12]}'
        target=out/f'{sec}.json'
        if target.exists():
            saved=json.loads(target.read_text(encoding='utf-8'))
            if saved.get('source_hash')!=manifests[sec]: raise ValueError(f'{sec}: existing pool provenance mismatch')
            continue
        # Copy only already grouped identical source candidates, retaining their original output provenance.
        reusable=next((p for p in pool.OUT.glob(f'*/{work}/{sec}.json') if p!=target and
                       json.loads(p.read_text(encoding='utf-8')).get('source_hash')==manifests[sec]),None)
        if reusable:
            target.write_bytes(reusable.read_bytes())
            continue
        if not evo.done(rid):
            jobs.append(node2b.job(rid,pool.dedup_msg(work,sec,cs),{'stage':'pool_v2','work':work,'sec':sec},w='g6'))
    evo.run_parallel(jobs,len(jobs) or 1)
    for sec,cs in candidates.items():
        if (out/f'{sec}.json').exists():
            print(work,sec,'reused identical reviewed pool',flush=True)
            continue
        rid=f'pl{tag}_{work}_{sec}_{manifests[sec][:12]}'
        if not evo.done(rid):
            continue
        ms=evo.parse_json(evo.output(rid))['mechs']
        seen=set(); valid=[]
        for m in ms:
            indices=[]
            for key in m.get('members',[]):
                if not isinstance(key,str) or not key.startswith('c') or not key[1:].isdigit():
                    raise ValueError(f'{sec}: invalid member {key}')
                i=int(key[1:])-1
                if not 0<=i<len(cs) or i in seen:
                    raise ValueError(f'{sec}: duplicate/out-of-range member {key}')
                seen.add(i);indices.append(i)
            if not indices or not m.get('text'):
                raise ValueError(f'{sec}: empty mechanism')
            valid.append((m,indices))
        # An omitted candidate is retained as its original mechanism; never silently discarded.
        missing=sorted(set(range(len(cs)))-seen)
        valid.extend(({'text':cs[i]['thread'],'premise':cs[i]['used'],'members':[f'c{i+1}'],'unmerged':True},[i]) for i in missing)
        for i,(m,indices) in enumerate(valid,1):
            mem=[cs[j] for j in indices]
            m.update(id=f'M{i}',sources=[c['src'] for c in mem],n=len(mem),
                     explains=sorted({b for c in mem for b in c['explains']}),
                     partly=sorted({b for c in mem for b in c['partly']}),
                     evidence=[{'source':c['src'],'thread':c['thread'],'used':c['used'],'explains':c['explains']} for c in mem])
        data={'sec':sec,'cands':cs,'mechs':[m for m,_ in valid],'unmerged_candidates':missing,'source_hash':manifests[sec]}
        (out/f'{sec}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(work,sec,len(cs),'candidates ->',len(valid),'mechanisms; omitted retained=',missing,flush=True)


if __name__=='__main__':
    # python pool_v2.py TAG op60 S01,S02,S03,S04,S05 d12*
    build(sys.argv[1],sys.argv[2],sys.argv[4:] or ['d12*'],None if sys.argv[3]=='all' else sys.argv[3].split(','))
