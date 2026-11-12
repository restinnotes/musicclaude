"""大众版画面第七版：线分两层。大字是要点（point），下面一行暗一些的小字是可选的补充（detail）。其余和 film_v6 完全一样。
python film_v7.py still --work op60 --tag Largon --sec S05 --at .6 --name 两层
python film_v7.py render --work op60 --tag Largon --out x.mp4
"""
import sys
import film_v6
from film_v6 import Film6, X0, LW, PLATE, PAD, WHITE, BG, mix, rrect, skia
from pathlib import Path
SMALL = .64


class Film7(Film6):
    def arrange(self, s):
        """线合并后组号会变：交界词只在两组都还在时才放接缝。"""
        n = len(s['groups']); keep = {k: v for k, v in self.links.items() if k[0] != s['sec'] or v < n}
        old, self.links = self.links, keep
        try: perm, border, moved = super().arrange(s)
        finally: self.links = old
        bad = [k for k in border if k+1 >= n]
        for k in bad:
            moved -= {id(b) for b in border.pop(k)}
        return perm, border, moved

    def band(self, g, ws, ls, base):
        rows = self.rows_of(g.get('beads', []), ws, film_v6.RW-10); lines = []; ss = ls*SMALL
        for l in g.get('lines', []):
            for n, r in enumerate(self.sense_wrap(l['text'], ls, LW-34)): lines.append((r, False, n == 0, ls))
            if l.get('detail'):
                for n, r in enumerate(self.sense_wrap(l['detail'], ss, LW-34)): lines.append((r, False, False, ss))
        lh = sum(z*1.3 for *_, z in lines)+ls*.34*max(0, len(g.get('lines', []))-1)
        h = max(len(rows)*ws*1.42, lh)+2*PAD
        return {'g': g, 'rows': rows, 'lines': lines, 'ws': ws, 'ls': ls, 'base': base, 'h': h, 'lh': lh}

    def draw_band(self, c, b, y, t, fade, s0, skip_last=False, ext_top=0, ext_bot=0):
        gc = self.group_color(b['g']); major = b['base'] > .95; top = y-ext_top; h = b['h']+ext_top+ext_bot
        c.drawRRect(rrect(X0, top, PLATE, h), skia.Paint(AntiAlias=True, Color=skia.Color(*mix(BG, gc, .46 if major else .28), int(255*fade))))
        yy = y+(b['h']-b['lh'])/2; first = True
        for r, _, head, size in b['lines']:
            if head and not first: yy += b['ls']*.34
            first = False; small = size < b['ls']
            col = mix(BG, WHITE, .72) if small else (WHITE if major else mix(BG, WHITE, .92))
            self.text(c, r, X0+14, yy+size, 'line', size, col, fade); yy += size*1.3
        rh = len(b['rows'])*b['ws']*1.42; ry = y+(b['h']-rh)/2
        for row in b['rows']:
            for w, dx in row: self.word(c, w, film_v6.RX+dx, ry, b['ws'], t, fade, s0, gc)
            ry += b['ws']*1.42
        return None


film_v6.Film6 = Film7

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    import argparse
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, nargs='*', default=[.6]); a.add_argument('--name', default='两层')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': film_v6.render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Film7(x.work, x.tag)
        for s in x.sec or []:
            lo, hi = f.src[s]['window']
            for at in x.at:
                p = film_v6.ROOT/f'out/{x.name}_{x.work}_{s}_{at}.png'; f.frame(lo+(hi-lo)*at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
