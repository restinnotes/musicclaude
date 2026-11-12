"""Collect unchanged GPT open reviews or one held-out Gemini anchor comparison."""
import argparse
import msvcrt
import os
from concurrent.futures import ThreadPoolExecutor
import continue_r80 as C
import round50_measure as M
import experiment_batch as B
import mg_schedule


def collect(action, tag, base):
    os.environ['THREAD_ROUTE']='gpt3s'
    B.F.configure()
    if action=='open':
        jobs=[(rid,msg,j) for rid,msg,j in M.jobs('open',tag,base) if j!='gem']
    else:
        jobs=[(rid.replace('v6b3_','ho_',1).replace('_g6_','_gem_',1),msg,'gem')
              for rid,msg,j in M.jobs('fair',tag,base) if j=='g6']
    lockfile=C.BATCH/f'{action}_{tag}_receiver.lock'
    with lockfile.open('a+b') as lock:
        if lock.seek(0,2)==0:lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        def one(job):
            rid,msg,j=job;p=B.evo.RUNS/rid
            B.write_frozen(p/'prepared_input.txt',msg)
            if (p/'input.txt').exists():assert (p/'input.txt').read_text(encoding='utf-8')==msg,rid
            if not B.evo.done(rid):
                s=mg_schedule.status()
                if s['cooling'] and s.get('cooldown_kind')=='suspicious_behavior':mg_schedule.check()
                result=(B.evo.call_gemini_direct(rid,msg,meta={'stage':'heldout','web':False})
                        if j=='gem' else B.evo.call(rid,msg,model=B.V.JUDGES[j],meta={'stage':'r50-open','web':True}))
                if not result:return {'rid':rid,'status':'incomplete_inspect_receiver'}
            return {'rid':rid,'status':'full_read_required','output_sha256':B.digest(B.evo.output(rid))}
        with ThreadPoolExecutor(max_workers=4 if action=='open' else 2) as pool:
            rows=list(pool.map(one,jobs))
        C.write(C.BATCH/f'{action}_{tag}_vs{base}_result.json',rows)
        print(B.json_text(rows),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['open','heldout']);p.add_argument('tag');p.add_argument('--base',default='r49b')
    a=p.parse_args();collect(a.action,a.tag,a.base)
