from pathlib import Path
import json,html
from collections import Counter
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
d=read(R/'CONTENT.json'); c=read(R/'COVERAGE.json'); cm={x['id']:x for x in c}
findings=[]
selection=read(R/'ACTIVE_VERSIONS.json')
for filename in selection['reviews']:findings.extend(read(R/filename).get('reverse_findings',[]))
fixes=read(R/'EDITORIAL_FIXES.json') if (R/'EDITORIAL_FIXES.json').exists() else []
fixes+=read(R/'FINAL_EDITS.json') if (R/'FINAL_EDITS.json').exists() else []
rows=[]
for p in d['pages']:
 for b in p['blocks']:
  ids=set(b.get('meaning_ids',[]))&set(cm)
  ids.update(x['id'] for x in c if b['id'] in x.get('block_ids',[]))
  meanings=[cm[i] for i in sorted(ids)]
  reverse=[f for f in findings if f.get('block_id')==b['id']]
  remaining=[]
  for f in reverse:
   # A tracked explicit rewrite is reviewable evidence that the flagged wording was fixed.
   repaired=any(z.get('block_id')==b['id'] and z.get('old') and z['old'] in f['span'] and z.get('new','') in b.get('text','') and f['span'] not in b.get('text','') for z in fixes)
   if not repaired:remaining.append(f)
  counts=dict(Counter(x['status'] for x in meanings))
  verdict='unreviewed' if not meanings or counts.get('unreviewed') else 'unresolved_connection' if remaining else 'associated_meanings_full' if all(x['status']=='full' for x in meanings) else 'has_unretained_difference'
  rows.append(dict(segment=p['segment'],block_id=b['id'],label=b['label'],text=b['text'],verdict=verdict,status_counts=counts,meanings=meanings,original_reverse_findings=reverse,unresolved_reverse_findings=remaining))
out={'scope':'这是本轮所有成品块的关联原意与连接复核，不等于恢复历史每一次合并操作。全部关联项full仅说明所列项已保留，仍可查原稿反驳；不据块数计算合并成功率。','blocks':rows}
(R/'MERGE_CHECK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
e=html.escape
parts=[]
for x in rows:
 items=''.join('<li>'+e(i['id'])+' · '+e(i['status'])+' · '+e(i['meaning'])+'<br><small>'+e(i['reason'])+'</small></li>' for i in x['meanings'])
 flag=''.join('<p>待修连接：'+e(z['problem'])+'</p>' for z in x['unresolved_reverse_findings'])
 parts.append('<article><h2>'+e(x['block_id'])+' · '+e(x['label'])+'</h2><p>'+e(x['verdict'])+'</p><pre>'+e(x['text'])+'</pre>'+flag+'<ul>'+items+'</ul></article>')
(R/'合并与连接检查.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>合并与连接检查</title><style>body{max-width:1200px;padding:30px;margin:auto;background:#f7f4ed;color:#283d32;font:16px/1.9 "Microsoft YaHei",sans-serif}pre{font:inherit;white-space:pre-wrap;background:#fffdf7;padding:15px}article{border-top:1px solid #bbb;margin:30px 0}small{color:#65736a}li{margin:10px 0}a{color:#28665e}</style><h1>合并与连接检查</h1><p><a href="船歌·每段一页.html#S02">阅读页</a> · <a href="内容与原稿核对.html">逐项核对</a></p><p>'+e(out['scope'])+'</p>'+''.join(parts)+'</html>',encoding='utf-8')
print('blocks checked',len(rows),'unresolved connections',sum(bool(x['unresolved_reverse_findings']) for x in rows))
