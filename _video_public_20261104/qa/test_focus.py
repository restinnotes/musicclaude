"""抽帧检查放大动画。python qa/test_focus.py WORK TAG SEC"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding='utf-8')
import skia
import film_v3 as F

work, tag, sec = sys.argv[1:4]
f = F.Page(work, tag)
foc = f.pages[sec]['focus']
print(sec, f.src[sec]['window'], len(foc))
for x in foc:
    print(round(x['a'], 1), round(x['z'], 1), x['size'], x['it']['text'][:24], '局部' if x['it'].get('win') else '')
x = foc[0]
for n, tt in [('中', (x['a']+x['z'])/2), ('长大', x['a']+.14), ('静', x['z']+.05)]:
    f.frame(tt).save(str(F.ROOT/f'out/动画测试_{n}.png'), skia.EncodedImageFormat.kPNG, 100)
