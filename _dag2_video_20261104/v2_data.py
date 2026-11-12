"""Recover original bead edges and explicit local windows without rewriting prose."""
import argparse, difflib, json, os, re, sys
from pathlib import Path
from dag2 import ROOT, EVO, read, write, sha, parse

CANON = {'op60': EVO/'inputs/pkg/03_Bead机器可读',
         'op61': Path('D:/musicclaude/_bead_op61_20261020/deliverable/03_Bead机器可读')}
RANGE = re.compile(r'(?:第|约|m\.?|mm\.?)?\s*(\d{1,3})(?:[–—\-至到](\d{1,3}))?\s*小节')
# Visible copy alone loses these location phrases. Original bytes and offsets remain in plans.
LOCATOR = re.compile(r'(?:尤其在|临近|接近|约在|约到|到了|到|在|从|约)?(?:第)?\s*\d{1,3}(?:[–—\-至到]\d{1,3})?(?:、\d{1,3}(?:[–—\-至到]\d{1,3})?)*\s*小节(?:的?交界|附近|左右|开始|起|以后|之后|之间|里)?[，、：]?|(?:mm?\.)\s*\d{1,3}(?:[–—\-]\d{1,3})?[，、：]?|到最后[一二三四五六七八九十\d]+小节[，：]?|几小节|第\s*\d+(?:分(?:钟)?)\d*(?:秒)?[，、：]?')

def display(text):
    removed=set()
    # This purely locational afterthought otherwise leaves "主题要才真正站稳"
    # after number removal. Omit the full locator clause, preserving the preceding
    # experience and its existing final punctuation. No replacement prose is added.
    for m in re.finditer(r'，主题要到第\d{1,3}小节才真正站稳',text):
        removed.update(range(m.start(),m.end()))
    for m in LOCATOR.finditer(text): removed.update(range(m.start(), m.end()))
    for m in re.finditer(r'（[^（）]*）|\([^()]*\)',text):
        if all(i in removed or text[i].isspace() for i in range(m.start()+1,m.end()-1)):
            removed.update(range(m.start(),m.end()))
    indices=[i for i in range(len(text)) if i not in removed]
    return ''.join(text[i] for i in indices), indices

def first_range(where, fallback):
    # Only the leading declared range is a scope; later ranges can be historical comparisons.
    parts=where.split('；');s=parts[0]
    m=re.search(r'(\d{1,3})(?:[–—\-至到](\d{1,3}))?',s)
    if not m:return fallback
    a=int(m[1]); b=int(m[2] or a)
    if '→' in s:
        nums=list(map(int,re.findall(r'\d+',s)));b=max(nums)
    for part in parts[1:]:
        mm=re.match(r'\s*(?:约|第|mm?\.)?(\d{1,3})(?:[–—\-至到](\d{1,3}))?',part)
        if not mm:break
        a=min(a,int(mm[1]));b=max(b,int(mm[2] or mm[1]))
    # An isolated "starts at" is not a one-measure scope.
    if re.search(r'\d+起',s):return fallback
    return a,b

def timing_call():
    inputs={}
    for w in CANON:
        src=read(ROOT/f'input/{w}.json');graph=read(ROOT/f'plans/{w}_v2_graph.json');rows=[]
        for s,g in zip(src['segments'],graph['segments']):
            for n in g['nodes']:
                if RANGE.search(n['text']) or ('；' in n['where'] and re.search(r'\d',n['where'])) or '末尾' in n['where']:
                    rows.append({'id':n['id'],'section_bars':s['bars'],'where':n['where'],'text':n['text']})
        inputs[w]=rows
    msg='''为视频制作局部文字出现的范围。只标注，不改写任何正文。输入每颗珠子有原始文字、作者已有定位where和当前音乐段范围section_bars。
请将每颗正文切为一个或几个连续块，每块quote必须逐字照抄，顺序拼接严格等于该颗text（包括全部标点），不要重复漏字。bars:[起始,结束]为含首尾的小节范围，只能使用给定定位/正文支持的范围，并裁在section_bars之内。没有更细依据的文字用完整段范围或where的整体范围；不要为制造动画猜时间。
特别注意：1.一句话里提到开头的某一小节，后面描述却持续多小节，不能把整段错误限为那个单独小节；2.有148–151；152–167；168–180这样的声明时要覆盖全部，不只取第一个范围；3.同一句中的先后动作可以以连续子句分块，各自时间可重叠，过渡不要为了精确而猜；4.历史对照的小节不属于当前出现时刻；5.末尾几小节可保持宽泛，除非正文明确给出范围；6.未定位的心理解释不能被强行缩成一个音或一小节。只输出JSON：{"op60":[{"id":"Sxx-Bx","chunks":[{"quote":"连续原文","bars":[1,3],"basis":"给定定位的依据"}]}],"op61":[...]}。全部输入都处理。输入：
'''+json.dumps(inputs,ensure_ascii=False)
    folder=ROOT/'runs/v2_local_timing';folder.mkdir(exist_ok=True)
    inp=folder/'prepared_input.txt'
    if inp.exists():assert inp.read_text(encoding='utf8')==msg
    else:inp.write_text(msg,encoding='utf8')
    os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo
    ans=evo.call('dag2_20261104_v2_local_timing',msg,model=evo.G6,meta={'stage':'DAG2-local-text-timing','web':True})
    if not ans:raise RuntimeError('Timing response incomplete; inspect existing run')
    (folder/'output.txt').write_text(ans,encoding='utf8');result=parse(ans);write(folder/'parsed.json',result)
    apply_timing(result)

