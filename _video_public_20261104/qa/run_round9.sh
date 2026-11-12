cd /d/musicclaude/_video_public_20261104
python -c "
import sys; sys.argv=['x']
import pub24
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(4) as ex: list(ex.map(pub24.lang_all, [(w,j,'w23') for w in pub24.WORKS for j in pub24.JUDGES]))
" > qa/log/pub24_langall_w23.log 2>&1 &
python pub24.py revise3 g6:g68 g56:g568 > qa/log/pub24_rev9.log 2>&1
grep -v "^\[pub" qa/log/pub24_rev9.log | cut -c1-300
for t in g683 g5683; do python pub24.py write $t > qa/log/pub24_write_$t.log 2>&1 & done; wait
python pub24.py stats g683 g5683
for t in g683 g5683; do python pub24.py show $t S05 | grep -v "^==\|安排" | head -12; done
for t in g683 g5683; do python pub24.py test $t > qa/log/pub24_test_$t.log 2>&1 & done; wait
grep "整屏人话分" qa/log/pub24_langall_w23.log
for t in g683 g5683; do echo "##### $t"; grep -E "严格覆盖|整屏人话分|要点 \{|看片盲比|^op6[01] g(6|56) $t 分" qa/log/pub24_test_$t.log | cut -c1-200; grep -E "^op6[01]_g(6|56)_$t " qa/log/pub24_test_$t.log | cut -c1-110; done
