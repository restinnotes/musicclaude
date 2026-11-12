until grep -q "second-wave" runs/E1.log && [ "$(pgrep -f 'exp.py 2' 2>/dev/null)" = "" ] && [ -n "$(ls runs/e2_*_r2/output.txt 2>/dev/null | head -1)" ]; do sleep 60; done
sleep 1500   # let the second wave and E2 finish (no pgrep on this host)
python - <<'PY'
import glob, json, random, evo
names=[d.replace("\\","/").split("/")[-1] for d in sorted(glob.glob("runs/e1_*")+glob.glob("runs/e2_*"))]
names=[n for n in names if evo.done(n) and not n.startswith("e1p_")]+["cw_c1_4_r1"]
plan={}
for jn in ["gpt6","gpt56","gemini"]:
    r=random.Random(f"V3E{jn}"); m=names[:]; r.shuffle(m)
    pad=(-len(m))%4; m+=r.sample(m[:-4],pad)
    for bi in range(len(m)//4):
        grp=m[bi*4:bi*4+4]+["B0"]; random.Random(f"V3E{jn}{bi}").shuffle(grp)
        plan[f"b{bi+1:02d}_{jn}"]={"judge":jn,"map":{f"文章{chr(65+i)}":n for i,n in enumerate(grp)}}
import os; os.makedirs("evaluations/V3E",exist_ok=True)
json.dump(plan,open("evaluations/V3E/plan.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
open("runs/V3E_names.txt","w").write(",".join(n for n in names if n!="cw_c1_4_r1"))
print(len(names),len(plan))
PY
python -u calib.py V3E op60 "x" --judge judge_v3 --workers 10 > runs/V3E.log 2>&1 &
python -u align.py op60 "$(cat runs/V3E_names.txt)" > runs/align_e.log 2>&1 &
wait
