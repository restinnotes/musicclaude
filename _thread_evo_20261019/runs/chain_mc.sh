# 11-01 experiment mc: baseline m with one change — N10c boost prompt v3 (BOOST_V=3: v2 rules but each segment no longer than now).
# Starts from m2 (same as m). Gemini kept off (it was down for all of m).
set -e
unset THREAD_ROUTE
export MG_ATTEMPTS=5 TAG=m LO_V=2 HUMAN_WRITER=argon FIX_LEN=0 WORD_EDITORS=argon GLOSS_TAG=m0 SRCV=4 BOOST_V=3
L=runs/run_mc.log; echo "START $1" >> $L
boost() { python -u v6boost.py fix $1 $2 >> $L 2>&1; python -u v6cov.py $2 >> $L 2>&1; python -u v6boost.py keep $1 $2 $3 >> $L 2>&1; python -u v6cov.py $3 >> $L 2>&1; }
if [ "$1" = first ]; then python -u v6boost.py fix m2 mc3 >> $L 2>&1; echo FIRSTDONE >> $L; exit 0; fi
python -u v6cov.py mc3 >> $L 2>&1; python -u v6boost.py keep m2 mc3 mc3k >> $L 2>&1; python -u v6cov.py mc3k >> $L 2>&1
boost mc3k mc4 mc4k
LO_TAG=mc4k python -u lang_open.py run >> $L 2>&1
python -u v6human.py fixopen mc4k mc5 >> $L 2>&1; python -u v6cov.py mc5 >> $L 2>&1
python -u v6guard.py fix mc4k mc5 mc5g >> $L 2>&1; python -u v6cov.py mc5g >> $L 2>&1
python -u v6guard.py revert mc4k mc5g mc5k >> $L 2>&1
python -u v6word.py mc5k mc6w >> $L 2>&1
echo MEASURE >> $L
python -u v6cov.py mc6w > runs/run_cov_mc6w.log 2>&1 &
LO_TAG=mc6w python -u lang_open.py run > runs/run_lo_mc6w.log 2>&1 &
python -u v6alone.py mc6w > runs/run_alone_mc6w.log 2>&1 &
python -u v6fix.py blind mc6w m6w > runs/run_blind_mc6w.log 2>&1 &
BLIND_REP=2 python -u v6fix.py blind mc6w m6w > runs/run_blind_mc6w_r2.log 2>&1 &
wait
echo ALLDONE >> $L
