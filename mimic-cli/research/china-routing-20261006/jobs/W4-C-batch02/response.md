## 1. 直接回答

本批次 **WEB RESEARCH AVAILABLE**，但 Temu/AliExpress 的直接商品核验均受到页面渲染/访问限制。9 个冻结 SKU × 2 平台＝18 个 platform-SKU 单元均已做明确搜索；在“必须打开原始页、不得用 snippet 推价/库存”的口径下，**0/18 可升级为 EXACT/OEM/COMPARABLE_OBSERVED，18/18 直接核验缺失，缺失率 100%**。这绝不等于 18 个商品均无货或平台无覆盖；尤其 AliExpress 已出现若干明确二级索引线索，但原商品页打开失败。([Invalid URL]())

冻结前状态原样保留：C04-S01/S02、C05-S01/S02、C06-S01/S02 的 `head_status_verified=true`；S03 三款均为 false；9 款 `exact_variant_verified` 均为 true。未把任何机会款升级成 verified-head。

## 2. 证据表

| SKU | 冻结 head/exact | Temu | AliExpress | 本批次关键结果 |
|---|---|---|---|---|
| C04-S01 ASUS 破晓 | T/T | BLOCKED | BLOCKED | 未取得可读原商品页 |
| C04-S02 GMK EVO-X2 | T/T | BLOCKED | BLOCKED | Ali 有 exact-title/item-ID 线索，原页被挡 |
| C04-S03 Beelink SER8 | F/T | BLOCKED | BLOCKED | Ali 线索为 8745HS 32GB+1TB，非冻结裸机 |
| C05-S01 Samsung 990 EVO Plus | T/T | BLOCKED | BLOCKED | 未核到可读 marketplace 原页 |
| C05-S02 Xiaomi BE6500 | T/T | BLOCKED | BLOCKED | Ali item-ID 线索存在，原页被挡 |
| C05-S03 KINGBANK 银爵 | F/T | BLOCKED | BLOCKED | 无可直接核验原页 |
| C06-S01 Lolli Pro SE | T/T | BLOCKED | BLOCKED | Ali 搜索明显假阳性是保护壳，不是耳机 |
| C06-S02 LolliClip SE | T/T | BLOCKED | BLOCKED | Ali exact-title 线索存在，原页被挡 |
| C06-S03 Comfo Clip Q | F/T | BLOCKED | BLOCKED | 无可直接核验原页 |

