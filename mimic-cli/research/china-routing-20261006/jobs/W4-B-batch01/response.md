### 1. 直接回答

本批次仅核查冻结的 C01/C02/C03 共 9 个 SKU、Temu 与 AliExpress 两个平台。**没有任何一个平台×SKU 单元达到可从原始交易页验证的 A exact、B same-OEM 或 C comparable**。共 18 个单元中：**BLOCKED 17，LOGIN_REQUIRED 1，可用原页观察 0，关键字段缺失率 18/18=100%**。这只是本批次研究访问缺失率，**绝不是“市场无货率”或全市场覆盖率**。

冻结前 `head_status_verified`、`exact_variant_verified` 原样保留；三个 opportunity SKU 仍是 `head_status_verified=false`，没有被提升为 verified-head。

### 2. 证据表

| SKU | 冻结标记 H/E | Temu | AliExpress |
|---|---|---|---|
| C01-S01 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C01-S02 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C01-S03 | F/T | BLOCKED ([Invalid URL]()) | LOGIN_REQUIRED；候选商品原页跳登录墙 ([Invalid URL]()) |
| C02-S01 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C02-S02 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C02-S03 | F/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C03-S01 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C03-S02 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) |
| C03-S03 | F/T | BLOCKED ([Invalid URL]()) | BLOCKED；另一个疑似 Gen5 候选商品原页 403 ([Invalid URL]()) |

H=`head_status_verified`，E=`exact_variant_verified`。

### 3. 一级来源

