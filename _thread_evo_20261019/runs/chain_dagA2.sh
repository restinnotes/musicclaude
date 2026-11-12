export THREAD_ROUTE=mimic MG_SLOTS=4 TAG=d LO_V=2
: > runs/run_dagA.log
python -u dag_run.py graph >> runs/run_dagA.log 2>&1
python -u dag_run.py import >> runs/run_dagA.log 2>&1
GLOSS_TAG=d0 python -u v6gen.py gloss >> runs/run_dagA.log 2>&1
GLOSS_TAG=d0 python -u v6gen.py write d0 d1 >> runs/run_dagA.log 2>&1
GLOSS_TAG=d0 python -u v6human.py find d1 >> runs/run_dagA.log 2>&1
GLOSS_TAG=d0 HUMAN_MODE=6 HUMAN_WRITER=argon python -u v6human.py write d1 d2 >> runs/run_dagA.log 2>&1
LO_TAG=d2 python -u lang_open.py run >> runs/run_dagA.log 2>&1
LO_TAG=d2 python -u lang_open.py run --gem >> runs/run_dagA.log 2>&1
GLOSS_TAG=d0 HUMAN_WRITER=argon python -u v6human.py fixopen d2 d3 >> runs/run_dagA.log 2>&1
echo MEASURE >> runs/run_dagA.log
python -u v6cov.py d3 > runs/run_cov_d3.log 2>&1 &
python -u v6alone.py d3 > runs/run_alone_d3.log 2>&1 &
python -u v6fix.py blind d3 h13 > runs/run_blind_d3.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind d3 h13 > runs/run_blind_d3_r2.log 2>&1 &
LO_TAG=d3 python -u lang_open.py run > runs/run_lo_d3.log 2>&1 &
wait
python v6weave.py d3 >> runs/run_dagA.log 2>&1
echo ALLDONE >> runs/run_dagA.log
