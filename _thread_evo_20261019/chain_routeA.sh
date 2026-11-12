(python -u centers_self.py s60 2 op60 > runs/cs60.log 2>&1; python -u tourney.py op60 s60 > runs/tnA60.log 2>&1) &
(python -u centers_self.py s61 2 op61 > runs/cs61.log 2>&1; python -u tourney.py op61 s61 > runs/tnA61.log 2>&1) &
wait
for w in 60 61; do
python - "$w" <<'PY'
import glob, json, random, os, sys, evo
w=sys.argv[1]
names=[d.replace("\\","/").split("/")[-1] for d in sorted(glob.glob(f"runs/tn_s{w}_*"))]
names=[n for n in names if evo.done(n)]
plan={}
for jn in ["gpt6","gpt56","gemini"]:
    r=random.Random(f"TA{w}{jn}"); m=names[:]; r.shuffle(m)
    pad=(-len(m))%4; m+=r.sample(m[:-4],pad) if pad else []
    for bi in range(len(m)//4):
        grp=m[bi*4:bi*4+4]; random.Random(f"TA{w}{jn}{bi}").shuffle(grp)
        plan[f"b{bi+1:02d}_{jn}"]={"judge":jn,"map":{f"文章{chr(65+i)}":n for i,n in enumerate(grp)}}
os.makedirs(f"evaluations/TA{w}",exist_ok=True)
json.dump(plan,open(f"evaluations/TA{w}/plan.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(w,len(names),len(plan))
PY
done
python -u calib.py TA60 op60 x --judge judge_v4 --workers 10 > runs/TA60j.log 2>&1 &
python -u calib.py TA61 op61 x --judge judge_v4 --workers 10 > runs/TA61j.log 2>&1 &
wait
echo done
