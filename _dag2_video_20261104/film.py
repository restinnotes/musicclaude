"""1920x1080 text-first Op52 layout. Source text is laid out, never shortened."""
import argparse, bisect, itertools, json, math, re, subprocess, sys
from pathlib import Path
import numpy as np
import skia
from dag2 import ROOT, OLD, read, write, bounds, sha

W,H,FPS=1920,1080,30
PALETTE=[(236,191,105),(124,205,218),(225,152,174),(173,173,233),(153,205,164),(225,171,127)]
BG=(15,20,28); FG=(235,236,233); MUTED=(170,181,193)
def col(rgb,a=255): return skia.ColorSetARGB(int(a),*map(int,rgb))
def paint(rgb,a=255): return skia.Paint(Color=col(rgb,a),AntiAlias=True)
def rect(c,x,y,w,h,rgb,a=255): c.drawRect(skia.Rect.MakeXYWH(x,y,w,h),paint(rgb,a))
def line(c,x,y,x1,y1,rgb,width=1,a=255):
 p=paint(rgb,a);p.setStrokeWidth(width);c.drawLine(x,y,x1,y1,p)

class Film:
 def __init__(self,work,variant='v1'):
  self.work,self.variant=work,variant
  self.src=read(ROOT/f'input/{work}.json');self.music=read(ROOT/f'input/{work}_music.json')
  pp=ROOT/f'plans/{work}_v1.json';self.plan=read(pp) if pp.exists() else None
  self.faces={k:skia.Typeface.MakeFromFile(str(OLD/f'work/fonts/{v}.ttf')) for k,v in [('body','Sans400'),('line','Serif500')]}
  self.dur=self.music['dur'];self.bar_times=dict(self.music['bars']);self.bar_numbers=sorted(self.bar_times)
  self.segs=self.src['segments'];self.starts=[self.bar_times[bounds(s['bars'])[0]] for s in self.segs]
  self.ends=self.starts[1:]+[self.dur]
  self.notes=self.music['notes'];self.ns=np.array([n['s'] for n in self.notes])
  self.pages=[];self.qa=[];self.rail_positions=[]
  self.outline={x['sec']:x for x in self.plan['outline']} if self.plan else {s['sec']:{'label':s['items'][0]['text'][:18]} for s in self.segs}
  self.phases=self.plan['phases'] if self.plan else [{'title':self.segs[a]['items'][0]['text'][:18],'sections':[s['sec'] for s in self.segs[a:b]],'line_id':self.segs[a]['items'][0]['id']} for a,b in zip([0,3,6,9,12],[3,6,9,12,len(self.segs)]) if a<len(self.segs)]
  self.links=self.plan['links'] if self.plan else []
  self.links=[l for l in self.links if l['strength']=='相近' and l.get('group',99)<len(PALETTE)]
  bp=ROOT/f'plans/{work}_physical.json';self.bindings=read(bp)['bindings'] if bp.exists() else []
  self.line_lookup={x['id']:(si,x) for si,s in enumerate(self.segs) for x in s['items']}
  for si,s in enumerate(self.segs): self.pages.append(self.page(si))

 def font(self,size,kind='body'): return skia.Font(self.faces[kind],size)
 def text(self,c,text,x,y,size,rgb=FG,kind='body',a=255):
  c.drawString(text,x,y,self.font(size,kind),paint(rgb,a))
 def wrapped(self,text,size,width,kind='body'):
  font=self.font(size,kind);adv=font.getWidths(font.textToGlyphs(text));rows=[];start=0;cw=0
  close='，。！？；：、）》」』】〕…,.!?;:';opening='（《「『【〔('
  for i,a in enumerate(adv):
   if cw+a>width and i>start:
    cut=i-1 if i>start+1 and (text[i] in close or text[i-1] in opening) else i
    rows.append((start,cut)); start=cut; cw=sum(adv[cut:i])
   cw+=a
  if start<len(text): rows.append((start,len(text)))
  return rows
 def draw_rich(self,c,text,x,y,size,width,kind='body',id=None,links=True,rgb=MUTED):
  rows=self.wrapped(text,size,width,kind);font=self.font(size,kind);ranges=[]
  if links and self.variant!='v0':
   for l in self.links:
    for k in ['line','bead']:
     if l[k+'_id']==id:ranges.append((*l[k+'_span'],PALETTE[l['group']]))
  for a,b in rows:
   xx=x
   for j in range(a,b):
    cc=next((cc for lo,hi,cc in ranges if lo<=j<hi),rgb)
    ch=text[j];self.text(c,ch,xx,y,size,cc,kind);xx+=font.measureText(ch)
   y+=size*1.3
  return y

 def blocks(self,si,body):
  s=self.segs[si];blocks=[]
  for i,it in enumerate(s['items']):
   blocks.append({'id':it['id'],'kind':'line','text':it['text'],'size':body+5,'font':'line','gap':10,'indent':0})
   for b in s['beads']:
    if b['after']==i:
     blocks.append({'id':b['id'],'kind':'bead','text':b['text'],'size':body,'font':'body','gap':10,'indent':12,'where':b['where']})
  return blocks

 def layout(self,si):
  # A column boundary never separates a story line from its paired beads.
  height=582
  for size in range(30,20,-1):
   for count in [2,3]:
    width=(1380-(count-1)*28)/count
    blocks=self.blocks(si,size)
    for b in blocks:
     b['height']=len(self.wrapped(b['text'],b['size'],width-b['indent'],b['font']))*b['size']*1.3+b['gap']+(21 if b['kind']=='bead' else 0)
    boundaries=list(range(1,len(blocks)))
    choices=[]
    for cut in itertools.combinations(boundaries,count-1):
     inds=[0,*cut,len(blocks)];columns=[]
     for a,b in zip(inds,inds[1:]):
      bs=blocks[a:b]
      if bs[0]['kind']=='bead':
       head=next(x for x in reversed(blocks[:a]) if x['kind']=='line')
       bs=[{**head,'continued':True},*bs]
      columns.append(bs)
     heights=[sum(b['height'] for b in bs) for bs in columns]
     choices.append((max(heights),columns,heights))
    if choices:
     h,columns,heights=min(choices,key=lambda x:x[0])
     if h<=height:return blocks,columns,size,heights,width
  raise ValueError(f'{self.work} {self.segs[si]["sec"]}: cannot fit all text at 21px')

 def page(self,si):
  surface=skia.Surface(W,H);c=surface.getCanvas();c.clear(col(BG))
  s=self.segs[si];blocks,columns,size,heights,width=self.layout(si)
  rect(c,48,103,1398,602,(20,27,37))
  for ci in range(1,len(columns)):line(c,65+ci*(width+28)-14,121,65+ci*(width+28)-14,687,(58,68,80),a=100)
  self.text(c,self.src['title'],54,43,27,FG,'line')
  self.text(c,self.src['performer'],54,75,19,(131,146,161))
  label=self.outline[s['sec']]['label']
  self.text(c,label,390,48,28,FG,'line')
  self.text(c,f"第 {s['bars']} 小节",390,79,19,(147,163,178))
  # Small stable legend communicates the only use of semantic colour.
  if self.variant!='v0':self.text(c,'同色文字彼此呼应',1192,78,18,(139,154,167))
  positions=[];visible={};
  for column,bs in enumerate(columns):
   x=65+column*(width+28);y=133
   for b in bs:
    y0=y-b['size']
    if b['kind']=='line':
     rect(c,x-8,y-b['size']+1,3,b['size']+4,(107,125,143))
     if b.get('continued'):self.text(c,'续',x-25,y-2,14,(121,138,154))
    else:
     where=b['where'].split('；')[0]
     if re.search(r'\d',where):
      lo,hi=bounds(where);where=(str(lo) if lo==hi else f'{lo}–{hi}')+' 小节'
     else:where='本段'
     self.text(c,where,x+b['indent'],y-2,16,(121,138,154));y+=21
    baseline=y
    y=self.draw_rich(c,b['text'],x+b['indent'],y,b['size'],width-b['indent'],b['font'],b['id'],rgb=FG if b['kind']=='line' else MUTED)
    visible[b['id']]=b['text'];positions.append({'id':b['id'],'column':column,'x':x,'top':y0,'bottom':y-7,'font':b['size'],'baseline':baseline})
    y+=b['gap']
  expected={b['id']:b['text'] for b in blocks}
  assert visible==expected
  assert all(sum(p['id']==b['id'] for p in positions)==1 for b in blocks if b['kind']=='bead')
  assert max(p['bottom'] for p in positions)<720
  self.qa.append({'sec':s['sec'],'body_font':size,'column_heights':heights,'content_exact':True,'all_ids':list(visible),'positions':positions,'repeated_line_for_continuation':[b['id'] for bs in columns for b in bs if b.get('continued')],'colour_groups':len(set(x['group'] for x in self.links if x['line_id'].startswith(s['sec']+'-')))})
  line(c,1480,32,1480,704,(56,69,84))
  self.text(c,'这一路',1520,47,23,(211,218,220),'line')
  self.draw_rail(c,si)
  return surface.makeImageSnapshot()

 def draw_rail(self,c,si):
  s=self.segs[si];phase_index=next(i for i,p in enumerate(self.phases) if s['sec'] in p['sections']);y=96;positions={}
  for pi,p in enumerate(self.phases):
   current=pi==phase_index;future=pi>phase_index
   # Future stages keep their place without revealing a later story.
   if future:
    self.text(c,f'{pi+1:02d}',1520,y,19,(78,94,110));line(c,1575,y-7,1825,y-7,(47,61,75));y+=37;continue
   rgb=FG if current else (133,151,166)
   positions[pi]=y-22
   line(c,1520,y-13,1526,y-7 if current else y-17,rgb,1.5)
   line(c,1526,y-7 if current else y-17,1532 if current else 1520,y-13 if current else y-21,rgb,1.5)
   y=self.draw_rich(c,p['title'],1551,y,21,305,'line',links=False,rgb=rgb)+3
   if current:
    for sec in p['sections']:
     idx=next(i for i,x in enumerate(self.segs) if x['sec']==sec)
     if idx>si:continue
     active=idx==si;rgb=FG if active else(122,141,158)
     if active:rect(c,1542,y-23,316,58,(34,47,62))
     yy=self.draw_rich(c,self.outline[sec]['label'],1555,y,20,290,'body',links=False,rgb=rgb)
     y=yy+6
   y+=9
  if y>702:raise ValueError(('rail overflow',self.work,s['sec'],y))
  self.rail_positions.append(positions)

 def frame(self,t):
  t=max(0,min(t,self.dur-0.001));si=max(0,bisect.bisect_right(self.starts,t)-1)
  surface=skia.Surface(W,H);c=surface.getCanvas();c.clear(col(BG));c.drawImage(self.pages[si],0,0)
  s=self.segs[si];local=(t-self.starts[si])/(self.ends[si]-self.starts[si])
  # Recall is driven by frozen citations, never inferred by the renderer.
  recalled=sorted({self.line_lookup[k][0] for it in s['items'] for k in it.get('cite',[]) if k in self.line_lookup and self.line_lookup[k][0]<si})
  if recalled:
   cited_phases={i for i,p in enumerate(self.phases) if any(self.segs[r]['sec'] in p['sections'] for r in recalled)}
   for pi in cited_phases:
    if pi in self.rail_positions[si]:rect(c,1500,self.rail_positions[si][pi],3,33,(172,204,224),225 if t-self.starts[si]<6 else 100)
   self.text(c,'这段回望',1590,835,18,(144,166,184))
   for j,r in enumerate(recalled[-2:]):
    text=self.outline[self.segs[r]['sec']]['label']
    self.text(c,'第 '+self.segs[r]['bars']+' 小节',1590,870+j*82,15,(119,147,169))
    self.draw_rich(c,text,1590,895+j*82,19,275,links=False,rgb=(172,204,224))
  # Current bar, progress; page itself remains steady throughout the section.
  bar=max(k for k in self.bar_numbers if self.bar_times[k]<=t)
  self.text(c,f'第 {bar} 小节',55,744,20,(174,189,202))
  self.text(c,f'{int(t)//60:02d}:{int(t)%60:02d}  /  {int(self.dur)//60:02d}:{int(self.dur)%60:02d}',1695,744,18,(144,162,179))
  line(c,54,765,1866,765,(46,60,74),2);line(c,54,765,54+1812*t/self.dur,765,(173,194,206),2)
  rect(c,0,780,1560,300,(12,18,25))
  for p in [36,48,60,72,84,96]:
   yy=1040-(p-28)/76*235;line(c,62,yy,1856,yy,(37,49,63),1,90)
  nowx=1540;speed=105
  line(c,nowx,797,nowx,1051,(105,126,146),1,90)
  self.text(c,'此刻',nowx-17,1070,16,(129,153,174))
  lo=np.searchsorted(self.ns,t-15);hi=np.searchsorted(self.ns,t+0.001)
  for n in self.notes[lo:hi]:
   x=nowx-(t-n['s'])*speed;y=1040-(n['p']-28)/76*235
   if x<55 or not 790<y<1048:continue
   active=n['s']<=t<max(n['e'],n['s']+0.12)
   rgb=(166,194,211) if n['h']==1 else(154,166,183)
   binding=next((b for b in self.bindings if b['sec']==s['sec'] and b['t0']<=n['s']<b['t1'] and b['hand']==n['h']),None)
   if binding and self.variant!='v0':rgb=PALETTE[binding['group']]
   # Semantic colours on text are persistent. Notes remain neutral unless an
   # exact, audited physical binding exists; narrative similarity is insufficient.
   radius=(3+3*n.get('en',0.5))*(1.2 if active else 1)
   length=min(180,max(3,(min(t,n['e'])-n['s'])*speed))
   line(c,x,y,min(nowx,x+length),y,rgb,2,170 if active else 80)
   c.drawCircle(x,y,radius,paint(rgb,245 if active else 100))
  return surface.makeImageSnapshot()

 def save_qa(self):
  out={'work':self.work,'variant':self.variant,'source_sha256':sha(ROOT/f'input/{self.work}.json'),'pages':self.qa,'text_fidelity':True,'minimum_body_font':min(x['body_font'] for x in self.qa),'all_segments':len(self.qa),'duration':self.dur,'physical_note_binding':'neutral until audited; no semantic inference from narrative links'}
  write(ROOT/f'qa/{self.work}_{self.variant}_layout.json',out)

