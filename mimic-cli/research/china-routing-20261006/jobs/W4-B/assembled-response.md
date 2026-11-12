ONE independent W4-B replicate, mechanically bundled from six disjoint category batches. No peer results were supplied. All frozen SKU IDs are retained; unobserved and blocked rows remain in the denominator. Original reports are untruncated.

=== UNEDITED W4-B-batch01; SHA256 85b73be0ecad6d4e65008c6e98356c941e3b92cdf72fedbe578b824cb84ba2a0 ===
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
=== UNEDITED W4-B-batch02; SHA256 76970a5fca76b4386d861349fda2a8e8e483787596d4e854f17dbddeee52617d ===
## 1. 直接回答

截至 **2026-10-06**，仅调查冻结批次 W4-B-batch02 的 9 个 SKU。网页研究本身可用，但当前研究接口对 9 个 Temu 原始搜索页全部不可访问，按预注册状态记为 `BLOCKED`；AliExpress 9 个原始搜索页同样全部不可访问。这里的 `BLOCKED` **绝不解释为缺货或 VERIFIED_UNAVAILABLE**。 ([](), [](), []()) ([Invalid URL]()) ([Invalid URL]())

本批共 **18 个 platform×SKU 观察单元：BLOCKED=18，合格 offers=0，offer级必需字段缺失率=100%**。A exact、B OEM、C comparable 的**已核验**计数均为 0；这不代表市场上不存在。冻结前 `head_status_verified` 与 `exact_variant_verified` 未改动。

## 2. 证据表

| SKU | 冻结 head/exact | Temu | AliExpress | 中国头部/美国中尾部 |
|---|---|---|---|---|
| C04-S01 | T / T | BLOCKED | BLOCKED | unresolved |
| C04-S02 | T / T | BLOCKED | BLOCKED | unresolved |
| C04-S03 | F / T | BLOCKED | BLOCKED | not_supported |
| C05-S01 | T / T | BLOCKED | BLOCKED | unresolved |
| C05-S02 | T / T | BLOCKED | BLOCKED | unresolved |
| C05-S03 | F / T | BLOCKED | BLOCKED | not_supported |
| C06-S01 | T / T | BLOCKED | BLOCKED | unresolved |
| C06-S02 | T / T | BLOCKED | BLOCKED | unresolved |
| C06-S03 | F / T | BLOCKED | BLOCKED | not_supported |

## 3. 一级来源

每个 SKU 都完成了一次精确型号/版本检索，并尝试打开对应 Temu、AliExpress 原始搜索页；失败均属于“原始页无法由本研究接口读取”，没有拿 HTTP 壳、搜索摘要或二级页面补成交价、seller、库存、仓库。

## 4. 论坛证据

