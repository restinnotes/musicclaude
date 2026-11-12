"""11-11 大众版画面第九版（只改画面，屏幕稿不变）。用户 11-11 看 K28b 试看版：
“目前这些动画 比如一句一句出来 主屏的 我看不到原因啊……至于现在可视化旁边的小块区域 则是完全没有做这个动画 然后也没有对某一句话去匹配某些音 也没有颜色区分”；
“还是说因为你三个都是同样颜色导致的 然后这个叠在可视化上面我不是这个意思啊”。11-09 用户：可视化区可以缩短，专门空出一块给跟动画走的内容，颜色要和可视化里的音对应。
改动：
1. 主屏：大字一屏开头一起出现，不再按写手随手给的秒数一条条冒；小字只有对得上具体时刻（珠子的局部时间窗）的才到那一刻出现，其余开头就在。
2. 可视化压矮，上方单独留一条旁注带，不叠在音符上。
3. 旁注每条一个自己的颜色；它说的声音（按字面：左手/低音 → 低声部，旋律/右手/歌声 → 高声部，内声部 → 中间）在它的时间窗里染成同一颜色，其余音保持一种颜色。
   时间窗只用原料里有的：珠子局部要点的时间窗，或比这一屏窄的珠子小节范围；都没有就整屏淡淡显示、不上色（标准：没有依据的不编位置，不确定是哪个声音的不上色）。
python film_v9.py still --work op60 --tag g68K28b --sec S06 --at .1 .5
python film_v9.py render --work op60 --tag g68K28b --start a --end b --out x.mp4
"""
import argparse, re, subprocess, sys
from pathlib import Path
import numpy as np
import skia
import film_pub
import os as _os
MODE = _os.environ.get('V9MODE', 'color')   # 11-11：band = 旁注带（用户否了：“太破坏连贯性了”）；color = 字都留主屏，只靠颜色把小字和音对上（用户：“可视化可能去匹配颜色还是可以做……给他一些音上色”）
TOP9 = 830 if MODE == 'band' else 710
film_pub.TOP = TOP9
import film_v6
film_v6.TOP = TOP9
import film_v8
from film_v8 import Film8, FEEL_C, LINE_C
from film_v6 import WHITE, BG, mix, ease, W, H, FPS
from film_v3 import R3, ROOT, rd

STRIP_Y0 = 704
NOTE_COLS = [(96, 206, 236), (244, 146, 112), (166, 226, 110), (214, 150, 246)]
LOW = re.compile('左手|低音|低声部|低八度|低沉|贝斯|低处')
HIGH = re.compile('右手|旋律|高音|歌声|主题|唱|高处')
MID = re.compile('内声部|中声部|中音')


def derive(work, tag):
    """11-11 用户：“小字里很大部分也是值得去做这种动画效果的……在这种动画里可能也值得继续分大小字”。
    对得上某一刻的小字（定位见 line_r79o/r3/locate.py，两种做法都定到且重合）从主屏挪到旁注带；旁注也按定位到点出现。产物 screen_{作品}_{TAG}V9.json。"""
    import os
    scr = rd(R3/f's24/screen_{work}_{tag}.json'); loc = rd(R3/f's24/locate_final_{work}.json')
    src = rd(R3.parent/os.environ.get('PUB_SRC', 'r2e')/f'{work}_src.json')
    pts = {b['id']: b['points'] for s in src['sections'] for b in s['beads']}

    def place(text, frm):
        best = None
        for f in frm or []:
            for p in pts.get(f, []):
                if p['id'] in loc:
                    ov = len(set(p['text']) & set(text))
                    if ov >= 3 and (best is None or ov > best[0]): best = (ov, p['id'])
        if not best: return None
        L = loc[best[1]]; w0, w1 = L['win']; return {'win': [w0, max(w1, w0+6.)], 'hand': L.get('hand') or ''}
    moved = 0
    if MODE == 'color':
        for s in scr['sections']:
            feels = [it for r in s['rows'] if r['kind'] == 'feel' for it in r['items']]
            for r in s['rows']:
                r.pop('at', None)
                for it in r.get('items') or []:
                    it.pop('at', None); L = place(it['text'], it.get('from'))
                    if L: it['hl'] = L; moved += 1
            for nt in s.get('notes') or []:   # 讲音乐的旁注不出字，只把位置和声部交给同一颗珠子在主屏的那条感受
                L = place(nt['text'], nt.get('from'))
                if not L or not L['hand']: continue
                tgt = next((it for it in feels if 'hl' not in it and set(it.get('from') or []) & set(nt.get('from') or [])), None)
                if tgt: tgt['hl'] = L; moved += 1
            s['notes'] = []; s['band'] = []
        (R3/f's24/screen_{work}_{tag}V9.json').write_text(__import__('json').dumps(scr, ensure_ascii=False, indent=1), encoding='utf-8'); print(work, '主屏小字带颜色的', moved, flush=True)
        import shutil; shutil.copyfile(R3/f'script_{work}_{tag}.json', R3/f'script_{work}_{tag}V9.json')
        return tag+'V9'
    for s in scr['sections']:
        band = []
        for r in s['rows']:
            if r['kind'] == 'feel':
                keep = []
                for it in r['items']:
                    L = place(it['text'], it.get('from'))
                    if L: band.append(dict(L, text=it['text'], kind='feel')); moved += 1
                    else: it.pop('at', None); keep.append(it)
                r['items'] = keep
            else: r.pop('at', None)
        s['rows'] = [r for r in s['rows'] if r['kind'] == 'line' or r['items']]
        for nt in s.get('notes') or []:
            L = place(nt['text'], nt.get('from'))
            band.append(dict(L or {'win': None, 'hand': ''}, text=nt['text'], kind='note'))
        s['band'] = band; s['notes'] = []
    (R3/f's24/screen_{work}_{tag}V9.json').write_text(__import__('json').dumps(scr, ensure_ascii=False, indent=1), encoding='utf-8'); print(work, '挪进旁注带的小字', moved, flush=True)
    import shutil; shutil.copyfile(R3/f'script_{work}_{tag}.json', R3/f'script_{work}_{tag}V9.json')   # 分段、阶段名照抄
    return tag+'V9'


