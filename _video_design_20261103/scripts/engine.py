# 《船歌》画面引擎：每一帧只由时间 T 决定。
# 设计原则：
# 1. 音乐场是“航迹”：音符在船头生成、向后退去，没有未来音符（实时内容只用已发生的）。
# 2. 画面只演听得见的事实：左手没音，水波就真的没了；颜色只来自珠子写过的冷暖。
# 3. 文字分两层：线（底部一句，不动）；珠子摘句（贴在它说的那几个音旁边，随音乐退去）。
# 4. 颜色只有三种含义：金=靠近与欢喜，玫=留不住，蓝=怕与收住。线、珠子、音符同色相连。
import json, math, sys
import numpy as np
import cv2
import skia

import os
LAYOUT = os.environ.get('LAYOUT', 'sub')
W, H, FPS = 1920, 1080, 30
NOW_X = 1780.0 if LAYOUT == 'rail' else 1540.0       # 船头位置
YSHIFT = 90.0 if LAYOUT == 'rail' else 0.0
V = 66.0             # 每秒后退像素
Y_LOW, Y_HIGH = 778.0, 122.0
P_LOW, P_HIGH = 24, 103
FIELD_BOTTOM = 800.0

HUE = {
    'gold': (255, 196, 92),
    'rose': (255, 96, 132),
    'blue': (126, 196, 255),
}
FONT_DIR = 'work/fonts/'


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def col(c, a=1.0):
    return skia.Color4f(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, max(0.0, min(1.0, a)))


def y_of(p):
    return YSHIFT + Y_LOW + (p - P_LOW) * (Y_HIGH - Y_LOW) / (P_HIGH - P_LOW)


