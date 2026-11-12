"""Generate the V2 viewer and factual delivery notes from final receipts."""
import argparse, html, shutil
from dag2 import ROOT,EVO,WORKS,read,sha

def build(preview=False):
    media=read(ROOT/'qa/v2_final_media.json');design=read(ROOT/'qa/v2_design.json');review=read(ROOT/'qa/v2_design_review.json')
    assert (preview or review['verdict']=='pass') and set(media)==set(WORKS) and all(v['pass'] for v in media.values())
    for w in WORKS:assert sha(ROOT/f'out/{w}_r54weave_DAG2_v2.mp4')==media[w]['video_sha256']
    pack=read(EVO/'runs/_reports/video_pack_r54weave.json');assert sha(pack['zip'])==pack['zip_sha256']
    sections=[];rows=[]
    for w,cfg in WORKS.items():
        f=read(ROOT/f'input/{w}.json');g=read(ROOT/f'plans/{w}_v2_graph.json');rail=read(ROOT/f'plans/{w}_v2_rail.json')
        buttons=''.join(f'<button onclick="seek(\'{w}\',{s["window"][0]})">{html.escape(o["label"])}</button>' for s,o in zip(g['segments'],rail['outline']))
        sections.append(f'<section><h2>{html.escape(cfg["title"])}</h2><video id="{w}" src="{w}_r54weave_DAG2_v2.mp4" controls preload="metadata"></video><details><summary>按故事片段回看</summary><div class="chapters">{buttons}</div></details></section>')
        rows.append(f'| {cfg["title"]} | {len(g["segments"])} | {sum(len(s["nodes"]) for s in g["segments"])} | {sum(len(s["edges"]) for s in g["segments"])} | {design[w]["local_blocks"]} | {design[w]["minimum_font"]}px | {media[w]["duration"]:.3f}s |')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>r54weave V2</title><style>*{box-sizing:border-box}body{margin:0;background:#0e1218;color:#e6e9ec;font:17px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1560px;margin:auto;padding:24px}section{margin:22px 0 64px}h1,h2{font-weight:400}h2{font-size:22px}video{width:100%;display:block;background:#0a0e13}summary{cursor:pointer;color:#abb9c7;margin-top:16px}.chapters{display:flex;flex-wrap:wrap;gap:8px;padding-top:12px}button{font:inherit;font-size:14px;background:#17202b;border:1px solid #334353;color:#cbd8e3;padding:8px 12px;border-radius:4px;cursor:pointer}img{width:100%}details{margin:20px 0}a{color:#9dd1dd}</style><main>'''+''.join(sections)+'''<details><summary>右栏三档折叠对比</summary><img src="右栏折叠对比_v2.png"></details><details><summary>局部文字出现的前后</summary><img src="局部文字动画_v2.png"></details></main><script>function seek(id,t){let v=document.getElementById(id);v.currentTime=t;v.scrollIntoView({behavior:'smooth',block:'center'});v.play()}document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(o=>{if(o!==v)o.pause()})))</script></html>'''
    (ROOT/'out/观看入口_v2.html').write_text(page,encoding='utf8')
    old=ROOT/'out/观看入口.html';backup=ROOT/'out/观看入口_v1.html'
    if old.exists() and not backup.exists():shutil.copyfile(old,backup)
    old.write_text(page,encoding='utf8')
    if preview:
        print('V2 viewing entry generated; final review remains pending, no final acceptance report written',flush=True);return
    text='''# r54weave 展示V2实际结果

本说明由 `report_v2.py` 读取成片QA生成。用户指出V1遗漏原珠子关系、音乐视觉偏离Op52及右栏内容过密，V2据此重做展示。

- 线和珠子作为独立节点，珠子之间保留原机器图的直接关系边，另一侧面、段内先后和不同理解不再混成连续段落。
- 去掉画面抬头、配色说明和小节/分钟定位。正文只移除定位字样及纯定位补充从句，原文和显示字符映射均保留，原定稿不改写；不新增替换正文。
- 底部实际调用原mamviz BALLS规则：现在固定中央，过去空心圆在左，未来实心圆在右，发声光点在中央移动；音乐区全宽370像素。半径沿原公式，上限27.75像素，避免旧数据长音产生过大的圆。独立的中央时间竖线及底部标记在音符间隙也可见，不靠伪造发声音符指示播放位置。
- 对局部文字依据原有定位分块，淡入/淡出。模型分块的逐字拼接必须等于原珠子正文。宽泛心理解释保持宽范围，不为了动画编造细时刻。
- 音乐颜色与当前可见的珠线文字联系共用调色，当前珠子节点也有同色标记；这是体验注意提示，不能据此宣称完成声部识别或逐音语义绑定。检查发现旧数据h是MIDI乐器编号，两首编号顺序不同，V2不将其默认为左右手。
- 右栏只有过去阶段的一行摘要和当前展开内容，提供极简/适中/展开三档预览；成片采用极简，只展开当前短语。原引用可使既有阶段标记亮起，不新增挤占空间的回望列表。

| 作品 | 段 | 珠子节点 | 原关系边 | 局部文字块 | 最小珠子字号 | 成片时长 |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

完整成片与三档比较位于 `out/`，当前入口为 `out/观看入口_v2.html`，通用的 `out/观看入口.html` 已指向V2；V1观看页另存。局部动画样片只截取原录音，不增加旁白。

所有27段检查文字分块完整、显示无定位标签、时间范围合法、图节点不重叠、缺字和音乐运动。两首完整视频通过全片解码及逐段编码后文字对照；原录音全曲解码PCM与成片完全一致。原写线DAG、合写文档、冻结输入、音符数据和ZIP校验保持原值。

实际边界：图片审查只覆盖所附画面与三帧变化，不等于完整主观观影或音乐听审。对齐和声部身份沿用旧数据，连接采用原确定性启发式，不宣称经乐谱确认的独立声部。宽泛定位保持宽泛。

证据为 `qa/v2_design.json`、`qa/v2_design_review.json`、`qa/v2_final_media.json`，模型原始输入/输出在 `runs/v2_*`，布局和标注在 `plans/*_v2_*`。V1及其原失败记录保留。
'''
    old=ROOT/'结果说明.md';backup=ROOT/'结果说明_V1.md'
    if old.exists() and not backup.exists():shutil.copyfile(old,backup)
    old.write_text(text,encoding='utf8');(ROOT/'结果说明_V2.md').write_text(text,encoding='utf8')
    print('V2 viewer and measured report generated; ZIP unchanged',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args();build(a.preview)
