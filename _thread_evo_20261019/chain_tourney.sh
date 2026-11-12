(python -u centers.py find c60v2 2 op60 v2 > runs/cf60v2.log 2>&1; python -u tourney.py op60 c60v2 > runs/tn60.log 2>&1) &
(python -u centers.py find c61v2 2 op61 v2 > runs/cf61v2.log 2>&1; python -u tourney.py op61 c61v2 > runs/tn61.log 2>&1) &
wait
for w in 60 61; do
python - "$w" <<'PY'
import glob, json, random, os, sys, evo
w=sys.argv[1]
names=[d.replace("\\","/").split("/")[-1] for d in sorted(glob.glob(f"runs/tn_c{w}v2_*"))]
names=[n for n in names if evo.done(n)]
plan={}
for jn in ["gpt6","gpt56","gemini"]:
    r=random.Random(f"TN{w}{jn}"); m=names[:]; r.shuffle(m)
    pad=(-len(m))%4; m+=r.sample(m[:-4],pad) if pad else []
    for bi in range(len(m)//4):
        grp=m[bi*4:bi*4+4]; random.Random(f"TN{w}{jn}{bi}").shuffle(grp)
        plan[f"b{bi+1:02d}_{jn}"]={"judge":jn,"map":{f"文章{chr(65+i)}":n for i,n in enumerate(grp)}}
os.makedirs(f"evaluations/TN{w}",exist_ok=True)
json.dump(plan,open(f"evaluations/TN{w}/plan.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(w,len(names),len(plan))
PY
done
python -u calib.py TN60 op60 x --judge judge_v4 --workers 10 > runs/TN60j.log 2>&1 &
python -u calib.py TN61 op61 x --judge judge_v4 --workers 10 > runs/TN61j.log 2>&1 &
wait
tail -1 runs/TN60j.log runs/TN61j.log
