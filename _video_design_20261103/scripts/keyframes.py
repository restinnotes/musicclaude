# 关键画面说明图：六帧 + 每帧一句说明
import sys
import cv2
import numpy as np
import skia
sys.path.insert(0, 'scripts')
import engine

ITEMS = [
    (146.8, '第 32 小节，全曲第一个顶点：字贴在它说的音旁边，线让开，不放字幕。'),
    (168.0, '第 36–37 小节：左手确实没有音，水面就没了，只剩一条细线。这是画面在说话，不是字。'),
    (112.0, '第 24 小节：空心圆是第 6 小节的旋律叠回来，同一首歌，这次变成了这样。'),
    (180.0, '第 40 小节：珠子写“空气一下凉了”“月光”，背景转成冷色。'),
    (400.0, '第 93 小节后：最响的地方。光和音符的大小都由录音的响度决定。'),
    (512.0, '曲终：整条线变成一张图，每首曲子都不一样。Center 到这时才出现。'),
]
film = engine.Film('work/op60_music_v3.json', 'work/op60_spec.json')
tf = skia.Typeface.MakeFromFile('work/fonts/Sans400.ttf')
font = skia.Font(tf, 25)
font.setSubpixel(True)
TW, TH, CAP = 960, 540, 66
sheet = np.full((3 * (TH + CAP), 2 * TW, 4), 16, dtype=np.uint8)
sheet[:, :, 3] = 255
surf = skia.Surface(sheet, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
canvas = surf.getCanvas()
for i, (t, cap) in enumerate(ITEMS):
    im = film.frame(t)
    im = cv2.resize(im, (TW, TH), interpolation=cv2.INTER_AREA)
    x = (i % 2) * TW
    y = (i // 2) * (TH + CAP)
    sheet[y:y + TH, x:x + TW, :3] = im
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(skia.Color4f(0.88, 0.87, 0.84, 1))
    # 说明超过一行时按字数断开
    if font.measureText(cap) > TW - 40:
        mid = len(cap) // 2
        cut = next((k for k in range(mid, len(cap)) if cap[k - 1] in '，。：'), mid)
        canvas.drawString(cap[:cut], x + 20, y + TH + 28, font, p)
        canvas.drawString(cap[cut:], x + 20, y + TH + 58, font, p)
    else:
        canvas.drawString(cap, x + 20, y + TH + 40, font, p)
surf.flushAndSubmit() if hasattr(surf, 'flushAndSubmit') else surf.flush()
open('out/关键画面.png', 'wb').write(cv2.imencode('.png', sheet[:, :, :3][:, :, ::-1])[1].tobytes())
print('ok')
