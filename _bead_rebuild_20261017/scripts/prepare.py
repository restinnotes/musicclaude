from pathlib import Path
import json, hashlib, shutil

R=Path(__file__).resolve().parents[1]
Q=R.parent/'_bead_quality_20261017'
A=R.parent/'_bead_full_audit_20261017'
for d in ['inputs','drafts','reviews','scripts','reference']:(R/d).mkdir(exist_ok=True,parents=True)
def put(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
brief='''你是中文音乐内容编辑。阅读完整相关原A及旧审计，给肖邦《船歌》Op.60重建Bead。当前实验要解决真实意义丢失，而不是写一篇更会总结的文章。固定14个S范围，不新研究、不联网、不创造听觉事实。
原稿内的不同动因、身体感、人物位置、时间顺序、意象细节、特殊词汇都可能独立有价值；共享“温柔/不安/留恋”不能当成重复。只有成品能还原各项不同意思才可称合并。审计过细、跨段或错位的条目可以作具体裁决，不能默默缩分母。
成品仍说完整自然中文，保留原文好句，只删重复场景、泛泛解释及编辑连接词。不要账本腔、心理学标签、夸张标题、金句总结，不用“不是X而是Y”反复制造戏剧。不可把不同来源串成同一个人的必然经历；不要自造“于是/渐渐/因此/底下其实”的关系。并列读法不要求互斥。
一个S在同一页。合理结构：同一声音的不同观察可平行排列；多种完整解释用并列读法；原文明确三次变化可用顺序；条件紧贴对应句。别强行每段都套同一结构。每块写真实内容，块标题是简单定位语。无任意加粗、戏剧强调、自动分镜、轮播或隐藏独特意思。全部卡片同等可见。宁可承认内容量，不能靠删异质性伪装降阅读负担。也不要把每条审计机械变一张卡片。
重点反例：S02三次相似尾音“安慰、犹豫、疼”必须保留中间项及顺序。S04流连细节与怕结束而开始用力是不同动因。S07深谈后沉默/语言跟不上感受、反复回放谈话、沉迷于自己正在感觉是三种读法，不串为一个时间过程；“遗憾”“情色性的暖意”不可被宽泛亲密替换。sfogato错放51的星空时间停摆整链隔离，合法心理失重独立保留。
只输出JSON，无代码围栏。格式 {"pages":[{"segment":"Sxx","bars":"...","title":"简单具体标题","intro":"可空，段内共同听觉前提一句，只写有来源者","blocks":[{"id":"Sxx-B01","kind":"facets|alternatives|sequence|observation|condition","label":"短定位","text":"完整自然中文","meaning_ids":["旧审计ID"],"evidence":[{"uid":"...","quote":"连续原文精确引句"}]}],"decisions":[{"meaning_ids":["..."],"status":"partial|omitted|pending|out_of_scope|duplicate","reason":"具体丢了什么/为何错段/为何真重复","duplicate_of":"有则填原ID"}]}],"method_notes":[]}
必须通读每段完整Pool，不能只改反例。每条审计ID都应在block.meaning_ids或decisions有去向；无损才可放block.meaning_ids，半保留放decisions.partial并说明余项。它们不等于证实覆盖，另有反向复核。正文句不得引用审计标签。来源引句需要短且精确，不用省略号拼接。音乐事实看已核准边界，错误事实可拒绝，原稿主观体验不能仅因谱面没有人而删除。
输出以内容好读为先，不用硬字数上限凑覆盖率。'''
(R/'EDITOR_BRIEF.txt').write_text(brief,encoding='utf-8')
meanings=json.loads((A/'ALL_MEANINGS.json').read_text(encoding='utf-8'))
for n in range(1,15):
 s=f'S{n:02}'
 rows=[x for x in meanings if x['segment']==s]
 put(R/'reference'/f'{s}_ledger.json',rows)
 text=brief+'\n\n【完整原A】\n'+(Q/'production_context'/'pools'/f'{s}.txt').read_text(encoding='utf-8')
 fact=Q/'audits'/f'facts_{s}.txt'
 if fact.exists():text+='\n【已核事实边界】\n'+fact.read_text(encoding='utf-8')
 thin=[{k:x[k] for k in ['id','meaning','dimension','distinctive_terms','relation','lost']} for x in rows]
 text+='\n【原意逐项账本：防止漏项，须回读上方原文】\n'+json.dumps(thin,ensure_ascii=False)
 (R/'inputs'/f'{s}.txt').write_text(text,encoding='utf-8')
shutil.copyfile(Q/'scripts'/'run_calls.py',R/'scripts'/'run_calls.py')
jobs=[]
for s in ['S02','S04','S07']:
 for tag,model in [('FLASH','antigravity-tools/gemini-3.8-flash-high'),('MUSE','opencode2api/muse-spark-1.3-contributor-free#xhigh')]:
  p=R/'inputs'/f'{s}.txt'
  jobs.append(dict(job_id=f'{s}_{tag}_relations_r1',channel='opencode',model=model,prompt_file=f'inputs/{s}.txt',prompt_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),timeout_seconds=1800,min_response_chars=500,labels={'segment':s,'method':'source_distinctions_relations','round':1}))
put(R/'jobs_pilot.json',dict(schema_version=1,max_workers=2,output_dir='scripts/call_results',jobs=jobs))
put(R/'reference'/'BASELINE_HASH.json',{'file':str(Q/'editorial'/'FINAL_BEADS.json'),'sha256':hashlib.sha256((Q/'editorial'/'FINAL_BEADS.json').read_bytes()).hexdigest()})
print('prepared',len(jobs),'real pilot jobs')

if __name__=='__main__':pass