def apply_timing(result):
    for w,rows in result.items():
        src=read(ROOT/f'input/{w}.json');graph=read(ROOT/f'plans/{w}_v2_graph.json');music=read(ROOT/f'input/{w}_music.json');times=dict(music['bars']);byid={n['id']:(s,n) for s in graph['segments'] for n in s['nodes']}
        expected={r['id'] for r in json.loads((ROOT/'runs/v2_local_timing/prepared_input.txt').read_text(encoding='utf8').split('输入：\n')[-1])[w]}
        assert {r['id'] for r in rows}==expected
        for row in rows:
            s,n=byid[row['id']];assert ''.join(ch['quote'] for ch in row['chunks'])==n['text'],(w,row['id'],'not an exact partition')
            ns=next(z for z in src['segments'] if z['sec']==s['sec']);sa,sb=first_range(ns['bars'],(0,0));chunks=[];offset=0
            for ch in row['chunks']:
                a,b=ch['bars'];assert sa<=a<=b<=sb,(w,row['id'],ch)
                tw=[times[a],times.get(b+1,music['dur'])];shown,indices=display(ch['quote'])
                chunks.append({'start':offset,'end':offset+len(ch['quote']),'text':ch['quote'],'display':shown,'original_indices':[offset+i for i in indices],'window':tw,'bars':[a,b],'basis':ch['basis']})
                offset+=len(ch['quote'])
            n['chunks']=chunks;n['window']=[min(c['window'][0] for c in chunks),max(c['window'][1] for c in chunks)]
        # Refresh untouched broad nodes as well when the display-only locator policy changes.
        for sg in graph['segments']:
            for n in sg['nodes']:
                for ch in n['chunks']:
                    shown,indices=display(ch['text']);ch['display']=shown;ch['original_indices']=[ch['start']+i for i in indices]
        graph['timing_model_output_sha256']=sha(ROOT/'runs/v2_local_timing/output.txt');write(ROOT/f'plans/{w}_v2_graph.json',graph)
    print('Exact local timing partitions compiled',flush=True)