class Film9(Film8):
    def __init__(self, work, tag):
        super().__init__(work, derive(work, tag))
        parts = {}
        for n in self.song.notes: parts.setdefault(n.part, []).append(n.pitch)
        hand_part = {'左手': min(parts, key=lambda k: np.mean(parts[k])), '右手': max(parts, key=lambda k: np.mean(parts[k]))}
        self.secwin = {}
        for i, (t0, sec) in enumerate(self.starts):
            self.secwin[sec] = (t0, self.starts[i+1][0] if i+1 < len(self.starts) else self.dur)
        self.band = {}; marks = []
        if MODE == 'color':
            for sec, s in self.screen.items():
                k = 0
                for r in s['rows']:
                    for it in r.get('items') or []:
                        if it.get('hl'):
                            it['hlcol'] = NOTE_COLS[k % len(NOTE_COLS)]; k += 1
                            h = it['hl']['hand']
                            if h: marks.append((it['hl']['win'][0], it['hl']['win'][1], [hand_part[x] for x in (('左手', '右手') if h == '两手' else (h,))], it['hlcol'], True))
        for sec, s in self.screen.items():
            items = sorted(s.get('band') or [], key=lambda x: (x['win'] or [9e9])[0])
            for k, it in enumerate(items):
                it['col'] = NOTE_COLS[k % len(NOTE_COLS)]
                if it['win'] and it['hand']:
                    hs = [hand_part[h] for h in (('左手', '右手') if it['hand'] == '两手' else (it['hand'],))]
                    marks.append((it['win'][0], it['win'][1], hs, it['col'], it['kind'] == 'note'))
            self.band[sec] = items
        self.note_mark = {}
        for n in self.song.notes:
            best = None
            for m in marks:
                if m[0] <= n.time < m[1] and n.part in m[2] and (best is None or (m[4], -(m[1]-m[0])) > (best[4], -(best[1]-best[0]))): best = m   # 讲声音的旁注优先占颜色
            self.note_mark[n.note_id] = (0, 0, 0, 0, best[3], '') if best else None
        self.marks = []

    def win_of(self, it):
        return None if MODE == 'color' else super().win_of(it)

    def draw_page(self, c, sec, t, fade, s0, skip_prev=False, skip_last=False):
        if MODE != 'color': return super().draw_page(c, sec, t, fade, s0, skip_prev, skip_last)
        from film_v8 import X0, Y0, Y1
        p = self.pages[sec]; y = Y0+max(0., (Y1-Y0-p['h'])*.25)
        for n, item in enumerate(p['items']):
            if n: y += p['gap']
            col = item['col']
            if item['kind'] == 'line':
                y0 = y
                for l, rh in zip(item['rows'], item['rh']):
                    base = y+rh
                    for ch, x, sz, key in l: self.text(c, ch, X0+22+x, base, 'line', sz, mix(col, WHITE, .25) if key else LINE_C, fade)
                    y += rh*1.32
                c.drawRoundRect(skia.Rect.MakeXYWH(X0, y0+6, 6, y-y0-6), 3, 3, skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(230*fade))))
            else:
                fs = item['size']
                for row in item['rows']:
                    for it, piece, x in row:
                        fc = mix(FEEL_C, col, .45)
                        if it.get('hlcol'):
                            hc = it['hlcol']; ta, tz = it['hl']['win']; fc = mix(FEEL_C, hc, .55)
                            if ta <= t < tz+.8:
                                k = ease((t-ta)/.5) * (1. if t < tz else max(0., 1-(t-tz)/.8)); fc = mix(fc, mix(hc, WHITE, .35), k)
                        self.text(c, piece, X0+22+x, y+fs*1.05, 'bead', fs, fc, fade)
                    y += fs*1.5
        return None

    def draw_notes(self, c, sec, t):
        if MODE == 'color': return
        y = STRIP_Y0 + 8
        live = [it for it in self.band.get(sec) or [] if it['win'] and it['win'][0]-.2 <= t < it['win'][1]+.8]
        for it in live:
            fs = 28 if it['kind'] == 'feel' else 22
            ta, tz = it['win']; a = ease((t-ta)/.5) * (1. if t < tz else max(0., 1-(t-tz)/.8))
            col = it['col'] if it['hand'] else mix(FEEL_C, it['col'], .35)
            for k, piece in enumerate(self.wrap(it['text'], 'bead', fs, 1500)[:2]):
                y += fs*1.25
                if y > TOP9-8: return
                if not k: c.drawRoundRect(skia.Rect.MakeXYWH(94, y-fs*.95, 5, fs*1.2), 2, 2, skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(230*a))))
                self.text(c, piece, 112, y, 'bead', fs, mix(col, WHITE, .25 if it['kind'] == 'feel' else .1), a)
            y += fs*.3

    def frame(self, t):
        t = max(0, min(t, self.dur-.001)); sf = skia.Surface(W, H); c = sf.getCanvas(); c.clear(skia.Color(*BG, 255))
        import bisect
        i = max(0, bisect.bisect_right(self.secstart, t)-1); sec, s0 = self.starts[i][1], self.starts[i][0]
        k = ease((t-s0)/.7) if i > 0 else 1.
        self.draw_music(c, t, (120, 124, 134))
        if MODE == 'band': c.drawRect(skia.Rect.MakeXYWH(0, STRIP_Y0-6, W, TOP9-STRIP_Y0+6), skia.Paint(Color=skia.Color(*mix(BG, (40, 34, 26), .5), 255)))
        self.draw_notes(c, sec, t)
        if k < 1: self.draw_page(c, self.starts[i-1][1], t, max(0., 1-k*2), self.starts[i-1][0])
        self.draw_page(c, sec, t, 1. if k >= 1 else max(0., k*2-1), s0)
        self.rail(c, sec)
        return sf.makeImageSnapshot()