def stills(work,variant):
 f=Film(work,variant);d=ROOT/f'previews/{variant}/{work}';d.mkdir(parents=True,exist_ok=True)
 for i,(a,b) in enumerate(zip(f.starts,f.ends)):
  img=f.frame(a+(b-a)*0.55);img.save(str(d/f'{i+1:02d}.png'),skia.EncodedImageFormat.kPNG,100)
 f.save_qa();print(work,variant,'all pages',len(f.pages),'min font',min(x['body_font'] for x in f.qa),flush=True)

def render(work,variant,start,end,path):
 f=Film(work,variant);end=min(end or f.dur,f.dur);duration=end-start
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 audio_codec=['-c:a','copy'] if start==0 and abs(end-f.dur)<0.01 else ['-c:a','aac','-b:a','256k']
 audio_input=(['-ss',str(start)] if start else [])+['-i',f.src['audio']]
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0',*audio_input,'-t',str(duration),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p',*audio_codec,'-movflags','+faststart',str(path)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 n=round(duration*FPS)
 try:
  for i in range(n):
   frame=f.frame(start+i/FPS);proc.stdin.write(frame.tobytes())
   if i%900==0:print(work,variant,round(i/FPS,1),'/',round(duration,1),flush=True)
 finally:proc.stdin.close()
 if proc.wait()!=0:raise RuntimeError('ffmpeg failed')
 f.save_qa();write(path.with_suffix('.json'),{'work':work,'variant':variant,'start':start,'end':end,'frames':n,'fps':FPS,'source_sha256':sha(ROOT/f'input/{work}.json'),'video_sha256':sha(path)})

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('command',choices=['stills','render']);p.add_argument('--work',required=True);p.add_argument('--variant',default='v1');p.add_argument('--start',type=float,default=0);p.add_argument('--end',type=float);p.add_argument('--out');a=p.parse_args()
 if a.command=='stills':stills(a.work,a.variant)
 else:render(a.work,a.variant,a.start,a.end,a.out or str(ROOT/f'out/{a.work}_{a.variant}.mp4'))
