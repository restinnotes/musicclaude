from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
e=html.escape; d=read(R/'reviews/S02_model_comparison.json')
parts=['<h1>同一S02输入的真实模型实验</h1><p><a href="模型输出对照.html">完整原始响应及运行状态</a> · <a href="内容与原稿核对.html">本轮成品核对</a></p><p>这是一次样本比较；未做消融实验，不据此宣称模型的普遍排名。局部原意保留和整段是否添出关系分开检查：单项能读到，仍可能被错误地串成同一经历。</p>']
parts.append('<table><tr><th>输出</th><th>完整保留的旧原意</th><th>正文字符数</th><th>结构</th></tr>')
for m in ['gpt','flash']:
 s=d['summary'][m]; t=s['text_metrics']
 parts.append('<tr><td>'+e(m)+'</td><td>'+e(s['full_fraction'])+'</td><td>'+str(t['body_characters_including_punctuation'])+'</td><td>'+str(t['block_count'])+'块；最长一块'+str(t['longest_block_characters'])+'字</td></tr>')
parts.append('</table><p>85项包括少量事实和错位候选，与全局858个局部体验的固定分母不同。两种数字不可互换。自报ID和引文未直接算成正文保留。</p>')
for x in d['key_five_differences']:
 parts.append('<article><h2>'+e(x['topic'])+'</h2><p>GPT：'+e(x['gpt'])+'</p><p>Flash：'+e(x['flash'])+'</p></article>')
parts.append('<h2>哪些机制表现出作用</h2><ul>'+''.join('<li>'+e(x)+'</li>' for x in d['mechanism_assessment']['useful_observed'])+'</ul><p>'+e(d['mechanism_assessment']['causal_limit'])+'</p>')
parts.append('<h2>逐项判断与精确落点</h2><p><a href="reviews/S02_model_comparison.json">打开85项完整判定及170个模型判读、原文与正文区间</a></p><p>所有原始模型响应均保留；Muse三次在本地服务就绪前失败，未生成正文，不据此评价其内容能力。</p>')
parts.append('<h2>反向发现</h2>')
for x in d['reverse_findings']:
 parts.append('<article><h3>'+e(x['model']+' · '+x['id'])+'</h3>'+''.join('<blockquote>'+e(z['quote'])+'</blockquote>' for z in x['output_spans'])+'<p>'+e(x['judgment'])+'</p></article>')
(R/'模型实验判读.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>模型实验判读</title><style>body{max-width:1050px;margin:30px auto;padding:20px;background:#f7f4ed;color:#2c3831;font:17px/1.85 "Microsoft YaHei",sans-serif}td,th{padding:12px;border:1px solid #bbb}table{border-collapse:collapse}article{padding:12px 0;border-top:1px solid #ccc}blockquote{border-left:3px solid #82988c;padding:10px 20px;margin-left:0;background:#fffdf8}a{color:#27675a}</style>'+''.join(parts)+'</html>',encoding='utf-8')
print('model findings view built')
