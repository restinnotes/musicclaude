"""大众版画面。版式参照 Op.52：上字下图，右侧一根细轴。

规则：
- 文字逐条出现，最新的珠子固定在同一位置，旧的往上退、变暗；线固定在珠子下方。
- 先珠子后线，全曲第一拍例外。
- 局部珠子：到那几小节才出现，句子和音符一起变色。
- 右栏：每个阶段一个短语；当前阶段列出线里高亮过的短语；没走到的不显示。

python film_pub.py still  --work op60 --tag a --t 150
python film_pub.py render --work op60 --tag a [--start 100 --end 180] [--order bead_first|line_first] [--out x.mp4]
python film_pub.py sheet  --work op60 --tag a          每段一张静帧
"""
import argparse, bisect, json, math, re, subprocess, sys
from pathlib import Path
import numpy as np
import skia

ROOT = Path(__file__).resolve().parent
FONTS = Path('D:/musicclaude/_video_design_20261103/work/fonts')
sys.path.insert(0, 'D:/music-experience-pipeline/src')
from mamviz.midi import Note, Song
from mamviz.geometry import Mapping
from mamviz.visual_lines import heuristic_assignments_for_song

W, H, FPS = 1920, 1080, 30
TOP = 710
BG = (14, 18, 24)
WHITE = (236, 238, 240)
GREY = (132, 142, 152)
AMBER = (226, 176, 92)
TEAL = (112, 214, 196)
BAND = (27, 21, 14)
BAND_LOCAL = (11, 31, 30)
READ_CPS = 5.0
FADE = .4
ROW = 74
BEAD_Y = 512     # 最新一句珠子的基线
LINE_Y = 634     # 线的基线
TEXT_X = 96
TEXT_W = 1320
RAIL_X = 1500
AGE_ALPHA = [1, .6, .36, .2, 0]
LOCAL_CAP = 10.0


def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ease(x):
    x = max(0., min(1., x)); return x*x*(3-2*x)
def mix(a, b, k): return tuple(int(x+(y-x)*k) for x, y in zip(a, b))
def chars(s): return len(re.sub(r'[\s，。、！？；：“”‘’（）…—,.!?;:"\']', '', s))
def read_time(it): return max(2.6, chars(it['text'])/READ_CPS+.8)


