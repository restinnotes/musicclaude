"""11-12 L38（第一次交回后的修改版）没过，第二次交回提出者（准则 I12：提出者判不可能才关；同一方案交回三次仍无改善报用户）。
python r3/handback_l38.py 34g62"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import handback_all as H
bi = sys.argv[1]; b0, i0 = bi[:2], bi[2:]
orig = H.scheme_info
def info(b, i):
    if b == '38':
        n, h = orig(b0, i0); prev = H.rd(H.S/f'hb2_{bi}.json')
        note = os.environ.get('HB_NOTE', '')
        return n + '（第二次交回）', h + f"\n【第一次交回时你的判断】{prev.get('why','')[:800]}\n【你上次改了什么】{prev.get('change','')[:600]}" + (f"\n【主持人说明】{note}" if note else '')
    return orig(b, i)
H.scheme_info = info
H.one(('38', bi))
