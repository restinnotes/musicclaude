"""Cheap check for music-driven / discrete Threads: share of segments whose first sentence is about the music,
and share of music sentences in the whole text.  usage: python mdrive.py <work> <glob>..."""
import re, sys, glob
import arts, evo, segcheck

MUS = re.compile(r"音乐|旋律|主题|和声|和弦|转调|调性|[A-G升降][♯♭#b]?(大|小)调|节奏|低音|小节|音型|琶音|乐句|声音|三连音|颤音|华彩|伴奏|再现|尾声|左手|右手|波兰舞曲|船歌的")
SENT = re.compile(r"[^。！？!?\n]+[。！？!?」”]*")


def score(text, work):
    j = segcheck.to_json(text, work)
    if not j:
        return None
    first = [SENT.findall(s["text"].strip())[:1] for s in j["segments"]]
    open_m = sum(bool(f and MUS.search(f[0])) for f in first) / len(j["segments"])
    sents = [x for s in j["segments"] for x in SENT.findall(s["text"])]
    return open_m, sum(bool(MUS.search(x)) for x in sents) / max(1, len(sents))


if __name__ == "__main__":
    work = sys.argv[1]
    for pat in sys.argv[2:]:
        for d in sorted(glob.glob(f"runs/{pat}")):
            n = d.replace("\\", "/").split("/")[-1]
            o = evo.output(n)
            r = score(arts.clean(o), work) if o else None
            print(f"{n:40s}", "—" if r is None else f"opens-with-music {r[0]:.2f}  music-sentences {r[1]:.2f}")
    if work == "op60":
        r = score(arts.b0(), "op60"); print(f"{'B0':40s}", "—" if r is None else f"opens-with-music {r[0]:.2f}  music-sentences {r[1]:.2f}")