def schedule(work, tag, order='bead_first', path=None):
    """由音乐时间排出每句的出现时刻。局部句钉在小节上，其余均匀放在它们之间。"""
    pts = rd(ROOT/f'plans/{work}_points.json')
    sc = rd(path or ROOT/f'runs/script_{work}_{tag}.json')
    by = {s['sec']: s for s in pts['sections']}
    phase_of = {x: i for i, p in enumerate(sc['phases']) for x in p['sections']}
    items, qa = [], []
    prev_end = 0.
    for si, sec in enumerate(sc['sections']):
        s = by[sec['sec']]; lo, hi = s['window']; ids = {p['id']: p for p in s['points']}
        seq = []
        for bi, bt in enumerate(sec['beats']):
            beads = []
            for b in bt['beads']:
                loc = [ids[x] for x in b.get('from', []) if x in ids and ids[x]['local']]
                it = {'kind': 'bead', 'text': b['text'], 'sec': sec['sec'], 'anchor': None, 'local_end': None}
                if loc:
                    # 句子的来源里有局部要点就钉在最早的那一处
                    win = min((w for p in loc for w in p['windows']), key=lambda w: w[0])
                    it['anchor'] = win[0]; it['local_end'] = win[1]
                beads.append(it)
            line = None
            if bt.get('line'):
                line = {'kind': 'line', 'text': bt['line']['text'], 'key': bt['line'].get('key', ''), 'sec': sec['sec'], 'anchor': None, 'phase': phase_of[sec['sec']]}
            first = si == 0 and bi == 0
            seq += ([line] if line and (first or order == 'line_first') else [])+beads+([line] if line and not (first or order == 'line_first') else [])
        rt = [read_time(x) for x in seq]
        # 目标时刻：钉住的句子不动，其余在相邻钉点之间均匀分布
        target = [None]*len(seq); fixed = [i for i, x in enumerate(seq) if x['anchor'] is not None]
        # 时间窗重叠时，后一句顺延到前一句之后，仍在自己的窗内；彻底颠倒的不钉
        kept, last_a = [], -1.
        for i in fixed:
            a = seq[i]['anchor']
            if a < last_a and seq[i]['local_end'] > last_a+1:
                seq[i]['anchor'] = a = last_a+.5
            if a >= last_a: kept.append(i); last_a = a
        fixed = kept
        marks = [(-1, lo+.2-0.)]+[(i, max(lo+.1, seq[i]['anchor']-.15)) for i in fixed]+[(len(seq), hi)]
        for (a, ta), (b, tb) in zip(marks, marks[1:]):
            if a >= 0: target[a] = ta
            free = b-a-1
            if free > 0:
                start = ta if a < 0 else ta+rt[a]*.8
                step = max(0., tb-start)/(free+(0 if b == len(seq) else 0))
                for k in range(free): target[a+1+k] = start+step*k
        t = list(target)
        for i in range(len(seq)):
            floor = prev_end if i == 0 else t[i-1]+rt[i-1]*.72
            t[i] = max(t[i], floor)
        # 溢出就往回压
        if seq and t[-1]+rt[-1]*.72 > hi+1.5:
            t[-1] = hi+1.5-rt[-1]*.72
            for i in range(len(seq)-2, -1, -1):
                t[i] = min(t[i], t[i+1]-rt[i]*.72)
        for x, tx, r in zip(seq, t, rt):
            x['t'] = max(0., tx); x['read'] = r
            if x['anchor'] is not None:
                x['drift'] = round(x['t']-x['anchor'], 2)
                # 落在原文说的小节范围内就不算偏；范围外的量才是真偏差
                x['outside'] = round(max(0., x['anchor']-x['t']-.5, x['t']-(x['local_end']-1)), 2)
        gaps = [b-a for a, b in zip(t, t[1:])]
        n = sum(chars(x['text']) for x in seq)
        qa.append({'sec': sec['sec'], 'seconds': round(hi-lo, 1), 'items': len(seq), 'chars': n, 'cps': round(n/(hi-lo), 2),
                   'min_gap': round(min(gaps), 2) if gaps else None, 'locals': sum(x['anchor'] is not None for x in seq),
                   'max_drift': max((abs(x.get('drift', 0)) for x in seq), default=0), 'max_outside': max((x.get('outside', 0) for x in seq), default=0)})
        prev_end = t[-1]+rt[-1]*.72 if seq else prev_end
        items += seq
    return sc, items, qa


class BallCanvas:
    def __init__(self, c): self.c = c
    def xy(self, x, y): return 960+x*960, TOP+(H-TOP)*(1-y)*.5
    def blend_line(self, x0, y0, x1, y1, color, alpha, width):
        x0, y0 = self.xy(x0, y0); x1, y1 = self.xy(x1, y1)
        p = skia.Paint(AntiAlias=True, Color=skia.Color(*[int(v) for v in color], max(0, min(255, int(105*alpha)))), StrokeWidth=width)
        self.c.drawLine(x0, y0, x1, y1, p)
    def blend_circle_poly(self, x, y, rx, ry, color, alpha, segs, fill=True, outline_width=2):
        x, y = self.xy(x, y); r = max(.05, rx*(H-TOP)*.5)
        p = skia.Paint(AntiAlias=True, Color=skia.Color(*[int(v) for v in color], max(0, min(255, int(alpha*255)))))
        if not fill:
            p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(max(1, outline_width*.7)); p.setAlphaf(alpha*.45)
        self.c.drawCircle(x, y, r, p)


