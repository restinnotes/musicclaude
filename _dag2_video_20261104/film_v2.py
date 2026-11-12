"""Graph-preserving presentation with Op52 BALLS motion and local text windows.

V1 is deliberately retained. This module writes only v2 artifacts.
"""
import argparse, bisect, itertools, json, math, subprocess, sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import skia
from dag2 import ROOT, OLD, read, write, sha
from film import Film as TextTools, col, paint, rect, line, PALETTE, FG, MUTED
from v2_data import display

sys.path.insert(0,'D:/music-experience-pipeline/src')
from mamviz.midi import Note, Song
from mamviz.geometry import Mapping
from mamviz.visual_lines import heuristic_assignments_for_song
from mamviz.renderers import draw_balls

W,H,FPS=1920,1080,30
TOP=710
BG=(14,18,24)
NODE=(18,23,30)
SYMBOL={'可同时成立':'∥','重叠但新增':'＋','段内先后':'→','不可同时成立':'≠','替代':'≠'}

def draw_center_guide(c,tint):
    # This is a transport marker, independent of whether a note is sounding.
    # It never invents a musical event in a gap between notes.
    line(c,960,TOP+14,960,H-17,tint,5,16)
    line(c,960,TOP+14,960,H-17,tint,1.2,105)
    for radius,alpha in [(12,12),(9,24),(6,65),(3.5,235)]:
        c.drawCircle(960,H-17,radius,paint(tint,alpha))

class BallCanvas:
    """Skia adapter for the exact Op52-era draw_balls formulas."""
    def __init__(self,c,tint):self.c,self.tint=c,tint
    def xy(self,x,y):return 960+x*960,TOP+(H-TOP)*(1-y)*.5
    def blend_line(self,x0,y0,x1,y1,color,alpha,width):
        x0,y0=self.xy(x0,y0);x1,y1=self.xy(x1,y1)
        line(self.c,x0,y0,x1,y1,color,width,max(0,min(255,105*alpha)))
    def blend_circle_poly(self,x,y,rx,ry,color,alpha,segs,fill=True,outline_width=2):
        x,y=self.xy(x,y);r=max(.05,rx*(H-TOP)*.5)
        p=paint(color,max(0,min(255,alpha*255)))
        if not fill:p.setStyle(skia.Paint.kStroke_Style);p.setStrokeWidth(max(1,outline_width*.7));p.setAlphaf(alpha*.45)
        self.c.drawCircle(x,y,r,p)

class Palette:
    def __init__(self):self.tint=(214,187,136);self.hand=None
    def rgb(self,n):return self.tint if self.hand is None or n.part==self.hand else (153,154,151)
    def color(self,n,state):
        r,g,b=self.rgb(n);return r<<16|g<<8|b

