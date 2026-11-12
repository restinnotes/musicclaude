"""Render approved exact-span annotations; source text is never rewritten."""
import json

import experiment_batch as B
import span_links as S

PALETTE = ('#377b68', '#9a642d', '#616eab', '#a35873', '#427f98', '#7f7936', '#885da0', '#a55740')


def visual_groups(section):
    """One color per connected, overlapping set of line spans, not per bead."""
    groups = []
    for link in sorted(section['links'], key=lambda x: (x['line_id'], x['line_span']['start'])):
        span = link['line_span']
        group = groups[-1] if groups else None
        if group is None or group['line_id'] != link['line_id'] or span['start'] >= group['end']:
            group = {'id': f"{section['work']}_{section['sec']}_G{len(groups)+1:02}",
                     'line_id': link['line_id'], 'start': span['start'], 'end': span['end'],
                     'color_hex': PALETTE[len(groups) % len(PALETTE)], 'link_ids': []}
            groups.append(group)
        group['end'] = max(group['end'], span['end'])
        group['link_ids'].append(link['id'])
        link['visual_group'] = group['id']
        link['color_hex'] = group['color_hex']
    section['visual_groups'] = groups

TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>珠子与线 · 片段对应样稿</title>
<style>
:root{color-scheme:light;--ink:#243530;--muted:#68766e;--paper:#f5f4ef;--border:#dedfd6;--green:#315f4d}
*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font-family:"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.8}button,select{font:inherit}button{cursor:pointer}header,main,footer{max-width:1330px;margin:auto;padding:28px 40px}header{padding-bottom:12px}.eyebrow{font-size:12px;letter-spacing:.18em;color:var(--green)}h1{font-family:Georgia,"Songti SC",serif;font-weight:500;font-size:34px;margin:8px 0}header p{color:var(--muted);max-width:880px;margin:6px 0 18px}.toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap}select,.outline{border:1px solid #cbd1c6;border-radius:8px;padding:7px 13px;background:#fafbf7;color:var(--ink)}.toolbar .count{margin-left:auto;color:var(--muted);font-size:13px}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 8px}.tab{padding:7px 15px;border:1px solid transparent;background:transparent;color:var(--muted);border-radius:30px}.tab[aria-pressed=true]{background:var(--green);color:#fff}.stage-title{display:flex;justify-content:space-between;gap:15px;border-top:1px solid var(--border);padding-top:22px}.stage-title h2{font-size:20px;font-weight:500;margin:0}.stage-title p{font-size:13px;margin:0;color:var(--muted)}.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:12px 0 20px}.legend span:first-child{border-bottom:3px solid #6d8d79}.legend span:nth-child(2){border-bottom:2px dashed #6d8d79}.columns{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.15fr);gap:28px;align-items:start}.column-head{font-size:13px;letter-spacing:.08em;color:var(--muted);margin:0 0 10px}.card{padding:20px 24px;margin-bottom:12px;background:#fffefa;border:1px solid var(--border);border-radius:12px}.id{font-family:Consolas,monospace;color:#6e7d71;font-size:12px;display:flex;gap:12px;align-items:center}.body{font-size:17px;line-height:2;margin:8px 0 4px;white-space:pre-wrap;overflow-wrap:anywhere}.bead .body{font-size:16px}.mark{background:var(--tint);border-bottom:3px solid var(--color);padding:1px 0;border-radius:2px;cursor:pointer;transition:opacity .15s,background .15s}.mark.weak{border-bottom-style:dashed}.mark:focus-visible{outline:2px solid var(--color);outline-offset:3px}.has-focus .mark:not(.selected){opacity:.43;background:transparent}.mark.selected{background:var(--active);box-shadow:0 0 0 2px var(--tint)}.link-keys{display:flex;gap:5px;flex-wrap:wrap;margin-top:10px}.key{font-size:11px;line-height:1.5;border:1px solid var(--color);color:var(--color);background:var(--tint);border-radius:5px;padding:1px 6px}.key[aria-pressed=true]{background:var(--color);color:#fff}.explanation{margin:24px 0 0;padding:20px 24px;background:#e9eee5;border-radius:12px;border:1px solid #d9e0d2;min-height:100px}.explanation h3{font-size:14px;margin:0 0 8px;font-weight:500}.explanation p{margin:5px 0;font-size:14px}.quote{background:#fffefa;padding:8px 12px;border-radius:6px;font-size:14px!important}.strength{font-size:12px;color:var(--muted)}details{font-size:13px;color:var(--muted);margin:22px 0}summary{cursor:pointer}details ul{padding-left:20px}footer{padding-top:0;font-size:12px;color:var(--muted)}.error{background:#fff0e9;padding:24px;border:1px solid #be7258}.sticky{position:sticky;top:16px}@media(max-width:820px){header,main,footer{padding:22px}.columns{grid-template-columns:1fr}.sticky{position:static}.toolbar .count{margin-left:0}h1{font-size:28px}.stage-title{display:block}.card{padding:16px 18px}.body{font-size:16px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body><header><div class="eyebrow">听见的感受 · 读到的经历</div><h1>看见一条线，怎样串起珠子</h1><p>同色标出的是两边情境相近的具体片段。点选任一处，看看它连到哪里；其余文字原样保留，不把一小处的联系扩成整颗珠子都已说清。</p><div class="toolbar"><label>作品 <select id="work" aria-label="选择作品"></select></label><button class="outline" id="clear">显示全部联系</button><button class="outline" id="download">下载对应表</button><span class="count" id="scope"></span></div><nav class="tabs" id="tabs" aria-label="选择段落"></nav></header><main><div class="stage-title"><h2 id="section"></h2><p id="meta"></p></div><div class="legend"><span>实线：情境相近</span><span>虚线：联系偏弱</span><span>未着色：保留原文，不强行对应</span><span>同色编号帮助辨认联系</span></div><div class="columns" id="columns"><div class="sticky"><h3 class="column-head">线 · 他经历的事</h3><div id="lines"></div><aside class="explanation" id="explanation" aria-live="polite"></aside></div><div><h3 class="column-head">珠子 · 听到与感到的</h3><div id="beads"></div></div></div><details><summary>查看未连部分与标注边界</summary><div id="unlinked"></div></details></main><footer id="footer"></footer><script id="mapping" type="application/json">__DATA__</script><script>
'use strict';
const DATA=JSON.parse(document.getElementById('mapping').textContent);
const $=s=>document.querySelector(s), palette=['#377b68','#9a642d','#616eab','#a35873','#427f98','#7f7936','#885da0','#a55740'];
let current, active=new Set(), groups=[];
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function tint(c,a){return c+Math.round(a*255).toString(16).padStart(2,'0')}
function check(s){let ids=new Set();for(const l of s.links){if(ids.has(l.id))throw Error('重复联系');ids.add(l.id);for(const [items,id,span] of [[s.lines,l.line_id,l.line_span],[s.beads,l.bead_id,l.bead_span]]){const t=items.find(x=>x.id===id);if(!t||Array.from(t.text).slice(span.start,span.end).join('')!==span.quote)throw Error('片段与原文不符')}}}
function colors(s){const sorted=[...s.links].sort((a,b)=>a.line_id.localeCompare(b.line_id)||a.line_span.start-b.line_span.start);groups=[];for(const l of sorted){let g=groups[groups.length-1];if(!g||g.line!==l.line_id||l.line_span.start>=g.end){g={line:l.line_id,start:l.line_span.start,end:l.line_span.end,color:palette[groups.length%palette.length],key:groups.length+1,links:[]};groups.push(g)}g.end=Math.max(g.end,l.line_span.end);g.links.push(l.id);l.group=g}}
function style(e,g){e.style.setProperty('--color',g.color);e.style.setProperty('--tint',tint(g.color,.13));e.style.setProperty('--active',tint(g.color,.30))}
function choose(ids){const same=ids.length===active.size&&ids.every(x=>active.has(x));active=new Set(same?[]:ids);focusUpdate()}
function fragment(item,kind){const p=el('p','body'),chars=Array.from(item.text),relevant=current.links.filter(l=>l[kind+'_id']===item.id);const bounds=[...new Set([0,chars.length,...relevant.flatMap(l=>[l[kind+'_span'].start,l[kind+'_span'].end])])].sort((a,b)=>a-b);for(let i=0;i<bounds.length-1;i++){const a=bounds[i],b=bounds[i+1],ls=relevant.filter(l=>l[kind+'_span'].start<=a&&l[kind+'_span'].end>=b),text=chars.slice(a,b).join('');if(!ls.length){p.append(document.createTextNode(text));continue}const e=el('span','mark'+(ls.every(l=>l.strength==='偏弱')?' weak':''),text);style(e,ls[0].group);const gs=[...new Set(ls.map(l=>l.group))];if(gs.length>1)e.style.background='linear-gradient(100deg,'+gs.map(g=>tint(g.color,.16)).join(',')+')';e.tabIndex=0;e.setAttribute('role','button');e.dataset.edges=JSON.stringify(ls.map(l=>l.id));e.setAttribute('aria-label',text+'，对应 '+[...new Set(ls.map(l=>l.group.key))].join('、'));e.title=ls.map(l=>`${l.line_id} ↔ ${l.bead_id}：${l.why}`).join('\n');e.onclick=()=>choose(ls.map(l=>l.id));e.onkeydown=ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();e.click()}};p.append(e)}if(p.textContent!==item.text)throw Error('原文发生改变');return p}
function card(item,kind){const e=el('article','card '+(kind==='bead'?'bead':''));e.append(el('div','id',item.id),fragment(item,kind));const ls=current.links.filter(l=>l[kind+'_id']===item.id),keys=el('div','link-keys');for(const g of [...new Set(ls.map(l=>l.group))]){const b=el('button','key','对应 '+g.key);style(b,g);const ids=ls.filter(l=>l.group===g).map(l=>l.id);b.dataset.edges=JSON.stringify(ids);b.onclick=()=>choose(ids);keys.append(b)}e.append(keys);return e}
function focusUpdate(){document.body.classList.toggle('has-focus',active.size>0);document.querySelectorAll('[data-edges]').forEach(e=>{const yes=JSON.parse(e.dataset.edges).some(id=>active.has(id));e.classList.toggle('selected',yes);e.setAttribute('aria-pressed',String(yes))});const box=$('#explanation');box.replaceChildren();if(!active.size){box.append(el('h3',null,'点选文字或对应编号'),el('p',null,'左边一句可以连到右边几颗珠子；右边一颗珠子，也可以由线里的几处分别串起。颜色只落在实际联系到的片段上。'));return}box.append(el('h3',null,'当前片段的联系'));for(const l of current.links.filter(l=>active.has(l.id))){box.append(el('p','strength',`对应 ${l.group.key} · ${l.line_id} ↔ ${l.bead_id} · ${l.strength}`),el('p','quote','线：'+l.line_quote),el('p','quote','珠子：'+l.bead_quote),el('p',null,l.why))}}
function show(s){current=s;active.clear();check(s);colors(s);$('#section').textContent=s.sec+' · '+s.bars;$('#meta').textContent='正文 '+s.tag+' · '+s.links.length+' 处片段联系';$('#lines').replaceChildren(...s.lines.map(i=>card(i,'line')));$('#beads').replaceChildren(...s.beads.map(i=>card(i,'bead')));$('#unlinked').replaceChildren();const ul=el('ul');for(const u of s.unlinked)ul.append(el('li',null,`${u.bead_id}「${u.quote}」：${u.reason}`));$('#unlinked').append(ul,el('p',null,s.note||'无补充边界说明。'));$('#tabs').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sec===s.sec)));focusUpdate()}
function workChanged(){const sections=DATA.sections.filter(s=>s.work===$('#work').value);$('#tabs').replaceChildren(...sections.map(s=>{const b=el('button','tab',s.sec);b.dataset.sec=s.sec;b.onclick=()=>show(s);return b}));show(sections[0])}
for(const w of [...new Set(DATA.sections.map(s=>s.work))]){$('#work').append(new Option(w==='op60'?'Op.60':'Op.61',w))}
$('#scope').textContent='样稿 · 两首作品 / '+DATA.sections.length+' 个段落';$('#footer').textContent='基于 '+DATA.tag+' 已写定正文的片段标注样稿。对应表示情境联系，不把珠子的声音或意象写成真实情节；此页不是全曲覆盖验收结论。';$('#work').onchange=workChanged;$('#clear').onclick=()=>{active.clear();focusUpdate()};$('#download').onclick=()=>{const blob=new Blob([JSON.stringify(DATA,(key,value)=>key==='group'?undefined:value,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download='珠线片段对应_'+DATA.tag+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
try{workChanged()}catch(e){$('#columns').replaceChildren(el('div','error','标注未通过原文核对：'+e.message));throw e}
</script></body></html>'''


def build(tag, full=False):
    root = S.OUT / tag
    manifest = json.loads((root / ('full_manifest.json' if full else 'pilot_manifest.json')).read_text(encoding='utf-8'))
    sections = [S.validated(t, tag) for t in manifest['tasks']]
    for section in sections:
        visual_groups(section)
    data = {'schema': 'music-span-links-v1', 'tag': tag, 'scope': manifest['scope'],
            'offset_unit': 'Unicode code points, zero-based start inclusive / end exclusive',
            'color_policy': 'One group per connected overlap of line spans within a section; linked bead fragments use the same color; weak edges use dashed underline; group IDs supplement color',
            'source_text_policy': 'Immutable full text; annotations are separate; no whole-bead coverage inferred',
            'sections': sections}
    raw = B.json_text(data)
    B.write_frozen(root / ('full_mapping.json' if full else 'pilot_mapping.json'), raw)
    safe = raw.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    html_path = root / ('珠线片段对应_全曲.html' if full else '珠线片段对应_样稿.html')
    template = TEMPLATE
    if full:
        template = template.replace('片段对应样稿', '片段对应').replace("'样稿 · 两首作品 / '", "'全曲 · 两首作品 / '")
        template = template.replace('已写定正文的片段标注样稿', '已写定正文的片段标注').replace('此页不是全曲覆盖验收结论', '片段联系不等于原覆盖验收结论')
    html_path.write_text(template.replace('__DATA__', safe), encoding='utf-8')
    receipt = {'sections': len(sections), 'links': sum(len(s['links']) for s in sections),
               'visual_groups': sum(len(s['visual_groups']) for s in sections),
               'line_items': sum(len(s['lines']) for s in sections), 'beads': sum(len(s['beads']) for s in sections),
               'mapping_sha256': B.digest(raw), 'html_sha256': B.digest(html_path.read_text(encoding='utf-8')),
               'all_quotes_exact': True, 'source_snapshots_unchanged': True, 'model_reviews_bound': True}
    (root / ('full_build_receipt.json' if full else 'build_receipt.json')).write_text(B.json_text(receipt), encoding='utf-8')
    print(B.json_text(receipt))
    return html_path


if __name__ == '__main__':
    import sys
    build(sys.argv[1], '--all' in sys.argv[2:])
