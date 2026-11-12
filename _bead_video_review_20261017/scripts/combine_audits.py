from pathlib import Path
import json, re, hashlib
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
BASE=Path(r'D:\musicclaude\_bead_quality_20261017')
units=json.loads((ROOT/'reference/A_UNITS_UNCHANGED.json').read_text(encoding='utf-8'))
names={'full':'完整保留','partial':'部分保留','omitted':'遗漏','quarantine':'待核／隔离','out_of_scope':'本段范围外'}
rows=[]
def collect(v):
    if isinstance(v,dict):
        if 'meaning' in v and 'status' in v and 'segment' in v:
            rows.append(v)
        else:
            for x in v.values():collect(x)
    elif isinstance(v,list):
        for x in v:collect(x)
for n in range(1,4):
    collect(json.loads((ROOT/f'audits/semantic_{n}.json').read_text(encoding='utf-8')))
assert rows, 'no rows'
assert {r['segment'] for r in rows}=={f'S{i:02}' for i in range(1,15)}
assert len({r['id'] for r in rows})==len(rows),'duplicate id'
errors=[]; checked=0
beads={b['segment']:b['body'] for b in json.loads((ROOT/'reference/FINAL_BEADS_UNCHANGED.json').read_text(encoding='utf-8'))}
pools={s:set(re.findall(r'^\[(SRC-[^\]]+)\]',(BASE/f'production_context/pools/{s}.txt').read_text(encoding='utf-8'),re.M)) for s in beads}
current_checked=0
for r in rows:
    assert r['status'] in names, r
    if r.get('current_support'):
        assert r['current_support'] in beads[r['segment']],r['id']
        current_checked+=1
    for e in r['evidence']:
        assert e['uid'] in pools[r['segment']],(r['id'],e['uid'])
        checked+=1
        if e['uid'] not in units or e['quote'] not in units[e['uid']]['text']:
            errors.append({'id':r['id'],'uid':e['uid'],'quote':e['quote']})
report={'families':len(rows),'exact_quotes_checked':checked,'quote_failures':errors,'current_support_checked':current_checked,'all_evidence_in_correct_segment_pool':True,
    'counts':dict(Counter(r['status'] for r in rows)),
    'by_segment':{f'S{i:02}':dict(Counter(r['status'] for r in rows if r['segment']==f'S{i:02}')) for i in range(1,15)},
    'mother_sha256':hashlib.sha256((BASE/'editorial/FINAL_BEADS.json').read_bytes()).hexdigest(),
    'scope':'按段归并的人工意义族；同义粒度有编辑判断。51个GLOBAL单位不纳入分母。不是原A所有命题的穷尽证明。',
    'complete_retention_definition':'该意义族登记的核心差异均被母稿表达；不等于该UID全部内容被表达。',
    'partial_retention_definition':'共同底色或部分差异保留，仍丢失影响理解的意思；不按完整保留计算。'}
