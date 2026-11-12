import sys,os,socket,subprocess,runpy,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(r'D:\musicclaude');T=P/'_thread_evo_20261019';B=P/'_bead_op61_20261020';O=T/'_codex/param_20261101';TMP=O/'tmp';R=TMP/'cli_legacy'
sys.path[:0]=[str(T),str(B)]
os.environ.pop('WORK',None);os.environ.pop('WORKS_ROOT',None);os.environ['CDV']='2'
blocked=[]
def deny(*args,**kwargs):blocked.append(str(args[:1]));raise RuntimeError('offline process/network denied')
subprocess.run=deny;subprocess.Popen=deny;os.system=deny;socket.socket.connect=deny;socket.create_connection=deny
# All actual write-open attempts must stay within audit artifacts.
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        mode=args[1] or '';flags=args[2] or 0
        if any(x in mode for x in 'wax+') or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
            path=Path(args[0]).resolve()
            if O.resolve() not in path.parents and path!=O.resolve():raise RuntimeError('offline write outside audit artifacts: '+str(path))
sys.addaudithook(audit)
def cli(file,args):
    sys.argv=[str(file)]+args
    try:runpy.run_path(str(file),run_name='__main__')
    except SystemExit as e:assert e.code in [0,None],(file,e.code)
for w in ['op60','op61']:
    cli(B/'gen_A/gen.py',['--work',w,'--corpus24','--render-dir',str(R/w/'N02')])
    cli(B/'chain.py',['render','--work',w,'--render-dir',str(R/w/'N03')])
    cli(T/'center_from_A.py',['--work',w,'--render-dir',str(R/w/'N04a')])
cli(T/'center_dag.py',['render','--work','op60,op61','--render-dir',str(R/'N04')])
checks=[]
for w in ['op60','op61']:
    for generated,actual in [(R/w/'N04a'/f'N04a.{w}.txt',T/'runs'/f'cA_{w}'/'input.txt'),(R/'N04'/f'N04b.{w}.txt',T/'runs'/f'cdw2_{w}'/'input.txt')]+[(R/'N04'/f'N04d.{w}.{jn}.txt',T/'runs'/f'cdf2_{w}_{jn}'/'input.txt') for jn in ['gpt6','gpt56']]:
        assert generated.read_text(encoding='utf-8')==actual.read_text(encoding='utf-8'),(generated,actual)
        checks.append(str(generated))
for jn in ['gpt6','gpt56']:
    for k in [1,2]:
        generated=R/'N04'/f'N04c.{jn}.{k}.txt';actual=T/'runs'/f'cds2_{jn}_{k}'/'input.txt'
        assert generated.read_text(encoding='utf-8')==actual.read_text(encoding='utf-8'),(generated,actual)
        checks.append(str(generated))
assert not blocked,blocked
report={'rendered_text_files':len(list(R.rglob('*.txt'))),'N04_cli_exact_against_historical':len(checks),'network_or_process_attempts':blocked,'write_boundary':'audit-hook enforced: only _codex/param_20261101','root':str(R)}
(O/'cli_test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
