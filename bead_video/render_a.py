"""Version A: hand-written PIL + ffmpeg render.

Overlay states (title + accumulating paragraphs, current paragraph bright, earlier ones dimmed)
are drawn as transparent PNGs, sequenced with the concat demuxer (with short crossfade frames),
then overlaid on the earlier text-free note visualization with the original Lipatti audio.
"""
import json, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
D = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
W, H, FPS = 1920, 1080, D["fps"]
FRAMES = ROOT / "a_frames"
OUT = ROOT / "out" / "op60_beads_A_script.mp4"

F_LABEL = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 26)
F_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 46)
F_BODY = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 31)
C_BRIGHT, C_DIM, C_LABEL, C_ACC = (236, 240, 246), (128, 136, 152), (150, 160, 182), (212, 178, 120)
X0, MAXW, TOP_BODY, BOTTOM = 130, 1660, 200, 690
LH = 50  # body line height


def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if font.getlength(cur + ch) > maxw and cur:
            # keep closing punctuation on the same line
            if ch in "，。、；：！？”’）》」』…—":
                cur += ch; continue
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def progress(draw, t):
    y = 36
    for s in D["segments"]:
        x1 = X0 + (s["start"] / D["duration"]) * MAXW
        x2 = X0 + (s["end"] / D["duration"]) * MAXW - 4
        active = s["start"] <= t < s["end"]
        draw.rectangle([x1, y, x2, y + 4], fill=C_ACC if active else (60, 66, 80))
        if s["end"] <= t:
            draw.rectangle([x1, y, x2, y + 4], fill=(110, 100, 84))


def state_image(seg, upto, t):
    """upto = number of paragraphs visible (last one is current)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    progress(dr, t)
    dr.text((X0, 70), f"{seg['id']} · 第{seg['measures']}小节 · {seg['label']}", font=F_LABEL, fill=C_LABEL)
    dr.text((X0, 112), seg["title"], font=F_TITLE, fill=C_BRIGHT)
    blocks = []
    for i in range(upto):
        lines = wrap(seg["paragraphs"][i]["text"], F_BODY, MAXW)
        blocks.append((i, lines))
    # scroll: drop oldest blocks until fits
    def height(bs):
        return sum(len(l) * LH + 22 for _, l in bs)
    while len(blocks) > 1 and TOP_BODY + height(blocks) > BOTTOM:
        blocks.pop(0)
    y = TOP_BODY
    for i, lines in blocks:
        col = C_BRIGHT if i == upto - 1 else C_DIM
        for ln in lines:
            if y + LH > BOTTOM + 10:
                break
            dr.text((X0, y), ln, font=F_BODY, fill=col)
            y += LH
        y += 22
    dr.text((W - 130 - F_LABEL.getlength(D["credits"]), H - 50), D["credits"], font=F_LABEL, fill=(120, 128, 146))
    return im


def main():
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir()
    (ROOT / "out").mkdir(exist_ok=True)
    # timeline of states: (start_time, image)
    states = []
    for seg in D["segments"]:
        states.append((seg["start"], state_image(seg, 0, seg["start"])))
        for k, p in enumerate(seg["paragraphs"]):
            states.append((p["start"], state_image(seg, k + 1, p["start"])))
    states.append((D["duration"], None))
    lines, n = [], 0
    XF = 10  # crossfade frames
    prev = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (t0, im), (t1, _) in zip(states, states[1:]):
        dur = t1 - t0
        nf = min(XF, max(1, int(dur * FPS) - 1))
        for f in range(nf):
            a = (f + 1) / (nf + 1)
            fr = Image.blend(prev, im, a)
            p = FRAMES / f"{n:05d}.png"; fr.save(p); n += 1
            lines.append(f"file '{p.as_posix()}'\nduration {1/FPS:.6f}")
        p = FRAMES / f"{n:05d}.png"; im.save(p); n += 1
        lines.append(f"file '{p.as_posix()}'\nduration {max(dur - nf / FPS, 1 / FPS):.6f}")
        prev = im
    lines.append(f"file '{p.as_posix()}'")
    (ROOT / "a_concat.txt").write_text("\n".join(lines), encoding="utf-8")
    print("states", len(states) - 1, "pngs", n)
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-i", D["background"],
           "-f", "concat", "-safe", "0", "-i", str(ROOT / "a_concat.txt"),
           "-i", D["audio"],
           "-filter_complex", f"[1:v]fps={FPS},format=rgba[ov];[0:v][ov]overlay=0:0:shortest=0:eof_action=pass,format=yuv420p[v]",
           "-map", "[v]", "-map", "2:a:0", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-t", str(D["duration"]), "-movflags", "+faststart", str(OUT)]
    subprocess.run(cmd, check=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
