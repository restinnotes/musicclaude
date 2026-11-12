"""11-11 晚（L33 流程审查采纳）：开新一批之前查上一批写没写进试验记录。两天内有开放评审结果的版本，名字要在两份试验记录之一里出现。
python r3/gate.py        → 没写的列出来，退出码 1"""
import sys, time, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
S = Path(__file__).resolve().parent/'s24'
logs = ''.join(Path(p).read_text(encoding='utf-8') for p in ['D:/musicclaude/_thread_evo_20261019/试验记录.md', 'D:/musicclaude/_dag2_video_20261104/试验记录.md'])
tags = {re.sub(r'^openF3_op6[01]_[a-z0-9]+_g68', '', p.stem) for p in S.glob('openF3_*.json') if time.time() - p.stat().st_mtime < 2*86400}
miss = sorted(t for t in tags if t not in logs and t != 'K11g')
print('试验记录缺：', miss or '无'); sys.exit(1 if miss else 0)
