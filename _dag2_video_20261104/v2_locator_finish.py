"""Repair one pure location-clause elision in an already encoded card.

Only S01-B5's rectangle is overlaid, through the first section. All remaining
base pixels and the audio track remain sourced from the verified V2 video.
"""
import subprocess,sys
import skia
from dag2 import ROOT,read,write,sha
from film_v2 import Film

def finish():
    f=Film('op61');p=f.layouts[0]['positions']['S01-B5'];assert (p['x'],p['y'],p['w'])==(920,502.64,468)
    x,y,w,h=int(p['x']),int(p['y']),int(p['w']),174
    # Align crop to the integer pixel origin, including antialiasing at the fractional card edge.
    end=f.ends[0];patch=ROOT/'experiments/v2_op61_locator_card.mkv'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','bgra','-video_size',f'{w}x{h}','-framerate','30','-i','pipe:0','-an','-c:v','ffv1','-threads','2',str(patch)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);key=None;data=None
    try:
        for i in range(round(end*30)):
            t=i/30;k=f.active_key(0,t)
            if k!=key:
                image=f.graph_image(0,t,k);array=image.toarray(colorType=skia.ColorType.kBGRA_8888_ColorType);data=array[y:y+h,x:x+w].copy().tobytes();key=k
            proc.stdin.write(data)
    finally:proc.stdin.close()
    assert proc.wait()==0
    path=ROOT/'out/op61_r54weave_DAG2_v2.mp4';rec=read(path.with_suffix('.json'))
    assert sha(path)==rec['video_sha256']
    old=ROOT/'experiments/v2_base/op61_before_locator_elision.mp4';assert not old.exists();path.replace(old);temp=path.with_name('_locator_'+path.name)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(old),'-i',str(patch),'-filter_complex_threads','1','-filter_complex',f'[0:v][1:v]overlay={x}:{y}:enable=lt(t\\,{end}):eof_action=pass:repeatlast=0:format=yuv420[v]',
                    '-map','[v]','-map','0:a:0','-c:v','h264_qsv','-preset','medium','-global_quality','18','-pix_fmt','nv12','-c:a','copy','-t',str(f.dur),'-movflags','+faststart',str(temp)],check=True)
    temp.replace(path);rec['locator_elision_repair']={'node':'S01-B5','reason':'remove whole pure location afterthought; retain grammatical experience text, no new prose','parent':str(old),'parent_sha256':rec['video_sha256'],'patch_sha256':sha(patch)};rec['video_sha256']=sha(path);write(path.with_suffix('.json'),rec);print('Op61 location-only clause repaired',flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');finish()
