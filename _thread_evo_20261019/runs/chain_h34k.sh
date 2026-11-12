export THREAD_ROUTE=mimic MG_SLOTS=3
until grep -q ALLDONE runs/run_hwrite_h4.log 2>/dev/null; do sleep 20; done
guard() {
  t=$1
  python -u v6keep.py check b0 $t > runs/run_keep_$t.log 2>&1
  python -u v6keep.py redo b0 $t ${t}r >> runs/run_keep_$t.log 2>&1
  python -u v6keep.py check b0 ${t}r >> runs/run_keep_$t.log 2>&1
  python -u v6keep.py revert b0 ${t}r ${t}k >> runs/run_keep_$t.log 2>&1
  python -u v6human.py find $t ${t}k > runs/run_hfind_$t.log 2>&1 &
  python -u v6alone.py ${t}k > runs/run_alone_${t}k.log 2>&1 &
  python -u v6cov.py ${t}k > runs/run_cov_${t}k.log 2>&1 &
  python -u v6check.py check ${t}k > runs/run_chk_${t}k.log 2>&1 &
  python -u v6fix.py blind ${t}k b0 > runs/run_blind_${t}k.log 2>&1 &
  BLIND_REP=2 python -u v6fix.py blind ${t}k b0 > runs/run_blind_${t}k_r2.log 2>&1 &
  wait
  echo ALLDONE >> runs/run_keep_$t.log
}
guard h3 &
guard h4 &
wait
echo ALLDONE > runs/run_h34k_done.log
