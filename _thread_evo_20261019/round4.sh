python -u gen.py Q1 op60 note D0 4 --workers 4 &
python -u gen.py Q1 op60 note D3 3 --workers 3 &
python -u gen.py Q1 op60 note D4 2 --workers 2 &
python -u gen.py M2 op60 orig D0 6 --workers 3 &
python -u gen.py M3 op60 orig D0 6 --workers 3 &
python -u gen.py P0o op60 orig D0 3 --workers 3 &
wait
D=g_Q1_op60_note_D0_r1,g_Q1_op60_note_D0_r2,g_Q1_op60_note_D0_r3,g_Q1_op60_note_D0_r4
python -u late.py Q1 op60 note D3 $D &
python -u late.py Q1 op60 note D0 $D &
wait