class Palette:
    tint = AMBER
    def rgb(self, n): return self.tint
    def color(self, n, state):
        r, g, b = self.tint; return r << 16 | g << 8 | b


class Film:
    def __init__(self, work, tag, order='bead_first', path=None, music_path=None):
        self.work = work
        self.sc, self.items, self.qa = schedule(work, tag, order, path)
        self.pts = rd(ROOT/f'plans/{work}_points.json')
        self.src_audio = self.pts['audio']
        self.music_path = Path(music_path or ROOT/f'input/{work}_music.json')
        self.music = rd(self.music_path); self.dur = self.music['dur']
        self.beads = [x for x in self.items if x['kind'] == 'bead']; self.bstart = [x['t'] for x in self.beads]
        self.lines = [x for x in self.items if x['kind'] == 'line']; self.lstart = [x['t'] for x in self.lines]
        self.phases = self.sc['phases']
        self.faces = {k: skia.Typeface.MakeFromFile(str(FONTS/f'{v}.ttf')) for k, v in [('bead', 'Sans400'), ('line', 'Serif700'), ('rail', 'Sans400'), ('railb', 'Serif700')]}
        self.fonts = {}
        self.notes = self.music['notes']; self.ns = np.array([n['s'] for n in self.notes])
        ns = [Note(n['s'], n['e'], max(.025, n['e']-n['s']), n['p'], 80, n['h'], n['h'], n['h'], note_id=f'n{i}') for i, n in enumerate(self.notes)]
        self.song = Song(ns, [(0, 0), (1, 1)], self.dur, note_by_id={n.note_id: n for n in ns})
        self.assign = heuristic_assignments_for_song(self.song)
        self.cfg = {'line_source': 'heuristic', 'scope': {'seconds_half_span': 3.0}, 'lines': {'width': 1.6, 'alpha': 1., 'rest_gap': .8}, 'notes': {'fill_alpha': .35, 'outline_width': 2.}, 'readability': {'enabled': True, 'radius': {'mode': 'original_cap', 'max': .15}}}
        self.mapping = Mapping(self.song, self.cfg); self.palette = Palette()
        # A sustained chord recedes when the next gesture starts. This affects
        # only its displayed core, never its onset, release, or score identity.
        self.chord_recede = {}
        i = 0
        while i < len(ns):
            j = i+1
            while j < len(ns) and ns[j].time-ns[i].time <= .03: j += 1
            chord = ns[i:j]
            if len({n.pitch for n in chord}) >= 3 and j < len(ns):
                for n in chord:
                    if n.duration >= 1.:
                        self.chord_recede[n.note_id] = max(ns[j].time, n.time+.22)
            i = j
        self.note_ends = np.array([n.end for n in ns])

    def core_style(self, n, t, radius):
        recede = self.chord_recede.get(n.note_id)
        k = ease((t-recede)/.22) if recede is not None else 0.
        # Four-pixel residuals remain visible beneath a crisp new arpeggio.
        cap = 4./((H-TOP)*.5)
        return radius+(min(radius, cap)-radius)*k, 1.-.80*k

    def font(self, kind, size):
        k = (kind, size)
        if k not in self.fonts:
            f = skia.Font(self.faces[kind], size); f.setSubpixel(True); self.fonts[k] = f
        return self.fonts[k]

    def text(self, c, s, x, y, kind, size, rgb, alpha):
        if alpha <= .003: return x
        f = self.font(kind, size)
        c.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255*min(1, alpha)))))
        return x+f.measureText(s)

    def fit(self, s, kind, size, width):
        while self.font(kind, size).measureText(s) > width and size > 26: size -= 1
        return size

    # ---------- 局部 ----------
    def local_now(self, t):
        best, level = None, 0.
        for b in self.beads[max(0, bisect.bisect_right(self.bstart, t)-6):bisect.bisect_right(self.bstart, t)]:
            if b['anchor'] is None: continue
            # 只有句子确实落在它说的那几小节里才一起变色
            if b['t'] >= b['local_end']-1: continue
            end = min(b['local_end'], b['t']+LOCAL_CAP); start = b['t']
            if start <= t < end:
                k = min(ease((t-start)/FADE), ease((end-t)/FADE))
                if k >= level: best, level = b, k
        return best, level

    # ---------- 主文字 ----------
    def draw_beads(self, c, t, local, level):
        n = bisect.bisect_right(self.bstart, t)
        shown = self.beads[max(0, n-5):n]
        lidx = bisect.bisect_right(self.lstart, t)-1
        for i, b in enumerate(shown):
            newer = shown[i+1:]
            pos = sum(ease((t-x['t'])/.45) for x in newer)
            if pos >= 4: continue
            a0 = int(pos); a = AGE_ALPHA[a0]+(AGE_ALPHA[min(a0+1, 4)]-AGE_ALPHA[a0])*(pos-a0)
            a *= ease((t-b['t'])/FADE)
            # 线落下后，它之前的珠子退一步，让眼睛落到线上
            if lidx >= 0 and self.lines[lidx]['t'] > b['t']:
                a *= 1-.28*ease((t-self.lines[lidx]['t'])/FADE)
            rise = (1-ease((t-b['t'])/FADE))*14
            rgb = mix(WHITE, TEAL, level) if b is local else WHITE
            size = self.fit(b['text'], 'bead', 42, TEXT_W)
            self.text(c, b['text'], TEXT_X, BEAD_Y-pos*ROW+rise, 'bead', size, rgb, a)

    def draw_line(self, c, t):
        i = bisect.bisect_right(self.lstart, t)-1
        for j in ([i-1, i] if i >= 1 else [i] if i == 0 else []):
            l = self.lines[j]
            if j == i-1:
                out = ease((t-self.lines[i]['t'])/FADE)
                if out >= 1: continue
                a, dy = 1-out, -out*16
            else:
                k = ease((t-l['t'])/FADE); a, dy = k, (1-k)*14
                # 新一拍的珠子出现后，这条线变暗一些，等新线落下
                nb = bisect.bisect_right(self.bstart, l['t'])
                if nb < len(self.beads) and self.beads[nb]['t'] <= t:
                    a *= 1-.42*ease((t-self.beads[nb]['t'])/FADE)
            self.draw_line_text(c, l, a, dy)

    def draw_line_text(self, c, l, a, dy):
        size = self.fit(l['text'], 'line', 48, TEXT_W-24)
        y = LINE_Y+dy
        rect = skia.Rect.MakeXYWH(TEXT_X-22, y-size+2, 5, size+10)
        c.drawRect(rect, skia.Paint(AntiAlias=True, Color=skia.Color(*AMBER, int(230*a))))
        s, key = l['text'], l.get('key') or ''
        at = s.find(key) if key else -1
        x = TEXT_X
        if at < 0: self.text(c, s, x, y, 'line', size, WHITE, a); return
        x = self.text(c, s[:at], x, y, 'line', size, WHITE, a)
        x = self.text(c, key, x, y, 'line', size, AMBER, a)
        self.text(c, s[at+len(key):], x, y, 'line', size, WHITE, a)

    # ---------- 右栏 ----------
    def draw_rail(self, c, t):
        landed = [l for l in self.lines if l['t'] <= t]
        if not landed: return
        cur = landed[-1]['phase']; x = RAIL_X; y = 70
        rows = []
        for i, p in enumerate(self.phases):
            if i < cur: rows.append(('past', p['label'], None))
            elif i == cur:
                rows.append(('phase', p['label'], None))
                keys = [l for l in landed if l['phase'] == cur and l.get('key')]
                folded = len(keys)-3
                if folded > 0: rows.append(('fold', '', folded))
                for l in keys[-3:]: rows.append(('key', l['key'], l))
        top = y-12; bottom = y
        pos = []
        for kind, text, extra in rows:
            step = {'past': 44, 'phase': 46, 'fold': 30, 'key': 46}[kind]
            pos.append(bottom); bottom += step
        spine = skia.Paint(AntiAlias=True, Color=skia.Color(92, 104, 118, 150), StrokeWidth=1.2)
        c.drawLine(x, top, x, bottom-30, spine)
        for (kind, text, extra), yy in zip(rows, pos):
            if kind == 'past':
                c.drawRect(skia.Rect.MakeXYWH(x-3, yy-11, 6, 6), skia.Paint(Color=skia.Color(*mix(AMBER, BG, .55), 255)))
                self.text(c, text, x+24, yy, 'rail', 23, GREY, .85)
            elif kind == 'phase':
                c.drawRect(skia.Rect.MakeXYWH(x-4, yy-13, 8, 8), skia.Paint(Color=skia.Color(*AMBER, 255)))
                self.text(c, text, x+24, yy, 'rail', 25, WHITE, .95)
            elif kind == 'fold':
                for k in range(min(extra, 3)):
                    c.drawCircle(x, yy-16+k*7, 1.8, skia.Paint(AntiAlias=True, Color=skia.Color(*GREY, 220)))
            else:
                latest = extra is landed[-1]
                k = ease((t-extra['t'])/FADE) if latest else 1
                if latest:
                    c.drawRect(skia.Rect.MakeXYWH(x-6, yy-16, 12, 12), skia.Paint(Color=skia.Color(*AMBER, int(255*k))))
                    self.text(c, text, x+24, yy, 'railb', 27, AMBER, k)
                else:
                    c.drawCircle(x, yy-10, 2.2, skia.Paint(AntiAlias=True, Color=skia.Color(*GREY, 220)))
                    self.text(c, text, x+24, yy, 'rail', 23, mix(WHITE, GREY, .4), .9)

    # ---------- 音乐 ----------
    def draw_music(self, c, t, level):
        tint = mix(AMBER, TEAL, level); self.palette.tint = tint
        c.drawRect(skia.Rect.MakeXYWH(0, TOP, W, H-TOP), skia.Paint(Color=skia.Color(*mix(BAND, BAND_LOCAL, level), 255)))
        lo = np.searchsorted(self.ns, t-4); hi = np.searchsorted(self.ns, t+4)
        canvas = BallCanvas(c)
        for n in self.song.notes[lo:hi]:
            a = self.assign[n.note_id]
            nx = self.song.note_by_id.get(a.successor_note_id)
            if nx is not None and nx.time-n.end < self.cfg['lines']['rest_gap']:
                x0, x1 = self.mapping.x(n.time, t), self.mapping.x(nx.time, t)
                if min(x0, x1) <= 1. and max(x0, x1) >= -1.:
                    canvas.blend_line(x0, self.mapping.y(n.pitch), x1, self.mapping.y(nx.pitch), tint, 1., 1.6)
        for n in self.song.notes[lo:hi]:
            x = self.mapping.x(n.time, t); r = self.mapping.radius(n.duration)
            if -1.-r <= x <= 1.+r:
                canvas.blend_circle_poly(x, self.mapping.y(n.pitch), r, r, tint, .35, 36, fill=n.time >= t)
        active = np.flatnonzero((self.ns < t) & (self.note_ends > t))
        cores = []
        for idx in active:
            n = self.song.notes[idx]
            nx = self.song.note_by_id.get(self.assign[n.note_id].successor_note_id, n)
            pr = (t-n.time)/n.duration
            y = self.mapping.y(n.pitch)+(self.mapping.y(nx.pitch)-self.mapping.y(n.pitch))*pr
            r, alpha = self.core_style(n, t, self.mapping.radius(n.duration)*(1-pr))
            cores.append((alpha, y, r))
        # Old chord residuals go behind the current notes, including their glow.
        for alpha, y, r in sorted(cores, key=lambda row: row[0]):
            _, yy = canvas.xy(0, y); rp = r*(H-TOP)*.5
            for rr, al in [(rp+6, 12), (rp+3, 22)]:
                c.drawCircle(960, yy, rr, skia.Paint(AntiAlias=True, Color=skia.Color(*tint, int(al*alpha))))
            canvas.blend_circle_poly(0, y, r, r, tint, alpha, 36)

    def frame(self, t):
        t = max(0, min(t, self.dur-.001))
        sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255))
        local, level = self.local_now(t)
        self.draw_music(c, t, level)
        self.draw_beads(c, t, local, level)
        self.draw_line(c, t)
        self.draw_rail(c, t)
        return sf.makeImageSnapshot()


