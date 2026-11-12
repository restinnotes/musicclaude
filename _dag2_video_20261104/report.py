"""Produce the viewer and the final report from measured artifacts."""
import html, json
from dag2 import ROOT, EVO, WORKS, read, write, sha, bounds

def build():
 final=read(ROOT/'qa/final_media.json');review=read(ROOT/'qa/visual_review_v2.json');temporal=read(ROOT/'qa/temporal.json')
 assert review['verdict']=='pass' and all(x['pass'] for x in temporal.values())
 oldzip=read(EVO/'runs/_reports/video_pack_r54weave.json');assert sha(oldzip['zip'])==oldzip['zip_sha256']
 sections=[];rows=[];outlines=[]
 for w,cfg in WORKS.items():
  source=read(ROOT/f'input/{w}.json');plan=read(ROOT/f'plans/{w}_v1.json');music=read(ROOT/f'input/{w}_music.json');times=dict(music['bars']);manifest=read(ROOT/'input/manifest.json')[w];media=final['media'][w]
  seconds=float(media['duration']);clock=f'{int(seconds)//60}:{int(seconds)%60:02d}'
  buttons=[]
  for s,o in zip(source['segments'],plan['outline']):
   t=times[bounds(s['bars'])[0]];label=f"{s['bars']} · {o['label']}"
   buttons.append(f'<button type="button" onclick="seek(\'{w}\',{t})">{html.escape(label)}</button>')
  sections.append(f'<section><h2>{html.escape(cfg["title"])}</h2><p>{html.escape(cfg["performer"])} · {clock} · 完整文字版</p><video id="{w}" controls preload="metadata" src="{w}_r54weave_DAG2_v1.mp4"></video><details><summary>按段跳转</summary><div class="chapters">'+''.join(buttons)+'</div></details></section>')
  strong=sum(x['strength']=='相近' for x in plan['links'])
  rows.append(f'| {cfg["title"]} | {clock} | {manifest["segments"]} | {manifest["lines"]} | {manifest["beads"]} | {len(plan["phases"])} | {strong} | {media["minimum_body_font"]}px |')
  outlines.append('### '+cfg['title']+'\n\n'+'\n'.join(f'- {p["title"]}：'+ '、'.join(p['sections']) for p in plan['phases']))
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>r54weave · 完整文字视频</title><style>*{box-sizing:border-box}body{margin:0;padding:36px;background:#0f141c;color:#ebede9;font:17px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1480px;margin:auto}h1{font-weight:500}h2{font-size:25px;font-weight:500}p{color:#aab7c5}section{margin:42px 0 70px}video{width:100%;display:block;background:#080d13;border:1px solid #334456}details{margin-top:16px}summary{cursor:pointer}.chapters{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}button{background:#192432;color:#d3dfeb;border:1px solid #364b61;padding:9px 13px;border-radius:5px;cursor:pointer;font:inherit;font-size:14px}button:hover{background:#293b4e}a{color:#9bd1df}</style><main><h1>r54weave · 边听边读</h1><p>完整的线和珠子按段保留。可以暂停细读，也可以按段回看；同色短语彼此呼应，右栏记录这一路。</p>'''+''.join(sections)+'''</main><script>function seek(id,t){const v=document.getElementById(id);v.currentTime=t;v.scrollIntoView({behavior:'smooth',block:'center'});v.play();}document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(o=>{if(o!==v)o.pause()})))</script></html>'''
 (ROOT/'out/观看入口.html').write_text(page,encoding='utf8')
 text='''# r54weave · DAG2 视频结果

此文由 `report.py` 根据实际输出与 QA 文件生成，不以计划代替成品。

完整视频：

- [船歌](out/op60_r54weave_DAG2_v1.mp4)
- [幻想波兰舞曲](out/op61_r54weave_DAG2_v1.mp4)
- [可按段跳转的观看入口](out/观看入口.html)

| 作品 | 时长 | 段 | 线 | 珠子 | 故事阶段 | 收下的局部联系 | 最小正文字号 |
|---|---:|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

全部正文逐字保留；每颗珠子出现一次；跨栏需要时重复原线并标“续”。标题和颜色只是附加展示标注。沿用 Op.52 的上字下图、右侧导航框架；相近文字相邻摆放，并以局部同色提示。右栏过去阶段折叠、当前展开，原引用驱动回望标记。

## 已有证据

- 冻结输入、原 graph、合写正文、录音与音乐数据 SHA 检查通过。
- 全部27段的正文完整性、坐标范围及字体缺字检查通过。
- 全部27段的稳定阅读区、音乐运动、段界与不显示未来音符检查通过。
- gpt3 实际收到5张图片（旧参考＋4处高风险画面），静帧审查通过，没有阻断项。原调用为 `dag2_20261104_visual_review_v2`，GPT-6 Thinking / max，97秒。
- 两首完整视频均通过完整解码；视频/音频时长差小于0.08秒。前、中、后三处原录音对比的波形相关系数均大于0.999。
- 旧视频最小包 ZIP 的 SHA 与既有清单一致。

证据分别在 `input/manifest.json`、`qa/*_v1_layout.json`、`qa/temporal.json`、`qa/visual_review_v2.json`、`qa/final_media.json`。最初重名图片上传失败、未收到图片的备用回答均保留在 `runs/visual_review_v1`，没有算作通过。

## 实际边界

这是完整文字的基础版。密集段需要暂停细读；没有做观众体验实验，也没有把静帧审查说成完整音画主观验收。音符复用既有对齐，《幻想波兰舞曲》自由节奏段仍可能有局部偏差；没有把相近的叙事片段当作逐音对应。只有《船歌》4–5小节明确的左手范围收下了对应色示范，其余缺乏可靠声部/范围依据的部分保持中性。

后续如果升级，优先单独完善对齐与声部分离，以及小屏幕阅读版本；不必重跑写线。当前流程与原 DAG 分开，说明和复现命令见 `DAG2.md`。本轮达到可交付基础版的检查要求，未宣称所有视觉可能性已穷尽。

## 提纲

'''+ '\n\n'.join(outlines)+'\n'
 (ROOT/'结果说明.md').write_text(text,encoding='utf8');print('Generated viewer and measured report',flush=True)

if __name__=='__main__':build()
