python -u gen.py R2 op61 note D0 3 --workers 3 &
python -u gen.py P0 op61 orig D0 6 --workers 1
python -u late.py P0 op61 orig D0 g_P0_op61_orig_D0_r1,g_P0_op61_orig_D0_r2,g_P0_op61_orig_D0_r3,g_P0_op61_orig_D0_r4,g_P0_op61_orig_D0_r5,g_P0_op61_orig_D0_r6
wait
