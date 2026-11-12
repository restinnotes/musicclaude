"""Meaningful integrity checks: source identities, exact excerpts, ranges, dispatch hashes."""
from pathlib import Path
import hashlib, json, re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def j(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    m=j(ROOT/'sources/SOURCE_MANIFEST.json'); sources={s['src_id']:s for s in m['sources']}
    assert len(sources)==30
    assert Counter(s['group'] for s in sources.values())==Counter({f'{x}-{c}':3 for x in ['gflash','muse','luna','gpt56w','gpt6w'] for c in ['int','web']})
    assert all(not x.startswith('SRC-gpro-') and x not in ['SRC-gpt56w-int-1','SRC-gpt56w-web-1'] for x in sources)
    assert all('sol' not in s['model_name'].lower() for s in sources.values())
    for s in sources.values():assert sha((ROOT/s['archive']).read_bytes())==s['actual_sha256']
    units=j(ROOT/'sources/units.json'); index=j(ROOT/'pools/POOL_INDEX.json')
    assert list(index)==[f'S{i:02d}' for i in range(1,15)]
    assert [n for s in index.values() for n in range(s['range'][0],s['range'][1]+1)]==list(range(1,117))
    checks=0
    for seg,spec in index.items():
        raw=(ROOT/f'pools/{seg}_FULL.txt').read_bytes(); assert sha(raw)==spec['pool_sha256']
        text=raw.decode('utf-8')
        assert '仅登记UID/范围，正文未传入' not in text
        present=re.findall(r'^\[(SRC-[^\]]+)\]',text,re.M)
        assert present==[e['uid'] for e in spec['units']]
        for e in spec['units']:
            u=units[e['uid']]; body=u['text'].rstrip()
            assert u['src'] in sources
            assert body in text
            assert body in (ROOT/sources[u['src']]['archive']).read_text(encoding='utf-8-sig')
            assert sha(body.encode())==e['sha256'];checks+=1
    dispatched=0
    for manifest in ROOT.glob('jobs*.json'):
        for job in j(manifest).get('jobs',[]):
            p=(manifest.parent/job['prompt_file']).resolve()
            if job.get('prompt_sha256'):
                assert sha(p.read_bytes())==job['prompt_sha256'], job['job_id']
                dispatched+=1
    result={'source_documents':len(sources),'groups':dict(Counter(s['group'] for s in sources.values())), 'segments':14,'complete_verbatim_segment_occurrences':checks,'job_prompt_hashes_checked':dispatched,'status':'passed','limit':'Integrity checks only; this is not a literary quality score or validation of all A musical claims.'}
    (ROOT/'audits/INTEGRITY_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__': main()
