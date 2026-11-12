# 11-02 round 2: scheme R, 3 samples per work (A3 reused from qe, same prompt); coverage + single read on each sample
export JV=2 MG_ATTEMPTS=5
L=runs/run_round1.log; echo "R START $(date)" >> $L
for k in 1 2 3; do
  ( SAMPLE=$k python -u pipe.py run schemes/R.json ra > runs/run_sc_ras$k.log 2>&1 || SAMPLE=$k python -u pipe.py run schemes/R.json ra >> runs/run_sc_ras$k.log 2>&1; echo "ras$k GEN EXIT $? $(date)" >> $L ) &
done
wait
for k in 1 2 3; do
  if [ -f evaluations/v6fix/op60_ras$k.json ] && [ -f evaluations/v6fix/op61_ras$k.json ]; then
    ( python -u v6cov.py ras$k > runs/run_cov2_ras$k.log 2>&1 ) &
  fi
done
wait
echo "R COV DONE $(date)" >> $L