两平台均执行了明确型号/容量/颜色或核心版本关键词搜索并尝试打开平台原始页。Temu 的精确搜索 URL 不可访问，部分被索引的美国分类页打开后只有空 HTML 壳；AliExpress 精确搜索页普遍不可读取或 403。网页壳不作为核验成功。Temu 的美国平板分类页就是这种情况。[Temu](https://www.temu.com/tablet-5010096208510-s.html?page=3)

### 4. 论坛证据

本批次**没有使用论坛或社区帖来证明 Temu/AliExpress 的价格、库存、卖家、仓库或 exact 版本**。15 分钟预算优先完成 18 个平台-SKU 单元的一次明确检索和原页访问，避免用社区转述替代交易页。

### 5. 反证

搜索索引确实能定位到若干候选链接，例如 OnePlus Ace 6T 和 Y700 Gen5，但候选链接存在并不等于商品字段已经核验；前者原页转登录，后者原页 403。[AliExpress](https://www.aliexpress.us/item/3256810319128337.html?utm_source=chatgpt.com) Temu 搜索索引也出现 iPad 候选，但原始页面正文无法读取，因此未引用其索引价格、库存或版本。[Temu](https://www.temu.com/tablet-5010096208510-s.html?page=3\&utm_source=chatgpt.com)

### 6. 置信度

对“**本次研究环境受到访问限制**”置信度高；对“这些商品实际是否在平台出售”置信度低/未决。因此没有把 BLOCKED/LOGIN_REQUIRED 转成 `VERIFIED_UNAVAILABLE`，也没有把索引候选计为 exact。

### 7. 缺口

全部 18 个单元的可审计 seller/item、精确地区版本、ZIP10001 普通公开 delivered price、库存、US warehouse、会员/新客/券、运费、重量尺寸、税费与关税基础均未能从可读原页观察，全部保留 null。未做任何 savings 计算。

### 8. 意外发现

C01-S03 的 AliExpress 候选不是普通 403，而是明确被重定向到 AliExpress 登录同步页，因此单独记为 `LOGIN_REQUIRED`。([Invalid URL]()) C03-S03 则是商品页直接 403，故仍为 `BLOCKED`。([Invalid URL]())

### 9. 自我反驳

“0 个已观察 offering”不能解释成“0 个 offering 存在”。搜索索引中的候选链接恰好说明平台可能存在相关商品；本结果只说明在无登录、不得绕过访问控制的条件下，**无法把它们审计到所要求的 exact/OEM/comparable 字段级别**。

### 10. 下一实验

下一轮只需在可正常加载的美国匿名浏览器环境重复同一冻结 SKU 和同一搜索词，目的地固定 ZIP10001；每 SKU/平台仍只检查一次关键结果页和候选商品页。只有原页实际显示型号、版本、seller/item、库存/仓库与普通公开 delivered price 时才填 offer；仍不登录、不下单、不联系卖家。比较端点定义为 **送达 ZIP10001 的普通公开价；美国销售税不估算、不并入，若结账页明确展示则单列**。四种 shipment structure 因本批次没有一个可验证报价，均保持 unresolved，不制造运费或关税率。

```json
{
  "job_id": "W4-B-batch01",
  "parent_replicate": "W4-B",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "assigned_sku_ids": ["C01-S01","C01-S02","C01-S03","C02-S01","C02-S02","C02-S03","C03-S01","C03-S02","C03-S03"],
  "categories": [
    {"category_id":"C01","status":"UNRESOLVED_ACCESS_LIMITED"},
    {"category_id":"C02","status":"UNRESOLVED_ACCESS_LIMITED"},
    {"category_id":"C03","status":"UNRESOLVED_ACCESS_LIMITED"}
  ],
  "batch_counts": {
    "sku_count": 9,
    "platform_sku_cells": 18,
    "exact_observed": 0,
    "oem_observed": 0,
    "comparable_only": 0,
    "reseller_only": 0,
    "blocked": 17,
    "login_required": 1,
    "not_observed": 0,
    "verified_unavailable": 0,
    "usable_original_page_observations": 0,
    "missing_rate": 1.0,
    "missing_rate_definition": "platform-SKU cells lacking a readable original marketplace page sufficient to verify required offering fields; not an availability rate"
  },
  "match_bucket_counts": {
    "A_exact": 0,
    "B_same_oem_different_branding": 0,
    "C_functional_comparable": 0,
    "note": "observed-count only; blocked/login-required cells are not treated as absence"
  },
  "costing_scope": {
    "comparison_endpoint": "ordinary delivered price to US ZIP10001",
    "us_sales_tax_treatment": "not estimated or added; if explicitly observed at checkout it would be reported separately",
    "savings_calculated": false,
    "tariff_calculated": false,
    "reason": "no directly verified offer, shipping quote, origin basis, weight/dimensions or tariff classification",
    "shipment_structures": [
      {"structure_id":"1","definition":null,"status":"UNRESOLVED_NO_VERIFIED_OFFER"},
      {"structure_id":"2","definition":null,"status":"UNRESOLVED_NO_VERIFIED_OFFER"},
      {"structure_id":"3","definition":null,"status":"UNRESOLVED_NO_VERIFIED_OFFER"},
      {"structure_id":"4","definition":null,"status":"UNRESOLVED_NO_VERIFIED_OFFER"}
    ]
  },
  "sources": [
    {"source_id":"T01","url":null,"web_ref":"turn365119view0","title":"Temu exact-search open attempt: C01-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T02","url":null,"web_ref":"turn365119view1","title":"Temu exact-search open attempt: C01-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T03","url":null,"web_ref":"turn365119view2","title":"Temu exact-search open attempt: C01-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T04","url":null,"web_ref":"turn365119view3","title":"Temu exact-search open attempt: C02-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T05","url":null,"web_ref":"turn365119view4","title":"Temu exact-search open attempt: C02-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T06","url":null,"web_ref":"turn365119view5","title":"Temu exact-search open attempt: C02-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T07","url":null,"web_ref":"turn365119view6","title":"Temu exact-search open attempt: C03-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T08","url":null,"web_ref":"turn365119view7","title":"Temu exact-search open attempt: C03-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"T09","url":null,"web_ref":"turn365119view8","title":"Temu exact-search open attempt: C03-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K03"]},
    {"source_id":"A01","url":null,"web_ref":"turn316464view0","title":"AliExpress exact-search open attempt: C01-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A02","url":null,"web_ref":"turn316464view1","title":"AliExpress exact-search open attempt: C01-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A03","url":null,"web_ref":"turn316464view2","title":"AliExpress exact-search open attempt: C01-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A04","url":null,"web_ref":"turn316464view3","title":"AliExpress exact-search open attempt: C02-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A05","url":null,"web_ref":"turn316464view4","title":"AliExpress exact-search open attempt: C02-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A06","url":null,"web_ref":"turn316464view5","title":"AliExpress exact-search open attempt: C02-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A07","url":null,"web_ref":"turn316464view6","title":"AliExpress exact-search open attempt: C03-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A08","url":null,"web_ref":"turn316464view7","title":"AliExpress exact-search open attempt: C03-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K03"]},
    {"source_id":"A09","url":null,"web_ref":"turn316464view8","title":"AliExpress exact-search open attempt: C03-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"A10","url":null,"web_ref":"turn571519view1","title":"AliExpress OnePlus Ace 6T candidate item open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"login_required","claims_supported":["K04"]},
    {"source_id":"A11","url":null,"web_ref":"turn767612view0","title":"AliExpress Lenovo Y700 Gen5 candidate item open attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K05"]}
  ],
  "claims": [
    {"claim_id":"K01","claim":"All nine assigned Temu SKU searches lacked a readable original page sufficient for offering verification.","classification":"FACT","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09"],"confidence":"high","counterevidence":"Search indexing may expose candidate listings, but snippets/page shells were not accepted as offering evidence."},
    {"claim_id":"K02","claim":"AliExpress exact-search access was blocked for the assigned SKUs; the OnePlus candidate item additionally exposed a login requirement.","classification":"FACT","source_ids":["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10"],"confidence":"high","counterevidence":"Indexed candidate links indicate possible marketplace presence but do not verify item fields."},
    {"claim_id":"K03","claim":"No Temu or AliExpress offering was counted in A exact, B same-OEM, C comparable, or reseller-only buckets because no required item fields were verified from a readable original page.","classification":"FACT","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09","A01","A02","A04","A05","A06","A07","A08"],"confidence":"high","counterevidence":"Candidate links appeared in web indexing but were intentionally not promoted to observations."},
    {"claim_id":"K04","claim":"The C01-S03 AliExpress candidate item could not be verified because opening the original item redirected to an inaccessible AliExpress login page.","classification":"FACT","source_ids":["A10"],"confidence":"high","counterevidence":"None; no authenticated session was attempted."},
    {"claim_id":"K05","claim":"The C03-S03 AliExpress candidate item could not be verified because the original product page returned HTTP 403 in the research environment.","classification":"FACT","source_ids":["A11"],"confidence":"high","counterevidence":"Its presence in search indexing is not proof of current availability, variant, price or ZIP10001 delivery."},
    {"claim_id":"K06","claim":"BLOCKED and LOGIN_REQUIRED are research-access outcomes and must not be interpreted as verified marketplace unavailability.","classification":"INFERENCE","source_ids":["K01","K02"],"confidence":"high","counterevidence":"None under the stated protocol."}
  ],
  "coverage": [
    {"sku_id":"C01-S01","category_id":"C01","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 256GB White; China-mainland dual-SIM constraint; T01"],"access_limitations":["original Temu search page inaccessible","ZIP10001 delivery context not verifiable","seller/item/region/currency/price/inventory/warehouse null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 256GB White; China-mainland dual-SIM constraint; A01"],"access_limitations":["original AliExpress search page inaccessible","ZIP10001 delivery context not verifiable","seller/item/region/currency/price/inventory/warehouse null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["frozen China exact variant retained","US/eSIM or other regional hardware cannot be treated as exact","no cross-bucket savings"]},
    {"sku_id":"C01-S02","category_id":"C01","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 Pro 256GB Silver; China-mainland dual-SIM constraint; T02"],"access_limitations":["original Temu search page inaccessible","ZIP10001 context not verifiable","all offer fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 Pro 256GB Silver; China-mainland dual-SIM constraint; A02"],"access_limitations":["original AliExpress search page inaccessible","ZIP10001 context not verifiable","all offer fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["frozen verified-head status preserved","regional iPhone hardware differences prevent exact inference"]},
    {"sku_id":"C01-S03","category_id":"C01","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["OnePlus Ace 6T 12GB+256GB Flash Black/闪速黑; T03"],"access_limitations":["original search/item content not readable","no candidate identity tied to readable original page","all offer fields null"]},"aliexpress":{"observation_status":"LOGIN_REQUIRED","offers":[],"search_scope":["OnePlus Ace 6T 12GB+256GB Flash Black/闪速黑","candidate item open attempt A10"],"access_limitations":["candidate original item redirected to AliExpress login","no login performed","color/version/price/seller/inventory/US warehouse/delivery not accepted from snippet"]},"china_head_us_middle_tail_status":"unresolved","caveats":["head_status_verified remains false","indexed candidate not counted as exact"]},
    {"sku_id":"C02-S01","category_id":"C02","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 天选7 Pro Core Ultra 7 251HX 16GB 1TB RTX5060 2.5K 300Hz 青; T04"],"access_limitations":["original Temu search page inaccessible","all marketplace fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 天选7 Pro Core Ultra 7 251HX 16GB 1TB RTX5060 2.5K 300Hz 青; A04"],"access_limitations":["original AliExpress search page inaccessible","near-model search-index results not accepted","all marketplace fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["天选 other generations/configurations not interchangeable","no A/B/C match recorded"]},
    {"sku_id":"C02-S02","category_id":"C02","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo 小新16SE Ryzen 7 16GB 512GB expandable-drive-bay; T05"],"access_limitations":["original Temu search page inaccessible","all marketplace fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo 小新16SE Ryzen 7 16GB 512GB expandable-drive-bay; A05"],"access_limitations":["original AliExpress search page inaccessible","all marketplace fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["frozen exact_variant_verified=true retained","generic 16-inch Ryzen laptops are not exact/OEM evidence"]},
    {"sku_id":"C02-S03","category_id":"C02","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["MECHREVO 无界14 2026 Core Ultra 5 226V 16GB 1TB 2.8K 灰; T06"],"access_limitations":["original Temu search page inaccessible","all marketplace fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["MECHREVO 无界14 2026 Core Ultra 5 226V 16GB 1TB 2.8K 灰; A06"],"access_limitations":["original AliExpress search page inaccessible","other MECHREVO models not accepted as same SKU","all marketplace fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["head_status_verified remains false","no OEM inference from brand/category similarity"]},
    {"sku_id":"C03-S01","category_id":"C03","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Apple iPad 11-inch A16 2025 128GB WLAN Silver; T07"],"access_limitations":["original exact-search inaccessible / indexed US category opened as page shell","no price/version/inventory accepted from indexing","all offer fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Apple iPad 11-inch A16 2025 128GB WLAN Silver; A07"],"access_limitations":["original search page inaccessible","all offer fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["128GB and 256GB remain separate SKUs","non-US locale candidate cannot establish ZIP10001 offering"]},
    {"sku_id":"C03-S02","category_id":"C03","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Apple iPad 11-inch A16 2025 256GB WLAN Silver; T08"],"access_limitations":["original Temu search page inaccessible","all offer fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Apple iPad 11-inch A16 2025 256GB WLAN Silver; A08"],"access_limitations":["original AliExpress search page inaccessible","all offer fields null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["256GB kept distinct from C03-S01","no indexed price treated as observed"]},
    {"sku_id":"C03-S03","category_id":"C03","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo Legion 拯救者 Y700 五代 8.8-inch 12GB+256GB Wi-Fi 碳晶黑; T09"],"access_limitations":["original Temu search page inaccessible","all offer fields null"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo Legion Y700 Gen5 12GB+256GB Black","candidate original item checked A11"],"access_limitations":["candidate item returned 403","search-index specifications/seller/price/inventory not accepted","ZIP10001 and US warehouse unverified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["head_status_verified remains false","older Y700 generations cannot be merged","indexed Gen5 candidate not promoted to exact"]}    
  ],
  "data_gaps": [
    "No readable original marketplace page sufficient to validate any of the 18 platform-SKU cells.",
    "Destination ZIP10001 could not be applied and verified on a readable target item page.",
    "Seller, item ID, exact marketplace variant, region, currency, ordinary delivered price, stock and US-warehouse evidence remain null.",
    "Membership/new-user/coupon/subsidy-directed pricing was neither inferred nor mixed with ordinary public pricing.",
    "No weight, dimensions, shipping component, tariff classification/source or tariff rate was manufactured.",
    "No savings were calculated and no A/B/C buckets were combined.",
    "Blocked, login-required, not-observed and verified-unavailable remain logically distinct; no cell was classified VERIFIED_UNAVAILABLE."
  ]
}
```