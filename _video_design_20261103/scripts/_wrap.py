def wrap(text, n=28):
    """最多两行：一行放得下就一行；否则在最靠近中间的逗号处断，两行都不超过 30 字。"""
    if len(text) <= n:
        return [text]
    mid = len(text) / 2
    cuts = [i + 1 for i, ch in enumerate(text) if ch in '，、；：？' and i + 1 < len(text) - 1]
    good = [c for c in cuts if c <= 30 and len(text) - c <= 30]
    c = min(good, key=lambda c: abs(c - mid)) if good else int(round(mid))
    return [text[:c], text[c:]]


def segment_row(row, frags):
    # 把一行切成（文字，颜色）小段
    out = [(row, None)]
    for frag, hue in frags:
        nxt = []
        for s, h in out:
            if h is None and frag in s:
                i = s.index(frag)
                if s[:i]:
                    nxt.append((s[:i], None))
                nxt.append((frag, hue))
                if s[i + len(frag):]:
                    nxt.append((s[i + len(frag):], None))
            else:
                nxt.append((s, h))
        out = nxt
    return out


