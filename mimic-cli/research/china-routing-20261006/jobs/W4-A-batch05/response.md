## 1. 直接回答

本批次仅处理 C13/C14/C15 的 9 个冻结 SKU，未替换、删除或另选型号；冻结前 `head_status_verified` / `exact_variant_verified` 原样保留。Temu 与 AliExpress 共 18 个 SKU×平台单元均完成一次明确型号检索，并尝试打开平台原始搜索页；两平台原始搜索入口在本研究环境均不可访问。因此结论是 **18/18 `BLOCKED`，不是无货**；`NOT_OBSERVED=0`、`VERIFIED_UNAVAILABLE=0`、A/B/C 可核验 offer 均为 0。可核验 offer 缺失率为 18/18=100%，原因全部是访问阻断。未登录、未下单、未联系卖家。

## 2. 证据表

| SKU | 冻结 head/exact | Temu | AliExpress | A/B/C | US仓/库存/普通送达价 |
|---|---|---|---|---|---|
| C13-S01 | true/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C13-S02 | true/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C13-S03 | false/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C14-S01 | false/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C14-S02 | false/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C14-S03 | false/false | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C15-S01 | true/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C15-S02 | false/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |
| C15-S03 | false/true | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 0/0/0 | 均 null |

## 3. 一级来源

