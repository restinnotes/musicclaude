"""Checks the corrected design contract, timed text, and encoded deliverables."""
import argparse, bisect, json, math, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont
from dag2 import ROOT, EVO, read, write, sha, parse
from film_v2 import Film, TOP, BG
from v2_data import LOCATOR, display

def text_qa():
    results={}
    for w in ['op60','op61']:
        f=Film(w);rows=[];glyphs=[]
        for si,(s,g,layout) in enumerate(zip(f.segs,f.graph['segments'],f.layouts)):
            assert {n['id'] for n in g['nodes']}=={b['id'] for b in s['beads']}
            scopes=[]
            for n,b in zip(g['nodes'],s['beads']):
                assert n['text']==b['text']
                assert ''.join(ch['text'] for ch in n['chunks'])==b['text']
                for ch in n['chunks']:
                    assert ch['display']==''.join(b['text'][i] for i in ch['original_indices'])
                    assert not LOCATOR.search(ch['display']),(w,n['id'],ch)
                    a,z=ch['window'];assert f.starts[si]-.001<=a<z<=f.ends[si]+.001,(w,n['id'],ch)
                    for a,z in ch.get('windows',[ch['window']]):
                        assert f.starts[si]-.001<=a<z<=f.ends[si]+.001
                        assert f.chunk_alpha(ch,(a+z)/2)>0
                    assert f.chunk_alpha(ch,ch['window'][0]-.01)==0 and f.chunk_alpha(ch,ch['window'][1]+.01)==0
                    if [a,z]!=g['window']:scopes.append({'id':n['id'],'window':[a,z],'display':ch['display']})
                    for char,glyph in zip(ch['display'],f.font(layout['size']).textToGlyphs(ch['display'])):
                        if glyph==0:glyphs.append(char)
            p=list(layout['positions'].values())
            for i,a in enumerate(p):
                assert a['x']+a['w']<1450 and a['y']+a['h']<TOP
                for b in p[i+1:]:
                    assert a['column']!=b['column'] or a['y']+a['h']<=b['y'] or b['y']+b['h']<=a['y']
            assert set(e['a'] for e in g['edges'])|set(e['b'] for e in g['edges']) <= set(layout['positions'])
            assert f.mapping.x(123.4,123.4)==0
            t=f.starts[si]+.5*(f.ends[si]-f.starts[si]);img=np.asarray(f.frame(t));later=np.asarray(f.frame(t+.8))
            motion=np.count_nonzero(img[TOP:]!=later[TOP:]);assert motion>0
            rows.append({'sec':s['sec'],'node_count':len(p),'edges':len(g['edges']),'local_text_blocks':len(scopes),'music_motion_pixels':int(motion),'all_text_partitioned_exactly':True,'no_location_labels':True,'local_scopes':scopes})
        assert not glyphs,(w,sorted(set(glyphs)))
        f.save_qa()
        results[w]={'pass':True,'segments':rows,'local_blocks':sum(r['local_text_blocks'] for r in rows),'minimum_font':min(q['body_font'] for q in f.qa),'right_rail_max_bottom':max(q['rail']['rows_end'] for q in f.qa),'missing_glyphs':[]}
    write(ROOT/'qa/v2_design.json',results)
    print(json.dumps({k:{q:v[q] for q in ['pass','local_blocks','minimum_font','right_rail_max_bottom']} for k,v in results.items()},ensure_ascii=False),flush=True)

