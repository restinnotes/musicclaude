import argparse, json
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from align_music import features, read

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--work', required=True)
    a.add_argument('--seconds', type=float, default=40)
    x = a.parse_args()
    root = Path(__file__).resolve().parent
    audio = read(root / f'plans/{x.work}_points.json')['audio']
    C, _, _, duration = features(audio, root/'cache')
    C = C[:, :round(x.seconds*22050/256)]
    db = librosa.amplitude_to_db(C, ref=np.max)
    fig, axs = plt.subplots(3, 1, figsize=(20, 10), sharex=True)
    paths = [root.parent / '_video_design_20261103/work' / f'{x.work}_music.json', root / f'input/{x.work}_music.json', root / f'input/{x.work}_music_aligned.json']
    for ax, path in zip(axs, paths):
        ax.imshow(db, origin='lower', aspect='auto', extent=[0, min(duration, C.shape[1]*256/22050), 20.5, 108.5], vmin=-65, vmax=-10, cmap='magma')
        if path.exists():
            notes = json.loads(path.read_text(encoding='utf-8'))['notes']
            ns = [n for n in notes if n['s'] < x.seconds]
            ax.scatter([n['s'] for n in ns], [n['p'] for n in ns], s=18, facecolors='none', edgecolors='cyan', linewidths=.8)
        ax.set_title(['Before old refinement (seed)', 'Published video input', 'Pitch-ordered candidate - review required'][list(axs).index(ax)])
        ax.set_ylabel('MIDI pitch')
        ax.set_xticks(np.arange(0, x.seconds+.1, 1), minor=True)
        ax.grid(axis='x', which='both', alpha=.15)
    axs[-1].set_xlim(0, x.seconds)
    axs[-1].set_xlabel('Recording time (s)')
    fig.tight_layout()
    out = root / f'qa/{x.work}_pitch_sync.png'
    fig.savefig(out, dpi=130)
    print(out)

if __name__ == '__main__': main()
