cd /d/musicclaude/_video_public_20261104
python pub24.py revise8 > qa/log/pub24_rev8.log 2>&1
grep -v "^\[pub" qa/log/pub24_rev8.log | cut -c1-300
for t in g568 g68; do python pub24.py write $t > qa/log/pub24_write_$t.log 2>&1 & done; wait
python pub24.py stats g568 g68
for t in g568 g68; do python pub24.py show $t S02 S05 | grep -v "^==\|安排" | head -30; done
for t in g568 g68; do python film_v8.py still --work op60 --tag $t --sec S02 S05 --at .85 --name 第八轮; python film_v8.py still --work op61 --tag $t --sec S05 --at .85 --name 第八轮; done
for t in g568 g68; do python pub24.py test $t > qa/log/pub24_test_$t.log 2>&1 & done; wait
for t in g568 g68; do echo "##### $t"; grep -E "严格覆盖|整屏人话分|要点 \{|看片盲比|^op6[01] g(6|56) $t 分" qa/log/pub24_test_$t.log | cut -c1-200; grep -E "^op6[01]_g(6|56)_$t " qa/log/pub24_test_$t.log | cut -c1-110; done
