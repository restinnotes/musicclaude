#!/bin/sh
# Op.52 上游：等分段 -> A 稿 -> 收集。每步的日志在 qa/log/。
cd /d/musicclaude/_video_public_20261104
T=/d/musicclaude/_thread_evo_20261019
for i in $(seq 1 120); do [ -f $T/works/op52/segmentation.json ] && break; sleep 30; done
[ -f $T/works/op52/segmentation.json ] || { echo 分段没回来; tail -n 3 qa/log/op52_N01b.log; exit 1; }
python - <<'EOF'
import json
p='D:/musicclaude/_thread_evo_20261019/works/op52/'
s=json.load(open(p+'segmentation.json',encoding='utf-8')); w=json.load(open(p+'work.json',encoding='utf-8'))
src=s['source'].get('author_or_institution') or '公开分析'
w['segmentation_source']=src[:30]; w['segmentation_source_note']=str(s['source'].get('reason',''))[:200]
json.dump(w,open(p+'work.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('分段',len(s['segments']),s['boundaries'],src[:60])
print([x['label'] for x in s['segments']])
EOF
python op52_a.py gpt > qa/log/op52_N02_gpt.log 2>&1 &
G=$!
python op52_a.py other > qa/log/op52_N02_other.log 2>&1 &
O=$!
wait $G; wait $O
tail -n 2 qa/log/op52_N02_gpt.log | cut -c1-400
tail -n 2 qa/log/op52_N02_other.log | cut -c1-1200
