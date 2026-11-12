"""Composite the reviewed independent time guide without rerendering text/music.

The full base renders already in flight are preserved. Only a 32px overlay is
generated, then the local GPU encodes the composite. Audio packets are copied.
"""
import argparse,bisect,json,subprocess,sys
from pathlib import Path
import skia
from dag2 import ROOT,read,write,sha
from film_v2 import Film,PALETTE,TOP,draw_center_guide

def finish(work,clip=False):
    f=Film(work);start=45 if clip else 0;duration=32 if clip else f.dur
    path=ROOT/('out/op60_v2_局部动画样片.mp4' if clip else f'out/{work}_r54weave_DAG2_v2.mp4')
    receipt=read(path.with_suffix('.json'))
    if receipt.get('central_guide_in_render'):
        assert sha(path)==receipt['video_sha256'];print(work,'central guide already in render',flush=True);return
    if receipt.get('central_guide_composite') and sha(path)==receipt['video_sha256']:
        print(work,'guide composite already verified against receipt',flush=True);return
    assert sha(path)==receipt['video_sha256'],'Base receipt/file mismatch or rendering still active'
    folder=ROOT/'experiments/v2_base';folder.mkdir(exist_ok=True)
    base=folder/path.name
    assert not base.exists(),'Refuse to overwrite preserved base'
    path.replace(base);temp=path.with_name('_'+path.name)
    stripes={}
    for tint in [*PALETTE,(214,187,136)]:
        sf=skia.Surface(32,370);c=sf.getCanvas();c.clear(skia.ColorTRANSPARENT);c.translate(-944,-TOP);draw_center_guide(c,tint)
        stripes[tint]=sf.makeImageSnapshot().toarray(colorType=skia.ColorType.kBGRA_8888_ColorType,alphaType=skia.AlphaType.kUnpremul_AlphaType).tobytes()
    cmd=['ffmpeg','-v','error','-y','-i',str(base),'-f','rawvideo','-pixel_format','bgra','-video_size','32x370','-framerate','30','-i','pipe:0',
         '-filter_complex_threads','1','-filter_complex','[0:v][1:v]overlay=944:710:format=yuv420:shortest=1[v]',
         '-map','[v]','-map','0:a:0','-t',str(duration),'-c:v','h264_qsv','-preset','medium','-global_quality','18','-pix_fmt','nv12','-c:a','copy','-movflags','+faststart',str(temp)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);frames=round(duration*30)
    try:
        for i in range(frames):
            t=min(start+i/30,f.dur-.001);si=max(0,bisect.bisect_right(f.starts,t)-1);focus=f.focus(si,t);tint=PALETTE[focus[2]] if focus else (214,187,136)
            proc.stdin.write(stripes[tint])
            if i%3600==0:print(work,'guide',round(i/30),'/',round(duration),flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('Guide composite failed; preserved base remains recoverable')
    temp.replace(path);receipt['central_guide_composite']={'base':str(base),'base_sha256':receipt['video_sha256'],'encoder':'h264_qsv','guide_width':32,'transport_marker_not_sounding_note':True};receipt['video_sha256']=sha(path);write(path.with_suffix('.json'),receipt);f.save_qa()
    print(work,'central guide composited',flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('--work',required=True);p.add_argument('--clip',action='store_true');a=p.parse_args();finish(a.work,a.clip)
