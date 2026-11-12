"""逐段查版面：字有没有超出音乐带上方、词块有没有超出右边界；输出每段一帧的总览图。python qa/layout_check.py 作品 TAG"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.stdout.reconfigure(encoding='utf-8')
import skia
import film_v5
from film_v5 import Film5, CHIP_X, SEP
from film_v3 import X1, Y1
from film_v4 import RX
w, tag = sys.argv[1:3]; f = Film5(w, tag); bad = 0; d = Path(__file__).parent/'f10'/f'{w}_{tag}'; d.mkdir(parents=True, exist_ok=True); n = 0
for t0, sec in f.starts:
    p = f.pages[sec]; total = sum(b['h'] for b in p['bands'])+sum(p['gaps'][k]['h'] if k in p['gaps'] else SEP for k in range(len(p['bands'])-1)); bot = p['top']+total; over = bot-Y1; wide = 0.
    for b in p['bands']:
        size = b['ws']; font = f.font('bead', size)
        for row in b['rows']:
            seen = {}; x = RX
            for wd, _ in row: seen.setdefault((wd.get('from') or [wd['text']])[0], []).append(wd)
            for ch in seen.values(): x += sum(font.measureText(q['text']) for q in ch)+size*.5*(len(ch)-1)+CHIP_X*2+14
            wide = max(wide, x-X1)
    fs = (p['bands'][0]['ls'], p['bands'][0]['ws']); lo, hi = f.src[sec]['window']
    print(sec, '词号', [b['ws'] for b in p['bands']], '线号', [b['ls'] for b in p['bands']], '底', round(bot), '超高', round(over) if over > 0 else 0, '超宽', round(wide) if wide > 0 else 0, '秒', round(hi-lo)); bad += over > 0 or wide > 0
    f.frame(lo+(hi-lo)*.6).save(str(d/f'{n:02d}.png'), skia.EncodedImageFormat.kPNG, 100); n += 1
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(d/'%02d.png'), '-vf', 'scale=640:-1,tile=4x4', '-frames:v', '1', str(d/'sheet.png')], check=True); print('问题段', bad, d/'sheet.png')