def examples():
    for w in ['op60','op61']:
        f=Film(w);d=ROOT/f'previews/v2/density0/{w}';d.mkdir(parents=True,exist_ok=True)
        for si,(a,b) in enumerate(zip(f.starts,f.ends)):
            # Select the densest real instant, not an all-text-at-once artificial image.
            chunks=f.layouts[si]['chunks'];candidates=sorted({a+1,(a+b)/2,*[(ch['window'][0]+ch['window'][1])/2 for ch in chunks]})
            best=max(candidates,key=lambda t:sum(len(ch['display']) for ch in chunks if f.chunk_alpha(ch,t)>.5))
            f.frame(best).save(str(d/f'{si+1:02d}.png'),skia.EncodedImageFormat.kPNG,100)
            write(d/f'{si+1:02d}.json',{'time':best,'section':f.segs[si]['sec'],'selection':'maximum visible text over representative midpoints'})
        f.save_qa()
    # Three meaningful densities in the same late four-node current phase.
    w='op60'
    for den in [0,1,2]:
        f=Film(w,den);t=f.starts[13]+3
        f.frame(t).save(str(ROOT/f'previews/v2/op60_rail_density{den}.png'),skia.EncodedImageFormat.kPNG,100);f.save_qa()
    # Timeline strip at musical boundaries. These are generated from actual frames.
    f=Film('op60');folder=ROOT/'previews/v2/local';folder.mkdir(exist_ok=True)
    for label,t in [('a',48),('b',56),('c',68)]:f.frame(t).save(str(folder/f'op60_local_{label}.png'),skia.EncodedImageFormat.kPNG,100)
    font=ImageFont.truetype(str(ROOT.parent/'_video_design_20261103/work/fonts/Sans400.ttf'),25)
    for kind,paths,labels in [
        ('右栏折叠对比',[ROOT/f'previews/v2/op60_rail_density{i}.png' for i in range(3)],['极简：仅当前短语','适中：当前与上一条','展开：当前阶段已走过的短语']),
        ('局部文字动画',[folder/f'op60_local_{s}.png' for s in ['a','b','c']],['局部变化出现前','热切上涌时','重新回柔时'])]:
        canvas=Image.new('RGB',(1920,1080 if kind.startswith('右栏') else 450),(14,18,24));draw=ImageDraw.Draw(canvas)
        for i,(p,label) in enumerate(zip(paths,labels)):
            im=Image.open(p)
            im=im.crop((1480,0,1920,710)).resize((580,936)) if kind.startswith('右栏') else im.resize((620,349))
            draw.text((i*640+20,20),label,font=font,fill=(225,228,231));canvas.paste(im,(i*640+15,75))
        canvas.save(ROOT/f'out/{kind}_v2.png')
    print('Examples and three-density comparison written',flush=True)

def review():
    paths=[ROOT/'reference/op52_245.png',ROOT/'previews/v2/density0/op60/04.png',ROOT/'previews/v2/density0/op61/07.png',ROOT/'out/右栏折叠对比_v2.png',ROOT/'out/局部文字动画_v2.png']
    folder=ROOT/'runs/v2_design_review';folder.mkdir(exist_ok=True);att=folder/'attachments';att.mkdir(exist_ok=True)
    copies=[]
    for i,p in enumerate(paths):
        dest=att/f'{i+1:02d}_{p.name}';shutil.copyfile(p,dest);copies.append(dest)
    msg='''你是视频展示层的严格审查者。附件1为Op52参考，附件2和3是新布局的两处最密实际时刻，附件4为右栏三档折叠，附件5为同一段局部文字的前/中/后三帧。用户纠正了V1：不能再把关系图混成连续文字，必须保留珠子的主体验/并列/段内先后/不同理解等关系；删除所有抬头、小节和分钟定位、配色说明；底部应真正仿Op52，当前时刻居中，圆点连线够大，并用已对应文字的颜色提示；局部珠子只在对应段落出现；右栏必须用折叠机制减少同屏文字。新脚本直接调用Op52时代mamviz的draw_balls，使用现有对齐音符，未来音符在右，过去空心在左，中央发声光点。音符色是当前体验的注意提示，不代表具体声部识别；原h仅为MIDI乐器编号，两首顺序不同，未把它当作左右手使用。主区全文保留（仅按用户要求去掉定位字样），局部文字按原定位分时显示，不以读速删改。左边是线节点，中间两列为珠子节点，关系边来自原机器图，原省略珠子不恢复或重写。
请检查实际可见问题：裁切/重叠、关系是否可读、音乐视觉是否仿Op52、中央时刻、右栏三种密度哪种适合默认、杂乱程度、时序三帧变化。不要仅因为机械检查通过就认可；发现严重问题必须revise。只输出JSON：{"verdict":"pass或revise","blocking":[{"image":"...","issue":"...","fix":"..."}],"default_density":0,"acceptable_tradeoffs":["..."],"not_verified":["..."],"notes":"..."}。只对所见静帧负责，不宣称看过全片。'''
    (folder/'prepared_input.txt').write_text(msg,encoding='utf8');write(folder/'attachments.json',{str(p):sha(p) for p in copies})
    os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo,gpt3_call
    rid='dag2_20261104_v2_design_review';(evo.RUNS/rid).mkdir(exist_ok=True);evo.check_submission()
    ans=evo.output(rid) if evo.done(rid) else gpt3_call.call(rid,msg,None,evo.G6,{'stage':'DAG2-v2-design-review','attach':[str(p) for p in copies],'web':True})
    if not ans:raise RuntimeError('Image review did not complete; inspect existing request')
    (folder/'output.txt').write_text(ans,encoding='utf8');obj=parse(ans);write(ROOT/'qa/v2_design_review.json',obj);print(json.dumps(obj,ensure_ascii=False),flush=True)