class Film(TextTools):
    def __init__(self,work,density=0):
        self.work,self.variant,self.density=work,'v2',density
        self.src=read(ROOT/f'input/{work}.json');self.music=read(ROOT/f'input/{work}_music.json')
        self.plan=read(ROOT/f'plans/{work}_v1.json');self.graph=read(ROOT/f'plans/{work}_v2_graph.json')
        rp=ROOT/f'plans/{work}_v2_rail.json';rail=read(rp) if rp.exists() else self.plan
        self.phases,self.outline=rail['phases'],{o['sec']:o for o in rail['outline']}
        self.faces={k:skia.Typeface.MakeFromFile(str(OLD/f'work/fonts/{v}.ttf')) for k,v in [('body','Sans400'),('line','Serif500')]}
        self.dur=self.music['dur'];self.segs=self.src['segments'];self.starts=[s['window'][0] for s in self.graph['segments']];self.ends=[s['window'][1] for s in self.graph['segments']]
        self.links=[l for l in self.plan['links'] if l['strength']=='相近' and l.get('group',99)<len(PALETTE)]
        self.line_lookup={x['id']:(si,x) for si,s in enumerate(self.segs) for x in s['items']}
        self.notes=self.music['notes'];self.ns=np.array([n['s'] for n in self.notes]);self.qa=[];self.pages=[]
        ns=[Note(n['s'],n['e'],max(.025,n['e']-n['s']),n['p'],80,n['h'],n['h'],n['h'],note_id=f'n{i}') for i,n in enumerate(self.notes)]
        self.song=Song(ns,[(0,0),(1,1)],self.dur,note_by_id={n.note_id:n for n in ns})
        self.assignments=heuristic_assignments_for_song(self.song)
        self.cfg={'line_source':'heuristic','scope':{'seconds_half_span':3.0},'lines':{'width':1.6,'alpha':1.,'rest_gap':.8},'notes':{'fill_alpha':.35,'outline_width':2.},'readability':{'enabled':True,'radius':{'mode':'original_cap','max':.15}}}
        self.mapping=Mapping(self.song,self.cfg);self.palette=Palette();self.layouts=[]
        for si in range(len(self.segs)):
            self.layouts.append(self.layout_graph(si));self.pages.append(self.static_page(si))
        self.cached_key=None;self.cached_text=None

    def curve(self,c,x0,y0,x1,y1,rgb,a=100,width=1.2,dashed=False):
        p=paint(rgb,a);p.setStyle(skia.Paint.kStroke_Style);p.setStrokeWidth(width)
        if dashed:p.setPathEffect(skia.DashPathEffect.Make([4,5],0))
        path=skia.Path();path.moveTo(x0,y0)
        if abs(x1-x0)<40:path.cubicTo(x0-22,y0,x1-22,y1,x1,y1)
        else:path.cubicTo((x0+x1)/2,y0,(x0+x1)/2,y1,x1,y1)
        c.drawPath(path,p)

    def layout_graph(self,si):
        s=self.segs[si];gs=self.graph['segments'][si]
        # Story nodes have a dedicated column; bead nodes remain distinct graph cards.
        for size in range(28,21,-1):
            nodes=[]
            for b in gs['nodes']:
                events=sorted({t for ch in b['chunks'] for win in ch.get('windows',[ch['window']]) for t in win})
                candidates=[(a+z)/2 for a,z in zip(events,events[1:])]
                count=max(sum(len(self.wrapped(ch['display'],size,436)) for ch in b['chunks'] if self.chunk_alpha(ch,t)>0) for t in candidates)
                h=31+count*size*1.26+20
                nodes.append({'node':b,'height':h})
            best=None
            # Exhaustive 2-column partition preserves order within each column.
            for mask in range(1,2**len(nodes)-1):
                cols=[[x for j,x in enumerate(nodes) if bool(mask&(1<<j))==flag] for flag in [True,False]]
                heights=[sum(x['height']+18 for x in c)-18 for c in cols]
                key=(max(heights),abs(heights[0]-heights[1]))
                if best is None or key<best[0]:best=(key,cols,heights)
            if best and best[0][0]<=650:break
        else:raise ValueError((self.work,s['sec'],'cannot fit graph cards'))
        _,cols,heights=best;positions={};chunks=[]
        for ci,items in enumerate(cols):
            x=410+ci*510;y=32
            for item in items:
                b=item['node'];positions[b['id']]={'x':x,'y':y,'w':468,'h':item['height'],'column':ci,'node':b}
                for ch in b['chunks']:
                    chunks.append({**ch,'id':b['id'],'x':x+16,'y':y+53,'size':size,'width':436,'node':b})
                y+=item['height']+18
        for story_size in range(29,22,-1):
            story=[]
            for it in s['items']:
                text,_=display(it['text']);h=len(self.wrapped(text,story_size,300,'line'))*story_size*1.26+23
                story.append({'item':it,'display':text,'height':h,'size':story_size})
            if sum(x['height'] for x in story)+16*(len(story)-1)<=650:break
        else:raise ValueError((self.work,s['sec'],'story overflow'))
        y=36
        for st in story:st.update(x=50,y=y,w=322,h=st['height']);y+=st['height']+16
        assert max(p['y']+p['h'] for p in positions.values())<TOP-15
        self.qa.append({'sec':s['sec'],'body_font':size,'bead_nodes':list(positions),'bead_edges':gs['edges'],'story_nodes':[s['item']['id'] for s in story],
                        'all_original_text_scheduled':True,'locations_displayed':False,'column_heights':heights,'positions':[{k:v for k,v in p.items() if k!='node'} for p in positions.values()]})
        return {'positions':positions,'chunks':chunks,'story':story,'size':size}

    def draw_spans(self,c,text,indices,x,y,size,width,kind,id,alpha=255):
        font=self.font(size,kind);rgb=FG if kind=='line' else (192,197,202)
        ranges=[]
        for l in self.links:
            for side in ['line','bead']:
                if l[side+'_id']==id:ranges.append((*l[side+'_span'],PALETTE[l['group']]))
        rows=self.wrapped(text,size,width,kind)
        for a,b in rows:
            xx=x
            for j in range(a,b):
                cc=next((v for lo,hi,v in ranges if lo<=indices[j]<hi),rgb)
                self.text(c,text[j],xx,y,size,cc,kind,a=alpha);xx+=font.measureText(text[j])
            y+=size*1.26
        return y

    def static_page(self,si):
        sf=skia.Surface(W,H);c=sf.getCanvas();c.clear(col(BG));layout=self.layouts[si]
        # Distinct story nodes preserve same-section citation edges; no prose interleaving.
        lookup={st['item']['id']:st for st in layout['story']}
        for edge in self.segs[si].get('because',[]):
            if edge['from'] in lookup and edge['to'] in lookup:
                a,b=lookup[edge['from']],lookup[edge['to']]
                self.curve(c,39,a['y']+a['h']/2,39,b['y']+b['h']/2,(137,150,164),65,dashed=edge.get('rel')=='引用')
        for st in layout['story']:
            rect(c,st['x']-10,st['y'],3,st['h']-10,(123,138,153),160)
            text,indices=display(st['item']['text'])
            self.draw_spans(c,text,indices,st['x'],st['y']+st['size'],st['size'],300,'line',st['item']['id'])
        self.draw_rail(c,si)
        return sf.makeImageSnapshot()

    def draw_rail(self,c,si):
        sec=self.segs[si]['sec'];pi=next(i for i,p in enumerate(self.phases) if sec in p['sections'])
        recalled={self.line_lookup[q][0] for it in self.segs[si]['items'] for q in it.get('cite',[]) if q in self.line_lookup and self.line_lookup[q][0]<si}
        recalled_phases={i for i,p in enumerate(self.phases) if any(self.segs[r]['sec'] in p['sections'] for r in recalled)}
        x=1530;y=66
        # Op52: a slim spine, one compact row per completed phase, only the active phase expands.
        line(c,x,45,x,658,(75,86,100),1,85)
        current_ids=[]
        for i,p in enumerate(self.phases):
            if i>pi:continue
            current=i==pi;rgb=FG if current else (122,133,145)
            rect(c,x-4,y-12,8,8,PALETTE[0] if current else (84,104,117),240 if current else 150)
            if i in recalled_phases and not current:
                rect(c,x-7,y-15,14,14,(124,174,194),90);rect(c,x-3,y-11,6,6,(159,203,216),230)
            y=self.draw_rich(c,p['title'],x+20,y,24 if current else 21,340,'line',links=False,rgb=rgb)+14
            if current:
                ids=[q for q in p['sections'] if next(j for j,s in enumerate(self.segs) if s['sec']==q)<=si]
                ids=ids[-(1 if self.density==0 else 2):] if self.density<2 else ids
                for q in ids:
                    active=q==sec;current_ids.append(q)
                    if active:rect(c,x+16,y-23,3,28,PALETTE[0],230)
                    y=self.draw_rich(c,self.outline[q]['label'],x+33,y,22,310,'body',links=False,rgb=FG if active else (133,146,158))+18
            y+=10
        assert y<690,(self.work,sec,'rail overflow',y)
        # Citations light the existing collapsed phase instead of adding a second list.
        self.qa[si]['rail']={'density':self.density,'expanded_sections':current_ids,'rows_end':y,'recalled_sections':[self.segs[r]['sec'] for r in recalled]}

    @staticmethod
    def alpha(window,t):
        a,b=window
        if not a<=t<b:return 0
        return min(1.,(t-a)/.35,(b-t)/.35)

    def chunk_alpha(self,ch,t):return max(self.alpha(win,t) for win in ch.get('windows',[ch['window']]))

    def active_key(self,si,t):
        # Text images change only at fades or locator boundaries; music stays 30 fps.
        return si,tuple(round(self.chunk_alpha(ch,t)*20)/20 for ch in self.layouts[si]['chunks'])

    def graph_image(self,si,t,key):
        sf=skia.Surface(W,H);c=sf.getCanvas();c.drawImage(self.pages[si],0,0)
        layout=self.layouts[si];pos=layout['positions'];gs=self.graph['segments'][si]
        visibility={id:max(self.chunk_alpha(ch,t) for ch in layout['chunks'] if ch['id']==id) for id in pos}
        focus=self.focus(si,t)
        # Associations are a distinct edge layer behind the opaque bead cards.
        for id,p in pos.items():
            if visibility[id]<=0:continue
            st=layout['story'][p['node']['after']]
            self.curve(c,st['x']+st['w']-4,st['y']+st['h']/2,p['x'],p['y']+20,(117,137,153),int(100*visibility[id]))
        for ei,e in enumerate(gs['edges']):
            pa,pb=pos[e['a']],pos[e['b']];al=min(visibility[e['a']],visibility[e['b']])
            if al<=0:continue
            if pa['column']==pb['column']:
                x=pa['x']+pa['w']+8+(ei%3)*4
                self.curve(c,x,pa['y']+24,x,pb['y']+24,(148,157,169),int(130*al),dashed=e['type']!='段内先后')
            else:
                left,right=(pa,pb) if pa['column']==0 else (pb,pa)
                self.curve(c,left['x']+left['w'],left['y']+20,right['x'],right['y']+20,(148,157,169),int(130*al),dashed=e['type']!='段内先后')
        for id,p in pos.items():
            al=visibility[id]
            if al<=0:continue
            rect(c,p['x'],p['y'],p['w'],p['h'],NODE,int(255*al))
            # Small role labels retain the original graph rather than flattening it into reading order.
            self.text(c,p['node']['role'],p['x']+16,p['y']+24,17,(140,151,164),a=int(255*al))
            incoming=[e for e in gs['edges'] if e['b']==id and visibility.get(e['a'],0)>0]
            symbol=' '.join(dict.fromkeys(SYMBOL.get(e['type'],'≠') for e in incoming))
            self.text(c,symbol,p['x']+p['w']-80,p['y']+24,19,(153,164,174),a=int(230*al))
            if focus and focus[3]['id']==id:rect(c,p['x'],p['y'],3,p['h'],PALETTE[focus[2]],int(210*al))
        cursor={id:p['y']+53 for id,p in pos.items()}
        for ch,alpha in zip(layout['chunks'],key[1]):
            if alpha:
                cursor[ch['id']]=self.draw_spans(c,ch['display'],ch['original_indices'],ch['x'],cursor[ch['id']],ch['size'],ch['width'],'body',ch['id'],int(255*alpha))
        return sf.makeImageSnapshot()

    def focus(self,si,t):
        choices=[]
        for ch in self.layouts[si]['chunks']:
            if self.chunk_alpha(ch,t)<=0:continue
            links=[l for l in self.links if l['bead_id']==ch['id'] and max(ch['start'],l['bead_span'][0])<min(ch['end'],l['bead_span'][1])]
            if not links:continue
            # Narrow, current local statements take precedence over whole-section context.
            for l in links:choices.append((ch['window'][1]-ch['window'][0],ch['window'][0],l['group'],ch))
        return min(choices,key=lambda x:(x[0],-x[1],x[2])) if choices else None

    def frame(self,t):
        t=max(0,min(t,self.dur-.001));si=max(0,bisect.bisect_right(self.starts,t)-1)
        key=self.active_key(si,t)
        if key!=self.cached_key:self.cached_text=self.graph_image(si,t,key);self.cached_key=key
        sf=skia.Surface(W,H);c=sf.getCanvas();c.drawImage(self.cached_text,0,0)
        focus=self.focus(si,t);tint=PALETTE[focus[2]] if focus else (214,187,136)
        self.palette.tint=tint
        # h is an original MIDI instrument index; Op61's order is reversed from
        # Op60. It must not be silently treated as an audited left/right hand.
        self.palette.hand=None
        # Colour is an editorial attention cue shared with a real text fragment, not a claim of voice recognition.
        shade=tuple(int(v*.075) for v in tint);rect(c,0,TOP,W,H-TOP,shade)
        lo=np.searchsorted(self.ns,t-4);hi=np.searchsorted(self.ns,t+4)
        visible=SimpleNamespace(notes=self.song.notes[lo:hi],parts=self.song.parts,line_assignments=self.song.line_assignments,note_by_id=self.song.note_by_id)
        draw_balls(BallCanvas(c,tint),visible,self.mapping,t,self.palette,self.cfg)
        # A subtle central glow keeps the current-time column legible without a label or timestamp.
        for n in self.song.notes[max(0,np.searchsorted(self.ns,t-7)):np.searchsorted(self.ns,t)]:
            if n.time<t<n.end:
                a=self.assignments[n.note_id];nextnote=self.song.note_by_id.get(a.successor_note_id,n)
                progress=(t-n.time)/n.duration;y=self.mapping.y(n.pitch)+(self.mapping.y(nextnote.pitch)-self.mapping.y(n.pitch))*progress
                _,yy=BallCanvas(c,tint).xy(0,y);r=self.mapping.radius(n.duration)*(H-TOP)*.5*(1-progress)
                for rr,alpha in [(r+6,12),(r+3,22)]:c.drawCircle(960,yy,rr,paint(self.palette.rgb(n),alpha))
        draw_center_guide(c,tint)
        return sf.makeImageSnapshot()

    def save_qa(self):
        write(ROOT/f'qa/{self.work}_v2_density{self.density}.json',{'work':self.work,'pages':self.qa,'minimum_body_font':min(p['body_font'] for p in self.qa),'now_x':960,'music_band':[0,TOP,W,H],
            'music_renderer':'mamviz.renderers.draw_balls, original circle and flying-core formulas; Skia backend',
            'music_successors':'existing deterministic heuristic; not verified score voices',
            'music_colour':'editorial attention cue from currently visible linked text; does not assert physical voice identity',
            'future_notes':'shown to right of central present, as in Op52','timing_basis':'existing aligned bar starts; explicit bead scope and sentence locators',
            'central_transport_marker':'always visible; independent of sounding-note cores, including silence',
            'input_sha256':sha(ROOT/f'input/{self.work}.json')})

