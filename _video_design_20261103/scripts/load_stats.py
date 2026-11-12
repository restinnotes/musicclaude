# 读取 r54weave 合写文件，按录音对齐数据算每段时长与阅读负荷（只读，不改任何主线文件）
import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
EVO=Path(r'D:\musicclaude\_thread_evo_20261019')
RUNS=Path(r'D:\music-experience-pipeline\runs\production')
WORKS={'op60':(RUNS/'frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b','船歌'),
       'op61':(RUNS/'polonaise-fantaisie-op-61-d53d9c49da26','幻想波兰舞曲')}
def parse(md):
    segs=[];cur=None;last=None
    for ln in md.splitlines():
        m=re.match(r'^### ([\d–-]+) 小节\s*（(.+?)）',ln)
        if m:
            cur={'bars':m.group(1),'rel':m.group(2),'lines':[],'beads':[]};segs.append(cur);continue
        if not cur: continue
        if ln.startswith('>'):
            t=ln[1:].strip()
            if t.startswith('<small>'):
                if cur['beads']: cur['beads'][-1]['where']=re.sub(r'</?small>','',t).strip('（）')
                continue
            cur['beads'].append({'text':t,'where':'','after':len(cur['lines'])-1})
        elif ln.strip():
            t=re.sub(r'\s*〔.*$','',ln).strip()
            cur['lines'].append(t)
    return segs
def clen(s): return len(re.sub(r'\s','',s))
out={}
for w,(run,name) in WORKS.items():
    al={int(k):float(v) for k,v in json.load(open(run/'music/alignment/measure_alignment.json',encoding='utf-8')).items()}
    dur=None
    pr=run/'production-run.json'
    last=max(al)
    md=(EVO/f'deliver_20261103_r54weave/{w}_线与珠子_r54weave.md').read_text(encoding='utf-8')
    segs=parse(md)
    print(f'\n=== {w} {name}  对齐小节 {min(al)}–{last}，最后小节起点 {al[last]:.1f}s')
    tl=tb=0;rows=[]
    for i,s in enumerate(segs):
        a,b=[int(x) for x in re.split('[–-]',s['bars'])]
        t0=al.get(a); t1=al.get(b+1)
        if t1 is None: t1=al[last]+ (al[last]-al.get(last-1,al[last]-4))
        d=t1-t0
        L=sum(clen(x) for x in s['lines']);B=sum(clen(x['text']) for x in s['beads'])
        tl+=L;tb+=B
        rows.append((s['bars'],s['rel'],t0,d,L,len(s['lines']),B,len(s['beads'])))
    T=rows[-1][2]+rows[-1][3]
    print('小节      关系      起点   时长   线字 条  珠字 颗  线字/秒 全部字/秒')
    for r in rows:
        print(f"{r[0]:8s} {r[1]:6s} {r[2]:6.1f} {r[3]:6.1f} {r[4]:5d} {r[5]:2d} {r[6]:5d} {r[7]:2d}  {r[4]/r[3]:6.2f} {(r[4]+r[6])/r[3]:6.2f}")
    print(f'合计 时长{T:.0f}s={T/60:.1f}分  线{tl}字 珠{tb}字  线{tl/T:.2f}字/秒 全部{(tl+tb)/T:.2f}字/秒')
    # 在每秒 x 字的读速下，全部读完需要几倍音乐时长
    for cps in (5,6,8):
        print(f'  读速{cps}字/秒：只读线占用 {tl/cps/T*100:.0f}% 时长；线+珠 {((tl+tb)/cps)/T*100:.0f}% 时长；超过100%的段数(线+珠) {sum(1 for r in rows if (r[4]+r[6])/cps>r[3])}/{len(rows)}；只线超的段数 {sum(1 for r in rows if r[4]/cps>r[3])}')
    out[w]=segs
json.dump(out,open(r'D:\musicclaude\_video_design_20261103\r54weave_parsed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
