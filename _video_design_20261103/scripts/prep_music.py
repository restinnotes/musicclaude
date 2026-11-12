# 从“音符对齐到录音”的 MIDI 和录音本身，整理出画面要用的音符数据；同时检查对齐精度。
import json,sys
import numpy as np, librosa, pretty_midi
sys.stdout.reconfigure(encoding='utf-8')
RUN=r"D:\music-experience-pipeline\runs\production\frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b"
pm=pretty_midi.PrettyMIDI(RUN+r"\music\alignment\performance_warped.mid")
al={int(k):float(v) for k,v in json.load(open(RUN+r"\music\alignment\measure_alignment.json",encoding='utf-8')).items()}
y,sr=librosa.load('work/op60.wav',sr=22050,mono=True)
hop=512
C=np.abs(librosa.cqt(y,sr=sr,hop_length=hop,fmin=librosa.midi_to_hz(21),n_bins=88,bins_per_octave=12))
env=librosa.feature.rms(y=y,hop_length=hop)[0]
fps=sr/hop
Cn=C/(np.percentile(C,99.5)+1e-9)
notes=[]
for h,ins in enumerate(pm.instruments):
    for n in ins.notes:
        i0=int(n.start*fps);i1=max(i0+2,int((n.start+0.15)*fps))
        b=min(87,max(0,n.pitch-21))
        e=float(np.mean(Cn[b,i0:i1])) if i0<C.shape[1] else 0
        g=float(np.mean(env[i0:i1])) if i0<len(env) else 0
        notes.append(dict(s=round(n.start,3),e=round(n.end,3),p=n.pitch,h=h,en=e,g=g))
notes.sort(key=lambda n:(n['s'],n['p']))
# 能量归一：单音亮度 = 这个音在录音里自己的响度 与 当时总响度 的混合
ens=np.array([n['en'] for n in notes]);gs=np.array([n['g'] for n in notes])
ens=np.clip(ens/np.percentile(ens,97),0,1)**0.6
gs=np.clip(gs/np.percentile(gs,98),0,1)**0.7
for n,a,b in zip(notes,ens,gs):
    n['en']=round(float(0.55*a+0.45*b),3);n.pop('g')
# 右手最高声部（skyline）：同时发声的一组里最高的算主线
EPS=0.045
i=0;N=len(notes)
for n in notes:n['sky']=False
rh=[n for n in notes if n['h']==1]
rh.sort(key=lambda n:n['s'])
i=0
while i<len(rh):
    j=i
    while j+1<len(rh) and rh[j+1]['s']-rh[i]['s']<EPS: j+=1
    top=max(rh[i:j+1],key=lambda n:n['p']);top['sky']=True
    i=j+1
# 对齐检查：用每 20 秒窗口，把 MIDI 起音序列和录音起音强度做相关，看最优偏移
ons=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
tr=np.zeros(len(ons))
for n in notes:
    k=int(n['s']*fps)
    if 0<=k<len(tr):tr[k]+=1
tr=np.convolve(tr,np.hanning(5),'same')
W=int(20*fps);rows=[]
for a in range(0,len(ons)-W,W):
    o=ons[a:a+W]-ons[a:a+W].mean();t=tr[a:a+W]-tr[a:a+W].mean()
    if o.std()==0 or t.std()==0:continue
    lags=range(-16,17);cs=[np.dot(np.roll(t,l),o)/(np.linalg.norm(t)*np.linalg.norm(o)+1e-9) for l in lags]
    b=int(np.argmax(cs));rows.append((a/fps,list(lags)[b]/fps*1000,cs[b]))
print('窗口起点s  最优偏移ms  相关')
for r in rows:print(f'{r[0]:7.0f} {r[1]:8.0f} {r[2]:6.2f}')
print('偏移绝对值中位数 %.0f ms, 最大 %.0f ms'%(np.median([abs(r[1]) for r in rows]),max(abs(r[1]) for r in rows)))
# 总响度曲线（每 0.1 秒一个值），后面画面整体明暗用
step=int(0.1*fps);envs=[round(float(np.mean(env[i:i+step])/(np.percentile(env,98)+1e-9)),3) for i in range(0,len(env),step)]
bars=sorted((k,v) for k,v in al.items())
json.dump(dict(notes=notes,bars=bars,env=envs,dur=len(y)/sr),open('work/op60_music.json','w',encoding='utf-8'))
# 每小节音符统计：核对“谱面事实”
print('小节  起点s 右手数 左手数 最高 最低 左手最高')
for k,t in bars:
    t1=al.get(k+1,len(y)/sr)
    R=[n for n in notes if n['h']==1 and t<=n['s']<t1];L=[n for n in notes if n['h']==0 and t<=n['s']<t1]
    print(f"{k:4d} {t:6.1f} {len(R):4d} {len(L):4d} {max([n['p'] for n in R+L] or [0]):4d} {min([n['p'] for n in R+L] or [0]):4d} {max([n['p'] for n in L] or [0]):4d}  hi{(max([n['en'] for n in R+L] or [0])):.2f}")
