"""Offline acceptance receipts: completeness, provenance and cross-reference integrity."""
import hashlib
import copy
import json
from collections import Counter
from pathlib import Path
import covjudge
import evo
import finish_thread_25 as finish
import synth_v2

OUT=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-25\n-n\outputs')

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(gatepath):
    gate=load(gatepath)
    assert gate['decision']=='accept_complete'
    results={}
    for work,info in gate['works'].items():
        sourcepath=evo.ROOT/f"evaluations/synth/{info['source_tag']}_{work}/run.json"
        source=load(sourcepath);expected=14 if work=='op60' else 13
        assert sha(sourcepath)==info['source_sha256']
        assert len(source['state'])==expected
        assert all(s['check'].get('pass') and not s['check'].get('problems') for s in source['state'].values())
        assert source['checkpoints'] and all(g.get('ok') and not g.get('problems') for g in source['checkpoints'].values())
        run=synth_v2.Run(info['source_tag'],work,'g6',source['pool']);run.state=source['state']
        seen=set();statuses=Counter()
        for sec,s in run.state.items():
            assert not run.validate_check(sec,s['pick'],s['check']),sec
            assert all({'id','explains','premise','invented','any_segment','result_only','note'}<=set(e) for e in s['pick']['eval']),sec
            for c in s['chosen']:assert set(c['depends'])<=seen
            for h in s['hist']:
                assert h['id'] not in seen;seen.add(h['id'])
            statuses.update(c['status'] for c in s['check']['coverage'])
        p=evo.ROOT/info['graph_path'];g=load(p)
        assert sha(p)==info['graph_sha256']
        finish.validate(g,source)
        assert not g.get('blocked_edits')
        bids={b['id'] for b in covjudge.beads(work) if b['role']!='演奏条件'}
        for seg in g['segments']:
            local={b['id'] for b in covjudge.beads(work) if b['sec']==seg['sec'] and b['role']!='演奏条件'}
            referenced=set()
            for item in seg['items']:
                assert set(item['explains'])<=local
                assert type(item['follows']) is bool
                referenced.update(item['sources'])
            assert referenced==set(range(1,len(source['state'][seg['sec']]['chosen'])+1)),seg['sec']
        assert sum(statuses.values())==len(bids)
        assert not statuses['missing']
        reviewpath=evo.ROOT/info['fidelity_review_path']
        assert sha(reviewpath)==info['fidelity_review_sha256']
        reviews=load(reviewpath)
        for model,r in reviews.items():
            assert r['pass'] is True and not r['problems'] and not r['arrow_problems'],model
            assert [s['sec'] for s in r['segments']]==list(source['state'])
            assert all(not s['missing'] and not s['invented'] for s in r['segments'])
        cr=load(finish.OUT/(info['source_tag']+'_'+work+'_center_reviews.json'))
        for model,r in cr.items():
            c=next(x for x in r['options'] if x['id']==info['center_option'])
            assert c['pass'],model
        prefix='Op60_船歌' if work=='op60' else 'Op61_幻想波兰舞曲'
        pkgpath=OUT/(prefix+'_Thread_完整记录.json');pkg=load(pkgpath)
        assert pkg['selected_synthesis']==source['state']
        assert pkg['candidate_pools']=={sec:run.mechs(sec) for sec in run.state}
        assert pkg['provenance']['final_gate_sha256']==sha(gatepath)
        assert pkg['graph']['center']==info['center']
        expected_graph=copy.deepcopy(g)
        expected_graph['center']=info['center']
        relations={r['sec']:r['relation'] for r in info['relations']}
        assert set(relations)==set(source['state'])
        assert set(relations.values())<={'正在面对','还说不清','没在想'}
        for seg in expected_graph['segments']:seg['relation']=relations[seg['sec']]
        assert pkg['graph']==expected_graph
        assert pkg['fidelity_reviews']==reviews
        assert pkg['post_review_main_change']==info.get('post_review_main_change',{})
        if info.get('post_review_main_change'):
            delta=info['post_review_main_change']
            before_path=evo.ROOT/delta['before_graph_path']
            assert sha(before_path)==delta['before_sha256'] and sha(p)==delta['after_sha256']
            expected_after=load(before_path)
            next(z for z in expected_after['segments'] if z['sec']==delta['sec'])['because'].remove(delta['removed_edge'])
            assert expected_after==g
        assert len(pkg['graph']['segments'])==expected
        assert [{k:v for k,v in b.items() if k not in ('author_fate','independent_check')} for b in pkg['beads']]==covjudge.beads(work)
        txt=(OUT/(prefix+'_Thread.txt')).read_text(encoding='utf-8-sig')
        assert txt.count('小节 ｜ ')==expected
        assert info['center'] in txt
        assert all(i['text'] in txt for s in g['segments'] for i in s['items'])
        results[work]={'sections':expected,'beads_preserved':len(pkg['beads']),'non_condition_beads':len(bids),'independent_coverage':dict(statuses),'items':sum(len(s['items']) for s in g['segments']),'cross_arrows':sum(len(s.get('because',[])) for s in g['segments']),'source_sha256':sha(sourcepath),'graph_sha256':sha(p),'export_sha256':sha(pkgpath)}
    receipt={'all_passed':True,'works':results,'gate_sha256':sha(gatepath),'scope':'Offline completeness/integrity only. Content acceptance is separately recorded by main review and model reviews.'}
    synth_v2.dump(gatepath.parent/'export_verification.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    import sys
    verify(Path(sys.argv[1]))
