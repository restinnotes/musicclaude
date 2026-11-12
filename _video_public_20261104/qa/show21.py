import json,glob,sys,os
sys.stdout.reconfigure(encoding='utf-8')
for p in sorted(glob.glob('r3/audit21/*.json')):
    r=json.load(open(p,encoding='utf-8')); print('==',os.path.basename(p)); n=0
    for s in r['sections']:
        for f in s.get('fine',[]):
            if f.get('screen')!='在' and f.get('matter')=='大' and n<7:
                print(' ',s['sec'],f.get('carrier'),'|',f.get('quote'),'=> 救:',f.get('fix')); n+=1
    if 'g6' in p:
        n=0
        for s in r['sections']:
            for l in s.get('lines',[])[:1]:
                if n<7: print('   线',s['sec'],l.get('where'),'要点:',l.get('point'),'| 废:',l.get('waste'),'| 留:',l.get('keep')); n+=1
