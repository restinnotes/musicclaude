"""大众版画面第六版：只留该留的。
- 音乐完全用 film_pub 的画法和对齐数据（和弦余音收小、退到当前音后面）。只有词明确指向某个声音时，那几个音才换成那个词的颜色；那个词到时才亮。
- 线下面有底色；珠子一律没有底色。
- 交界的词用渐变字：从上一组的颜色渐变到下一组，放在两组接缝的高度。
- 没有脉动、没有光柱、没有方框。
python film_v6.py still --work op60 --tag w20 --sec S04 --at .6 --name 方向13
python film_v6.py render --work op60 --tag w20 --out x.mp4
"""
import argparse, re, subprocess, sys
import skia
from pathlib import Path
from film_v4 import Words, LADDER, LW, RX, RW, PREV, PAD
import numpy as np
import film_pub as FP
from film_pub import W, H, BG, WHITE, FPS, TOP, AMBER, BAND, BallCanvas, ease, mix
from film_v3 import EMOTIONS, X0, X1, Y0, Y1, ROOT
import film_v5
SEP = 10; PLATE = LW+18


def rrect(x, y, w, h, r=8): return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


class Film6(Words):
    sense_wrap = film_v5.Film5.sense_wrap

    def __init__(self, work, tag):
        super().__init__(work, tag)
        # 词一律用所在组的颜色；颜色只来自明确指向的标记，不读整段配色。
        ex = [m for m in self.marks if m[5]]; self.marks = ex; self.word_marks = ex; self.note_mark = {}
        for n in self.song.notes:
            best = None
            for m in ex:
                if m[0] <= n.time < m[1] and m[2] <= n.pitch <= m[3] and (best is None or m[1]-m[0] < best[1]-best[0]): best = m
            self.note_mark[n.note_id] = best
        ns = self.song.notes; self.chord_recede = {}; i = 0
        while i < len(ns):
            j = i+1
            while j < len(ns) and ns[j].time-ns[i].time <= .03: j += 1
            chord = ns[i:j]
            if len({n.pitch for n in chord}) >= 3 and j < len(ns):
                for n in chord:
                    if n.duration >= 1.: self.chord_recede[n.note_id] = max(ns[j].time, n.time+.22)
            i = j

    def arrange(self, s):
        """线严格按原来的顺序，不重排。共享词块只有落在相邻两条线之间才放接缝；一组至少留一块自己的词。"""
        gs = s['groups']; perm = tuple(range(len(gs))); border = {}; moved = set()
        for i, g in enumerate(gs):
            chs = self.chunks(g.get('beads', [])); left = len(chs)
            for ch in chs:
                j = self.links.get((s['sec'], ch[0]['text']))
                if j is None or abs(j-i) != 1 or left <= 1: continue
                border.setdefault(min(i, j), []).extend(ch); moved |= {id(b) for b in ch}; left -= 1
        return perm, border, moved

    def group_color(self, g): return EMOTIONS[g['emotion']]

    def rows_of(self, beads, size, width):
        """按块换行：同一块的词挨着，块和块之间空得多一些。"""
        f = self.font('bead', size); gap = size*.45; between = size*1.15; rows = [[]]; x = 0.
        for ch in self.chunks(beads):
            ww = [f.measureText(b['text']) for b in ch]; tot = sum(ww)+gap*(len(ch)-1)
            if x and x+between+tot > width: rows.append([]); x = 0.
            elif x: x += between
            for b, w in zip(ch, ww):
                if x and x+w > width: rows.append([]); x = 0.
                rows[-1].append((b, x)); x += w+gap
            x -= gap
        return rows

    def band(self, g, ws, ls, base):
        rows = self.rows_of(g.get('beads', []), ws, RW-10); lines = []
        for l in g.get('lines', []):
            for n, r in enumerate(self.sense_wrap(l['text'], ls, LW-34)): lines.append((r, l is g['lines'][-1], n == 0))
        lh = len(lines)*ls*1.28+ls*.34*max(0, len(g.get('lines', []))-1)
        h = max(len(rows)*ws*1.42, lh)+2*PAD
        return {'g': g, 'rows': rows, 'lines': lines, 'ws': ws, 'ls': ls, 'base': base, 'h': h}

    def layout(self, s):
        gs = s['groups']; prev = self.prev_line(s['sec']); perm, border, moved = self.arrange(s)
        top = Y0+(PREV*1.3+12 if prev else 0); room = Y1-top
        for mw, ml, sw, sl in LADDER:
            bands = []
            for i in perm:
                g = gs[i]; major = g.get('rank') == '主'
                bands.append(self.band({**g, 'beads': [b for b in g.get('beads', []) if id(b) not in moved]}, mw if major else sw, ml if major else sl, 1. if major else .92))
            gaps = {k: {'rows': self.rows_of(v, sw, RW-10), 'ws': sw} for k, v in border.items()}
            for v in gaps.values(): v['h'] = len(v['rows'])*sw*1.42+2
            fits = all(self.font('bead', b['ws']).measureText(w['text']) <= RW-10 for b in list(bands)+list(gaps.values()) for row in b['rows'] for w, _ in row)
            if fits and sum(b['h'] for b in bands)+sum(gaps[k]['h'] if k in gaps else SEP for k in range(len(bands)-1)) <= room: break
        return {'bands': bands, 'gaps': gaps, 'prev': prev, 'top': top, 'focus': []}

    def word(self, c, b, x, y, size, t, fade, s0, base_col):
        col = mix(base_col, WHITE, .62); sc = 1.; w = self.font('bead', size).measureText(b['text'])
        stag = (sum(map(ord, b['text'])) % 6)*.05; k = ease((t-s0-stag)/.45) if s0 > 0 else 1.; a = fade*k
        if b.get('win'):
            ta, tz = b['win']
            if t < ta: col = mix(BG, base_col, .5)
            elif t < tz:
                up = ease((t-ta)/.3); off = ease((tz-t)/.6); col = mix(col, WHITE, up*off); sc = 1+.14*up*off
        cx, cy = x+w/2, y+size*.62
        c.save(); c.translate(cx, cy); c.scale(sc, sc); c.translate(-cx, -cy); self.text(c, b['text'], x, y+size, 'bead', size, col, a); c.restore()

    def draw_band(self, c, b, y, t, fade, s0, skip_last=False, ext_top=0, ext_bot=0):
        gc = self.group_color(b['g']); major = b['base'] > .95; top = y-ext_top; h = b['h']+ext_top+ext_bot
        c.drawRRect(rrect(X0, top, PLATE, h), skia.Paint(AntiAlias=True, Color=skia.Color(*mix(BG, gc, .46 if major else .28), int(255*fade))))
        n = len(b['lines']); lh = n*b['ls']*1.28+b['ls']*.34*max(0, len(b['g'].get('lines', []))-1)
        yy = y+(b['h']-lh)/2; last = None; first = True
        for r, is_last, head in b['lines']:
            if head and not first: yy += b['ls']*.34
            first = False
            if is_last and major: last = last or (X0+14, yy, b['ls'])
            if not (skip_last and is_last and major): self.text(c, r, X0+14, yy+b['ls'], 'line', b['ls'], WHITE if major else mix(BG, WHITE, .9), fade)
            yy += b['ls']*1.28
        rh = len(b['rows'])*b['ws']*1.42; ry = y+(b['h']-rh)/2
        for row in b['rows']:
            for w, dx in row: self.word(c, w, RX+dx, ry, b['ws'], t, fade, s0, gc)
            ry += b['ws']*1.42
        return last

    def draw_gap(self, c, gap, a, b, y, t, fade, s0):
        """交界的词是渐变字：上半是上一组的颜色，下半是下一组的颜色。"""
        ca, cb = mix(self.group_color(a['g']), WHITE, .3), mix(self.group_color(b['g']), WHITE, .3); ws = gap['ws']; f = self.font('bead', ws); yy = y+1
        for row in gap['rows']:
            for w, dx in row:
                top, bot = yy+ws*.12, yy+ws*1.12; x = RX+dx
                sh = skia.GradientShader.MakeLinear([skia.Point(0, top), skia.Point(0, bot)], [skia.Color(*ca, int(255*fade)), skia.Color(*cb, int(255*fade))])
                c.drawString(w['text'], x, yy+ws, f, skia.Paint(AntiAlias=True, Shader=sh))
            yy += ws*1.42

    def draw_page(self, c, sec, t, fade, s0, skip_prev=False, skip_last=False):
        p = self.pages[sec]; y = p['top']; last = None
        if p['prev'] and not skip_prev:
            for r in self.wrap(p['prev'], 'line', PREV, X1-X0-30)[:1]: self.text(c, r, X0+14, Y0+PREV, 'line', PREV, mix(BG, WHITE, .5), fade)
        ys = []; yy = y
        for n, b in enumerate(p['bands']):
            ys.append(yy); yy += b['h']+(p['gaps'][n]['h'] if n in p['gaps'] else SEP)
        for n, b in enumerate(p['bands']):
            et = p['gaps'][n-1]['h']/2 if n-1 in p['gaps'] else 0; eb = p['gaps'][n]['h']/2 if n in p['gaps'] else 0
            last = self.draw_band(c, b, ys[n], t, fade, s0, skip_last, et, eb) or last
        for n, gap in p['gaps'].items(): self.draw_gap(c, gap, p['bands'][n], p['bands'][n+1], ys[n]+p['bands'][n]['h'], t, fade, s0)
        return last

    def tint_of(self, n):
        m = self.note_mark.get(n.note_id)
        return m[4] if m else AMBER

    core_style = FP.Film.core_style

    def draw_music(self, c, t, mood):
        """和 film_pub.Film.draw_music 一样，只是明确指向的音用那个词的颜色。"""
        c.drawRect(skia.Rect.MakeXYWH(0, TOP, W, H-TOP), skia.Paint(Color=skia.Color(*BAND, 255)))
        lo = np.searchsorted(self.ns, t-4); hi = np.searchsorted(self.ns, t+4); canvas = BallCanvas(c)
        for n in self.song.notes[lo:hi]:
            nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id)
            if nx is not None and nx.time-n.end < self.cfg['lines']['rest_gap']:
                x0, x1 = self.mapping.x(n.time, t), self.mapping.x(nx.time, t)
                if min(x0, x1) <= 1. and max(x0, x1) >= -1.: canvas.blend_line(x0, self.mapping.y(n.pitch), x1, self.mapping.y(nx.pitch), self.tint_of(n), 1., 1.6)
        for n in self.song.notes[lo:hi]:
            x = self.mapping.x(n.time, t); r = self.mapping.radius(n.duration)
            if -1.-r <= x <= 1.+r: canvas.blend_circle_poly(x, self.mapping.y(n.pitch), r, r, self.tint_of(n), .35, 36, fill=n.time >= t)
        cores = []
        for idx in np.flatnonzero((self.ns < t) & (self.note_ends > t)):
            n = self.song.notes[idx]; nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id, n); pr = (t-n.time)/n.duration
            y = self.mapping.y(n.pitch)+(self.mapping.y(nx.pitch)-self.mapping.y(n.pitch))*pr
            r, alpha = self.core_style(n, t, self.mapping.radius(n.duration)*(1-pr)); cores.append((alpha, y, r, self.tint_of(n)))
        for alpha, y, r, tint in sorted(cores, key=lambda row: row[0]):
            _, yy = canvas.xy(0, y); rp = r*(H-TOP)*.5
            for rr, al in [(rp+6, 12), (rp+3, 22)]: c.drawCircle(960, yy, rr, skia.Paint(AntiAlias=True, Color=skia.Color(*tint, int(al*alpha))))
            canvas.blend_circle_poly(0, y, r, r, tint, alpha, 36)


def render(work, tag, start, end, out):
    f = Film6(work, tag); end = min(end or f.dur, f.dur); d = end-start; out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
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
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, nargs='*', default=[.6]); a.add_argument('--name', default='方向13')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Film6(x.work, x.tag)
        for s in x.sec or []:
            lo, hi = f.src[s]['window']
            for at in x.at:
                p = ROOT/f'out/{x.name}_{x.work}_{s}_{at}.png'; f.frame(lo+(hi-lo)*at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
