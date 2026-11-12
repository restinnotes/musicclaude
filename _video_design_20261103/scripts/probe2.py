import json,sys,numpy as np
sys.stdout.reconfigure(encoding='utf-8')
import skia
print('skia',skia.__version__)
try:
    import fontTools;print('fonttools',fontTools.version)
except Exception as e:print(e)
d=json.load(open('work/op60_music.json',encoding='utf-8'))
N=d['notes'];B=dict((k,v) for k,v in d['bars']);dur=d['dur']
def pcv(b):
    t0=B[b];t1=B.get(b+1,dur)
    v=np.zeros(12)
    for n in N:
        if n['h']==1 and n['sky'] and t0<=n['s']<t1:v[n['p']%12]+=1
    return v/(np.linalg.norm(v)+1e-9)
for name,dst,L,rng in [('第一主题回来',24,4,range(4,20)),('第一主题大再现',84,4,range(4,30)),('第三段再现',93,4,range(40,80)),('51回40',51,4,range(38,48))]:
    sc=[]
    for k in rng:
        s=np.mean([pcv(dst+i)@pcv(k+i) for i in range(L)]);sc.append((round(float(s),2),k))
    print(name,'第',dst,'小节起最像：',sorted(sc,reverse=True)[:4])
