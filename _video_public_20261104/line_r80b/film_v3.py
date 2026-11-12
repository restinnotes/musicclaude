"""大众版画面第三版：主组大、次组小；颜色代表情绪；音符按模型标的小节和音高染色。
python film_v3.py still --work op60 --tag d1 --sec S04 S05 --at .6
python film_v3.py render --work op60 --tag d1 --start a --end b --out x.mp4
"""
import argparse, bisect, json, subprocess, sys
from pathlib import Path
import numpy as np, skia
import film_pub as FP
from film_pub import Film, W, H, TOP, BG, WHITE, GREY, RAIL_X, FPS, ease, mix, BallCanvas
from pub3 import EMOTIONS
ROOT = Path(__file__).resolve().parent; R2 = ROOT/'r2'; R3 = ROOT/'r3'
def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
NEUTRAL = (128, 124, 116)
X0, X1, Y0, Y1 = 72, 1440, 44, 690
NOHEAD = '，。、！？；：”’）》…'
STAGE_CX, STAGE_CY, STAGE_W = 750, 350, 1240


class Page(Film):
    def __init__(self, work, tag):
        self.work = work; self.sc = rd(R3/f'script_{work}_{tag}.json'); self.src = {s['sec']: s for s in rd(R2/f'{work}_src.json')['sections']}
        _mp = ROOT/f'input/{work}_music_aligned.json'; self.music = rd(_mp if _mp.exists() else ROOT/f'input/{work}_music.json'); self.dur = self.music['dur']; self.audio = rd(ROOT/f'plans/{work}_points.json')['audio']
        self.faces = {k: skia.Typeface.MakeFromFile(str(FP.FONTS/f'{v}.ttf')) for k, v in [('bead', 'Sans400'), ('line', 'Serif700'), ('rail', 'Sans400'), ('railb', 'Serif700')]}
        self.fonts = {}; self.notes = self.music['notes']; self.ns = np.array([n['s'] for n in self.notes])
        ns = [FP.Note(n['s'], n['e'], max(.025, n['e']-n['s']), n['p'], 80, n['h'], n['h'], n['h'], note_id=f'n{i}') for i, n in enumerate(self.notes)]
        self.song = FP.Song(ns, [(0, 0), (1, 1)], self.dur, note_by_id={n.note_id: n for n in ns})
        self.note_ends = np.array([n.end for n in ns])
        self.assign = FP.heuristic_assignments_for_song(self.song)
        self.cfg = {'line_source': 'heuristic', 'scope': {'seconds_half_span': 3.0}, 'lines': {'width': 1.6, 'alpha': 1., 'rest_gap': .8}, 'notes': {'fill_alpha': .35, 'outline_width': 2.}, 'readability': {'enabled': True, 'radius': {'mode': 'original_cap', 'max': .15}}}
        self.mapping = FP.Mapping(self.song, self.cfg)
        bars = sorted((int(a), b) for a, b in (self.music['bars'].items() if isinstance(self.music['bars'], dict) else self.music['bars'])); self.bar_t = dict(bars)
        self.bar_end = {b: (bars[i+1][1] if i+1 < len(bars) else self.dur) for i, (b, _) in enumerate(bars)}
        mp = R3/f'marks_{work}_{tag}.json'; marks = {(m['sec'], m['text']): m for m in rd(mp)['marks']} if mp.exists() else {}
        self.marks = []; self.pages = {}; self.starts = []; self.mood = {}
        for s in self.sc['sections']:
            src = self.src[s['sec']]; lo, hi = src['window']; self.starts.append((lo, s['sec']))
            main = next(g for g in s['groups'] if g.get('rank') == '主'); self.mood[s['sec']] = EMOTIONS[main['emotion']]
            for g in s['groups']:
                for b in g.get('beads', []):
                    b['color'] = EMOTIONS[b.get('emotion') or g['emotion']]; b['win'] = None; m = marks.get((s['sec'], b['text']))
                    if m and m.get('render') and m.get('bars'):
                        a, z = m['bars'][0], m['bars'][-1]
                        if a in self.bar_t and z in self.bar_end:
                            ta, tz = self.bar_t[a], self.bar_end[z]; p = m.get('pitch') or [0, 127]
                            self.marks.append((ta, tz, p[0], p[1], b['color'], b['text']))
                            if tz-ta < .6*(hi-lo): b['win'] = [ta, tz]
                            else: b['mark_long'] = [ta, tz]
            self.pages[s['sec']] = self.layout(s); self.pages[s['sec']]['focus'] = self.schedule(s, lo, hi)
        self.marks.sort(key=lambda m: m[0]); self.mstart = [m[0] for m in self.marks]; self.secstart = [a for a, _ in self.starts]

    # ---------- 注意力：字一直都在，一次放大一句，放大完缩回原位 ----------
    def stage(self, it, kind):
        for size in (84, 76, 68, 60, 54, 48):
            rows = self.wrap(it['text'], kind, size, STAGE_W)
            if len(rows)*size*1.3 <= 520 and (len(rows) == 1 or len(rows[-1]) > 4): break
        w = max(self.font(kind, size).measureText(r) for r in rows); h = len(rows)*size*1.3
        return {'it': it, 'kind': kind, 'size': size, 'rows': rows, 'x': STAGE_CX-w/2, 'y': STAGE_CY-h/2, 'w': w, 'h': h}

    def hold(self, it):
        return min(4.2, 1.5+len(it['text'])*.07)

    def schedule(self, s, lo, hi):
        main = next(g for g in s['groups'] if g.get('rank') == '主'); order = [main]+[g for g in s['groups'] if g is not main]; local = []; rest = []
        for g in order:
            for b in g.get('beads', []):
                if b.get('win'):
                    a, z = b['win']; base = self.hold(b)
                    local.append({'a': a, 'z': a+max(base, min(z-a, base+2)), **self.stage(b, 'bead')})
                else: rest.append((b, 'bead'))
            for l in g.get('lines', []): rest.append((l, 'line'))
        local.sort(key=lambda f: f['a']); kept = []
        for f in local:
            if kept and f['a'] < kept[-1]['z']+.15:
                if f['a']-kept[-1]['a'] < 1.4: f['a'] = kept[-1]['a']+1.4; f['z'] = max(f['z'], f['a']+1.4)
                kept[-1]['z'] = f['a']-.15
            kept.append(f)
        kept = [f for f in kept if f['a'] < hi-.5]
        for f in kept: f['z'] = min(f['z'], hi-.2)
        free = (hi-lo)-sum(f['z']-f['a'] for f in kept)-1.; need = sum(self.hold(i)+.15 for i, _ in rest)
        gap = max(.15, min(1.5, (free-need)/(len(rest)+1))) if rest else 0; cur = lo+.7; out = []
        for it, kind in rest:
            d = self.hold(it)
            for f in kept:
                if cur < f['z']+.15 and cur+d > f['a']-.15: cur = f['z']+.2
            if cur+d > hi-.3: break
            out.append({'a': cur, 'z': cur+d, **self.stage(it, kind)}); cur += d+gap
        return sorted(kept+out, key=lambda f: f['a'])

    def env(self, f, t):
        return min(ease((t-f['a'])/.32), ease((f['z']-t)/.38))

    def focus_at(self, sec, t):
        for f in self.pages[sec]['focus']:
            if f['a'] <= t < f['z']: return f, self.env(f, t)
        return None, 0.

    def draw_focus(self, c, f, e, fade):
        it = f['it']; hx, hy, hs = it.get('home', (f['x'], f['y'], f['size'])); sc = hs/f['size']+(1-hs/f['size'])*e; x = hx+(f['x']-hx)*e; y = hy+(f['y']-hy)*e
        c.drawRect(skia.Rect.MakeXYWH(0, 0, RAIL_X-24, TOP), skia.Paint(Color=skia.Color(*BG, int(205*e*fade))))
        col = it.get('color') or mix(self.cur_gc, WHITE, .1); c.save(); c.translate(x, y); c.scale(sc, sc)
        self.rich(c, 0, 0, f['rows'], it, f['kind'], f['size'], mix(col, WHITE, .12), mix(col, WHITE, .45), min(1, e*2)*fade, 1.3); c.restore()

    # ---------- 版面：主组在左，次组在右 ----------
    def wrap(self, text, kind, size, width):
        f = self.font(kind, size); rows = []; cur = ''; w = 0
        for ch in text:
            cw = f.measureText(ch)
            if w+cw > width and cur and ch not in NOHEAD: rows.append(cur); cur = ''; w = 0
            cur += ch; w += cw
        if cur: rows.append(cur)
        return rows

    def block(self, g, bs, ls, width):
        be = [(b, self.wrap(b['text'], 'bead', bs, width)) for b in g.get('beads', [])]
        le = [(l, self.wrap(l['text'], 'line', ls, width)) for l in g.get('lines', [])]
        ks = max(20, round(bs*.56)); h = ks*1.5+sum(len(r)*bs*1.26+10 for _, r in be)+(10 if le else 0)+sum(len(r)*ls*1.28+8 for _, r in le)
        return {'g': g, 'be': be, 'le': le, 'bs': bs, 'ls': ls, 'ks': ks, 'h': h}

    def layout(self, s):
        main = next(g for g in s['groups'] if g.get('rank') == '主'); rest = [g for g in s['groups'] if g is not main]
        if not rest:
            for bs, ls in [(58, 50), (52, 46), (46, 42), (40, 36), (34, 32)]:
                b = self.block(main, bs, ls, X1-X0-30)
                if b['h'] <= Y1-Y0: break
            return {'main': b, 'side': [], 'mw': X1-X0}
        mw = 720; sx = X0+mw+44; sw = X1-sx
        for bs, ls in [(60, 48), (54, 46), (50, 44), (46, 40), (42, 36), (38, 33), (34, 30), (30, 27)]:
            mb = self.block(main, bs, ls, mw-30)
            if mb['h'] <= Y1-Y0: break
        for bs, ls in [(40, 34), (36, 32), (32, 30), (30, 28), (28, 26), (26, 24), (24, 22), (22, 20)]:
            side = [self.block(g, bs, ls, sw-30) for g in rest]
            if sum(x['h'] for x in side)+22*(len(side)-1) <= Y1-Y0: break
        return {'main': mb, 'side': side, 'sx': sx, 'mw': mw}

    def rich(self, c, x, y, rows, it, kind, size, base, key, a, lead):
        t = it['text']; on = [False]*len(t)
        for k in it.get('keys', []):
            i = t.find(k)
            if i >= 0:
                for j in range(i, i+len(k)): on[j] = True
        pos = 0
        for r in rows:
            xx = x
            for ch in r:
                self.text(c, ch, xx, y+size, kind, size, key if on[pos] else base, a); xx += self.font(kind, size).measureText(ch); pos += 1
            y += size*lead

    def draw_block(self, c, b, x, y, t, fade, major, fo=None, e=0.):
        g = b['g']; gc = EMOTIONS[g['emotion']]
        c.drawRect(skia.Rect.MakeXYWH(x, y+6, 5 if major else 3, b['h']-10), skia.Paint(AntiAlias=True, Color=skia.Color(*gc, int(220*fade))))
        tx = x+20; yy = y; dim = 1-.6*e
        self.text(c, g.get('kind', ''), tx, yy+b['ks'], 'railb', b['ks'], mix(gc, WHITE, .25), fade); yy += b['ks']*1.5
        for it, rows in b['be']:
            a = fade*dim; col = it['color']; live = False; it['home'] = (tx, yy, b['bs'])
            if fo is it: a = fade*(1-min(1, e*3))
            if it.get('win'):
                a *= 1. if t >= it['win'][0]+.3 else 0.; live = it['win'][0] <= t < it['win'][1]
            elif it.get('mark_long'):
                live = it['mark_long'][0] <= t < it['mark_long'][1]
            base = mix(BG, col, .62 if major else .5); key = col
            if live: base = mix(BG, col, .85); key = mix(col, WHITE, .35)
            self.rich(c, tx, yy, rows, it, 'bead', b['bs'], base, key, a, 1.26); yy += len(rows)*b['bs']*1.26+10
        yy += 10 if b['le'] else 0
        for it, rows in b['le']:
            it['home'] = (tx, yy, b['ls']); it['color'] = mix(gc, WHITE, .5)
            self.rich(c, tx, yy, rows, it, 'line', b['ls'], mix(BG, WHITE, .68), mix(gc, WHITE, .3), fade*(1-min(1, e*3)) if fo is it else fade*dim, 1.28); yy += len(rows)*b['ls']*1.28+8

    def draw_page(self, c, sec, t, fade):
        p = self.pages[sec]; fo, e = self.focus_at(sec, t); it = fo['it'] if fo else None
        self.draw_block(c, p['main'], X0, Y0, t, fade, True, it, e)
        y = Y0
        for b in p['side']:
            self.draw_block(c, b, p['sx'], y, t, fade, False, it, e); y += b['h']+22
        if fo and e > 0: self.draw_focus(c, fo, e, fade)

    # ---------- 音乐 ----------
    def color_of(self, n):
        i = bisect.bisect_right(self.mstart, n.time)-1; best = None
        for m in self.marks[max(0, i-10):i+1]:
            if m[0] <= n.time < m[1] and m[2] <= n.pitch <= m[3] and (best is None or m[1]-m[0] < best[1]-best[0]): best = m
        if not best: return None, False
        return best[4], best[5] == self.ftext

    def draw_music(self, c, t, mood):
        c.drawRect(skia.Rect.MakeXYWH(0, TOP, W, H-TOP), skia.Paint(Color=skia.Color(*mix(BG, mood, getattr(self, 'band', .10)), 255)))
        lo = np.searchsorted(self.ns, t-4); hi = np.searchsorted(self.ns, t+4); canvas = BallCanvas(c); dull = mix(NEUTRAL, mood, .35)
        for n in self.song.notes[lo:hi]:
            nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id)
            if nx is not None and nx.time-n.end < self.cfg['lines']['rest_gap']:
                x0, x1 = self.mapping.x(n.time, t), self.mapping.x(nx.time, t)
                if min(x0, x1) <= 1. and max(x0, x1) >= -1.:
                    col, hot = self.color_of(n); canvas.blend_line(x0, self.mapping.y(n.pitch), x1, self.mapping.y(nx.pitch), col or dull, (2. if hot else 1.2) if col else .8, 2. if col else 1.4)
        for n in self.song.notes[lo:hi]:
            x = self.mapping.x(n.time, t); r = self.mapping.radius(n.duration)
            if -1.-r <= x <= 1.+r:
                col, hot = self.color_of(n); rr = r*(1.35 if hot else 1); canvas.blend_circle_poly(x, self.mapping.y(n.pitch), rr, rr, mix(col, WHITE, .3) if hot else (col or dull), (1. if hot else .72) if col else .25, 36, fill=n.time >= t)
        for idx in np.flatnonzero((self.ns < t) & (self.note_ends > t)):
            n = self.song.notes[idx]; nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id, n)
            pr = (t-n.time)/n.duration; y = self.mapping.y(n.pitch)+(self.mapping.y(nx.pitch)-self.mapping.y(n.pitch))*pr
            r = self.mapping.radius(n.duration)*(1-pr); col, _ = self.color_of(n); bright = mix(col, WHITE, .2) if col else mix(dull, WHITE, .35)
            _, yy = canvas.xy(0, y); rp = r*(H-TOP)*.5
            for rr, al in [(rp+6, 12), (rp+3, 22)]: c.drawCircle(960, yy, rr, skia.Paint(AntiAlias=True, Color=skia.Color(*bright, al)))
            canvas.blend_circle_poly(0, y, r, r, bright, 1., 36)

    def rail(self, c, sec):
        x = RAIL_X; y = 62; cur = next(i for i, p in enumerate(self.sc['phases']) if sec in p['sections'])
        c.drawLine(x, y-12, x, y+46*cur+6, skia.Paint(AntiAlias=True, Color=skia.Color(92, 104, 118, 150), StrokeWidth=1.2))
        for i, p in enumerate(self.sc['phases'][:cur+1]):
            now = i == cur; size = 25 if now else 21; col = EMOTIONS.get(p.get('emotion'), GREY)
            while self.font('rail', size).measureText(p['label']) > 370 and size > 15: size -= 1
            c.drawRect(skia.Rect.MakeXYWH(x-(6 if now else 4), y-(15 if now else 12), 12 if now else 8, 12 if now else 8), skia.Paint(Color=skia.Color(*(col if now else mix(BG, col, .65)), 255)))
            self.text(c, p['label'], x+22, y, 'railb' if now else 'rail', size, mix(col, WHITE, .35) if now else mix(BG, col, .6), 1); y += 46

    def frame(self, t):
        t = max(0, min(t, self.dur-.001)); sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255))
        i = max(0, bisect.bisect_right(self.secstart, t)-1); sec = self.starts[i][1]
        k = ease((t-self.starts[i][0])/.5) if i > 0 else 1.
        mood = self.mood[sec] if k >= 1 else mix(self.mood[self.starts[i-1][1]], self.mood[sec], k)
        fo, e = self.focus_at(sec, t); self.ftext = fo['it']['text'] if fo and e > .3 else None
        self.draw_music(c, t, mood)
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
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, default=.6); a.add_argument('--name', default='方向3')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Page(x.work, x.tag)
        for s in x.sec:
            lo, hi = f.src[s]['window']; p = ROOT/f'out/{x.name}_{x.work}_{s}.png'; f.frame(lo+(hi-lo)*x.at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
