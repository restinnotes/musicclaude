## 1. 直接回答

本批次 **9 个冻结 SKU × 2 平台 = 18 个平台-SKU 单元**均完成一次明确检索，并尝试打开平台原始搜索/商品页。结果是 **Temu 9/9、AliExpress 9/9 均在原站页面访问阶段 BLOCKED**；因此本批次实际核验到的 A exact、B same-OEM、C comparable、reseller-only offer 都是 **0 个“已观察”**，但这**绝不等于平台无货或无覆盖**。Temu 的 9 个原站入口均不可读；AliExpress 同样如此。([Invalid URL]()) ([Invalid URL]())

## 2. 证据表

| SKU | 冻结 head | 冻结 exact | Temu | AliExpress |
|---|---:|---:|---|---|
| C10-S01 | true | true | BLOCKED / 0 offer | BLOCKED / 0 |
| C10-S02 | true | true | BLOCKED / 0 | BLOCKED / 0 |
| C10-S03 | false | true | BLOCKED / 0 | BLOCKED / 0 |
| C11-S01 | true | true | BLOCKED / 0 | BLOCKED / 0 |
| C11-S02 | true | true | BLOCKED / 0 | BLOCKED / 0 |
| C11-S03 | false | true | BLOCKED / 0 | BLOCKED / 0 |
| C12-S01 | true | true | BLOCKED / 0 | BLOCKED / 0 |
| C12-S02 | true | true | BLOCKED / 0 | BLOCKED / 0 |
| C12-S03 | false | true | BLOCKED / 0 | BLOCKED / 0 |

## 3. 一级来源

