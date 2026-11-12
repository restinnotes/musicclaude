"""Package a paired continuation only after complete, hash-bound acceptance.

No model calls and no automatic mainline/DAG edits. All prose is read from graphs.
"""
import argparse
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import continue_r80 as C
import continuation_evidence as E
import audit_r80 as A
import build_r78a_docs as OLD
import build_continuation_notes as N
import build_final_compare as COMPARE
import experiment_batch as B
import screen_flow as F
import v6weave
import covjudge


def accepted(tag, base):
    A.fair(tag, base, 'full')
    data = json.loads((C.BATCH/f'{tag}_vs{base}_full_audit.json').read_text(encoding='utf-8'))
    assert data['total']['pass'] and not data['missing'], (tag,base,data['total'])
    # User's explicit constraint: both works must pass together. Aggregate
    # positives cannot compensate for a failing work. Each work has four of
    # the eight balanced reviews; apply the same 75% and net conditions.
    assert all(row['n']==4 and row['wins']>=3 and row['no_regress']>=3
               and all(row['net'][k]>=0 for k in F.DIMENSIONS[:3])
               for row in data['per_work'].values()), data['per_work']
    E.fair(tag,base)
    assert F.floor_state(tag,base)['status']=='pass', F.floor_state(tag,base)
    return data


def package(tag, base, extra):
    comparisons = {b:accepted(tag,b) for b in dict.fromkeys((base,'r49b',*extra))}
    for kind in ['coverage','alone']:
        E.floor(tag,base,kind)
    chain=[];current=tag
    while current!='r78a':
        manifests=[json.loads(p.read_text(encoding='utf-8')) for p in C.BATCH.glob('*_manifest.json')]
        m=next(m for m in manifests if current in m['tags'])
        step={'tag':current,'base':m['base'],'suffix':m.get('stage','F2')}
        for w in F.WORKS:
            assert OLD.verify_apply(step,w), (step,w)
        chain.append({**step,'template_sha256':m['template_sha256']})
        current=m['base']
    v6weave.main(tag)
    delivery_date = datetime.now(ZoneInfo('America/New_York')).strftime('%Y%m%d')
    out=C.ROOT/f'deliver_{delivery_date}_{tag}'
    out.mkdir(exist_ok=True)
    integrity={}
    for w in F.WORKS:
        g=A.V.graph_of(w,tag)
        assert g['center']==A.V.graph_of(w,'r78a')['center']
        assert [(s['sec'],s['bars']) for s in g['segments']]==[(s['sec'],s['bars']) for s in A.V.graph_of(w,'r78a')['segments']]
        assert all(2<=len(s['items'])<=4 for s in g['segments'])
        beads=[b for b in covjudge.beads(w) if b['role']!='演奏条件']
        for folder in ['beads_clean','beads_lang']:
            p=C.ROOT/'evaluations'/folder/f'{w}.json'
            if p.exists():
                overlay=json.loads(p.read_text(encoding='utf-8'))
                beads=[dict(b,text=overlay.get(b['id'],b['text'])) for b in beads]
        joined=(A.V.OUT/f'合写_{w}_{tag}.md').read_text(encoding='utf-8')
        baseline=(C.ROOT/'deliver_20261104_r78a'/f'{w}_线与珠子_r78a.md').read_text(encoding='utf-8')
        items=[i['text'] for s in g['segments'] for i in s['items']]
        assert all(joined.count(t)==1 for t in items)
        assert all(joined.count(b['text'])==baseline.count(b['text'])==1 for b in beads)
        B.write_frozen(out/f'{w}_只看线_{tag}.md',f'# {w}｜线（{tag}）\n\n'+A.V.view(g))
        B.write_frozen(out/f'{w}_线与珠子_{tag}.md',joined)
        integrity[w]={'items':len(items),'chars':sum(map(len,items)),'beads':len(beads),
                      'beads_sha256':C.digest(A.V.beads(w)), 'line_sha256':C.digest(A.V.view(g)),
                      'model_edits_only':True,'display_beads_verbatim_from_r78a':True}
    N.build(tag)
    COMPARE.main(tag,'r49b',str(out/f'最终版本_{tag}_vs_r49b.md'),base,*extra)
    shutil.copyfile(C.ROOT/'版本说明'/f'{tag}_vs_{base}.md',out/f'{tag}_vs_{base}_提示词与差别.md')
    receipt={'tag':tag,'base':base,'accepted_at':datetime.now(ZoneInfo('America/New_York')).isoformat(),
             'paired_chain_from_r78a':list(reversed(chain)), 'comparisons':comparisons,'integrity':integrity,
             'converged':False,'scope':'Paired acceptance; convergence requires later independent rounds.'}
    B.write_frozen(out/'integrity.json',B.json_text(receipt))
    text=f'''# {tag} 交付说明

两首一起从 {base} 前进；成品正文来自同一提示词和步骤的模型修改，逐条反查原文并机械套用。没有按作品拼版。

正反八票、两首分别的结果及固定锚点 r49b 的结果见逐段对比。覆盖和单独读底线均按既定规则核对；通过不代表每项覆盖数提高。

每首有只看线、线与珠子两份。珠子显示文字逐字沿用 r78a，Center 和分段不变。提示词与差别文档列出全部变化及本地原文路径。

本包确认接纳，不据此宣称收敛、解决全部中等问题或已在其他作品泛化。后续收敛核对见主目录 STATUS.md 和试验记录.md。
'''
    B.write_frozen(out/'00_说明.md',text)
    archive=Path.home()/'Downloads'/f'deliver_{delivery_date}_{tag}.zip'
    assert not archive.exists(),archive
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):
            if p.is_file():z.write(p,arcname=f'{out.name}/{p.name}')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(z.read(f'{out.name}/{p.name}')==p.read_bytes() for p in out.iterdir() if p.is_file())
    C.write(C.BATCH/f'{tag}_acceptance.json',receipt)
    print('PACKAGED',out,archive)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tag');p.add_argument('base');p.add_argument('extra',nargs='*')
    a=p.parse_args();package(a.tag,a.base,a.extra)
