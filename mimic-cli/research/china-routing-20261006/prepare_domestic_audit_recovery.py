"""Reconcile a stopped failed 27-candidate audit into three bounded mg audits."""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
from completed_reports import resolved_folder

HERE=Path(__file__).resolve().parent

def register_ready():
    jobs=[]
    for batch in range(1,7):
        parent=f'R2-domestic-batch{batch:02d}'
        base=HERE/'jobs'/parent
        if not (base/'prompt.txt').exists():continue
        actual=resolved_folder(parent)
        rp=actual/'result.json';dp=actual/'diagnostics.json'
        plan=base/'category-recovery-plan.json'
        if plan.exists():
            jobs+=json.loads(plan.read_text(encoding='utf-8'))['jobs']
            continue
        if not rp.exists() or json.loads(rp.read_text(encoding='utf-8')).get('transport_success'):continue
        if not dp.exists():continue
        diagnostics=json.loads(dp.read_text(encoding='utf-8'))
        if diagnostics.get('diagnostics',{}).get('generation_stop_verified') is not True:continue
        cats=[f'C{i:02d}' for i in range((batch-1)*3+1,batch*3+1)]
        inputs=json.loads((base/'audit-input.json').read_text(encoding='utf-8'))['inputs']
        children=[]
        for cat in cats:
            job=f'{parent}-recovery-{cat}'
            folder=HERE/'jobs'/job;folder.mkdir(exist_ok=True)
            packets=[]
            for entry in inputs:
                original_id=entry['job_id']
                original_folder=resolved_folder(original_id)
                evidence=json.loads((original_folder/'evidence.json').read_text(encoding='utf-8'))
                candidates=[c for c in evidence.get('sku_candidates',[]) if c.get('category_id')==cat]
                refs={s for c in candidates for s in c.get('source_ids',[])}
                packets.append({'original_job_id':original_id,
                    'original_response_byte_sha256':hashlib.sha256((original_folder/'response.md').read_bytes()).hexdigest(),
                    'category':next((c for c in evidence.get('categories',[]) if c.get('category_id')==cat),None),
                    'sku_candidates':candidates,
                    'sources':[s for s in evidence.get('sources',[]) if s.get('source_id') in refs],
                    'original_source_access_is_unverified_until_you_inspect_it':True})
            prompt=f'''你是mg独立国内样本审计员 {job}。本次仅一个品类{cat}、最多9个候选；禁止扩展品类，禁止查任何海外具体SKU价格/覆盖/销售。三份独立研究已经完成，你现在才能看它们的候选。上一次三品类27候选审计已停止失败，其截图和诊断保留；你没有收到它或其他审计员的结果。
as-of2026-10-06，真实网页浏览。核对下面全部候选的真实品牌/型号/精确版本、国内购买/排名证据。官方型号存在不证明畅销；评论数和推荐榜不证明销量排名；不把未登录、snippet、HTTP200壳页或AIGC文章当作成交价/消费者证据。遇blocked只记缺口，不反复请求。普通/会员/券/国补/旧价分开，未知null。最多用约8分钟核验有限关键来源，正文不超过800汉字，加紧凑JSON，不扩写十章。
每个候选都要在candidate_audits列出原original_job_id和original_candidate_id(原字段candidate_sku_id/候选sku_id/sku_id)。质量grade：VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT、VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT、VERIFIED_MODEL_ONLY_HEAD_UNVERIFIED、PROVISIONAL_VARIANT、UNVERIFIED_BLOCKED、EXCLUDE_ALLOWED_REASON。未知不要升级。仅假货/非目标类/完全无法定义版本/非实物/明确非法禁运能排除；重量电池电压兼容保修不得删。
建议保留最多2个domestic_head+1个domestic_opportunity：先真实核验国内销量/榜单+版本，再真实国内购买证据+版本，最后型号存在但头部未核验；同级按brand/model/variant的NFKC/casefold字典序。不同容量地域捆绑不可合并。没有核验就留gap，可少于3个；型号存在未核验的候选不能推荐。未核验head要明确，不进入verified-head统计。不要联系/支付/下单/动登录态。
有效JSON：{{"job_id":"{job}","web_research_available":true,"pre_freeze_compliance":true,"review_performed":true,"category_ids":["{cat}"],"candidate_audits":[{{"original_job_id":"...","original_candidate_id":"...","brand":"...","model":"...","exact_variant":"...","quality_grade":"...","model_exists_verified":false,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":[],"caveat":"..."}}],"recommended_selection":[{{"original_job_id":"...","original_candidate_id":"...","brand":"...","model":"...","exact_variant":"...","category_id":"{cat}","sampling_stratum":"domestic_head|domestic_opportunity","quality_grade":"...","reason":"...","source_ids":[]}}],"exclusion_log":[],"category_gaps":[],"sources":[{{"source_id":"S01","url":"https://...","title":"...","published_at":null,"retrieved_at":null,"source_type":"official|community|secondary","access_state":"read_full_page|blocked|login_required|snippet_only|page_shell","claims_supported":[]}}],"claims":[],"data_gaps":[]}}
下面是完整的本品类候选/引用来源结构化记录，非其他品类原报告的全文；引用原报告哈希保留，末尾四个裁决员仍会收到全部未截断原报告。这里的研究员VERIFIED只是待核验主张。\n'''+json.dumps(packets,ensure_ascii=False)
            (folder/'prompt.txt').write_text(prompt,encoding='utf-8')
            (folder/'audit-input.json').write_text(json.dumps({'parent_audit':parent,'category_id':cat,'packets':packets,'contains_peer_audit_outputs':False},ensure_ascii=False,indent=2),encoding='utf-8')
            children.append(job)
        bundle_id=actual.name+'-recovery-bundle'
        bundle=HERE/'jobs'/bundle_id;bundle.mkdir(exist_ok=True)
        (bundle/'prompt.txt').write_text('Mechanical bundle of three completed independent mg category-source audits. This file is provenance, not a submitted prompt.',encoding='utf-8')
        record={'registered_utc':datetime.now(timezone.utc).isoformat(),'parent_audit':parent,
            'failed_attempt_job_id':actual.name,'failed_request_id':diagnostics['diagnostics'].get('request_id'),
            'jobs':children,'bundle_job_id':bundle_id,'category_ids':cats,
            'original_failure_preserved':True,'generation_stop_verified':True}
        with plan.open('x',encoding='utf-8') as h:json.dump(record,h,ensure_ascii=False,indent=2)
        resolution={'original_job_id':actual.name,'replacement_job_id':bundle_id,
            'replacement_prompt_sha256':hashlib.sha256((bundle/'prompt.txt').read_bytes()).hexdigest(),
            'original_result_preserved':True,'reason':'Three bounded mg category audits mechanically bundled, original stopped incomplete response preserved'}
        with (actual/'completion-resolution.json').open('x',encoding='utf-8') as h:json.dump(resolution,h,ensure_ascii=False,indent=2)
        jobs+=children
    return jobs

