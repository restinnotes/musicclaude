# 2b fused rewrite once alignments of B0 and D exist
until [ -f evaluations/align/B0.md ] && [ -f evaluations/align/g_P0_op60_orig_D3_r2.md ]; do sleep 30; done
python -u fuse.py op60 B0,g_P0_op60_orig_D3_r2 > runs/fuse1.log 2>&1