def compile_work(w):
    src=read(ROOT/f'input/{w}.json');music=read(ROOT/f'input/{w}_music.json')
    times=dict(music['bars']);dur=music['dur'];segments=[];sources={}
    def interval(a,b,lo,hi):
        return [max(lo,times.get(a,lo)),min(hi,times.get(b+1,dur))]
    for si,s in enumerate(src['segments']):
        nums=list(map(int,re.findall(r'\d+',s['bars'])));a,b=min(nums),max(nums)
        lo=times[a];hi=times[int(re.findall(r'\d+',src['segments'][si+1]['bars'])[0])] if si+1<len(src['segments']) else dur
        p=CANON[w]/(s['sec']+'.json');original=read(p);sources[str(p)]=sha(p)
        nodes=[];idmap={};used=set()
        for bead in s['beads']:
            matches=sorted([(difflib.SequenceMatcher(None,bead['text'],x['text'],autojunk=False).ratio(),x) for x in original['beads']],key=lambda x:x[0],reverse=True)
            score,old=matches[0]
            assert score>=.4 and score-matches[1][0]>.2,(w,bead['id'],'ambiguous original identity')
            assert old['id'] not in used;used.add(old['id']);idmap[old['id']]=bead['id']
            ba,bb=first_range(bead['where'],(a,b));ba=max(a,ba);bb=min(b,bb)
            win=interval(ba,bb,lo,hi)
            assert win[1]>win[0],(w,bead,win)
            # Split only at an explicit, non-retrospective locator. Unlocated words keep the broad bead window.
            text=bead['text'];markers=[]
            for m in RANGE.finditer(text):
                ma,mb=int(m[1]),int(m[2] or m[1])
                if ba<=ma<=mb<=bb:
                    start=m.start()
                    while start>0 and text[start-1] not in '。；！？':start-=1
                    markers.append((start,ma,mb))
            markers=sorted({(x[0],x[1],x[2]) for x in markers})
            # Multiple locators in one sentence cannot safely retime that sentence.
            unique=[]
            for m in markers:
                if sum(x[0]==m[0] for x in markers)==1:unique.append(m)
            cuts=sorted({0,len(text),*(x[0] for x in unique)})
            chunks=[]
            for start,end in zip(cuts,cuts[1:]):
                if start==end:continue
                marker=next((x for x in unique if x[0]==start),None)
                tw=interval(marker[1],marker[2],*win) if marker else win
                shown,indices=display(text[start:end])
                chunks.append({'start':start,'end':end,'text':text[start:end],'display':shown,'original_indices':[start+i for i in indices], 'window':tw,'basis':'explicit sentence locator' if marker else 'declared bead scope'})
            assert ''.join(c['text'] for c in chunks)==text
            nodes.append({**bead,'original_id':old['id'],'role':old['role'],'identity_score':score,'window':win,'chunks':chunks})
        edges=[];omitted=[]
        for edge in original.get('relations',[]):
            if edge['a'] in idmap and edge['b'] in idmap:edges.append({**edge,'a':idmap[edge['a']],'b':idmap[edge['b']]})
            else:omitted.append(edge)
        segments.append({'sec':s['sec'],'window':[lo,hi],'nodes':nodes,'edges':edges,'edges_with_absent_original_node':omitted})
    out={'work':w,'input_sha256':sha(ROOT/f'input/{w}.json'),'canonical_sha256':sources,'segments':segments,
         'visible_copy_policy':'remove location phrases only; original text preserved with character-index map',
         'edge_policy':'original direct edges only; no inferred bridge through an omitted node'}
    write(ROOT/f'plans/{w}_v2_graph.json',out)
    print(w,'nodes',sum(len(s['nodes']) for s in segments),'edges',sum(len(s['edges']) for s in segments),'local chunks',sum(c['basis'].startswith('explicit') for s in segments for n in s['nodes'] for c in n['chunks']),flush=True)

def outline_call():
    inputs={}
    for w in CANON:
        src=read(ROOT/f'input/{w}.json');old=read(ROOT/f'plans/{w}_v1.json')
        inputs[w]={'segments':[{'sec':s['sec'],'lines':s['items']} for s in src['segments']],'phases':old['phases']}
    msg='''给音乐视频右栏做一次极简提纲压缩。旧标题过长，挤满侧栏。按Op52方式，过去阶段只留一行，当前阶段展开，未来故事不显示。主区保留完整正文。
不改现有阶段分组。每个阶段标题和每段短语分别压缩到5–12汉字，必要可到14字；从对应原句连续逐字摘取，不拼接，不切掉否定词/条件而反转意思。保留足够语义，读起来是短语。不要加入小节、时间、解释、角色名、标题“这一路”。阶段标题只能用已有阶段所提供line_id的原话；段短语可选该段任一句。输出一次JSON，按op60/op61键：各含phases:[{title,line_id,sections}]与outline:[{sec,label,line_id}]。这些标签共同用于三种折叠密度：极简只展开当前短语，适中当前+上一短语，展开显示当前阶段已经走过的短语。不要提供三个重复正文版本。输入：
'''+json.dumps(inputs,ensure_ascii=False)
    folder=ROOT/'runs/v2_rail_compact';folder.mkdir(parents=True,exist_ok=True)
    inp=folder/'prepared_input.txt'
    if inp.exists():assert inp.read_text(encoding='utf8')==msg
    else:inp.write_text(msg,encoding='utf8')
    os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo
    answer=evo.call('dag2_20261104_v2_rail_compact',msg,model=evo.G6,meta={'stage':'DAG2-compact-outline','web':True})
    if not answer:raise RuntimeError('outline request did not complete; inspect existing run')
    (folder/'output.txt').write_text(answer,encoding='utf8');result=parse(answer)
    for w,plan in result.items():
        src=read(ROOT/f'input/{w}.json');old=read(ROOT/f'plans/{w}_v1.json');lookup={i['id']:i['text'] for s in src['segments'] for i in s['items']}
        assert [p['sections'] for p in plan['phases']]==[p['sections'] for p in old['phases']]
        assert [o['sec'] for o in plan['outline']]==[s['sec'] for s in src['segments']]
        for item,key in [(p,'title') for p in plan['phases']]+[(p,'label') for p in plan['outline']]:
            assert item[key] in lookup[item['line_id']] and len(item[key])<=16,item
        write(ROOT/f'plans/{w}_v2_rail.json',plan)
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');p=argparse.ArgumentParser();p.add_argument('command',choices=['compile','outline','timing']);a=p.parse_args()
    if a.command=='compile':
        for w in CANON:compile_work(w)
    elif a.command=='outline':outline_call()
    else:timing_call()
