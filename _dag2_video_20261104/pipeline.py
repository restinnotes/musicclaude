"""DAG2 reproducible CLI. Plans are cached; render and QA are entirely local."""
import argparse, concurrent.futures, json, os, shutil, subprocess, sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dag2 import ROOT, EVO, WORKS, read, write, sha, freeze, prepare, call, repair_headers, parse

def compile_all():
 from physical import compile_one
 from film import stills
 for w in WORKS:compile_one(w);stills(w,'v1')

def review():
 # Files are attached through the paced gpt3 transport, with original receipts.
 paths=[ROOT/'reference/op52_245.png'];selection={}
 for w in WORKS:
  pages=read(ROOT/f'qa/{w}_v1_layout.json')['pages']
  dense=min(range(len(pages)),key=lambda i:pages[i]['body_font'])
  late=min(range(len(pages)*2//3,len(pages)),key=lambda i:pages[i]['body_font'])
  selection[w]={'densest':pages[dense]['sec'],'late_densest':pages[late]['sec'],'rule':'minimum body font over all segments and over final third; earliest breaks ties'}
  for i in [dense,late]:paths.append(ROOT/f'previews/v1/{w}/{i+1:02d}.png')
 write(ROOT/'qa/representative_scenes.json',selection)
 msg='''你是DAG2视频展示层的独立静帧审查者。附件依次为旧Op52基线、r54weave新布局的4处高风险静帧。只评价你看到的画面，不声称看过整段运动或听过音频。用户明确要求全文保留、可暂停回看，不以读速为由删字；基线为上字下图右提纲，相关线和珠子靠近、局部同色，右栏过去阶段折叠、当前阶段展开，引用前文显示回望。现在最小正文21px，全部27段的全部线/珠子已机械逐字核验。重复的线若有“续”字，是跨栏珠子继续沿用同一句线，非内容漏删。颜色只对应本段文字联系，不是固定情绪类别；音符只有明确小节+声部才染色，其余中性，未来阶段不提前展示故事。请检查遮挡、裁切、层级、密集段可辨认性、主区/右栏/音乐关系、对应色是否过多或无法分辨。不要要求改写正文，也不要为了炫技增加无意义图形。只输出JSON：{"verdict":"pass或revise","blocking":[{"image":"文件名","issue":"具体可见问题","fix":"最小改法"}],"acceptable_tradeoffs":["..."],"strengths":["..."],"not_verified":["..."],"notes":"..."}。pass意为此完整文字基础版可交付，不代表没有后续优化空间。'''
 folder=ROOT/'runs/visual_review_v2';folder.mkdir(parents=True,exist_ok=True)
 copies=folder/'attachments';copies.mkdir(exist_ok=True)
 unique=[]
 for i,path in enumerate(paths):
  name=f'{i+1:02d}_{path.parent.name}_{path.name}';dest=copies/name
  if dest.exists():assert sha(dest)==sha(path)
  else:shutil.copyfile(path,dest)
  unique.append(dest)
 paths=unique
 assert len({p.name.casefold() for p in paths})==len(paths)
 manifest={str(p):sha(p) for p in paths};write(folder/'attachments.json',manifest)
 inp=folder/'prepared_input.txt'
 if inp.exists():assert inp.read_text(encoding='utf8')==msg
 else:inp.write_text(msg,encoding='utf8')
 os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo,gpt3_call
 # The text-only backup cannot review images. Preserve gpt3's same scheduling
 # and protection checks, but never send an image task to an incapable fallback.
 rid='dag2_20261104_visual_review_v2';(evo.RUNS/rid).mkdir(exist_ok=True);evo.check_submission()
 response=evo.output(rid) if evo.done(rid) else gpt3_call.call(rid,msg,None,evo.G6,{'stage':'DAG2-static-visual-review','attach':[str(p) for p in paths],'web':True})
 if response:
  receipt=read(evo.RUNS/rid/'call.log');assert receipt['route']=='gpt3-serial' and receipt['completed']
  (folder/'output.txt').write_text(response,encoding='utf8');result=parse(response);write(ROOT/'qa/visual_review_v2.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
 elif gpt3_call.protection_signal():
  import mg_schedule;mg_schedule.fail(rid,{'type':'suspicious_behavior','message':gpt3_call.stopped()})

def full_one(w):
 from film import render
 render(w,'v1',0,None,ROOT/f'out/{w}_r54weave_DAG2_v1.mp4')

def remux_audio():
 # Preserve the AAC priming packet: an unnecessary -ss 0 may discard it.
 # This corrects only muxed audio; rendered video packets are copied unchanged.
 for w in WORKS:
  p=ROOT/f'out/{w}_r54weave_DAG2_v1.mp4';temp=p.with_name(p.stem+'_remux.mp4');src=read(ROOT/f'input/{w}.json');duration=read(ROOT/f'input/{w}_music.json')['dur'];old_sha=sha(p)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-i',src['audio'],'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(duration),'-movflags','+faststart',str(temp)],check=True)
  arrays=[]
  for q in [src['audio'],str(temp)]:arrays.append(subprocess.check_output(['ffmpeg','-v','error','-i',q,'-map','0:a:0','-ac','1','-ar','16000','-f','f32le','-']))
  assert arrays[0]==arrays[1],(w,'remuxed PCM differs')
  temp.replace(p);receipt=read(p.with_suffix('.json'));receipt['audio_remux']={'parent_video_sha256':old_sha,'reason':'preserve original AAC priming by avoiding a redundant input seek at zero','full_pcm_identical':True};receipt['video_sha256']=sha(p);write(p.with_suffix('.json'),receipt)
  print(w,'original complete decoded audio preserved',flush=True)

def media_qa():
 from film import Film, W, H
 import skia
 manifest=read(ROOT/'input/manifest.json');result={'source_integrity':{},'media':{}}
 for w in WORKS:
  frozen=manifest[w]
  checks={key:sha(p)==frozen[key] for key,p in [('input_sha256',ROOT/f'input/{w}.json'),('music_sha256',ROOT/f'input/{w}_music.json'),('graph_sha256',Path(frozen['graph'])),('joined_sha256',Path(frozen['joined'])),('audio_sha256',Path(frozen['audio']))]}
  assert all(checks.values());result['source_integrity'][w]=checks
  path=ROOT/f'out/{w}_r54weave_DAG2_v1.mp4'
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
  video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio');expected=read(ROOT/f'input/{w}_music.json')['dur']
  assert (video['width'],video['height'])==(1920,1080) and video['r_frame_rate']=='30/1'
  assert abs(float(info['format']['duration'])-expected)<0.08
  assert abs(float(video['duration'])-float(audio['duration']))<0.08
  # Complete decoder pass catches corrupt/truncated packets rather than trusting headers.
  subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True)
  correlations=[];pcm=[]
  # Decode both from the beginning. Independently fast-seeking AAC containers
  # can reset the resampler at different fractional phases and produce a false
  # waveform mismatch despite an identical complete decoded audio stream.
  for audio_path in [frozen['audio'],str(path)]:
   raw=subprocess.check_output(['ffmpeg','-v','error','-i',audio_path,'-map','0:a:0','-ac','1','-ar','16000','-f','f32le','-'])
   pcm.append(np.frombuffer(raw,dtype=np.float32))
  identical_pcm=np.array_equal(pcm[0],pcm[1]);assert identical_pcm,(w,'full decoded PCM differs')
  for second in [2,expected*.5,expected-12]:
   a=round(second*16000);b=a+8*16000
   correlation=float(np.corrcoef(pcm[0][a:b],pcm[1][a:b])[0,1]);assert correlation>.999,(w,second,correlation)
   correlations.append({'second':second,'correlation':correlation})
  q=read(ROOT/f'qa/{w}_v1_layout.json');src=read(ROOT/f'input/{w}.json')
  for s,page in zip(src['segments'],q['pages']):assert set(page['all_ids'])=={x['id'] for x in s['items']+s['beads']}
  film=Film(w);encoded_checks=[]
  for s,a,b in zip(film.segs,film.starts,film.ends):
   t=a+(b-a)*.55
   expected_frame=film.frame(t).toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[:,:,:3]
   raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
   decoded=np.frombuffer(raw,dtype=np.uint8).reshape(H,W,3)
   delta=expected_frame[103:705,48:1446].astype(float)-decoded[103:705,48:1446].astype(float)
   mse=float(np.mean(delta*delta));psnr=float(10*np.log10(255**2/max(mse,1e-12)));assert psnr>32,(w,s['sec'],psnr)
   encoded_checks.append({'sec':s['sec'],'main_panel_psnr':psnr,'pass':True})
  result['media'][w]={'path':str(path),'sha256':sha(path),'duration':info['format']['duration'],'frames':video['nb_frames'],'audio_duration':audio['duration'],'decode_pass':True,'full_audio_pcm_identical':bool(identical_pcm),'audio_correlations':correlations,'encoded_text_frames':encoded_checks,'all_text_ids':True,'minimum_body_font':q['minimum_body_font']}
 write(ROOT/'qa/final_media.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('command',choices=['plan','compile','review','render','qa','remux-audio']);a=p.parse_args()
 if a.command=='plan':
  freeze();prepare()
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(call,WORKS))
  repair_headers()
 elif a.command=='compile':compile_all()
 elif a.command=='review':review()
 elif a.command=='remux-audio':remux_audio()
 elif a.command=='render':
  assert read(ROOT/'qa/visual_review_v2.json')['verdict']=='pass','Resolve visual review first'
  with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(full_one,WORKS))
 else:media_qa()
