
const D=[];
const c=document.getElementById('c'),a=document.getElementById('a'),f=document.getElementById('f');
function el(t,k,x){const e=document.createElement(t);if(k)e.className=k;if(x!=null)e.textContent=x;return e}
const secs=[];
D.forEach(s=>{
  const sec=el('section');secs.push(sec);
  sec.appendChild(el('h2',null,'第 '+s.bars+' 小节　·　'+s.rel));
  s.rows.forEach(r=>{
    const p=el('p',r.k);p.tabIndex=0;
    if(r.k==='bead'){
      p.appendChild(el('span','tag'+(r.alt?' alt':''),(r.alt?'另一种听法 · ':'')+r.bars));
      p.appendChild(document.createTextNode(r.text));
    }else{p.textContent=r.text}
    const go=()=>{a.currentTime=r.t;a.play()};
    p.addEventListener('click',go);
    p.addEventListener('keydown',e=>{if(e.key==='Enter')go()});
    sec.appendChild(p);
  });
  c.appendChild(sec);
});
let cur=-1;
a.addEventListener('timeupdate',()=>{
  const t=a.currentTime;let n=-1;
  D.forEach((s,i)=>{if(t>=s.t0)n=i});
  if(n!==cur){
    if(cur>=0)secs[cur].classList.remove('on');
    cur=n;
    if(cur>=0){secs[cur].classList.add('on');if(f.checked&&!a.paused)secs[cur].scrollIntoView({behavior:'smooth',block:'start'})}
  }
});
