from pathlib import Path
import json, html, hashlib

BASE=Path(r'D:\musicclaude\_bead_quality_20261017')
OLD=Path(r'D:\musicclaude\_bead_video_review_20261017')
ROOT=Path(r'D:\musicclaude\_bead_page_20261017')
ROOT.mkdir(exist_ok=True)
beads={b['segment']:b for b in json.loads((BASE/'editorial/FINAL_BEADS.json').read_text(encoding='utf-8'))}
specs=[
 {'segment':'S02','bars':'4–16','name':'第一主题','emphasis':['旋律刚往高处伸，声音反而收轻了。','安慰里已经有一点微痛。'],
  'reason':'前一句说明这份亲近里为什么还有小心；后一句说明重复的乐句没有停在同一种温柔里。强调的是段落内的关键关系，不能把“千言万语”或“叹息”单独放大当作结论。'},
 {'segment':'S07','bars':'51–61','name':'第二主题前半的延续','emphasis':['惦记的对象反而不那么清楚了。'],
  'reason':'这一段有区别的体验是：起初回想某个人或一段谈话，后来越来越沉入回想带来的感觉。原文用后面的具体感官把它说清楚；因此保留整个段落，不将其改成前后箭头或一句宣言。音乐收轻又推进的句子仍在同页。'},
 {'segment':'S13','bars':'103–110','name':'第二主题前半的再现','emphasis':['上面的声音一回回落下，近乎叹息；低处不肯让步'],
  'reason':'这里首先值得听清的是叹息与持续力量同时存在，才能理解后面的热烈与不适。笑容发僵只是帮助理解的比喻，按正文大小放在上下文里，不单独成为标题或一屏。'}
]
pages=[]
for s in specs:
    b=beads[s['segment']]
    body=html.escape(b['body'])
    for phrase in s['emphasis']:
        assert b['body'].count(phrase)==1
        body=body.replace(html.escape(phrase),'<strong>'+html.escape(phrase)+'</strong>')
    # Preserve every word and paragraph of the approved mother text.
    s['body']=b['body']
    s['source_bead_title']=b['title']
    s['source_uids']=b['sources']
    paras=body.split('\n\n')
    pages.append(f'''<section class="sheet" id="{s['segment']}" {'hidden' if s['segment']!='S02' else ''}>
      <header><div class="chapter">{s['segment']}<span>第 {s['bars']} 小节</span></div><h1>{s['name']}</h1></header>
      <div class="body">{''.join('<p>'+p+'</p>' for p in paras)}</div>
      <footer>肖邦 · 船歌 Op.60</footer></section>''')

