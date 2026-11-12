cd /d/musicclaude/_video_public_20261104
for t in g64s g64f g564s g564f; do python pub24.py write $t > qa/log/pub24_write_$t.log 2>&1 & done; wait
python pub24.py stats g64s g64f g564s g564f
for t in g64s g64f g564s g564f; do python pub24.py test $t > qa/log/pub24_test_$t.log 2>&1 & done; wait
for t in g64s g64f g564s g564f; do echo "##### $t"; grep -E "整屏人话分|要点 \{|看片盲比|^op6[01] g[0-9]+ \{|^op6[01] g(6|56) $t 分" qa/log/pub24_test_$t.log | cut -c1-240; grep -E "^op6[01]_g(6|56)_$t " qa/log/pub24_test_$t.log | cut -c1-160; done
