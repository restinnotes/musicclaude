cd /d/musicclaude/_video_public_20261104
python pub24.py revise7 > qa/log/pub24_rev7.log 2>&1
grep -v "^\[pub" qa/log/pub24_rev7.log | cut -c1-300
for t in g567 g67; do python pub24.py write $t > qa/log/pub24_write_$t.log 2>&1 & done; wait
python pub24.py stats g567 g67
for t in g567 g67; do python pub24.py test $t > qa/log/pub24_test_$t.log 2>&1 & done; wait
for t in g567 g67; do echo "##### $t"; grep -E "严格覆盖|整屏人话分|要点 \{|看片盲比|^op6[01] g(6|56) $t 分" qa/log/pub24_test_$t.log | cut -c1-200; grep -E "^op6[01]_g(6|56)_$t " qa/log/pub24_test_$t.log | cut -c1-110; done
