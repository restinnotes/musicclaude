"""A fresh mg final-deliverable audit, after the four judges and synthesis."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
JOB='Q-final-completeness'

def prepare(job=JOB, filename='final-quality-audit-input.txt'):
    folder=HERE/'jobs'/job;folder.mkdir(exist_ok=True)
    from completed_reports import completed_files
    report=completed_files('S1-final')[1].read_text(encoding='utf-8')
    brief=(HERE/'original-brief.txt').read_text(encoding='utf-8')
    audit_index=(HERE/'coordinator-source-audit.json').read_text(encoding='utf-8')
    full='=== FULL USER BRIEF ===\n'+brief+'\n=== COMPLETE FINAL MG REPORT ===\n'+report+'\n=== MG SOURCE AUDIT INDEX ===\n'+audit_index
    full+='\n=== ACTUAL IMMUTABLE FREEZE ARTIFACT ===\n'+(HERE/'sample-freeze-v1.json').read_text(encoding='utf-8')
    full+='\n=== EXPLICITLY EARLIER PREFREEZE IDENTITY NOTE ===\n'+(HERE/'prefreeze-identity-validation-note.json').read_text(encoding='utf-8')
    full+='\n=== MECHANICAL 54-SKU LOGICAL REPLICATE DENOMINATORS ===\n'+(HERE/'audited-denominator-checks.json').read_text(encoding='utf-8')
    from prepare_reviews import ROLES
    from completed_reports import resolved_folder
    inputs=[]
    for judge_job in ROLES:
        result_path,judge_path=completed_files(judge_job)
        judge_text=judge_path.read_text(encoding='utf-8')
        full+='\n=== COMPLETED INDEPENDENT JUDGE '+judge_job+' ===\n'+judge_text
        inputs.append({'job_id':judge_job,'resolved_job':resolved_folder(judge_job).name,
            'result':json.loads(result_path.read_text(encoding='utf-8')),
            'attachments':json.loads((resolved_folder(judge_job)/'attachments.json').read_text(encoding='utf-8')),
            'response_sha256':hashlib.sha256(judge_path.read_bytes()).hexdigest()})
    full+='\n=== 24-REPORT INPUT MANIFEST ===\n'+(HERE/'judge-evidence-pack.json').read_text(encoding='utf-8')
    full+='\n=== MECHANICAL JUDGE INPUT AND COMPLETION RECORDS ===\n'+json.dumps(inputs,ensure_ascii=False,indent=2)
    (HERE/filename).write_text(full,encoding='utf-8',newline='\n')
    sha=hashlib.sha256(full.encode('utf-8')).hexdigest()
    prompt=f'''你是独立mg最终交付审计员 {job}。不是新增市场研究员，不替代四个独立裁决员。只核验附件中的完整最终报告是否落实原始用户任务和已有mg审计结果，禁止新查事实或修改冻结样本。附件{filename} SHA256={sha}。
逐项检查：24个独立研究复本是否真实完成且拆分/续接不冒充更多独立复本；4个同证据独立评审；完整18品类矩阵；A-L交付章节；12个业务问题；broad/narrow/thin/full marketplace及shopping agent/logistics platform各自Strong/Moderate/Weak/Rejected、置信度、decisive evidence、strongest counterargument、change-of-mind data；四种shipping structures；10个最强支持/反对；confirmed/probable/speculative竞争历史解释；$10k实际减少不确定性实验。
逐一检查所有最终数字是否有可追溯source/claim/sku证据，统计分母是否含notobserved/blocked，verified-head/provisional和A/B/C是否分列。mean/median/P10/P25/P50/P75/P90及≥10/20/30/40/50%只有输入充分才能成立，无法算时明确写无法估计。需求支出权重不能混增长/碎片化机会评分，也不能把PCE/批发/零售/shipments混平均。demand-weighted分布、feasibility-weighted样本、opportunity-seeking样本按用户两处要求明确解释各自定义；数据不支持权重则留缺而不编造。不要要求用不存在的观测凑出数字。登录数据缺口必须有精确字段和影响。退货/欺诈/支付成本与兼容性必须进入可行性而不成为前置删样本理由。
特别核查裁判本身的范围错误是否被总合成纠正：本研究工具/会话访问失败，不能直接证明普通消费者或全球市场价格发现失败；要分开measurement failure、已证明consumer price-discovery failure、已证明profitable anomaly set。J3当前证据NO-GO不等于真实市场很小。sample_frozen=false属于更早的prefreeze note，不是稍后实际冻结artifact的当前状态；C17 model缺口仍须保留。单批9/9不得代替每个六批logical replicate的54行分母。
附件无法全部读则INPUT_INCOMPLETE且accepted=false。若报告符合要求且如实报告关键缺口，可accepted=true，即使商业判断仍有不确定性；不因没有付费数据库拒绝诚实研究。实际遗漏、unsupported数字或错口径是material修复项。中文简短结论，随后有效JSON：
{{"job_id":"{job}","input_complete":true,"accepted":false,"checks":[{{"requirement":"...","status":"pass|material_failure|honest_data_gap","evidence_location":"...","reason":"..."}}],"material_fixes":[],"unsupported_final_numbers":[],"remaining_decisive_unknowns":[]}}
现在阅读附件并审计，不要重复整个报告。'''
    (folder/'prompt.txt').write_text(prompt,encoding='utf-8')
    (folder/'attachments.json').write_text(json.dumps({'files':[{'relative_path':filename,'filename':filename,'sha256':sha}]},indent=2),encoding='utf-8')
    print(json.dumps({'job_id':job,'input_sha256':sha}))

if __name__=='__main__':prepare()
