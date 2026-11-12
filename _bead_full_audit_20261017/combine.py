import json,re,hashlib,html
from pathlib import Path
from collections import Counter
R=Path(__file__).parent; B=Path(r'D:\musicclaude\_bead_quality_20261017')
U=json.loads((B/'sources/units.json').read_text(encoding='utf-8'))
beads={b['segment']:b['body'] for b in json.loads((B/'editorial/FINAL_BEADS.json').read_text(encoding='utf-8'))}
inputs=json.loads((R/'INPUT_CHECK.json').read_text(encoding='utf-8'))
rows=[]; reviews=[]; merges=[]; limitations=[]; errors=[]
for filename in ['audit_1.json','audit_2.json','audit_3.json','audit_4.json','audit_global.json']:
    f=R/filename
    if not f.exists():errors.append('Missing '+filename);continue
    d=json.loads(f.read_text(encoding='utf-8'))
    rows+=d['meanings'];reviews+=d['unit_reviews'];merges+=d['merges'];limitations+=d['limitations']
ids={x['id'] for x in rows}
if len(ids)!=len(rows):errors.append('Duplicate meaning IDs')
checked=0;spans=0
for r in rows:
    if r['status'] not in ['full','partial','omitted','altered','pending','not_applicable']:errors.append(f"{r['id']} bad status")
    if not r['evidence']:errors.append(f"{r['id']} missing evidence")
    for e in r['evidence']:
        if e['uid'] not in U or e['quote'] not in U[e['uid']]['text']:errors.append(f"{r['id']} invalid quote {e['uid']}: {e['quote'][:90]}")
        checked+=1
    texts=[beads[r['segment']]] if r['segment'] in beads else list(beads.values())
    for s in r['current_spans']:
        if not any(s in t for t in texts):errors.append(f"{r['id']} invalid current span: {s[:90]}")
        spans+=1
    if r['status']=='full' and not r['current_spans']:errors.append(f"{r['id']} full without text")
for r in reviews:
    for i in r['meaning_ids']:
        if i not in ids:errors.append(f"{r['uid']} bad meaning reference {i}")
reviewed={(x['segment'],x['uid']) for x in reviews}
expected={(s,u) for s,us in inputs['pools'].items() for u in us}
remainder=json.loads((R/'REMAINDER_INPUT.json').read_text(encoding='utf-8'))
expected|={('GLOBAL',u['uid']) for u in remainder}
missing=sorted(expected-reviewed)
if missing:errors.append(f'Missing unit reviews: {missing}')
for m in merges:
    for i in m['source_meaning_ids']:
        if i not in ids:errors.append(f"{m['id']} bad merge reference {i}")
    for s in m['current_spans']:
        if s not in beads[m['segment']]:errors.append(f"{m['id']} bad merge span {s[:90]}")
for segment in beads:
    if not any(m['segment']==segment for m in merges):errors.append('Missing merge review '+segment)
def stats(rs):
    c=Counter(x['status'] for x in rs)
    eligible=sum(c[s] for s in ['full','partial','omitted','altered'])
    return dict(total=len(rs),counts=dict(c),assessed_denominator=eligible,complete_retention_pct=round(c['full']/eligible*100,2) if eligible else None,complete_over_all_candidates_pct=round(c['full']/len(rs)*100,2) if rs else None)
local=[r for r in rows if r['segment']!='GLOBAL' and r['dimension']!='音乐事实']
report=dict(mother_sha256=hashlib.sha256((B/'editorial/FINAL_BEADS.json').read_bytes()).hexdigest(),raw_sources=30,raw_units=353,expected_unit_segment_reviews=len(expected),actual_unique_reviews=len(reviewed),missing_unit_reviews=missing,exact_quotes=checked,current_spans=spans,errors=errors,local_experience=stats(local),local_music_facts=stats([r for r in rows if r['segment']!='GLOBAL' and r['dimension']=='音乐事实']),global_separate=stats([r for r in rows if r['segment']=='GLOBAL']),by_segment={s:stats([r for r in local if r['segment']==s]) for s in beads},merge_verdicts=dict(Counter(m['verdict'] for m in merges)),limitations=limitations)
canonical_config=json.loads((R/'CANONICAL_GROUPS.json').read_text(encoding='utf-8'))
rowmap={x['id']:x for x in rows};parent={r['id']:r['id'] for r in rows if r['segment']!='GLOBAL' and r.get('counting_role')!='context_detail'}
def root(i):
    if parent[i]!=i:parent[i]=root(parent[i])
    return parent[i]
def union(xs):
    xs=[i for i in xs if i in parent]
    for i in xs[1:]:parent[root(i)]=root(xs[0])
global_ids={}
for r in rows:
    if r.get('global_meaning_id') and r['id'] in parent:global_ids.setdefault(r['global_meaning_id'],[]).append(r['id'])
