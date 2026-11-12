python -u late.py P0 op60 orig D0 r1_P0_op60_D0_1,r1_P0_op60_D0_2,r1_P0_op60_D0_3,g_P0_op60_orig_D0_r1,g_P0_op60_orig_D0_r2,g_P0_op60_orig_D0_r3 &
python -u late.py P0 op60 orig D3 g_P0_op60_orig_D0_r1,g_P0_op60_orig_D0_r2,g_P0_op60_orig_D0_r3 &
python -u late.py P0 op60 orig D4 g_P0_op60_orig_D0_r1,g_P0_op60_orig_D0_r2,g_P0_op60_orig_D0_r3 &
python -u late.py P1 op60 orig D3 g_P1_op60_orig_D0_r1,g_P1_op60_orig_D0_r2,g_P1_op60_orig_D0_r3 &
python -u gen.py M1 op60 orig D0 3 --workers 3 &
python -u gen.py M2 op60 orig D0 3 --workers 3 &
python -u gen.py M3 op60 orig D0 3 --workers 3 &
python -u gen.py P0 op60 note D0 3 --workers 3 &
wait
python -u gen.py P0 op60 ranges D0 6 --workers 3
