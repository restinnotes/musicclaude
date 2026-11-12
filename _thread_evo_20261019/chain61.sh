until python -c "import json,sys; d=json.load(open('D:/musicclaude/_bead_op61_20261020/deliverable/03_Bead机器可读/13段_STRUCT轻量版.json',encoding='utf-8')); sys.exit(0 if len(d['segments'])==13 else 1)" 2>/dev/null; do sleep 60; done
python -u hold61.py centers > runs/H61c.log 2>&1
python -u hold61.py gen > runs/H61g.log 2>&1
python - <<'PY'
import glob, json, random, os, evo
names=[d.replace("\\","/").split("/")[-1] for d in sorted(glob.glob("runs/h61_*"))]
names=[n for n in names if evo.done(n)]
plan={}
for jn in ["gpt6","gpt56","gemini"]:
    r=random.Random(f"V4H61{jn}"); m=names[:]; r.shuffle(m)
    pad=(-len(m))%4; m+=r.sample(m[:-4],pad)
    for bi in range(len(m)//4):
        grp=m[bi*4:bi*4+4]; random.Random(f"V4H61{jn}{bi}").shuffle(grp)
        plan[f"b{bi+1:02d}_{jn}"]={"judge":jn,"map":{f"文章{chr(65+i)}":n for i,n in enumerate(grp)}}
os.makedirs("evaluations/V4H61",exist_ok=True)
json.dump(plan,open("evaluations/V4H61/plan.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(names),len(plan))
PY
python -u calib.py V4H61 op61 "x" --judge judge_v4 --workers 12 > runs/V4H61.log 2>&1
tail -1 runs/V4H61.log
