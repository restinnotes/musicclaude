export JV=2 MG_ATTEMPTS=5
L=runs/run_round1.log; echo "START-C $(date)" >> $L
python -u pipe.py run schemes/Q1.json qb >> runs/run_sc_qb.log 2>&1; rc=$?
echo "qb2 GEN EXIT $rc $(date)" >> $L
[ $rc -eq 0 ] || exit 1
python -u v6cov.py qb > runs/run_cov2_qb.log 2>&1 &
python -u v6alone.py qb > runs/run_alone2_qb.log 2>&1 &
( E2E_TAG=qb python -u e2e_open.py run > runs/run_eo2_qb.log 2>&1; E2E_TAG=qb python -u e2e_open.py run --gem >> runs/run_eo2_qb.log 2>&1 ) &
python -u v6fix.py blind qb m6w > runs/run_blind2_qb.log 2>&1 &
wait
echo "qb MEASURED $(date)" >> $L
