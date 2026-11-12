cd /d/musicclaude/_video_public_20261104
python pub24.py test g68L > qa/log/pub24_test_g68L_b.log 2>&1 &
python pub24.py fixlines g68L g68L2 > qa/log/pub24_fix_g68L2.log 2>&1
python pub24.py test g68L2 > qa/log/pub24_test_g68L2.log 2>&1
wait
python pub24.py gate g68L g68L2
grep -E "op6[01] g(6|56) [XY] 选" qa/log/pub24_test_g68L_b.log qa/log/pub24_test_g68L2.log | cut -c1-260
