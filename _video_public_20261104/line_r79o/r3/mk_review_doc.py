import json,os,re,sys
sys.stdout.reconfigure(encoding='utf-8')
NAME={'op60':'船歌 Op.60','op61':'幻想波兰舞曲 Op.61'}; JN={'g6':'GPT-6','g56':'GPT-5.6','argon':'Argon'}
sw=json.load(open('r3/s24/swap_r2e.json',encoding='utf-8'))
out=['# 主线一直在用的线，和评审对它的具体意见（11-12 整理）','',
'这条线是 r79o（11-06 定为主线，之后只标了对应珠子、改了两句），屏幕上的大字就是它的原话。下面每首先放线的全文，每段后面跟：互换测试的结果、开放评审里点到这一段的原话。每首最后是三位评审各自排在最前面的几条意见全文。','',
'说明：这条线不是由现在的“骨架 → 选路 → 写线”一次写出来的，它是 11-06 之前的老稿经过多轮局部修改和回补得到的，当时的骨架中间稿没有留全，所以这里看的是线本身。','']
for w in ('op60','op61'):
    d=json.load(open(f'r2e/{w}_src.json',encoding='utf-8')); rev={}
    for j in JN:
        p=f'r3/s24/openF3_{w}_{j}_g68CTRLsk2F.json'
        if os.path.exists(p): rev[j]=json.load(open(p,encoding='utf-8'))
    out+=[f'## {NAME[w]}','',f'**Center：**{d["center"]}','']
    for s in d['sections']:
        out+=[f'### {s["sec"]}（{s.get("bars","")}）']+[f'- {l["text"]}' for l in s['lines']]+['']
        t=[x for x in sw if x['w']==w and x['sec']==s['sec']]
        if t: out+=['互换测试：'+'；'.join(f"{JN[x['judge']]}{'猜对' if x['right'] else '猜成 '+x['pick_sec']}"+(f"，也配得上 {'、'.join(a[2:] for a in x['also'])}" if x['also'] else '，只配本段') for x in t),'']
        for j,r in rev.items():
            for k,x in enumerate(r['issues'],1):
                if re.search(s['sec']+r'(?!\d)', str(x.get('sec',''))): out+=[f"> {JN[j]} 第 {k} 条（{x.get('sec','')}）：{x['problem']}",'']
    out+=[f'### {NAME[w]}：三位评审排在最前面的意见（全文）','']
    for j,r in rev.items():
        for k,x in enumerate(r['issues'][:4],1): out+=[f"{k}. **{JN[j]}**（{x.get('sec','')}）：{x['problem']}",'']
p='D:/musicclaude/_dag2_video_20261104/读稿/主线线稿与评价_1112.md'
open(p,'w',encoding='utf-8').write('\n'.join(out)); print(len('\n'.join(out)),'字')
r=json.load(open('r3/s24/openF3_op60_g6_g68CTRLsk2F.json',encoding='utf-8')); print(list(r.keys())); print(list(r['issues'][0].keys()))
