# 用法：python scripts/render.py stills 150 165 ...      抽单帧看
#       python scripts/render.py clip 107.6 190 out.mp4   并行渲染一段，配真实录音
import multiprocessing as mp
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
AUDIO = os.environ.get('AUDIO', r'D:\musicclaude\bead_video\remotion_b\public\audio.m4a')
MUSIC = os.environ.get('MUSIC', 'work/op60_music.json')
SPEC = os.environ.get('SPEC', 'work/op60_spec.json')
CHUNKS = os.environ.get('CHUNKS', 'work/chunks')


def worker(args):
    import engine
    k, f0, f1, tmp = args
    film = engine.Film(MUSIC, SPEC)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{engine.W}x{engine.H}', '-r', str(engine.FPS),
           '-i', '-', '-c:v', 'libx264', '-crf', '19', '-preset', 'fast', '-pix_fmt', 'yuv420p', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(film.frame(f / engine.FPS).tobytes())
    p.stdin.close()
    p.wait()
    return k


def main():
    mode = sys.argv[1]
    if mode == 'stills':
        import engine
        import cv2
        film = engine.Film(MUSIC, SPEC)
        os.makedirs('work/stills', exist_ok=True)
        for s in sys.argv[2:]:
            t = float(s)
            img = film.frame(t)
            cv2.imwrite(f'work/stills/t{t:06.1f}.png', img[:, :, ::-1])
            print('ok', t)
        return
    t0, t1, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    import engine
    fps = engine.FPS
    F0, F1 = int(t0 * fps), int(t1 * fps)
    nw = int(os.environ.get('WORKERS', '12'))
    chunk = (F1 - F0) // nw + 1
    os.makedirs(CHUNKS, exist_ok=True)
    jobs = []
    for k in range(nw):
        a = F0 + k * chunk
        b = min(F1, a + chunk)
        if a >= b:
            break
        jobs.append((k, a, b, f'{CHUNKS}/c{k:02d}.mp4'))
    with mp.Pool(len(jobs)) as pool:
        for k in pool.imap_unordered(worker, jobs):
            print('chunk', k, flush=True)
    lst = f'{CHUNKS}/list.txt'
    with open(lst, 'w') as fh:
        for j in jobs:
            fh.write(f"file '{os.path.basename(j[3])}'\n")
    dur = t1 - t0
    # 片头（t0<0）延后音乐；音乐结束后的尾声用静音补足
    delay = int(max(0, -t0) * 1000)
    aud_t0 = max(0, t0)
    af = (f'adelay={delay}:all=1,' if delay else '') + f'apad,atrim=0:{dur},afade=t=in:st=0:d=0.2,afade=t=out:st={max(0, dur - 1.0)}:d=1.0'
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                           '-ss', str(aud_t0), '-i', AUDIO,
                           '-af', af,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out])
    print('done', out, os.path.getsize(out))


if __name__ == '__main__':
    main()
