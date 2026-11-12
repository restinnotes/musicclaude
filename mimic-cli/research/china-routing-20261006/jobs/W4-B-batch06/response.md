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