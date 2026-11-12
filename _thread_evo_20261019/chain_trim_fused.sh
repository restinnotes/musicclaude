until [ -f runs/f_B0/output.txt ] && [ -f runs/f_g_P0_op60_orig_D3_r2/output.txt ]; do sleep 30; done
python -u trim.py "f_B0,f_g_P0_op60_orig_D3_r2" > runs/trim_fused.log 2>&1
