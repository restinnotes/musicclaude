"""全 D 盘找录音和乐谱，结果写到 qa/log/audio_hits.txt。"""
import os, re, sys
EXT = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.opus', '.webm', '.mp4', '.mkv', '.aac', '.wma', '.ape', '.mid', '.midi', '.musicxml', '.mxl', '.krc', '.lrc'}
HIT = re.compile(r'richter|里赫特|李希特|ballade|ballad|叙事曲|op\.?[ _-]*52|chopin|肖邦|F[ _-]?minor|Рихтер', re.I)
SKIP = {'$RECYCLE.BIN', 'System Volume Information', 'node_modules', '.git', 'Config.Msi', 'DockerDesktopWSL', 'SteamLibrary', 'Program Files', 'Program Files (x86)'}
out = open(sys.argv[1], 'w', encoding='utf-8'); n = 0; audio = 0
for root, dirs, files in os.walk('D:\\'):
    dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('tool-results') and d != 'runs']
    for f in files:
        n += 1
        if os.path.splitext(f)[1].lower() in EXT:
            audio += 1; p = os.path.join(root, f)
            if HIT.search(p):
                try: sz = os.path.getsize(p)
                except OSError: sz = -1
                out.write(f'{sz}\t{p}\n'); out.flush()
out.write(f'# 完成：共扫 {n} 个文件，音频和乐谱 {audio} 个\n'); out.close()