def stills(work,density=0):
    f=Film(work,density);d=ROOT/f'previews/v2/density{density}/{work}';d.mkdir(parents=True,exist_ok=True)
    for i,(a,b) in enumerate(zip(f.starts,f.ends)):
        f.frame(a+(b-a)*.55).save(str(d/f'{i+1:02d}.png'),skia.EncodedImageFormat.kPNG,100)
    f.save_qa();print(work,density,'pages',len(f.pages),'minfont',min(q['body_font'] for q in f.qa),flush=True)

def render(work,start=0,end=None,out=None,density=0,encoder='libx264'):
    f=Film(work,density);end=min(end or f.dur,f.dur);duration=end-start
    out=Path(out or ROOT/f'out/{work}_r54weave_DAG2_v2.mp4');out.parent.mkdir(parents=True,exist_ok=True)
    audio_codec=['-c:a','copy'] if start==0 and abs(end-f.dur)<.01 else ['-c:a','aac','-b:a','256k']
    audio_input=(['-ss',str(start)] if start else [])+['-i',f.src['audio']]
    video_codec=['-c:v','h264_qsv','-preset','medium','-global_quality','18','-pix_fmt','nv12'] if encoder=='h264_qsv' else ['-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p']
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s','1920x1080','-r','30','-i','pipe:0',*audio_input,'-t',str(duration),'-map','0:v:0','-map','1:a:0',*video_codec,*audio_codec,'-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);n=round(duration*FPS)
    try:
        for i in range(n):
            proc.stdin.write(f.frame(start+i/FPS).tobytes())
            if i%1800==0:print(work,'v2',round(i/FPS),'/',round(duration),flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg failed')
    f.save_qa();write(out.with_suffix('.json'),{'work':work,'variant':'v2','encoder':encoder,'central_guide_in_render':True,'start':start,'end':end,'frames':n,'fps':FPS,'video_sha256':sha(out),'source_sha256':sha(ROOT/f'input/{work}.json')})

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('command',choices=['stills','render']);p.add_argument('--work',required=True);p.add_argument('--density',type=int,default=0);p.add_argument('--start',type=float,default=0);p.add_argument('--end',type=float);p.add_argument('--out');p.add_argument('--encoder',choices=['libx264','h264_qsv'],default='libx264');a=p.parse_args()
    if a.command=='stills':stills(a.work,a.density)
    else:render(a.work,a.start,a.end,a.out,a.density,a.encoder)