Temu 的相关美国类目结果能被搜索引擎定位，但打开后为空壳/无法得到可核验字段，因此没有采用其中显示的价格或库存。[Temu](https://www.temu.com/mini-pc-5020244034103-s.html?utm_source=chatgpt.com)

## 3. 一级来源

厂商页只用于锁定身份，不替代 marketplace offering：GMK 官方活动明确列出 EVO-X2 **128GB+2TB**，并称活动购买平台限官网与 AliExpress；Beelink 美国官网确认 SER8 8745HS/Space Gray，但当前公开配置是有内存/SSD的成机，并不能证明冻结裸机捆绑；小米页确认 BE6500 是中国官网型号；三星中国页明确给出 2TB `MZ-V9S2T0BW`；漫步者官方页确认 Lolli Pro SE 与云岩白。[GMKtec](https://www.gmktec.com/pages/gmktec-zai?utm_source=chatgpt.com)

## 4. 论坛证据

论坛仅作警示。2025 年 OzBargain 讨论指出中国版 Xiaomi Wi-Fi 7 路由器可能涉及 CN 固件及频段差异，因此不能把“中国版 BE6500”静默当成美国区硬件。另一个社区旧帖的 AliExpress SER8 链接明确写的是 **8845HS barebone**，不是本冻结样本的 8745HS。[OzBargain](https://www.ozbargain.com.au/node/923545?utm_source=chatgpt.com)

## 5. 反证

AliExpress 二级索引能定位 Xiaomi BE6500、LolliClip SE，以及 GMK EVO-X2 128GB+2TB 的商品线索；但对应原始 AliExpress 页面均发生非重试型访问失败，所以不读取其索引价格、卖家、库存或配送。Beelink 索引条目为 32GB+1TB，也不能因同 CPU/机型就划入 A exact。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005012374999592?utm_source=chatgpt.com)

## 6. 置信度

对“冻结 SKU/头部状态未改变”和“本环境无法直接核验两个平台”的结论为 **high**；对 AliExpress 可能存在若干商品条目的判断为 **medium**；对任一当前普通价、ZIP10001 配送、库存、卖家、US warehouse 均无可报告置信度。

## 7. 缺口

全部 offer 的 seller、stock、warehouse、ordinary price、delivery、重量/尺寸、关税分类及来源均保持 `null`。比较端点预定义为**送达 ZIP10001 的公开普通商品价+公开普通运费，US sales tax 不计入，除非未登录公开页明确报价**；本批次没有足够报价，因此不估税、不估关税、不造 savings。协调器既有四种 shipment structure 应分别保留 null，而不是合并或推断。

## 8. 意外发现

最有价值的是 **GMK 官方自己确认 AliExpress 是 EVO-X2 128GB+2TB 的购买渠道**，说明“平台可能覆盖”与“本次已实际观察到 offering”是两个不同命题。[GMKtec](https://www.gmktec.com/pages/gmktec-zai?utm_source=chatgpt.com)

## 9. 自我反驳

本结果很可能低估真实覆盖：BLOCKED 不是 unavailable，0 个 verified offer 也不是 0 个 marketplace offer。反过来，二级索引出现型号也不能证明今天仍有库存、更不能证明可送 ZIP10001；因此没有把它们升级成 A/B/C 或计算跨境节省。

## 10. 下一实验

下一轮只需用**未登录、美国区、ZIP10001 的干净浏览器**复核已定位的 AliExpress item `1005011904874318`（EVO-X2）、`1005012374999592`（BE6500）、`1005013110936399`（LolliClip SE），以及 SER8 线索的实际 variant selector；同时重复 9 个 Temu exact 搜索。只记录公开 seller、variant、ship-from、stock、普通价格和配送，不登录、不下单、不换 SKU。

```json
{
  "job_id":"W4-C-batch02",
  "parent_replicate":"W4-C",
  "web_research_available":true,
  "pre_freeze_compliance":true,
  "frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "assigned_sku_ids":["C04-S01","C04-S02","C04-S03","C05-S01","C05-S02","C05-S03","C06-S01","C06-S02","C06-S03"],
  "categories":[
    {"category_id":"C04","status":"coverage_unresolved_due_marketplace_access"},
    {"category_id":"C05","status":"coverage_unresolved_due_marketplace_access"},
    {"category_id":"C06","status":"coverage_unresolved_due_marketplace_access"}
  ],
  "batch_counts":{"sku_count":9,"platform_sku_cells":18,"direct_verified_offering_cells":0,"blocked_cells":18,"direct_observation_gap_rate":1.0},
  "cost_methodology":{
    "destination":"US ZIP10001",
    "comparison_endpoint":"ordinary_public_item_price_plus_public_ordinary_shipping_before_US_sales_tax",
    "us_sales_tax_treatment":"excluded_unless_explicitly_quoted_on_public_logged-out_page",
    "tariff_rates":"not_estimated",
    "four_shipment_structures":"coordinator-defined structures preserved separately as null because no verified quote was obtained"
  },
  "sources":[
    {"source_id":"S01","url":null,"source_ref":"turn650119search0","title":"GMKtec x Z.AI campaign: EVO-X2 128GB+2TB and AliExpress purchase-platform statement","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S02","url":null,"source_ref":"turn193454search11","title":"Beelink US SER8 Ryzen 7 8745HS","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S03","url":null,"source_ref":"turn631315view0","title":"Xiaomi Router BE6500 China official page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},
    {"source_id":"S04","url":null,"source_ref":"turn832806view0","title":"Samsung 990 EVO Plus 2TB MZ-V9S2T0BW China page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S05","url":null,"source_ref":"turn193454search10","title":"EDIFIER Lolli Pro SE official page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"S06","url":null,"source_ref":"turn371742view0","title":"Temu US mini-PC result/index page","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S07","url":null,"source_ref":"turn371742view1","title":"Temu US 2TB SSD result/index page","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S08","url":null,"source_ref":"turn371742view2","title":"Temu US router/internet result/index page","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S09","url":null,"source_ref":"turn371742view3","title":"Temu DDR5 product page lead","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S10","url":null,"source_ref":"turn972512view0","title":"AliExpress item 1005011904874318 direct-open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
    {"source_id":"S11","url":null,"source_ref":"turn736342view0","title":"AliExpress item 1005009535991864 direct-open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
    {"source_id":"S12","url":null,"source_ref":"turn845113view0","title":"AliExpress item 1005012374999592 direct-open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
    {"source_id":"S13","url":null,"source_ref":"turn845113view1","title":"AliExpress item 1005013110936399 direct-open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
    {"source_id":"S14","url":null,"source_ref":"turn570317view1","title":"Secondary AliExpress index lead for GMKtec EVO-X2 128GB/2TB","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S15","url":null,"source_ref":"turn650119search3","title":"Secondary AliExpress index lead for Xiaomi BE6500","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S16","url":null,"source_ref":"turn650119search8","title":"Secondary AliExpress index lead for EDIFIER LolliClip SE","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S17","url":null,"source_ref":"turn528291search2","title":"Secondary AliExpress index lead for Beelink SER8 8745HS 32GB/1TB","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S18","url":null,"source_ref":"turn528291search0","title":"AliExpress-indexed protective case for Lolli Pro SE, not the earbuds","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K09"]},
    {"source_id":"S19","url":null,"source_ref":"turn427880view4","title":"Wykop discussion linking AliExpress SER8 8845HS barebone","published_at":"2024-12-09","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K10"]},
    {"source_id":"S20","url":null,"source_ref":"turn650119search10","title":"OzBargain discussion of China-region Xiaomi routers","published_at":"2025-09-10","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K11"]}
  ],
  "claims":[
    {"claim_id":"K01","claim":"All 18 platform-SKU direct-verification cells remained blocked/page-shell limited; no marketplace offer was promoted to verified observed status.","classification":"FACT","source_ids":["S06","S07","S08","S09","S10","S11","S12","S13"],"confidence":"high","counterevidence":"Secondary indexes indicate some AliExpress listing leads, so blocked must not be interpreted as unavailable."},
    {"claim_id":"K02","claim":"GMKtec's official campaign identifies EVO-X2 128GB+2TB and states eligible purchases can come from its official website or AliExpress.","classification":"FACT","source_ids":["S01"],"confidence":"high","counterevidence":"This does not establish current AliExpress seller, price, stock, US delivery or warehouse."},
    {"claim_id":"K03","claim":"Beelink's US page confirms SER8 8745HS and Space Gray, but its displayed bundles are not the frozen barebone configuration.","classification":"FACT","source_ids":["S02"],"confidence":"high","counterevidence":"US official configuration is not evidence that a China-region barebone marketplace variant is identical."},
    {"claim_id":"K04","claim":"Xiaomi BE6500 identity is confirmed on Xiaomi's China site; US-region equivalence was not assumed.","classification":"FACT","source_ids":["S03"],"confidence":"high","counterevidence":"No direct AliExpress or Temu region/firmware selector was accessible."},
    {"claim_id":"K05","claim":"Samsung China identifies 990 EVO Plus 2TB as MZ-V9S2T0BW.","classification":"FACT","source_ids":["S04"],"confidence":"high","counterevidence":"Manufacturer identity does not prove marketplace coverage."},
    {"claim_id":"K06","claim":"EDIFIER's official page confirms Lolli Pro SE and the 云岩白 color option.","classification":"FACT","source_ids":["S05"],"confidence":"high","counterevidence":"Manufacturer identity does not prove Temu/AliExpress coverage."},
    {"claim_id":"K07","claim":"Secondary indexes locate AliExpress leads for EVO-X2, BE6500 and LolliClip SE, but the original AliExpress item pages could not be opened.","classification":"FACT","source_ids":["S10","S12","S13","S14","S15","S16"],"confidence":"medium","counterevidence":"No seller, stock, price, warehouse or ZIP10001 delivery field was verified."},
    {"claim_id":"K08","claim":"A Beelink SER8 8745HS AliExpress-indexed lead showed a 32GB/1TB bundle rather than the frozen barebone bundle.","classification":"FACT","source_ids":["S11","S17"],"confidence":"medium","counterevidence":"Variant selector on the original marketplace page could not be inspected."},
    {"claim_id":"K09","claim":"A Lolli Pro SE AliExpress search lead was a protective case rather than the frozen earbuds.","classification":"FACT","source_ids":["S18"],"confidence":"high","counterevidence":"It does not rule out a separate earbuds listing."},
    {"claim_id":"K10","claim":"The community SER8 AliExpress link discussed an 8845HS barebone, not the frozen 8745HS variant.","classification":"FACT","source_ids":["S19"],"confidence":"medium","counterevidence":"It is an old community post and is not current marketplace availability evidence."},
    {"claim_id":"K11","claim":"Community discussion warns that some China-market Xiaomi Wi-Fi 7 routers may differ in firmware and radio-band behavior from local-market hardware.","classification":"FACT","source_ids":["S20"],"confidence":"low","counterevidence":"This is community evidence and was not verified for the specific frozen BE6500 unit."}
  ],
  "coverage":[
    {"sku_id":"C04-S01","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 破晓 mini PC i5-13500H 16GB 512GB Wi-Fi 6","Temu US mini-PC result/index and direct exact-search attempt"],"access_limitations":["original search/result rendering was inaccessible or page-shell only; no price/spec/seller/stock inferred"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 破晓 mini PC i5-13500H 16GB 512GB Wi-Fi 6","AliExpress direct search attempt"],"access_limitations":["AliExpress search endpoint inaccessible; no original item page verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen SKU retained; absence not treated as unavailability."]},
    {"sku_id":"C04-S02","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["GMKtec EVO-X2 Ryzen AI Max+ 395 128GB 2TB"],"access_limitations":["Temu original exact-search/product rendering not verifiable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["GMKtec EVO-X2 Ryzen AI Max+ 395 128GB 2TB","candidate item 1005011904874318 direct-open attempt"],"access_limitations":["candidate exact-title lead exists but original AliExpress page is blocked"]},"china_head_us_middle_tail_status":"unresolved","caveats":["GMK official source supports AliExpress as a purchase channel but not current offer fields.","No secondary-index price used."]},
    {"sku_id":"C04-S03","category_id":"C04","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Beelink SER8 8745HS Space Gray barebone"],"access_limitations":["Temu original search/product details not verifiable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Beelink SER8 8745HS barebone","candidate item 1005009535991864 direct-open attempt"],"access_limitations":["original AliExpress item blocked"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Secondary candidate was 32GB/1TB, not frozen barebone; not bucket A.","Old community Ali link was 8845HS, not 8745HS."]},
    {"sku_id":"C05-S01","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Samsung 990 EVO Plus 2TB MZ-V9S2T0BW"],"access_limitations":["Temu 2TB SSD page opened as page shell; no exact product page verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Samsung 990 EVO Plus 2TB MZ-V9S2T0BW"],"access_limitations":["AliExpress direct search inaccessible; no original marketplace offer verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Samsung manufacturer identity confirmed separately; marketplace availability unresolved."]},
    {"sku_id":"C05-S02","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Xiaomi BE6500 Wi-Fi 7 6500 2.5G"],"access_limitations":["Temu router result/index could not provide verifiable original offer details"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Xiaomi BE6500 Wi-Fi 7","candidate item 1005012374999592 direct-open attempt"],"access_limitations":["secondary exact-title lead exists; original AliExpress item blocked"]},"china_head_us_middle_tail_status":"unresolved","caveats":["China-region firmware/hardware equivalence to any US-market version not assumed.","No indexed price used."]},
    {"sku_id":"C05-S03","category_id":"C05","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["KINGBANK 银爵 32GB 16GBx2 DDR5-6000 C36"],"access_limitations":["related DDR5 page was not the frozen SKU and original exact-search rendering was unavailable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["KINGBANK Silver DDR5 6000 32GB 16GBx2 C36"],"access_limitations":["AliExpress direct search inaccessible; no exact original product page verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Generic DDR5 results were not used as OEM or comparable evidence."]},
    {"sku_id":"C06-S01","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Lolli Pro SE 云岩白 ANC"],"access_limitations":["Temu exact product page not verifiable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Lolli Pro SE white ANC"],"access_limitations":["direct platform search inaccessible; indexed result located an accessory case only"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Protective case is a false positive and was not counted as reseller coverage of the earbuds."]},
    {"sku_id":"C06-S02","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER LolliClip SE 云霜金 open-ear clip"],"access_limitations":["Temu original exact-offer details unavailable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER LolliClip SE","candidate item 1005013110936399 direct-open attempt"],"access_limitations":["exact-title secondary lead exists; original AliExpress page blocked, color/region/bundle not verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["No secondary price, stock or seller adopted."]},
    {"sku_id":"C06-S03","category_id":"C06","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Comfo Clip Q 奶霜白"],"access_limitations":["Temu direct exact-offer rendering unavailable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Comfo Clip Q cream white"],"access_limitations":["AliExpress direct search inaccessible; no original offer verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Domestic and other-market listings were not substituted for Temu/AliExpress coverage."]}
  ],
  "data_gaps":[
    "No directly verified Temu or AliExpress offer for any assigned SKU.",
    "Seller, current stock, US-warehouse evidence, ordinary public price and ZIP10001 delivery are null.",
    "No member price, coupon, targeted subsidy or logged-in price was used.",
    "Weight, dimensions, tariff classification/source and tariff amount remain null.",
    "No A/B/C savings statistics were computed.",
    "Blocked and not-proven-unavailable remain distinct; no SKU received VERIFIED_UNAVAILABLE.",
    "All four coordinator-defined shipment structures remain separately unfilled rather than estimated."
  ]
}
```