厂商原始页只用于划定“exact”的版本边界，**不替代 Temu/AliExpress 覆盖证据**。70mai 美国站公开的是全球版“M800”，存在前摄/前后双摄等选项，不能据此把冻结的中国 `M800Pro 2026/4G/无卡`自动判为同一 exact。[70mai Official Store](https://70mai.store/collections/night-driving-weather?utm_source=chatgpt.com) DDPAI 官方确认全球 `MINI PRO 4K`，但页面不足以锁定冻结样本的“360度旋转+无卡套餐”区域版本。[DDPAI Global](https://store.ddpai.com/products/mini-pro-4k?utm_source=chatgpt.com) 70mai 官方另有 `Cordless Air Compressor 2`，也不能自动等同国内“青春版2 2026新款”。[70mai Official Store](https://70mai.store/collections/auto-accessories/products/tp07?utm_source=chatgpt.com)

Naturehike 官方 Cloud Up Pro 2 明确为两人、20D Nylon，但冻结样本本身“浅灰红”聚合变体未锁，因此仍不能升级 exact。[Naturehike](https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent?utm_source=chatgpt.com) Bambu A1 美国官方页明确为美国销售版本并从 US warehouse 发货；冻结 SKU 是“A1 单机大陆版”，地区不同，不能作为 A 桶 exact。[Bambu Lab Store](https://us.store.bambulab.com/products/a1?sscid=71k9_oao1t\&utm_source=chatgpt.com) Creality Space Pi V2 Plus 官方甚至分别列出 US Plug item number `4005010154`，进一步说明大陆版与美国版必须逐版本核。[Creality VIP Mall](https://mvip.creality.com/en/goods/goodsDetail/2645?utm_source=chatgpt.com)

## 4. 论坛证据

论坛仅作反证/风险线索，不证明平台成交覆盖。Bambu 社区用户近期报告中国/美国等区域机存在绑定、固件或区域使用差异，因此对 C15-S02 的“大陆版→美国 exact”应保持严格。[Reddit](https://www.reddit.com/r/BambuLab/comments/1v0i1sc/i_bought_a_3d_printer_then_i_moved_now_its_a_brick/?utm_source=chatgpt.com) P2S 后来确实进入美国官方销售，但这只证明美国市场存在 P2S，不证明 Temu/AliExpress 有冻结的 P2S Combo listing。[Reddit](https://www.reddit.com/r/BambuLab/comments/1p0ygr7/p2s_available_in_us_finally/?utm_source=chatgpt.com) Naturehike 用户讨论支持 Cloud Up Pro 2 是真实全球型号，但同样不能证明特定颜色/20D聚合变体在目标平台可买。[Reddit](https://www.reddit.com/r/bikepacking/comments/1t0x2it/bikepacking_tent_for_2/?utm_source=chatgpt.com)

## 5. 反证

三个最重要反证是：① M800 全球命名与冻结 `M800Pro` 不完全一致；② A1 美国官方 SKU 与“大陆版”明确属于不同地区销售边界；③ Space Pi V2 Plus 有独立 US 插头料号。故即便未来搜索到相似标题，也必须看到型号、套装、地区/插头、容量/重量级别等关键选择器后才能进 A；图片相似、参数接近或品牌同源只能保留 B/C，不能跨桶算节省。[70mai Official Store](https://70mai.store/collections/night-driving-weather?utm_source=chatgpt.com)

## 6. 置信度

对“本研究环境无法读取两平台搜索结果”置信度高，因为 18 个原始搜索入口逐一失败；对“平台实际有没有商品”置信度低，故全部用 `BLOCKED` 而不是“没有”。冻结前 verified-head 仅 C13-S01、C13-S02、C15-S01 三项保持 true；其余任何头部槽位均未被升级。

## 7. 缺口

18 个平台单元均无法核验 seller/item、variant selector、库存、US warehouse、USD 普通公开价、配送费、ZIP10001 送达价、重量/尺寸、会员价/定向券。没有 offer，因此关税分类、税率、四种运输结构成本及节省率全部保持 null；美国 sales tax 不估算、不计入比较端点。

## 8. 意外发现

厂商一级页反而显示了多处区域化差异：A1 美国库存、Space Pi 独立 US plug、70mai 全球 M800 命名等。这意味着本 workstream 即使后续发现 AliExpress/Temu 商品，也不能只靠同品牌同外观认定 A 桶。[Bambu Lab Store](https://us.store.bambulab.com/products/a1?sscid=71k9_oao1t\&utm_source=chatgpt.com)

## 9. 自我反驳

普通消费者浏览器可能可以访问这些平台，因此这里的 `BLOCKED` 是**研究访问状态**，不是平台可用性结论；搜索引擎没有返回平台 PDP 也不能证明无货。反过来，厂商美国站已有相近型号也不能证明第三方平台存在对应 SKU。两类证据都没有被越权外推。

## 10. 下一实验

协调器若继续复核，应保持同一冻结 SKU 与同一检索词，用美国未登录浏览器、目的地 ZIP10001 重跑每个平台一次；只记录公开 PDP 实际选择的版本、seller/item、库存、仓库、基础价+配送，并在出现登录墙时直接记 `LOGIN_REQUIRED`。四种运输结构的具体定义本批次指令未提供，因此下面只保留四个空槽位，避免自造口径。

```json
{
  "job_id":"W4-A-batch05",
  "parent_replicate":"W4-A",
  "web_research_available":true,
  "pre_freeze_compliance":true,
  "frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "as_of":"2026-10-06",
  "destination_zip":"10001",
  "assigned_sku_ids":["C13-S01","C13-S02","C13-S03","C14-S01","C14-S02","C14-S03","C15-S01","C15-S02","C15-S03"],
  "categories":[
    {"category_id":"C13","status":"BOTH_PLATFORM_SEARCH_ACCESS_BLOCKED"},
    {"category_id":"C14","status":"BOTH_PLATFORM_SEARCH_ACCESS_BLOCKED"},
    {"category_id":"C15","status":"BOTH_PLATFORM_SEARCH_ACCESS_BLOCKED"}
  ],
  "batch_stats":{
    "sku_count":9,
    "platform_sku_cells":18,
    "observation_status_counts":{"EXACT_OBSERVED":0,"OEM_OBSERVED":0,"COMPARABLE_ONLY":0,"RESELLER_ONLY":0,"NOT_OBSERVED":0,"BLOCKED":18,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0},
    "match_bucket_counts":{"A":0,"B":0,"C":0},
    "verified_offer_cells":0,
    "offer_verification_missing_cells":18,
    "offer_verification_missing_rate":1.0,
    "both_platforms_blocked_skus":9
  },
  "comparison_method":{
    "endpoint":"ordinary_public_delivered_price_to_US_ZIP10001",
    "us_sales_tax_treatment":"excluded_and_not_estimated; no checkout performed",
    "member_88vip_targeted_coupon_subsidy":"not_imputed; null unless directly observed",
    "tariff_classification":null,
    "tariff_source":null,
    "quote_assumptions":"No marketplace offer was verified, so no tariff, savings, shipping, weight or dimensional assumptions were manufactured."
  },
  "shipment_structures":[
    {"structure_id":"structure_1","definition":null,"status":"UNOBSERVED","note":"definition not supplied in this batch instruction"},
    {"structure_id":"structure_2","definition":null,"status":"UNOBSERVED","note":"definition not supplied in this batch instruction"},
    {"structure_id":"structure_3","definition":null,"status":"UNOBSERVED","note":"definition not supplied in this batch instruction"},
    {"structure_id":"structure_4","definition":null,"status":"UNOBSERVED","note":"definition not supplied in this batch instruction"}
  ],
  "sources":[
    {"source_id":"S01","url":"https://www.temu.com/search_result.html?search_key=70mai%20M800Pro","title":"Temu search - 70mai M800Pro","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S02","url":"https://www.aliexpress.us/w/wholesale-70mai-m800pro.html","title":"AliExpress US search - 70mai M800Pro","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S03","url":"https://www.temu.com/search_result.html?search_key=DDPAI%20MINI%20Pro%204K","title":"Temu search - DDPAI MINI Pro 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S04","url":"https://www.aliexpress.us/w/wholesale-ddpai-mini-pro-4k.html","title":"AliExpress US search - DDPAI MINI Pro 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S05","url":"https://www.temu.com/search_result.html?search_key=70mai%20Cordless%20Air%20Compressor%202","title":"Temu search - 70mai Cordless Air Compressor 2","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S06","url":"https://www.aliexpress.us/w/wholesale-70mai-cordless-air-compressor-2.html","title":"AliExpress US search - 70mai Cordless Air Compressor 2","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S07","url":"https://www.temu.com/search_result.html?search_key=Mobi%20Garden%20NXZQU61017","title":"Temu search - Mobi Garden NXZQU61017","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S08","url":"https://www.aliexpress.us/w/wholesale-mobi-garden-nxzqu61017.html","title":"AliExpress US search - Mobi Garden NXZQU61017","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S09","url":"https://www.temu.com/search_result.html?search_key=Li-Ning%20Zhan%20Ji%205000%204U","title":"Temu search - Li-Ning Zhan Ji 5000 4U","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S10","url":"https://www.aliexpress.us/w/wholesale-li-ning-zhan-ji-5000-4u.html","title":"AliExpress US search - Li-Ning Zhan Ji 5000 4U","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S11","url":"https://www.temu.com/search_result.html?search_key=Naturehike%20Cloud%20Up%20Pro%202%2020D","title":"Temu search - Naturehike Cloud Up Pro 2 20D","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S12","url":"https://www.aliexpress.us/w/wholesale-naturehike-cloud-up-pro-2-20d.html","title":"AliExpress US search - Naturehike Cloud Up Pro 2 20D","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S13","url":"https://www.temu.com/search_result.html?search_key=Bambu%20Lab%20P2S%20Combo","title":"Temu search - Bambu Lab P2S Combo","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S14","url":"https://www.aliexpress.us/w/wholesale-bambu-lab-p2s-combo.html","title":"AliExpress US search - Bambu Lab P2S Combo","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S15","url":"https://www.temu.com/search_result.html?search_key=Bambu%20Lab%20A1%203D%20printer","title":"Temu search - Bambu Lab A1","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S16","url":"https://www.aliexpress.us/w/wholesale-bambu-lab-a1-3d-printer.html","title":"AliExpress US search - Bambu Lab A1","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S17","url":"https://www.temu.com/search_result.html?search_key=Creality%20Space%20Pi%20V2%20Plus","title":"Temu search - Creality Space Pi V2 Plus","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S18","url":"https://www.aliexpress.us/w/wholesale-creality-space-pi-v2-plus.html","title":"AliExpress US search - Creality Space Pi V2 Plus","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K02"]},
    {"source_id":"S19","url":"https://70mai.store/collections/night-driving-weather","title":"70mai Official Store - M800","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S20","url":"https://store.ddpai.com/products/mini-pro-4k","title":"DDPAI MINI PRO 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},
    {"source_id":"S21","url":"https://70mai.store/collections/auto-accessories/products/tp07","title":"70mai Cordless Air Compressor 2","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S22","url":"https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent","title":"Naturehike Cloud Up Pro 2-Person","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"S23","url":"https://us.store.bambulab.com/products/a1","title":"Bambu Lab A1 US Store","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S24","url":"https://mvip.creality.com/en/goods/goodsDetail/2645","title":"Creality Space Pi V2 Plus Filament Dryer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K09"]},
    {"source_id":"S25","url":"https://dashcamtalk.com/dash-cam/70mai-4k-m800/","title":"70mai 4K M800 Review / Community","published_at":"2026","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S26","url":"https://www.reddit.com/r/BambuLab/comments/1v0i1sc/i_bought_a_3d_printer_then_i_moved_now_its_a_brick/","title":"BambuLab community discussion on region lock","published_at":"2026-07-19","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S27","url":"https://www.reddit.com/r/BambuLab/comments/1p0ygr7/p2s_available_in_us_finally/","title":"BambuLab community - P2S available in US","published_at":"2025-11-19","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K10"]},
    {"source_id":"S28","url":"https://www.reddit.com/r/bikepacking/comments/1t0x2it/bikepacking_tent_for_2/","title":"Bikepacking community - Cloud Up Pro 2","published_at":"2026-05-01","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K06"]}
  ],
  "claims":[
    {"claim_id":"K01","claim":"All 18 direct Temu/AliExpress marketplace-search page checks for the assigned SKUs were inaccessible in the research environment.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"A normal consumer browser may still be able to access these platforms; BLOCKED is an observation-access result, not proof of marketplace absence."},
    {"claim_id":"K02","claim":"No marketplace seller/item, exact variant, inventory, US warehouse, ordinary USD delivered price, shipping amount, weight, dimensions or tariff-relevant offer data were directly verified.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"Search snippets or page shells were intentionally not promoted to verified offer evidence."},
    {"claim_id":"K03","claim":"The 70mai global/US store uses M800 naming and offers M800 configurations; this is insufficient to prove the frozen China M800Pro 2026 dual/4G/no-card variant is exact on either target marketplace.","classification":"INFERENCE","source_ids":["S19","S25"],"confidence":"medium","counterevidence":"M800 and M800Pro may share substantial hardware, but no target-platform PDP was accessible to prove exact regional/bundle equivalence."},
    {"claim_id":"K04","claim":"DDPAI has an official global MINI PRO 4K product, but the retrieved official page does not establish the frozen 360-degree/no-card package as the identical regional variant.","classification":"INFERENCE","source_ids":["S20"],"confidence":"medium","counterevidence":"The core model name matches; exact package/region remains unverified."},
    {"claim_id":"K05","claim":"70mai officially sells a Cordless Air Compressor 2, but this does not prove equivalence to the frozen domestic '青春版2 2026新款' on Temu or AliExpress.","classification":"INFERENCE","source_ids":["S21"],"confidence":"medium","counterevidence":"The global product could be related or identical hardware, but exact domestic naming/version mapping was not directly verified."},
    {"claim_id":"K06","claim":"Naturehike officially sells Cloud Up Pro 2 as a 2-person tent with 20D nylon components, but the frozen grey-red aggregate variant remains insufficiently mapped for exact classification.","classification":"FACT","source_ids":["S22","S28"],"confidence":"high","counterevidence":"Model-family identity is strong; color/aggregate variant identity is the unresolved component."},
    {"claim_id":"K07","claim":"Bambu Lab's US A1 listing is a US-market listing shipped from a US warehouse and therefore cannot be substituted for the frozen 'A1 单机 大陆版' exact variant without regional-equivalence proof.","classification":"INFERENCE","source_ids":["S23"],"confidence":"high","counterevidence":"Core hardware specifications may overlap, but the frozen sample explicitly includes mainland-region identity."},
    {"claim_id":"K08","claim":"Community reports describe Bambu A1-family region/account binding issues, reinforcing the need to keep region as an exact-match dimension.","classification":"FACT","source_ids":["S26"],"confidence":"medium","counterevidence":"Community reports are not manufacturer policy documents and do not establish behavior for every serial number or firmware version."},
    {"claim_id":"K09","claim":"Creality's Space Pi V2 Plus official page distinguishes plug-specific item numbers including US Plug 4005010154, so the frozen mainland version cannot be treated as a US exact offer without variant proof.","classification":"FACT","source_ids":["S24"],"confidence":"high","counterevidence":"Plug differences alone may not imply deeper hardware differences, but they are sufficient to prevent automatic exact-bucket assignment."},
    {"claim_id":"K10","claim":"No A/B/C marketplace savings, tariffs or delivered-cost comparisons can be computed for this batch from verified Temu/AliExpress offers.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"None; doing so would require inventing missing marketplace offer components."}
  ],
  "coverage":[
    {"sku_id":"C13-S01","category_id":"C13","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"70MAI M800Pro","source_ids":["S01"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified; no snippet used."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"70MAI M800Pro","source_ids":["S02"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified; no snippet used."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen verified-head retained; global M800 evidence cannot substitute for M800Pro exact regional/bundle proof."]},
    {"sku_id":"C13-S02","category_id":"C13","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DDPAI MINI Pro 4K","source_ids":["S03"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DDPAI MINI Pro 4K","source_ids":["S04"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen verified-head retained; official global MINI PRO 4K does not by itself lock the frozen 360-degree/no-card package."]},
    {"sku_id":"C13-S03","category_id":"C13","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"70mai Cordless Air Compressor 2 / 青春版2","source_ids":["S05"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"70mai Cordless Air Compressor 2 / 青春版2","source_ids":["S06"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Opportunity sample remains non-head; global Cordless Air Compressor 2 cannot be assumed exact to 青春版2 2026新款."]},
    {"sku_id":"C14-S01","category_id":"C14","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"MOBI GARDEN NXZQU61017 Cold Mountain 2 Plus","source_ids":["S07"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"MOBI GARDEN NXZQU61017 Cold Mountain 2 Plus","source_ids":["S08"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen head_status_verified=false retained; no marketplace evidence obtained."]},
    {"sku_id":"C14-S02","category_id":"C14","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Li-Ning Zhan Ji 5000 4U / 战戟5000 4U 空拍","source_ids":["S09"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Li-Ning Zhan Ji 5000 4U / 战戟5000 4U 空拍","source_ids":["S10"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen 4U unstrung exact variant retained; no stringing/bundle assumptions made."]},
    {"sku_id":"C14-S03","category_id":"C14","head_status_verified":false,"exact_variant_verified":false,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Naturehike Cloud Up Pro 2 20D / 云尚PRO 2人 20D","source_ids":["S11"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Naturehike Cloud Up Pro 2 20D / 云尚PRO 2人 20D","source_ids":["S12"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen exact_variant_verified=false retained; official global 2-person/20D evidence does not resolve grey-red aggregate mapping."]},
    {"sku_id":"C15-S01","category_id":"C15","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Bambu Lab P2S Combo","source_ids":["S13"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Bambu Lab P2S Combo","source_ids":["S14"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen verified-head retained; general US P2S availability is not evidence of Temu/AliExpress P2S Combo coverage."]},
    {"sku_id":"C15-S02","category_id":"C15","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Bambu Lab A1 3D printer mainland version","source_ids":["S15"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Bambu Lab A1 3D printer mainland version","source_ids":["S16"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen mainland-version identity retained; US A1 listing is not treated as exact."]},
    {"sku_id":"C15-S03","category_id":"C15","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Creality Space Pi V2 Plus mainland version","source_ids":["S17"]}],"access_limitations":["Direct Temu search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Creality Space Pi V2 Plus mainland version","source_ids":["S18"]}],"access_limitations":["Direct AliExpress US search page inaccessible; no PDP verified."],"exact_offering_observed":null,"oem_observed":null,"comparable_observed":null,"reseller_only_observed":null,"us_warehouse_evidence":null,"inventory":null,"ordinary_delivered_price":null},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen opportunity/non-head identity retained; official US plug has distinct item number, so no regional exact substitution."]}
  ],
  "data_gaps":[
    {"gap":"Temu original search/PDP access","affected_cells":9,"status":"BLOCKED"},
    {"gap":"AliExpress original search/PDP access","affected_cells":9,"status":"BLOCKED"},
    {"gap":"seller/item/variant/inventory/US-warehouse evidence","affected_cells":18,"status":"UNOBSERVED_DUE_TO_BLOCK"},
    {"gap":"ordinary delivered USD price to ZIP10001 and shipping components","affected_cells":18,"status":"UNOBSERVED_DUE_TO_BLOCK"},
    {"gap":"weight/dimensions/tariff classification/tariff source","affected_cells":18,"status":"UNOBSERVED_DUE_TO_BLOCK"},
    {"gap":"four shipment-structure definitions","affected_cells":18,"status":"NOT_SUPPLIED_IN_BATCH_INSTRUCTION"}
  ]
}
```