template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>船歌 · 每段一页</title><style>
*{box-sizing:border-box}body{margin:0;background:#e7e5df;color:#30372f;font-family:'Microsoft YaHei','Segoe UI',sans-serif}.reviewbar{max-width:1280px;margin:20px auto 14px;display:flex;align-items:center;justify-content:space-between;padding:0 4px;gap:20px;font-size:13px;color:#62675f}nav{display:flex;gap:8px}button{font:inherit;border:1px solid #c7c9bd;background:transparent;padding:8px 16px;border-radius:3px;color:#394537;cursor:pointer}button.active{background:#3f5041;color:#fff;border-color:#3f5041}button:focus-visible,summary:focus-visible{outline:3px solid #ad8650;outline-offset:3px}.sheet{position:relative;max-width:1280px;aspect-ratio:16/9;min-height:680px;margin:0 auto;background:#f9f7f1;padding:45px 88px 52px;box-shadow:0 2px 10px #00000008}.sheet[hidden]{display:none}.chapter{font-size:14px;letter-spacing:1px;color:#6d7569}.chapter span{margin-left:18px;font-size:13px;letter-spacing:0}h1{font-size:24px;font-weight:500;margin:12px 0 0}header{padding-bottom:20px;border-bottom:1px solid #dfdfd3}.body{max-width:1010px;font-size:23px;line-height:1.95;letter-spacing:.02em;margin-top:20px}.body p{margin:0 0 15px}.body strong{font-weight:600;color:#35503d;text-decoration:underline;text-decoration-color:#c0cbb5;text-decoration-thickness:2px;text-underline-offset:5px}footer{position:absolute;bottom:24px;font-size:12px;color:#8a8e82}.notes{max-width:1150px;margin:25px auto;padding:0 15px;font-size:14px;line-height:1.9;color:#687061}summary{cursor:pointer}a{color:#466346}.notes p{max-width:1000px}.notes small{font-size:12px}
@media(max-width:900px){.reviewbar{padding:0 20px}.sheet{padding:32px 38px 60px;min-height:0;aspect-ratio:auto}.body{font-size:21px;line-height:1.95}h1{font-size:22px}footer{bottom:20px}}
@media(max-width:520px){.reviewbar{align-items:flex-start;flex-direction:column;gap:10px}.sheet{padding:27px 22px 58px}.body{font-size:19px;line-height:1.95}.body p{margin-bottom:20px}.notes{padding:0 22px}}
</style><div class="reviewbar"><span>每段一页 · 这三个 S 各自保持同一页</span><nav aria-label="选择音乐段"><button data-id="S02" class="active">S02</button><button data-id="S07">S07</button><button data-id="S13">S13</button></nav></div><main>__PAGES__</main><div class="notes"><details><summary>本页的取舍说明</summary><p id="reason"></p><p>正文逐字保留已认可母稿；去掉此前另拟的口号标题，取消段内分镜和逐句切换。强调句与正文同样大小。这里只用这三个样例校正呈现方向，没有宣称语言或观看效果已通过用户验收。</p><small>尚未绑定录音。这是固定页面样例，段内不自动换字、不逐句点亮。原来的异质性审计仍独立保留。</small></details></div><script>const DATA=__DATA__;function show(id){if(!DATA.some(x=>x.segment===id))id='S02';document.querySelectorAll('.sheet').forEach(s=>s.hidden=s.id!==id);document.querySelectorAll('nav button').forEach(b=>{b.classList.toggle('active',b.dataset.id===id);b.setAttribute('aria-pressed',String(b.dataset.id===id))});document.getElementById('reason').textContent=DATA.find(x=>x.segment===id).reason;if(location.hash!=='#'+id)history.replaceState(null,'','#'+id)}document.querySelectorAll('nav button').forEach(b=>b.addEventListener('click',()=>show(b.dataset.id)));show((location.hash.match(/S\\d{2}/)||['S02'])[0]);addEventListener('hashchange',()=>show((location.hash.match(/S\\d{2}/)||['S02'])[0]));</script></html>'''
page=template.replace('__PAGES__','\n'.join(pages)).replace('__DATA__',json.dumps(specs,ensure_ascii=False).replace('</','<\\/'))
(ROOT/'每段一页.html').write_text(page,encoding='utf-8')
(ROOT/'PAGE_CONTENT.json').write_text(json.dumps({'version':2,'layout':'one_page_per_segment','intra_segment_switching':False,'body_verbatim':True,'pages':specs,'mother_sha256':hashlib.sha256((BASE/'editorial/FINAL_BEADS.json').read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
# Preserve the rejected preview, then update the existing user-facing path too.
archive=OLD/'archive_rejected_preview'
archive.mkdir(exist_ok=True)
old_file=OLD/'分镜与异质性预览.html'
if not (archive/old_file.name).exists():
    (archive/old_file.name).write_bytes(old_file.read_bytes())
old_file.write_text(page,encoding='utf-8')
(ROOT/'说明.txt').write_text('这版修正为一个S一页。三个样例的正文逐字保留母稿，取消所有段内卡片切换和口号式大标题。\nS02强调收轻与重复后的微痛；S07强调回想对象退后、感受本身成为中心；S13强调上方叹息与低处力量并存。其余比喻留在正文，不单独放大。\n尚未绑定录音。旧分镜已被否定，不作为当前推荐。此前异质性审计没有因此作废。\n',encoding='utf-8')
print(json.dumps({'output':str(ROOT/'每段一页.html'),'pages':len(specs),'body_verbatim':True},ensure_ascii=False))
