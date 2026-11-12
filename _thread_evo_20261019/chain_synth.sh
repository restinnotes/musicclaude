python -u synth_chain_1021.py gen > runs/SY_gen.log 2>&1
python -u synth_chain_1021.py inv > runs/SY_inv.log 2>&1
python -u synth_chain_1021.py syn > runs/SY_syn.log 2>&1
python -u synth_chain_1021.py c1 > runs/SY_c1.log 2>&1
python -u calib.py SY60 op60 pc_C1_n8_op60_c6_r1_r1,pc_C1_n8_op60_c6_r2_r1,pc_C1_n8_op60_c6_r3_r1,pc_C1_n8_op60_c6_r4_r1,pc_C1_n8_op60_c6_syn_r1 --shuffles 2 --judge judge_line_v6 --workers 4 > runs/SY60j.log 2>&1 &
python -u calib.py SY61 op61 pc_C1_n8_op61_c4_r1_r1,pc_C1_n8_op61_c4_r2_r1,pc_C1_n8_op61_c4_r3_r1,pc_C1_n8_op61_c4_r4_r1,pc_C1_n8_op61_c4_syn_r1 --shuffles 2 --judge judge_line_v6 --workers 4 > runs/SY61j.log 2>&1 &
wait
echo done
