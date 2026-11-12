"""大众版画面第八版：屏幕稿（pub24）上下交替排。线一行：关键词更大更亮，其余字正常；感受一行：字小、散开。
局部小节的感受到那几小节才出现，出现后留在原处；不是局部的感受整段都在。音乐画法同 film_v6（只有明确指向的词才给音上色，这里没有标）。
python film_v8.py still --work op60 --tag g6 --sec S02 S05 --at .2 .6
python film_v8.py render --work op60 --tag g6 --start a --end b --out x.mp4
"""
import argparse, bisect, sys
import skia
import film_v6
from film_v6 import Film6, X0, X1, Y0, Y1, WHITE, BG, mix, ease, W, H
from film_pub import TOP
from film_v3 import NOHEAD, ROOT, R3, rd, EMOTIONS

LINE_C = (236, 232, 224); KEY_C = (255, 214, 150); FEEL_C = (170, 186, 200)
LADDER = [(46, 1.32, 30), (42, 1.3, 28), (38, 1.3, 26), (35, 1.28, 24), (32, 1.26, 22), (29, 1.25, 21), (26, 1.24, 20)]
WIDTH = X1-X0-34


class Film8(Film6):
    def __init__(self, work, tag):
        self.screen = {s['sec']: s for s in rd(R3/f's24/screen_{work}_{tag}.json')['sections']}
        src = {s['sec']: s for s in rd(ROOT/f'r2/{work}_src.json')['sections']}
        self.local = {b['id']: b['points'][0]['windows'][0] for s in src.values() for b in s['beads'] if b['points'] and any(p['local'] for p in b['points'])}
        super().__init__(work, tag)

    # ---------- 版面 ----------
    def line_rows(self, row, size, kscale):
        """逐字排：关键词的字用大号。返回若干行，每行是 [(字, x, 字号, 是否关键词)]。"""
        text = row['text']; flag = [False]*len(text)
        for k in row.get('keys') or []:
            i = text.find(k)
            if i >= 0:
                for j in range(i, i+len(k)): flag[j] = True
        rows = [[]]; x = 0.
        for ch, f in zip(text, flag):
            sz = round(size*kscale) if f else size; cw = self.font('line', sz).measureText(ch)
            if x+cw > WIDTH and rows[-1] and ch not in NOHEAD: rows.append([]); x = 0.
            rows[-1].append((ch, x, sz, f)); x += cw
        return rows

    def feel_rows(self, row, size):
        """碎片按珠子成簇：同一颗珠子的碎片挨得近，不同珠子之间空得多；结尾句号去掉。"""
        f = self.font('bead', size); near = size*.75; far = size*1.9; rows = [[]]; x = 0.; last = None
        for it in row.get('items', []):
            text = it['text'].rstrip('。')
            for piece in self.wrap(text, 'bead', size, WIDTH):
                w = f.measureText(piece); gap = 0. if not x else (near if it.get('bead') == last else far)
                if x and x+gap+w > WIDTH: rows.append([]); x = 0.; gap = 0.
                x += gap; rows[-1].append((it, piece, x)); x += w
            last = it.get('bead')
        return rows

    def layout(self, s):
        sc = getattr(self, 'screen', None)
        if not sc: return {'items': [], 'h': 0}
        rows = sc[s['sec']]['rows']
        for size, ks, fs in LADDER:
            items = []; h = 0.
            first = next((r.get('emotion') for r in rows if r['kind'] == 'line'), None); emo = first
            for n, r in enumerate(rows):
                if r['kind'] == 'line':
                    emo = r.get('emotion') or emo
                    lr = self.line_rows(r, size, ks); rh = [max(z for *_, z, _ in l) for l in lr]
                    items.append({'kind': 'line', 'rows': lr, 'rh': rh, 'col': EMOTIONS.get(emo, (186, 192, 204)), 'at': r.get('at')}); h += sum(x*1.32 for x in rh)   # 11-09 依次出现（reveal.py）加了 at
                else:
                    fr = self.feel_rows(r, fs); items.append({'kind': 'feel', 'rows': fr, 'size': fs, 'col': EMOTIONS.get(emo, (186, 192, 204))}); h += len(fr)*fs*1.5
                h += size*.55 if n else 0
            if h <= Y1-Y0-10: break
        return {'items': items, 'h': h, 'gap': size*.55}

    # ---------- 画 ----------
    def win_of(self, it):
        b = it.get('bars')
        if b and b[0] in self.bar_t and b[1] in self.bar_end: return [self.bar_t[b[0]], self.bar_end[b[1]]]
        return self.local.get(it.get('bead'))

    def draw_page(self, c, sec, t, fade, s0, skip_prev=False, skip_last=False):
        p = self.pages[sec]; y = Y0+max(0., (Y1-Y0-p['h'])*.25)
        for n, item in enumerate(p['items']):
            if n: y += p['gap']
            col = item['col']
            if item['kind'] == 'line':
                y0 = y; lf = fade
                if item.get('at') is not None:   # 11-09 依次出现：到 at 才淡入（0.6 秒）
                    lf = 0. if t < s0+item['at'] else fade*ease((t-s0-item['at'])/.6)
                for l, rh in zip(item['rows'], item['rh']):
                    base = y+rh
                    for ch, x, sz, key in l: self.text(c, ch, X0+22+x, base, 'line', sz, mix(col, WHITE, .25) if key else LINE_C, lf)
                    y += rh*1.32
                c.drawRoundRect(skia.Rect.MakeXYWH(X0, y0+6, 6, y-y0-6), 3, 3, skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(230*lf))))
            else:
                fs = item['size']
                for row in item['rows']:
                    for it, piece, x in row:
                        base_c = mix(FEEL_C, col, .45); a = fade; fc = base_c; w = self.win_of(it)
                        if not w and it.get('at') is not None: w = [s0+it['at'], s0+it['at']+4]   # 11-09 依次出现：到 at 淡入，加亮 4 秒后恢复常色
                        if w:
                            ta, tz = w
                            if t < ta: a = 0.
                            else:
                                up = ease((t-ta)/.6); live = ta <= t < tz
                                a = fade*up; fc = mix(base_c, WHITE, .5) if live else base_c
                        self.text(c, piece, X0+22+x, y+fs*1.05, 'bead', fs, fc, a)
                    y += fs*1.5
        return None

    def draw_notes(self, c, sec, t):
        """11-09 用户：“这种 原先那个小节的 然后这种左手的 我觉得应该都是能够去对应到可视化的旁边的吧 可以给可视化的旁边划一块区域啊”。
        旁注在音符动画上方一条、播放点右侧：到对应小节淡入，至少留 5 秒，那几小节结束后淡出；同时有几条就往下叠。"""
        notes = (self.screen.get(sec) or {}).get('notes') or []
        y = TOP+40; fs = 26
        for nt in notes:
            b = [int(x) for x in str(nt.get('bars', '')).replace('–', '-').split('-') if x.strip().isdigit()]
            if not b or b[0] not in self.bar_t or b[-1] not in self.bar_end: continue
            ta = self.bar_t[b[0]]; tz = max(self.bar_end[b[-1]], ta+5.)
            if not (ta <= t < tz+.6): continue
            a = ease((t-ta)/.5) * (1. if t < tz else max(0., 1-(t-tz)/.6))
            c.drawRoundRect(skia.Rect.MakeXYWH(992, y-fs*1.05, 6, fs*1.35), 3, 3, skia.Paint(AntiAlias=True, Color=skia.Color(*KEY_C, int(200*a))))
            self.text(c, nt['text'], 1010, y, 'bead', fs, mix(FEEL_C, WHITE, .35), a)
            y += fs*1.7

    def frame(self, t):
        t = max(0, min(t, self.dur-.001)); sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255)); self.now = t
        i = max(0, bisect.bisect_right(self.secstart, t)-1); sec, s0 = self.starts[i][1], self.starts[i][0]
        k = ease((t-s0)/.7) if i > 0 else 1.
        self.draw_music(c, t, (120, 124, 134))
        self.draw_notes(c, sec, t)   # 11-09 旁注：可视化旁的细致感受（notes.py）
        if k < 1: self.draw_page(c, self.starts[i-1][1], t, max(0., 1-k*2), self.starts[i-1][0])
        self.draw_page(c, sec, t, 1. if k >= 1 else max(0., k*2-1), s0)
        self.rail(c, sec)
        return sf.makeImageSnapshot()


film_v6.Film6 = Film8

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = argparse.ArgumentParser(); a.add_argument('cmd'); a.add_argument('--work', default='op60'); a.add_argument('--tag'); a.add_argument('--sec', nargs='*'); a.add_argument('--at', type=float, nargs='*', default=[.6]); a.add_argument('--name', default='交替')
    a.add_argument('--start', type=float, default=0); a.add_argument('--end', type=float); a.add_argument('--out')
    x = a.parse_args()
    if x.cmd == 'render': film_v6.render(x.work, x.tag, x.start, x.end, x.out)
    else:
        f = Film8(x.work, x.tag)
        for s in x.sec or []:
            lo, hi = f.src[s]['window']
            for at in x.at:
                p = ROOT/f'out/{x.name}_{x.work}_{x.tag}_{s}_{at}.png'; f.frame(lo+(hi-lo)*at).save(str(p), skia.EncodedImageFormat.kPNG, 100); print(p)
