python -u cmpasm.py > runs/CA.log 2>&1
for w in op60 op61; do
  N=$(python -c "import json,glob;print(','.join(sorted(p.split('\\')[-1].split('/')[-1][:-5] for p in glob.glob('evaluations/cmpasm/ca_*.json') if json.load(open(p,encoding='utf-8'))['work']=='$w')))")
  echo $w $N
  python -u calib.py CA_$w $w "$N" --shuffles 2 --judge judge_asm_v1 --workers 6 > runs/CA_${w}j.log 2>&1 &
done
wait
echo done
