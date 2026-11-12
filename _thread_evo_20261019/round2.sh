python -u gen.py P0 op60 ranges D0 3 --workers 3 &
python -u gen.py P1 op60 orig D0 3 --workers 3 &
python -u gen.py P2 op60 orig D0 3 --workers 3 &
python -u gen.py P3 op60 orig D0 3 --workers 3 &
wait
