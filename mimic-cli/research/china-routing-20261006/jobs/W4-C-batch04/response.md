## 1. 直接回答

截至 **2026-10-06**，仅对冻结批次 **W4-C-batch04** 的 9 个 SKU 执行 Temu / AliExpress 独立覆盖调查，没有替换任何冻结 SKU，也没有查看其他批次结果。

本批次 18 个「SKU×平台」观察单元中：**Temu：9/9 NOT_OBSERVED；AliExpress：4/9 BLOCKED、5/9 NOT_OBSERVED。A/B/C 经原始平台页核验的匹配均为 0。** 因此没有可合法计算的普通公开 delivered price、节省额、US warehouse 比例或关税成本。这里的 `NOT_OBSERVED` 绝不等于无货或无覆盖；`BLOCKED` 也绝不等于有货。

AliExpress 的二级索引确实留下了 P20 Max、WU130X、GO 3S 的型号族候选，但直接打开对应 AliExpress 原商品页均被研究通道阻断，所以没有采用索引价格、卖家、库存或配送信息。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005013026385525?utm_source=chatgpt.com)

## 2. 证据表

| sku_id | 冻结 head/exact | Temu | AliExpress | A/B/C 已核验 | 结论 |
|---|---|---|---|---|---|
| C10-S01 | true/true | NOT_OBSERVED | BLOCKED | 0/0/0 | P20 Max 型号族候选存在，但未说明水箱非上下水版 |
| C10-S02 | true/true | NOT_OBSERVED | BLOCKED | 0/0/0 | 同一候选不能证明自动上下水版 |
| C10-S03 | false/true | NOT_OBSERVED | NOT_OBSERVED | 0/0/0 | 未观察到 ROMO P 水箱版原页 |
| C11-S01 | true/true | NOT_OBSERVED | NOT_OBSERVED | 0/0/0 | 未观察到 DZC1050-26BT |
| C11-S02 | true/true | NOT_OBSERVED | NOT_OBSERVED | 0/0/0 | 未观察到 WJZ1601S 双电套装 |
| C11-S03 | false/true | NOT_OBSERVED | BLOCKED | 0/0/0 | 二级索引有 WU130X，但候选甚至注明不含电池/充电器，不能匹配 2.0Ah 单电 |
| C12-S01 | true/true | NOT_OBSERVED | NOT_OBSERVED | 0/0/0 | 未观察到银色 28–60 套装原页 |
| C12-S02 | true/true | NOT_OBSERVED | NOT_OBSERVED | 0/0/0 | 未观察到 ILCE-7M5 Body Only 原页 |
| C12-S03 | false/true | NOT_OBSERVED | BLOCKED | 0/0/0 | GO 3S 型号族候选缺颜色/64GB/Standard Bundle，原页阻断 |

Temu 的精确外部搜索没有返回上述 SKU 的可核验商品原页，同时直接站内搜索 URL 在本研究通道不可访问；因此采用 `NOT_OBSERVED + access limitation`，而不是 `VERIFIED_UNAVAILABLE`。([Invalid URL]())

## 3. 一级来源

