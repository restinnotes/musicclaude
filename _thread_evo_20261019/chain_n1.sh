until [ $(ls runs/n1_*/output.txt runs/n1_*/uncertain.json 2>/dev/null | wc -l) -ge 24 ]; do sleep 30; done
python - <<'PY'
import glob, json, random, os, evo
names=[d.replace("\\","/").split("/")[-1] for d in sorted(glob.glob("runs/n1_*"))]
names=[n for n in names if evo.done(n)]+["g_P0_op60_orig_D3_r2"]
plan={}
for jn in ["gpt6","gpt56","gemini"]:
    r=random.Random(f"V4N1{jn}"); m=names[:]; r.shuffle(m)
    pad=(-len(m))%4; m+=r.sample(m[:-4],pad)
    for bi in range(len(m)//4):
        grp=m[bi*4:bi*4+4]+["B0"]; random.Random(f"V4N1{jn}{bi}").shuffle(grp)
        plan[f"b{bi+1:02d}_{jn}"]={"judge":jn,"map":{f"文章{chr(65+i)}":n for i,n in enumerate(grp)}}
os.makedirs("evaluations/V4N1",exist_ok=True)
json.dump(plan,open("evaluations/V4N1/plan.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(names),len(plan))
PY
python -u calib.py V4N1 op60 "x" --judge judge_v4 --workers 12 > runs/V4N1.log 2>&1
