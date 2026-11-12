import json,copy
from pathlib import Path
R=Path(__file__).parent
d=json.loads((R/'audit_global.json').read_text(encoding='utf-8'))
review=json.loads((R/'GLOBAL_SECOND_PASS.json').read_text(encoding='utf-8'))
fs={x['id']:x for x in review['findings']};rows=d['meanings'];by={x['id']:x for x in rows};decisions=[]
def modify(id,fid,**kw):
    by[id].update(kw);decisions.append(dict(finding=fid,action='modify',meaning_ids=[id],fields=list(kw)))
def append(fid,meaning=None,dimension='体验',evidence=None,status=None):
    f=fs[fid];i=f'G-A{len(rows)+1:03}';ev=evidence or f['evidence']
    row=dict(id=i,segment='GLOBAL',meaning=meaning or f['proposed_meaning'],dimension=dimension,distinctive_terms=[],evidence=[dict(uid=e['uid'],quote=e['quote']) for e in ev],status=status or f['proposed_current_coverage'],current_spans=[x['quote'] for x in f['current_spans']],lost=f['problem'],rationale=f['scope_and_fact_boundary'],relation=dict(kind='condition' if dimension=='表演条件' else 'standalone',with_=[],explanation='补审从复述/方法/书目中拆回的独立差异，不因同属全曲幸福主题而归为同义。'),repair=f['repair_candidate'])
    rows.append(row);by[i]=row;decisions.append(dict(finding=fid,action='add_distinction',meaning_ids=[i]));return row
for n in [1,2,3,4,7,9,10,11,12,13,14,15,22]:
    append(f'GSP-{n:02}',dimension='表演条件' if n in [1,2] else '关系' if n in [7,10,11,12,13,14] else '体验')
modify('G-A004','GSP-05',evidence=[by['G-A004']['evidence'][0]],meaning='生命力将尽时仍不愿从白日梦醒来。')
append('GSP-05','生命与爱意倒计时之中，白日梦仍有感官的饱满和精神狂喜。',evidence=[fs['GSP-05']['evidence'][0]],status='omitted')
modify('G-A006','GSP-06',meaning='重新获得的自持已受过暴露和疼痛的考验，不同于最初平静。',evidence=[by['G-A006']['evidence'][1]],status='omitted',current_spans=[],lost='身体平复不等于经历考验后重新获得的自持。')
append('GSP-06','情绪逐渐失去克制，后来又慢慢收回。',dimension='时间变化',evidence=[fs['GSP-06']['evidence'][0]],status='partial')
modify('G-A058','GSP-07',evidence=[by['G-A058']['evidence'][0]],lost='自我价值确认、苦涩反讽和告别世界分别未被明确表达；“甜蜜的恐惧”另列，不能作为这些解释的同义证据。')
modify('G-A065','GSP-08',meaning='肉体亲密与超脱同时存在。',evidence=[dict(uid=fs['GSP-08']['evidence'][0]['uid'],quote=fs['GSP-08']['evidence'][0]['quote'])])
append('GSP-08','夜水、死亡、宗教式超越和告别世界，是可以分别成立的全曲解释。',dimension='视角',evidence=[fs['GSP-08']['evidence'][1]])
modify('G-A026','GSP-16',meaning='同一摇晃由安全变为不满足随波，再主动不求平静任由卷入，最后不需水面平静也能安心。',evidence=by['G-A026']['evidence']+[dict(uid=fs['GSP-16']['evidence'][0]['uid'],quote=fs['GSP-16']['evidence'][0]['quote'])],lost='起初承托和后来卷入局部有，主动放弃维持平静及最后不以水面平静为前提的关系未完整。')
modify('G-A048','GSP-17',status='partial',lost='前后旋律对比有；听者携带中途经历形成记忆、记忆改变回归意义的因果未明确。')
modify('G-A046','GSP-18',meaning='恋人躲在贡多拉里亲吻拥抱，是一种具体身体亲密读法。',status='omitted',current_spans=[],lost='耳语与肩贴肩不是躲在船中的亲吻拥抱；不能当作已保留的同义动作。')
for meaning in ['净化是一种独立全曲读法。','狂喜是一种独立全曲读法。','带神秘感的风景是一种独立全曲读法。']:
    append('GSP-18',meaning,dimension='视角',status='omitted')['current_spans']=[]
modify('G-A020','GSP-19',meaning='无论内心经历回忆、犹疑、挣扎或强烈感情，外部时间始终继续前进。')
modify('G-A047','GSP-20',meaning='完整承担感情还包括欲望、不确定、失控及不能永久保留的疼痛，经历之后仍接受。',evidence=by['G-A047']['evidence']+[dict(uid=fs['GSP-20']['evidence'][0]['uid'],quote=fs['GSP-20']['evidence'][0]['quote'])],lost='局部沉溺和喜痛有；承担不确定、失控、必逝疼痛后仍接受的范围关系未全。')
modify('G-A069','GSP-21',status='omitted',lost='因失去过而热烈有重量、明知会失去仍尽力肯定的主观意义未写。小节定位与传记前提另外待核。')
for id in ['G-A068','G-A070']:
    modify(id,'GSP-21',status='omitted',rationale='作为来源中存在的体验审计可判未保留；精确定位仍待核，不能自动放入S14。',placement_status='pending')
by['G-A069']['placement_status']='pending'
# 再拆不同解释清单，防止重现一个partial大桶掩盖多条损失。
base=by['G-A058'];base['meaning']='自我价值确认是一种全曲读法。'
for meaning in ['苦涩的反讽是一种全曲读法。','与世界告别是一种全曲读法。']:
    x=copy.deepcopy(base);x['id']=f'G-A{len(rows)+1:03}';x['meaning']=meaning;rows.append(x)
last=next(x for x in rows if x['meaning'].startswith('夜水、死亡、宗教式'))
last['meaning']='夜水是一种全曲解释。'
for meaning in ['死亡是一种全曲解释。','宗教式超越是一种全曲解释。']:
    x=copy.deepcopy(last);x['id']=f'G-A{len(rows)+1:03}';x['meaning']=meaning;rows.append(x)
last['lost']='现稿有水景，但没有夜水这一全曲解释。告别世界与G-A同名条目去重，不另增。'
for u in d['unit_reviews']:
    u['meaning_ids']=[r['id'] for r in rows if any(e['uid']==u['uid'] for e in r['evidence'])]
    if u['meaning_ids']:u['disposition']='accounted'
    if u['uid']=='SRC-gpt6w-web-1-U23':u['residual']='书目链接为元信息；强音温暖歌唱的表演条件、悬停与光线及来之不易的安宁已拆出，不再整段按metadata排除。作者归因没有外部复核。'
    if u['uid'] in ['SRC-muse-int-2-U01','SRC-muse-int-3-U01']:u['residual']='心理潮汐、情绪自行转弯已补入；不要固定剧情为方法说明；138小节断言隔离。'
d['second_pass_applied']=dict(findings=22,decisions=decisions)
(R/'audit_global.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'GLOBAL_REVIEW_DECISIONS.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2),encoding='utf-8')
print('global entries',len(rows))