def render(work, tag, start, end, out):
    f = Film9(work, tag); end = min(end or f.dur, f.dur); d = end-start; out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', *(['-ss', str(start)] if start else []), '-i', f.audio, '-t', str(d), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(round(d*FPS)): p.stdin.write(f.frame(start+i/FPS).tobytes())
    finally: p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed')
    print(out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('--work'); ap.add_argument('--tag'); ap.add_argument('--sec', nargs='*'); ap.add_argument('--at', nargs='*', type=float)
    ap.add_argument('--t', nargs='*', type=float); ap.add_argument('--start', type=float, default=0); ap.add_argument('--end', type=float); ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'render': render(a.work, a.tag, a.start, a.end, a.out); sys.exit()
    f = Film9(a.work, a.tag)
    ts = list(a.t or [])
    for sec in a.sec or []:
        t0, t1 = f.secwin[sec]
        for x in a.at or [.5]: ts.append(t0+(t1-t0)*x)
    for sec, items in f.band.items():
        if a.sec and sec not in a.sec: continue
        for it in items: print(sec, it['kind'], [round(x, 1) for x in it['win']] if it['win'] else '不定位', it['hand'] or '不上色', it['text'])
    for t in ts:
        p = Path('out')/f'第九版_{a.work}_{a.tag}_{t:.1f}.png'; img = f.frame(t); img.save(str(p), skia.kPNG); print(p)