一级来源只用于锁定**版本边界**，不用于推断 Temu/AliExpress 覆盖。石头官方商城将 **P20 Max 上下水版**和**水箱版**分别列示，证明仅写“P20 Max”的 AliExpress 候选不足以区分 C10-S01/C10-S02。[Roborock Official Store](https://mall.roborock.com/?utm_source=chatgpt.com) DJI 官方明确 ROMO P Water Tank Version 为透明机器人/透明基站系列。[DJI Store](https://store.dji.com/lu/product/dji-romo-p-water-tank-version?utm_source=chatgpt.com)

Sony 官方说明 ILCE-7CM2L 配 SEL2860（FE 28-60mm）套机，且 Sony USA 将 Alpha 7 V `ILCE-7M5/B` 的 **Body Only** 与镜头套装分开。[Sony](https://www.sony.com/electronics/support/articles/00302930?utm_source=chatgpt.com) Insta360 官方又把 GO 3S 的颜色、64/128GB 和 Standard Bundle 分成独立选项，因此“GO 3S”泛型号页不能成为 C12-S03 的 A 桶证据。[Insta360 Store](https://store.insta360.com/ph/product/go-3s?c=6617\&from=banner\&utm_source=chatgpt.com)

## 4. 论坛证据

社区中确有用户讨论 AliExpress 上未带 Insta360 品牌名的 GO 3S 第三方 listing，并建议核对卖家历史、评论及真伪；这只能作为**交易风险信号**，不能证明该商品是假货，也不能证明本冻结版本当前可买。[Reddit](https://www.reddit.com/r/Aliexpress/comments/1kim10j?utm_source=chatgpt.com) 另有 2026 年 AliExpress/Insta360 讨论提到区域、进口税和售后可能改变实际成本，进一步说明不能仅凭标题价格构造美国 landed cost。[Reddit](https://www.reddit.com/r/Insta360/comments/1vg1i8j/insat360_go_ultra_from_aliexpress_legit/?utm_source=chatgpt.com)

## 5. 反证

不能得出“AliExpress 没有这些型号”。二级索引近期记录过 Roborock P20 Max、WORX WU130X 和 Insta360 GO 3S 的 AliExpress 商品 ID；这正是把相关单元保留为 `BLOCKED` 而非 `VERIFIED_UNAVAILABLE` 的反证。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005013026385525?utm_source=chatgpt.com)

其中 WU130X 索引候选明确写有 **Without battery and charger**，反而否定它可以直接冒充冻结的 WU130X.1 12V/40Nm/2.0Ah 单电版本。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005012312044183?utm_source=chatgpt.com)

## 6. 置信度

冻结前 `head_status_verified`、`exact_variant_verified` 全部原样保留；未验证 head 的 C10-S03、C11-S03、C12-S03 没有升级。对“本次没有直接核验到任何 A/B/C offer”的置信度为**中等**；对“市场实际上不存在这些产品”的置信度为**低/不作该主张**，因为平台访问和索引覆盖均不完整。

## 7. 缺口

本批次 **18/18** 单元均缺少经原始商品页验证的 ZIP10001 普通公开 delivered price、卖家、实时库存和 US warehouse，关键交易字段缺失率 **100%**。重量/尺寸、分项运费、关税分类及分类来源也均为 `null`。美国销售税未进入比较端点：本研究未结账，故将 sales tax 记为**未观察且排除**，不是假设为 0。

用户要求保留的四种 shipment structure 均分别保留，但当前任务没有提供四种结构的定义映射，且无合格报价，因此 Structure 1–4 全部保持 `unresolved`，不自行发明定义或关税率。

## 8. 意外发现

最大问题不是“找不到相似型号”，而是**相似型号太容易造成错误 exact**：P20 Max 水箱/上下水是官方明确分开的版本；WU130X 的无电池裸机与 2.0Ah 单电套装差异实质性；GO 3S 必须同时钉住 Arctic White、64GB、Standard Bundle。[Roborock Official Store](https://mall.roborock.com/?utm_source=chatgpt.com)

## 9. 自我反驳

外部搜索引擎未索引到商品，不能证明平台没有商品；地域个性化、动态加载和 robots/access 限制都可能造成假阴性。因此本报告没有把 14 个 `NOT_OBSERVED` 转成 unavailable，也没有把二级索引候选的 USD 数字冒充 2026-10-06 对 ZIP10001 的公开成交条件。

## 10. 下一实验

下一轮最有信息增益的实验是：在**无需登录的美国区域可视浏览器**中逐一打开这 9 个型号的 Temu/AliExpress 搜索和候选 item，设置目的地 ZIP10001，仅观察不结账；逐字段记录精确变体、seller、库存、US warehouse、商品价、运费及公开优惠。若仍需登录或页面阻断，继续保留 `LOGIN_REQUIRED/BLOCKED`，不重选 SKU。

本批次计数仅为：**Temu NOT_OBSERVED=9；AliExpress BLOCKED=4、NOT_OBSERVED=5；经原页验证 offers=0；A=0、B=0、C=0。** 不代表全样本或全市场覆盖率。

```json
{
  "job_id": "W4-C-batch04",
  "parent_replicate": "W4-C",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "as_of": "2026-10-06",
  "assigned_sku_ids": ["C10-S01","C10-S02","C10-S03","C11-S01","C11-S02","C11-S03","C12-S01","C12-S02","C12-S03"],
  "categories": [
    {"category_id":"C10","status":"completed_with_access_limits"},
    {"category_id":"C11","status":"completed_with_access_limits"},
    {"category_id":"C12","status":"completed_with_access_limits"}
  ],
  "comparison_endpoint": {
    "destination_country":"US",
    "destination_zip":"10001",
    "price_basis":"ordinary_public_delivered_price_before_US_sales_tax",
    "US_sales_tax":{"included":false,"observed":false,"value":null,"note":"No checkout performed; tax is unobserved, not assumed zero."},
    "member_price":null,
    "88vip_price":null,
    "targeted_coupon":null,
    "china_national_subsidy":null
  },
  "matching_policy": {
    "A":"exact brand+model+capacity/version+region+bundle",
    "B":"same OEM with different branding only when strong OEM evidence exists",
    "C":"functional comparable",
    "cross_bucket_savings_allowed":false
  },
  "observation_summary": {
    "sku_count":9,
    "platform_sku_cells":18,
    "temu":{"NOT_OBSERVED":9,"BLOCKED":0,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0,"verified_offers":0},
    "aliexpress":{"NOT_OBSERVED":5,"BLOCKED":4,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0,"verified_offers":0},
    "match_counts":{"A":0,"B":0,"C":0},
    "critical_transaction_fields_missing_cells":18,
    "critical_transaction_fields_missing_rate":1.0,
    "scope_note":"Batch observation missingness only; not a full-market or full-sample coverage rate."
  },
  "shipment_structures": [
    {"structure_id":"1","definition":null,"status":"unresolved","quote":null,"tariff":null,"reason":"Four-structure mapping not supplied in batch prompt; no verified platform offer."},
    {"structure_id":"2","definition":null,"status":"unresolved","quote":null,"tariff":null,"reason":"Four-structure mapping not supplied in batch prompt; no verified platform offer."},
    {"structure_id":"3","definition":null,"status":"unresolved","quote":null,"tariff":null,"reason":"Four-structure mapping not supplied in batch prompt; no verified platform offer."},
    {"structure_id":"4","definition":null,"status":"unresolved","quote":null,"tariff":null,"reason":"Four-structure mapping not supplied in batch prompt; no verified platform offer."}
  ],
  "sources": [
    {"source_id":"S01","url":null,"web_ref":"turn417789view0","title":"Temu direct search URL access test - Roborock P20 Max","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S02","url":null,"web_ref":"turn417789view1","title":"Temu direct search URL access test - Insta360 GO 3S","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S03","url":null,"web_ref":"turn218596search0","title":"Pricearchive index - Roborock P20 Max AliExpress item 1005013026385525","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02","K06"]},
    {"source_id":"S04","url":null,"web_ref":"turn852527view1","title":"AliExpress original item 1005013026385525 access attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S05","url":null,"web_ref":"turn218596search2","title":"Pricearchive index - WORX WU130X AliExpress item 1005012312044183","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03","K06"]},
    {"source_id":"S06","url":null,"web_ref":"turn852527view2","title":"AliExpress original WU130X item access attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K03"]},
    {"source_id":"S07","url":null,"web_ref":"turn383977search0","title":"Pricearchive index - Insta360 GO 3S AliExpress item 1005009689106522","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K04","K06"]},
    {"source_id":"S08","url":null,"web_ref":"turn852527view3","title":"AliExpress original GO 3S item access attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K04"]},
    {"source_id":"S09","url":null,"web_ref":"turn387412search0","title":"Roborock official mall - P20 Max water-tank and plumbing variants","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S10","url":null,"web_ref":"turn387412search4","title":"DJI ROMO P Water Tank Version - DJI Store","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S11","url":null,"web_ref":"turn860631search0","title":"Sony ILCE-7CM2L setup - SEL2860 kit lens","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K09"]},
    {"source_id":"S12","url":null,"web_ref":"turn804867search0","title":"Sony Alpha 7 V ILCE-7M5/B - Body Only","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K10"]},
    {"source_id":"S13","url":null,"web_ref":"turn387412search1","title":"Insta360 GO 3S official store - color/capacity/bundle options","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K11"]},
    {"source_id":"S14","url":null,"web_ref":"turn914808reddit22","title":"Reddit r/Aliexpress - GO 3S third-party listing discussion","published_at":"2025-05-09","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K12"]},
    {"source_id":"S15","url":null,"web_ref":"turn914808reddit27","title":"Reddit r/Insta360 - AliExpress import/authenticity discussion","published_at":"2026-08-05","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K13"]}
  ],
  "claims": [
    {"claim_id":"K01","claim":"No assigned SKU produced a Temu exact/OEM/comparable original product page that could be directly verified in this research pass; direct Temu search URLs were inaccessible in the research channel.","classification":"FACT","source_ids":["S01","S02"],"confidence":"medium","counterevidence":"Search-index incompleteness or geo-personalized listings may create false negatives; therefore no VERIFIED_UNAVAILABLE claim."},
    {"claim_id":"K02","claim":"A secondary index identifies an AliExpress Roborock P20 Max model-family candidate, but the original item page was blocked and does not establish either frozen P20 Max variant.","classification":"FACT","source_ids":["S03","S04","S09"],"confidence":"high","counterevidence":"Secondary index presence is evidence against claiming model-family absence."},
    {"claim_id":"K03","claim":"A secondary index identifies a WU130X candidate described as without battery and charger; the original AliExpress page was blocked, so it cannot establish frozen WU130X.1 2.0Ah single-battery exact coverage.","classification":"FACT","source_ids":["S05","S06"],"confidence":"high","counterevidence":"The indexed model family may still have another unobserved exact bundle."},
    {"claim_id":"K04","claim":"A secondary index identifies a GO 3S model-family candidate, but its indexed title does not establish Arctic White 64GB Standard Bundle and the original AliExpress page was blocked.","classification":"FACT","source_ids":["S07","S08","S13"],"confidence":"high","counterevidence":"Another exact variant listing may exist but was not observed."},
    {"claim_id":"K05","claim":"Across 18 platform-SKU cells there were zero original-page-verified A, B, or C offers in this batch pass.","classification":"FACT","source_ids":["S01","S02","S04","S06","S08"],"confidence":"medium","counterevidence":"Platform access limitations prevent interpreting zero verified offers as zero market supply."},
    {"claim_id":"K06","claim":"Secondary AliExpress indexes are counterevidence to any assertion that P20 Max, WU130X, or GO 3S model families are definitely absent from AliExpress.","classification":"INFERENCE","source_ids":["S03","S05","S07"],"confidence":"medium","counterevidence":"Indexes may be stale and do not prove current stock, exact variant, destination eligibility, seller, or delivered price."},
    {"claim_id":"K07","claim":"Roborock officially separates P20 Max water-tank and automatic-plumbing variants.","classification":"FACT","source_ids":["S09"],"confidence":"high","counterevidence":null},
    {"claim_id":"K08","claim":"DJI officially defines a ROMO P Water Tank Version in the ROMO product family.","classification":"FACT","source_ids":["S10"],"confidence":"high","counterevidence":null},
    {"claim_id":"K09","claim":"Sony documents ILCE-7CM2L as the Alpha 7C II kit using the SEL2860 FE 28-60mm lens.","classification":"FACT","source_ids":["S11"],"confidence":"high","counterevidence":null},
    {"claim_id":"K10","claim":"Sony US lists ILCE-7M5/B Alpha 7 V with a distinct Body Only style.","classification":"FACT","source_ids":["S12"],"confidence":"high","counterevidence":null},
    {"claim_id":"K11","claim":"Insta360's official product page treats GO 3S color, capacity, and bundle as explicit variant dimensions.","classification":"FACT","source_ids":["S13"],"confidence":"high","counterevidence":null},
    {"claim_id":"K12","claim":"Community discussion reports third-party/unbranded GO 3S listings on AliExpress and recommends seller/authenticity checks; it is not proof of counterfeit status.","classification":"FACT","source_ids":["S14"],"confidence":"medium","counterevidence":"Community reports are anecdotal and seller/listing-specific."},
    {"claim_id":"K13","claim":"Community reports indicate import duty, tax, delivery region and warranty can materially affect apparent AliExpress savings.","classification":"INFERENCE","source_ids":["S15"],"confidence":"low","counterevidence":"Anecdotal experiences do not establish costs for ZIP10001 or any assigned listing."}
  ],
  "coverage": [
    {"sku_id":"C10-S01","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"Roborock P20 Max\" A2950RR water tank","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact indexed original product page surfaced; direct Temu search URL inaccessible via research channel."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"1005013026385525 (secondary-index candidate only)","match_bucket":null,"evidence":"Model-family title P20 Max only; frozen non-plumbing water-tank variant not proven; original AliExpress page blocked.","exact_variant":null,"inventory":null,"US_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"price_type":null,"access_state":"blocked_original_page","observed_at":"2026-10-06","source_ids":["S03","S04","S09"]}],"search_scope":[{"query":"site:aliexpress.com/item \"Roborock P20 Max\" A2950RR water tank","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["Original AliExpress candidate page inaccessible; secondary indexed price/seller/stock not accepted as transaction evidence."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","P20 Max water-tank and plumbing variants cannot be merged.","No savings computed."]},
    {"sku_id":"C10-S02","category_id":"C10","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"Roborock P20 Max\" A2950RR automatic plumbing","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact indexed original product page surfaced; direct Temu search inaccessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"1005013026385525 (secondary-index candidate only)","match_bucket":null,"evidence":"Generic P20 Max candidate does not prove automatic water-supply/drain variant; original page blocked.","exact_variant":null,"inventory":null,"US_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"price_type":null,"access_state":"blocked_original_page","observed_at":"2026-10-06","source_ids":["S03","S04","S09"]}],"search_scope":[{"query":"site:aliexpress.com/item \"Roborock P20 Max\" A2950RR automatic plumbing","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["Original page inaccessible; indexed model-family evidence insufficient for bucket A."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","Not merged with C10-S01.","No savings computed."]},
    {"sku_id":"C10-S03","category_id":"C10","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"DJI ROMO P\" \"Water Tank\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:aliexpress.com/item \"DJI ROMO P\" \"Water Tank\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact robot offer surfaced; no inference from accessories or snippets."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head_status_verified remains false.","DJI official regional page verifies variant definition only, not platform coverage."]},
    {"sku_id":"C11-S01","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"DZC1050-26BT\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:aliexpress.com/item \"DZC1050-26BT\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","Mains voltage and plug compatibility remain unobserved for US use."]},
    {"sku_id":"C11-S02","category_id":"C11","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"WJZ1601S\" 16V dual battery","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:aliexpress.com/item \"WJZ1601S\" 16V dual battery","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","Battery/charger region compatibility remains null."]},
    {"sku_id":"C11-S03","category_id":"C11","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"WU130X.1\" 12V 40Nm 2.0Ah","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"1005012312044183 (secondary-index candidate only)","match_bucket":null,"evidence":"Indexed title says WU130X 12V 40Nm but without battery and charger; does not establish WU130X.1 or frozen 2.0Ah single-battery bundle; original page blocked.","exact_variant":null,"inventory":null,"US_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"price_type":null,"access_state":"blocked_original_page","observed_at":"2026-10-06","source_ids":["S05","S06"]}],"search_scope":[{"query":"site:aliexpress.com/item \"WU130X.1\" 12V 40Nm 2.0Ah","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["Original candidate page inaccessible; secondary price and seller data rejected."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head_status_verified remains false.","Wrong/no-battery bundle cannot be bucket A.","OEM relationship not inferred from appearance/specification similarity."]},
    {"sku_id":"C12-S01","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"Sony A7C II\" silver \"28-60\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:aliexpress.com/item \"Sony A7C II\" silver \"28-60\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact silver ILCE-7CM2L/28-60 original offer surfaced."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","Body-only or other-color offers would not be exact."]},
    {"sku_id":"C12-S02","category_id":"C12","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"ILCE-7M5\" \"Alpha 7 V\" body only","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"aliexpress":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:aliexpress.com/item \"ILCE-7M5\" \"Alpha 7 V\" body only","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head/exact flags preserved.","Sony official US page verifies Body Only distinction but not marketplace coverage."]},
    {"sku_id":"C12-S03","category_id":"C12","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"NOT_OBSERVED","offers":[],"search_scope":[{"query":"site:temu.com \"Insta360 GO 3S\" \"Arctic White\" 64GB \"Standard Bundle\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["No exact original product page surfaced; direct Temu search URL inaccessible."]},"aliexpress":{"observation_status":"BLOCKED","offers":[{"url":null,"seller":null,"item":"1005009689106522 (secondary-index candidate only)","match_bucket":null,"evidence":"Indexed title establishes GO 3S model family only; Arctic White, 64GB and Standard Bundle are not established; original AliExpress page blocked.","exact_variant":null,"inventory":null,"US_warehouse_evidence":null,"currency":null,"price":null,"delivery":null,"price_type":null,"access_state":"blocked_original_page","observed_at":"2026-10-06","source_ids":["S07","S08","S13"]}],"search_scope":[{"query":"site:aliexpress.com/item \"Insta360 GO 3S\" \"Arctic White\" 64GB \"Standard Bundle\"","destination":"US ZIP10001","observed_at":"2026-10-06"}],"access_limitations":["Original item inaccessible; secondary indexed price not accepted as ordinary delivered price."]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head_status_verified remains false.","Generic GO 3S cannot be bucket A without color+capacity+bundle.","Community authenticity concerns are not treated as counterfeit proof."]}
  ],
  "data_gaps": [
    "Temu direct in-site search pages were inaccessible through the research channel; exact external searches yielded no verified original offers.",
    "AliExpress original pages for the three indexed model families evaluated against four frozen SKUs were inaccessible.",
    "No verified seller identity for any assigned SKU.",
    "No verified current inventory for any assigned SKU.",
    "No verified US-warehouse evidence for any assigned SKU.",
    "No ordinary public delivered price to ZIP10001 for any assigned SKU.",
    "No verified shipping component price, package weight or package dimensions.",
    "No tariff classification, tariff-source determination or tariff-rate assumption was manufactured.",
    "US sales tax was not observed because no checkout was performed; it is excluded from the comparison endpoint rather than set to zero.",
    "Definitions of the required four shipment structures were not supplied in this batch prompt, so all four were preserved separately as unresolved.",
    "NOT_OBSERVED must not be interpreted as out-of-stock or unavailable; BLOCKED must not be interpreted as available.",
    "All source attestations remain subject to coordinator review."
  ]
}
```