def media(work=None):
    target=ROOT/'qa/v2_final_media.json';result=read(target) if target.exists() else {}
    for w in ([work] if work else ['op60','op61']):
        f=Film(w);p=ROOT/f'out/{w}_r54weave_DAG2_v2.mp4'
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1')
        assert abs(float(info['format']['duration'])-f.dur)<.08
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        pcm=[]
        for q in [f.src['audio'],str(p)]:pcm.append(subprocess.check_output(['ffmpeg','-v','error','-i',q,'-map','0:a:0','-ac','1','-ar','16000','-f','f32le','-']))
        assert pcm[0]==pcm[1],(w,'original PCM changed')
        psnrs=[];events=[]
        scheduled=[(f'section_{i+1}',start+(end-start)*.55) for i,(start,end) in enumerate(zip(f.starts,f.ends))]
        scheduled.extend((f'local_event_{i+1}',t) for i,t in enumerate([48,56,68,143,500] if w=='op60' else [100,322.8,330,340,452.5,688.5,691,696]))
        for label,t in scheduled:
            frame=round(t*30);t=frame/30
            raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
            encoded=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)
            original=np.asarray(f.frame(t))[:,:,:3][:,:,::-1]
            mse=np.mean((encoded[:TOP].astype(float)-original[:TOP].astype(float))**2);psnr=10*math.log10(255**2/max(mse,1e-9));assert psnr>30,(w,label,psnr)
            mse_guide=np.mean((encoded[TOP:,944:976].astype(float)-original[TOP:,944:976].astype(float))**2);guide_psnr=10*math.log10(255**2/max(mse_guide,1e-9));assert guide_psnr>29,(w,label,'center guide',guide_psnr)
            psnrs.append(round(psnr,2));events.append({'label':label,'time':t,'text_psnr':round(psnr,2),'center_guide_psnr':round(guide_psnr,2)})
        frozen=read(ROOT/'input/manifest.json')[w]
        checks={k:sha(q)==frozen[k] for k,q in [('input_sha256',ROOT/f'input/{w}.json'),('music_sha256',ROOT/f'input/{w}_music.json'),('graph_sha256',Path(frozen['graph'])),('joined_sha256',Path(frozen['joined'])),('audio_sha256',Path(frozen['audio']))]}
        assert all(checks.values())
        result[w]={'pass':True,'source_integrity':checks,'full_decode':True,'original_decoded_pcm_exact':True,'duration':float(info['format']['duration']),'video_sha256':sha(p),'encoded_text_panel_psnr':psnrs,'encoded_event_checks':events}
        print(w,'full media verified',flush=True)
    write(target,result)

def clip_qa():
    f=Film('op60');p=ROOT/'out/op60_v2_局部动画样片.mp4';events=[]
    subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    for local in [3,11,23]:
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(local),'-i',str(p),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
        a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3).astype(float);b=np.asarray(f.frame(45+local))[:,:,:3][:,:,::-1].astype(float)
        values={}
        for key,slices in [('text',(slice(0,TOP),slice(None))),('center_guide',(slice(TOP,None),slice(944,976)))]:
            mse=np.mean((a[slices]-b[slices])**2);value=10*math.log10(255**2/max(mse,1e-9));assert value>29,(key,local,value);values[key]=round(value,2)
        events.append({'global_time':45+local,'psnr':values})
    subprocess.run(['ffmpeg','-v','error','-y','-ss','11','-i',str(p),'-frames:v','1',str(ROOT/'out/新版样片截图.png')],check=True)
    write(ROOT/'qa/v2_clip.json',{'pass':True,'full_decode':True,'events':events,'video_sha256':sha(p)});print(events,flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('command',choices=['text','examples','review','media','clip']);p.add_argument('--work',choices=['op60','op61']);a=p.parse_args()
    if a.command=='media':media(a.work)
    else:{'text':text_qa,'examples':examples,'review':review,'clip':clip_qa}[a.command]()
