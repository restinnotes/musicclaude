from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
review=read(R/'reviews/S02_component_review.json'); rows=review['baseline_coverage']
assert len(rows)==85 and len({x['id'] for x in rows})==85
current={x['id']:x for x in read(R/'COVERAGE.json')};differences=[]
for x in rows:
 before=current[x['id']]
 if x['status']!=before['status']:
  differences.append(dict(id=x['id'],previous_status=before['status'],challenger_status=x['status'],previous_reason=before['reason'],challenge=x['reason'],resolution='Explicit post-review correction overrides if available; otherwise use conservative challenger status.'))
 x['reason']='第二轮更保守的独立复核：'+x['reason']
put(R/'reviews/S02_adversarial_current_review.json',{'coverage':rows,'reverse_findings':[],'naturalness_findings':[],'method':'只取组件复核中另审当前CONTENT的baseline_coverage；绝不把未采用组件的coverage移入成品。保留复核分歧；后续明确修补仍按对应实际原句裁决。','source_review':'S02_component_review.json','content_snapshot_sha256':review['audit_metadata']['source_hashes_sha256']['CONTENT.json']})
put(R/'AUDIT_DISAGREEMENTS.json',{'scope':'S02第二轮复核与上一轮差异；不是全十四段置信区间。两轮状态定义不同：第二轮将部分关系歧义计入partial，而第一轮把关系另列；保守取项，不宣称模型一致。','differences':differences})
s=read(R/'ACTIVE_VERSIONS.json')
if 'reviews/S02_adversarial_current_review.json' not in s['reviews']:s['reviews'].append('reviews/S02_adversarial_current_review.json')
put(R/'ACTIVE_VERSIONS.json',s);assemble.main()
print('disagreements recorded',len(differences))
