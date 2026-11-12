"""Partition one immutable domestic sample into disjoint mg pricing/coverage batches."""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent

def prepare():
    sample_path=HERE/'sample-freeze-v1.json'
    if not sample_path.exists():raise SystemExit('Domestic sample is not frozen')
    sha=hashlib.sha256(sample_path.read_bytes()).hexdigest()
    if (HERE/'sample-freeze-v1.sha256').read_text(encoding='utf-8').split()[0]!=sha:
        raise SystemExit('Frozen sample hash mismatch')
    sample=json.loads(sample_path.read_text(encoding='utf-8'))
    plan_path=HERE/'post-freeze-batch-plan.json'
    if plan_path.exists():raise SystemExit('Post-freeze plan already registered')
    jobs=[]
    for batch in range(1,7):
        cats=[f'C{i:02d}' for i in range((batch-1)*3+1,batch*3+1)]
        assigned=[s['sku_id'] for s in sample['skus'] if s['category_id'] in cats]
        for replica in 'ABC':
            for stream in ('W3','W4'):
                parent=stream+'-'+replica
                identifier=f'{parent}-batch{batch:02d}'
                folder=HERE/'jobs'/identifier
                folder.mkdir(exist_ok=True)
                scope={'job_id':identifier,'parent_replicate':parent,'category_ids':cats,
                    'assigned_sku_ids':assigned,'frozen_sample_sha256':sha,
                    'full_sample_sku_count':len(sample['skus']),'not_a_new_sample':True}
                (folder/'task-input.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2),encoding='utf-8')
                common=f'''你是独立mg研究员 {identifier}，所属独立复本{parent}。你只能执行本次3个品类{json.dumps(cats)}，分配sku_ids={json.dumps(assigned)}。六个互不重叠批次合起来覆盖同一冻结样本，你不能看其他复本或批次的结果。
现在是冻结后研究，完整样本SHA256={sha}。本次子集仅是执行分工，不是删除/替换样本。按每个assigned sku_id逐行输出，找不到、登录墙、blocked、不完整数据全部保留；不得重新选“容易找到海外价”的型号。冻结前证据等级、head_status_verified和exact_variant_verified必须保留，未验证头部样本不能变成verified-head统计。
as-of2026-10-06；必须真实网页搜索并打开原始页面。研究不可用写WEB RESEARCH UNAVAILABLE。不能用snippet猜成交价、卖家、规格和库存；截图/HTTP200/网页壳不代表已核验。必须分清中国/美国地区、USD/CNY、账号、观察日期、普通公开价、会员/88VIP/定向券/国补；未观察字段null。目的地统一美国ZIP10001。不得下单、联系商家、付费或操作登录态。
每个匹配单独分A exact品牌型号容量版本地区捆绑一致，B strong-evidence same OEM但branding不同，C functional comparable。不能跨bucket算同款节省。相似图片/规格不足以证明OEM。美国区和中国区硬件不同不能冒充exact。
正文用中文简短十节：直接回答、证据表、一级来源、论坛证据、反证、置信度、缺口、意外发现、自我反驳、下一实验。调查限定约15分钟，每个SKU尽力一次明确搜索+检查关键页面；遇登录/blocked记录缺口，不无限重试。文本约1500字，所有数值可追溯URL日期，JSON紧凑完整。
'''
                if stream=='W3':
                    assignment='''仅做Price Spread Audit。对每个分配SKU查中国普通可用价格，以及美国可方便购买渠道Amazon、AliExpress、Temu、品牌官网/专业retailer/eBay，记录最便宜可核验convenient海外选项；优先精确规格，不用替代款冒充exact。记录商家/item_id、在售库存/发货地区、价格货币、运费、account_access、观察时间、价格类型、match_bucket和match_evidence。买家区域/账号看不到则不宣称缺货。
真实landed必须记录商品价、中国国内运费、agent费、实际/体积重、包装/电池附费、国际运费、清关mandatory charges、适用HTS/MFN/301/额外税/豁免来源与有效日、换汇来源。任何必要项未观测则landed_total=null，不能设成0或猜“固定税率”。四种物流结构分开：standalone、consolidated marginal、1000独立消费者订单商务价、true physical bulk import。没有真实报价则标情景假设、不算verified landed savings。
比较统一为到ZIP10001、含各自delivery/mandatory import costs、US state/local sales tax excluded的透明端点；同时注明未包含sales/use tax，不能称已核验最终checkout总价。只有A/B/C各bucket两边价格和必要成本均可用时分别算 savings=(overseas_delivered-landed)/overseas_delivered。缺值保留分母。仅给本批次真实观测小样本描述统计，不声称全市场分布；最终复本/总分布由所有批次统一计算。category/head/weight/ASP/coverage分层要保留；n太小/缺GMV权重则明确不能得出demand-weighted分布。
JSON附observations:[{sku_id,category_id,head_status_verified,exact_variant_verified,offers:[],landed_by_architecture:[],best_verified_convenient_offer:null,savings_by_bucket:[],missing_components:[],evidence_status:"..."}]；每个assigned sku_id一行。每个offer字段至少channel,url,seller_id,item_id,match_bucket,match_evidence,region_variant,currency,price,delivery_price,price_type,access_state,observed_at,source_ids。每个landed结构所有成本明细+合计+是否真实报价，未知null。
'''
                else:
                    assignment='''仅做Temu / AliExpress Coverage。两平台完全分别调查。每个assigned SKU都分别搜索并检查精确型号、规格、版本、地域和捆绑。每个平台分别记录exact offering是否已实际观察、OEM、comparable、仅marked-up reseller、US warehouse证据、库存和seller/item/URL/region/currency/ordinary delivered price日期。没有搜索结果只能NOT_OBSERVED，访问受阻BLOCKED，需要登录LOGIN_REQUIRED；只有直接可靠证据才VERIFIED_UNAVAILABLE。不能从snippet或页面壳证明价格/覆盖，也不能把Temu没有exact推给AliExpress。不要按海外可见度改变国内样本。
JSON附coverage:[{sku_id,category_id,head_status_verified,exact_variant_verified,temu:{observation_status:"EXACT_OBSERVED|OEM_OBSERVED|COMPARABLE_ONLY|RESELLER_ONLY|NOT_OBSERVED|BLOCKED|LOGIN_REQUIRED|VERIFIED_UNAVAILABLE",offers:[],search_scope:[],access_limitations:[]},aliexpress:{同样字段},china_head_us_middle_tail_status:"verified|not_supported|unresolved",caveats:[]}]；每个assigned sku_id一行。offers至少URL、seller/item、match_bucket/证据、精确版本、库存与仓库证据、currency/price/delivery、price_type/access_state/observed_at/source_ids。全部未知null，不把未观测等同于缺货。只给本批次观察计数和缺失率，不声称全样本/全市场覆盖率。
'''
                schema=f'''文末有效JSON代码块基础schema：{{"job_id":"{identifier}","parent_replicate":"{parent}","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"{sha}","assigned_sku_ids":{json.dumps(assigned)},"categories":[{{"category_id":"...","status":"..."}}],"sources":[{{"source_id":"S01","url":"https://...","title":"...","published_at":null,"retrieved_at":null,"source_type":"official|government|secondary|community","access_state":"read_full_page|snippet_only|blocked|login_required|page_shell","claims_supported":[]}}],"claims":[{{"claim_id":"K01","claim":"...","classification":"FACT|INFERENCE|HYPOTHESIS","source_ids":[],"confidence":"high|medium|low","counterevidence":"..."}}],"data_gaps":[]}}；加上本workstream要求的observations或coverage，categories包括且只包括本次3个category_id。不要研究其他批次。冻结子集将由协调器作为下一段附上。现在开始。'''
                (folder/'prompt.txt').write_text(common+assignment+schema,encoding='utf-8')
                jobs.append(identifier)
    jobs.extend('W5-'+r for r in 'ABC')
    plan={'registered_at_utc':datetime.now(timezone.utc).isoformat(),'jobs':jobs,
        'frozen_sample_sha256':sha,'replicates':list('ABC'),'streams':['W3','W4'],
        'batches_per_replicate':6,'contains_peer_outputs':False,
        'prompt_hashes':{j:hashlib.sha256((HERE/'jobs'/j/'prompt.txt').read_bytes()).hexdigest() for j in jobs}}
    plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'post_freeze_jobs':len(jobs),'sample_sha256':sha}))

if __name__=='__main__':prepare()
