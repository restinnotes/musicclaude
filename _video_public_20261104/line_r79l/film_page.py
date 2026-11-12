"""大众版一屏：一组线和珠子一种颜色，几组并排，不暗示先后。
局部珠子到那几小节才亮；那几小节的音符在音乐图上是同一种颜色，提前从右边过来。
python film_page.py still --work op60 --tag X --sec S04 --at .55
python film_page.py render --work op60 --tag X --start a --end b --out x.mp4
"""
import argparse, bisect, json, subprocess, sys
from pathlib import Path
import numpy as np, skia
import film_pub as FP
from film_pub import Film, W, H, TOP, BG, WHITE, GREY, AMBER, RAIL_X, BAND, FPS, ease, mix, BallCanvas
ROOT = Path(__file__).resolve().parent; OUT = ROOT/'r2'
def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
PALETTE = [(236, 191, 105), (112, 205, 222), (232, 142, 170), (170, 172, 240), (146, 208, 158), (230, 165, 118)]
NEUTRAL = (128, 124, 116)
DIM_BEAD = (126, 134, 144); DIM_LINE = (176, 182, 190)
X0, X1, Y0, Y1 = 64, 1440, 40, 690
NOPUNCT_HEAD = '，。、！？；：”’）》'


class Page(Film):
    def __init__(self, work, tag):
        self.work = work; self.sc = rd(OUT/f'script_{work}_{tag}.json'); self.src = {s['sec']: s for s in rd(OUT/f'{work}_src.json')['sections']}
        self.meta = rd(OUT/f'meta_{tag}.json'); self.music = rd(ROOT/f'input/{work}_music.json'); self.dur = self.music['dur']; self.audio = rd(ROOT/f'plans/{work}_points.json')['audio']
        self.faces = {k: skia.Typeface.MakeFromFile(str(FP.FONTS/f'{v}.ttf')) for k, v in [('bead', 'Sans400'), ('line', 'Serif700'), ('rail', 'Sans400'), ('railb', 'Serif700')]}
        self.fonts = {}; self.notes = self.music['notes']; self.ns = np.array([n['s'] for n in self.notes])
        ns = [FP.Note(n['s'], n['e'], max(.025, n['e']-n['s']), n['p'], 80, n['h'], n['h'], n['h'], note_id=f'n{i}') for i, n in enumerate(self.notes)]
        self.song = FP.Song(ns, [(0, 0), (1, 1)], self.dur, note_by_id={n.note_id: n for n in ns})
        self.note_ends = np.array([n.end for n in ns]); self.chord_recede = {}
        self.assign = FP.heuristic_assignments_for_song(self.song)
        self.cfg = {'line_source': 'heuristic', 'scope': {'seconds_half_span': 3.0}, 'lines': {'width': 1.6, 'alpha': 1., 'rest_gap': .8}, 'notes': {'fill_alpha': .35, 'outline_width': 2.}, 'readability': {'enabled': True, 'radius': {'mode': 'original_cap', 'max': .15}}}
        self.mapping = FP.Mapping(self.song, self.cfg)
        self.windows = []  # (开始, 结束, 颜色序号, 句子)
        self.pages = {}; self.starts = []
        for s in self.sc['sections']:
            src = self.src[s['sec']]; pts = {p['id']: p for b in src['beads'] for p in b['points']}; lo, hi = src['window']
            self.starts.append((lo, s['sec']))
            for gi, g in enumerate(s['groups']):
                for b in g.get('beads', []):
                    ps = [pts[x] for x in b.get('from', []) if x in pts]; loc = [p for p in ps if p['local']]
                    b['win'] = None
                    if loc and len(loc)*2 >= len(ps):
                        a = min(w[0] for p in loc for w in p['windows']); z = max(w[1] for p in loc for w in p['windows'])
                        if z-a < .6*(hi-lo): b['win'] = [a, z]; self.windows.append((a, z, gi, b['text']))
            self.pages[s['sec']] = self.layout(s)
        self.windows.sort(); self.wstart = [w[0] for w in self.windows]

    # ---------- 版面 ----------
    def wrap(self, text, kind, size, width):
        f = self.font(kind, size); rows = []; cur = ''; w = 0
        for ch in text:
            cw = f.measureText(ch)
            if w+cw > width and cur and ch not in NOPUNCT_HEAD:
                rows.append(cur); cur = ''; w = 0
            cur += ch; w += cw
        if cur: rows.append(cur)
        return rows

    def layout(self, s):
        gs = s['groups']; n = len(gs); per = n if n <= 3 else (2 if n == 4 else 3)
        grid = [gs[i:i+per] for i in range(0, n, per)]
        for bs, ls in [(36, 40), (34, 38), (32, 36), (30, 34), (28, 32), (26, 30), (24, 28), (22, 26)]:
            colw = (X1-X0-44*(per-1))/per; y = Y0; out = []
            for row in grid:
                blocks = []
                for k, g in enumerate(row):
                    x = X0+k*(colw+44); gi = gs.index(g)
                    be = [(b, self.wrap(b['text'], 'bead', bs, colw-22)) for b in g.get('beads', [])]
                    le = [(l, self.wrap(l['text'], 'line', ls, colw-22)) for l in g.get('lines', [])]
                    bh = sum(len(r)*bs*1.32+12 for _, r in be); lh = sum(len(r)*ls*1.3+10 for _, r in le)
                    blocks.append({'x': x, 'gi': gi, 'be': be, 'le': le, 'bh': bh, 'lh': lh})
                top = max(b['bh'] for b in blocks); low = max(b['lh'] for b in blocks)
                out.append({'y': y, 'blocks': blocks, 'top': top, 'low': low}); y += top+low+34
            if y-34 <= Y1: break
        return {'rows': out, 'bs': bs, 'ls': ls, 'colw': colw, 'fit': y-34 <= Y1}

    def rich(self, c, x, y, rows, it, kind, size, base, keyc, alpha, lead):
        t = it['text']; on = [False]*len(t)
        for k in it.get('keys', []):
            i = t.find(k)
            if i >= 0:
                for j in range(i, i+len(k)): on[j] = True
        pos = 0
        for r in rows:
            xx = x; yy = y+size
            for ch in r:
                self.text(c, ch, xx, yy, kind, size, keyc if on[pos] else base, alpha); xx += self.font(kind, size).measureText(ch); pos += 1
            y += size*lead
        return y

    # ---------- 音乐：局部窗口里的音符用那一组的颜色 ----------
    def color_at(self, time):
        i = bisect.bisect_right(self.wstart, time)-1; best = None
        for w in self.windows[max(0, i-6):i+1]:
            if w[0] <= time < w[1] and (best is None or w[1]-w[0] < best[1]-best[0]): best = w
        return PALETTE[best[2] % len(PALETTE)] if best else NEUTRAL

    def draw_music(self, c, t):
        cur = self.color_at(t); glow = cur != NEUTRAL
        c.drawRect(skia.Rect.MakeXYWH(0, TOP, W, H-TOP), skia.Paint(Color=skia.Color(*(mix(BG, cur, .13) if glow else mix(BAND, BG, .6)), 255)))
        lo = np.searchsorted(self.ns, t-4); hi = np.searchsorted(self.ns, t+4); canvas = BallCanvas(c)
        for n in self.song.notes[lo:hi]:
            nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id)
            if nx is not None and nx.time-n.end < self.cfg['lines']['rest_gap']:
                x0, x1 = self.mapping.x(n.time, t), self.mapping.x(nx.time, t)
                if min(x0, x1) <= 1. and max(x0, x1) >= -1.:
                    canvas.blend_line(x0, self.mapping.y(n.pitch), x1, self.mapping.y(nx.pitch), self.color_at(n.time), 1., 1.6)
        for n in self.song.notes[lo:hi]:
            x = self.mapping.x(n.time, t); r = self.mapping.radius(n.duration)
            if -1.-r <= x <= 1.+r:
                col = self.color_at(n.time)
                canvas.blend_circle_poly(x, self.mapping.y(n.pitch), r, r, col, .62 if col != NEUTRAL else .35, 36, fill=n.time >= t)
        for idx in np.flatnonzero((self.ns < t) & (self.note_ends > t)):
            n = self.song.notes[idx]; nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id, n)
            pr = (t-n.time)/n.duration; y = self.mapping.y(n.pitch)+(self.mapping.y(nx.pitch)-self.mapping.y(n.pitch))*pr
            r = self.mapping.radius(n.duration)*(1-pr); col = self.color_at(n.time)
            bright = mix(col, (255, 255, 255), .15) if col != NEUTRAL else (205, 198, 184)
            _, yy = canvas.xy(0, y); rp = r*(H-TOP)*.5
            for rr, al in [(rp+6, 12), (rp+3, 22)]: c.drawCircle(960, yy, rr, skia.Paint(AntiAlias=True, Color=skia.Color(*bright, al)))
            canvas.blend_circle_poly(0, y, r, r, bright, 1., 36)

    # ---------- 一屏 ----------
    def sec_at(self, t):
        i = max(0, bisect.bisect_right([a for a, _ in self.starts], t)-1); return i, self.starts[i][1]

    def draw_page(self, c, sec, t, fade=1.):
        p = self.pages[sec]; bs, ls = p['bs'], p['ls']
        for row in p['rows']:
            for b in row['blocks']:
                col = PALETTE[b['gi'] % len(PALETTE)]; x = b['x']; y = row['y']
                c.drawRect(skia.Rect.MakeXYWH(x, y+4, 4, row['top']+row['low']-4), skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(190*fade))))
                yy = y
                for it, rows in b['be']:
                    win = it.get('win'); a = fade; base, key = DIM_BEAD, WHITE
                    if win:
                        a *= ease((t-win[0])/.35)
                        if win[0] <= t < win[1]: base, key = mix(DIM_BEAD, col, .65), col
                    self.rich(c, x+18, yy, rows, it, 'bead', bs, base, key, a, 1.32); yy += len(rows)*bs*1.32+12
                yy = y+row['top']+2
                for it, rows in b['le']:
                    self.rich(c, x+18, yy, rows, it, 'line', ls, DIM_LINE, col, fade, 1.3); yy += len(rows)*ls*1.3+10

    def rail(self, c, sec):
        x = RAIL_X; y = 62; cur = next(i for i, p in enumerate(self.sc['phases']) if sec in p['sections'])
        c.drawLine(x, y-12, x, y+46*cur+8, skia.Paint(AntiAlias=True, Color=skia.Color(92, 104, 118, 150), StrokeWidth=1.2))
        for i, p in enumerate(self.sc['phases'][:cur+1]):
            now = i == cur; size = 24 if now else 21
            while self.font('rail', size).measureText(p['label']) > 380 and size > 15: size -= 1
            c.drawRect(skia.Rect.MakeXYWH(x-(5 if now else 3), y-(14 if now else 11), 10 if now else 6, 10 if now else 6), skia.Paint(Color=skia.Color(*(WHITE if now else GREY), 255)))
            self.text(c, p['label'], x+22, y, 'rail', size, WHITE if now else GREY, 1 if now else .85); y += 46

    def frame(self, t):
        t = max(0, min(t, self.dur-.001)); sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255))
        self.draw_music(c, t); i, sec = self.sec_at(t); start = self.starts[i][0]
        k = ease((t-start)/.4) if i > 0 else 1.
        if k < 1: self.draw_page(c, self.starts[i-1][1], t, 1-k)
        self.draw_page(c, sec, t, k); self.rail(c, sec)
        return sf.makeImageSnapshot()


def render(work, tag, start, end, out):
    f = Page(work, tag); end = min(end or f.dur, f.dur); d = end-start; out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
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
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, default=.55); a.add_argument('--name', default='方向2')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Page(x.work, x.tag)
        for s in x.sec:
            lo, hi = f.src[s]['window']; p = ROOT/f'out/{x.name}_{x.work}_{s}.png'; f.frame(lo+(hi-lo)*x.at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p, f.pages[s]['bs'], f.pages[s]['fit'])
