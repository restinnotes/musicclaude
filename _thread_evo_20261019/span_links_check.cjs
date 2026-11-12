// Offline DOM contract checks. This does not launch or control a browser.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tag,text=''){this.tag=tag;this.children=[];this._text=text;this.dataset={};this.attributes={};this.value='';this.props={};this.style={setProperty:(k,v)=>this.props[k]=v};this.classes=new Set();this.classList={toggle:(k,v)=>{if(v===undefined)v=!this.classes.has(k);v?this.classes.add(k):this.classes.delete(k);return v},contains:k=>this.classes.has(k)}}
 set className(v){this.classes=new Set(v.split(' ').filter(Boolean))}get className(){return [...this.classes].join(' ')}
 set textContent(v){this._text=String(v);this.children=[]}get textContent(){return this._text+this.children.map(c=>c.textContent).join('')}
 append(...nodes){for(let n of nodes){if(typeof n!=='object')n=new Element('#text',String(n));this.children.push(n);if(this.tag==='select'&&!this.value)this.value=n.value}}
 replaceChildren(...nodes){this._text='';this.children=[];this.append(...nodes)}
 setAttribute(k,v){this.attributes[k]=v}getAttribute(k){return this.attributes[k]}
 querySelectorAll(q){const all=this.children.flatMap(c=>[c,...c.querySelectorAll(q)]);return all.filter(c=>q==='button'?c.tag==='button':q==='[data-edges]'?c.dataset.edges!==undefined:q==='.mark'?c.classes.has('mark'):false)}
 click(){this.onclick?.()}remove(){}
}
const fixture=process.argv[2],script=process.argv[3];
const data=JSON.parse(fs.readFileSync(fixture,'utf8'));
const ids={};for(const id of ['work','clear','download','scope','tabs','section','meta','columns','lines','beads','explanation','unlinked','footer','mapping'])ids[id]=new Element(id==='work'?'select':'div');
ids.mapping.textContent=JSON.stringify(data);
const body=new Element('body');body.append(...Object.values(ids));
const document={body,getElementById:id=>ids[id],querySelector:q=>ids[q.slice(1)],querySelectorAll:q=>body.querySelectorAll(q),createElement:tag=>new Element(tag),createTextNode:text=>new Element('#text',text)};
const context=vm.createContext({document,Option:function(text,value){const e=new Element('option',text);e.value=value;return e},Blob,URL,setTimeout,console});
vm.runInContext(fs.readFileSync(script,'utf8'),context);
let fragments=0;
for(let i=0;i<data.sections.length;i++){
 vm.runInContext(`show(DATA.sections[${i}])`,context);
 vm.runInContext(`{
 const s=DATA.sections[${i}];
 for(const link of s.links){
  const saved=s.visual_groups.find(g=>g.id===link.visual_group);
  if(!saved||!saved.link_ids.includes(link.id)||saved.line_id!==link.line_id||saved.start!==link.group.start||saved.end!==link.group.end||saved.color_hex!==link.group.color||link.color_hex!==link.group.color)throw Error('Exported color group differs from display');
 }
 const exported=JSON.parse(JSON.stringify(DATA,(key,value)=>key==='group'?undefined:value));
 for(const link of exported.sections[${i}].links)if(!link.visual_group||!link.color_hex||link.group)throw Error('Download lost stable color metadata');
 }`,context);
 const s=data.sections[i];
 for(const [id,items] of [['lines',s.lines],['beads',s.beads]]){
  assert.equal(ids[id].children.length,items.length,'all original items retained');
  for(let k=0;k<items.length;k++)assert.equal(ids[id].children[k].children[1].textContent,items[k].text,'original prose byte-for-byte by content');
 }
 const marks=body.querySelectorAll('.mark');fragments+=marks.length;
 if(marks.length){
  let prevented=false;marks[0].onkeydown({key:'Enter',preventDefault(){prevented=true}});
  assert(prevented);assert(body.classList.contains('has-focus'));
  const selected=body.querySelectorAll('.mark').filter(e=>e.classList.contains('selected'));
  assert(selected.length>=2,'a selected correspondence lights both ends');
  assert(ids.explanation.textContent.includes('当前片段的联系'));
  ids.clear.click();assert(!body.classList.contains('has-focus'));
  const beadMark=ids.beads.querySelectorAll('.mark')[0];beadMark.click();
  assert(ids.lines.querySelectorAll('.mark').some(e=>e.classList.contains('selected')),'reverse bead-to-line selection');
 }
}
vm.runInContext(`{
const l={id:'unicode',line_id:'u',bead_id:'v',line_span:{start:1,end:2},bead_span:{start:0,end:1},strength:'相近',why:'test'};
current={links:[l]};colors(current);const p=fragment({id:'u',text:'前🎵后'},'line');
if(p.textContent!=='前🎵后'||p.children[1].textContent!=='🎵')throw Error('Unicode codepoint offset split');
const ls=[{line_id:'u',line_span:{start:0,end:2},id:'a'},{line_id:'u',line_span:{start:1,end:5},id:'b'},{line_id:'u',line_span:{start:4,end:7},id:'c'},{line_id:'u',line_span:{start:7,end:8},id:'d'}];
colors({links:ls});if(groups.length!==2||ls[0].group!==ls[2].group||ls[2].group===ls[3].group)throw Error('overlap color grouping');
}`,context);
console.log(JSON.stringify({mode:'offline DOM, not browser visual verification',sections:data.sections.length,fragments,source_text_exact:true,bidirectional_selection:true,keyboard_selection:true,unicode_offsets:true,overlap_grouping:true,export_matches_display:true},null,2));
