"""Full-feedback restoration of a near-passing candidate, collect only."""
import json
import os
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import experiment_batch as B

PROMPT = '''下面是同一条线的原版和局部修订版，及两位评委正反位置的四份完整比较。X/Y含义逐份给出。
这些是实际反馈，不先假定所有评委同意任何单一原因。请读完，判断修订方向是否值得保留，并只修接近过线的具体短处。

本次修订的目标是：保住已形成的跨段心理推进，让人平常地讲自己的经历；涉及实质损失时补回转折、决定的来由或珠子的独有落脚处。
写出人物此刻具体想要、顾虑、愿意或不愿意什么，认识可以从这些变化中显出，不站到人物外面整理他的心理。不要为了显得口语就换掉真正的新认识，也不要把每个旧版优势都加回来造成重复。

共同要求：已确立的处境可保留；不能新增他人的举动、心理事实、对白、外部事件、前史、物件；希望和推测不偷换为事实。珠子的画面不变成真的情节。每段2–4条，每条一句，不改分段/Center/珠子。仅replace/delete，最多动8条原条目，未动正文逐字；保留原编号，不在text中抄引用。原标签暂保留，后续独立核对。结尾最终选择不改，不硬造问题已解决。字数尽量不增，但不为压字数丢失实质内容。
评委提的损失是证据，不是必须照办的指令；如确实不能同时改善，允许空edits，如实说明。

【修订版，改动基底】
{REVISED}
【原版，作比较】
{ORIGINAL}
【固定珠子】
{BEADS}
【完整四份比较；每份先标X/Y对应】
{REVIEWS}

只输出JSON：{{"edits":[{{"id":"原编号","op":"replace","text":"改后一句"}}],"note":"判断路线及保留/修复了哪些实质内容，未解决什么"}}。'''

ROOT = B.ROOT / 'runs/_batches/round50_from_r49b'

def prepare(target, revised, base):
    tasks=[]
    for w in B.F.WORKS:
        reviews=[]
        for j in B.F.JUDGES:
            for seat in ('newX','newY'):
                rid=f'v6b3_{w}_{j}_{revised}_vs{base}_{seat}'
                if not B.reviewed(rid):
                    raise ValueError(f'full feedback unread: {rid}')
                reviews.append({'rid':rid, 'X':revised if seat=='newX' else base,
                                'Y':base if seat=='newX' else revised, 'full_raw_response':B.evo.output(rid)})
        msg=PROMPT.format(REVISED=B.V.view(B.V.graph_of(w,revised),ids=True),ORIGINAL=B.V.view(B.V.graph_of(w,base),ids=True),BEADS=B.V.beads(w),REVIEWS=B.json_text(reviews))
        rid=f'sc{target}_{w}_A5'
        B.write_frozen(B.evo.RUNS/rid/'prepared_input.txt',msg)
        tasks.append({'work':w,'rid':rid,'sha256':B.digest(msg)})
    manifest={'target':target,'revised':revised,'base':base,'tasks':tasks,'prompt':PROMPT}
    B.write_frozen(ROOT/f'{target}_manifest.json',B.json_text(manifest))
    return manifest

def collect(target):
    import msvcrt
    import mg_schedule
    os.environ['THREAD_ROUTE']='mimic'
    B.F.configure()
    m=json.loads((ROOT/f'{target}_manifest.json').read_text(encoding='utf-8'))
    with (ROOT/f'{target}_receiver.lock').open('a+') as lock:
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        def one(t):
            msg=(B.evo.RUNS/t['rid']/'prepared_input.txt').read_text(encoding='utf-8')
            assert B.digest(msg)==t['sha256']
            if not B.evo.done(t['rid']):
                try:
                    r=B.evo.call(t['rid'],msg,model=B.evo.G6,meta={'stage':'r50_full_feedback_restore','web':True})
                except mg_schedule.CoolingDown as exc:
                    return {**t,'status':'cooldown','reason':str(exc)}
                if not r:return {**t,'status':'incomplete_inspect_receiver'}
            return {**t,'status':'full_read_required'}
        with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,m['tasks']))
        (ROOT/f'{target}_collection.json').write_text(B.json_text(rows),encoding='utf-8')
        print(B.json_text(rows),flush=True)

if __name__=='__main__':
    import sys
    if sys.argv[1]=='prepare':prepare(*sys.argv[2:5])
    else:collect(sys.argv[2])
