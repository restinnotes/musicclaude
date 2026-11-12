"""Run the same alignment and render pipeline on one or more works.

python sync_preview.py --work op60 op61
Use --full to render entire candidate films instead of opening previews.
Candidates deliberately retain REVIEW_REQUIRED status; originals stay intact.
"""
import argparse
from pathlib import Path
import subprocess
import sys
from align_music import align_file, read

ROOT = Path(__file__).resolve().parent
WORKS = {
    'op60': {'tag': 'r1', 'title': '船歌'},
    'op61': {'tag': 'r2', 'title': '幻想波兰舞曲'},
}

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--work', nargs='+', choices=list(WORKS), default=list(WORKS))
    a.add_argument('--seconds', type=float, default=35)
    a.add_argument('--full', action='store_true')
    a.add_argument('--label', default='v2', help='Output revision; keeps previous previews')
    x = a.parse_args()
    outdir = ROOT/'out/对齐试验'
    outdir.mkdir(parents=True, exist_ok=True)
    for work in x.work:
        cfg = WORKS[work]
        music = ROOT/f'input/{work}_music_aligned.json'
        ep = ROOT/f'input/{work}_events.json'
        align_file(ROOT/f'input/{work}_music_source.json', read(ROOT/f'plans/{work}_points.json')['audio'], music, ROOT/f'qa/{work}_alignment.json', ROOT/'cache', events=ep if ep.exists() else None)
        out = outdir/f'{cfg["title"]}_通用对齐_{x.label}_{"全片" if x.full else "开头试验"}.mp4'
        cmd = [sys.executable, str(ROOT/'film_pub.py'), 'render', '--work', work, '--tag', cfg['tag'], '--music', str(music), '--out', str(out)]
        if not x.full:
            cmd += ['--end', str(x.seconds)]
        subprocess.run(cmd, check=True)
        if not x.full:
            old = ROOT/f'out/{cfg["title"]}_大众版_{cfg["tag"]}.mp4'
            comparison = outdir/f'{cfg["title"]}_上下对照_{x.label}.mp4'
            # Compare the actual existing release to the candidate using one
            # shared audio stream and identical original recording timestamps.
            graph = "[0:v]crop=1920:370:0:710,pad=1920:420:0:50:color=0x0e1218,drawtext=text='ORIGINAL':x=30:y=10:fontsize=26:fontcolor=white[a];[1:v]crop=1920:370:0:710,pad=1920:420:0:50:color=0x0e1218,drawtext=text='CANDIDATE - REVIEW REQUIRED':x=30:y=10:fontsize=26:fontcolor=white[b];[a][b]vstack=inputs=2[v]"
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(old), '-i', str(out), '-filter_complex', graph, '-map', '[v]', '-map', '1:a:0', '-t', str(x.seconds), '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '19', '-c:a', 'copy', '-movflags', '+faststart', str(comparison)], check=True)
            print(comparison, flush=True)

if __name__ == '__main__': main()
