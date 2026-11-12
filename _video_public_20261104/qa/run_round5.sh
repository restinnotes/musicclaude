cd /d/musicclaude/_video_public_20261104
python pub24.py revise3 g56:g564s g6:g64s > qa/log/pub24_rev5.log 2>&1
grep -v "^\[pub" qa/log/pub24_rev5.log | cut -c1-300
for t in g564s3 g64s3; do python pub24.py write $t > qa/log/pub24_write_$t.log 2>&1 & done; wait
python pub24.py stats g564s3 g64s3
for t in g564s3 g64s3; do python pub24.py test $t > qa/log/pub24_test_$t.log 2>&1 & done; wait
for t in g564s3 g64s3; do echo "##### $t"; grep -E "整屏人话分|要点 \{|看片盲比|^op6[01] g(6|56) $t 分" qa/log/pub24_test_$t.log | cut -c1-200; grep -E "^op6[01]_g(6|56)_$t " qa/log/pub24_test_$t.log | cut -c1-110; done
