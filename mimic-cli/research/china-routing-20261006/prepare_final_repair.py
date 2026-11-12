"""Explicit mg revision after a terminal material-reject audit; no new research."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from completed_reports import completed_files,resolved_folder
HERE=Path(__file__).resolve().parent
q=resolved_folder('Q-final-completeness')
qa=json.loads((q/'evidence.json').read_text(encoding='utf-8'))
assert qa['input_complete'] is True and qa['accepted'] is False
parent=resolved_folder('S1-final'); assert (parent/'result.json').exists()
job=parent.name+'-recovery01';folder=HERE/'jobs'/job;folder.mkdir(exist_ok=True)
base=(HERE/'final-synthesis-evidence.txt').read_text(encoding='utf-8')
prior=completed_files('S1-final')[1].read_text(encoding='utf-8')
pack=base+'\n=== PRIOR COMPLETE SYNTHESIS, REJECTED BY MG QUALITY AUDIT ===\n'+prior
pack+='\n=== COMPLETE INDEPENDENT MG QUALITY AUDIT ===\n'+(q/'response.md').read_text(encoding='utf-8')
pack+='\n=== MACHINE READABLE REQUIRED MATERIAL REPAIRS ===\n'+json.dumps(qa,ensure_ascii=False,indent=2)
name='final-repair01-evidence.txt';evidence=HERE/name
with evidence.open('x',encoding='utf-8',newline='\n') as f:f.write(pack)
sha=hashlib.sha256(evidence.read_bytes()).hexdigest()
prompt=f'''你是mg最终总合成修订员 {job}。上一版完整交付被独立mg终审判accepted=false，修复清单完整在附件{name}，SHA256={sha}。附件包含原始brief、全部24份未截断研究报告、25份源审计、4份同证据独立裁判、真实冻结工件说明、上一版全文和完整终审。封闭证据，不新增市场事实、不查网页、不修改/删除冻结SKU，不用Codex结论替代mg判断。
逐条落实终审material_fixes，重新写出自包含的完整最终报告，不要仅给勘误、补丁、修改计划或摘要。保留原始任务的A-L、18类完整矩阵、12问题、四种shipping结构、10支持10反对、confirmed/probable/speculative历史、六种业务评级和具体$10,000实验。重新裁决依赖错误前提的thin/narrow评级，不预设原评级必须保留。
必须限定本研究measurement/access/transaction-chain failure的证据范围；普通消费者/global price-discovery failure未证明，profitable anomaly set未证明。不得将工具打不开网页自动升级成全球市场失灵。
分别定义demand-weighted、feasibility-weighted、opportunity-seeking及其不同目标、权重/抽样定义。18个domestic-opportunity是预注册stratum，不是feasibility weights。尚未有合法权重时留NA，不在看到结果后发明权重。分别写各自统计是否可构造。
显式列样本分层：36head slots=32verified-head+4fallback/unverified(C07-S02,C14-S01,C14-S02,C15-S02)，另18opportunity；C14-S03的PROVISIONAL_VARIANT及C17-S01/S02 manufacturer model null是正交身份质量标记，不新增/删物理SKU，不互换分母。
显式分开研究replicate A/B/C与match桶A(exact)/B(strong same-OEM)/C(functional comparable)，提供最终分桶表。usable landed观察都是0的情况下可以各列n=0；未可靠审计的其它桶计数则NA，不能杜撰。n=0不是0%节省/覆盖。各replicate全54行，不能把六批9/9和三replicate重复SKU相加。
不要沿用W4-B旧17blocked+1login数字作最终访问计数。按已审计page_shell/login_required/blocked/not_observed分别说明渠道/batch范围；没有可靠全量计数则NA。保留所有missing。
删去未经校准的0.xx置信度，使用有解释的高/中/低定性confidence；不要临时编造一个数值rubric来救原小数。补最小metric->source-audit claim/job->SKU/denominator artifact追溯索引。
内外工件hash属于不同文件，请正确解释：四裁判读judge-evidence-pack.txt的0912...，原合成读加入brief和四裁判的2be...，当前修订附件又是新容器。区别不是四裁判读错文件。LF文本hash与Windows原文件CRLF bytehash也不得混同。
读取全部输入，给24报告和4裁判的具体检查完整性表。再给7项material fixes的处理索引。无数据的median/mean/分位/≥阈值仍不可估。输出完整中文最终可交付报告，显式source URL/evidence IDs，不请求用户确认。
'''
with (folder/'prompt.txt').open('x',encoding='utf-8') as f:f.write(prompt)
with (folder/'attachments.json').open('x',encoding='utf-8') as f:json.dump({'files':[{'relative_path':name,'filename':name,'sha256':sha}]},f,indent=2)
row={'original_job_id':parent.name,'replacement_job_id':job,'replacement_prompt_sha256':hashlib.sha256((folder/'prompt.txt').read_bytes()).hexdigest(),
     'reason':'Independent mg final quality audit rejected seven concrete material requirements; explicit full mg revision, old report/audit preserved',
     'original_result_preserved':True,'utc':datetime.now(timezone.utc).isoformat()}
with (parent/'completion-resolution.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
print(json.dumps({'job':job,'evidence_sha256':sha,'material_fixes':qa['material_fixes']},ensure_ascii=False))
