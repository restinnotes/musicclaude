python -u gen.py P0 op61 orig D0 6 --workers 3 &
python -u gen.py Q1 op61 note D0 6 --workers 3 &
wait
python -u late.py P0 op61 orig D0 g_P0_op61_orig_D0_r1,g_P0_op61_orig_D0_r2,g_P0_op61_orig_D0_r3,g_P0_op61_orig_D0_r4,g_P0_op61_orig_D0_r5,g_P0_op61_orig_D0_r6 &
python -u late.py Q1 op61 note D0 g_Q1_op61_note_D0_r4,g_Q1_op61_note_D0_r5,g_Q1_op61_note_D0_r6 &
wait
