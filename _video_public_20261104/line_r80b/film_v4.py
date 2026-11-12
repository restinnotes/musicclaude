"""大众版画面第四版：每组一条带，左边是线，右边是这条线对应的词；同一颗珠子的词挨在一起。
音乐按情绪分色（r3/colors_*），只属于某几小节的词到时亮起，对应的音同时变亮。换段时当前的线移到上方变暗。
python film_v4.py still --work op60 --tag w4 --sec S04 S05 --at .6
python film_v4.py render --work op60 --tag w4 --start a --end b --out x.mp4
"""
import argparse, bisect, itertools, subprocess, sys
import skia
from pathlib import Path
from film_pub import W, H, BG, WHITE, FPS, ease, mix
from film_v3 import Page, EMOTIONS, X0, X1, Y0, Y1, ROOT, R3, rd

LW = 560; RX = X0+LW+36; RW = X1-RX; PREV = 24; PAD = 14; BGAP = 16
LADDER = [(56, 42, 38, 30), (50, 40, 36, 29), (46, 37, 33, 28), (42, 34, 30, 26), (38, 31, 28, 25), (34, 29, 26, 24), (30, 27, 24, 22), (26, 25, 22, 20), (23, 23, 20, 19)]


class Words(Page):
    def __init__(self, work, tag):
        lp = R3/f'links_{work}_{tag}.json'; self.links = {}
        if lp.exists():
            for x in rd(lp)['links']: self.links[(x['sec'], x['first'])] = int(x['also'])
        super().__init__(work, tag)
        p = R3/f'colors_{work}_{tag}.json'
        if p.exists():
            for m in rd(p)['colors']:
                if m.get('emotion') in EMOTIONS and m.get('bars') and m['bars'][0] in self.bar_t and m['bars'][-1] in self.bar_end:
                    q = m.get('pitch') or [0, 127]; self.marks.append((self.bar_t[m['bars'][0]], self.bar_end[m['bars'][-1]], q[0], q[1], EMOTIONS[m['emotion']], ''))
        self.note_mark = {}
        for n in self.song.notes:
            best = None
            for m in self.marks:
                if m[0] <= n.time < m[1] and m[2] <= n.pitch <= m[3] and (best is None or m[1]-m[0] < best[1]-best[0]): best = m
            self.note_mark[n.note_id] = best
        self.word_marks = [m for m in self.marks if m[5]]

    def schedule(self, s, lo, hi):
        return []

    def prev_line(self, sec):
        i = [x for _, x in self.starts].index(sec)
        if not i: return ''
        p = self.sc['sections'][i-1]; main = next(g for g in p['groups'] if g.get('rank') == '主')
        return main['lines'][-1]['text'] if main.get('lines') else ''

    # ---------- 版面 ----------
    def chunks(self, beads):
        """同一颗珠子要点拆出的词算一块。"""
        out = []; seen = {}
        for b in beads:
            k = (b.get('from') or [b['text']])[0]
            if k not in seen: seen[k] = []; out.append(seen[k])
            seen[k].append(b)
        return out

    def flow(self, beads, size, width):
        f = self.font('bead', size); gap = size*.5; between = size*1.5; rows = [[]]; x = 0.
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
        rows = self.flow(g.get('beads', []), ws, RW-10)
        lines = []
        for l in g.get('lines', []):
            for r in self.wrap(l['text'], 'line', ls, LW-24): lines.append((r, l is g['lines'][-1]))
        h = max(len(rows)*ws*1.3, len(lines)*ls*1.3)+2*PAD
        return {'g': g, 'rows': rows, 'lines': lines, 'ws': ws, 'ls': ls, 'base': base, 'h': h}

    def arrange(self, s):
        """决定带的上下顺序，让共享的词块尽量落在相邻两带的交界。"""
        gs = s['groups']; shared = []
        for i, g in enumerate(gs):
            for ch in self.chunks(g.get('beads', [])):
                j = self.links.get((s['sec'], ch[0]['text']))
                if j is not None and j < len(gs) and j != i: shared.append((i, j, ch))
        mi = next(i for i, g in enumerate(gs) if g.get('rank') == '主'); best = None
        for perm in itertools.permutations(range(len(gs))):
            pos = {g: k for k, g in enumerate(perm)}
            score = sum(abs(pos[i]-pos[j]) == 1 for i, j, _ in shared)*10-pos[mi]-sum(k*g for k, g in enumerate(perm))*.001
            if best is None or score > best[0]: best = (score, perm, pos)
        _, perm, pos = best; moved = set(); border = {}
        for i, j, ch in shared:
            if abs(pos[i]-pos[j]) == 1:
                border.setdefault(min(pos[i], pos[j]), []).extend(ch); moved |= {id(b) for b in ch}
        return perm, border, moved

    def layout(self, s):
        gs = s['groups']; prev = self.prev_line(s['sec']); perm, border, moved = self.arrange(s)
        top = Y0+(PREV*1.3+12 if prev else 0); room = Y1-top
        for mw, ml, sw, sl in LADDER:
            bands = []
            for i in perm:
                g = gs[i]; major = g.get('rank') == '主'
                bands.append(self.band({**g, 'beads': [b for b in g.get('beads', []) if id(b) not in moved]}, mw if major else sw, ml if major else sl, .97 if major else .78))
            gaps = {k: {'rows': self.flow(v, sw, RW-10), 'ws': sw} for k, v in border.items()}
            for v in gaps.values(): v['h'] = len(v['rows'])*sw*1.3+10
            if sum(b['h'] for b in bands)+sum(gaps[k]['h'] if k in gaps else BGAP for k in range(len(bands)-1)) <= room: break
        return {'bands': bands, 'gaps': gaps, 'prev': prev, 'top': top, 'focus': []}

    def draw_gap(self, c, gap, a, b, y, t, fade, s0):
        ca, cb = EMOTIONS[a['g']['emotion']], EMOTIONS[b['g']['emotion']]; h = gap['h']
        fill = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, y), skia.Point(0, y+h)], [skia.Color(*ca, int(40*fade)), skia.Color(*cb, int(40*fade))]))
        bar = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, y), skia.Point(0, y+h)], [skia.Color(*ca, int(240*fade)), skia.Color(*cb, int(240*fade))]))
        c.drawRect(skia.Rect.MakeXYWH(X0, y, X1-X0, h), fill); c.drawRect(skia.Rect.MakeXYWH(X0, y, 5, h), bar)
        yy = y+5
        for row in gap['rows']:
            for w, dx in row: self.word(c, w, RX+dx, yy, gap['ws'], t, fade, s0, True)
            yy += gap['ws']*1.3

    # ---------- 画 ----------
    def word(self, c, b, x, y, size, t, fade, s0, major):
        col = b['color']; base = col if major else mix(BG, col, .85); sc = 1.; halo = 0.
        w = self.font('bead', size).measureText(b['text'])
        stag = (sum(map(ord, b['text'])) % 6)*.05; k = ease((t-s0-stag)/.45) if s0 > 0 else 1.
        a = fade*k; sc = .84+.16*k
        if b.get('win'):
            ta, tz = b['win']
            if t < ta: base = mix(BG, col, .22)
            elif t < tz:
                up = ease((t-ta)/.25); pop = max(0, 1-(t-ta)/.7); off = ease((tz-t)/.5)
                sc = 1+(.04+.2*pop)*up*off; halo = up*off; base = mix(col, WHITE, .5*up*off)
        cx, cy = x+w/2, y+size*.62
        c.save(); c.translate(cx, cy); c.scale(sc, sc); c.translate(-cx, -cy)
        if halo > 0: c.drawRoundRect(skia.Rect.MakeXYWH(x-12, y+size*.06, w+24, size*1.16), 10, 10, skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(70*halo*fade))))
        self.text(c, b['text'], x, y+size, 'bead', size, base, a); c.restore()

    def draw_band(self, c, b, y, t, fade, s0, skip_last=False):
        gc = EMOTIONS[b['g']['emotion']]; major = b['base'] > .9
        c.drawRoundRect(skia.Rect.MakeXYWH(X0, y, X1-X0, b['h']), 10, 10, skia.Paint(AntiAlias=True, Color=skia.Color(*gc, int((22 if major else 13)*fade))))
        c.drawRect(skia.Rect.MakeXYWH(X0, y, 5, b['h']), skia.Paint(AntiAlias=True, Color=skia.Color(*gc, int(240*fade))))
        yy = y+PAD; last = None
        for r, is_last in b['lines']:
            if is_last and major: last = last or (X0+20, yy, b['ls'])
            if not (skip_last and is_last and major): self.text(c, r, X0+20, yy+b['ls'], 'line', b['ls'], mix(BG, WHITE, b['base']), fade)
            yy += b['ls']*1.3
        yy = y+PAD
        for row in b['rows']:
            for w, dx in row: self.word(c, w, RX+dx, yy, b['ws'], t, fade, s0, major)
            yy += b['ws']*1.3
        return last

    def draw_page(self, c, sec, t, fade, s0, skip_prev=False, skip_last=False):
        p = self.pages[sec]; y = p['top']; last = None
        if p['prev'] and not skip_prev:
            for r in self.wrap(p['prev'], 'line', PREV, X1-X0-30)[:1]: self.text(c, r, X0+20, Y0+PREV, 'line', PREV, mix(BG, WHITE, .4), fade)
        for n, b in enumerate(p['bands']):
            last = self.draw_band(c, b, y, t, fade, s0, skip_last) or last; y += b['h']
            if n in p['gaps']:
                self.draw_gap(c, p['gaps'][n], b, p['bands'][n+1], y, t, fade, s0); y += p['gaps'][n]['h']
            else: y += BGAP
        return last

    def frame(self, t):
        t = max(0, min(t, self.dur-.001)); sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255)); self.now = t
        i = max(0, bisect.bisect_right(self.secstart, t)-1); sec, s0 = self.starts[i][1], self.starts[i][0]
        k = ease((t-s0)/.7) if i > 0 else 1.; old = self.starts[i-1][1] if i > 0 else None
        mood = self.mood[sec] if k >= 1 else mix(self.mood[old], self.mood[sec], k)
        live = [m for m in self.word_marks if m[0] <= t < m[1] and m[1]-m[0] < .6*(self.src[sec]['window'][1]-self.src[sec]['window'][0])]
        lk = max([min(ease((t-m[0])/.3), ease((m[1]-t)/.5)) for m in live], default=0.)
        if live: mood = mix(mood, live[-1][4], lk)
        self.band = .03; mood = (120, 124, 134)
        self.draw_music(c, t, mood)
        if k < 1:
            last = self.draw_page(c, old, t, max(0., 1-k*2), self.starts[i-1][0], skip_prev=True, skip_last=True)
            self.draw_page(c, sec, t, max(0., k*2-1), s0+.3, skip_prev=True)
            if last:
                x0, y0, z0 = last; zz = z0+(PREV-z0)*k; yy = y0+(Y0-y0)*k; xx = x0+(X0+20-x0)*k; col = mix(mix(BG, WHITE, .97), mix(BG, WHITE, .4), k)
                prev = self.pages[sec]['prev']
                rows = self.wrap(prev, 'line', zz, LW-24 if k < .5 else X1-X0-30)
                for n, r in enumerate(rows[:1 if k >= .5 else 9]): self.text(c, r, xx, yy+zz+n*zz*1.3, 'line', zz, col, 1)
        else:
            self.draw_page(c, sec, t, 1, s0)
        self.rail(c, sec)
        return sf.makeImageSnapshot()

    def color_of(self, n):
        m = self.note_mark.get(n.note_id)
        if not m: return None, False
        return m[4], bool(m[5]) and m[0] <= self.now < m[1]


def render(work, tag, start, end, out):
    f = Words(work, tag); end = min(end or f.dur, f.dur); d = end-start; out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
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
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, default=.6); a.add_argument('--name', default='方向4')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Words(x.work, x.tag)
        for s in x.sec:
            lo, hi = f.src[s]['window']; p = ROOT/f'out/{x.name}_{x.work}_{s}.png'; f.frame(lo+(hi-lo)*x.at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