def assemble_ready():
    for path in (HERE/'jobs').glob('R2-domestic-batch*/category-recovery-plan.json'):
        plan=json.loads(path.read_text(encoding='utf-8'))
        target=HERE/'jobs'/plan['bundle_job_id']
        if (target/'result.json').exists():continue
        combined={'job_id':plan['bundle_job_id'],'web_research_available':True,
            'pre_freeze_compliance':True,'review_performed':True,'category_ids':plan['category_ids'],
            'candidate_audits':[],'recommended_selection':[],'exclusion_log':[],
            'category_gaps':[],'sources':[],'claims':[],'data_gaps':[]}
        records,reports=[],[];valid=True
        for child,cat in zip(plan['jobs'],plan['category_ids']):
            folder=HERE/'jobs'/child
            if not (folder/'result.json').exists() or not (folder/'evidence.json').exists():valid=False;break
            result=json.loads((folder/'result.json').read_text(encoding='utf-8'))
            data=json.loads((folder/'evidence.json').read_text(encoding='utf-8'))
            if not result.get('transport_success') or data.get('review_performed') is not True or data.get('web_research_available') is not True or data.get('pre_freeze_compliance') is not True:valid=False;break
            if data.get('category_ids')!=[cat]:valid=False;break
            original=json.loads((folder/'audit-input.json').read_text(encoding='utf-8'))
            expected={(p['original_job_id'], c.get('candidate_sku_id') or c.get('sku_candidate_id') or c.get('候选sku_id') or c.get('sku_id')) for p in original['packets'] for c in p['sku_candidates']}
            actual={(c.get('original_job_id'),c.get('original_candidate_id')) for c in data.get('candidate_audits',[])}
            if expected!=actual:valid=False;break
            raw=(folder/'response.md').read_bytes();sha=hashlib.sha256(raw).hexdigest()
            reports.append('\n=== UNEDITED MG CATEGORY AUDIT '+child+'; SHA256 '+sha+' ===\n'+raw.decode('utf-8'))
            records.append({'job_id':child,'response_sha256':sha,'screenshots_complete':result.get('screenshots_complete',False)})
            for key in ('candidate_audits','recommended_selection','exclusion_log','category_gaps','sources','claims','data_gaps'):
                for row in data.get(key,[]):
                    if isinstance(row,dict):
                        row={**row,'category_audit_job_id':child}
                        if key=='sources':row['source_id']=cat+'-'+str(row['source_id'])
                        if 'source_ids' in row:row['source_ids']=[cat+'-'+str(x) for x in row['source_ids']]
                    combined[key].append(row)
        if not valid:continue
        raw=('This is one logical mg sample audit assembled mechanically from three completed single-category mg audits. The original larger audit failed and is preserved; no new model synthesis was invented. Source IDs are mechanically prefixed by category to avoid collisions.\n'+''.join(reports)).encode('utf-8')
        (target/'response.md').write_bytes(raw)
        (target/'evidence.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2),encoding='utf-8')
        result={'job_id':plan['bundle_job_id'],'transport_success':True,'status':'needs_review',
            'completion_mode':'mechanical_bundle_of_three_successful_mg_category_audits',
            'completed_utc':datetime.now(timezone.utc).isoformat(),'category_audit_inputs':records,
            'response_sha256':hashlib.sha256(raw).hexdigest(),'screenshots_complete':all(x['screenshots_complete'] for x in records)}
        (target/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    print(json.dumps({'recovery_jobs':register_ready()}));assemble_ready()
