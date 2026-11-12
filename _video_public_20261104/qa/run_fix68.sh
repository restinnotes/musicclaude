cd /d/musicclaude/_video_public_20261104
python pub24.py fixlines g68 g68L > qa/log/pub24_fix_g68L.log 2>&1
grep -v "^\[pub" qa/log/pub24_fix_g68L.log
python - <<'P'
import json,sys; sys.stdout.reconfigure(encoding='utf-8')
for w in ('op60','op61'):
    a=json.load(open(f'r3/s24/screen_{w}_g68.json',encoding='utf-8')); b=json.load(open(f'r3/s24/screen_{w}_g68L.json',encoding='utf-8'))
    for s,t in zip(a['sections'],b['sections']):
        for x,y in zip([x for x in s['rows'] if x['kind']=='line'],[x for x in t['rows'] if x['kind']=='line']):
            if x['text']!=y['text']: print(w,s['sec'],x['text'],'→',y['text'])
P
python pub24.py test g68L > qa/log/pub24_test_g68L.log 2>&1
python pub24.py gate g68L
