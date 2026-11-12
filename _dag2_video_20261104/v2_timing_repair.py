"""Focused model repair; preserve the first reply and support disjoint local windows."""
import json,os,sys
from dag2 import ROOT,EVO,read,write,parse,sha
from v2_data import apply_timing,display

def apply(result):
    base=read(ROOT/'runs/v2_local_timing/parsed.json')
    for w,rows in result.items():
        ids={r['id'] for r in rows};base[w]=[r for r in base[w] if r['id'] not in ids]+rows
        # apply_timing expects one outer range. Actual disjoint windows are restored below.
    normalized=json.loads(json.dumps(base))
    for rows in normalized.values():
        for r in rows:
            for ch in r['chunks']:
                if 'ranges' in ch:ch['bars']=[min(v[0] for v in ch['ranges']),max(v[1] for v in ch['ranges'])]
    apply_timing(normalized)
    for w,rows in base.items():
        p=ROOT/f'plans/{w}_v2_graph.json';graph=read(p);music=read(ROOT/f'input/{w}_music.json');times=dict(music['bars']);nodes={n['id']:n for s in graph['segments'] for n in s['nodes']}
        for r in rows:
            for ch,original in zip(nodes[r['id']]['chunks'],r['chunks']):
                if 'ranges' in original:
                    ch['windows']=[[times[a],times.get(b+1,music['dur'])] for a,b in original['ranges']];ch['ranges']=original['ranges']
        graph['timing_repair_output_sha256']=sha(ROOT/'runs/v2_local_timing_repair/output.txt');write(p,graph)
    write(ROOT/'runs/v2_local_timing_repair/applied.json',base);print('Scoped timing repair compiled',flush=True)

def main():
    ids={'op60':['S03-B3','S04-B2','S09-B1'],'op61':['S05-B4','S07-B1','S13-B5']};data={}
    for w,selected in ids.items():
        src=read(ROOT/f'input/{w}.json');before={r['id']:r for r in read(ROOT/'runs/v2_local_timing/parsed.json')[w]};data[w]=[]
        for s in src['segments']:
            for b in s['beads']:
                if b['id'] in selected:data[w].append({**b,'section_bars':s['bars'],'previous':before[b['id']]})
    msg='''修补局部时间标注的6颗珠子，不改正文。每颗chunks按quote逐字拼接必须等于输入text，不漏标点。输出同样op60/op61列表结构，全部6颗处理。一般块用bars:[a,b]；同一段文字在不连续的两段出现时可改用ranges:[[a,b],[c,d]]，不要把句子拆成只有数字或定位的空壳。依据：
1 Op60 S03-B3：末尾思绪/谈话结/顺畅受阻是where17–23的整体理解，不能因前句约20–22小节而一并缩窄；具体绕远/滞留句仍可20–22。
2 Op60 S04-B2：原珠子审稿关系图明确“想把最深情意说出口，喉咙颤抖哽咽；右手高处悬停左手仍推着走”对应约30–34；不要随前一句32附近缩成单一32。32附近的金光描述可保留其明确点位，34的安静单独。
3 Op60 S09-B1：“整段像两个人对视到呼吸都停了”是整体72–77，不应只76–77；具体76–77颤音仍局部。
4 Op61 S05-B4：“尤其在128–129、139–144小节附近，旋律几乎单独露出来...”是同一句体验对应两个不连续片段，使用单块ranges:[[128,129],[139,144]]，不可切成“尤其在128–129、”使第一段只有定位没有实质。
5 Op61 S07-B1：where是182附近，惊醒/寒风/身体反应紧接该事件，不可在181（事件尚未发生时）提前呈现。请依原定位处理，不把心理反应编成贯穿全段181–205的状态。
6 Op61 S13-B5：where虽写末尾几小节，但不能因宽泛而从254一直显示。现有对齐音符及小节表给出具体结尾事件证据：286开始688.04秒有一记轻和弦（音高44/51/56/60），287开始689.48秒另一记轻的低区和弦（32/51/60），288开始695.06秒最后高音和弦（包含80/92），总录音698.781秒。这与正文“两记低处轻声，随后高处亮光”对应。按这个已有证据在286–288的尾部组织，最后高音那句可288；心理比较总结保持结尾整体。不要展示具体秒数，这是幕后数据。
只输出JSON，chunks每块含quote、bars或ranges、basis。输入：
'''+json.dumps(data,ensure_ascii=False)
    folder=ROOT/'runs/v2_local_timing_repair';folder.mkdir(exist_ok=True);inp=folder/'prepared_input.txt'
    if inp.exists():assert inp.read_text(encoding='utf8')==msg
    else:inp.write_text(msg,encoding='utf8')
    os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo
    ans=evo.call('dag2_20261104_v2_local_timing_repair',msg,model=evo.G6,meta={'stage':'DAG2-targeted-timing-repair','web':True})
    if not ans:raise RuntimeError('No complete timing repair')
    (folder/'output.txt').write_text(ans,encoding='utf8');result=parse(ans);write(folder/'parsed.json',result);apply(result)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');main()