def save_qa(f, name):
    glyph_missing = []
    for x in f.items:
        for kind, s in [('bead' if x['kind'] == 'bead' else 'line', x['text'])]:
            for ch, g in zip(s, f.font(kind, 40).textToGlyphs(s)):
                if g == 0: glyph_missing.append(ch)
    out = {'music_path': str(f.music_path.resolve()), 'alignment': f.music.get('alignment'), 'sections': f.qa, 'glyph_missing': sorted(set(glyph_missing)), 'items': len(f.items), 'chars': sum(chars(x['text']) for x in f.items), 'dur': f.dur,
           'cps': round(sum(chars(x['text']) for x in f.items)/f.dur, 2), 'locals': sum(x['anchor'] is not None for x in f.items),
           'max_drift': max((abs(x.get('drift', 0)) for x in f.items), default=0), 'outside': [{'sec': x['sec'], 'text': x['text'], 'by': x['outside']} for x in f.items if x.get('outside', 0) > 0]}
    (ROOT/'qa').mkdir(exist_ok=True)
    Path(ROOT/f'qa/{name}.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out


def render(work, tag, start=0, end=None, out=None, order='bead_first', path=None, music_path=None):
    f = Film(work, tag, order, path, music_path); end = min(end or f.dur, f.dur); d = end-start
    out = Path(out or ROOT/f'out/{work}_大众版_{tag}.mp4'); out.parent.mkdir(parents=True, exist_ok=True)
    whole = start == 0 and abs(end-f.dur) < .01
    audio = (['-ss', str(start)] if start else [])+['-i', f.src_audio]
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', *audio, '-t', str(d), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', *(['-c:a', 'copy'] if whole else ['-c:a', 'aac', '-b:a', '256k']), '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(round(d*FPS)):
            p.stdin.write(f.frame(start+i/FPS).tobytes())
    finally: p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed')
    qa_name = f'{work}_{tag}_{order}_film'+('_aligned' if music_path else '')
    print(json.dumps(save_qa(f, qa_name), ensure_ascii=False)[-300:], flush=True); print(out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', required=True); a.add_argument('--tag', default='a'); a.add_argument('--t', type=float, nargs='*')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out'); a.add_argument('--order', default='bead_first'); a.add_argument('--path'); a.add_argument('--music', help='Explicit music JSON for alignment comparisons')
    x = a.parse_args()
    if x.cmd == 'still':
        f = Film(x.work, x.tag, x.order, x.path, x.music)
        for tt in x.t: f.frame(tt).save(str(ROOT/f'previews/{x.work}_{x.tag}_{tt:.0f}.png'), skia.EncodedImageFormat.kPNG, 100); print(tt)
    elif x.cmd == 'sheet':
        f = Film(x.work, x.tag, x.order, x.path, x.music); d = ROOT/f'previews/{x.work}_{x.tag}'; d.mkdir(exist_ok=True, parents=True)
        for s in f.pts['sections']:
            f.frame(s['window'][0]+(s['window'][1]-s['window'][0])*.8).save(str(d/f"{s['sec']}.png"), skia.EncodedImageFormat.kPNG, 100)
        print(json.dumps(save_qa(f, f'{x.work}_{x.tag}_sheet'), ensure_ascii=False)[-400:])
    else: render(x.work, x.tag, x.start, x.end, x.out, x.order, x.path, x.music)
