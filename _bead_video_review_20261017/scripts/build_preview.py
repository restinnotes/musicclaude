from pathlib import Path
import json, hashlib, html, re

raise SystemExit('旧分镜已被用户否定。请运行同目录 build_segment_pages.py，生成每个S一页的修订版。')

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(r'D:\musicclaude\_bead_quality_20261017')
beads = json.loads((BASE/'editorial/FINAL_BEADS.json').read_text(encoding='utf-8'))
units = json.loads((BASE/'sources/units.json').read_text(encoding='utf-8'))

# Display candidates, not new musical sections or performance timings.
cases = [
 dict(segment='S02', bars='4–16', title='肩膀贴着肩膀，声音却更轻', frames=[
  dict(module='scene', cue='歌声进入时；具体秒点待录音对齐', headline='肩膀贴着肩膀，声音放得极低。', lines=['只要身边的人听见就够了。'], note='保留人物、距离、动作。无需先读“亲密、克制”两个标签。', origin='mother'),
  dict(module='parallel', cue='旋律向上而声音收轻的乐句', headline='千言万语涌上来，第一句话却像叹息。', lines=['旋律往高处伸。','声音反而收轻了。'], note='两栏表示同一刻并存，不能用箭头伪装成先后。观众先看一句完整的话，再留意声音。', origin='mother'),
  dict(module='detail', cue='可替换的感官侧面；不强行追加一屏', headline='温热的风裹在皮肤上，甚至有些黏稠。', lines=['亲近里，也有一点倦意。'], note='这是一张替换候选。实际乐句容不下时，不能为了覆盖率快速轮播。', origin='mother', optional=True),
  dict(module='variation', cue='相似句尾再现时；逐乐句核对', headline='同一句话，仍想再说一遍。', lines=['相似的尾音','下面的水波换了颜色。','安慰里，已经有一点微痛。'], note='保留固定的“相似尾音”，只更新变化的部分。这里不是精确三次计数，也不是给音符逐字配字幕。', origin='mother'),
  dict(module='scene', cue='后半回应与呼气处；具体秒点待录音对齐', headline='终于相视，听懂了一点什么。', lines=['却没有急着把话说尽。'], note='与开头同用情景模块，观众无需重新学习布局。', origin='mother')],
 alternatives=[
  dict(title='眼前的这一刻', text='不敢看太用力，怕把这片刻看碎了。', uid='SRC-muse-int-1-U03', quote='像靠在船舷上，眼睛看着远处，不敢看太用力，怕把这片刻看碎了。', distinction='对象仍在眼前；怕当下被惊碎。母稿只保留了珍惜与易碎，没完整说出这种时间位置。'),
  dict(title='回想已经过去的事', text='知道回不去了，却也不想回去。不哭，但眼眶是热的。', uid='SRC-muse-int-2-U03', quote='你想起一段很好的过去，你知道回不去了，但你此刻并不想回去', distinction='对象已是过去；承认失去，却不要求重来。不能与上一种简单合成“怕失去”。')]),
 dict(segment='S07', bars='51–61', title='已经不是在想谁，是舍不得停止感觉', frames=[
  dict(module='scene', cue='相似歌声更满、更密地回来时', headline='决定睡了，脑子却又把那段谈话放了一遍。', lines=['没有新发生的事，身体里的热度却又回来。'], note='保留日常动作与身体反应，省掉层层解释。', origin='mother'),
  dict(module='change', cue='整段体验的阅读展开；不是新增小节边界', headline='渐渐地，惦记的人反而没那么清楚了。', lines=['起初，想着某个人、某件事。','后来，舍不得停止这种感觉。'], note='这次箭头表示原稿明确写出的心理转变；不把它当作乐谱的精确事件。', origin='mother'),
  dict(module='parallel', cue='段内收轻又推起处；不规定全段直线上升', headline='舒服，却越来越难同它拉开距离。', lines=['气味、身体感觉、幻想和快感混在一起。','温柔里面，已经有了坐不住的力量。'], note='并排保留感官沉醉与不安；不改成“情绪复杂”或“沉醉→焦虑”。', origin='mother')],
 alternatives=[dict(title='同一段的另一种听法', text='谈得太深，两个人都静了下来。话暂时跟不上感受。', uid='SRC-gpt56w-int-2-U06', quote='很像一次非常深入的谈话之后，两个人都沉默下来。', distinction='心理上的安静不等于声音全部变弱，更不等于这里有 sfogato。它和“脑子不停重播”是不同的注意中心，应作为另一版观看路径，不能硬接成必然先后。')]),
 dict(segment='S13', bars='103–110', title='说出来了，分量却没有减轻', frames=[
  dict(module='parallel', cue='103起，上声部下落与低处支撑并存', headline='话已经说出口，还想再确认一遍。', lines=['上面的声音一回回落下，近乎叹息。','低处那股力量，仍然不肯让步。'], note='版面保留两个同时发生的动作。不能一句“更激动”抹平，也不能把叹息当作全段平息。', origin='mother'),
  dict(module='detail', cue='后半声音聚紧、摩擦加重处', headline='笑着笑着，表情忽然有一点僵。', lines=['热烈还在，里面却有一根刺。'], note='用微小的人物动作让观众迅速接近感受。无需先展示“反讽、矛盾、复杂性”。', origin='mother'),
  dict(module='parallel', cue='110段末花饰；不移用111的 calando', headline='话音已有了转圜，心里却还绷着。', lines=['花饰向高处伸去，再落下来。','说出来之后，分量没有减轻。'], note='最后留住这一屏，待录音确定何时撤下；不靠频繁变化证明同步。', origin='mother')],
 alternatives=[])
]

