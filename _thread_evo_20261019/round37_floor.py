import os,sys,json
os.environ.setdefault('JV','2')
sys.path.insert(0,'.')
import screen_flow as F
F.configure()
tag,base=sys.argv[1:3]
for k in ('coverage','alone'):
    print(k,json.dumps(F.run_floor(tag,base,k),ensure_ascii=False)[:600],flush=True)
print('all',json.dumps(F.floor_state(tag,base),ensure_ascii=False)[:600])
