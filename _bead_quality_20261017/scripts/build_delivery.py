"""Assemble the human-readable delivery; no model calls and no source rewrites."""
from pathlib import Path
import json,re,hashlib,html
R=Path(__file__).resolve().parents[1]
def read(p): return (R/p).read_text(encoding='utf-8-sig')
def j(p): return json.loads(read(p))
def put(p,s):
    q=R/p;q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(s.rstrip()+'\n',encoding='utf-8',newline='\n')
def clean_old(s):
    # Only presentation markup/section wrappers; paragraph wording is unchanged.
    s=re.sub(r'<[^>]*>','',s)
    s=re.sub(r'^#{1,3}\s*②[^\n]*\n','',s,flags=re.M)
    return '\n\n'.join(x.strip() for x in s.split('\n\n') if x.strip())
def cell(s):return s.replace('|','\\|').replace('\n\n','<br><br>').replace('\n','<br>')
def norm(s):return re.sub(r'[*`_]','',s).replace('\r\n','\n')
def source_link(uid):
    sid=uid.rsplit('-U',1)[0]
    return f'[{uid}](sources/{sid}.md)'
def main():
    beads=j('editorial/candidate_beads.json'); cards=j('editorial/evidence_cards.json')
    units=j('sources/units.json'); segs=j('sources/structure.json')['frozen_segments']
    choices=j('editorial/old_excerpt_choices.json')
    old=read('baseline_package/out/READER_v3.md')
    oldparts={m[1]:m[2].strip() for m in re.finditer(r'^## (S\d\d)\b[^\n]*\n(.*?)(?=^## S\d\d\b|\Z)',old,re.M|re.S)}
    assert len(oldparts)==14
    out=['# 肖邦《船歌》Op.60 · 十四颗珠子','',
         '沿用 PTNA／朝山十四段。这里的情景和人物动作是聆听比喻，并非作曲家生平或唯一的演奏解释。正文由本轮主编辑依据正式原A、受控试写和事实复核逐段整合；不是某个外部模型一次生成的原样输出。','',
         '可按音乐顺序读；想先看差异，读 S02、S07、S13。来源与前后对照见 [BEAD_CONTENT_REVIEW.md](BEAD_CONTENT_REVIEW.md)。','']
    review=['# 原A → 上一版 → 新版：直接读内容','',
        '新版栏是全部十四颗最终正文，未用摘要替代。原A栏是经回原文核对的短引句；上一版栏是选取的完整段落，不声称展示全部旧稿。每段都链接完整旧珠子，避免把删掉的内容藏起来。旧稿已有的好句也保留展示。','',
        '**读法：**先横向读 S02、S07、S13，再读其余段。改善与损失是主编辑的内容判断，没有模型投票或质量分数。音乐结构、小节边界不变；原A来自正式30份，历史V2A只作独立表达对照。','',
        '正式稿是主编辑选材、组织与精编的结果；外部模型真实输出及同输入条件见 [模型与方法实测](MODEL_METHOD_COMPARISON.md)。','']
    internal=['# 珠子来源与取舍','',
        '这是精简的内部账本。adopted_sources 是支持最终正文的来源清单；alternative/quarantine 仅作留档，绝不合并统计为采用。单元的跨段范围不因进入某一颗珠子而被改成本段。','',
        '正文在 [READER.md](READER.md)，连续原句在 [内容对照](BEAD_CONTENT_REVIEW.md)，所有完整相关原文及继承标题在 [生产上下文](production_context/CONTEXT_REPAIR.json)。','']
    plainold=['# 上一版读者稿（仅移除显示标签）','',
        '来自交付包 READER_v3.md。移除 box/text/WritingBlock 标签及②节包装行，未改段落文字。原始文件见 [存档](baseline_package/out/READER_v3.md)。','']
    trace=[]
    for b,(rng,label) in zip(beads,segs):
        sid=b['segment']; card=cards[sid]; body=b['body'];title=b['title']
        assert sid in oldparts
        assert all(u in units for u in b['sources'])
        out += [f'## {sid} · 第{rng.replace("-","–")}小节｜{title}','',body,'']
        full=clean_old(oldparts[sid])
        plainold += [f'## {sid} · {rng}','',full,'']
        paras=full.split('\n\n'); selected=[]
        for needle in choices[sid]:
            hits=[p for p in paras if needle in p]
            assert len(hits)==1,(sid,needle,len(hits))
            selected.append(hits[0])
        quotes=[]
        for uid,q in card['quotes']:
            raw=units[uid]['text']
            assert norm(q) in norm(raw),(sid,uid,q)
            quotes.append(f'“{q}”\n\n{source_link(uid)}')
        review += [f'## {sid} · 第{rng.replace("-","–")}小节｜{title}','',
                   '| 原A中值得保留的文字 | 上一版：完整段落摘选 | 新版：完整正文 |',
                   '|---|---|---|',
                   '| '+ ' | '.join(cell(s) for s in ['\n\n'.join(quotes),'\n\n'.join(selected),body])+' |','',
                   '**具体变化与代价：**'+card['change'],'',
                   f'[上一版该段完整珠子](baseline_package/beads/STEP4_{sid}.md) · [本段完整生产Pool](production_context/pools/{sid}.txt)','']
        internal += [f'## {sid} · {rng}｜{title}','',card['change'],'',
                     '**正文采用：**'+ '、'.join(source_link(u) for u in b['sources'])+'。','',
                     f'完整原文与原范围：[生产Pool](production_context/pools/{sid}.txt)。','']
        if (R/f'audits/facts_{sid}.txt').exists():
            internal += [f'位置／事实边界：[facts_{sid}.txt](audits/facts_{sid}.txt)。','']
        trace.append({'segment':sid,'range':rng,'adopted_sources':b['sources'],
                      'reader_sha256':hashlib.sha256(body.encode()).hexdigest(),
                      'author':'main_editor_synthesis','external_model_verbatim':False,
                      'quotes_verified_after_markdown_delimiter_normalization':card['quotes']})
    internal += ['## 保留在正文之外的差异','',
        '- **S02：**Muse-int-1 U03 的“靠在船舷上，眼睛看着远处，不敢看太用力，怕把这片刻看碎了”仍然很好。本稿选择肩膀／皮肤／手掌这一组触感，没有把第二套视线与船舷场景也堆进来。它是可替换材料，并非差材料。',
        '- **S07：**GPT-5.6w-int-2 U06 有独立的心理失重与谈话后静默体验，可以另写一颗偏内向的读法；不能借此把m.51误认成dolce sfogato，或把全段音响判为停止／悬空。主稿选回想谈话、感觉本身的吸引与局部推涌。',
        '- **S13：**退潮读法有演奏条件。Kopp [25]讨论以Rubinstein 1962为例的收势传统，也提出维持张力的个人选择；本稿采用后者。不能把m.111才发生的谱面解决提前到103，也不能宣布所有收势演法都错误。实际录音本轮未亲听；文献条件见 [事实审计](audits/S13_FACT_AUDIT.md)。',
        '- **S14：**到岸与梦醒作为明确的两种空间感保留；永别、死亡及人生学会放手没有在这一篇里展开。它们不是被证明不可能，而是不必再替最后几声和弦写一段人生结论。','',
        '## 不进入生产正文的材料','',
        '- GPro 六份及旧标签伪装成5.6w的两份Sol：保留旧包，不进入正式来源。',
        '- S07 中“dolce sfogato在51／poco più mosso在51”的错误依据，以及依赖错定位而来的星空、时间停摆叙事：排除，不自动搬到别段。',
        '- 原A中未经支持的病情／临终因果、138小节／6/8等错误：不作为正文依据。',
        '- GLOBAL 51条完整归档，但不声称它们进入过模型的局部试写输入。本轮没有把全曲主旨重新灌回每段。','']
    put('READER.md','\n'.join(out));put('BEAD_CONTENT_REVIEW.md','\n'.join(review))
    put('BEADS_INTERNAL.md','\n'.join(internal));put('OLD_READER_CLEAN.md','\n'.join(plainold))
    put('editorial/FINAL_BEADS.json',json.dumps(beads,ensure_ascii=False,indent=2))
    put('editorial/FINAL_TRACE.json',json.dumps(trace,ensure_ascii=False,indent=2))
    print(json.dumps({'beads':len(beads),'original_quotes_checked':sum(len(c['quotes']) for c in cards.values()),'old_full_paragraphs':sum(map(len,choices.values()))},ensure_ascii=False))
if __name__=='__main__':main()
