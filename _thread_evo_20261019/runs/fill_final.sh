# wait for chain_final, then re-run every measurement until all judges returned (scripts skip finished calls)
cd /d/musicclaude/_thread_evo_20261019
until grep -q ALLDONE runs/run_final.log 2>/dev/null; do sleep 60; done
export LO_V=2
L=runs/run_fill.log; : > $L
for round in 1 2 3 4; do
  echo "ROUND $round $(date +%H:%M)" >> $L
  for t in h23 h25w q8w q10w h24 h24g q9 q9g; do python -u v6cov.py $t >> $L 2>&1 & done; wait
  for t in h23 h25w q8w q10w; do LO_TAG=$t python -u lang_open.py run >> $L 2>&1 & done
  python -u v6alone.py h23 >> $L 2>&1 & python -u v6alone.py h25w >> $L 2>&1 &
  wait
  python -u v6fix.py blind h23 h17 >> $L 2>&1 & python -u v6fix.py blind q8w h23 >> $L 2>&1 &
  python -u v6fix.py blind h25w h23 >> $L 2>&1 & BLIND_REP=2 python -u v6fix.py blind h25w h23 >> $L 2>&1 &
  python -u v6fix.py blind q10w h25w >> $L 2>&1 &
  wait
  n=$(grep -c "FAILED" $L | tail -1)
  python - <<'P' >> $L
import evo
ids=[f"cov_{w}_{j}_{t}" for t in ("h23","h25w","q8w","q10w") for w in ("op60","op61") for j in ("g6","g56")]
ids+=[f"v6b_{w}_{j}_{a}_vs{b}" for a,b in (("h23","h17"),("q8w","h23"),("h25w","h23"),("q10w","h25w")) for w in ("op60","op61") for j in ("g6","g56")]
ids+=[f"al_{w}_{j}_{t}" for t in ("h23","h25w") for w in ("op60","op61") for j in ("g6","g56")]
miss=[i for i in ids if not evo.done(i)]
print("MISSING", len(miss), miss)
open("runs/fill_missing.txt","w").write(str(len(miss)))
P
  [ "$(cat runs/fill_missing.txt)" = "0" ] && break
  sleep 600
done
echo FILLDONE >> $L