未用论坛/社区数据证明覆盖。唯一有用的社区痕迹是 PiBenchmarks 的用户基准记录出现 `Samsung SSD990EVOPlus2TB`，但持有该硬件不能证明从 AliExpress 购买，更不能证明当前 listing、卖家、价格或库存。[Pi Benchmarks](https://pibenchmarks.com/benchmark/130440/?utm_source=chatgpt.com)

## 5. 反证

AliExpress 并不能因 `BLOCKED` 被解释成“没有”。二级聚合页确实出现 KINGBANK DDR5-6000 银色系列，并可解析到 AliExpress item `1005010520353531`，但原始商品页仍打不开。[Trovaprezzi](https://www.trovaprezzi.it/prezzo_ram_ram_ddr5_6000_mhz_16_gbx2.aspx) Samsung 990 EVO Plus 也有二级 AliExpress 痕迹并解析到 item `1005008997118442`；其二级标题同时跨 1T/2T/4T，且原始页不可读取，因此不能确认冻结的 2TB exact variant。[Pricearchive.org](https://ms.pricearchive.org/search/aliexpress.com/%D0%BC2-ssd-samsung/1?sort=SALE_PRICE_DESC)

## 6. 置信度

对“本研究接口无法直接核验这 18 个观察单元”的置信度高；对 Temu/AliExpress **真实市场在售状态**置信度低/未知。因此没有任何 `VERIFIED_UNAVAILABLE`。

## 7. 缺口

seller、item状态、库存、US warehouse、USD/CNY普通公开价、ZIP10001运费/送达价、重量尺寸、运输结构输入、关税分类/来源/金额全部为 `null`。比较端点定义为送达 **ZIP10001 的普通公开价 + 可见运费**；美国销售税不计入比较端点，除非平台直接强制显示，本批未观察到。四种 shipment structure 保持彼此分离，全部为空，不合并、不补税率、不制造节省。

## 8. 意外发现

外部聚合器可以暴露 AliExpress item ID，即使原站无法读取；这些信息只适合作为后续定位线索，不能升级成 offer。

## 9. 自我反驳

最重要的反驳是：这里可能主要是**研究接口/反爬访问限制**，并非平台本身对美国用户不可用。因此本结果衡量的是“本批可核验性”，不是 Temu/AliExpress 的市场覆盖率。

## 10. 下一实验

下一轮应使用能正常读取两平台公开美国站页面、但不登录的浏览环境，固定 ZIP10001，对同一 9 个冻结 SKU 各重复一次 exact 搜索；只记录原始页直接显示的 seller/item、精确版本、库存、US warehouse、普通价、运费与送达条件。仍不登录、不下单、不联系商家，也不替换冻结 SKU。

```json
{
"job_id":"W4-B-batch02",
"parent_replicate":"W4-B",
"web_research_available":true,
"pre_freeze_compliance":true,
"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
"assigned_sku_ids":["C04-S01","C04-S02","C04-S03","C05-S01","C05-S02","C05-S03","C06-S01","C06-S02","C06-S03"],
"categories":[{"category_id":"C04","status":"blocked_no_admissible_offer"},{"category_id":"C05","status":"blocked_no_admissible_offer"},{"category_id":"C06","status":"blocked_no_admissible_offer"}],
"comparison_endpoint":{"destination":"US ZIP10001","ordinary_price":"public delivered price + visible shipping if directly observed","us_sales_tax":"excluded unless mandatory tax is directly shown; none observed","member_coupon_subsidy":"kept separate; none observed","four_shipment_structures":"kept separate; all null/unresolved because no admissible offer input"},
"batch_counts":{"platform_sku_units":18,"BLOCKED":18,"EXACT_OBSERVED":0,"OEM_OBSERVED":0,"COMPARABLE_ONLY":0,"RESELLER_ONLY":0,"NOT_OBSERVED":0,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0,"offers":0,"missing_rate":1.0},
"sources":[
{"source_id":"S01","url":"https://www.temu.com/search_result.html?search_key=ASUS%2013500H%2016GB%20512GB%20mini%20PC","title":"Temu search C04-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S02","url":"https://www.aliexpress.com/w/wholesale-ASUS-13500H-16GB-512GB-mini-PC.html","title":"AliExpress search C04-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S03","url":"https://www.temu.com/search_result.html?search_key=GMKtec%20EVO-X2%20Ryzen%20AI%20Max%20395%20128GB%202TB","title":"Temu search C04-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S04","url":"https://www.aliexpress.com/w/wholesale-GMKtec-EVO-X2-Ryzen-AI-Max-395-128GB-2TB.html","title":"AliExpress search C04-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S05","url":"https://www.temu.com/search_result.html?search_key=Beelink%20SER8%208745HS%20barebone","title":"Temu search C04-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S06","url":"https://www.aliexpress.com/w/wholesale-Beelink-SER8-8745HS-barebone.html","title":"AliExpress search C04-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S07","url":"https://www.temu.com/search_result.html?search_key=Samsung%20990%20EVO%20Plus%202TB","title":"Temu search C05-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S08","url":"https://www.aliexpress.com/w/wholesale-Samsung-990-EVO-Plus-2TB.html","title":"AliExpress search C05-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S09","url":"https://www.temu.com/search_result.html?search_key=Xiaomi%20BE6500%20WiFi%207","title":"Temu search C05-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S10","url":"https://www.aliexpress.com/w/wholesale-Xiaomi-BE6500-WiFi-7.html","title":"AliExpress search C05-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S11","url":"https://www.temu.com/search_result.html?search_key=KINGBANK%20DDR5%206000%2032GB%20CL36","title":"Temu search C05-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S12","url":"https://www.aliexpress.com/w/wholesale-KINGBANK-DDR5-6000-32GB-CL36.html","title":"AliExpress search C05-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S13","url":"https://www.temu.com/search_result.html?search_key=EDIFIER%20Lolli%20Pro%20SE%20white%20ANC","title":"Temu search C06-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S14","url":"https://www.aliexpress.com/w/wholesale-EDIFIER-Lolli-Pro-SE-white-ANC.html","title":"AliExpress search C06-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S15","url":"https://www.temu.com/search_result.html?search_key=EDIFIER%20LolliClip%20SE%20gold","title":"Temu search C06-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S16","url":"https://www.aliexpress.com/w/wholesale-EDIFIER-LolliClip-SE-gold.html","title":"AliExpress search C06-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S17","url":"https://www.temu.com/search_result.html?search_key=EDIFIER%20Comfo%20Clip%20Q%20white","title":"Temu search C06-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K05"]},
{"source_id":"S18","url":"https://www.aliexpress.com/w/wholesale-EDIFIER-Comfo-Clip-Q-white.html","title":"AliExpress search C06-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05"]},
{"source_id":"S19","url":"https://www.trovaprezzi.it/prezzo_ram_ram_ddr5_6000_mhz_16_gbx2.aspx","title":"KINGBANK AliExpress trace","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"S20","url":"https://it.aliexpress.com/item/1005010520353531.html","title":"AliExpress item 1005010520353531","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K03"]},
{"source_id":"S21","url":"https://ms.pricearchive.org/search/aliexpress.com/%D0%BC2-ssd-samsung/1?sort=SALE_PRICE_DESC","title":"Samsung AliExpress trace","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K04"]},
{"source_id":"S22","url":"https://www.aliexpress.com/item/1005008997118442.html","title":"AliExpress item 1005008997118442","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K04"]},
{"source_id":"S23","url":"https://pibenchmarks.com/benchmark/130440/","title":"Samsung SSD990EVOPlus2TB user benchmark","published_at":null,"retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K07"]}
],
"claims":[
{"claim_id":"K01","claim":"Temu原始搜索页对9个SKU均无法读取；仅能判BLOCKED，不能判无货。","classification":"FACT","source_ids":["S01","S03","S05","S07","S09","S11","S13","S15","S17"],"confidence":"high","counterevidence":"Temu通用页可被索引，但不能核验本批SKU。"},
{"claim_id":"K02","claim":"AliExpress原始搜索页对9个SKU均无法读取；仅能判BLOCKED，不能判无货。","classification":"FACT","source_ids":["S02","S04","S06","S08","S10","S12","S14","S16","S18"],"confidence":"high","counterevidence":"外部聚合器存在个别AliExpress线索。"},
{"claim_id":"K03","claim":"KINGBANK DDR5-6000银色家族有AliExpress间接线索并解析到item 1005010520353531，但原始商品页blocked，不能计offer。","classification":"FACT","source_ids":["S19","S20"],"confidence":"high","counterevidence":"卖家、美国区、ZIP10001、库存、仓库、普通送达价均未直接观察。"},
{"claim_id":"K04","claim":"Samsung 990 EVO Plus家族有AliExpress间接线索并解析到item 1005008997118442，但原始商品页blocked，不能确认2TB exact offer。","classification":"FACT","source_ids":["S21","S22"],"confidence":"high","counterevidence":"二级标题跨1T/2T/4T，不能证明2TB选择项当前可售。"},
{"claim_id":"K05","claim":"18个platform×SKU单元无可接纳的原始offer；卖家、库存、美国仓、ZIP10001送达价均为null。","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"二级线索不提升为offer。"},
{"claim_id":"K06","claim":"冻结前head_status_verified与exact_variant_verified对9个SKU均原样保留。","classification":"FACT","source_ids":[],"confidence":"high","counterevidence":"本workstream不重审国内冻结证据。"},
{"claim_id":"K07","claim":"社区基准只证明有人使用Samsung SSD990EVOPlus2TB设备字符串，不能证明AliExpress当前listing/卖家/价格/库存。","classification":"FACT","source_ids":["S23"],"confidence":"high","counterevidence":"硬件可由其他渠道购得。"}
],
"coverage":[
{"sku_id":"C04-S01","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com ASUS 13500H 16GB 512GB mini PC","page:https://www.temu.com/search_result.html?search_key=ASUS%2013500H%2016GB%20512GB%20mini%20PC"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com ASUS 13500H 16GB 512GB mini PC","page:https://www.aliexpress.com/w/wholesale-ASUS-13500H-16GB-512GB-mini-PC.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C04-S02","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com GMKtec EVO-X2 Ryzen AI Max 395 128GB 2TB","page:https://www.temu.com/search_result.html?search_key=GMKtec%20EVO-X2%20Ryzen%20AI%20Max%20395%20128GB%202TB"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com GMKtec EVO-X2 Ryzen AI Max 395 128GB 2TB","page:https://www.aliexpress.com/w/wholesale-GMKtec-EVO-X2-Ryzen-AI-Max-395-128GB-2TB.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C04-S03","category_id":"C04","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com Beelink SER8 8745HS barebone","page:https://www.temu.com/search_result.html?search_key=Beelink%20SER8%208745HS%20barebone"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com Beelink SER8 8745HS barebone","page:https://www.aliexpress.com/w/wholesale-Beelink-SER8-8745HS-barebone.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"not_supported","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C05-S01","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com Samsung 990 EVO Plus 2TB","page:https://www.temu.com/search_result.html?search_key=Samsung%20990%20EVO%20Plus%202TB"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com Samsung 990 EVO Plus 2TB","page:https://www.aliexpress.com/w/wholesale-Samsung-990-EVO-Plus-2TB.html","secondary:item 1005008997118442; primary blocked"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C05-S02","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com Xiaomi BE6500 WiFi 7","page:https://www.temu.com/search_result.html?search_key=Xiaomi%20BE6500%20WiFi%207"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com Xiaomi BE6500 WiFi 7","page:https://www.aliexpress.com/w/wholesale-Xiaomi-BE6500-WiFi-7.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C05-S03","category_id":"C05","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com KINGBANK DDR5 6000 32GB CL36","page:https://www.temu.com/search_result.html?search_key=KINGBANK%20DDR5%206000%2032GB%20CL36"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com KINGBANK DDR5 6000 32GB CL36","page:https://www.aliexpress.com/w/wholesale-KINGBANK-DDR5-6000-32GB-CL36.html","secondary:item 1005010520353531; primary blocked"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"not_supported","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C06-S01","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com EDIFIER Lolli Pro SE white ANC","page:https://www.temu.com/search_result.html?search_key=EDIFIER%20Lolli%20Pro%20SE%20white%20ANC"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com EDIFIER Lolli Pro SE white ANC","page:https://www.aliexpress.com/w/wholesale-EDIFIER-Lolli-Pro-SE-white-ANC.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C06-S02","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com EDIFIER LolliClip SE gold","page:https://www.temu.com/search_result.html?search_key=EDIFIER%20LolliClip%20SE%20gold"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com EDIFIER LolliClip SE gold","page:https://www.aliexpress.com/w/wholesale-EDIFIER-LolliClip-SE-gold.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]},
{"sku_id":"C06-S03","category_id":"C06","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:temu.com EDIFIER Comfo Clip Q white","page:https://www.temu.com/search_result.html?search_key=EDIFIER%20Comfo%20Clip%20Q%20white"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["web:site:aliexpress.com EDIFIER Comfo Clip Q white","page:https://www.aliexpress.com/w/wholesale-EDIFIER-Comfo-Clip-Q-white.html"],"access_limitations":["primary_blocked","no_ZIP10001_context","no_snippet_inference"]},"china_head_us_middle_tail_status":"not_supported","caveats":["BLOCKED≠缺货/VERIFIED_UNAVAILABLE","A/B/C均未形成可核验offer"]}
],
"data_gaps":["18/18原始平台搜索页blocked；不等同无货。","seller/item/stock/US-warehouse/ZIP10001普通送达价均未直接观察。","重量/尺寸、运费结构、关税分类/来源/金额均为null；未制造税率或节省。","四种shipment structure保持分离但本批均无输入，未合并或替代。","二级/社区线索只作发现与反证，不进入offers。"],
"source_attestation":"model-observed; coordinator_review_pending"
}
```
=== UNEDITED W4-B-batch03; SHA256 773e085e5c6a63bab7565b708cc072160226f5540d62595befda64a35c07503c ===
以下为 W4-B-batch03 本批次冻结后 Temu / AliExpress Coverage 结果。所有“blocked”均只表示本次访问受阻，不表示市场无货。

### 1. 直接回答

截至 **2026-10-06**，仅研究指定 9 个 SKU、18 个“SKU×平台”单元。Temu 9/9 的原始搜索页不可访问；AliExpress 9/9 的原始搜索页或候选商品页不可访问。因此本批次 **A exact=0、B OEM=0、C comparable=0、reseller-only=0，BLOCKED=18/18**；这是“本批次可核验观察计数”，不是全市场覆盖率或缺货率。四个 AliExpress 候选由二级完整页面定位到 item ID，但原始商品页仍打不开，故价格、seller、库存、美国仓、ZIP10001 delivered price 全部保持 null。([Invalid URL]())

### 2. 证据表

| SKU | 冻结 head / variant | Temu | AliExpress | 本批次结论 |
|---|---|---|---|---|
| C07-S01 | true / true | BLOCKED | BLOCKED；发现 G304 候选 item，但黑色/非G304X未核 | unresolved ([Invalid URL]()) |
| C07-S02 | false / true | BLOCKED | BLOCKED | unresolved ([Invalid URL]()) |
| C07-S03 | false / true | BLOCKED | BLOCKED；发现 RS6+ 候选，白武士/雪刃轴Pro未核 | unresolved ([Invalid URL]()) |
| C08-S01 | true / true | BLOCKED | BLOCKED | unresolved ([Invalid URL]()) |
| C08-S02 | true / true | BLOCKED | BLOCKED；发现 Band 11 Pro NFC 候选，羽砂黑/铝壳未核 | unresolved ([Invalid URL]()) |
| C08-S03 | false / true | BLOCKED | BLOCKED | unresolved ([Invalid URL]()) |
| C09-S01 | true / true | BLOCKED | BLOCKED；发现 8MP/4K/CN 候选，交易字段未核 | unresolved ([Invalid URL]()) |
| C09-S02 | true / true | BLOCKED | BLOCKED | unresolved ([Invalid URL]()) |
| C09-S03 | false / true | BLOCKED | BLOCKED | unresolved ([Invalid URL]()) |

### 3. 一级来源

Temu 的逐型号搜索页无法读取；AliExpress 的搜索页以及已定位候选商品的 `.com` / 美国域商品页均无法读取，故 HTTP/索引存在不能升级为 verified offer。唯一额外可读的品牌一级来源是 Aqara 中国参数页：S1E 型号 **CJPKG01LM**、额定 **220V~50Hz**、2.4GHz Wi-Fi。([Invalid URL]())

### 4. 论坛证据

G304 在 AliExpress 有真假混杂的用户经验：2026 年 Reddit 讨论报告多例低价 Logitech/G304 假货、G HUB 不识别；另有用户声称买到可被 G HUB 识别的 G304。因此社区证据只能形成真实性风险提示，不能判定本次候选。[Reddit](https://www.reddit.com/r/Aliexpress/comments/1r1f06j/logitech_mice_for_75/?utm_source=chatgpt.com) Aqara 论坛则有针对 CJPKG01LM 的回答称 S1E 为中国大陆区域设备、不能在 Aqara Home 美国区域工作；这是兼容性反证，不是平台无货证明。[Aqara Forum](https://forum.aqara.com/t/is-there-any-way-to-integrate-the-s1-switch-into-the-us/69988?utm_source=chatgpt.com)

### 5. 反证

不能把 BLOCKED 写成 VERIFIED_UNAVAILABLE：二级索引确实显示 AliExpress 曾/正在索引 G304、RS6+、Band 11 Pro NFC、Smart Camera 4 8MP/4K 商品。由于这些不是本次可读的原始交易页，其索引价格、卖家、库存一律没有进入 coverage 数据。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005013028004177)

### 6. 置信度

“本次原始页面访问受阻”置信度高；“某平台没有该商品”置信度低且**未作此结论**。A/B/C 均未分桶；尤其不能把中国版硬件/区域版本凭型号文字冒充美国 exact。

### 7. 缺口

18/18 单元均缺少可直接核验的普通公开到门价、seller、库存、US warehouse、配送费、重量/尺寸以及关税分类；关键交易字段缺失率为 **100%**。ZIP10001 为统一目的地；美国 sales tax 不计入比较端点，也未推算。四种上游既定运输结构的定义未随本批次材料提供，因此保留四个独立 null 槽，不自行命名或补价。

### 8. 意外发现

C09-S03 的主要风险可能不是“能否买到”，而是中国区 S1E 的区域绑定与 220V 规格；即便跨境存在 listing，也不能自动成为美国区 exact-equivalent。[Aqara](https://www.aqara.cn/Smart-Magic-Switch-S1E_spec?utm_source=chatgpt.com)

### 9. 自我反驳

当前结果可能低估真实平台覆盖，因为访问限制发生在研究工具侧；二级索引反而说明部分 SKU 有潜在 listing。因此本报告只证明“这次无法可靠观察”，不证明“没有商品”。同样，G304 假货案例不能泛化到所有 AliExpress G304。

### 10. 下一实验

下一轮应在**未登录、美国区域、ZIP10001**的可交互浏览器中逐个打开同一冻结 SKU，确认 variant selector、seller、库存、发货仓、普通公开价格、shipping、到门价和地区兼容性；仍不登录、不下单、不联系商家。只有这些字段可读后才分 A/B/C，并单独保留四种运输结构与显式关税组件。

```json
{"job_id":"W4-B-batch03","parent_replicate":"W4-B","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185","assigned_sku_ids":["C07-S01","C07-S02","C07-S03","C08-S01","C08-S02","C08-S03","C09-S01","C09-S02","C09-S03"],"categories":[{"category_id":"C07","status":"BOTH_MARKETPLACES_BLOCKED_FOR_ASSIGNED_SKUS"},{"category_id":"C08","status":"BOTH_MARKETPLACES_BLOCKED_FOR_ASSIGNED_SKUS"},{"category_id":"C09","status":"BOTH_MARKETPLACES_BLOCKED_FOR_ASSIGNED_SKUS"}],"sources":[
{"source_id":"S01","url":"https:\/\/www.temu.com\/search_result.html?search_key=Logitech%20G304","title":"Temu search — Logitech G304","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S02","url":"https:\/\/www.aliexpress.com\/item\/1005013028004177.html","title":"AliExpress candidate item 1005013028004177 — Logitech G304","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S03","url":"https:\/\/www.pricearchive.org\/aliexpress.com\/item\/1005013028004177","title":"PriceArchive index — Logitech G304 candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"S04","url":"https:\/\/www.temu.com\/search_result.html?search_key=Logitech%20GPW5%20snow%20leopard","title":"Temu search — Logitech GPW5 Snow Leopard","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S05","url":"https:\/\/www.aliexpress.com\/w\/wholesale-logitech-gpw5.html","title":"AliExpress search — Logitech GPW5","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S06","url":"https:\/\/www.temu.com\/search_result.html?search_key=ATK%20RS6%2B","title":"Temu search — ATK RS6+","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S07","url":"https:\/\/www.aliexpress.com\/item\/1005012984653410.html","title":"AliExpress candidate item 1005012984653410 — ATK RS6+","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S08","url":"https:\/\/cs.pricearchive.org\/aliexpress.com\/item\/1005012984653410","title":"PriceArchive index — ATK RS6+ candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"S09","url":"https:\/\/www.temu.com\/search_result.html?search_key=Huawei%20Band%2011%20NFC","title":"Temu search — Huawei Band 11 NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S10","url":"https:\/\/www.aliexpress.com\/w\/wholesale-huawei-band-11-nfc.html","title":"AliExpress search — Huawei Band 11 NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S11","url":"https:\/\/www.temu.com\/search_result.html?search_key=Huawei%20Band%2011%20Pro%20NFC","title":"Temu search — Huawei Band 11 Pro NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S12","url":"https:\/\/www.aliexpress.com\/item\/1005012863923426.html","title":"AliExpress candidate item 1005012863923426 — Huawei Band 11 Pro NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S13","url":"https:\/\/cs.pricearchive.org\/aliexpress.com\/item\/1005012863923426","title":"PriceArchive index — Huawei Band 11 Pro NFC candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"S14","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Watch%20S5%2041mm","title":"Temu search — Xiaomi Watch S5 41mm","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S15","url":"https:\/\/www.aliexpress.com\/w\/wholesale-xiaomi-watch-s5-41mm.html","title":"AliExpress search — Xiaomi Watch S5 41mm","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S16","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Smart%20Camera%204","title":"Temu search — Xiaomi Smart Camera 4","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S17","url":"https:\/\/www.aliexpress.com\/item\/1005013099255546.html","title":"AliExpress candidate item 1005013099255546 — Xiaomi Smart Camera 4","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S18","url":"https:\/\/www.pricearchive.org\/aliexpress.com\/item\/1005013099255546","title":"PriceArchive index — Xiaomi Smart Camera 4 8MP 4K candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"S19","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Smart%20Door%20Lock%204%20Pro%20Dual%20Camera","title":"Temu search — Xiaomi Smart Door Lock 4 Pro Dual Camera","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S20","url":"https:\/\/www.aliexpress.com\/w\/wholesale-xiaomi-smart-door-lock-4-pro-dual-camera.html","title":"AliExpress search — Xiaomi Smart Door Lock 4 Pro Dual Camera","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S22","url":"https:\/\/www.temu.com\/search_result.html?search_key=Aqara%20S1E%20CJPKG01LM","title":"Temu search — Aqara S1E CJPKG01LM","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K07"]},
{"source_id":"S23","url":"https:\/\/www.aliexpress.com\/w\/wholesale-aqara-s1e.html","title":"AliExpress search — Aqara S1E","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02","K07"]},
{"source_id":"S24","url":"https:\/\/www.aqara.cn\/Smart-Magic-Switch-S1E_spec","title":"妙控开关 S1E 产品参数 — Aqara 中国","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
{"source_id":"S25","url":"https:\/\/forum.aqara.com\/t\/is-there-any-way-to-integrate-the-s1-switch-into-the-us\/69988","title":"Aqara Forum — S1E in US region","published_at":"2025-08-13","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K06"]},
{"source_id":"S26","url":"https:\/\/www.reddit.com\/r\/Aliexpress\/comments\/1r1f06j\/logitech_mice_for_75\/","title":"Reddit r/Aliexpress — low-price Logitech/G304 counterfeit reports","published_at":"2026-02-10","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K04"]}
],"claims":[
{"claim_id":"K01","claim":"All nine assigned Temu searches/item checks were blocked in this run; no Temu offering was directly verified.","classification":"FACT","source_ids":["S01","S04","S06","S09","S11","S14","S16","S19","S22"],"confidence":"high","counterevidence":"External search engines may index Temu pages, but snippets/page shells were not accepted as observations."},
{"claim_id":"K02","claim":"All nine assigned AliExpress original search/item checks were blocked in this run; no AliExpress transactional page was directly verified.","classification":"FACT","source_ids":["S02","S05","S07","S10","S12","S15","S17","S20","S23"],"confidence":"high","counterevidence":"Secondary indexes and community links indicate some candidate listings may exist, but original pages remained unreadable."},
{"claim_id":"K03","claim":"Secondary full-page indexes identified candidate AliExpress item IDs for G304, ATK RS6+, Huawei Band 11 Pro NFC, and Xiaomi Smart Camera 4 8MP 4K; these candidates do not verify exact frozen variants or current transaction fields.","classification":"FACT","source_ids":["S03","S08","S13","S18"],"confidence":"high","counterevidence":"Original AliExpress pages for the candidates were blocked, so seller, exact variant, stock, warehouse, price and delivery remain null."},
{"claim_id":"K04","claim":"Community reports document counterfeit or suspected-counterfeit Logitech G304/other Logitech mice on AliExpress; this is only a risk signal, not evidence about any current candidate listing.","classification":"FACT","source_ids":["S26"],"confidence":"medium","counterevidence":"Other community reports also describe genuine G304 purchases; authenticity must be verified per listing/device."},
{"claim_id":"K05","claim":"Aqara's official China specification page identifies S1E model CJPKG01LM with 220V~50Hz and 2.4GHz Wi-Fi.","classification":"FACT","source_ids":["S24"],"confidence":"high","counterevidence":null},
{"claim_id":"K06","claim":"An Aqara forum response states S1E/CJPKG01LM is for Mainland China region and will not work in the US region of Aqara Home.","classification":"FACT","source_ids":["S25"],"confidence":"medium","counterevidence":"Community/forum evidence is not a substitute for a current official US compatibility statement."},
{"claim_id":"K07","claim":"No current A/B/C match bucket can be assigned for any marketplace cell because readable original marketplace evidence was not obtained.","classification":"INFERENCE","source_ids":["S01","S02","S04","S05","S06","S07","S09","S10","S11","S12","S14","S15","S16","S17","S19","S20","S22","S23"],"confidence":"high","counterevidence":"Secondary indexes name some matching models but do not meet the required original-page standard."},
{"claim_id":"K08","claim":"china_head_us_middle_tail_status remains unresolved for all nine assigned SKUs in this batch.","classification":"INFERENCE","source_ids":["S01","S02","S04","S05","S06","S07","S09","S10","S11","S12","S14","S15","S16","S17","S19","S20","S22","S23"],"confidence":"high","counterevidence":null}
],"observations":{"batch_counts":{"assigned_skus":9,"platform_sku_cells":18,"blocked_cells":18,"exact_observed":0,"oem_observed":0,"comparable_only":0,"reseller_only":0,"not_observed":0,"login_required":0,"verified_unavailable":0,"transaction_field_complete_cells":0,"key_transaction_field_missing_rate":1.0},"comparison_endpoint":"Ordinary public delivered price to US ZIP10001, before US sales tax; any explicitly displayed import/tariff component would be retained separately.","us_sales_tax_treatment":"Excluded from comparison endpoint and not imputed; checkout was not performed.","shipment_structures":[{"structure_id":"1","definition":null,"status":"UNOBSERVED","reason":"The upstream four-structure definitions were not present in this batch prompt; definition and values were not invented."},{"structure_id":"2","definition":null,"status":"UNOBSERVED","reason":"The upstream four-structure definitions were not present in this batch prompt; definition and values were not invented."},{"structure_id":"3","definition":null,"status":"UNOBSERVED","reason":"The upstream four-structure definitions were not present in this batch prompt; definition and values were not invented."},{"structure_id":"4","definition":null,"status":"UNOBSERVED","reason":"The upstream four-structure definitions were not present in this batch prompt; definition and values were not invented."}],"tariff_policy":"No tariff classification or rate was manufactured. Offer-level tariff_classification and tariff_source remain null without readable original offer/shipping evidence.","coordinator_note":"Sources are model-attested and await coordinator review."},"coverage":[
{"sku_id":"C07-S01","category_id":"C07","head_status_verified":true,"exact_variant_verified":true,"target_exact_variant":"Logitech G304 黑色（非G304X）","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech G304 black non-G304X","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search/item page was not accessible; no transactional fields were verified."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":"https:\/\/www.aliexpress.com\/item\/1005013028004177.html","seller":null,"item":"1005013028004177","match_bucket":null,"match_evidence":"Secondary index names Logitech G304, but original AliExpress page was blocked; black/non-G304X variant, authenticity, seller and stock were not verified.","exact_variant_observed":null,"inventory":null,"us_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"ordinary_delivered_price":null,"price_type":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S02","S03"],"weight":null,"dimensions":null,"shipping_structure":null,"tariff_classification":null,"tariff_source":null,"quote_assumptions":"ZIP10001; no login/checkout; US sales tax excluded; no secondary-index price used."}],"search_scope":[{"query":"Logitech G304 black non-G304X","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original item page was not accessible; no transactional fields were verified."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C07-S02","category_id":"C07","head_status_verified":false,"exact_variant_verified":true,"target_exact_variant":"Logitech GPW5雪豹无线电竞游戏鼠标","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech GPW5 Snow Leopard wireless gaming mouse","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech GPW5 Snow Leopard wireless gaming mouse","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original search page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C07-S03","category_id":"C07","head_status_verified":false,"exact_variant_verified":true,"target_exact_variant":"ATK RS6+ 白武士，雪刃轴Pro，68键，有线磁轴","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"ATK RS6+ White Warrior Snow Blade Pro 68-key wired magnetic","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":"https:\/\/www.aliexpress.com\/item\/1005012984653410.html","seller":null,"item":"1005012984653410","match_bucket":null,"match_evidence":"Secondary index names ATK RS6+, but original page was blocked; White Warrior/Snow Blade Pro/68-key exact configuration was not verified.","exact_variant_observed":null,"inventory":null,"us_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"ordinary_delivered_price":null,"price_type":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S07","S08"],"weight":null,"dimensions":null,"shipping_structure":null,"tariff_classification":null,"tariff_source":null,"quote_assumptions":"ZIP10001; no login/checkout; US sales tax excluded; no secondary-index price used."}],"search_scope":[{"query":"ATK RS6+ White Warrior Snow Blade Pro 68-key wired magnetic","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original item page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C08-S01","category_id":"C08","head_status_verified":true,"exact_variant_verified":true,"target_exact_variant":"华为手环11 NFC版 悦动白，铝合金表壳，1.62英寸","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 NFC white aluminum 1.62","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 NFC white aluminum 1.62","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original search page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C08-S02","category_id":"C08","head_status_verified":true,"exact_variant_verified":true,"target_exact_variant":"华为手环11 Pro NFC 羽砂黑 铝合金表壳","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 Pro NFC black aluminum","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":"https:\/\/www.aliexpress.com\/item\/1005012863923426.html","seller":null,"item":"1005012863923426","match_bucket":null,"match_evidence":"Secondary index names Huawei Band 11 Pro NFC, but original page was blocked; black/aluminum exact variant, seller and stock were not verified.","exact_variant_observed":null,"inventory":null,"us_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"ordinary_delivered_price":null,"price_type":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S12","S13"],"weight":null,"dimensions":null,"shipping_structure":null,"tariff_classification":null,"tariff_source":null,"quote_assumptions":"ZIP10001; no login/checkout; US sales tax excluded; no secondary-index price used."}],"search_scope":[{"query":"Huawei Band 11 Pro NFC black aluminum","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original item page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C08-S03","category_id":"C08","head_status_verified":false,"exact_variant_verified":true,"target_exact_variant":"Xiaomi Watch S5 41mm 海盐蓝；澎湃OS 4","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Watch S5 41mm sea-salt blue HyperOS 4","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Watch S5 41mm sea-salt blue HyperOS 4","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original search page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C09-S01","category_id":"C09","head_status_verified":true,"exact_variant_verified":true,"target_exact_variant":"小米智能摄像机 4 室内云台 800万像素 4K","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Camera 4 8MP 4K indoor pan-tilt","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":"https:\/\/www.aliexpress.com\/item\/1005013099255546.html","seller":null,"item":"1005013099255546","match_bucket":null,"match_evidence":"Secondary index names Xiaomi Smart Camera 4 8MP 4K and CN, but original page was blocked; seller, stock, warehouse and delivered price were not verified.","exact_variant_observed":null,"inventory":null,"us_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"ordinary_delivered_price":null,"price_type":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S17","S18"],"weight":null,"dimensions":null,"shipping_structure":null,"tariff_classification":null,"tariff_source":null,"quote_assumptions":"ZIP10001; no login/checkout; US sales tax excluded; no secondary-index price used."}],"search_scope":[{"query":"Xiaomi Smart Camera 4 8MP 4K indoor pan-tilt","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original item page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C09-S02","category_id":"C09","head_status_verified":true,"exact_variant_verified":true,"target_exact_variant":"小米智能门锁 4 Pro 双摄版 双摄/人脸/掌静脉/猫眼大屏","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Door Lock 4 Pro Dual Camera face palm-vein peephole display","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Door Lock 4 Pro Dual Camera face palm-vein peephole display","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original search page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]},
{"sku_id":"C09-S03","category_id":"C09","head_status_verified":false,"exact_variant_verified":true,"target_exact_variant":"Aqara 妙控开关 S1E 皎月白；CJPKG01LM","temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Aqara S1E CJPKG01LM white","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["Temu original search page was not accessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Aqara S1E CJPKG01LM white","region":"US","destination_zip":"10001","checked_at":"2026-10-06"}],"access_limitations":["AliExpress original search page was not accessible."]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED is an access result, not evidence of unavailability.","No A/B/C bucket assigned without readable original marketplace evidence."]}
],"data_gaps":["Temu original search/item pages were inaccessible for all 9 assigned SKUs; seller, exact variant, stock, US warehouse, price, delivery, dimensions, weight and tariff fields are unobserved.","AliExpress original search/item pages were inaccessible for all 9 assigned SKUs; four secondary-index candidates could not be promoted to observed offers.","No ordinary public delivered price to ZIP10001 was verified on either platform; no US sales tax, coupon, membership price, directed coupon, subsidy or checkout-only price was inferred.","The four upstream shipment-structure definitions were not included in this batch input; four placeholders are preserved separately without invented definitions or costs."]}
```
=== UNEDITED W4-B-batch04; SHA256 20e4b1eac56e779825918538f964fb1687f50edac0dca47f96e6a25fa12314ea ===
### 1. 直接回答

本批次网页研究可用，但**Temu 与 AliExpress 的原始搜索/商品页面均未达到可核验状态**。9 个冻结 SKU × 2 平台共 **18 个 platform-SKU 检查单元：0 个可核验 offering，18 个 `BLOCKED`，本批次核验缺失率 100%**。这不是“无货率”，也不证明平台没有销售；因此没有任何 SKU 被写成 `VERIFIED_UNAVAILABLE`，也没有用 snippet、缓存页或页面壳填价格、卖家、库存、US warehouse 或 ZIP10001 到手价。

冻结前标记全部原样保留：6 个 head SKU 的 `head_status_verified=true`，3 个 opportunity SKU 为 false；9 个 `exact_variant_verified` 均为 true。

### 2. 证据表

| SKU | 冻结 head/exact | Temu | AliExpress | 本批次结论 |
|---|---|---|---|---|
| C10-S01 P20 Max 非上下水 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C10-S02 P20 Max 自动上下水 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C10-S03 DJI ROMO P 水箱版 | F/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C11-S01 DZC1050-26BT | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C11-S02 WJZ1601S 双电 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C11-S03 WU130X.1 单电 | F/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C12-S01 A7C II 银色28-60 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C12-S02 Alpha 7 V 单机 | T/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |
| C12-S03 GO 3S 白64GB标准版 | F/T | BLOCKED ([Invalid URL]()) | BLOCKED ([Invalid URL]()) | 无可核验 A/B/C offering |

### 3. 一级来源

按要求进一步打开 AliExpress 候选原始页时，P20 类候选、电锤、16V 双电钻、WORX 候选等关键页面均返回 403；Sony/GO 3S 相关搜索页亦出现 403 或页面壳。因此 HTTP 页面存在、搜索引擎索引存在都没有被升级成“已观察商品”。 ([Invalid URL]())

### 4. 论坛证据

唯一有用的社区反证是 2025-05-09 的 GO 3S 讨论：用户讨论的是 **128GB、第三方 AliExpress listing**，而非冻结的“灵动白 64GB 标准版”；其 AliExpress 链接进一步访问又落到登录态。因此它只能说明历史上可能存在相关第三方 listing，不能证明 2026-10-06 的 exact 覆盖。 [Reddit](https://www.reddit.com/r/Insta360/comments/1kilmw5)

### 5. 反证

“BLOCKED”不能解释成“平台没有商品”。二级索引仍能定位到一个 Roborock P20 Max AliExpress item `1005013026385525`；另一个索引定位到 WORX `WU130X` item `1005012312044183`，但后者明确是**不含电池/充电器**，与冻结 `WU130X.1、2.0Ah 单电`不一致。两者的原始 AliExpress 商品页均未成功核验，所以不进入 offers，也不算 A/B/C。 [Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005013026385525)

### 6. 置信度

对“本研究环境下原始页受阻，因此本批次 18/18 无法完成 marketplace verification”的置信度高；对“Temu/AliExpress 实际是否有货、是否有 US warehouse、普通公开成交价多少”的置信度为低/不可判定。`china_head_us_middle_tail_status` 因而九项全部为 `unresolved`。

### 7. 缺口

卖家、item、精确地区版、库存、US warehouse、ZIP10001 delivery、普通公开 USD 到手价、重量/尺寸、运费组成、HS/关税分类与税率全部保持 `null`。美国 sales tax 未进入比较，因为 checkout 税额未观察。四种 shipment structure 未收到上游定义，因此分别保留为 null，绝不自行补定义或费率。

### 8. 意外发现

搜索索引能暴露很具体的型号甚至 item ID，而对应原始 marketplace 页却 403/登录墙。这正说明“索引命中”与“商品已核验”必须分开；否则会把过期、不同套装或地区版本误写成 exact。

### 9. 自我反驳

不同网络、浏览器或公开美国站点会话可能能够打开这些页面；P20 Max/WU130X 的二级索引也直接反驳了“看不到页面=平台没有商品”。因此本报告只陈述**本批次访问状态**，不外推全平台覆盖率，更不生成 A/B/C 节省金额。

### 10. 下一实验

下一次应在**未登录、美国站点、目的地 ZIP10001**的普通公开浏览器中，对这 9 个 SKU × 2 平台各仅重跑一遍 exact 查询，并打开命中的商品页；逐项记录品牌/型号/容量或功率/地区版/捆绑、seller/item、库存、US warehouse、公开普通价与 delivery。仍受阻即保留 BLOCKED，不登录、不下单、不联系客服。取得上游四种 shipment structure 定义前，成本模型继续保持 null。

```json
{"job_id":"W4-B-batch04","parent_replicate":"W4-B","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185","as_of":"2026-10-06","assigned_sku_ids":["C10-S01","C10-S02","C10-S03","C11-S01","C11-S02","C11-S03","C12-S01","C12-S02","C12-S03"],"categories":[{"category_id":"C10","status":"UNRESOLVED_BOTH_PLATFORMS_BLOCKED"},{"category_id":"C11","status":"UNRESOLVED_BOTH_PLATFORMS_BLOCKED"},{"category_id":"C12","status":"UNRESOLVED_BOTH_PLATFORMS_BLOCKED"}],"comparison_endpoint":{"country":"US","zip":"10001"},"cost_protocol":{"ordinary_public_price_only":true,"member_coupon_subsidy_price_not_inferred":true,"us_sales_tax_treatment":"not_observed_not_included","shipment_structures":[{"structure_id":"1","definition":null,"observed_cost":null},{"structure_id":"2","definition":null,"observed_cost":null},{"structure_id":"3","definition":null,"observed_cost":null},{"structure_id":"4","definition":null,"observed_cost":null}],"shipment_structure_note":"Upstream definitions were not supplied; structures remain separate and no cost is imputed.","tariff_classification":null,"tariff_source":null,"tariff_rate":null,"quote_assumptions":"No price/logistics quote accepted without direct original-page observation."},"batch_counts":{"sku_count":9,"platform_sku_units":18,"exact_observed":0,"oem_observed":0,"comparable_only":0,"reseller_only":0,"not_observed":0,"blocked":18,"login_required":0,"verified_unavailable":0,"verified_offer_count":0,"missing_rate":1.0},"sources":[{"source_id":"T01","url":"https://www.temu.com/search_result.html?search_key=Roborock%20P20%20Max%20A2950RR&locale_override=211~en~USD","title":"Temu exact search: Roborock P20 Max A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T02","url":"https://www.temu.com/search_result.html?search_key=Roborock%20P20%20Max%20automatic%20water%20A2950RR&locale_override=211~en~USD","title":"Temu exact search: P20 Max automatic-water A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T03","url":"https://www.temu.com/search_result.html?search_key=DJI%20ROMO%20P%20water%20tank&locale_override=211~en~USD","title":"Temu exact search: DJI ROMO P water tank","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T04","url":"https://www.temu.com/search_result.html?search_key=DZC1050-26BT&locale_override=211~en~USD","title":"Temu exact search: DZC1050-26BT","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T05","url":"https://www.temu.com/search_result.html?search_key=WJZ1601S&locale_override=211~en~USD","title":"Temu exact search: WJZ1601S","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T06","url":"https://www.temu.com/search_result.html?search_key=WU130X.1&locale_override=211~en~USD","title":"Temu exact search: WU130X.1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T07","url":"https://www.temu.com/search_result.html?search_key=Sony%20A7C%20II%2028-60%20silver&locale_override=211~en~USD","title":"Temu exact search: Sony A7C II 28-60 silver","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T08","url":"https://www.temu.com/search_result.html?search_key=Sony%20Alpha%207%20V%20body&locale_override=211~en~USD","title":"Temu exact search: Sony Alpha 7 V body","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"T09","url":"https://www.temu.com/search_result.html?search_key=Insta360%20GO%203S%2064GB%20white&locale_override=211~en~USD","title":"Temu exact search: Insta360 GO 3S 64GB white","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"A01","url":"https://www.aliexpress.us/w/wholesale-roborock-p20-max-a2950rr.html","title":"AliExpress exact search: Roborock P20 Max A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A02","url":"https://www.aliexpress.us/w/wholesale-roborock-p20-max-automatic-water-a2950rr.html","title":"AliExpress exact search: P20 Max automatic-water A2950RR","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A03","url":"https://www.aliexpress.us/w/wholesale-dji-romo-p-water-tank.html","title":"AliExpress exact search: DJI ROMO P water tank","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A04","url":"https://www.aliexpress.us/w/wholesale-dzc1050-26bt.html","title":"AliExpress exact search: DZC1050-26BT","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A05","url":"https://www.aliexpress.us/w/wholesale-wjz1601s.html","title":"AliExpress exact search: WJZ1601S","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A06","url":"https://www.aliexpress.us/w/wholesale-wu130x-1.html","title":"AliExpress exact search: WU130X.1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A07","url":"https://www.aliexpress.us/w/wholesale-sony-a7c-ii-28-60-silver.html","title":"AliExpress exact search: Sony A7C II 28-60 silver","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A08","url":"https://www.aliexpress.us/w/wholesale-sony-alpha-7-v-body.html","title":"AliExpress exact search: Sony Alpha 7 V body","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"A09","url":"https://www.aliexpress.us/w/wholesale-insta360-go-3s-64gb-white.html","title":"AliExpress exact search: Insta360 GO 3S 64GB white","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"S19","url":"https://www.pricearchive.org/aliexpress.com/item/1005013026385525","title":"AliExpress-indexed Roborock P20 Max candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S20","url":"https://www.pricearchive.org/aliexpress.com/item/1005012312044183","title":"AliExpress-indexed WORX WU130X candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K04"]},{"source_id":"S21","url":"https://www.reddit.com/r/Insta360/comments/1kilmw5/buying_a_go_3s_on_aliexpress_not_sold_by_insta360/","title":"Buying a GO 3S on AliExpress, not sold by Insta360","published_at":"2025-05-09","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K05"]},{"source_id":"S22","url":"https://www.aliexpress.us/item/3256808554560690.html","title":"GO 3S candidate linked from Reddit","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"login_required","claims_supported":["K05"]}],"claims":[{"claim_id":"K01","claim":"All nine assigned Temu exact-query original search pages were inaccessible in this research run; this supports BLOCKED, not NOT_OBSERVED or VERIFIED_UNAVAILABLE.","classification":"FACT","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09"],"confidence":"high","counterevidence":"Search-engine indexes may expose related pages, but no original Temu listing was verified."},{"claim_id":"K02","claim":"All nine assigned AliExpress exact-query original searches were inaccessible, blocked, 403, or non-verifying page shells; no listing fields were accepted from snippets.","classification":"FACT","source_ids":["A01","A02","A03","A04","A05","A06","A07","A08","A09"],"confidence":"high","counterevidence":"External indexes contain related AliExpress candidates, so marketplace absence cannot be inferred."},{"claim_id":"K03","claim":"A secondary index identifies AliExpress item 1005013026385525 as a Roborock P20 Max candidate, but the original item could not be verified; exact A2950RR plumbing variant, seller, stock, warehouse and ZIP10001 delivered price remain unknown.","classification":"FACT","source_ids":["S19"],"confidence":"medium","counterevidence":"Original AliExpress item page was inaccessible."},{"claim_id":"K04","claim":"A secondary index identifies AliExpress item 1005012312044183 as WORX WU130X 12V 40Nm without battery and charger; this does not establish the frozen WU130X.1 2.0Ah single-battery bundle.","classification":"FACT","source_ids":["S20"],"confidence":"medium","counterevidence":"Original AliExpress item page was inaccessible and bundle differs from frozen variant."},{"claim_id":"K05","claim":"Historical community evidence discusses a third-party GO 3S 128GB AliExpress listing, not the frozen 64GB white standard version; its linked AliExpress page required login during this run.","classification":"FACT","source_ids":["S21","S22"],"confidence":"medium","counterevidence":"Historical/community evidence cannot establish current 2026 exact coverage."},{"claim_id":"K06","claim":"This batch contains 18 platform-SKU checks, 0 verified offers and 18 blocked checks, yielding a batch verification-missing rate of 1.0.","classification":"INFERENCE","source_ids":["T01","T02","T03","T04","T05","T06","T07","T08","T09","A01","A02","A03","A04","A05","A06","A07","A08","A09"],"confidence":"high","counterevidence":"A different public browsing environment may expose the pages; the statistic is not a market-wide coverage rate."}],"data_gaps":["No directly verified seller/item offer, marketplace exact variant, stock, US warehouse, ZIP10001 delivery, ordinary delivered price, weight, dimensions, shipping components, tariff classification/source/rate, or A/B/C savings.","Secondary indexes and community evidence were not substituted for original marketplace-page verification.","Four upstream shipment-structure definitions were not provided, so all four remain separate and null."],"coverage":[
{"sku_id":"C10-S01","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Roborock P20 Max A2950RR","source_ids":["T01"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Roborock P20 Max A2950RR","source_ids":["A01","S19"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Secondary index found AliExpress item 1005013026385525 titled Roborock P20 Max; original item page was not verified, so this is anti-absence evidence only.","Non-automatic-water A2950RR variant was not established overseas."]},
{"sku_id":"C10-S02","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Roborock P20 Max automatic water A2950RR","source_ids":["T02"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Roborock P20 Max automatic water A2950RR","source_ids":["A02"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Automatic water/drainage hardware variant was not verified; related P20 Max indexing cannot be promoted to exact."]},
{"sku_id":"C10-S03","category_id":"C10","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DJI ROMO P water tank","source_ids":["T03"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DJI ROMO P water tank","source_ids":["A03"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Transparent robot plus transparent base and water-tank version were not directly observed on either platform."]},
{"sku_id":"C11-S01","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DZC1050-26BT","source_ids":["T04"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"DZC1050-26BT","source_ids":["A04"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["No direct evidence established exact 1050W DZC1050-26BT, safety clutch, voltage/plug, inventory or US warehouse."]},
{"sku_id":"C11-S02","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"WJZ1601S","source_ids":["T05"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"WJZ1601S","source_ids":["A05"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["No direct evidence established WJZ1601S 16V dual-battery bundle, charger region, inventory or warehouse."]},
{"sku_id":"C11-S03","category_id":"C11","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"WU130X.1","source_ids":["T06"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"WU130X.1","source_ids":["A06","S20"]}],"access_limitations":["blocked_original_search_or_product_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Secondary index found item 1005012312044183 as WU130X 12V 40Nm without battery/charger; frozen WU130X.1 requires 2.0Ah single-battery bundle, so exact match is not established."]},
{"sku_id":"C12-S01","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Sony A7C II 28-60 silver","source_ids":["T07"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Sony A7C II 28-60 silver","source_ids":["A07"]}],"access_limitations":["blocked_or_403_search_page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Silver body plus FE 28-60mm kit and region/bundle were not directly verified."]},
{"sku_id":"C12-S02","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Sony Alpha 7 V body","source_ids":["T08"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Sony Alpha 7 V body","source_ids":["A08"]}],"access_limitations":["blocked_or_nonverifying_page_shell"]},"china_head_us_middle_tail_status":"unresolved","caveats":["ILCE-7M5/Alpha 7 V body-only official-set configuration was not directly verified."]},
{"sku_id":"C12-S03","category_id":"C12","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Insta360 GO 3S 64GB white","source_ids":["T09"]}],"access_limitations":["blocked_original_search_page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Insta360 GO 3S 64GB white","source_ids":["A09","S21","S22"]}],"access_limitations":["blocked_original_search_page","historical_candidate_login_required"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Reddit linked a historical third-party GO 3S 128GB offer; it is not the frozen 64GB white standard bundle and the AliExpress candidate redirected to login."]}
]}
```
=== UNEDITED W4-B-batch05; SHA256 59fd9269e0323d091bf95369c6b12e41ee5e2537eff4dae6a6593f24719be74c ===
## 1. 直接回答

本批次保持 9 个冻结 SKU 原样，未替换、未跨批次。Web research 可用，但本环境对 **Temu 与 AliExpress 的原始搜索/商品页均无法取得足以核验 seller、精确版本、库存、US warehouse、ZIP10001 delivered price 的页面内容**；因此 18 个“SKU×平台”检查全部记为 **BLOCKED**，而不是 NOT_OBSERVED、更不是 VERIFIED_UNAVAILABLE。直接可用 offer 为 0/18，字段缺失率 100%；这只是**本批次访问缺失率**，不代表两平台或市场覆盖率。

## 2. 证据表

| SKU | 冻结 head / exact | Temu | AliExpress | 判定 |
|---|---|---|---|---|
| C13-S01 | true / true | BLOCKED | BLOCKED | 两平台精确搜索原始页均不可读。([Invalid URL]()) |
| C13-S02 | true / true | BLOCKED | BLOCKED | 同上。([Invalid URL]()) |
| C13-S03 | false / true | BLOCKED | BLOCKED | 充气泵精确查询页均受阻。([Invalid URL]()) |
| C14-S01 | false / true | BLOCKED | BLOCKED | NXZQU61017 查询无法直接读取。([Invalid URL]()) |
| C14-S02 | false / true | BLOCKED | BLOCKED | Halbertec/战戟5000 查询受阻。([Invalid URL]()) |
| C14-S03 | false / false | BLOCKED | BLOCKED | Ali 有第三方索引到疑似商品，但原始 Ali 页打不开，故不算 observed。([Invalid URL]()) |
| C15-S01 | true / true | BLOCKED | BLOCKED | 找到第三方指向 P2S Combo 的 Ali item，原页仍被阻断。([Invalid URL]()) |
| C15-S02 | false / true | BLOCKED | BLOCKED | A1 原始平台搜索不可读。([Invalid URL]()) |
| C15-S03 | false / true | BLOCKED | BLOCKED | Space Pi V2 Plus 原始平台搜索不可读。([Invalid URL]()) |

## 3. 一级来源

一级来源只用于**型号/版本边界反查**，不代替 Temu/Ali coverage。70mai 美国官网当前名称为 **Dash Cam 4K M800**，明确双录、4G compatible，并写明 **128GB 内置 eMMC**；这与冻结项“M800Pro、无卡”的字面版本不能自动视为 exact。[70mai](https://www.70mai.com/us/m800/) DDPAI 官网可核 MINI PRO 4K、24/7 parking monitoring，但当前官网页为 sold out，且未由该页证明冻结项的“360°旋转+无卡套餐”。[DDPAI Global](https://store.ddpai.com/products/mini-pro-4k)

Naturehike 官方 Cloud Up Pro 2P 页面直接出现灰红配色图，并明确 20D nylon、210×130×105 cm、packed weight 1.53 kg，支持冻结 C14-S03 的产品身份线索，但不能修复其冻结的 `exact_variant_verified=false`。[Naturehike](https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent) Li-Ning 官方区域页确认 Halbertec 5000 约 84g、落在 4U/3U 边界，但 Ali/Temu 精确 4U 空拍仍未核。[Li-ning](https://li-ning.co.uk/product/li-ning-halbertec-5000/)

## 4. 论坛证据

Bambu 官方论坛的 P2S 发布帖确认 P2S/P2S Combo 产品身份；另一个用户讨论中有人从 AliExpress 买到的是 **P2S buffer 配件**，不是 P2S Combo 整机。因此该论坛证据不能用于 C15-S01 的 exact offering。[Bambu Lab Community Forum](https://forum.bambulab.com/t/the-icon-redefined-meet-the-p2s/201263)

## 5. 反证

最重要的反证是跨地区硬件/版本不能靠品牌型号合并。Creality 官方把 Space Pi V2 Plus 的 US Plug 与 CN Plug 分列为不同 item number（US 4005010154、CN 4005010166），所以冻结的“大陆版”不能被任何美国插头 listing 冒充 exact。[Creality VIP Mall](https://mvip.creality.com/en/goods/goodsDetail/2645) 同理，M800 海外官网内置 eMMC 与冻结“无卡”表述存在明显版本边界。

## 6. 置信度

对“**本环境未能直接核验任何 Temu/Ali offer**”置信度高；对“两平台不存在这些商品”置信度极低，因此没有给 VERIFIED_UNAVAILABLE。A/B/C 三桶均为 0 个可计数 offer；未把图片、snippet、第三方价格缓存或社区链接升级为 A/B/C。

## 7. 缺口

seller/item、库存、US warehouse、ZIP10001 运费、普通公开成交价、会员/券价、重量运输计费、HTS 分类与关税来源全部保持 null。未进入结账，因此 **US sales tax 不估算、不计入 delivered price**。四种运输结构未在本分段给出标签定义，故分别保留四个未观测槽位，不合并、不自行命名。

## 8. 意外发现

C14-S03 的官方全球页实际上加强了“灰红/2人/20D”组合的真实性，但冻结前仍只有 provisional variant mapping，所以仍保持 `exact_variant_verified=false`。[Naturehike](https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent) C15-S03 则恰好相反：官方明确证明插头 SKU 分区，使“大陆版→美国商品 exact”更难成立。[Creality VIP Mall](https://mvip.creality.com/en/goods/goodsDetail/2645)

## 9. 自我反驳

“原始页打不开”可能是研究工具/反爬限制，而非普通美国消费者实际看不到；因此 BLOCKED 不能解释为缺货或无覆盖。第三方索引也说明至少 C14-S03、C15-S01 存在值得复核的 Ali 候选，但按预注册规则，在原页未读到 variant、seller、stock、delivery 前不能计为 observed。

## 10. 下一实验

下一轮应仅对同一 9 个冻结 SKU，在**可读取公开商品页但仍不登录、不下单**的美国区浏览环境重复：锁 ZIP10001 → 核型号/版本/捆绑 → seller/item → US warehouse/库存 → ordinary delivered price → 四运输结构 → HTS 来源。优先复核 C14-S03 的 Ali item 与 C15-S01 的 P2S Combo 候选，不扩样本。

```json
{"job_id":"W4-B-batch05","parent_replicate":"W4-B","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185","assigned_sku_ids":["C13-S01","C13-S02","C13-S03","C14-S01","C14-S02","C14-S03","C15-S01","C15-S02","C15-S03"],"categories":[{"category_id":"C13","status":"all_6_platform_checks_blocked_no_offer_verified"},{"category_id":"C14","status":"all_6_platform_checks_blocked_no_offer_verified"},{"category_id":"C15","status":"all_6_platform_checks_blocked_no_offer_verified"}],"coverage_counts":{"assigned_skus":9,"platform_sku_checks":18,"exact_observed":0,"oem_observed":0,"comparable_only":0,"reseller_only":0,"not_observed":0,"blocked":18,"login_required":0,"verified_unavailable":0,"directly_usable_offers":0,"missing_rate":1.0},"comparison_context":{"destination":"US ZIP10001","us_sales_tax_treatment":"not estimated or included; checkout not performed","tariff_classification":null,"tariff_source":null,"quote_assumptions":"No delivered-cost quote created because no directly reliable marketplace offer was observable.","shipment_structures":[{"structure_slot":1,"definition":null,"quote":null,"status":"UNOBSERVED"},{"structure_slot":2,"definition":null,"quote":null,"status":"UNOBSERVED"},{"structure_slot":3,"definition":null,"quote":null,"status":"UNOBSERVED"},{"structure_slot":4,"definition":null,"quote":null,"status":"UNOBSERVED"}],"shipment_structure_note":"Four slots preserved separately; their semantic labels were not supplied in this batch prompt and were not invented."},"sources":[{"source_id":"S01","url":"https://www.temu.com/search_result.html?search_key=70mai%20M800Pro","title":"Temu search: 70mai M800Pro","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S02","url":"https://www.aliexpress.com/w/wholesale-70mai-m800pro.html","title":"AliExpress search: 70mai M800Pro","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S03","url":"https://www.temu.com/search_result.html?search_key=DDPAI%20MINIPro%204K","title":"Temu search: DDPAI MINIPro 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S04","url":"https://www.aliexpress.com/w/wholesale-ddpai-minipro-4k.html","title":"AliExpress search: DDPAI MINIPro 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S05","url":"https://www.temu.com/search_result.html?search_key=70mai%20Youth%20Edition%202%20tire%20inflator","title":"Temu search: 70mai Youth Edition 2 inflator","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S06","url":"https://www.aliexpress.com/w/wholesale-70mai-youth-edition-2.html","title":"AliExpress search: 70mai Youth Edition 2","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S07","url":"https://www.temu.com/search_result.html?search_key=MOBI%20GARDEN%20NXZQU61017","title":"Temu search: MOBI GARDEN NXZQU61017","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S08","url":"https://www.aliexpress.com/w/wholesale-mobi-garden-nxzqu61017.html","title":"AliExpress search: MOBI GARDEN NXZQU61017","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S09","url":"https://www.temu.com/search_result.html?search_key=Li-Ning%20Halbertec%205000%204U","title":"Temu search: Li-Ning Halbertec 5000 4U","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S10","url":"https://www.aliexpress.com/w/wholesale-li-ning-halbertec-5000.html","title":"AliExpress search: Li-Ning Halbertec 5000","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S11","url":"https://www.temu.com/search_result.html?search_key=Naturehike%20Cloud%20Up%20Pro%2020D","title":"Temu search: Naturehike Cloud Up Pro 20D","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S12","url":"https://www.aliexpress.com/item/1005008302503831.html","title":"AliExpress candidate: Naturehike Cloud Up Pro 2-Person","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02","K05"]},{"source_id":"S13","url":"https://www.temu.com/search_result.html?search_key=Bambu%20Lab%20P2S%20Combo","title":"Temu search: Bambu Lab P2S Combo","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S14","url":"https://ko.aliexpress.com/item/1005010542893160.html","title":"AliExpress candidate: Bambu Lab P2S AMS Combo","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02","K07"]},{"source_id":"S15","url":"https://www.temu.com/search_result.html?search_key=Bambu%20Lab%20A1","title":"Temu search: Bambu Lab A1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S16","url":"https://www.aliexpress.com/w/wholesale-bambu-lab-a1.html","title":"AliExpress search: Bambu Lab A1","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S17","url":"https://www.temu.com/search_result.html?search_key=Creality%20Space%20Pi%20V2%20Plus","title":"Temu search: Creality Space Pi V2 Plus","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S18","url":"https://www.aliexpress.com/w/wholesale-space-pi-v2-plus.html","title":"AliExpress search: Space Pi V2 Plus","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K02"]},{"source_id":"S19","url":"https://www.70mai.com/us/m800/","title":"70mai Dash Cam 4K M800","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S20","url":"https://store.ddpai.com/products/mini-pro-4k","title":"DDPAI MINI PRO 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},{"source_id":"S21","url":"https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent","title":"Naturehike Cloud Up Pro 2-Person","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},{"source_id":"S22","url":"https://li-ning.co.uk/product/li-ning-halbertec-5000/","title":"Li-Ning Halbertec 5000","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},{"source_id":"S23","url":"https://mvip.creality.com/en/goods/goodsDetail/2645","title":"Creality Space Pi V2 Plus Filament Dryer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},{"source_id":"S24","url":"https://forum.bambulab.com/t/the-icon-redefined-meet-the-p2s/201263","title":"The Icon, Redefined — Meet the P2S","published_at":"2025-10-14","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K07"]},{"source_id":"S25","url":"https://forum.bambulab.com/t/p2s-buffer-availability/206346","title":"P2S buffer availability?","published_at":"2025-11-06","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K07"]}],"claims":[{"claim_id":"K01","claim":"All 18 assigned SKU-platform direct checks were access-blocked at the original Temu/AliExpress page level.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"External search indexes sometimes exposed generic or candidate listings, but original pages could not be reliably read."},{"claim_id":"K02","claim":"No Temu/AliExpress exact, OEM, comparable or reseller offer is counted because seller, exact variant, stock, warehouse and delivered price were not directly verified on an original marketplace page.","classification":"INFERENCE","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"This is an evidence-status conclusion, not evidence that such offers do not exist."},{"claim_id":"K03","claim":"70mai's US first-party page calls the product Dash Cam 4K M800 and specifies built-in 128GB eMMC plus separate 4G hardwire dependency, so it cannot automatically be equated with the frozen M800Pro/no-card bundle.","classification":"FACT","source_ids":["S19"],"confidence":"high","counterevidence":"Regional naming may differ; the frozen domestic exact-variant verification remains preserved."},{"claim_id":"K04","claim":"DDPAI first-party evidence confirms MINI PRO 4K and 24/7 parking monitoring, but does not by itself verify the frozen 360-degree/no-card bundle on either marketplace.","classification":"FACT","source_ids":["S20"],"confidence":"high","counterevidence":"A marketplace-specific variant could exist but was not directly observable."},{"claim_id":"K05","claim":"Naturehike first-party evidence supports a Cloud Up Pro 2-person grey/red configuration and 20D nylon specifications, but AliExpress exact coverage remains blocked.","classification":"FACT","source_ids":["S21","S12"],"confidence":"high","counterevidence":"Frozen exact_variant_verified remains false because domestic aggregate-variant mapping was not locked pre-freeze."},{"claim_id":"K06","claim":"Regional hardware/variant distinctions matter: Creality lists separate US and CN plug item numbers for Space Pi V2 Plus; Li-Ning first-party material supports the Halbertec 5000 model/weight family but not marketplace exact coverage.","classification":"FACT","source_ids":["S22","S23"],"confidence":"high","counterevidence":"No direct Temu/AliExpress offer was readable to determine which region variant was being sold."},{"claim_id":"K07","claim":"Bambu community evidence of AliExpress purchasing concerns P2S buffer accessories and cannot establish P2S Combo printer coverage; the exact-looking AliExpress P2S Combo candidate remained blocked.","classification":"FACT","source_ids":["S14","S24","S25"],"confidence":"high","counterevidence":"A secondary indexed P2S Combo listing exists, but its seller, current stock, US delivery and bundle could not be verified directly."}],"coverage":[
{"sku_id":"C13-S01","category_id":"C13","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["70mai M800Pro; 2026; front/rear; 4K; 4G; no-card","destination US ZIP10001"],"access_limitations":["S01 direct Temu search page not accessible; snippets/page shells excluded"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["70mai M800Pro; 2026; front/rear; 4K; 4G; no-card","destination US ZIP10001"],"access_limitations":["S02 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","Official US M800 naming/storage differs from frozen wording; no cross-region exact inference."]},
{"sku_id":"C13-S02","category_id":"C13","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["DDPAI MINIPro 4K; 360-degree; parking; no-card","destination US ZIP10001"],"access_limitations":["S03 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["DDPAI MINIPro 4K; 360-degree; parking; no-card","destination US ZIP10001"],"access_limitations":["S04 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen domestic head/exact flags preserved.","First-party MINI PRO 4K existence does not verify the frozen bundle on either marketplace."]},
{"sku_id":"C13-S03","category_id":"C13","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["70mai Youth Edition 2 tire inflator; 2026","destination US ZIP10001"],"access_limitations":["S05 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["70mai Youth Edition 2 tire inflator; 2026","destination US ZIP10001"],"access_limitations":["S06 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["not_supported reflects frozen head_status_verified=false, not absence from US marketplaces."]},
{"sku_id":"C14-S01","category_id":"C14","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["MOBI GARDEN NXZQU61017; Cold Mountain 2 Plus; red-gray; 2-person; snow skirt","destination US ZIP10001"],"access_limitations":["S07 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["MOBI GARDEN NXZQU61017; Cold Mountain 2 Plus; red-gray; 2-person; snow skirt","destination US ZIP10001"],"access_limitations":["S08 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["Domestic slot remains non-verified-head as frozen."]},
{"sku_id":"C14-S02","category_id":"C14","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Li-Ning Halbertec/战戟5000; 4U; unstrung","destination US ZIP10001"],"access_limitations":["S09 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Li-Ning Halbertec/战戟5000; 4U; unstrung","destination US ZIP10001"],"access_limitations":["S10 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["First-party model evidence does not establish platform seller/bundle."]},
{"sku_id":"C14-S03","category_id":"C14","head_status_verified":false,"exact_variant_verified":false,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Naturehike Cloud Up Pro; 2-person; 20D; grey-red","destination US ZIP10001"],"access_limitations":["S11 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Naturehike Cloud Up Pro; 2-person; 20D; grey-red; candidate item 1005008302503831","destination US ZIP10001"],"access_limitations":["S12 original AliExpress item blocked; indexed existence not accepted as offer evidence"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen exact_variant_verified=false preserved.","First-party global product page supports 2P grey/red and 20D but does not resolve frozen domestic aggregate mapping."]},
{"sku_id":"C15-S01","category_id":"C15","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Bambu Lab P2S/P2SC Combo; multicolor set","destination US ZIP10001"],"access_limitations":["S13 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Bambu Lab P2S/P2SC AMS Combo; candidate item 1005010542893160","destination US ZIP10001"],"access_limitations":["S14 original AliExpress item blocked; community accessory evidence excluded from printer offer"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen verified-head/exact flags preserved.","No current US seller, stock, warehouse or bundle was directly verified."]},
{"sku_id":"C15-S02","category_id":"C15","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Bambu Lab A1; standalone; mainland version","destination US ZIP10001"],"access_limitations":["S15 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Bambu Lab A1; standalone; mainland version","destination US ZIP10001"],"access_limitations":["S16 original AliExpress search page blocked; generic A1 cannot be assumed mainland version"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["Frozen mainland-version requirement retained.","No US-region hardware was substituted as exact."]},
{"sku_id":"C15-S03","category_id":"C15","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Creality Space Pi V2 Plus; mainland/CN version","destination US ZIP10001"],"access_limitations":["S17 direct Temu search page not accessible"],"observed_at":"2026-10-06"},"aliexpress":{"observation_status":"BLOCKED","exact_offering_observed":false,"oem_observed":false,"comparable_observed":false,"reseller_only_observed":false,"us_warehouse_evidence_observed":false,"inventory_observed":false,"offers":[],"search_scope":["Creality Space Pi V2 Plus; mainland/CN version","destination US ZIP10001"],"access_limitations":["S18 original AliExpress search page blocked"],"observed_at":"2026-10-06"},"china_head_us_middle_tail_status":"not_supported","caveats":["Creality first-party page distinguishes CN and US plug item numbers; US-plug listing would not be exact to frozen mainland variant without additional evidence.","Packing size/weight from first party: 343x226x300mm, gross weight 2500g; no marketplace shipping quote observed."]}
],"data_gaps":["No directly readable Temu or AliExpress product page for any assigned SKU.","All marketplace seller/item/stock/US-warehouse/ordinary-delivered-price fields remain null.","No membership, coupon, subsidy or targeted price was treated as ordinary price.","ZIP10001 shipping could not be quoted without a readable offer page; no checkout was attempted.","US sales tax remains unestimated and excluded.","No HTS classification or tariff rate was manufactured for unverified offers.","Four shipment structures were kept as separate unresolved slots because their labels were not supplied in this batch prompt.","Third-party indexes and snippets were not used to prove price, seller, stock, exact variant or warehouse.","Sources attested here remain subject to coordinator review."]}
```
=== UNEDITED W4-B-batch06; SHA256 322db564d21001beb0f431c16eb87057217ffcd27d18428f8765227be8e627e0 ===
## 一、直接回答

本批次严格只调查冻结的 9 个 SKU、Temu/AliExpress 两个平台。18 个“SKU×平台”单元均完成一次明确检索并尝试打开第一方搜索/商品入口；**18/18 第一方页面均无法在当前网页环境读取，因此全部记为 `BLOCKED`**，不是 `NOT_OBSERVED`，更不是 `VERIFIED_UNAVAILABLE`。没有任何 SKU 可升级为 `EXACT_OBSERVED/OEM_OBSERVED/COMPARABLE_ONLY/RESELLER_ONLY`。

本批次：9/9 SKU 已尝试；0 个第一方已核验 offer；普通公开 delivered price、库存、US warehouse 证据缺失率均 **100%**。这只描述 W4-B-batch06，不代表全样本或全市场覆盖率。

比较端点固定为**美国 ZIP10001 的普通公开到手价，US sales tax 排除在比较端点之外**；会员价、定向券、补贴等必须另列。本轮因第一方受阻，四种运输结构均保持独立的 `null`，未合并、未估运费、未制造关税分类或税率。

## 二、证据表

| SKU | 冻结 head / exact | Temu | AliExpress | 结论 |
|---|---|---|---|---|
| C16-S01 COACH CV976 | true / true | BLOCKED | BLOCKED | 无第一方 offer ([Invalid URL]()) |
| C16-S02 Nike CW2288-111 白42 | true / true | BLOCKED | BLOCKED | 二级索引有 CW2288-111 候选，但 42 码/美国区/库存均未核验 ([Invalid URL]()) |
| C16-S03 adidas JI0079 37码 | false / true | BLOCKED | BLOCKED | 二级索引定位 JI0079 候选商品 ID，但原页打不开、37码未核验 ([Invalid URL]()) |
| C17-S01 CHAHUA 34L×3 | true / true | BLOCKED | BLOCKED | 无可读第一方结果 ([Invalid URL]()) |
| C17-S02 CHAHUA 30.5L×2 | true / true | BLOCKED | BLOCKED | 无可读第一方结果 ([Invalid URL]()) |
| C17-S03 JEKO&JEKO 5层 | false / true | BLOCKED | BLOCKED | 无可读第一方结果 ([Invalid URL]()) |
| C18-S01 LEGO 10698+礼袋 | true / true | BLOCKED | BLOCKED | 礼袋捆绑无法核验 ([Invalid URL]()) |
| C18-S02 CRYBABY Vacation Mode On 随机1个 | true / true | BLOCKED | BLOCKED | 有二级“pendant 1PC/6PCS”线索，另有同系列冰箱贴反例；均不能算 A ([Invalid URL]()) |
| C18-S03 BANDAI RG RX-78-2 Ver.2.0 | false / true | BLOCKED | BLOCKED | 两个二级 AliExpress 候选，原始商品页打不开 ([Invalid URL]()) |

## 三、一级来源

品牌一级页只用于锁定“什么才算 exact”，不用于本工作流的 Temu/AliExpress 价格：Nike 官方确认 CW2288-111 为 White/White；adidas 官方确认 JI0079；LEGO 官方确认 10698 为 790 件 Large Creative Brick Box，因此冻结 SKU 的“赠礼袋”仍必须额外一致；Bandai 官方资料明确区分 RG 1/144 RX-78-2 Gundam Ver.2.0。[Nike.com](https://www.nike.com/t/air-force-1-07-mens-shoes-DZejrQoC/CW2288-111)

## 四、论坛证据

论坛只作版本辨识辅助，不证明平台覆盖。社区资料同样把 CW2288-111指向白色 AF1；Gunpla 社区明确讨论 Ver.1.0 与 Ver.2.0 的结构差异，因此 RX-78-2 不可把旧版或其他比例冒充 exact。[Reddit](https://www.reddit.com/r/Pandabuy/comments/18vuly5?utm_source=chatgpt.com)

## 五、反证

不能把“BLOCKED”解释成“平台没有”。尤其 AliExpress 二级索引在 2026-10-06 附近仍能看到 JI0079 与 RG RX-78-2 Ver.2.0 的候选记录；这正是反对 `VERIFIED_UNAVAILABLE` 的证据。[Pricearchive.org](https://ms.pricearchive.org/aliexpress.com/item/1005012746466736)

同样，CRYBABY 搜索还出现“同系列但冰箱贴”的条目，说明系列名相同绝不足以证明 A exact，甚至不能自动成为 C。[Pricearchive.org](https://ro.pricearchive.org/aliexpress.com/item/1005010230412412)

## 六、置信度

**高置信度**：冻结 `head_status_verified`/`exact_variant_verified` 已原样保留；18 个第一方访问均受阻；没有任何第一方价格、库存、卖家、仓库或 ZIP10001 运费被实际观察。

**低置信度**：两平台真实当前覆盖范围及可购买性；因此 `china_head_us_middle_tail_status` 九行全部为 `unresolved`。

## 七、缺口

最大缺口是第一方动态页面无法读取，导致 US 地区、ZIP10001、具体尺码/容量/捆绑、seller、库存、US warehouse、商品价、运费及优惠类型全部为 `null`。二级索引价格没有写入 offer 成交价，也未用于节省率、关税或 A/B/C 统计。

## 八、意外发现

AliExpress 的二级索引并非完全空白：CW2288-111、JI0079、CRYBABY pendant 以及 RX-78-2 Ver.2.0 都存在候选线索；其中 Bandai 还出现多 SKU/多版本式商品页线索。这意味着“找不到搜索引擎结果”和“平台证实无货”之间差距很大。[Pricearchive.org](https://ms.pricearchive.org/search/aliexpress.com/%D0%BA%D0%BE%D0%B6%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5-%D0%BA%D1%80%D0%BE%D1%81%D1%81%D0%BE%D0%B2%D0%BA%D0%B8-%D0%BC%D1%83%D0%B6%D1%81%D0%BA%D0%B8%D0%B5-nike/1?utm_source=chatgpt.com)

## 九、自我反驳

也可以主张二级索引足够证明 AliExpress “有货”；但这会违反本次规则：无法确认美国区、当前库存、最终 variant、卖家以及 ZIP10001 配送，且价格索引自己也提示平台实际价可能不同。因此本批次宁可留下 `BLOCKED/null`，不把二级页面升级为 A 或成交价格。

## 十、下一实验

只对**同一冻结 9 SKU**复核：使用能执行平台 JavaScript、无需登录的美国公开会话，设置 ZIP10001；逐个重开现有搜索词及已发现候选 ID，一次记录型号/尺码或容量/捆绑、seller、stock、warehouse、普通公开价、shipping、时间戳。仍打不开即保持 `BLOCKED`，不换型号、不扩大样本。

下面 JSON 保持有效格式；为避免把不可核验的裸链接伪装成已读页面，`url` 为 `null`，并以 `source_ref` 对应上面的可点击网页证据。

```json
{
  "job_id": "W4-B-batch06",
  "parent_replicate": "W4-B",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "assigned_sku_ids": ["C16-S01","C16-S02","C16-S03","C17-S01","C17-S02","C17-S03","C18-S01","C18-S02","C18-S03"],
  "categories": [
    {"category_id":"C16","status":"3/3 frozen SKUs attempted; Temu 3 BLOCKED; AliExpress 3 BLOCKED; 0 first-party verified offers"},
    {"category_id":"C17","status":"3/3 frozen SKUs attempted; Temu 3 BLOCKED; AliExpress 3 BLOCKED; 0 first-party verified offers"},
    {"category_id":"C18","status":"3/3 frozen SKUs attempted; Temu 3 BLOCKED; AliExpress 3 BLOCKED; 0 first-party verified offers"}
  ],
  "cost_policy": {
    "destination":"US ZIP10001",
    "comparison_endpoint":"ordinary public item price plus publicly visible delivery to ZIP10001",
    "us_sales_tax_treatment":"excluded from comparison endpoint; not observed",
    "membership_coupon_subsidy_treatment":"must be separate; none observed",
    "shipment_structures":{"structure_1":null,"structure_2":null,"structure_3":null,"structure_4":null},
    "shipment_structure_note":"four structures preserved separately; names not supplied in this batch prompt and no verified quote was obtained",
    "tariff_classification":null,
    "tariff_source":null,
    "tariff_rate":null
  },
  "batch_statistics": {
    "frozen_skus_attempted":9,
    "platform_sku_cells_attempted":18,
    "blocked_cells":18,
    "exact_observed":0,
    "oem_observed":0,
    "comparable_only":0,
    "reseller_only":0,
    "verified_unavailable":0,
    "first_party_verified_offer_count":0,
    "ordinary_delivered_price_missing_rate":1.0,
    "stock_missing_rate":1.0,
    "us_warehouse_evidence_missing_rate":1.0,
    "scope":"W4-B-batch06 only; not a full-sample or market coverage rate"
  },
  "sources": [
    {"source_id":"S01","url":null,"source_ref":"turn184288view0","title":"Temu first-party exact search attempt: COACH CV976","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S02","url":null,"source_ref":"turn207181view1","title":"Temu first-party exact search attempt: CW2288-111","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S03","url":null,"source_ref":"turn184288view1","title":"Temu first-party exact search attempt: JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S04","url":null,"source_ref":"turn184288view2","title":"Temu first-party exact search attempt: CHAHUA 34L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S05","url":null,"source_ref":"turn184288view3","title":"Temu first-party exact search attempt: CHAHUA 30.5L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S06","url":null,"source_ref":"turn184288view4","title":"Temu first-party exact search attempt: JEKO&JEKO 5 drawer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S07","url":null,"source_ref":"turn207181view0","title":"Temu first-party exact search attempt: LEGO 10698","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S08","url":null,"source_ref":"turn184288view5","title":"Temu first-party exact search attempt: CRYBABY Vacation Mode On","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S09","url":null,"source_ref":"turn184288view6","title":"Temu first-party exact search attempt: RG RX-78-2 Ver.2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01","K06"]},
    {"source_id":"S10","url":null,"source_ref":"turn184288view7","title":"AliExpress US first-party exact search attempt: COACH CV976","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K06"]},
    {"source_id":"S11","url":null,"source_ref":"turn207181view2","title":"AliExpress US first-party exact search attempt: CW2288-111","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K03","K06"]},
    {"source_id":"S12","url":null,"source_ref":"turn207181view3","title":"AliExpress US first-party exact search attempt: JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K04","K06"]},
    {"source_id":"S13","url":null,"source_ref":"turn184288view8","title":"AliExpress US first-party exact search attempt: CHAHUA 34L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K06"]},
    {"source_id":"S14","url":null,"source_ref":"turn184288view9","title":"AliExpress US first-party exact search attempt: CHAHUA 30.5L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K06"]},
    {"source_id":"S15","url":null,"source_ref":"turn184288view10","title":"AliExpress US first-party exact search attempt: JEKO&JEKO 5 drawer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K06"]},
    {"source_id":"S16","url":null,"source_ref":"turn184288view11","title":"AliExpress US first-party exact search attempt: LEGO 10698","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K06"]},
    {"source_id":"S17","url":null,"source_ref":"turn184288view12","title":"AliExpress US first-party exact search attempt: CRYBABY Vacation Mode On","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05","K06"]},
    {"source_id":"S18","url":null,"source_ref":"turn184288view13","title":"AliExpress US first-party exact search attempt: RG RX-78-2 Ver.2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02","K05","K06"]},
    {"source_id":"S19","url":null,"source_ref":"turn106064search5","title":"PriceArchive AliExpress Nike index containing CW2288-111 candidates","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03","K07"]},
    {"source_id":"S20","url":null,"source_ref":"turn800570view0","title":"PriceArchive AliExpress item 1005012746466736, JI0079 candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K04","K07"]},
    {"source_id":"S21","url":null,"source_ref":"turn572312search6","title":"Secondary AliExpress UK listing lead: CRYBABY Vacation Mode On Pendant Blind Box 1PC/6PCS","published_at":"2026-06-25","retrieved_at":"2026-10-06","source_type":"secondary","access_state":"snippet_only","claims_supported":["K05","K07"]},
    {"source_id":"S22","url":null,"source_ref":"turn800570view2","title":"PriceArchive AliExpress item 1005010230412412, CRYBABY fridge magnet wrong-product counterexample","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S23","url":null,"source_ref":"turn800570view3","title":"PriceArchive AliExpress item 1005013164825333, RX-78-2 Ver.2.0 candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05","K07"]},
    {"source_id":"S24","url":null,"source_ref":"turn800570view4","title":"PriceArchive AliExpress item 1005013093026012, multi-variant RX-78-2 Ver.2.0 candidate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05","K07"]},
    {"source_id":"S25","url":null,"source_ref":"turn542709view0","title":"Nike official CW2288-111 product page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S26","url":null,"source_ref":"turn542709view1","title":"adidas official JI0079 product page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S27","url":null,"source_ref":"turn542709view2","title":"LEGO official 10698 product page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S28","url":null,"source_ref":"turn542709view3","title":"Bandai Hobby official RG RX-78-2 Gundam Ver.2.0 manual index","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S29","url":null,"source_ref":"turn893879reddit43","title":"Reddit discussion referencing AF1 code CW2288-111","published_at":"2024-01-01","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K09"]},
    {"source_id":"S30","url":null,"source_ref":"turn893879reddit37","title":"Reddit discussion distinguishing RG RX-78-2 Ver.1.0 and Ver.2.0","published_at":"2025-04-16","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K09"]}
  ],
  "claims": [
    {"claim_id":"K01","claim":"All nine frozen SKUs had a Temu first-party exact-search endpoint attempted and the endpoint was inaccessible in this research environment.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09"],"confidence":"high","counterevidence":"External web indexing may still contain Temu pages; this does not prove Temu unavailability."},
    {"claim_id":"K02","claim":"All nine frozen SKUs had an AliExpress US first-party exact-search endpoint attempted and the endpoint was inaccessible in this research environment.","classification":"FACT","source_ids":["S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"Secondary indexes contain several candidate listings, so blocked access must not be treated as absence."},
    {"claim_id":"K03","claim":"Secondary indexing surfaced AliExpress CW2288-111 candidates, but size 42, US-region availability, seller, stock and delivered price were not verified on the original page.","classification":"FACT","source_ids":["S11","S19"],"confidence":"medium","counterevidence":"The secondary index indicates candidate existence but cannot satisfy the required first-party verification standard."},
    {"claim_id":"K04","claim":"Secondary indexing identified AliExpress item 1005012746466736 as a JI0079 candidate, while the original AliExpress search/detail path was inaccessible and size 37 was not verified.","classification":"FACT","source_ids":["S12","S20"],"confidence":"medium","counterevidence":"The indexed title matches the model but not the complete frozen variant."},
    {"claim_id":"K05","claim":"Secondary sources surfaced CRYBABY and RX-78-2 Ver.2.0 AliExpress candidates; one CRYBABY result was explicitly a fridge magnet rather than the frozen vinyl-plush pendant, demonstrating same-series title is insufficient for exact matching.","classification":"FACT","source_ids":["S17","S18","S21","S22","S23","S24"],"confidence":"medium","counterevidence":"Original US-region platform pages could not be inspected."},
    {"claim_id":"K06","claim":"No first-party seller, current stock, US-warehouse evidence, ordinary public price, ZIP10001 delivery charge or ordinary delivered price was observed in any of the 18 platform-SKU cells.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18"],"confidence":"high","counterevidence":"Secondary price indexes exist for some candidates but are intentionally excluded from transaction-price observation."},
    {"claim_id":"K07","claim":"The secondary candidate records are retained as leads but are excluded from A/B/C match counts and pricing statistics because first-party variant, region and transaction conditions were not verified.","classification":"INFERENCE","source_ids":["S19","S20","S21","S23","S24"],"confidence":"high","counterevidence":"A less strict protocol might accept secondary indexing, but that would violate this batch's stated rules."},
    {"claim_id":"K08","claim":"Official brand sources confirm key model identities used as exact-match guards: CW2288-111, JI0079, LEGO 10698 and RG RX-78-2 Gundam Ver.2.0.","classification":"FACT","source_ids":["S25","S26","S27","S28"],"confidence":"high","counterevidence":"These official pages do not establish Temu or AliExpress coverage."},
    {"claim_id":"K09","claim":"Community evidence can help distinguish identifiers and versions but is not used to establish marketplace coverage, price, seller, inventory or authenticity.","classification":"INFERENCE","source_ids":["S29","S30"],"confidence":"high","counterevidence":"Community posts are not transaction pages."}
  ],
  "coverage": [
    {
      "sku_id":"C16-S01","category_id":"C16","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["COACH CV976 CITY33 exact model/variant search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible","US region/ZIP could not be set or verified","no login attempted"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["COACH CV976 CITY33 exact model/variant search","AliExpress US first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible","no original product page observed","no login attempted"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Frozen domestic head/exact flags preserved unchanged.","No A/B/C match observed; absence not proven."]
    },
    {
      "sku_id":"C16-S02","category_id":"C16","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Nike CW2288-111 Air Force 1 white size 42 exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible","no size-42 offer verified"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"CW2288-111 secondary-index candidate","match_bucket":null,"match_evidence":"secondary index title matches model; white/size 42/US region/bundle not verified on original page","exact_version":null,"stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S11","S19"]}],"search_scope":["CW2288-111 exact search","size 42 and White/White required","AliExpress US first-party search attempted","secondary candidate retained but not counted"],"access_limitations":["first-party search page inaccessible","candidate seller/price/stock/size not promoted from secondary evidence"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Frozen verified-head status retained.","Secondary candidate does not qualify as A exact."]
    },
    {
      "sku_id":"C16-S03","category_id":"C16","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["adidas JI0079 Superstar II size 37 exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"AliExpress candidate item 1005012746466736","match_bucket":null,"match_evidence":"secondary full page identifies JI0079; size 37, region, seller, stock and original product conditions unverified","exact_version":null,"stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S12","S20"]}],"search_scope":["JI0079 exact search","size 37 required","original AliExpress page attempted"],"access_limitations":["first-party search/detail page inaccessible","secondary indexed price not used"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Opportunity SKU remains non-head.","No A/B/C count assigned."]
    },
    {
      "sku_id":"C17-S01","category_id":"C17","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["CHAHUA 34L x3 milk-yellow 45.5x38x31cm exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["CHAHUA 34L x3 milk-yellow exact search","AliExpress US first-party search endpoint attempted"],"access_limitations":["first-party search page inaccessible","no exact capacity/pack/dimensions verified"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Bulky/volumetric shipping cost not estimated.","No observed OEM/comparable promoted."]
    },
    {
      "sku_id":"C17-S02","category_id":"C17","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["CHAHUA 30.5L drawer box two-pack exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["CHAHUA 30.5L drawer box two-pack exact search","AliExpress US first-party search endpoint attempted"],"access_limitations":["first-party search page inaccessible","pack count and capacity unverified"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Bulky/volumetric shipping cost not estimated.","No observed OEM/comparable promoted."]
    },
    {
      "sku_id":"C17-S03","category_id":"C17","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["JEKO&JEKO five-drawer five-layer cabinet exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["JEKO&JEKO five-drawer five-layer cabinet exact search","AliExpress US first-party search endpoint attempted"],"access_limitations":["first-party search page inaccessible","no five-layer exact product observed"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Opportunity SKU remains non-head.","Dimensional-weight cost not estimated."]
    },
    {
      "sku_id":"C18-S01","category_id":"C18","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["LEGO 10698 exact search","gift-bag bundle required","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible","gift-bag bundle not verified"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["LEGO 10698 exact search","gift-bag bundle required","AliExpress US first-party search endpoint attempted"],"access_limitations":["first-party search page inaccessible","no original listing observed"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Standard 10698 alone would not satisfy frozen gift-bag bundle requirement.","No substitute set counted."]
    },
    {
      "sku_id":"C18-S02","category_id":"C18","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["POP MART CRYBABY Vacation Mode On vinyl-plush pendant blind box random 1 exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"secondary lead: Vacation Mode On Pendant Blind Box 1PC/6PCS","match_bucket":null,"match_evidence":"series/form and 1PC option appear in secondary listing; current US original page, seller, stock and random-one configuration not verified","exact_version":null,"stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S17","S21"]},{"url":null,"seller":null,"item":"AliExpress item 1005010230412412 secondary-index result","match_bucket":null,"match_evidence":"rejected candidate: same CRYBABY Vacation Mode On series but product is a fridge magnet, not the frozen vinyl-plush pendant blind box","exact_version":"Fridge Magnet Blind Box","stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S17","S22"]}],"search_scope":["Vacation Mode On pendant blind box exact search","random 1 required","AliExpress US first-party search attempted"],"access_limitations":["first-party page inaccessible","secondary UK/third-party data not used as US offer or current price"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Blind-box randomized content preserved.","Same-series fridge magnet explicitly rejected."]
    },
    {
      "sku_id":"C18-S03","category_id":"C18","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["BANDAI RG 1/144 RX-78-2 Gundam Ver.2.0 exact search","Temu first-party search endpoint attempted","target US ZIP10001"],"access_limitations":["first-party search page inaccessible"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"AliExpress candidate item 1005013164825333","match_bucket":null,"match_evidence":"secondary title states Bandai RG 1/144 RX-78-2 Gundam Ver.2.0; original page, seller, authenticity, US availability and stock unverified","exact_version":null,"stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S18","S23"]},{"url":null,"seller":null,"item":"AliExpress candidate item 1005013093026012","match_bucket":null,"match_evidence":"secondary title combines RX-78-2 Ver.2.0 and RX-178 variants; selected option cannot be inspected, therefore exact match not established","exact_version":null,"stock":null,"warehouse_evidence":null,"region":null,"currency":null,"price":null,"delivery":null,"price_type":null,"shipment_structure":null,"tariff_classification":null,"tariff_source":null,"access_state":"blocked","observed_at":"2026-10-06","source_ids":["S18","S24"]}],"search_scope":["RG 1/144 RX-78-2 Ver.2.0 exact search","AliExpress US first-party search attempted","two secondary candidates retained separately"],"access_limitations":["first-party search/detail pages inaccessible","multi-variant selection cannot be verified"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["Opportunity SKU remains non-head.","Collector-box condition, warehouse and stock all unobserved."]
    }
  ],
  "data_gaps": [
    "All 18 first-party platform-SKU observations are BLOCKED; none may be interpreted as unavailable.",
    "No current first-party seller, inventory, US-warehouse status, public price, shipping charge or delivered price to ZIP10001 was observed.",
    "No A/B/C match was counted because exact region/version/bundle could not be checked on the original marketplace page.",
    "Secondary indexed prices and seller information were intentionally excluded from transactional fields.",
    "No tariff classification or tariff rate was manufactured for missing shipment quotes.",
    "All four shipment structures remain separate null observations rather than being collapsed.",
    "US sales tax is excluded from the comparison endpoint and was not observed.",
    "Unassigned frozen SKUs and other W4 replicates/batches were not researched."
  ]
}
```