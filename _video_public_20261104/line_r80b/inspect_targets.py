"""Visual evidence for reported passages; does not change alignment."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from align_music import features, read, FPS

ROOT = Path(__file__).resolve().parent
C, D, env, dur = features(read(ROOT/'plans/op61_points.json')['audio'], ROOT/'cache')
old = read(ROOT/'input/op61_music_aligned.json')['notes']
fig, axs = plt.subplots(2, 1, figsize=(20, 12))
for ax, (lo, hi) in zip(axs, [(0, 6), (17, 37)]):
    a, b = round(lo*FPS), round(hi*FPS)
    local = C[:, a:b]
    ax.imshow(20*np.log10(np.maximum(local, 1e-7)/local.max()), origin='lower', aspect='auto', extent=[a/FPS, b/FPS, 20.5, 108.5], vmin=-70, vmax=-10, cmap='magma')
    notes = [n for n in old if lo <= n['s'] <= hi]
    ax.scatter([n['s'] for n in notes], [n['p'] for n in notes], edgecolors='cyan', facecolors='none', s=40)
    ax.set_yticks(np.arange(24, 109, 3)); ax.set_xticks(np.arange(lo, hi+.01, .5))
    ax.grid(alpha=.2)
    ax.set_xlabel('Recording seconds'); ax.set_ylabel('MIDI pitch')
fig.tight_layout()
fig.savefig(ROOT/'qa/op61_targeted_diagnostic.png', dpi=140)
print(ROOT/'qa/op61_targeted_diagnostic.png')