class Film:
    def __init__(self, music_path, spec_path):
        m = json.load(open(music_path, encoding='utf-8'))
        s = json.load(open(spec_path, encoding='utf-8'))
        self.notes = m['notes']
        self.bars = {int(k): float(v) for k, v in m['bars']}
        self.dur = float(m['dur'])
        self.env = m['env']
        self.spec = s
        self.starts = np.array([n['s'] for n in self.notes])
        self.mood = sorted(s['mood'], key=lambda x: x['t'])
        self.lines = sorted(s['lines'], key=lambda x: x['t'])
        self.phrases = sorted(s['phrases'], key=lambda x: x['t'])
        self.ghosts = s.get('ghosts', [])
        self.beads = s.get('necklace', [])
        self.arcs = s.get('arcs', [])
        self.end_t = s.get('end_t', self.dur)
        self.tail = s.get('tail', 0.0)
        self.wave_on = s.get('wave', True)
        self.gain = s.get('gain', 1.0)
        # 被摘句点亮的音符：记下颜色，之后留在航迹里
        self.mark = {}
        for ph in self.phrases:
            if not ph.get('sel'):
                continue
            t0, t1, kind = ph['sel']
            idx = [i for i, n in enumerate(self.notes) if t0 <= n['s'] < t1 and self._match(n, kind)]
            ph['_idx'] = idx
            for i in idx:
                self.mark[i] = ph['hue']
        # 左手水波的轮廓（每组最低音）与右手主线
        L = sorted([n for n in self.notes if n['h'] == 0], key=lambda n: n['s'])
        self.wave = self._contour(L, low=True)
        R = sorted([n for n in self.notes if n['h'] == 1 and n['sky']], key=lambda n: n['s'])
        self.melody = [(n['s'], n['p'], n['en']) for n in R]
        self.melody_s = np.array([x[0] for x in self.melody])
        self.wave_s = np.array([x[0] for x in self.wave])
        self.typeface = {k: skia.Typeface.MakeFromFile(FONT_DIR + k + '.ttf') for k in ('Serif500', 'Serif300', 'Serif700', 'Sans300', 'Sans400')}
        self.font_line = skia.Font(self.typeface['Serif500'], 47)
        self.font_phrase = skia.Font(self.typeface['Serif300'], 34)
        self.font_small = skia.Font(self.typeface['Sans300'], 22)
        self.font_title = skia.Font(self.typeface['Serif500'], 74)
        self.font_center = skia.Font(self.typeface['Serif500'], 46)
        self.font_rail = skia.Font(self.typeface['Serif500'], 40)
        self.font_rail.setSubpixel(True)
        self.font_rail.setEdging(skia.Font.Edging.kAntiAlias)
        for f in (self.font_line, self.font_phrase, self.font_small, self.font_title, self.font_center):
            f.setSubpixel(True)
            f.setEdging(skia.Font.Edging.kSubpixelAntiAlias if False else skia.Font.Edging.kAntiAlias)
        self.noise = (np.random.RandomState(7).randn(H + 64, W + 64) * 1.1).astype(np.float32)

    @staticmethod
    def _match(n, kind):
        return {
            'top': n['h'] == 1 and n['sky'],
            'rh': n['h'] == 1,
            'inner': n['h'] == 1 and not n['sky'],
            'lh': n['h'] == 0,
            'all': True,
        }[kind]

    @staticmethod
    def _contour(L, low=True):
        out = []
        i = 0
        while i < len(L):
            j = i
            while j + 1 < len(L) and L[j + 1]['s'] - L[i]['s'] < 0.05:
                j += 1
            n = min(L[i:j + 1], key=lambda x: x['p']) if low else max(L[i:j + 1], key=lambda x: x['p'])
            out.append((n['s'], n['p'], n['en']))
            i = j + 1
        return out

    def t_of_bar(self, b):
        k = int(math.floor(b))
        t0 = self.bars.get(k, self.dur)
        t1 = self.bars.get(k + 1, self.dur)
        return t0 + (b - k) * (t1 - t0)

    def mood_at(self, T):
        M = self.mood
        if T <= M[0]['t']:
            return M[0]
        for a, b in zip(M, M[1:]):
            if T < b['t']:
                span = b.get('fade', 3.0)
                k = smooth((T - (b['t'] - span)) / span)
                if k <= 0:
                    return a
                return {key: [lerp(a[key][i], b[key][i], k) for i in range(3)] for key in ('top', 'bot', 'rh', 'lh')}
        return M[-1]

    def env_at(self, T):
        i = int(T / 0.1)
        if 0 <= i < len(self.env):
            return min(1.0, self.env[i])
        return 0.0

    # ---- 画一帧 ----
    def frame(self, T):
        if T < 0:
            return self._intro(T)
        m = self.mood_at(T)
        e = self.env_at(T)
        arr = np.zeros((H, W, 4), dtype=np.uint8)
        # 背景：竖直渐变（颜色来自珠子的冷暖）
        tp = np.array(m['top'], dtype=np.float32)
        bt = np.array(m['bot'], dtype=np.float32)
        ky = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        bg = tp[None, None, :] * (1 - ky) + bt[None, None, :] * ky
        rgb = np.broadcast_to(bg, (H, W, 3)).copy()
        arr[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        arr[:, :, 3] = 255
        surf = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
        c = surf.getCanvas()
        self._draw_prow(c, T, m, e)
        self._draw_wave(c, T, m)
        self._draw_ghosts(c, T)
        self._draw_notes(c, T, m)
        self._draw_melody(c, T, m)
        surf.flushAndSubmit() if hasattr(surf, 'flushAndSubmit') else surf.flush()
        # 光晕
        small = cv2.resize(arr[:, :, :3], (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        blur = cv2.GaussianBlur(small, (0, 0), 7)
        up = cv2.resize(blur, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        f = arr[:, :, :3].astype(np.float32) + up * (0.45 + 1.05 * e)
        # 底部压暗，给线留干净的位置；左边缘淡出
        f *= self._mask[:, :, None] if hasattr(self, '_mask') else self._build_mask()[:, :, None]
        ox = int(T * 113) % 60
        oy = int(T * 71) % 60
        f += self.noise[oy:oy + H, ox:ox + W, None]
        arr[:, :, :3] = np.clip(f, 0, 255).astype(np.uint8)
        c2 = surf.getCanvas()
        self._draw_necklace(c2, T)
        self._draw_phrases(c2, T)
        self._draw_line(c2, T)
        self._draw_end(c2, T, arr)
        surf.flushAndSubmit() if hasattr(surf, 'flushAndSubmit') else surf.flush()
        return arr[:, :, :3].copy()

    def _intro(self, T):
        arr = np.zeros((H, W, 4), dtype=np.uint8)
        arr[:, :, 3] = 255
        arr[:, :, :3] = (8, 9, 20)
        surf = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
        c = surf.getCanvas()
        L = self.spec.get('intro_len', 5.0)
        a = smooth((T + L) / 0.8) * (1 - smooth((T + 0.9) / 0.8))
        t1 = self.spec.get('title', '')
        t2 = self.spec.get('subtitle', '')
        pt = skia.Paint(AntiAlias=True)
        pt.setColor4f(col((244, 242, 236), a))
        c.drawString(t1, (W - self._text_width(self.font_title, t1)) / 2, 510, self.font_title, pt)
        pt2 = skia.Paint(AntiAlias=True)
        pt2.setColor4f(col((200, 200, 210), a * 0.9))
        c.drawString(t2, (W - self._text_width(self.font_phrase, t2)) / 2, 590, self.font_phrase, pt2)
        surf.flushAndSubmit() if hasattr(surf, 'flushAndSubmit') else surf.flush()
        return arr[:, :, :3].copy()

    def _build_mask(self):
        yy = np.linspace(0, H, H, dtype=np.float32)
        xx = np.linspace(0, W, W, dtype=np.float32)
        if LAYOUT == 'rail':
            ym = np.ones_like(yy)
            q = np.clip((xx - 640) / 420, 0, 1)
            xm = 0.34 + 0.66 * (q * q * (3 - 2 * q))
        else:
            k = np.clip((yy - 700) / 200, 0, 1)
            ym = 1 - 0.72 * (k * k * (3 - 2 * k))
            xm = 0.25 + 0.75 * np.clip(xx / 520, 0, 1)
        self._mask = (ym[:, None] * xm[None, :]).astype(np.float32)
        return self._mask

    def _draw_prow(self, c, T, m, e):
        # 船头的一层光：声音响多大，光就多亮
        p = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus)
        shader = skia.GradientShader.MakeRadial(
            skia.Point(NOW_X, 430), 520,
            [skia.Color4f(m['rh'][0] / 255, m['rh'][1] / 255, m['rh'][2] / 255, 0.04 + 0.13 * e), skia.Color4f(0, 0, 0, 0)],
        )
        p.setShader(shader)
        c.drawRect(skia.Rect(0, 0, W, 860), p)

    def _x(self, s, T):
        return NOW_X - (T - s) * V

    def _visible_range(self, arr_s, T, back=24.0):
        i0 = int(np.searchsorted(arr_s, T - back))
        i1 = int(np.searchsorted(arr_s, T, side='right'))
        return i0, i1

    def _age_alpha(self, age, tau=15.0):
        return math.exp(-age / tau)

    def _draw_wave(self, c, T, m):
        # 左手画成水面：有音才有波，没有音波就断。振幅就是音高起伏。只用于真有持续摇荡的曲子。
        if not self.wave_on:
            return
        i0, i1 = self._visible_range(self.wave_s, T)
        pts = self.wave[i0:i1]
        if len(pts) < 2:
            return
        groups = []
        cur = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if b[0] - a[0] > 1.7:
                groups.append(cur)
                cur = [b]
            else:
                cur.append(b)
        groups.append(cur)
        for g in groups:
            if len(g) < 2:
                continue
            # 把活水面接到船头（声音还在响时）
            path = skia.Path()
            xs = [self._x(s, T) for s, p, en in g]
            ys = [y_of(p) for s, p, en in g]
            path.moveTo(xs[0], ys[0])
            for k in range(1, len(xs)):
                mx = (xs[k - 1] + xs[k]) / 2
                my = (ys[k - 1] + ys[k]) / 2
                path.quadTo(xs[k - 1], ys[k - 1], mx, my)
            path.lineTo(xs[-1], ys[-1])
            # 下方填充
            fill = skia.Path(path)
            base = FIELD_BOTTOM + 30
            fill.quadTo(xs[-1] + 14, ys[-1] + (base - ys[-1]) * 0.55, xs[-1] + 34, base)
            fill.lineTo(xs[0] - 34, base)
            fill.quadTo(xs[0] - 14, ys[0] + (base - ys[0]) * 0.55, xs[0], ys[0])
            fill.close()
            age_r = T - g[-1][0]
            live = math.exp(-age_r / 2.6)
            pa = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9.0))
            colors = [col(m['lh'], 0.13 * (0.25 + 0.75 * live)), col(m['lh'], 0.0)]
            pa.setShader(skia.GradientShader.MakeLinear(
                [skia.Point(0, 500), skia.Point(0, FIELD_BOTTOM + 30)], colors))
            c.drawPath(fill, pa)
            ps = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus, Style=skia.Paint.kStroke_Style, StrokeWidth=2.0,
                            StrokeCap=skia.Paint.kRound_Cap)
            ps.setColor4f(col(m['lh'], 0.26 * (0.3 + 0.7 * live)))
            c.drawPath(path, ps)

    def _draw_melody(self, c, T, m):
        # 右手主线：一根连起来的细线
        i0, i1 = self._visible_range(self.melody_s, T)
        pts = self.melody[i0:i1]
        for a, b in zip(pts, pts[1:]):
            if b[0] - a[0] > 1.8:
                continue
            xa, ya = self._x(a[0], T), y_of(a[1])
            xb, yb = self._x(b[0], T), y_of(b[1])
            age = T - b[0]
            al = 0.50 * self._age_alpha(age, 11.0)
            ps = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus, StrokeWidth=1.5, Style=skia.Paint.kStroke_Style,
                            StrokeCap=skia.Paint.kRound_Cap)
            ps.setColor4f(col(m['rh'], al))
            c.drawLine(xa, ya, xb, yb, ps)

    def _draw_ghosts(self, c, T):
        # 同一首歌上一次的样子：把旧音符叠回现在的位置（空心、很淡）
        for g in self.ghosts:
            if not (g['t0'] - 0.2 <= T <= g['t1'] + 24):
                continue
            fade_in = smooth((T - g['t0']) / 1.2)
            fade_out = 1 - smooth((T - g['t1']) / 8.0)
            for s, p in g['pts']:
                if s > T or T - s > 22:
                    continue
                x = self._x(s, T)
                y = y_of(p)
                a = 0.62 * fade_in * fade_out * self._age_alpha(T - s, 16.0)
                pp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.4, BlendMode=skia.kPlus)
                pp.setColor4f(col((236, 240, 255), a))
                c.drawCircle(x, y, 6.2, pp)

    def _draw_notes(self, c, T, m):
        i0, i1 = self._visible_range(self.starts, T)
        for i in range(i0, i1):
            n = self.notes[i]
            age = T - n['s']
            xh = self._x(n['s'], T)
            xt = self._x(min(n['e'], T), T)
            y = y_of(n['p'])
            en = n['en']
            hue = self.mark.get(i)
            sky = n['h'] == 1 and n['sky']
            flash = math.exp(-age / 0.32)
            fade = self._age_alpha(age, 15.0)
            size = 0.72 + 0.75 * self.env_at(n['s'])
            if hue:
                c0 = HUE[hue]
                fresh = math.exp(-age / 6.0)
                a = (0.34 + 0.66 * en) * (0.20 + 0.80 * fresh) * (0.35 + 0.65 * fade)
                h = 3.2 + 3.4 * fresh
                rad = 2.2 + 8.0 * flash + 2.2 * en * fresh
            elif n['h'] == 1:
                c0 = m['rh']
                a = ((0.26 + 0.64 * en) if sky else (0.10 + 0.34 * en)) * fade
                h = 4.2 if sky else 2.4
                rad = (2.6 + 6.5 * flash * en) if sky else (1.4 + 3.2 * flash * en)
            else:
                c0 = m['lh']
                a = (0.16 + 0.44 * en) * fade
                h = 3.0
                rad = 2.2 + 8.0 * flash * en
            a = min(1.0, a * self.gain)
            # 音身（持续的部分）
            if xt - xh > 1:
                pl = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus, StrokeWidth=h, Style=skia.Paint.kStroke_Style,
                                StrokeCap=skia.Paint.kRound_Cap)
                pl.setColor4f(col(c0, a * 0.55))
                c.drawLine(xh, y, xt, y, pl)
            # 音头
            pd = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus)
            pd.setColor4f(col(c0, min(1.0, a + 0.5 * flash)))
            c.drawCircle(xh, y, rad * size, pd)
            if flash > 0.04:
                pg = skia.Paint(AntiAlias=True, BlendMode=skia.kPlus,
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8.0))
                pg.setColor4f(col(c0, 0.55 * flash * (0.3 + 0.7 * en)))
                c.drawCircle(xh, y, rad * size * 2.2, pg)

    def _text_width(self, font, s):
        return font.measureText(s)

    def _draw_phrases(self, c, T):
        for ph in self.phrases:
            t = ph['t']
            d = ph['d']
            if not (t - 0.1 <= T <= t + d + 0.9):
                continue
            a = smooth((T - t) / 0.45) * (1 - smooth((T - (t + d)) / 0.85))
            if a <= 0:
                continue
            hue = HUE[ph['hue']]
            idx = ph.get('_idx') or []
            # 以被点亮音符里已经响过的那些为锚
            sounded = [self.notes[i] for i in idx if self.notes[i]['s'] <= T]
            # 文字位置：只由它出现那一刻决定，之后跟随音乐一起退去
            ax = NOW_X - (T - t) * V + ph.get('dx', -40)
            ay = ph['y'] + YSHIFT
            tw = self._text_width(self.font_phrase, ph['text'])
            tx = ax - tw
            # 底衬：让文字在音符上也看得清
            pb = skia.Paint(AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16.0))
            pb.setColor4f(skia.Color4f(0, 0, 0, 0.42 * a))
            c.drawRoundRect(skia.Rect(tx - 16, ay - 38, tx + tw + 16, ay + 12), 10, 10, pb)
            # 引线：从文字连到它说的那些音
            if sounded:
                cx = np.mean([self._x(n['s'], T) for n in sounded])
                cy = np.mean([y_of(n['p']) for n in sounded])
                lx = max(tx + 8, min(tx + tw - 8, cx))
                ly = ay + 8 if cy > ay else ay - 40
                pl = skia.Paint(AntiAlias=True, StrokeWidth=1.1, Style=skia.Paint.kStroke_Style)
                pl.setColor4f(col(hue, 0.55 * a))
                c.drawLine(lx, ly, cx, cy, pl)
            pt = skia.Paint(AntiAlias=True)
            pt.setColor4f(col(hue, a))
            c.drawString(ph['text'], tx, ay, self.font_phrase, pt)

    def _draw_rail(self, c, T):
        # 一段一页：同一段已经出现的句子都留着，当前句最亮；进入新段才翻页。字不动。
        X0, TOP, COLS = 96.0, 170.0, 13
        font = self.font_rail
        cur = None
        for ln in self.lines:
            if ln['t'] - 0.1 <= T:
                cur = ln
        if cur is None:
            return
        sec = cur['id'][:3]
        group = [l for l in self.lines if l['id'][:3] == sec and l['t'] - 0.1 <= T]
        first = group[0]
        page_a = smooth((T - first['t']) / 0.6)
        nxt = [l for l in self.lines if l['t'] > T and l['id'][:3] != sec]
        if nxt:
            page_a *= 1 - smooth((T - (nxt[0]['t'] - 0.9)) / 0.7)
        y = TOP
        for ln in group:
            chars = []
            for row in ln['rows']:
                for s, hue in row:
                    chars += [(ch, hue) for ch in s]
            rows = []
            cur_row = []
            for ch, hue in chars:
                if len(cur_row) >= COLS and ch not in '，。、；：？！”）':
                    rows.append(cur_row)
                    cur_row = []
                cur_row.append((ch, hue))
            if cur_row:
                rows.append(cur_row)
            is_cur = ln is cur
            a = smooth((T - ln['t']) / 0.6) * page_a * (1.0 if is_cur else 0.46)
            for r in rows:
                x = X0
                # 同色片段合并绘制
                i = 0
                while i < len(r):
                    j = i
                    while j + 1 < len(r) and r[j + 1][1] == r[i][1]:
                        j += 1
                    txt = ''.join(q[0] for q in r[i:j + 1])
                    pt = skia.Paint(AntiAlias=True)
                    pt.setColor4f(col(HUE[r[i][1]] if r[i][1] else (244, 242, 236), a))
                    c.drawString(txt, x, y, font, pt)
                    x += font.measureText(txt)
                    i = j + 1
                y += 53
            y += 26

    def _draw_line(self, c, T):
        if LAYOUT == 'rail':
            return self._draw_rail(c, T)
        for ln in self.lines:
            t = ln['t']
            d = ln['d']
            if not (t - 0.1 <= T <= t + d + 0.8):
                continue
            a = smooth((T - t) / 0.6) * (1 - smooth((T - (t + d)) / 0.7))
            if a <= 0:
                continue
            rows = ln['rows']
            lh = 68
            y0 = 908 if len(rows) == 2 else 942
            for r, row in enumerate(rows):
                tw = sum(self._text_width(self.font_line, seg[0]) for seg in row)
                x = (W - tw) / 2
                y = y0 + r * lh
                for s, hue in row:
                    pt = skia.Paint(AntiAlias=True)
                    if hue:
                        pt.setColor4f(col(HUE[hue], a))
                    else:
                        pt.setColor4f(col((244, 242, 236), a))
                    c.drawString(s, x, y, self.font_line, pt)
                    x += self._text_width(self.font_line, s)

    def _necklace_x(self, t):
        x0, x1 = 160.0, 1760.0
        return x0 + (x1 - x0) * t / self.dur

    def _draw_necklace(self, c, T):
        # 顶部一根线：全曲的进度；走过的珠子留下颜色；线引用前文时，从前文拉一道弧到这里
        y = 54.0
        k = 1.0
        p0 = skia.Paint(AntiAlias=True, StrokeWidth=1.0, Style=skia.Paint.kStroke_Style)
        p0.setColor4f(skia.Color4f(1, 1, 1, 0.16 * k))
        c.drawLine(self._necklace_x(0), y, self._necklace_x(self.dur), y, p0)
        xn = self._necklace_x(min(T, self.dur))
        p1 = skia.Paint(AntiAlias=True, StrokeWidth=1.4, Style=skia.Paint.kStroke_Style)
        p1.setColor4f(skia.Color4f(1, 1, 1, 0.50 * k))
        c.drawLine(self._necklace_x(0), y, xn, y, p1)
        for arc in self.arcs:
            ta, tb = arc['from'], arc['to']
            if T < tb:
                continue
            xa, xb = self._necklace_x(ta), self._necklace_x(tb)
            recent = math.exp(-(T - tb) / 7.0)
            h = min(30.0, 6 + (xb - xa) * 0.05)
            path = skia.Path()
            path.moveTo(xa, y)
            path.quadTo((xa + xb) / 2, y + h * 2.0, xb, y)
            pa = skia.Paint(AntiAlias=True, StrokeWidth=1.0 + 0.8 * recent, Style=skia.Paint.kStroke_Style)
            pa.setColor4f(col(HUE[arc['hue']], (0.10 + 0.62 * recent) * k))
            c.drawPath(path, pa)
        for b in self.beads:
            x = self._necklace_x(b['t'])
            pd = skia.Paint(AntiAlias=True)
            if T >= b['t']:
                pd.setColor4f(col(HUE[b['hue']], 0.95 * k))
                c.drawCircle(x, y, 3.4, pd)
            else:
                pd.setColor4f(skia.Color4f(1, 1, 1, 0.20 * k))
                c.drawCircle(x, y, 1.7, pd)
        pn = skia.Paint(AntiAlias=True)
        pn.setColor4f(skia.Color4f(1, 1, 1, 0.95 * k))
        if T <= self.dur:
            c.drawCircle(xn, y, 4.4, pn)

    def _draw_end(self, c, T, arr):
        # 曲终回望：音乐停了，整条线还在
        if T < self.end_t:
            return
        k = smooth((T - self.end_t) / 2.2)
        pb = skia.Paint(AntiAlias=True)
        pb.setColor4f(skia.Color4f(0.015, 0.015, 0.025, 0.93 * k))
        c.drawRect(skia.Rect(0, 0, W, H), pb)
        # 放大的整条线
        xa0, xa1 = 180.0, 1740.0
        y = 430.0
        X = lambda t: xa0 + (xa1 - xa0) * t / self.dur
        pl = skia.Paint(AntiAlias=True, StrokeWidth=1.6, Style=skia.Paint.kStroke_Style)
        pl.setColor4f(skia.Color4f(1, 1, 1, 0.55 * k))
        c.drawLine(X(0), y, X(self.dur), y, pl)
        for arc in self.arcs:
            xa, xb = X(arc['from']), X(arc['to'])
            h = (xb - xa) * 0.42
            path = skia.Path()
            path.moveTo(xa, y)
            path.quadTo((xa + xb) / 2, y + h, xb, y)
            pa = skia.Paint(AntiAlias=True, StrokeWidth=1.0, Style=skia.Paint.kStroke_Style, BlendMode=skia.kPlus)
            pa.setColor4f(col(HUE[arc['hue']], 0.46 * k))
            c.drawPath(path, pa)
        for b in self.beads:
            pd = skia.Paint(AntiAlias=True)
            pd.setColor4f(col(HUE[b['hue']], k))
            c.drawCircle(X(b['t']), y, 6.0, pd)
        center = self.spec.get('center', '')
        k2 = smooth((T - self.end_t - 2.2) / 2.0)
        if center:
            tw = self._text_width(self.font_center, center)
            pt = skia.Paint(AntiAlias=True)
            pt.setColor4f(col((244, 242, 236), k2))
            c.drawString(center, (W - tw) / 2, 250, self.font_center, pt)
        title = self.spec.get('credit', '')
        if title:
            tw = self._text_width(self.font_small, title)
            pt = skia.Paint(AntiAlias=True)
            pt.setColor4f(col((200, 200, 205), 0.8 * k2))
            c.drawString(title, (W - tw) / 2, 1000, self.font_small, pt)
