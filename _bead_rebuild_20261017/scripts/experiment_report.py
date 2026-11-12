from pathlib import Path
import json,html,re,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
rows=[]
for d in sorted((R/'scripts'/'call_results').iterdir()):
 m=d/'metadata.json'
 if not m.exists():continue
 x=read(m);rows.append({k:x.get(k) for k in ['job_id','status','requested_model','prompt_sha256','prompt_characters','response_chars','seconds','errors','observed']})
(R/'MODEL_RUNS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
parts=[]
for x in rows:
 d=R/'scripts'/'call_results'/x['job_id'];response=(d/'response.txt').read_text(encoding='utf-8') if (d/'response.txt').exists() else ''
 parts.append('<section><h2>'+html.escape(x['job_id'])+'</h2><p>'+html.escape(str(x['status'])+' / '+str(x['requested_model'])+' / '+str(x['seconds'])+' 秒')+'</p><p>输入内容哈希：<code>'+html.escape(str(x['prompt_sha256']))+'</code></p><p>'+html.escape('; '.join(x.get('errors') or []))+'</p><pre>'+html.escape(response or '没有生成可评阅的正文；失败不能当作模型质量证据。')+'</pre></section>')
intro='''<h1>本轮真实模型输出</h1><p><a href="船歌·每段一页.html#S02">编辑成品</a> · <a href="内容与原稿核对.html">逐项核对</a></p><p>Flash/Muse 的每一段使用同一份完整 UTF-8 输入。GPT-6w 的 S02 因通道正文限制使用相同 S02.txt 作真实附件，另附一句读取附件的任务包络；这构成内容相同、传递方式不同的比较，不能声称字节级请求完全相同。主编辑的成品单独保存，未覆盖任何模型响应。</p><p>Muse 的本地 standalone 服务在就绪以前退出，均保留失败记录。Flash 可生成丰富长稿，但仍会把独立动因合在同一类别，并写出过强的意图判断；本轮不按模型自评选冠军。局部运行不能推出某模型普遍更好。</p>'''
(R/'模型输出对照.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>模型输出对照</title><style>body{max-width:1200px;margin:35px auto;padding:0 25px;background:#f7f5ef;color:#263b31;font:16px/1.8 "Microsoft YaHei",sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;padding:20px;background:#fffdf7;border:1px solid #ccc}section{margin-top:35px;border-top:1px solid #abb}code{overflow-wrap:anywhere}a{color:#256258}</style>'+intro+''.join(parts)+'</html>',encoding='utf-8')
print([(x['job_id'],x['status']) for x in rows])