for c in cases:
 c['mother'] = next(b['body'] for b in beads if b['segment']==c['segment'])
 for i,f in enumerate(c['frames'],1):
  f['id']=f"{c['segment']}-D{i:02}"
  f['start_seconds']=None
  f['end_seconds']=None
  f['visible_characters']=len(''.join([f['headline']]+f['lines']))
  f['source_bead']=c['segment']
 for a in c['alternatives']:
  assert a['quote'] in units[a['uid']]['text'], a['uid']
  a['original_unit']=units[a['uid']]['text']

payload=dict(version='display-study-1', musical_segments_unchanged=True,
 recording=None, timing_status='unbound', claims_reading_speed_improvement=False,
 cases=cases)
(ROOT/'DISPLAY_STUDY.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')

template = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>让意思留住，让眼睛轻一点 · 船歌</title>
<style>
:root{--paper:#f4f0e8;--ink:#203c38;--muted:#6d7770;--gold:#b29362;--line:#d7d9cc}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:'Microsoft YaHei','Segoe UI',sans-serif}button{font:inherit;cursor:pointer;border:1px solid var(--line);border-radius:30px;background:transparent;color:inherit;padding:9px 18px}button:hover,button.active{background:var(--ink);color:white}button:focus-visible{outline:3px solid var(--gold);outline-offset:3px}.wrap{max-width:1240px;margin:auto;padding:34px 32px}header{display:flex;align-items:center;justify-content:space-between;gap:24px}header small{letter-spacing:2px;color:var(--muted)}h1{font:500 30px/1.4 'Microsoft YaHei',sans-serif;margin:10px 0}nav{display:flex;gap:8px}.intro{font-size:14px;color:var(--muted);line-height:1.8;margin:16px 0 24px}.stage{position:relative;aspect-ratio:16/9;background:#173531;border-radius:6px;overflow:hidden;color:#f7f3e9;padding:5% 7%;display:flex;flex-direction:column;justify-content:center}.stage:after{content:'';position:absolute;inset:auto -10% -32% -10%;height:55%;border:1px solid #f3e7c320;border-radius:50%;pointer-events:none}.eyebrow{position:absolute;top:7%;left:7%;font-size:13px;letter-spacing:2px;color:#b9c9bd}.stage h2{font:500 clamp(24px,3.4vw,43px)/1.55 'Microsoft YaHei',sans-serif;margin:10px 0 26px;max-width:920px}.lines{font-size:clamp(16px,1.8vw,24px);line-height:1.85;color:#d9e1d9}.parallel .lines{display:grid;grid-template-columns:1fr 1fr;gap:28px}.parallel .lines div{border-top:1px solid #b29362;padding-top:16px}.change .lines{display:flex;align-items:center;gap:32px}.change .lines div+div:before{content:'→';color:#bcaa7d;margin-right:25px}.detail h2{max-width:760px}.variation .lines{display:grid;grid-template-columns:0.7fr 1fr;gap:5px 32px}.variation .lines div:first-child{grid-row:span 2;border-right:1px solid #b29362;display:flex;align-items:center;color:#c9b58a}.foot{position:absolute;bottom:6%;left:7%;right:7%;display:flex;justify-content:space-between;font-size:12px;color:#a8bbb0}.controls{display:flex;justify-content:space-between;gap:20px;align-items:center;margin:16px 0}.dots{display:flex;gap:7px;flex-wrap:wrap}.dots button{padding:8px 13px;font-size:12px}.next{display:flex;gap:8px}.caption{padding:16px 20px;border-left:3px solid var(--gold);background:#ebe9df;font-size:14px;line-height:1.8}.caption strong{font-weight:500;color:#234c43}details{border-top:1px solid var(--line);margin-top:25px;padding-top:17px}summary{cursor:pointer;font-size:16px}article{font-size:16px;line-height:1.95;max-width:900px;margin-top:20px}.altgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}.alt{border:1px solid var(--line);padding:24px;background:#faf8f2}.alt h3{font-size:13px;color:var(--muted);font-weight:500}.alt p{font:500 22px/1.7 'Microsoft YaHei',sans-serif}.alt .why{font:14px/1.9 'Microsoft YaHei',sans-serif;color:var(--muted)}.alt blockquote{margin:15px 0;padding-left:15px;border-left:2px solid var(--gold);font-size:14px;line-height:1.8}.tiny{font-size:12px;color:var(--muted);line-height:1.8}.principles{display:grid;grid-template-columns:repeat(3,1fr);gap:25px;margin:35px 0}.principles h3{font-weight:500;font-size:17px}.principles p{font-size:14px;line-height:1.9;color:var(--muted)}footer{margin:30px 0 10px;font-size:12px;line-height:1.9;color:var(--muted)}
@media(max-width:720px){.wrap{padding:20px 14px}header{display:block}nav{margin-top:15px}h1{font-size:24px}.stage{min-height:440px;aspect-ratio:auto;padding:75px 25px}.stage h2{font-size:28px}.parallel .lines{grid-template-columns:1fr;gap:12px}.lines{font-size:18px}.change .lines{display:block}.change .lines div+div:before{content:'↓';display:block}.controls{align-items:flex-start;flex-direction:column}.altgrid,.principles{grid-template-columns:1fr}.eyebrow{left:25px;top:25px}}
</style><div class="wrap"><header><div><small>CHOPIN · BARCAROLLE · OP.60</small><h1>让意思留住，让眼睛轻一点。</h1></div><nav id="nav"></nav></header>
<p class="intro">分镜阅读试样 · 手动切换，无音频、无假定秒点。深绿色画面是观众看到的候选文字；下面是审稿说明。保留现版母稿，试着改变呈现方法。</p>
<section id="stage" class="stage" aria-live="polite"></section><div class="controls"><div class="dots" id="dots"></div><div class="next"><button id="prev" aria-label="上一张">← 上一张</button><button id="next" aria-label="下一张">下一张 →</button></div></div><div class="caption" id="caption"></div>
<details><summary>读原有母稿：这些句子原来怎样连在一起</summary><article id="mother"></article></details>
<details id="altbox"><summary>不同意思怎样保留，而不是强行合成一种心情</summary><p class="tiny">下面是另一条观看路径的候选，不与主画面同时挤上屏。放进这里不等于已在视频里覆盖；导出视频仍须明确选择及记录。</p><div id="alternatives" class="altgrid"></div></details>
<div class="principles"><div><h3>相同布局，承载不同关系</h3><p>同一刻并存，用两栏；确实发生转变，才用前后；相同乐句回返，保留旧位置，只换有变化的一句。</p></div><div><h3>让句子继续说人话</h3><p>“笑着笑着，表情忽然有一点僵。”可以独占一屏。无需先翻译成“喜悦中的不安”，再要求观众翻译回来。</p></div><div><h3>让音乐决定何时值得换</h3><p>当前画面仍成立，就留着。不是每个小节都要换，也不是每个候选都必须上屏。实际停留时长须选定录音后试听校准。</p></div></div>
<footer>本页为展示研究，不是已经验证过的成片。S01–S14 音乐结构没有更改。多个展示画面只是同一段内部的呈现候选。S13 的“收退”须随具体演奏另做版本，不能从文字凭空确定。未开展观众阅读速度或理解率测试。</footer></div>
<script>const DATA=__DATA__;let ci=0,fi=0;const $=id=>document.getElementById(id);const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function render(){const c=DATA.cases[ci],f=c.frames[fi];$('nav').innerHTML=DATA.cases.map((x,i)=>`<button class="${i===ci?'active':''}" onclick="selectCase(${i})">${x.segment} · ${x.bars}</button>`).join('');$('stage').className='stage '+f.module;$('stage').innerHTML=`<div class="eyebrow">船歌 · ${c.segment} · 第 ${c.bars} 小节</div><h2>${esc(f.headline)}</h2><div class="lines">${f.lines.map(x=>`<div>${esc(x)}</div>`).join('')}</div><div class="foot"><span>CHOPIN / OP.60</span><span>${fi+1} / ${c.frames.length}</span></div>`;$('dots').innerHTML=c.frames.map((x,i)=>`<button class="${i===fi?'active':''}" onclick="selectFrame(${i})">${i+1}${x.optional?' · 可替换':''}</button>`).join('');$('caption').innerHTML=`<strong>${esc(f.cue)}</strong><br>${esc(f.note)} <span class="tiny">（本屏 ${f.visible_characters} 字符，含标点；不是阅读速度达标证明。）</span>`;$('mother').innerHTML=c.mother.split('\n\n').map(x=>'<p>'+esc(x)+'</p>').join('');$('alternatives').innerHTML=c.alternatives.map(a=>`<div class="alt"><h3>${esc(a.title)}</h3><p>${esc(a.text)}</p><div class="why">${esc(a.distinction)}</div><blockquote>${esc(a.quote)}</blockquote><span class="tiny">原A：${esc(a.uid)} · 展示句有编辑缩写</span></div>`).join('');$('altbox').hidden=!c.alternatives.length;location.hash=c.segment+'-'+(fi+1)}function selectCase(i){ci=i;fi=0;render()}function selectFrame(i){fi=i;render()}function move(d){fi=(fi+d+DATA.cases[ci].frames.length)%DATA.cases[ci].frames.length;render()}$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')move(1);if(e.key==='ArrowLeft')move(-1)});const hash=location.hash.match(/(S\d+)-(\d+)/);if(hash){let n=DATA.cases.findIndex(c=>c.segment===hash[1]);if(n>=0){ci=n;fi=Math.min(+hash[2]-1,DATA.cases[ci].frames.length-1);fi=Math.max(0,fi)}}render();</script></html>'''
(ROOT/'分镜与异质性预览.html').write_text(template.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')

lines=['# 视频展示试样：保留人话，只改变组织方式','', '本文件提供 3 段、11 张候选画面（含 1 张替换画面），以及 3 条另一观看路径的候选。不是把 11 张都强制排进最终视频。尚未绑定录音，不提供臆测秒点。','']
for c in cases:
 lines += [f"## {c['segment']} · {c['bars']} 小节",'']
 for f in c['frames']:
  lines += [f"### {f['id']} · {f['module']}"+(' · 替换候选' if f.get('optional') else ''),'',f['headline'],'']+['- '+x for x in f['lines']]+['',f"呈现：{f['note']}",f"锚点：{f['cue']}",'']
 for a in c['alternatives']:
  lines += [f"另一听法：{a['title']}",'',a['text'],'',a['distinction'],f"原文（{a['uid']}）：{a['quote']}",'']
(ROOT/'DISPLAY_STUDY.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'cases':len(cases),'frames':sum(len(c['frames']) for c in cases),'alternatives':sum(len(c['alternatives']) for c in cases),'mother_sha256':hashlib.sha256((BASE/'editorial/FINAL_BEADS.json').read_bytes()).hexdigest()},ensure_ascii=False))
