python -u gen.py R2 op60 note D0 6 --workers 3 &
python -u gen.py R2 op61 note D0 6 --workers 3 &
wait
python -u late.py R2 op60 note D0 g_R2_op60_note_D0_r1,g_R2_op60_note_D0_r2,g_R2_op60_note_D0_r3,g_R2_op60_note_D0_r4,g_R2_op60_note_D0_r5,g_R2_op60_note_D0_r6 &
python -u late.py R2 op61 note D0 g_R2_op61_note_D0_r1,g_R2_op61_note_D0_r2,g_R2_op61_note_D0_r3,g_R2_op61_note_D0_r4,g_R2_op61_note_D0_r5,g_R2_op61_note_D0_r6 &
wait
