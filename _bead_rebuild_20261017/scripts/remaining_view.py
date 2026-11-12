from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
e=html.escape;c={x['id']:x for x in read(R/'COVERAGE.json')};g=read(R/'FIXED_DENOMINATOR_COMPARISON.json');parts=[]
for x in g:
 if x['new_status']=='full':continue
 z=c[x['best_id']]
 parts.append('<article data-status="'+e(z['status'])+'"><h2>'+e(z['id']+' · '+z['status'])+'</h2><p>'+e(z['meaning'])+'</p><p>'+e(z['reason'])+'</p><blockquote>'+e(z.get('span','') or '当前正文没有可认领的对应句。')+'</blockquote><small>同义组：'+e('、'.join(x['canonical_members']))+'</small></article>')
intro='<h1>仍未完整保留的差别</h1><p><a href="船歌·每段一页.html#S02">内容阅读页</a> · <a href="内容与原稿核对.html">全部逐项复核</a></p><p>这里列出固定858组比较范围中仍未判full的全部项目；partial、omitted、pending和not_applicable均未移出分母。它们包括实际缺失、复核分歧、来源错位和未核音乐条件，不能都概括成漏写，也不能都当作已保留。</p><p>S02经过第二轮更保守复核，部分合场、主体与范围判定存在分歧；未明确解决的项目保守列为未完整，不采用较高一轮的计数。<a href="AUDIT_DISAGREEMENTS.json">逐项分歧原记录</a></p>'
(R/'尚未完整保留.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>尚未完整保留</title><style>body{max-width:1000px;margin:30px auto;padding:20px;background:#f7f4ec;color:#293b32;font:17px/1.85 "Microsoft YaHei",sans-serif}article{border-top:1px solid #b7c0b5;padding:20px 0}blockquote{border-left:3px solid #9aa99d;padding-left:20px;margin-left:0}a{color:#286a59}small{color:#657367}</style>'+intro+''.join(parts)+'</html>',encoding='utf-8')
print('remaining canonical groups',len(parts))
