# 11-01 experiment mb: baseline m with one change — N10c boost prompt v2 (BOOST_V=2: one point per item, may add an item,
# keep each segment's relation). Starts from m2 (same as m). Gemini kept off on both sides (it was down for all of m).
set -e
unset THREAD_ROUTE
export MG_ATTEMPTS=5 TAG=m LO_V=2 HUMAN_WRITER=argon FIX_LEN=0 WORD_EDITORS=argon GLOSS_TAG=m0 SRCV=4 BOOST_V=2
L=runs/run_mb.log; echo "START $1" >> $L
boost() { python -u v6boost.py fix $1 $2 >> $L 2>&1; python -u v6cov.py $2 >> $L 2>&1; python -u v6boost.py keep $1 $2 $3 >> $L 2>&1; python -u v6cov.py $3 >> $L 2>&1; }
if [ "$1" = first ]; then python -u v6boost.py fix m2 mb3 >> $L 2>&1; echo FIRSTDONE >> $L; exit 0; fi
python -u v6cov.py mb3 >> $L 2>&1; python -u v6boost.py keep m2 mb3 mb3k >> $L 2>&1; python -u v6cov.py mb3k >> $L 2>&1
boost mb3k mb4 mb4k
LO_TAG=mb4k python -u lang_open.py run >> $L 2>&1
python -u v6human.py fixopen mb4k mb5 >> $L 2>&1; python -u v6cov.py mb5 >> $L 2>&1
python -u v6guard.py fix mb4k mb5 mb5g >> $L 2>&1; python -u v6cov.py mb5g >> $L 2>&1
python -u v6guard.py revert mb4k mb5g mb5k >> $L 2>&1
python -u v6word.py mb5k mb6w >> $L 2>&1
echo MEASURE >> $L
python -u v6cov.py mb6w > runs/run_cov_mb6w.log 2>&1 &
LO_TAG=mb6w python -u lang_open.py run > runs/run_lo_mb6w.log 2>&1 &
python -u v6alone.py mb6w > runs/run_alone_mb6w.log 2>&1 &
python -u v6fix.py blind mb6w m6w > runs/run_blind_mb6w.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind mb6w m6w > runs/run_blind_mb6w_r2.log 2>&1 &
wait
echo ALLDONE >> $L