(ROOT/'audits/COMBINED_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if errors:
    print(json.dumps({'quote_failures':errors},ensure_ascii=False,indent=2))
    raise SystemExit(1)
(ROOT/'MEANING_INVENTORY.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# 十四段异质性反向核查','',report['scope'],'','本表核查的是旧母稿。展示候选或补回句另列，不会让旧稿的覆盖统计自动上升。','', '| 段落 | 完整 | 部分 | 遗漏 | 待核／隔离 | 本段范围外 |','|---|---:|---:|---:|---:|---:|']
for sid,c in report['by_segment'].items():md.append('| '+sid+' | '+' | '.join(str(c.get(s,0)) for s in names)+' |')
md+=['','“部分”不与“完整”合并计算覆盖率；“隔离”和“范围外”也不是可以忽略的有效遗漏。这里只统计按段意义族，不给整份原A一个伪精确百分比。','']
for sid in report['by_segment']:
    md += ['## '+sid,'']
    for r in (x for x in rows if x['segment']==sid):
        md += [f"### {r['id']} · {names[r['status']]} · {r['meaning']}",'']
        if r.get('subdifferences'):md+=['子差异：'+'；'.join(r['subdifferences']),'']
        md+=['母稿对应：'+(r.get('current_support') or '无'),'','未保住的意思：'+(r.get('lost_meaning') or '本条未发现'),'','判断：'+r.get('reason',''),'']
        for e in r['evidence']:md += [f"原A {e['uid']}：",'', '> '+e['quote'].replace('\n','\n> '),'']
        if r.get('suggested_human_line'):md += ['补回候选（不自动加入母稿）：'+r['suggested_human_line'],'']
(ROOT/'MEANING_REVIEW.md').write_text('\n'.join(md),encoding='utf-8')

page=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>异质性逐条核对</title><style>*{box-sizing:border-box}body{max-width:1080px;margin:auto;padding:35px 24px;background:#f4f0e8;color:#243d37;font:16px/1.9 'Microsoft YaHei',sans-serif}h1{font-size:29px;font-weight:500}h2{font-size:21px;font-weight:500;margin:8px 0}p{margin:12px 0}.note{font-size:14px;color:#6b766e}.bar{position:sticky;top:0;z-index:2;background:#f4f0e8;padding:14px 0;display:flex;gap:10px;flex-wrap:wrap}select,input{font:inherit;padding:8px 12px;border:1px solid #cccfc0;background:#faf8f2;color:inherit;border-radius:4px}input{flex:1;min-width:200px}.card{padding:25px 30px;margin:18px 0;background:#faf8f2;border:1px solid #d8dbcd;border-left:4px solid #af9667}.status{font-size:13px;color:#6f796d}.full{border-left-color:#315f4e}.omitted{border-left-color:#aa6b49}.quarantine{border-left-color:#847b91}blockquote{margin:14px 0;padding:10px 20px;border-left:2px solid #c7b48c;font-size:14px;white-space:pre-wrap;background:#f0eee5}.proposed{font-size:19px;line-height:1.8}.label{font-size:12px;color:#6e7b70;letter-spacing:1px}summary{cursor:pointer}a{color:#245c48}</style><h1>被合并的，究竟是不是同一个意思？</h1><p class="note">反向检查十四段母稿。完整、部分、遗漏分别列出；不把用了同一个来源编号视为保住了这个来源的全部意思。以下是人工归并的意义族，不是所有原稿命题的穷尽清单；51个GLOBAL单位未纳入。</p><p><a href="分镜与异质性预览.html">看三段分镜试样 →</a></p><div class="bar"><select id="seg" aria-label="音乐段"><option value="">全部十四段</option></select><select id="status" aria-label="保留状态"><option value="">所有状态</option></select><input id="search" aria-label="搜索意义和原句" placeholder="搜索意思、原句或来源"></div><p id="count" class="note"></p><main id="list"></main><script>const rows=__ROWS__,names=__NAMES__;const $=x=>document.getElementById(x);const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));for(let i=1;i<=14;i++){let s='S'+String(i).padStart(2,'0');$('seg').add(new Option(s,s))}for(let [k,v]of Object.entries(names))$('status').add(new Option(v,k));function render(){let q=$('search').value.trim().toLowerCase();let shown=rows.filter(r=>(!$('seg').value||r.segment===$('seg').value)&&(!$('status').value||r.status===$('status').value)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));$('count').textContent=`显示 ${shown.length} / ${rows.length} 个按段意义族。补回句仍是编辑候选，不算旧母稿已覆盖。`;$('list').innerHTML=shown.map(r=>`<article class="card ${r.status}"><span class="status">${esc(r.id)} · ${esc(r.segment)} · ${names[r.status]}</span><h2>${esc(r.meaning)}</h2><p class="note">${(r.subdifferences||[]).map(esc).join('；')}</p><div class="label">母稿怎样写</div><p>${esc(r.current_support||'没有对应表达。')}</p><div class="label">少了什么</div><p>${esc(r.lost_meaning||'本条未发现核心差异丢失。')}</p><p class="note">${esc(r.reason)}</p>${r.suggested_human_line?`<div class="label">补回候选 · 尚未加入母稿</div><p class="proposed">${esc(r.suggested_human_line)}</p>`:''}<details><summary>看原文依据（${r.evidence.length}处）</summary>${r.evidence.map(e=>`<blockquote>${esc(e.quote)}</blockquote><span class="note">${esc(e.uid)}</span>`).join('')}</details></article>`).join('')}['seg','status','search'].forEach(id=>$(id).addEventListener('input',render));render();</script></html>'''
page=page.replace('</style>','body{overflow-wrap:anywhere}</style>').replace('__ROWS__',json.dumps(rows,ensure_ascii=False).replace('</','<\\/')).replace('__NAMES__',json.dumps(names,ensure_ascii=False))
(ROOT/'异质性逐条核对.html').write_text(page,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
