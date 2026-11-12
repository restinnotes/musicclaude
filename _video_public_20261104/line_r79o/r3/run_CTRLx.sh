#!/bin/bash
# 11-12 用户的怀疑“埋了事件评委就以为不打转”：只插 3–5 件事、其余重复的句子一字不改（CTRLx），看开放评审还报不报打转
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
CTRL_X=1 python r3/ctrl_fwd.py > r3/ctrl_x.log 2>&1 || exit 1
python - <<'PY'
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
for w in ['op60','op61']:
    a=json.load(open(f'r2e/{w}_src.json',encoding='utf-8')); b=json.load(open(f'r2CTRLx/{w}_src.json',encoding='utf-8'))
    ch=[(l0['id'],l0['text'],l1['text']) for s0,s1 in zip(a['sections'],b['sections']) for l0,l1 in zip(s0['lines'],s1['lines']) if l0['text']!=l1['text']]
    print(w,'改了',len(ch),'条')
    for c in ch: print('  ',c[0],'｜原：',c[1],'｜换成：',c[2])
PY
PUB_FRAG_LINEONLY=1 PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68CTRLx prompt_K28b.txt argon "40,5,30,6,3,5" - g68CTRLsk2F r2CTRLx > r3/run_CTRLx.log 2>&1
grep -h "大块\|绝对验收5b\|盲比5" r3/run_CTRLx.log | cut -c1-220
python - <<'PY'
import json,sys,os
sys.stdout.reconfigure(encoding='utf-8')
for w in ['op60','op61']:
  for j in ['g6','g56','argon']:
    q=f'r3/s24/openF3_{w}_{j}_g68CTRLx.json'
    if os.path.exists(q):
      d=json.load(open(q,encoding='utf-8')); print(w,j,':',' ｜ '.join(x['problem'][:40].replace(chr(10),' ') for x in d['issues'][:4]))
PY