for xs in global_ids.values():union(xs)
for group in canonical_config['groups']:union(group['ids'])
groups={}
for i in parent:groups.setdefault(root(i),[]).append(rowmap[i])
priority={'full':0,'partial':1,'altered':2,'omitted':3,'pending':4,'not_applicable':5}
unique=[]
for members in groups.values():
    representative=min(members,key=lambda r:priority[r['status']]).copy()
    representative['canonical_members']=[r['id'] for r in members]
    representative['canonical_status_note']='仅在已确认同一独立意思的组内，以适用段中实际表达最充分者判覆盖；各段原判定仍可查。'
    unique.append(representative)
report['unique_local_experience']=stats([r for r in unique if r['dimension']!='音乐事实'])
report['cross_segment_duplicate_records_removed']=sum(len(x['canonical_members'])-1 for x in unique)
report['context_details_not_counted_as_independent']=len([r for r in rows if r.get('counting_role')=='context_detail'])
report['canonical_note']='同一宽范围原意在任一适用段表达即计已触达；逐段未表达仍保留在定位账，不能据此误报必须每段复述。全曲账不与局部账直接相加。'
(R/'CANONICAL_LOCAL_MEANINGS.json').write_text(json.dumps(unique,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'ALL_MEANINGS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'ALL_MERGES.json').write_text(json.dumps(merges,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'ALL_UNIT_REVIEWS.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding='utf-8')
sentence_rows=[]
for seg,body in beads.items():
    for n,s in enumerate(re.findall(r'[^。！？\n]+[。！？]?|[^\n]+$',body),1):
        refs=[r['id'] for r in rows if r['segment']==seg and any(t in s or s in t for t in r['current_spans'])]
        ms=[m['id'] for m in merges if m['segment']==seg and any(t in s or s in t for t in m['current_spans'])]
        sentence_rows.append(dict(id=f'{seg}-T{n:02}',segment=seg,text=s,meaning_ids=refs,merge_ids=ms,needs_direct_review=not refs and not ms))
(R/'CURRENT_SENTENCE_LEDGER.json').write_text(json.dumps(sentence_rows,ensure_ascii=False,indent=2),encoding='utf-8')
names=dict(full='完整保留',partial='部分保留',omitted='遗漏',altered='改义',pending='待核',not_applicable='不适用')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>原稿 → 当前稿 · 内容审计</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f2ec;color:#24342f;font:16px/1.85 "Microsoft YaHei",sans-serif}main,header{max-width:1160px;margin:auto;padding:24px}h1{font-size:28px;font-weight:500}h2{font-size:19px;font-weight:500}.bar{position:sticky;top:0;background:#f5f2ec;padding:12px 0;z-index:2;display:flex;gap:10px;flex-wrap:wrap}input,select{padding:8px;font:inherit;background:white;border:1px solid #c9ccc3}input{flex:1}.item{padding:25px;margin:18px 0;border:1px solid #c9ccc3;background:#fffdf8}.meta{font-size:13px;color:#55645c}blockquote{white-space:pre-wrap;border-left:2px solid #b7beaf;margin:12px 0;padding:10px 18px;background:#f1f2ec;font-size:15px}p{margin:10px 0}summary{cursor:pointer}.label{font-size:13px;color:#576259}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left}a{color:#235b4a}section{overflow-wrap:anywhere}</style><header><h1>原稿 → 当前稿：意思是否真的还在</h1><p>审计30份冻结A原稿，对照现有14段正文。此页是审计账本，不是视频画面，也不是已修订成片。</p><p>“完整”只计正文能读出的全部区别；“部分”不算完整覆盖。待核项保留在总候选账中。全曲读法与局部意义分别统计，不能相加当成去重总数。数值取决于公开的语义划分，可逐项反驳。</p><div id="totals"></div></header><main><div class="bar"><select id="mode"><option value="meanings">原意逐项</option><option value="merges">合并检查</option><option value="units">原文单元去向</option></select><select id="seg"><option value="">全部段落</option></select><select id="status"><option value="">所有判定</option></select><input id="q" placeholder="搜索犹豫、怕结束、沉默、原句或UID" aria-label="搜索"></div><p id="count"></p><section id="list"></section></main><script>const data=__DATA__, merges=__MERGES__, units=__UNITS__, stats=__STATS__,names=__NAMES__;let $=id=>document.getElementById(id),esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));for(const s of [...Object.keys(stats.by_segment),'GLOBAL'])$('seg').add(new Option(s,s));for(const [k,v]of Object.entries(names))$('status').add(new Option(v,k));$('totals').innerHTML='<table><tr><th>段落</th><th>完整</th><th>部分</th><th>遗漏</th><th>改义</th><th>待核</th><th>不适用</th></tr>'+Object.entries({...stats.by_segment,GLOBAL:stats.global_separate}).map(([s,v])=>'<tr><td>'+s+'</td>'+Object.keys(names).map(k=>'<td>'+(v.counts[k]||0)+'</td>').join('')+'</tr>').join('')+'</table>';function render(){let mode=$('mode').value,q=$('q').value.toLowerCase(),arr=mode==='meanings'?data:mode==='merges'?merges:units;arr=arr.filter(r=>(!$('seg').value||r.segment===$('seg').value)&&(mode!=='meanings'||!$('status').value||r.status===$('status').value)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));$('count').textContent='符合当前筛选：'+arr.length+'项';$('list').innerHTML=arr.map(r=>mode==='meanings'?`<article class="item" id="${esc(r.id)}"><div class="meta">${esc(r.id)} · ${esc(r.dimension)} · ${names[r.status]}</div><h2>${esc(r.meaning)}</h2><div class="label">原稿</div>${r.evidence.map(e=>`<blockquote>${esc(e.quote)}</blockquote><div class="meta">${esc(e.uid)}</div>`).join('')}<div class="label">现稿</div><p>${r.current_spans.map(esc).join('<br>')||'没有对应表达'}</p><div class="label">未保留／判断依据</div><p>${esc(r.lost)}</p><p>${esc(r.rationale)}</p><details><summary>关系与修订建议（未写入成品）</summary><p>${esc(JSON.stringify(r.relation))}</p><p>${esc(r.repair)}</p></details></article>`:mode==='merges'?`<article class="item"><div class="meta">${esc(r.id)} · ${esc(r.verdict)}</div><h2>${r.current_spans.map(esc).join(' / ')}</h2><p>${esc(r.reason)}</p><p>保住：${esc(JSON.stringify(r.preserved))}</p><p>损失：${esc(JSON.stringify(r.lost))}</p><p>关联原意：${r.source_meaning_ids.map(i=>`<a href="#${esc(i)}" onclick="showMeaning('${esc(i)}');return false">${esc(i)}</a>`).join(' · ')}</p><p>${esc(r.repair)}</p></article>`:`<article class="item"><h2>${esc(r.segment)} · ${esc(r.uid)}</h2><p>${esc(r.disposition)}</p><p>${esc(r.residual)}</p><p>${r.meaning_ids.map(esc).join(' · ')}</p></article>`).join('')}function showMeaning(id){$('mode').value='meanings';$('seg').value='';$('status').value='';$('q').value=id;render();window.scrollTo(0,0)}for(const id of ['mode','seg','status','q'])$(id).addEventListener('input',render);render();</script></html>'''
page=page.replace('<div id="totals"></div>','<details><summary>展开逐段统计（音乐事实另计）</summary><div id="totals"></div></details>')
page=page.replace('const data=__DATA__,','const sourceTexts=__SOURCE_TEXTS__,data=__DATA__,')
page=page.replace('<div class="meta">${esc(e.uid)}</div>','<div class="meta">${esc(e.uid)}</div><details><summary>核对这个原文单元的全文</summary><blockquote>${esc(sourceTexts[e.uid])}</blockquote></details>')
page=page.replace('<p>${esc(r.residual)}</p><p>${r.meaning_ids.map(esc).join(\' · \')}</p>','<p>${esc(r.residual)}</p><p>${r.meaning_ids.map(esc).join(\' · \')}</p><details><summary>原文全文</summary><blockquote>${esc(sourceTexts[r.uid])}</blockquote></details>')
page=page.replace('render();</script>',"if(location.hash){let h=decodeURIComponent(location.hash.slice(1));if([...$('seg').options].some(o=>o.value===h))$('seg').value=h;else $('q').value=h}render();</script>")
page=page.replace('__SOURCE_TEXTS__',json.dumps({k:v['text'] for k,v in U.items()},ensure_ascii=False).replace('</','<\\/'))
page=page.replace('${esc(r.verdict)}',"${esc(({lossless:'无损合并',lossy:'有损合并',false_equivalence:'错误等同',invented_link:'新增连接',not_a_merge:'单源转述／不构成合并'})[r.verdict]||r.verdict)}")
for key,value in [('DATA',rows),('MERGES',merges),('UNITS',reviews),('STATS',report),('NAMES',names)]:page=page.replace('__'+key+'__',json.dumps(value,ensure_ascii=False).replace('</','<\\/'))
if errors:page=page.replace('<h1>', '<p style="background:#fff0cb;padding:15px">审计仍在进行，当前数字不作为交付结论。剩余检查见 VALIDATION.json。</p><h1>',1)
(R/'完整内容审计.html').write_text(page,encoding='utf-8')
print(json.dumps({'rows':len(rows),'reviews':len(reviewed),'missing_review_count':len(missing),'exact_quotes':checked,'span_checks':spans,'errors':[e for e in errors if not e.startswith('Missing unit reviews')],'local_experience':report['local_experience'],'merges':report['merge_verdicts']},ensure_ascii=False,indent=2))
