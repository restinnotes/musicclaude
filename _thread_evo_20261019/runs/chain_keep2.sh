export THREAD_ROUTE=mimic MG_SLOTS=3
HUMAN_WRITER=gpt HUMAN_MODE=4 python -u v6human.py write b0 h6 > runs/run_hwrite_h6b.log 2>&1
guard() {
  t=$1; export KEEP_SEV=1
  [ $t = h5 -o $t = h6 ] && export HUMAN_WRITER=gpt
  python -u v6keep.py check b0 $t > runs/run_keep2_$t.log 2>&1
  python -u v6keep.py redo b0 $t ${t}q >> runs/run_keep2_$t.log 2>&1
  python -u v6keep.py check b0 ${t}q >> runs/run_keep2_$t.log 2>&1
  python -u v6keep.py revert b0 ${t}q ${t}k >> runs/run_keep2_$t.log 2>&1
  echo GUARDDONE >> runs/run_keep2_$t.log
  python -u v6human.py find ${t}k > runs/run_hfind_${t}k.log 2>&1 &
  python -u v6alone.py ${t}k > runs/run_alone_${t}k.log 2>&1 &
  python -u v6cov.py ${t}k > runs/run_cov_${t}k.log 2>&1 &
  python -u v6check.py check ${t}k > runs/run_chk_${t}k.log 2>&1 &
  python -u v6fix.py blind ${t}k b0 > runs/run_blind_${t}k.log 2>&1 &
  BLIND_REP=2 python -u v6fix.py blind ${t}k b0 > runs/run_blind_${t}k_r2.log 2>&1 &
  wait
  echo ALLDONE >> runs/run_keep2_$t.log
}
guard h3 & guard h4 & guard h5 & guard h6 &
wait
echo ALLDONE > runs/run_keep2_done.log
