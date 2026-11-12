"""逐段查第六版版面：字有没有超出音乐带上方、词有没有超出右边界；每段出一帧总览。python qa/layout6.py 作品 TAG"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.stdout.reconfigure(encoding='utf-8')
import skia
from film_v6 import Film6, SEP
from film_v3 import X1, Y1
from film_v4 import RX
w, tag = sys.argv[1:3]; f = Film6(w, tag); bad = 0; d = Path(__file__).parent/'f14'/f'{w}_{tag}'; d.mkdir(parents=True, exist_ok=True)
for n, (t0, sec) in enumerate(f.starts):
    p = f.pages[sec]; total = sum(b['h'] for b in p['bands'])+sum(p['gaps'][k]['h'] if k in p['gaps'] else SEP for k in range(len(p['bands'])-1)); over = p['top']+total-Y1; wide = 0.
    for b in list(p['bands'])+list(p['gaps'].values()):
        font = f.font('bead', b['ws'])
        for row in b['rows']:
            for wd, dx in row: wide = max(wide, RX+dx+font.measureText(wd['text'])-X1)
    bad += over > 0 or wide > 0; lo, hi = f.src[sec]['window']
    print(sec, '词号', [b['ws'] for b in p['bands']], '线号', [b['ls'] for b in p['bands']], '超高', round(max(0, over)), '超宽', round(max(0, wide)))
    f.frame(lo+(hi-lo)*.6).save(str(d/f'{n:02d}.png'), skia.EncodedImageFormat.kPNG, 100)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(d/'%02d.png'), '-vf', 'scale=640:-1,tile=4x4', '-frames:v', '1', str(d/'sheet.png')], check=True); print('问题段', bad, d/'sheet.png')