厂商来源只用于守住 exact 边界，不代替平台覆盖证据。DJI 官方页明确 ROMO P Water Tank Version 为透明机器人+透明基站；Sony 官方帮助页明确 ILCE-7CM2=α7C II、ILCE-7M5=α7 V；Insta360 官方资料确认 GO 3S 有 64GB、Arctic White，官方商店又把 Standard Bundle 与其他套装分开。[DJI Store](https://store.dji.com/au/product/dji-romo-p-water-tank-version?from=store_homepage)

WORX 官方/说明书资料还显示 WU130X 系列套装不能粗暴合并：WU130X.1 对应单电配置，而 WU130X 可对应双电，支持冻结样本继续严格钉住 **WU130X.1 2.0Ah 单电**。[Worx](https://www.worx.cn/content/details26_9742.html)

## 4. 论坛证据

Reddit 能看到 ROMO P 与 GO 3S 的真实用户使用/售后讨论，但没有任何材料能证明对应 Temu/AliExpress exact listing、美国仓、库存或 ZIP10001 成交价，因此未升级为 coverage offer。[Reddit](https://www.reddit.com/r/RobotVacuums/comments/1txt7ju/dji_romo_p/?utm_source=chatgpt.com)

## 5. 反证

AliExpress 的外部价格追踪页曾索引一个带 “DJI ROMO P/S/A” 字样的条目，但全文实际是滚刷、边刷、滤芯、拖布、尘袋等**兼容配件**，不是 ROMO P 整机；其 AliExpress 原 item 页又无法打开。因此它既不是 A exact，也不是 B OEM，更不能用其价格证明整机覆盖。[Pricearchive.org](https://he.pricearchive.org/aliexpress.com/item/1005010313425811)

## 6. 置信度

对“本研究环境原始平台页被阻断”的判断为**高置信度**；对“Temu/AliExpress 实际是否存在这些 SKU”的判断为**低置信度/未解决**。没有任何 SKU 达到 `VERIFIED_UNAVAILABLE`，也没有把外部 snippet、搜索为空或页面壳解释成缺货。

## 7. 缺口

本批次 18/18 单元均未核验 seller、item、库存、US warehouse、公开普通价、运费、ZIP10001 delivered price、重量尺寸对应物流报价或关税分类。因此这些字段缺失率为 **100%**。比较端点仍固定为 **美国 ZIP10001 的普通公开 delivered price**；美国 sales tax 默认不计入跨平台比较，除非页面明确把强制税额包含在显示总价中——本批次没有观察到这种报价。四种 shipment structure 保留为四个独立空槽，不自行猜定义或费用。

## 8. 意外发现

最有用的非覆盖发现是 **WU130X 与 WU130X.1 的电池套装差异足以改变 exact 判断**；另外 ROMO P 的 Water Tank Version、GO 3S 的颜色/容量/Standard Bundle 都证明“型号关键词命中”远不足以判定 A 桶。

## 9. 自我反驳

外部搜索零结果可能是假阴性，平台也可能因地区、机器人访问策略、会话或索引方式隐藏实际 listing。因此 18 个 `BLOCKED` 不能推出“海外没有卖”，也不能据此计算中国头部—美国中尾部覆盖率或任何节省比例。

## 10. 下一实验

下一次只需在能匿名读取 Temu/AliExpress 原站的环境中，对同一 18 个单元各再做一次固定搜索，并将目的地设为 ZIP10001；只记录原页直接显示的型号/版本/卖家/库存/仓库/普通价/运费。遇登录墙或阻断立即停止，不换“更容易搜”的型号，不跨 A/B/C 桶。

以下 JSON 中 `url` 对无法完整读取或本界面以引用标识追溯的来源保留 `null`，另存 `web_ref`；这避免把“尝试访问的地址”伪装成已经读到的原始页面。

```json
{
  "job_id":"W4-A-batch04",
  "parent_replicate":"W4-A",
  "web_research_available":true,
  "pre_freeze_compliance":true,
  "frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "assigned_sku_ids":["C10-S01","C10-S02","C10-S03","C11-S01","C11-S02","C11-S03","C12-S01","C12-S02","C12-S03"],
  "categories":[
    {"category_id":"C10","status":"TEMU_AND_ALIEXPRESS_PRIMARY_ACCESS_BLOCKED"},
    {"category_id":"C11","status":"TEMU_AND_ALIEXPRESS_PRIMARY_ACCESS_BLOCKED"},
    {"category_id":"C12","status":"TEMU_AND_ALIEXPRESS_PRIMARY_ACCESS_BLOCKED"}
  ],
  "batch_observation_counts":{
    "assigned_skus":9,
    "platform_sku_cells":18,
    "EXACT_OBSERVED":0,
    "OEM_OBSERVED":0,
    "COMPARABLE_ONLY":0,
    "RESELLER_ONLY":0,
    "NOT_OBSERVED":0,
    "BLOCKED":18,
    "LOGIN_REQUIRED":0,
    "VERIFIED_UNAVAILABLE":0,
    "verified_offer_cells":0,
    "seller_missing_cells":18,
    "item_missing_cells":18,
    "inventory_missing_cells":18,
    "us_warehouse_missing_cells":18,
    "zip10001_delivered_price_missing_cells":18,
    "core_offer_field_missing_rate":1.0
  },
  "comparison_endpoint":{
    "destination":"US ZIP10001",
    "price_basis":"ordinary public delivered price",
    "member_or_targeted_prices":"separate; none observed",
    "china_88vip_or_subsidy":"separate; none observed",
    "us_sales_tax":"excluded unless explicitly included in displayed mandatory delivered total",
    "observed_destination_specific_quotes":0
  },
  "shipment_structures":[
    {"slot":1,"definition":null,"status":"PRESERVED_SEPARATELY; DEFINITION_NOT_SUPPLIED_IN_BATCH_PROMPT; NO_VERIFIED_OFFER","observed_cost":null},
    {"slot":2,"definition":null,"status":"PRESERVED_SEPARATELY; DEFINITION_NOT_SUPPLIED_IN_BATCH_PROMPT; NO_VERIFIED_OFFER","observed_cost":null},
    {"slot":3,"definition":null,"status":"PRESERVED_SEPARATELY; DEFINITION_NOT_SUPPLIED_IN_BATCH_PROMPT; NO_VERIFIED_OFFER","observed_cost":null},
    {"slot":4,"definition":null,"status":"PRESERVED_SEPARATELY; DEFINITION_NOT_SUPPLIED_IN_BATCH_PROMPT; NO_VERIFIED_OFFER","observed_cost":null}
  ],
  "cost_component_policy":{
    "product_price":null,
    "shipping":null,
    "currency":null,
    "observation_date":null,
    "offer_variant":null,
    "weight":null,
    "dimensions":null,
    "tariff_classification":null,
    "tariff_source":null,
    "tariff_rate":null,
    "quote_assumptions":[],
    "reason":"No marketplace offer was verifiably opened; no missing component, tariff, landed cost or savings was imputed."
  },
  "sources":[
    {"source_id":"T01","url":null,"web_ref":"turn777103view0","title":"Temu original search attempt — C10-S01 Roborock P20 Max A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T02","url":null,"web_ref":"turn777103view1","title":"Temu original search attempt — C10-S02 Roborock P20 Max A2950RR automatic-water variant","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T03","url":null,"web_ref":"turn777103view2","title":"Temu original search attempt — C10-S03 DJI ROMO P Water Tank","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T04","url":null,"web_ref":"turn777103view3","title":"Temu original search attempt — C11-S01 DZC1050-26BT","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T05","url":null,"web_ref":"turn777103view4","title":"Temu original search attempt — C11-S02 WJZ1601S","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T06","url":null,"web_ref":"turn777103view5","title":"Temu original search attempt — C11-S03 WU130X.1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T07","url":null,"web_ref":"turn777103view6","title":"Temu original search attempt — C12-S01 Sony A7C II 28-60 silver","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T08","url":null,"web_ref":"turn777103view7","title":"Temu original search attempt — C12-S02 Sony ILCE-7M5 Alpha 7 V","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"T09","url":null,"web_ref":"turn777103view8","title":"Temu original search attempt — C12-S03 Insta360 GO 3S 64GB white","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},

    {"source_id":"A01","url":null,"web_ref":"turn802572view0","title":"AliExpress original search attempt — C10-S01 Roborock P20 Max A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A02","url":null,"web_ref":"turn802572view1","title":"AliExpress original search attempt — C10-S02 Roborock P20 Max A2950RR automatic-water variant","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A03","url":null,"web_ref":"turn802572view2","title":"AliExpress original search attempt — C10-S03 DJI ROMO P Water Tank","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A04","url":null,"web_ref":"turn802572view3","title":"AliExpress original search attempt — C11-S01 DZC1050-26BT","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A05","url":null,"web_ref":"turn802572view4","title":"AliExpress original search attempt — C11-S02 WJZ1601S","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A06","url":null,"web_ref":"turn802572view5","title":"AliExpress original search attempt — C11-S03 WU130X.1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A07","url":null,"web_ref":"turn802572view6","title":"AliExpress original search attempt — C12-S01 Sony A7C II 28-60 silver","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A08","url":null,"web_ref":"turn802572view7","title":"AliExpress original search attempt — C12-S02 Sony ILCE-7M5 Alpha 7 V","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A09","url":null,"web_ref":"turn802572view8","title":"AliExpress original search attempt — C12-S03 Insta360 GO 3S 64GB white","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A10","url":null,"web_ref":"turn547254view0","title":"AliExpress original item 1005010313425811 access attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K03"]},

    {"source_id":"S19","url":null,"web_ref":"turn463277view0","title":"PriceArchive mirror/index for AliExpress item 1005010313425811 — DJI ROMO compatible spare parts","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"M01","url":null,"web_ref":"turn903236view0","title":"DJI ROMO P Water Tank Version — DJI official store","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},
    {"source_id":"M02","url":null,"web_ref":"turn548558view2","title":"WORX WU130X product information — WORX China","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"M03","url":null,"web_ref":"turn254330view0","title":"WU130X/WU130X.1 instruction manual, technical-data page screenshot","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"M04","url":null,"web_ref":"turn505528view0","title":"Sony ILCE-7CM2 α7C II Help Guide","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"M05","url":null,"web_ref":"turn505528view1","title":"Sony ILCE-7M5 α7 V Help Guide","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"M06","url":null,"web_ref":"turn548558view5","title":"Insta360 GO 3S hardware specifications","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"M07","url":null,"web_ref":"turn548558view6","title":"Insta360 GO 3S official store configuration page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"F01","url":null,"web_ref":"turn112969reddit0","title":"Reddit discussion — DJI ROMO P","published_at":"2026-06-05","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"F02","url":null,"web_ref":"turn980332reddit5","title":"Reddit discussion — Insta360 GO 3S","published_at":"2026-08-26","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]}
  ],
  "claims":[
    {"claim_id":"K01","claim":"All nine assigned Temu SKU searches reached an inaccessible original-platform page state; no Temu offer was promoted from snippets or third-party pages.","classification":"FACT","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09"],"confidence":"high","counterevidence":"External search non-results cannot establish marketplace absence."},
    {"claim_id":"K02","claim":"All nine assigned AliExpress SKU searches reached an inaccessible original-platform page state; no AliExpress offer was directly verified.","classification":"FACT","source_ids":["A01","A02","A03","A04","A05","A06","A07","A08","A09"],"confidence":"high","counterevidence":"Blocked access cannot distinguish an existing but inaccessible listing from no listing."},
    {"claim_id":"K03","claim":"The externally indexed AliExpress item associated with DJI ROMO wording describes compatible spare parts rather than the ROMO P robot, while its original AliExpress item page was inaccessible; it is not counted as an offer.","classification":"FACT","source_ids":["S19","A10"],"confidence":"high","counterevidence":"None sufficient to upgrade the item to a robot listing."},
    {"claim_id":"K04","claim":"DJI's official page identifies ROMO P Water Tank Version as the transparent robot plus transparent base-station variant; this is used only as an exact-variant boundary.","classification":"FACT","source_ids":["M01"],"confidence":"high","counterevidence":"Manufacturer identity does not prove Temu or AliExpress coverage."},
    {"claim_id":"K05","claim":"WORX documentation supports distinguishing WU130X.1 single-battery packaging from WU130X dual-battery packaging, so bundle identity is material to bucket A.","classification":"FACT","source_ids":["M02","M03"],"confidence":"high","counterevidence":"This does not demonstrate a marketplace listing."},
    {"claim_id":"K06","claim":"Sony official help guides identify ILCE-7CM2 as α7C II and ILCE-7M5 as α7 V; these identifiers constrain exact-model matching only.","classification":"FACT","source_ids":["M04","M05"],"confidence":"high","counterevidence":"Kit color/lens/body configuration still must be verified on the marketplace offer itself."},
    {"claim_id":"K07","claim":"Insta360 official sources establish GO 3S 64GB and Arctic White configurations and distinguish Standard Bundle from other bundles.","classification":"FACT","source_ids":["M06","M07"],"confidence":"high","counterevidence":"Official configuration availability does not establish marketplace coverage."},
    {"claim_id":"K08","claim":"Community discussions provide ownership/use evidence for ROMO P and GO 3S but do not verify Temu/AliExpress seller, item, inventory, warehouse or delivered price.","classification":"INFERENCE","source_ids":["F01","F02"],"confidence":"high","counterevidence":"A community post linking a readable exact marketplace item could change this, but none was verified here."},
    {"claim_id":"K09","claim":"Because original marketplace pages were blocked, A/B/C/reseller classification, seller/item, inventory, US warehouse and ZIP10001 delivered price remain unobserved for every platform-SKU cell.","classification":"INFERENCE","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09","A01","A02","A03","A04","A05","A06","A07","A08","A09"],"confidence":"high","counterevidence":"Successful future anonymous original-page access could resolve these fields."}
  ],
  "data_gaps":[
    "Temu original search/product content inaccessible for all 9 assigned SKUs.",
    "AliExpress original search/product content inaccessible for all 9 assigned SKUs.",
    "No verified seller, item ID, inventory, US-warehouse evidence, ordinary price, shipping charge or ZIP10001 delivered total.",
    "No verified marketplace offer from which to attach weight, dimensions, shipment structure, tariff classification/source/rate or quote assumptions.",
    "The batch prompt requires preservation of four shipment structures but does not define their names; four distinct null slots are therefore retained rather than invented."
  ],
  "coverage":[
    {"sku_id":"C10-S01","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact model: Roborock P20 Max A2950RR","non-automatic-water/water-tank variant","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; seller/item/spec/inventory/warehouse/price/delivery not inferred from snippets."],"source_ids":["T01"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact model: Roborock P20 Max A2950RR","non-automatic-water/water-tank variant","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; no cross-platform inference from Temu or external search."],"source_ids":["A01"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C10-S02","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact model: Roborock P20 Max A2950RR","automatic-water-line variant","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; automatic-water version not merged with non-automatic-water version."],"source_ids":["T02"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact model: Roborock P20 Max A2950RR","automatic-water-line variant","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; no price, seller, inventory or US-warehouse inference."],"source_ids":["A02"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C10-S03","category_id":"C10","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["DJI ROMO P","Water Tank Version","transparent robot plus transparent base","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; manufacturer source used only for exact-boundary checking."],"source_ids":["T03","M01"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["DJI ROMO P","Water Tank Version","transparent robot plus transparent base","original AliExpress search attempted","direct candidate item page attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform content inaccessible.","Secondary indexed candidate was compatible spare parts, not the robot, and was excluded from A/B/C offers."],"source_ids":["A03","A10","S19","M01"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen non-head status retained.","No accessory listing is treated as whole-product coverage.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C11-S01","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Dongcheng DZC1050-26BT","1050W hammer/chisel two-use, safety clutch","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; specifications and mains-voltage suitability could not be checked on an offer."],"source_ids":["T04"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Dongcheng DZC1050-26BT","1050W hammer/chisel two-use, safety clutch","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; no seller/stock/warehouse/plug/voltage claim inferred."],"source_ids":["A04"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C11-S02","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Dongcheng WJZ1601S","16V dual-battery kit","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; battery count and charger-region compatibility not inferred."],"source_ids":["T05"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Dongcheng WJZ1601S","16V dual-battery kit","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; no seller, stock, warehouse or delivered-price claim."],"source_ids":["A05"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C11-S03","category_id":"C11","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["WORX WU130X.1","12V 40Nm 2.0Ah single-battery exact bundle","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; similar WU130X dual-battery packages are not promoted to exact."],"source_ids":["T06","M02","M03"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["WORX WU130X.1","12V 40Nm 2.0Ah single-battery exact bundle","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; bundle identity could not be checked on a marketplace offer."],"source_ids":["A06","M02","M03"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen non-head status retained.","WU130X and WU130X.1 bundle differences prevent automatic exact matching.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C12-S01","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Sony Alpha 7C II / ILCE-7CM2","silver","FE 28-60mm lens kit","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; body-only, other color or other lens kits cannot be treated as exact."],"source_ids":["T07","M04"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Sony Alpha 7C II / ILCE-7CM2","silver","FE 28-60mm lens kit","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; seller, kit contents, region, stock and price remain unobserved."],"source_ids":["A07","M04"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","Official model identity alone does not establish exact silver 28-60 marketplace kit.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C12-S02","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Sony ILCE-7M5 / Alpha 7 V","body only, official standard bundle","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; kit versus body-only configuration not observable."],"source_ids":["T08","M05"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Sony ILCE-7M5 / Alpha 7 V","body only, official standard bundle","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; no seller, region, inventory, warehouse or delivered-price verification."],"source_ids":["A08","M05"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","Official ILCE-7M5=Alpha 7 V identity does not establish marketplace body-only bundle.","No unobserved field is interpreted as out-of-stock or unavailable."]},
    {"sku_id":"C12-S03","category_id":"C12","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Insta360 GO 3S","Arctic White / 灵动白","64GB","Standard Bundle","original Temu search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; different capacities, colors or bundles are not treated as exact."],"source_ids":["T09","M06","M07"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Insta360 GO 3S","Arctic White / 灵动白","64GB","Standard Bundle","original AliExpress search attempted","destination endpoint intended: US ZIP10001"],"access_limitations":["Original platform page inaccessible; exact capacity/color/bundle, seller, stock and US warehouse cannot be observed."],"source_ids":["A09","M06","M07"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen non-head status retained.","Official 64GB Arctic White/Standard Bundle boundary is not marketplace coverage evidence.","No unobserved field is interpreted as out-of-stock or unavailable."]}
  ]
}
```