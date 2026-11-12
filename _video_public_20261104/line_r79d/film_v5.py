"""大众版画面第五版。
- 线下面有实心底色（情绪色），一眼看出是几组。
- 交界：共享词块是一块从上一组颜色渐变到下一组颜色的实心块，骑在两组的接缝上；有共享的两组贴在一起，没共享的分开。
- 动画：当前响着的音是什么情绪，同情绪的组和词就跟着亮（不分先后，全屏字一直在）；局部词到时实心亮起、放大、放出波纹，音乐带上对应的音区同色框亮起并有光柱连到词。
python film_v5.py still --work op60 --tag w8 --sec S04 S05 --at .6 --name 方向7
python film_v5.py render --work op60 --tag w8 --start a --end b --out x.mp4
"""
import argparse, re, subprocess, sys
import numpy as np
import skia
from pathlib import Path
import film_v4
from film_v4 import Words, LADDER, LW, RX, RW, PREV, PAD
from film_pub import W, H, BG, WHITE, FPS, ease, mix, TOP
from film_v3 import EMOTIONS, X0, X1, Y0, Y1, ROOT
SEP = 8; PLATE = LW+18; CHIP_X = 12; CHIP_Y = 7


def rrect(x, y, w, h, r=10): return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


class Film5(Words):
    def __init__(self, work, tag):
        super().__init__(work, tag)
        # 每一刻响着的音是什么情绪，平滑后给画面用。
        names = list(EMOTIONS); idx = {tuple(EMOTIONS[k]): i for i, k in enumerate(names)}; step = .1; n = int(self.dur/step)+2
        act = np.zeros((n, len(names)))
        for note in self.song.notes:
            m = self.note_mark.get(note.note_id)
            if not m: continue
            i = idx.get(tuple(m[4]))
            if i is None: continue
            act[int(note.time/step):int(min(note.end, note.time+1.5)/step)+1, i] += 1
        kern = np.ones(9)/9
        for i in range(len(names)): act[:, i] = np.convolve(act[:, i], kern, 'same')
        # 当前最响的情绪算满分，其余按比例，这样总有一组明显亮着。
        top = act.max(1, keepdims=True); self.act = np.divide(act, top, out=np.zeros_like(act), where=top > 0); self.act_names = names; self.act_step = step
        # 每个音起音时给同情绪的字一个脉冲，字跟着音乐跳。
        ps = .04; pulse = np.zeros((int(self.dur/ps)+2, len(names)))
        for n0, note in zip(self.notes, self.song.notes):
            m = self.note_mark.get(note.note_id)
            if m and tuple(m[4]) in idx: pulse[int(note.time/ps), idx[tuple(m[4])]] += float(n0.get('en', .5))**1.5
        dec = np.exp(-ps/.28)
        for i in range(1, len(pulse)): pulse[i] = np.maximum(pulse[i], pulse[i-1]*dec)
        scale = np.percentile(pulse[pulse > .01], 90) if (pulse > .01).any() else 1.
        self.pulse = np.clip(pulse/scale, 0, 1); self.pulse_step = ps
        env = self.music.get('env') or []
        self.env = np.array([e[1] if isinstance(e, (list, tuple)) else e for e in env], float) if len(env) else np.zeros(1)
        if self.env.max() > 0: self.env = self.env/np.percentile(self.env, 98)
        self.env_step = self.dur/max(1, len(self.env))

    def active(self, t, emotion_rgb):
        i = min(len(self.act)-1, int(t/self.act_step)); names = self.act_names
        for k, name in enumerate(names):
            if tuple(EMOTIONS[name]) == tuple(emotion_rgb): return float(self.act[i, k])
        return 0.

    def beat(self, t, emotion_rgb):
        i = min(len(self.pulse)-1, int(t/self.pulse_step))
        for k, name in enumerate(self.act_names):
            if tuple(EMOTIONS[name]) == tuple(emotion_rgb): return float(self.pulse[i, k])
        return 0.

    def energy(self, t):
        return float(min(1, self.env[min(len(self.env)-1, int(t/self.env_step))]))

    # ---------- 版面 ----------
    def arrange(self, s):
        """交界词块放在两组接缝上，但不能把一组的词搬空：一组至少留一块自己的。"""
        perm, border, moved = super().arrange(s)
        kept = dict()
        for n, g in enumerate(s['groups']):
            chs = self.chunks(g.get('beads', [])); own = [c for c in chs if id(c[0]) not in moved]
            lost = [c for c in chs if id(c[0]) in moved]
            while lost and not own and chs:
                c = lost.pop(); own.append(c)
                for b in c: moved.discard(id(b)); kept[id(b)] = True
        border = {k: [b for b in v if id(b) not in kept] for k, v in border.items()}
        return perm, {k: v for k, v in border.items() if v}, moved

    def layout(self, s):
        gs = s['groups']; prev = self.prev_line(s['sec']); perm, border, moved = self.arrange(s)
        top = Y0+(PREV*1.3+12 if prev else 0); room = Y1-top
        for mw, ml, sw, sl in LADDER:
            bands = []
            for i in perm:
                g = gs[i]; major = g.get('rank') == '主'
                bands.append(self.band({**g, 'beads': [b for b in g.get('beads', []) if id(b) not in moved]}, mw if major else sw, ml if major else sl, 1. if major else .92))
            gaps = {k: {'rows': self.flow(v, sw, RW-30), 'ws': sw} for k, v in border.items()}
            for v in gaps.values(): v['h'] = len(v['rows'])*(sw*1.3+CHIP_Y*2+18)+4
            if sum(b['h'] for b in bands)+sum(gaps[k]['h'] if k in gaps else SEP for k in range(len(bands)-1)) <= room: break
        return {'bands': bands, 'gaps': gaps, 'prev': prev, 'top': top, 'focus': []}

    def sense_wrap(self, text, size, width):
        """尽量在标点停顿处换行，一个小句放不下才在句中折。一句话还是一句话，扫的时候一眼一小句。"""
        f = self.font('line', size); out = []; cur = ''
        for part in re.findall(r'[^，。；？！：]+[，。；？！：”」]*', text) or [text]:
            if cur and f.measureText(cur+part) <= width and len(cur) < 9: cur += part; continue
            if cur: out.append(cur); cur = ''
            if f.measureText(part) <= width: cur = part
            else:
                rows = self.wrap(part, 'line', size, width)
                if len(rows[-1]) <= 4: rows = self.wrap(part, 'line', size, width*.82)
                out += rows[:-1]; cur = rows[-1]
        if cur: out.append(cur)
        return out

    def band(self, g, ws, ls, base):
        rows = self.flow(g.get('beads', []), ws, RW-30)
        lines = []
        for l in g.get('lines', []):
            rs = self.sense_wrap(l['text'], ls, LW-34)
            for n, r in enumerate(rs): lines.append((r, l is g['lines'][-1], n == 0))
        lh = len(lines)*ls*1.28+ls*.34*max(0, len(g.get('lines', []))-1)
        h = max(len(rows)*(ws*1.3+CHIP_Y*2+2), lh)+2*PAD
        return {'g': g, 'rows': rows, 'lines': lines, 'ws': ws, 'ls': ls, 'base': base, 'h': h}

    # ---------- 画 ----------
    def chip(self, c, ch, x, y, size, t, fade, s0, major):
        """一块词：同一块的词共用一个底块。到时亮起的局部词实心放大。"""
        f = self.font('bead', size); gap = size*.5
        ww = [f.measureText(b['text']) for b in ch]; total = sum(ww)+gap*(len(ch)-1)
        col = ch[0]['color']; win = next((b['win'] for b in ch if b.get('win')), None)
        stag = (sum(map(ord, ch[0]['text'])) % 6)*.05; k = ease((t-s0-stag)/.45) if s0 > 0 else 1.
        act = self.active(t, col); bt = self.beat(t, col)*act; a = fade*k
        fill = .08+.26*act+.34*bt; sc = 1+.015*act+.05*bt; txt = mix(col, WHITE, .5+.3*act+.2*bt); ring = 0.; solid = 0.
        if win:
            ta, tz = win
            if t < ta: fill = .05; txt = mix(BG, col, .45)
            elif t < tz:
                up = ease((t-ta)/.2); off = ease((tz-t)/.6); pop = max(0, 1-(t-ta)/.9)
                solid = up*off; sc = 1+(.08+.32*pop)*up*off; ring = max(0, 1-(t-ta)/1.1)
            else: fill = .22; txt = mix(col, WHITE, .6)
        w, h = total+CHIP_X*2, size*1.3+CHIP_Y*2; cx, cy = x+w/2, y+h/2
        c.save(); c.translate(cx, cy); c.scale(sc, sc); c.translate(-cx, -cy)
        if solid > 0:
            for n, al in [(16, 26), (9, 46), (4, 74)]: c.drawRRect(rrect(x-n, y-n, w+2*n, h+2*n, 12+n), skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(al*solid*a))))
        if solid > 0: c.drawRRect(rrect(x, y, w, h, 10), skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(255*a*solid))))
        if ring > 0:
            for q in (0., .35):
                rk = max(0, ring-q)
                if rk > 0: c.drawRRect(rrect(x-(1-rk)*70, y-(1-rk)*40, w+2*(1-rk)*70, h+2*(1-rk)*40, 16), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=skia.Color(*col, int(230*rk*solid*a))))
        tx = x+CHIP_X
        for b, wd in zip(ch, ww):
            self.text(c, b['text'], tx, y+CHIP_Y+size*1.02, 'bead', size, mix(txt, WHITE, solid) if solid else txt, a); tx += wd+gap
        c.restore()
        return cx, cy, w, solid

    def draw_rows(self, c, rows, ws, y, t, fade, s0, major, width=RW):
        """按块铺开。flow 已算好每个词的 x，这里重新按块排，让底块不重叠。"""
        f = self.font('bead', ws); gap = ws*.5; focus = []
        for row in rows:
            groups = []; seen = {}
            for b, _ in row:
                key = (b.get('from') or [b['text']])[0]
                if key not in seen: seen[key] = []; groups.append(seen[key])
                seen[key].append(b)
            x = RX
            for ch in groups:
                out = self.chip(c, ch, x, y, ws, t, fade, s0, major)
                if out[3] > 0: focus.append((out, ch[0]['color']))
                x += sum(f.measureText(b['text']) for b in ch)+gap*(len(ch)-1)+CHIP_X*2+14
            y += ws*1.3+CHIP_Y*2+2
        return focus

    def draw_band(self, c, b, y, t, fade, s0, skip_last=False, ext_top=0, ext_bot=0):
        gc = EMOTIONS[b['g']['emotion']]; major = b['base'] > .95; act = self.active(t, gc); en = self.energy(t); bt = self.beat(t, gc)*act
        top = y-ext_top; h = b['h']+ext_top+ext_bot
        # 右边浅色、左边（线下面）深色，都随当前音乐的情绪和强弱呼吸。
        right = mix(BG, gc, (.12 if major else .07)+.12*act+.08*bt); left = mix(BG, gc, (.36 if major else .24)+.30*act+.18*bt)
        c.drawRRect(rrect(X0, top, PLATE, h, 8), skia.Paint(AntiAlias=True, Color=skia.Color(*left, int(255*fade))))
        n = len(b['lines']); lh = n*b['ls']*1.28+b['ls']*.34*max(0, len(b['g'].get('lines', []))-1)
        yy = y+(b['h']-lh)/2; last = None; first = True
        for r, is_last, head in b['lines']:
            if head and not first: yy += b['ls']*.34
            first = False
            if is_last and major: last = last or (X0+14, yy, b['ls'])
            if not (skip_last and is_last and major): self.text(c, r, X0+14, yy+b['ls'], 'line', b['ls'], WHITE if major else mix(BG, WHITE, .9), fade)
            yy += b['ls']*1.28
        rh = len(b['rows'])*(b['ws']*1.3+CHIP_Y*2+2)
        focus = self.draw_rows(c, b['rows'], b['ws'], y+(b['h']-rh)/2, t, fade, s0, major)
        return last, focus

    def draw_gap(self, c, gap, a, b, y, t, fade, s0):
        """共享词块骑在两组接缝上：块的颜色从上一组渐变到下一组。"""
        ca, cb = EMOTIONS[a['g']['emotion']], EMOTIONS[b['g']['emotion']]; ws = gap['ws']; f = self.font('bead', ws); g2 = ws*.5; yy = y+3; focus = []
        for row in gap['rows']:
            groups = []; seen = {}
            for w, _ in row:
                key = (w.get('from') or [w['text']])[0]
                if key not in seen: seen[key] = []; groups.append(seen[key])
                seen[key].append(w)
            x = RX
            for ch in groups:
                ww = [f.measureText(w['text']) for w in ch]; total = sum(ww)+g2*(len(ch)-1)+CHIP_X*2+6; h = ws*1.3+CHIP_Y*2+6
                act = max(self.active(t, ca), self.active(t, cb)); bt = max(self.beat(t, ca)*self.active(t, ca), self.beat(t, cb)*self.active(t, cb)); sc = 1+.01*act+.035*bt; cx, cy = x+total/2, yy+h/2
                c.save(); c.translate(cx, cy); c.scale(sc, sc); c.translate(-cx, -cy)
                # 向两边溢出的色晕
                glow = skia.GradientShader.MakeLinear([skia.Point(0, yy-14), skia.Point(0, yy+h+14)], [skia.Color(*ca, int(120*fade)), skia.Color(*cb, int(120*fade))])
                c.drawRRect(rrect(x-10, yy-14, total+20, h+28, 18), skia.Paint(AntiAlias=True, Shader=glow))
                sh = skia.GradientShader.MakeLinear([skia.Point(0, yy), skia.Point(0, yy+h)], [skia.Color(*mix(BG, ca, .92), int(255*fade)), skia.Color(*mix(BG, cb, .92), int(255*fade))])
                c.drawRRect(rrect(x, yy, total, h, 12), skia.Paint(AntiAlias=True, Shader=sh))
                c.drawRRect(rrect(x, yy, total, h, 12), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=skia.Color(255, 255, 255, int(170*fade))))
                tx = x+CHIP_X+3
                for w, wd in zip(ch, ww):
                    self.text(c, w['text'], tx+1, yy+CHIP_Y+3+ws*1.02+1, 'bead', ws, (20, 22, 28), fade*.55); self.text(c, w['text'], tx, yy+CHIP_Y+3+ws*1.02, 'bead', ws, WHITE, fade); tx += wd+g2
                c.restore(); x += total+22
            yy += ws*1.3+CHIP_Y*2+18
        return focus

    def draw_page(self, c, sec, t, fade, s0, skip_prev=False, skip_last=False):
        p = self.pages[sec]; y = p['top']; last = None; all_focus = []
        if p['prev'] and not skip_prev:
            for r in self.wrap(p['prev'], 'line', PREV, X1-X0-30)[:1]: self.text(c, r, X0+14, Y0+PREV, 'line', PREV, mix(BG, WHITE, .5), fade)
        ys = []; yy = y
        for n, b in enumerate(p['bands']):
            ys.append(yy); yy += b['h']+(p['gaps'][n]['h'] if n in p['gaps'] else SEP)
        # 先画带（有共享的两带向接缝伸过去贴住），再把共享块压在接缝上。
        for n, b in enumerate(p['bands']):
            et = p['gaps'][n-1]['h']/2 if n-1 in p['gaps'] else 0; eb = p['gaps'][n]['h']/2 if n in p['gaps'] else 0
            l, fo = self.draw_band(c, b, ys[n], t, fade, s0, skip_last, et, eb); last = l or last; all_focus += fo
        for n, gap in p['gaps'].items():
            self.draw_gap(c, gap, p['bands'][n], p['bands'][n+1], ys[n]+p['bands'][n]['h'], t, fade, s0)
        # 光柱：亮起的词连到下面音乐里对应的音区
        for (cx, cy, w, solid), col in all_focus:
            y0 = ys[-1]+p['bands'][-1]['h']; hw = min(w/2, 70)
            if y0 >= TOP: continue
            path = skia.Path(); path.moveTo(cx-hw, y0); path.lineTo(cx+hw, y0); path.lineTo(cx+hw*2.4, TOP+4); path.lineTo(cx-hw*2.4, TOP+4); path.close()
            bm = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, TOP+4)], [skia.Color(*col, int(150*solid*fade)), skia.Color(*col, int(60*solid*fade))])
            c.drawPath(path, skia.Paint(AntiAlias=True, Shader=bm))
        return last

    def draw_music(self, c, t, mood):
        super().draw_music(c, t, mood)
        # 局部词对应的音区：同色框，随音乐滚动。
        for m in self.word_marks:
            if m[0]-4 > t or m[1]+1 < t: continue
            x0 = 960+self.mapping.x(m[0], t)*960; x1 = 960+self.mapping.x(m[1], t)*960
            if m[2] > 0 or m[3] < 127: y0, y1 = TOP+(H-TOP)*(1-self.mapping.y(m[3]))*.5-14, TOP+(H-TOP)*(1-self.mapping.y(m[2]))*.5+14
            else: y0, y1 = TOP+6, H-6
            on = min(ease((t-m[0]+.3)/.3), ease((m[1]-t+.6)/.6)); on = max(.18, on)
            x0, x1 = max(-40, x0), min(W+40, x1)
            if x1 <= x0: continue
            c.drawRRect(rrect(x0, y0, x1-x0, y1-y0, 10), skia.Paint(AntiAlias=True, Color=skia.Color(*m[4], int(38*on))))
            c.drawRRect(rrect(x0, y0, x1-x0, y1-y0, 10), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2, Color=skia.Color(*m[4], int(130*on))))


def render(work, tag, start, end, out):
    f = Film5(work, tag); end = min(end or f.dur, f.dur); d = end-start; out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    whole = start == 0 and abs(end-f.dur) < .01
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', *(['-ss', str(start)] if start else []), '-i', f.audio, '-t', str(d), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', *(['-c:a', 'copy'] if whole else ['-c:a', 'aac', '-b:a', '256k']), '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(round(d*FPS)): p.stdin.write(f.frame(start+i/FPS).tobytes())
    finally: p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed')
    print(out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, nargs='*', default=[.6]); a.add_argument('--name', default='方向7')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out'); a.add_argument('--t', type=float, nargs='*')
    x = a.parse_args()
    if x.cmd == 'render': render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Film5(x.work, x.tag)
        if x.t:
            for tt in x.t:
                p = ROOT/f'out/{x.name}_{x.work}_{tt}.png'; f.frame(tt).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
        for s in x.sec or []:
            lo, hi = f.src[s]['window']
            for at in x.at:
                p = ROOT/f'out/{x.name}_{x.work}_{s}_{at}.png'; f.frame(lo+(hi-lo)*at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
