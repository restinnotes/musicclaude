export THREAD_ROUTE=mimic MG_SLOTS=3
python -u v6gen.py gloss > runs/run_gloss.log 2>&1 &
python -u v6drift.py f8 > runs/run_drift_f8.log 2>&1 &
wait
python -u v6gen.py write w38 g1 > runs/run_gen_g1.log 2>&1
python -u v6alone.py g1 > runs/run_alone_g1.log 2>&1 &
python -u v6cov.py g1 > runs/run_cov_g1.log 2>&1 &
python -u v6check.py check g1 > runs/run_chk_g1.log 2>&1 &
python -u v6drift.py g1 > runs/run_drift_g1.log 2>&1 &
wait
python -u v6gen.py fix g1 g2 > runs/run_gen_g2.log 2>&1
python -u v6alone.py g2 > runs/run_alone_g2.log 2>&1 &
python -u v6cov.py g2 > runs/run_cov_g2.log 2>&1 &
python -u v6check.py check g2 > runs/run_chk_g2.log 2>&1 &
python -u v6drift.py g2 > runs/run_drift_g2.log 2>&1 &
python -u v6fix.py blind g2 > runs/run_blind_g2.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind g2 > runs/run_blind_g2_r2.log 2>&1 &
wait
python v6weave.py g2 > runs/run_weave_g2.log 2>&1
echo ALLDONE >> runs/run_weave_g2.log
