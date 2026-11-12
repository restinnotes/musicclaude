ONE independent W4-A replicate, mechanically bundled from six disjoint category batches. No peer results were supplied. All frozen SKU IDs are retained; unobserved and blocked rows remain in the denominator. Original reports are untruncated.

=== UNEDITED W4-A-batch01; SHA256 73cdaf481edb548424659d8dac3e49310264687ecbd91c09e054d13e6b7bcd54 ===
## 一、直接回答

本批次 9 个冻结 SKU 均已按 **Temu / AliExpress 分平台尝试检索**，未替换任何 SKU，也未把未核验 head 升级。结果是：**18 个 SKU×平台单元全部因平台访问限制记为 `BLOCKED`；0 个可接受 A-exact、B-OEM 或 C-comparable offer。** 这不表示商品不存在，更不构成 `VERIFIED_UNAVAILABLE`。本批次合格 offer 缺失率为 **18/18=100%**，仅代表 W4-A-batch01 的可核验性。

## 二、证据表

| SKU | 冻结 head/exact | Temu | AliExpress | 本批次结论 |
|---|---|---|---|---|
| C01-S01 | true/true | BLOCKED | BLOCKED | iPhone 17 256GB 白色大陆双卡未核到美国区原页 |
| C01-S02 | true/true | BLOCKED | BLOCKED | iPhone 17 Pro 256GB 银色大陆版未核到 |
| C01-S03 | false/true | BLOCKED | BLOCKED | Ace 6T 12+256 闪速黑未核到 |
| C02-S01 | true/true | BLOCKED | BLOCKED | 天选7 Pro 指定 251HX/5060/1TB/青未核到 |
| C02-S02 | true/true | BLOCKED | BLOCKED | 小新16SE 指定配置未核到 |
| C02-S03 | false/true | BLOCKED | BLOCKED | 无界14 2026 226V/16/1T/灰未核到 |
| C03-S01 | true/true | BLOCKED | BLOCKED | iPad A16 128GB WLAN 银色未核到美国 ZIP10001 offer |
| C03-S02 | true/true | BLOCKED | BLOCKED | iPad A16 256GB WLAN 银色未核到 |
| C03-S03 | false/true | BLOCKED | BLOCKED | Y700 五代 12+256 黑存在旁证，但美国区原始商品页未核验 |

## 三、一级来源

Temu 首页本次可请求，但打开后无可读商品内容；直接关键词搜索 URL 对工具不可访问，分类页打开后同样表现为动态页面壳，因此不能从索引摘要提取价格、seller、库存或仓库。[Temu](https://www.temu.com/) AliExpress 美国站首页直接返回 **403 Forbidden**，各精确搜索 URL 也不可访问，因此九个 SKU 均只能记 `BLOCKED`，不能记 `NOT_OBSERVED` 或 `VERIFIED_UNAVAILABLE`。([Invalid URL]())

## 四、论坛证据

Y700 五代有可完整打开的 Reddit 讨论：用户讨论 AliExpress 上的 Gen5，并贴出 AliExpress 链接；另有用户称从 “lenovo online store” 买过 16GB/512GB。另一帖有人称从 AliExpress 买到 Gen5 16/512。它们只能证明**AliExpress 上曾有 Y700 Gen5 市场活动**，不能证明冻结的 **12GB+256GB / 碳晶黑 / ZIP10001** 当前可售。[Reddit](https://www.reddit.com/r/androidtablets/comments/1sy4bfj/y700_gen_5_on_aliexpress/)

## 五、反证

不能把“平台打不开”解释成“平台没有”。尤其 Y700：2026-10-05 的二级来源明确称 AliExpress Choice Day 有 Gen5 销售活动，并强调中国版、优惠码及价格/库存会变动；但它没有核验本研究要求的卖家、精确容量颜色、美国仓、ZIP10001 普通 delivered price，因此拒绝写入 offer。[Tamachan Lab](https://tamachan-lab.pages.dev/articles/aliexpress-legion-y700-gen4-gen5-sale-2026/) Temu 搜索索引还曾浮出瑞士站 A16 iPad 商品候选，但打开原页仅剩页面壳且地区错误，同样不计覆盖。[Temu](https://www.temu.com/ch-fr/-ipad-11-pouces-2025--a16-wi-fi-6-%C3%A9cran--10-9-tablette--18-g-606443138810199.html?utm_source=chatgpt.com)

## 六、置信度

对“**本环境无法完成两平台原页核验**”置信度高；对“这些 SKU 实际是否在平台销售”置信度低，因此全部保持 unresolved。A/B/C 三 bucket 本批次均为 0 个合格匹配，不做节省比较。

## 七、缺口

seller/item、精确版本选择、库存、US warehouse、USD/CNY 普通公开价、ZIP10001 运费、delivery、会员/定向券状态、重量尺寸、HTS/关税依据均未观察，全部保持 null。四种 shipment structure 均分别保留为 unresolved；因冻结子集未提供四种结构的定义，不擅自命名或合并。比较终点固定为 **ZIP10001 delivered、美国销售税不计入**；未进入 checkout，故税额也为 null。

## 八、意外发现

Y700 Gen5 在 2026-10-05 的近期二级材料仍显示 AliExpress 活动，但报价是优惠码场景且面向日本语境；这恰好说明“能找到海外价格”不能替代本研究要求的美国区普通公开价。[Tamachan Lab](https://tamachan-lab.pages.dev/articles/aliexpress-legion-y700-gen4-gen5-sale-2026/)

## 九、自我反驳

最强反驳是：搜索引擎缓存与社区链接说明至少部分商品可能真实存在。如果把这些线索当 `EXACT_OBSERVED`，会人为提高覆盖率；但用户规则明确禁止 snippet、页面壳和第三方转述证明卖家/成交价/库存，因此本报告选择保守的 `BLOCKED`。

## 十、下一实验

下一步只需在**无登录态、美国区域、目的地 ZIP10001** 的可交互浏览器中，对这 18 个查询各复查一次：搜索结果页→精确商品页→variant→seller→库存/warehouse→普通 delivered price；不下单、不登录、不联系商家。若仍受阻，就维持 `BLOCKED`，不继续重试。

以下 JSON 中 `url` 保持 `null`，用 `citation_ref(s)` 绑定本次可点击网页证据；这样不把无法稳定打开的页面地址伪装成已核验商品 URL。

```json
{"job_id":"W4-A-batch01","parent_replicate":"W4-A","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185","assigned_sku_ids":["C01-S01","C01-S02","C01-S03","C02-S01","C02-S02","C02-S03","C03-S01","C03-S02","C03-S03"],"categories":[{"category_id":"C01","status":"6/6 platform-SKU checks BLOCKED; 0 qualified offers"},{"category_id":"C02","status":"6/6 platform-SKU checks BLOCKED; 0 qualified offers"},{"category_id":"C03","status":"6/6 platform-SKU checks BLOCKED; 0 qualified offers"}],"batch_counts":{"assigned_skus":9,"platform_sku_cells":18,"status_counts":{"BLOCKED":18,"EXACT_OBSERVED":0,"OEM_OBSERVED":0,"COMPARABLE_ONLY":0,"RESELLER_ONLY":0,"NOT_OBSERVED":0,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0},"qualified_offer_missing_rate":1.0},"comparison_scope":{"destination":"US ZIP 10001","endpoint":"delivered_to_ZIP10001_before_US_sales_tax","us_sales_tax_treatment":"excluded; checkout not observed","shipment_structures":[{"structure_index":1,"definition":null,"status":"unresolved","item_price":null,"shipping":null,"tariff_classification":null,"tariff_source":null,"tariff_amount":null},{"structure_index":2,"definition":null,"status":"unresolved","item_price":null,"shipping":null,"tariff_classification":null,"tariff_source":null,"tariff_amount":null},{"structure_index":3,"definition":null,"status":"unresolved","item_price":null,"shipping":null,"tariff_classification":null,"tariff_source":null,"tariff_amount":null},{"structure_index":4,"definition":null,"status":"unresolved","item_price":null,"shipping":null,"tariff_classification":null,"tariff_source":null,"tariff_amount":null}],"note":"Four shipment structures preserved separately; definitions were not supplied in this batch prompt and were not invented."},"sources":[{"source_id":"S01","url":null,"citation_ref":"turn245734view2","title":"Temu home page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K01"]},{"source_id":"S02","url":null,"citation_refs":["turn523736view0","turn523736view1","turn523736view2","turn523736view3","turn523736view4","turn523736view5"],"title":"Temu direct exact-query attempts for C01/C02","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S03","url":null,"citation_refs":["turn646733view0","turn646733view1","turn646733view2"],"title":"Temu direct exact-query attempts for C03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S04","url":null,"citation_ref":"turn989333view0","title":"Temu US tablets/laptops category","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K01"]},{"source_id":"S05","url":null,"citation_ref":"turn461178view0","title":"Temu Switzerland iPad A16 candidate page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K04"]},{"source_id":"S06","url":null,"citation_ref":"turn245734view0","title":"AliExpress US home page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"S07","url":null,"citation_refs":["turn646733view3","turn646733view4","turn646733view5"],"title":"AliExpress US exact-query attempts for C01","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"S08","url":null,"citation_refs":["turn670855view0","turn670855view1","turn670855view2","turn670855view3","turn670855view4","turn670855view5"],"title":"AliExpress US exact-query attempts for C02/C03","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},{"source_id":"S09","url":null,"citation_ref":"turn751917view0","title":"AliExpress Choice Day Y700 Gen4/Gen5 secondary report","published_at":"2026-10-05","retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03","K05"]},{"source_id":"S10","url":null,"citation_ref":"turn535114view0","title":"Reddit: Y700 Gen 5 on AliExpress","published_at":"2026-04-28","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S11","url":null,"citation_ref":"turn535114view1","title":"Reddit: Y700 Gen5 purchase discussion","published_at":"2026-07-13","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K03"]}],"claims":[{"claim_id":"K01","claim":"Temu exact-query pages for all nine assigned SKUs were inaccessible in this environment; accessible Temu landing/category pages did not yield readable item-level original-page evidence.","classification":"FACT","source_ids":["S01","S02","S03","S04"],"confidence":"high","counterevidence":"Search indexing surfaced cached/category content, but snippets and page shells are excluded by protocol."},{"claim_id":"K02","claim":"AliExpress US first-party access was blocked/403 and the nine assigned direct query pages could not be inspected.","classification":"FACT","source_ids":["S06","S07","S08"],"confidence":"high","counterevidence":"Community and secondary sources show AliExpress marketplace activity, so this does not prove unavailability."},{"claim_id":"K03","claim":"Third-party evidence supports that Lenovo Y700 Gen5 has appeared on AliExpress, but does not verify the frozen 12GB+256GB carbon-black variant delivered to ZIP10001 on 2026-10-06.","classification":"FACT","source_ids":["S09","S10","S11"],"confidence":"medium","counterevidence":"No readable first-party AliExpress item/checkout page was available."},{"claim_id":"K04","claim":"A Temu-indexed iPad A16 candidate outside the US region cannot establish US coverage and its opened original page was only a shell.","classification":"FACT","source_ids":["S05"],"confidence":"high","counterevidence":"None sufficient for ZIP10001."},{"claim_id":"K05","claim":"No A-exact, B-OEM or C-comparable offer can be accepted for any of the 18 platform-SKU cells in this batch.","classification":"INFERENCE","source_ids":["S01","S02","S03","S04","S06","S07","S08"],"confidence":"high","counterevidence":"This is an evidence-availability conclusion, not a claim of marketplace absence."}],"coverage":[{"sku_id":"C01-S01","category_id":"C01","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17; 256GB; white; China mainland dual-SIM; Temu exact query"],"access_limitations":["direct search URL inaccessible","no readable item-level original page","ZIP10001 delivery/warehouse/price not observable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17; 256GB; white; China mainland dual-SIM; AliExpress US exact query"],"access_limitations":["US platform access blocked/403","direct search inaccessible","seller/item/stock/price/warehouse not observable"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Frozen head and exact-variant flags preserved.","No absence inference from blocked access."]},{"sku_id":"C01-S02","category_id":"C01","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 Pro; 256GB; silver; China mainland dual-SIM; Temu exact query"],"access_limitations":["direct search URL inaccessible","item-level verification unavailable"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPhone 17 Pro; 256GB; silver; China mainland dual-SIM; AliExpress US exact query"],"access_limitations":["US platform blocked","item-level verification unavailable"]},"china_head_us_middle_tail_status":"unresolved","caveats":["US eSIM/unlocked hardware cannot substitute for the frozen mainland dual-SIM version."]},{"sku_id":"C01-S03","category_id":"C01","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["OnePlus Ace 6T; 12GB+256GB; 闪速黑; Temu exact query"],"access_limitations":["direct search URL inaccessible","no seller/item page verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["OnePlus Ace 6T; 12GB+256GB; black; AliExpress US exact query"],"access_limitations":["US platform blocked","third-party snippets rejected","stock/region/ROM/price not verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["OnePlus 15R branding/ROM differences were not treated as A-exact or B-OEM without first-party evidence."]},{"sku_id":"C02-S01","category_id":"C02","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS Tianxuan 7 Pro; Core Ultra 7 251HX; 16GB; 1TB; RTX5060; 2.5K 300Hz; 青; Temu exact query"],"access_limitations":["direct search inaccessible","no exact configuration page verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["same exact Tianxuan 7 Pro configuration; AliExpress US exact query"],"access_limitations":["direct search inaccessible","US delivery/warehouse unavailable"]},"china_head_us_middle_tail_status":"unresolved","caveats":["TUF/Tianxuan regional branding was not assumed to be exact."]},{"sku_id":"C02-S02","category_id":"C02","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo Xiaoxin 16SE; Ryzen 7; 16GB; 512GB; expandable SSD slot; Temu exact query"],"access_limitations":["direct search inaccessible","no exact CPU submodel/region page verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["same frozen Xiaoxin 16SE configuration; AliExpress US exact query"],"access_limitations":["US platform blocked","no item page verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Other Xiaoxin/IdeaPad regional models were not substituted."]},{"sku_id":"C02-S03","category_id":"C02","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["MECHREVO Wujie 14 2026; Core Ultra 5 226V; 16GB; 1TB; 2.8K; grey; Temu exact query"],"access_limitations":["direct search inaccessible","no exact original item page"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["same Wujie 14 2026 exact configuration; AliExpress US exact query"],"access_limitations":["US platform blocked","no exact original item page"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Wujie 14S/14X/other CPU versions were not substituted."]},{"sku_id":"C03-S01","category_id":"C03","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPad 11-inch A16 2025; 128GB; WLAN; silver; Temu exact query"],"access_limitations":["US exact search inaccessible","a non-US indexed candidate was region-mismatched and opened only as page shell","price/seller/stock not accepted"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPad A16; 128GB; Wi-Fi; silver; AliExpress US exact query"],"access_limitations":["US platform blocked","no first-party offer verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Pink or cellular variants cannot substitute for silver Wi-Fi 128GB."]},{"sku_id":"C03-S02","category_id":"C03","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPad 11-inch A16 2025; 256GB; WLAN; silver; Temu exact query"],"access_limitations":["direct search inaccessible","no US item page verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["iPad A16; 256GB; Wi-Fi; silver; AliExpress US exact query"],"access_limitations":["US platform blocked","no first-party offer verified"]},"china_head_us_middle_tail_status":"unresolved","caveats":["128GB and 256GB remain separate frozen SKUs."]},{"sku_id":"C03-S03","category_id":"C03","pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo Legion Y700 5th; 8.8-inch; 12GB+256GB; Wi-Fi; carbon black; Temu exact query"],"access_limitations":["direct search inaccessible","no item-level offer verified"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Lenovo Legion Y700 Gen5/5th; 12GB+256GB; carbon black; AliExpress US exact query"],"access_limitations":["first-party AliExpress page blocked","community/secondary evidence cannot establish current exact US offer","seller/stock/US warehouse/USD delivered price null"]},"china_head_us_middle_tail_status":"unresolved","caveats":["Community evidence supports Gen5 marketplace presence only; it does not close exact variant/region/warehouse/price requirements.","Coupon/Japan-market price evidence excluded from ordinary US delivered price."]}],"data_gaps":["18/18 platform-SKU cells lack readable current first-party item pages.","No verified seller/item IDs, stock, US warehouse, USD/CNY ordinary delivered prices, shipping components, weight/dimensions, tariff classification/source or checkout tax.","No A/B/C offer statistics can be computed without fabricating evidence.","Four shipment-structure definitions were not supplied in the frozen subset; four unresolved slots were preserved rather than renamed or merged."]}
```
=== UNEDITED W4-A-batch02; SHA256 75db6c61c2918d51c1dd13272dee2ba94595cc0afb676f378298d764d554ba6e ===
## 1. 直接回答

本批仅执行 C04/C05/C06 的 9 个冻结 SKU，未替换样本；冻结前 `head_status_verified` / `exact_variant_verified` 原样保留。共完成 **9 SKU × 2 平台 = 18 次**明确站内搜索/关键页检查；Temu 9/9、AliExpress 9/9 均因平台页面不可访问而判为 **BLOCKED**，不是 NOT_OBSERVED、更不是 VERIFIED_UNAVAILABLE。故本批直接观察到的 A exact、B same-OEM、C comparable 均为 **0**；这只是本批观测结果，不能解读为“市场没有”。seller/item、库存、US warehouse、币种、普通公开价、运费、ZIP10001 delivered price、重量尺寸、HTS/关税字段缺失率均为 **100%**。不计算节省。

比较端点预设为：**公开未登录商品价 + ZIP10001 必付运费，US sales tax 之前**；会员价、88VIP、定向券、首单、国补、账号价全部排除。四个履约结构——Temu跨境、Temu美仓、AliExpress跨境、AliExpress美仓——本批均 unresolved。

## 2. 证据表

| SKU | 冻结 flags | Temu | AliExpress |
|---|---|---|---|
| C04-S01 | head=true; exact=true | **BLOCKED B01** ([]()) | **BLOCKED B02** ([Invalid URL]()) |
| C04-S02 | true; true | **BLOCKED B03** ([Invalid URL]()) | **BLOCKED B04** ([Invalid URL]()) |
| C04-S03 | false; true | **BLOCKED B05** ([Invalid URL]()) | **BLOCKED B06** ([Invalid URL]()) |
| C05-S01 | true; true | **BLOCKED B07** ([Invalid URL]()) | **BLOCKED B08** ([Invalid URL]()) |
| C05-S02 | true; true | **BLOCKED B09** ([Invalid URL]()) | **BLOCKED B10**；另有候选原始 item 页仍打不开 ([Invalid URL]()) |
| C05-S03 | false; true | **BLOCKED B11** ([Invalid URL]()) | **BLOCKED B12** ([Invalid URL]()) |
| C06-S01 | true; true | **BLOCKED B13** ([Invalid URL]()) | **BLOCKED B14** ([Invalid URL]()) |
| C06-S02 | true; true | **BLOCKED B15** ([Invalid URL]()) | **BLOCKED B16** ([Invalid URL]()) |
| C06-S03 | false; true | **BLOCKED B17** ([Invalid URL]()) | **BLOCKED B18**；候选 item 页仍打不开 ([Invalid URL]()) |

## 3. 一级来源

身份核对没有替代平台 coverage。GMKtec 官方页实际打开，确认 EVO-X2 Ryzen AI Max+ 395 存在 **128GB + 2TB** 选择；但不能据此证明 Temu/AliExpress 有 exact。[GMKtec](https://www.gmktec.com/en/products/amd-ryzen%E2%84%A2-ai-max-395-evo-x2-ai-mini-pc) Beelink 官方当前页确认 SER8 8745HS 硬件家族，但页面展示配置机，并未替本冻结的“深空灰准系统”建立两平台 exact。[Beelink](https://www.bee-link.com/products/beelink-ser8-8745hs) Samsung 官方确认 990 EVO Plus 2TB、MZ-V9S2T0B/AM、标称读取 7,250MB/s。[Samsung nz](https://www.samsung.com/us/memory-storage/nvme-ssd/990-evo-plus-gen4-nvme-ssd-2tb-sku-mz-v9s2t0b-am/?msockid=03275822e3046d4623e14ecce2b06c98) Xiaomi 中国官网确认 BE6500 型号存在。[Xiaomi India](https://www.mi.com/xiaomi-routers/be-6500)

三款 EDIFIER 的中国官方页分别确认 Lolli Pro SE 云岩白、LolliClip SE 云霜金、Comfo Clip Q 奶霜白，因此冻结版本定义保持不变；但任何海外 listing 仍须单独核地域、硬件、捆绑。[Edifier Official](https://www.edifier.com/cn/product/product-864.html)

## 4. 论坛证据

Reddit 有用户专门质疑 AliExpress 上 SER8 “barebone”的真实性，评论还指出非官方店铺存在保修/真实性风险；这只能支持“不能轻率判 exact”，不能证明某 listing 假货或不存在。[Reddit](https://www.reddit.com/r/MiniPCs/comments/1obzocf) 2026-08-18 的什么值得买全文则记录了 LolliClip SE 两周使用和云霜金等信息，属于近期消费者使用佐证，不用于 Temu/AliExpress 价格、库存或覆盖判断。[SMZDM Post](https://post.smzdm.com/p/a26z6722/)

## 5. 反证

不能把 BLOCKED 推成“没有海外货”。二级索引确实出现了 Xiaomi BE6500 的 AliExpress 候选，说明“搜索环境没读到平台正文”与“商品不存在”是两件事；但直接打开原始 AliExpress item 页仍失败，所以不升级为 EXACT_OBSERVED。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005012374999592?utm_source=chatgpt.com) 同理，EDIFIER 出现 “Comfo Q” 候选，但名称又与冻结的 “Comfo Clip Q” 不完全一致，且原页被阻断，连 B bucket 都不能据此成立。[Pricearchive.org](https://www.pricearchive.org/aliexpress.com/item/1005012085072129?utm_source=chatgpt.com)

## 6. 置信度

对“**本研究环境下 18/18 为 BLOCKED**”置信度高；对平台实际是否有货、卖家数、仓库、价格和 A/B/C 实际覆盖，置信度低/不可判定。`china_head_us_middle_tail_status` 因此全部为 `unresolved`。本批没有把任何冻结前非-head 样本升级成 verified-head。

## 7. 缺口

ZIP10001 无法在两平台实际应用，所以普通公开 delivered price、库存、seller/item、US warehouse、跨境/美仓履约结构均 null；重量尺寸、运输报价、HTS 分类和关税率也不推测。ASUS 破晓与 KINGBANK 银爵在本时限内没有新增可用一级来源，但这不改变冻结前 exact 验证状态。

## 8. 意外发现

AliExpress 的公开二级索引对 C05-S02、C06-S03 至少给出了候选线索，但原始页面阻断使其不能进入 offers。尤其 Comfo Q / Comfo Clip Q 的命名差异说明“图片像、规格接近”不足以证明 same OEM 或 exact；本批没有利用二级索引展示的价格数字。

## 9. 自我反驳

最可能的反驳是：平台搜索页被研究环境阻断，不代表普通浏览器也被阻断，因此 18/18 BLOCKED 可能严重低估真实 coverage。成立。因此本报告只声称“本批无法直接核验”，绝不声称 Temu/AliExpress 对这些型号的市场覆盖率为零。反过来，二级索引也不能证明当前库存、普通价、US warehouse 或 ZIP10001 可交付。

## 10. 下一实验

下一轮只需用**未登录、美国地区、ZIP10001 的公开可视浏览器**各 SKU/平台再做一次：站内精确搜索→打开首个合理候选→读取型号/容量/颜色/硬件版本/捆绑、seller/item ID、ship-from、库存、普通公开价、必付运费和配送日期；登录墙即 LOGIN_REQUIRED，反爬即 BLOCKED。仍不下单、不联系商家、不使用账号优惠。

下列 JSON 中 `source.url` 保留 `null`，对应 B/P/C/X source_id 已由正文可点击来源引用定位；这样不把访问失败跳转或二级索引伪装成已核验原始商品 URL。`offers` 为空，因此也没有制造任何卖家/item URL。

```json
{
"job_id":"W4-A-batch02",
"parent_replicate":"W4-A",
"web_research_available":true,
"pre_freeze_compliance":true,
"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
"assigned_sku_ids":["C04-S01","C04-S02","C04-S03","C05-S01","C05-S02","C05-S03","C06-S01","C06-S02","C06-S03"],
"categories":[{"category_id":"C04","status":"PLATFORM_ACCESS_BLOCKED; no Temu/AliExpress offer verified"},{"category_id":"C05","status":"PLATFORM_ACCESS_BLOCKED; no Temu/AliExpress offer verified"},{"category_id":"C06","status":"PLATFORM_ACCESS_BLOCKED; no Temu/AliExpress offer verified"}],
"pricing_endpoint":{"destination":"US ZIP10001","delivered_price":"public item price + mandatory shipping, pre-US-sales-tax","sales_tax":"excluded; not estimated","excluded_price_types":["member/88VIP","targeted coupon","first-order credit","government subsidy","account-specific"],"savings_calculated":false},
"shipment_structures":[{"id":"TEMU_CROSS_BORDER","status":"unresolved_blocked"},{"id":"TEMU_US_WAREHOUSE","status":"unresolved_blocked"},{"id":"ALIEXPRESS_CROSS_BORDER","status":"unresolved_blocked"},{"id":"ALIEXPRESS_US_WAREHOUSE","status":"unresolved_blocked"}],
"observations":{"platform_sku_checks":18,"blocked":18,"exact_observed":0,"oem_observed":0,"comparable_only":0,"reseller_only":0,"not_observed":0,"login_required":0,"verified_unavailable":0,"offers_directly_observed":0,"missing_rate":{"seller_item_stock_warehouse":1.0,"currency_price_shipping":1.0,"weight_dimensions":1.0,"hts_tariff":1.0},"scope":"this batch only"},
"sources":[
{"source_id":"B01","url":null,"title":"Temu search C04-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B02","url":null,"title":"AliExpress search C04-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B03","url":null,"title":"Temu search C04-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B04","url":null,"title":"AliExpress search C04-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B05","url":null,"title":"Temu search C04-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B06","url":null,"title":"AliExpress search C04-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B07","url":null,"title":"Temu search C05-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B08","url":null,"title":"AliExpress search C05-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B09","url":null,"title":"Temu search C05-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B10","url":null,"title":"AliExpress search C05-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B11","url":null,"title":"Temu search C05-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B12","url":null,"title":"AliExpress search C05-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B13","url":null,"title":"Temu search C06-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B14","url":null,"title":"AliExpress search C06-S01","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B15","url":null,"title":"Temu search C06-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B16","url":null,"title":"AliExpress search C06-S02","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B17","url":null,"title":"Temu search C06-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"B18","url":null,"title":"AliExpress search C06-S03","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K01","K08"]},
{"source_id":"P01","url":null,"title":"GMKtec EVO-X2 official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
{"source_id":"P02","url":null,"title":"Beelink SER8 8745HS official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},
{"source_id":"P03","url":null,"title":"Samsung 990 EVO Plus 2TB official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},
{"source_id":"P04","url":null,"title":"Xiaomi BE6500 official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
{"source_id":"P05","url":null,"title":"EDIFIER Lolli Pro SE official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
{"source_id":"P06","url":null,"title":"EDIFIER LolliClip SE official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
{"source_id":"P07","url":null,"title":"EDIFIER Comfo Clip Q official","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
{"source_id":"C01","url":null,"title":"SMZDM LolliClip SE two-week use report","published_at":"2026-08-18","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K07"]},
{"source_id":"C02","url":null,"title":"Reddit barebone SER8 on AliExpress discussion","published_at":"2025-10-21","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K03","K07"]},
{"source_id":"X01","url":null,"title":"AliExpress BE6500 secondary index","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K09"]},
{"source_id":"X02","url":null,"title":"AliExpress Comfo Q secondary index","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K09"]},
{"source_id":"X03","url":null,"title":"AliExpress BE6500 original item attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K09"]},
{"source_id":"X04","url":null,"title":"AliExpress Comfo Q original item attempt","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K09"]}
],
"claims":[
{"claim_id":"K01","claim":"本批9 SKU×2平台共18次站内检查均BLOCKED。","classification":"FACT","source_ids":["B01","B02","B03","B04","B05","B06","B07","B08","B09","B10","B11","B12","B13","B14","B15","B16","B17","B18"],"confidence":"high","counterevidence":"不代表平台实际无货或无listing。"},
{"claim_id":"K02","claim":"GMKtec官方页存在EVO-X2 Ryzen AI Max+ 395的128GB+2TB选项。","classification":"FACT","source_ids":["P01"],"confidence":"high","counterevidence":"不能替代Temu/AliExpress coverage。"},
{"claim_id":"K03","claim":"Beelink官方可核SER8 8745HS家族，但不能据此证明冻结barebone在两平台为exact；论坛亦对Ali barebone真实性提出质疑。","classification":"INFERENCE","source_ids":["P02","C02"],"confidence":"medium","counterevidence":"合法barebone listing仍可能存在，原始平台页未能读取。"},
{"claim_id":"K04","claim":"Samsung官方确认990 EVO Plus 2TB/MZ-V9S2T0B/AM与7250MB/s读取规格。","classification":"FACT","source_ids":["P03"],"confidence":"high","counterevidence":"仅作身份核对。"},
{"claim_id":"K05","claim":"Xiaomi中国官网确认BE6500型号；未推断美国硬件/固件等同。","classification":"FACT","source_ids":["P04"],"confidence":"high","counterevidence":"跨地区版本仍待listing正文核验。"},
{"claim_id":"K06","claim":"EDIFIER中国官网确认Lolli Pro SE云岩白、LolliClip SE云霜金、Comfo Clip Q奶霜白。","classification":"FACT","source_ids":["P05","P06","P07"],"confidence":"high","counterevidence":"平台地区/捆绑仍待原页。"},
{"claim_id":"K07","claim":"论坛材料仅作身份风险/近期使用补充，不作平台成交价、库存或覆盖证明。","classification":"FACT","source_ids":["C01","C02"],"confidence":"medium","counterevidence":"社区为个案。"},
{"claim_id":"K08","claim":"因无平台listing正文可读，本批A/B/C observed均为0；这是观测结果，不是市场不存在断言。","classification":"FACT","source_ids":["B01","B02","B03","B04","B05","B06","B07","B08","B09","B10","B11","B12","B13","B14","B15","B16","B17","B18"],"confidence":"high","counterevidence":"二级索引存在少量候选。"},
{"claim_id":"K09","claim":"AliExpress二级索引出现BE6500和Comfo Q候选，但原始item页仍BLOCKED，因此不改变BLOCKED状态。","classification":"FACT","source_ids":["X01","X02","X03","X04"],"confidence":"high","counterevidence":"后续公开可视浏览器可重新核验。"}
],
"data_gaps":["18/18平台-SKU检查均在站内搜索页访问受阻；未读到平台商品正文。","ZIP10001未能站内应用，seller/item/库存/仓库/币种/公开价/运费/普通送达价/重量尺寸/HTS/关税率均未观察。","AliExpress二级索引出现Xiaomi BE6500与EDIFIER Comfo Q候选，但原始AliExpress item页BLOCKED；不计observed offer。","GMKtec EVO-X2、Beelink SER8 8745HS、Samsung 990 EVO Plus 2TB、Xiaomi BE6500及三款EDIFIER有本轮一级来源核对；ASUS/KINGBANK未在时限内新增一级来源。","四种平台×履约地结构均unresolved；未计算landed cost或savings。"],
"coverage":[
{"sku_id":"C04-S01","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 破晓迷你主机 i5-13500H 16GB 512GB","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B01"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["ASUS 破晓迷你主机 i5-13500H 16GB 512GB","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B02"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C04-S02","category_id":"C04","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["GMKtec EVO-X2 Ryzen AI Max+ 395 128GB 2TB","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B03"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["GMKtec EVO-X2 Ryzen AI Max+ 395 128GB 2TB","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B04"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C04-S03","category_id":"C04","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Beelink SER8 8745HS Space Gray barebone","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B05"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Beelink SER8 8745HS Space Gray barebone","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B06"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing","Beelink官方可核8745HS家族，但未据此把Ali/Temu barebone视为exact"]},
{"sku_id":"C05-S01","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Samsung 990 EVO Plus 2TB MZ-V9S2T0 7250MB/s","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B07"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Samsung 990 EVO Plus 2TB MZ-V9S2T0 7250MB/s","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B08"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C05-S02","category_id":"C05","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["Xiaomi BE6500 Wi-Fi 7 6500 2.5G Qualcomm quad-core","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B09"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["Xiaomi BE6500 Wi-Fi 7 6500 2.5G Qualcomm quad-core","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用","二级索引出现BE6500候选，但AliExpress原始item页仍BLOCKED；不计offer"],"search_source_ids":["B10"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing","不使用二级索引的价格/卖家/库存"]},
{"sku_id":"C05-S03","category_id":"C05","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["KINGBANK Silver DDR5-6000 32GB 16GBx2 C36","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B11"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["KINGBANK Silver DDR5-6000 32GB 16GBx2 C36","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B12"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C06-S01","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Lolli Pro SE Cloud Rock White ANC","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B13"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Lolli Pro SE Cloud Rock White ANC","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B14"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C06-S02","category_id":"C06","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER LolliClip SE Yunshuang Gold","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B15"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER LolliClip SE Yunshuang Gold","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B16"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]},
{"sku_id":"C06-S03","category_id":"C06","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Comfo Clip Q Cream White","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用"],"search_source_ids":["B17"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["EDIFIER Comfo Clip Q Cream White","US ZIP10001; public/logged-out"],"access_limitations":["站内搜索页不可访问；未读到商品正文、规格选择、seller、库存、仓库、运费；ZIP10001未能站内应用","二级索引出现'Comfo Q'候选，原始item页BLOCKED且名称与Comfo Clip Q不完全一致；不计B"],"search_source_ids":["B18"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冻结前head/exact标志原样保留","BLOCKED仅表示访问受阻，不等同缺货/无listing"]}
]
}
```
=== UNEDITED W4-A-batch03; SHA256 8f5815a726d3a4975045c3cb676acdf893cef1870ca055cd4ee581fc1f4bc068 ===
## 1. 直接回答

本批次网页研究**可执行**，且仅研究冻结的 C07/C08/C09 共 9 个 SKU，没有替换或删除 SKU。但 Temu 与 AliExpress 的 18 个“平台×SKU”目标搜索页在当前研究通道均无法实际打开核验：Temu 首页只能取得页面壳，AliExpress 美国站首页返回访问阻断；各 SKU 的目标搜索 URL 同样不可读。因此本批次记录为 **18/18 `BLOCKED`，0 个 A-exact、0 个 B-OEM、0 个 C-comparable、0 个可核验普通成交/配送价**。平台单元缺失率为 **100%（18/18）**；这**不等于缺货，也不等于 `VERIFIED_UNAVAILABLE`**。[Temu](https://www.temu.com/)

比较终点固定为美国 ZIP10001 的普通公开 delivered price；美国 sales tax 原则上不计，除非平台明确包含。此次没有任何合格报价，所以不计算节省、关税、四种运输结构总成本或跨 bucket 比较。

## 2. 证据表

| SKU | 冻结 head / exact | Temu | AliExpress | 本批次结果 |
|---|---|---|---|---|
| C07-S01 G304 黑色 | true / true | BLOCKED | BLOCKED | 无 offer，不能用 G305/相似鼠标顶替 A-exact。([Invalid URL]()) |
| C07-S02 GPW5 雪豹 | false / true | BLOCKED | BLOCKED | 未验证头部状态原样保留。([Invalid URL]()) |
| C07-S03 ATK RS6+ 白武士 | false / true | BLOCKED | BLOCKED | 无目标平台可读商品页。([Invalid URL]()) |
| C08-S01 Band 11 NFC 悦动白 | true / true | BLOCKED | BLOCKED | NFC 中国大陆地域约束不能忽略。([Invalid URL]()) |
| C08-S02 Band 11 Pro NFC 羽砂黑 | true / true | BLOCKED | BLOCKED | 同上。([Invalid URL]()) |
| C08-S03 Watch S5 41mm 海盐蓝 | false / true | BLOCKED | BLOCKED | 未观察到能闭合颜色+OS 的平台页。([Invalid URL]()) |
| C09-S01 小米摄像机4 8MP 4K | true / true | BLOCKED | BLOCKED | 无平台原页；另有小米动态页映射异常。([Invalid URL]()) |
| C09-S02 门锁4 Pro 双摄版 | true / true | BLOCKED | BLOCKED | 无平台原页。([Invalid URL]()) |
| C09-S03 Aqara S1E CJPKG01LM | false / true | BLOCKED | BLOCKED | 美国区兼容性存在直接反证。([Invalid URL]()) |

## 3. 一级来源

厂商原页只用于建立**匹配护栏**，不用于替代 Temu/AliExpress 覆盖证据。Logitech 的 G304 黑色官方页正文同时出现 G305 命名，说明地区命名存在交叉，不能看到“G305”就自动升级为 A-exact。ATK 官方 RS6+ 页可闭合 White Samurai、磁轴、有线等基线。[Logitech](https://www.logitechg.com/en-in/shop/p/g304-lightspeed-wireless-gaming-mouse)

华为官方规格可闭合 Band 11 的悦动白、铝合金、1.62 英寸，以及 Band 11 Pro 的羽砂黑铝合金；华为支持页还明确 NFC 交通卡/门禁等相关能力仅支持**中国大陆发售的 NFC 版本**，因此美国区近似版本不能冒充冻结 exact。[Huawei Consumer](https://consumer.huawei.com/cn/wearables/band11/specs/) Aqara 官方规格页确认 S1E 型号 CJPKG01LM、220V~50Hz。[aqara.cn](https://www.aqara.cn/Smart-Magic-Switch-S1E_spec)

## 4. 论坛证据

Aqara 官方论坛中，工作人员回复称 S1E 面向中国大陆市场，在美国 region 下不能正常使用，需要选择 Mainland China region；这是 C09-S03 地域适配的直接社区反证。[Aqara Forum](https://forum.aqara.com/t/is-there-any-way-to-integrate-the-s1-switch-into-the-us/69988) 另有外设社区完整文章把国内“GPW5 雪豹”对应到 PRO X2 SUPERSTRIKE，可作为命名映射辅助，但不能替代平台商品页验证。[Weistang](https://www.weistang.com/portal.php?aid=26341\&mod=view\&page=1)

## 5. 反证

最强反证不是“平台没有货”，而是**不能把全球版/近似名误判为 exact**：华为 NFC 有大陆区限制；Aqara S1E 有美国 region 不适用证据；G304/G305 存在官方地区命名交叉。[Huawei Consumer](https://consumer.huawei.com/cn/support/content/zh-cn15996163/)

## 6. 置信度

对“当前研究接口无法核验这 18 个目标平台单元”置信度高；对“Temu/AliExpress 实际是否销售这些产品”置信度低、状态 unresolved。所有 `china_head_us_middle_tail_status` 均保留 `unresolved`。

## 7. 缺口

seller/item、精确平台版本、库存、US warehouse、USD/CNY、ordinary delivered price、配送费结构、重量尺寸、HTS/关税分类与税率来源均未在目标平台原页观察到，因此全部为 `null`，绝不把未知写成缺货。ZIP10001 也无法在被阻断页面中实际设置验证。未登录、未下单、未联系商家。

## 8. 意外发现

小米当前动态商品页出现明显映射不稳定：同一 `product_id=21165` 的抓取内容曾落到其他小米产品，而非智能摄像机 4；因此搜索索引标题、HTTP 成功或页面壳都不足以闭合 C09-S01。[Xiaomi India](https://www.mi.com/shop/buy/detail?product_id=21165)

## 9. 自我反驳

“18/18 BLOCKED”可能主要反映当前研究接口与两平台的反自动化/动态页面限制，而不是商品不存在。搜索引擎覆盖本身也不完整；所以不能据此推出“海外没有 exact”、不能改写冻结样本，也不能把状态升级为 `VERIFIED_UNAVAILABLE`。

## 10. 下一实验

下一轮应在可正常渲染的**未登录美国站浏览器**中固定 US + ZIP10001，对这 9 个 exact query 各执行一次，逐项保存 seller/item URL、变体选择、库存、仓库、货币、普通公开商品价与配送费；A/B/C 分开。若仍被挡，继续保留 `BLOCKED`，不重选“更容易找到海外价”的 SKU。四种 shipment structure 因本段未给出各结构名称且无报价，均保持独立的 `not_computable`，不自行发明结构或税率。

```json
{
  "job_id":"W4-A-batch03",
  "parent_replicate":"W4-A",
  "web_research_available":true,
  "pre_freeze_compliance":true,
  "frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "as_of":"2026-10-06",
  "assigned_sku_ids":["C07-S01","C07-S02","C07-S03","C08-S01","C08-S02","C08-S03","C09-S01","C09-S02","C09-S03"],
  "categories":[
    {"category_id":"C07","status":"temu_aliexpress_target_pages_blocked_no_verified_offers"},
    {"category_id":"C08","status":"temu_aliexpress_target_pages_blocked_no_verified_offers"},
    {"category_id":"C09","status":"temu_aliexpress_target_pages_blocked_no_verified_offers"}
  ],
  "batch_counts":{
    "sku_count":9,
    "platform_sku_cells":18,
    "A_exact_offers":0,
    "B_same_oem_branding_diff_offers":0,
    "C_functional_comparable_offers":0,
    "reseller_only_cells":0,
    "blocked_cells":18,
    "login_required_cells":0,
    "verified_unavailable_cells":0,
    "price_observations":0,
    "missing_rate_platform_sku_cells":1.0
  },
  "comparison_policy":{
    "destination":"US ZIP 10001",
    "endpoint":"ordinary delivered price to ZIP10001 before US sales tax",
    "us_sales_tax":"excluded unless explicitly included by platform; none observed",
    "membership_88vip_targeted_coupon_subsidy":"not mixed with ordinary public price; none observed",
    "currency":"null unless directly observed on target page",
    "savings":"not calculated because no verified A/B/C offer"
  },
  "shipment_structures":[
    {"structure_id":"1","protocol_label":null,"status":"not_computable","reason":"no verified platform offer or shipping quote; protocol label not supplied in this batch"},
    {"structure_id":"2","protocol_label":null,"status":"not_computable","reason":"no verified platform offer or shipping quote; protocol label not supplied in this batch"},
    {"structure_id":"3","protocol_label":null,"status":"not_computable","reason":"no verified platform offer or shipping quote; protocol label not supplied in this batch"},
    {"structure_id":"4","protocol_label":null,"status":"not_computable","reason":"no verified platform offer or shipping quote; protocol label not supplied in this batch"}
  ],
  "sources":[
    {"source_id":"S01","url":"https:\/\/www.temu.com\/","title":"Temu homepage","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S02","url":"https:\/\/www.aliexpress.us\/","title":"AliExpress US homepage","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S03","url":"https:\/\/www.temu.com\/search_result.html?search_key=Logitech%20G304","title":"Temu search: Logitech G304","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S04","url":"https:\/\/www.aliexpress.us\/w\/wholesale-logitech-g304.html","title":"AliExpress search: Logitech G304","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S05","url":"https:\/\/www.temu.com\/search_result.html?search_key=Logitech%20GPW5","title":"Temu search: Logitech GPW5","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S06","url":"https:\/\/www.aliexpress.us\/w\/wholesale-logitech-gpw5.html","title":"AliExpress search: Logitech GPW5","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S07","url":"https:\/\/www.temu.com\/search_result.html?search_key=ATK%20RS6%2B","title":"Temu search: ATK RS6+","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S08","url":"https:\/\/www.aliexpress.us\/w\/wholesale-atk-rs6-plus.html","title":"AliExpress search: ATK RS6+","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S09","url":"https:\/\/www.temu.com\/search_result.html?search_key=Huawei%20Band%2011%20NFC","title":"Temu search: Huawei Band 11 NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S10","url":"https:\/\/www.aliexpress.us\/w\/wholesale-huawei-band-11-nfc.html","title":"AliExpress search: Huawei Band 11 NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S11","url":"https:\/\/www.temu.com\/search_result.html?search_key=Huawei%20Band%2011%20Pro%20NFC","title":"Temu search: Huawei Band 11 Pro NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S12","url":"https:\/\/www.aliexpress.us\/w\/wholesale-huawei-band-11-pro-nfc.html","title":"AliExpress search: Huawei Band 11 Pro NFC","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S13","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Watch%20S5%2041mm","title":"Temu search: Xiaomi Watch S5 41mm","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S14","url":"https:\/\/www.aliexpress.us\/w\/wholesale-xiaomi-watch-s5-41mm.html","title":"AliExpress search: Xiaomi Watch S5 41mm","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S15","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Smart%20Camera%204%208MP%204K","title":"Temu search: Xiaomi Smart Camera 4 8MP 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S16","url":"https:\/\/www.aliexpress.us\/w\/wholesale-xiaomi-smart-camera-4-8mp-4k.html","title":"AliExpress search: Xiaomi Smart Camera 4 8MP 4K","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S17","url":"https:\/\/www.temu.com\/search_result.html?search_key=Xiaomi%20Smart%20Door%20Lock%204%20Pro%20Dual%20Camera","title":"Temu search: Xiaomi Smart Door Lock 4 Pro Dual Camera","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S18","url":"https:\/\/www.aliexpress.us\/w\/wholesale-xiaomi-smart-door-lock-4-pro-dual-camera.html","title":"AliExpress search: Xiaomi Smart Door Lock 4 Pro Dual Camera","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S19","url":"https:\/\/www.temu.com\/search_result.html?search_key=Aqara%20S1E%20CJPKG01LM","title":"Temu search: Aqara S1E CJPKG01LM","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},
    {"source_id":"S20","url":"https:\/\/www.aliexpress.us\/w\/wholesale-aqara-s1e-cjpkg01lm.html","title":"AliExpress search: Aqara S1E CJPKG01LM","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K02"]},
    {"source_id":"S21","url":"https:\/\/www.logitechg.com\/en-in\/shop\/p\/g304-lightspeed-wireless-gaming-mouse","title":"Logitech G304 LIGHTSPEED Wireless Gaming Mouse","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S22","url":"https:\/\/store.logitech.com.cn\/product\/Detail\/8182?SellerId=616&Source=616","title":"Logitech China GPW product page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K04"]},
    {"source_id":"S23","url":"https:\/\/www.atk.store\/products\/atk-rs6-plus-series-aluminum-magnetic-switch-keyboard","title":"ATK RS6+ Series Aluminum Magnetic Switch Keyboard","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S24","url":"https:\/\/consumer.huawei.com\/cn\/wearables\/band11\/specs\/","title":"HUAWEI Band 11 specifications","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"S25","url":"https:\/\/consumer.huawei.com\/cn\/wearables\/band11-pro\/specs\/","title":"HUAWEI Band 11 Pro specifications","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},
    {"source_id":"S26","url":"https:\/\/consumer.huawei.com\/cn\/support\/content\/zh-cn15996163\/","title":"Huawei Band model/NFC support information","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06","K07"]},
    {"source_id":"S27","url":"https:\/\/consumer.huawei.com\/cn\/support\/content\/zh-cn15936679\/","title":"Huawei wearable NFC regional support information","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06","K07"]},
    {"source_id":"S28","url":"https:\/\/www.mi.com\/shop\/buy\/detail?product_id=25419","title":"Xiaomi Watch S5 41mm","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S29","url":"https:\/\/www.mi.com\/xiaomi-smartlock-4-pro-dual-camera","title":"小米智能门锁4 Pro 双摄版","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K09"]},
    {"source_id":"S30","url":"https:\/\/www.aqara.cn\/Smart-Magic-Switch-S1E_spec","title":"妙控开关 S1E 产品参数","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K10"]},
    {"source_id":"S31","url":"https:\/\/forum.aqara.com\/t\/is-there-any-way-to-integrate-the-s1-switch-into-the-us\/69988","title":"Is there any way to integrate the S1 switch into the US?","published_at":"2025-08-13","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K10"]},
    {"source_id":"S32","url":"https:\/\/www.weistang.com\/portal.php?aid=26341&mod=view&page=1","title":"罗技 GPW5 雪豹相关体验文章","published_at":"2026-02-10","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K04"]},
    {"source_id":"S33","url":"https:\/\/www.mi.com\/shop\/buy\/detail?product_id=21165","title":"Xiaomi dynamic product page at product_id=21165","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K11"]}
  ],
  "claims":[
    {"claim_id":"K01","claim":"All nine Temu SKU-specific target search URLs were inaccessible in the research interface; the Temu homepage exposed only a page shell, so no Temu offer, price, seller, inventory, warehouse or ZIP10001 delivery value was verified.","classification":"FACT","source_ids":["S01","S03","S05","S07","S09","S11","S13","S15","S17","S19"],"confidence":"high","counterevidence":"Search engines may index Temu pages, but no exact target item page was directly readable and snippets were not used as offer evidence."},
    {"claim_id":"K02","claim":"All nine AliExpress US SKU-specific target search URLs were inaccessible in the research interface and the US homepage returned blocked/403 behavior, so no AliExpress offer was verified.","classification":"FACT","source_ids":["S02","S04","S06","S08","S10","S12","S14","S16","S18","S20"],"confidence":"high","counterevidence":"External indexing may exist but cannot establish live seller, variant, price, stock or delivery without opening the original item page."},
    {"claim_id":"K03","claim":"Logitech's official G304 page for the black model uses G304 in the product identity while page copy also refers to G305 LIGHTSPEED; therefore a future G305 listing must not automatically be classified as A-exact for frozen G304 without region/variant closure.","classification":"INFERENCE","source_ids":["S21"],"confidence":"high","counterevidence":"No target-platform G305 or G304 offer was actually observed in this batch."},
    {"claim_id":"K04","claim":"A readable community article maps the domestic GPW5 雪豹 name to Logitech PRO X2 SUPERSTRIKE; the Logitech China page itself was only a page shell in this run, so this mapping remains supporting rather than decisive platform evidence.","classification":"FACT","source_ids":["S22","S32"],"confidence":"medium","counterevidence":"No Temu or AliExpress product page was available to confirm an actual matching offer."},
    {"claim_id":"K05","claim":"ATK's official RS6+ page provides a White Samurai option and describes a magnetic-switch, wired 65% keyboard baseline; these specifications were used only as match guardrails, not as marketplace price evidence.","classification":"FACT","source_ids":["S23"],"confidence":"high","counterevidence":"No target-platform offer was readable."},
    {"claim_id":"K06","claim":"Huawei official materials support the Band 11 悦动白/aluminum/1.62-inch baseline and identify an NFC version; Huawei also states relevant NFC wallet/card functions apply to NFC versions sold in Mainland China, creating a region-specific exact-match constraint.","classification":"FACT","source_ids":["S24","S26","S27"],"confidence":"high","counterevidence":"A marketplace listing could still sell a Mainland-China unit to a US address, but none was directly observed."},
    {"claim_id":"K07","claim":"Huawei official materials support Band 11 Pro 羽砂黑 with aluminum case and an NFC model, while the same Mainland-China NFC restriction prevents treating an unspecified global variant as exact.","classification":"FACT","source_ids":["S25","S26","S27"],"confidence":"high","counterevidence":"No target-platform listing was readable."},
    {"claim_id":"K08","claim":"Xiaomi's current official page confirms the Xiaomi Watch S5 41mm model, but the fetched page text did not close the frozen 海盐蓝 plus 澎湃OS 4 combination; this source therefore cannot substitute for exact target-platform verification.","classification":"FACT","source_ids":["S28"],"confidence":"high","counterevidence":"The domestic frozen evidence already verifies the exact variant; this claim concerns only the independently opened current manufacturer page."},
    {"claim_id":"K09","claim":"Xiaomi's official page currently identifies 小米智能门锁4 Pro 双摄版, providing a manufacturer naming baseline but no Temu/AliExpress coverage evidence.","classification":"FACT","source_ids":["S29"],"confidence":"high","counterevidence":"No marketplace offer was readable."},
    {"claim_id":"K10","claim":"Aqara's official specification page identifies S1E model CJPKG01LM and 220V~50Hz; an Aqara forum response states S1E is intended for Mainland China and does not work in the US region, requiring Mainland China region selection.","classification":"FACT","source_ids":["S30","S31"],"confidence":"high","counterevidence":"This does not prove marketplace unavailability; it is a regional-use constraint."},
    {"claim_id":"K11","claim":"The currently retrieved Xiaomi page at product_id=21165 did not reliably resolve to the frozen Smart Camera 4 product, demonstrating that search-index titles or dynamic page shells cannot by themselves establish exact variant identity.","classification":"FACT","source_ids":["S33"],"confidence":"high","counterevidence":"A search index had previously associated the identifier with a camera page, but the directly opened current page content was inconsistent."}
  ],
  "data_gaps":[
    "Temu SKU-specific target search pages were blocked/inaccessible; homepage only yielded a page shell.",
    "AliExpress US SKU-specific target search pages were blocked/inaccessible; US homepage returned blocked/403 behavior.",
    "seller, item_id, exact marketplace variant, stock, warehouse, US-warehouse evidence, currency, ordinary price, delivery charge and ZIP10001 delivered price are unobserved and must not be interpreted as out-of-stock.",
    "No verified package weight or dimensions were available from the target marketplace offers.",
    "No tariff classification, tariff-rate source or import-duty quote was observed; no tariff rate was manufactured.",
    "ZIP10001 could not be applied and verified on the blocked target pages.",
    "The four shipment-structure protocol labels were not supplied in this batch and no marketplace/freight quote was available, so all four remain separately non-computable."
  ],
  "coverage":[
    {
      "sku_id":"C07-S01","category_id":"C07","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech G304","source_id":"S03","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech G304","source_id":"S04","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation","G304/G305 regional naming cannot be auto-promoted to A-exact"]
    },
    {
      "sku_id":"C07-S02","category_id":"C07","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech GPW5","source_id":"S05","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Logitech GPW5","source_id":"S06","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","head_status_verified=false preserved and excluded from verified-head statistics","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C07-S03","category_id":"C07","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"ATK RS6+","source_id":"S07","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"ATK RS6+","source_id":"S08","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","head_status_verified=false preserved and excluded from verified-head statistics","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C08-S01","category_id":"C08","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 NFC","source_id":"S09","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 NFC","source_id":"S10","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","Mainland-China NFC-region constraint must be closed before A-exact classification","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C08-S02","category_id":"C08","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 Pro NFC","source_id":"S11","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Huawei Band 11 Pro NFC","source_id":"S12","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","Mainland-China NFC-region constraint must be closed before A-exact classification","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C08-S03","category_id":"C08","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Watch S5 41mm","source_id":"S13","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Watch S5 41mm","source_id":"S14","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","head_status_verified=false preserved and excluded from verified-head statistics","current manufacturer fetch did not independently close 海盐蓝 plus 澎湃OS 4","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C09-S01","category_id":"C09","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Camera 4 8MP 4K","source_id":"S15","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Camera 4 8MP 4K","source_id":"S16","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","dynamic Xiaomi page mapping anomaly means page shell/index title cannot establish exact identity","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C09-S02","category_id":"C09","head_status_verified":true,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Door Lock 4 Pro Dual Camera","source_id":"S17","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Xiaomi Smart Door Lock 4 Pro Dual Camera","source_id":"S18","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","US door/lock-body compatibility remains unverified","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    },
    {
      "sku_id":"C09-S03","category_id":"C09","head_status_verified":false,"exact_variant_verified":true,
      "temu":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Aqara S1E CJPKG01LM","source_id":"S19","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","homepage only page shell","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":[{"query":"Aqara S1E CJPKG01LM","source_id":"S20","observed_at":"2026-10-06"}],"access_limitations":["target search URL inaccessible in research interface","AliExpress US homepage blocked/403","not logged in","ZIP10001 delivery/currency/stock not verifiable"]},
      "china_head_us_middle_tail_status":"unresolved",
      "caveats":["frozen SKU retained; BLOCKED is not out-of-stock or VERIFIED_UNAVAILABLE","head_status_verified=false preserved and excluded from verified-head statistics","official/community evidence indicates CJPKG01LM is 220V and China-region dependent; US-region similarity cannot be treated as exact","A/B/C have no verifiable target-platform item page, so no cross-bucket savings calculation"]
    }
  ]
}
```
=== UNEDITED W4-A-batch04; SHA256 61c8a148963e82298ce93dc7af4f7807cedacb3e8a59aa767d51a58b39ff2219 ===
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
=== UNEDITED W4-A-batch05; SHA256 31e98b499939595cff0d40ffba236803ae8fec3151a37be4723ea7aa436259db ===
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
=== UNEDITED W4-A-batch06; SHA256 19214aface74c40865d39108710d5240ff594173b2199d473c39287ebf7cf1b1 ===
### 1. 直接回答

本批次只研究 C16/C17/C18 的 9 个冻结 SKU，未替换任何 SKU，冻结前 `head_status_verified` / `exact_variant_verified` 全部原样保留。共执行 **18 个平台检查（9 SKU×Temu/AliExpress）**；两平台原始搜索页在本研究环境均不可读，因此 **18/18=BLOCKED，已核平台 offer=0，研究缺失率100%**。这不是“市场无货率”，也不能写成 `VERIFIED_UNAVAILABLE`。A/B/C 均无可计入 offer，更无同款节省或跨 bucket 节省。

### 2. 证据表

| sku_id | 冻结 head/exact | Temu | AliExpress | 本批结论 |
|---|---|---|---|---|
| C16-S01 | T/T | BLOCKED | BLOCKED | CV976 奶茶色 exact 未能平台核验。([](), []()) |
| C16-S02 | T/T | BLOCKED | BLOCKED | CW2288-111 还必须锁定白色+42码。([Invalid URL]()) |
| C16-S03 | F/T | BLOCKED | BLOCKED | JI0079 二级索引有痕迹，但 Ali 原商品页也阻断，37码未核。([Invalid URL]()) |
| C17-S01 | T/T | BLOCKED | BLOCKED | Temu 曾浮出3×45L通用箱URL，但打开为空壳，不能算C comparable。([Invalid URL]()) |
| C17-S02 | T/T | BLOCKED | BLOCKED | 30.5L×2抽屉式未核。([Invalid URL]()) |
| C17-S03 | F/T | BLOCKED | BLOCKED | JEKO&JEKO 5层未核。([Invalid URL]()) |
| C18-S01 | T/T | BLOCKED | BLOCKED | 10698 基础盒不足以代替“赠礼袋”冻结捆绑。([Invalid URL]()) |
| C18-S02 | T/T | BLOCKED | BLOCKED | 同系列冰箱贴≠搪胶毛绒挂件随机1个。([Invalid URL]()) |
| C18-S03 | F/T | BLOCKED | BLOCKED | 二级索引有完整RG 2.0标题，但 Ali 原页阻断。([Invalid URL]()) |

### 3. 一级来源

品牌一级来源用于限定“exact”的边界，而不用于证明 Temu/AliExpress 覆盖：Nike 官方确认 CW2288-111 为 White/White；adidas 官方确认 JI0079；LEGO 官方 10698 为 790件基础盒；POP MART 官方分别存在 Vacation Mode On **Vinyl Plush Pendant** 与 **Fridge Magnet** 两个不同产品；Bandai 官方确认 RG 1/144 RX-78-2 Ver.2.0。[Nike.com](https://www.nike.com/t/air-force-1-07-mens-shoes-DZejrQoC/CW2288-111) Coach CV976 官方URL在本次打开时重定向到英国首页，不能补做海外颜色映射。[Coach](https://www.coach.com/products/city-tote-bag-in-signature-canvas/CV976.html)

### 4. 论坛证据

论坛证据很弱：Gunpla 社区有用户提到从 Temu 得到适用于 RG RX-78-2 Ver.2.0 的**武器套件**，不是冻结 SKU 的完整 Bandai 模型；另有 replica 社区讨论 CW2288-111，但不能验证当前 AliExpress/Temu 卖家、真伪、42码或库存。[Reddit](https://www.reddit.com/r/Gunpla/comments/1mrn25e?utm_source=chatgpt.com)

### 5. 反证

不能把 BLOCKED 推成“没有货”。PriceArchive 在 2026-10-06 附近仍索引到 AliExpress 的 JI0079、Bandai RG 2.0，以及 Vacation Mode On 冰箱贴等标题；但这些均非本协议允许的原平台核验。[Pricearchive.org](https://ms.pricearchive.org/aliexpress.com/item/1005013164825333) 另一个二级页面的 exact-series 毛绒挂件当前显示“无报价”，但那也不能证明美国 AliExpress 不可售。[Yorkshire.com](https://www.yorkshire.com/marketplace/toys-and-games-1239/puzzles-3867/c3041cd4-fab4-4cbe-bb56-467e63c44b28)

### 6. 置信度

对“**本研究环境访问受阻**”置信度高；对“平台真实覆盖/缺货”置信度低，因此 9 个 `china_head_us_middle_tail_status` 全部为 `unresolved`。冻结的 6 个 verified-head 仍为 head，3 个 opportunity 位绝不升级。

### 7. 缺口

seller、item、库存、US warehouse、region、币种、ZIP10001普通公开送达价、运费、用于运输计费的重量/尺寸、HTS/关税分类及来源均未直接观察，全部保持 `null`。比较端点定义为 **ZIP10001普通公开商品价+直接可见运费/强制平台费用；美国销售税排除且本次未观察**。协调器本段未给出四种 shipment structure 的定义，所以仅分别保留四个 null 槽，不擅自命名或填税率。

### 8. 意外发现

最明显的是 CRYBABY：二级 AliExpress 痕迹出现同系列冰箱贴，而一级来源证明它与冻结的毛绒挂件是不同物件；这正说明只看系列名或图片会产生错误 exact。[POP MART](https://www.popmart.com/us/products/4071)

### 9. 自我反驳

本结果很可能低估真实平台覆盖，因为阻断发生在研究工具而非证明消费者浏览器也不可访问；同时二级索引确实提供若干候选。反过来，二级索引又可能地区错配、规格不全或陈旧，所以也不能把这些候选升级为 A/B/C offer。

### 10. 下一实验

协调器下一轮应在**未登录、美国地区、ZIP10001**的普通浏览器里仅复核这些冻结 SKU；优先检查已定位的 AliExpress 候选 `JI0079 item 1005012746466736`、`RG 2.0 item 1005013164825333`，并严格记录卖家、精确尺码/版本、库存、仓库、普通公开价格与运费。仍不得登录、下单、联系卖家。所有本模型证据仍待协调器复核。

```json
{"job_id":"W4-A-batch06","parent_replicate":"W4-A","web_research_available":true,"pre_freeze_compliance":true,"frozen_sample_sha256":"4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185","assigned_sku_ids":["C16-S01","C16-S02","C16-S03","C17-S01","C17-S02","C17-S03","C18-S01","C18-S02","C18-S03"],"categories":[{"category_id":"C16","status":"unresolved_due_platform_access_block"},{"category_id":"C17","status":"unresolved_due_platform_access_block"},{"category_id":"C18","status":"unresolved_due_platform_access_block"}],"batch_counts":{"assigned_skus":9,"platform_checks":18,"status_counts":{"EXACT_OBSERVED":0,"OEM_OBSERVED":0,"COMPARABLE_ONLY":0,"RESELLER_ONLY":0,"NOT_OBSERVED":0,"BLOCKED":18,"LOGIN_REQUIRED":0,"VERIFIED_UNAVAILABLE":0},"verified_platform_offers":0,"missing_or_inaccessible_checks":18,"missing_rate":1.0,"note":"batch research-missing rate only; not market coverage/stockout"},"costing":{"comparison_endpoint":"ordinary public delivered price to US ZIP10001; visible item price+shipping/mandatory platform charges","us_sales_tax_treatment":"excluded; not observed","shipment_structures":[{"structure_index":1,"definition":null,"quote":null,"currency":null,"weight_dimensions":null,"shipping":null,"tariff_classification":null,"tariff_source":null},{"structure_index":2,"definition":null,"quote":null,"currency":null,"weight_dimensions":null,"shipping":null,"tariff_classification":null,"tariff_source":null},{"structure_index":3,"definition":null,"quote":null,"currency":null,"weight_dimensions":null,"shipping":null,"tariff_classification":null,"tariff_source":null},{"structure_index":4,"definition":null,"quote":null,"currency":null,"weight_dimensions":null,"shipping":null,"tariff_classification":null,"tariff_source":null}],"assumptions":["four structure definitions absent from frozen subset; preserved as separate null slots","no tariff/shipping rate manufactured"]},"sources":[{"source_id":"S01","url":"https://www.temu.com/search_result.html?search_key=COACH%20CV976","title":"Temu search: COACH CV976","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S02","url":"https://www.aliexpress.com/w/wholesale-COACH-CV976.html","title":"AliExpress search: COACH CV976","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S03","url":"https://www.temu.com/search_result.html?search_key=CW2288-111","title":"Temu search: CW2288-111","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S04","url":"https://www.aliexpress.com/w/wholesale-CW2288-111.html","title":"AliExpress search: CW2288-111","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S05","url":"https://www.temu.com/search_result.html?search_key=JI0079","title":"Temu search: JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S06","url":"https://www.aliexpress.com/w/wholesale-JI0079.html","title":"AliExpress search: JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S07","url":"https://www.temu.com/search_result.html?search_key=CHAHUA%2034L%203","title":"Temu search: CHAHUA 34L×3","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S08","url":"https://www.aliexpress.com/w/wholesale-CHAHUA-34L.html","title":"AliExpress search: CHAHUA 34L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S09","url":"https://www.temu.com/search_result.html?search_key=CHAHUA%2030.5L","title":"Temu search: CHAHUA 30.5L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S10","url":"https://www.aliexpress.com/w/wholesale-CHAHUA-30.5L.html","title":"AliExpress search: CHAHUA 30.5L","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S11","url":"https://www.temu.com/search_result.html?search_key=JEKO%20JEKO%205%20drawer","title":"Temu search: JEKO JEKO 5 drawer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S12","url":"https://www.aliexpress.com/w/wholesale-JEKO-JEKO-5-drawer.html","title":"AliExpress search: JEKO JEKO 5 drawer","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S13","url":"https://www.temu.com/search_result.html?search_key=LEGO%2010698","title":"Temu search: LEGO 10698","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S14","url":"https://www.aliexpress.com/w/wholesale-LEGO-10698.html","title":"AliExpress search: LEGO 10698","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S15","url":"https://www.temu.com/search_result.html?search_key=CRYBABY%20Vacation%20Mode%20On","title":"Temu search: CRYBABY Vacation Mode On","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S16","url":"https://www.aliexpress.com/w/wholesale-CRYBABY-Vacation-Mode-On.html","title":"AliExpress search: CRYBABY Vacation Mode On","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S17","url":"https://www.temu.com/search_result.html?search_key=RG%201%2F144%20RX-78-2%20Ver%202.0","title":"Temu search: RG 1/144 RX-78-2 Ver 2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S18","url":"https://www.aliexpress.com/w/wholesale-RG-1-144-RX-78-2-Ver-2.0.html","title":"AliExpress search: RG 1/144 RX-78-2 Ver 2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":["K01"]},{"source_id":"S19","url":"https://www.nike.com/t/air-force-1-07-mens-shoes-DZejrQoC/CW2288-111","title":"Nike Air Force 1 '07 CW2288-111","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S20","url":"https://www.adidas.com/us/superstar-ii-shoes/JI0079.html","title":"adidas Superstar II JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S21","url":"https://www.lego.com/en-us/product/lego-large-creative-brick-box-10698","title":"LEGO 10698 Large Creative Brick Box","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S22","url":"https://www.popmart.com/us/products/4071","title":"POP MART CRYBABY Vacation Mode On Vinyl Plush Pendant Blind Box","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03","K04"]},{"source_id":"S23","url":"https://www.popmart.com/us/products/4049/crybaby-vacation-mode-on-series-fridge-magnet-blind-box","title":"POP MART CRYBABY Vacation Mode On Fridge Magnet Blind Box","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K04"]},{"source_id":"S24","url":"https://bandaihobbysite.cn/index/index/detail/id/2701","title":"BANDAI RG 1/144 RX-78-2 Ver.2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S25","url":"https://ms.pricearchive.org/aliexpress.com/item/1005013164825333","title":"AliExpress trace: Bandai RG RX-78-2 Ver.2.0","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02"]},{"source_id":"S26","url":"https://ms.pricearchive.org/aliexpress.com/item/1005012746466736","title":"AliExpress trace: adidas JI0079","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02"]},{"source_id":"S27","url":"https://ro.pricearchive.org/aliexpress.com/item/1005010230412412","title":"AliExpress trace: CRYBABY Vacation Mode On fridge magnet","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02","K04"]},{"source_id":"S28","url":"https://ro.pricearchive.org/search/aliexpress.com/air-force-one-mid/1","title":"AliExpress trace search: Nike Air Force 1","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02"]},{"source_id":"S29","url":"https://www.yorkshire.com/marketplace/toys-and-games-1239/puzzles-3867/c3041cd4-fab4-4cbe-bb56-467e63c44b28","title":"CRYBABY Vacation Mode On pendant aggregate","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02"]},{"source_id":"S30","url":"https://www.reddit.com/r/Gunpla/comments/1mrn25e","title":"Reddit: Temu/Gunpla accessory discussion","published_at":null,"retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K05"]},{"source_id":"S31","url":"https://www.reddit.com/r/repbudgetsneakers/comments/wu9nbx","title":"Reddit: CW2288-111 discussion","published_at":null,"retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K05"]},{"source_id":"S32","url":"https://www.temu.com/plastic-storage-bin-container-w-lid-3-45l-set-of-3-stackable-compact-sturdy-new-g-602936818117657.html","title":"Temu generic 3×45L storage-bin page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"page_shell","claims_supported":["K01"]}],"claims":[{"claim_id":"K01","claim":"9 assigned SKUs × 2 platforms = 18 direct marketplace search checks were inaccessible/page-shell and are classified BLOCKED, not unavailable.","classification":"FACT","source_ids":["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18","S32"],"confidence":"high","counterevidence":"secondary indexes surface some candidates, so BLOCKED cannot mean no listing"},{"claim_id":"K02","claim":"Secondary indexes surface AliExpress traces for CW2288-111, JI0079, CRYBABY Vacation Mode On and RG RX-78-2 Ver.2.0; none are platform-verified offers.","classification":"FACT","source_ids":["S25","S26","S27","S28","S29"],"confidence":"medium","counterevidence":"seller/variant/stock/US warehouse/ZIP10001 delivery cannot be verified from those secondary pages"},{"claim_id":"K03","claim":"Primary brand pages confirm strict variant boundaries for Nike CW2288-111, adidas JI0079, LEGO 10698, POP MART Vacation Mode On vinyl-plush pendant, and BANDAI RG RX-78-2 Ver.2.0.","classification":"FACT","source_ids":["S19","S20","S21","S22","S24"],"confidence":"high","counterevidence":"brand-page existence does not establish Temu/AliExpress coverage or frozen bundle/size"},{"claim_id":"K04","claim":"POP MART Vacation Mode On fridge magnet is a distinct product from the frozen vinyl-plush pendant and is not exact.","classification":"FACT","source_ids":["S22","S23","S27"],"confidence":"high","counterevidence":"same series branding is insufficient for exact/OEM equivalence"},{"claim_id":"K05","claim":"Forum evidence is contextual only and does not verify a current exact platform offer.","classification":"INFERENCE","source_ids":["S30","S31"],"confidence":"high","counterevidence":"community posts can indicate related-item presence but not current seller/variant/stock/delivery"}],"candidate_traces":[{"sku_id":"C16-S02","platform":"aliexpress","trace":"secondary CW2288-111 title; white/42/direct offer unresolved","usable_as_offer":false,"source_ids":["S28"]},{"sku_id":"C16-S03","platform":"aliexpress","trace":"secondary item 1005012746466736 titled JI0079; size37/direct offer unresolved","usable_as_offer":false,"source_ids":["S26"],"original_url":"https://www.aliexpress.com/item/1005012746466736.html","original_access_state":"blocked"},{"sku_id":"C17-S01","platform":"temu","trace":"generic 3×45L storage-bin URL opened as page shell; not counted as C","usable_as_offer":false,"source_ids":["S32"]},{"sku_id":"C18-S02","platform":"aliexpress","trace":"secondary fridge-magnet trace is variant-mismatched; exact pendant aggregate currently has no offers, neither proves US AliExpress status","usable_as_offer":false,"source_ids":["S27","S29","S22","S23"],"original_url":"https://www.aliexpress.com/item/1005010230412412.html","original_access_state":"blocked"},{"sku_id":"C18-S03","platform":"aliexpress","trace":"secondary item 1005013164825333 titled Bandai RG RX-78-2 Ver.2.0; direct offer unresolved","usable_as_offer":false,"source_ids":["S25","S24"],"original_url":"https://www.aliexpress.com/item/1005013164825333.html","original_access_state":"blocked"}],"coverage":[{"sku_id":"C16-S01","category_id":"C16","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:COACH CV976 CITY33 奶茶色","S01","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:COACH CV976 CITY33 奶茶色","S02","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED不等于缺货/无listing"]},{"sku_id":"C16-S02","category_id":"C16","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:NIKE CW2288-111 白色 42码","S03","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:NIKE CW2288-111 白色 42码","S04","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["A需白色+42码","BLOCKED不等于缺货/无listing"]},{"sku_id":"C16-S03","category_id":"C16","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:adidas JI0079 Superstar II 37码","S05","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:adidas JI0079 Superstar II 37码","S06","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["A需37码","BLOCKED不等于缺货/无listing"]},{"sku_id":"C17-S01","category_id":"C17","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:CHAHUA 34L×3 奶黄色 45.5×38×31cm","S07","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:CHAHUA 34L×3 奶黄色 45.5×38×31cm","S08","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED不等于缺货/无listing"]},{"sku_id":"C17-S02","category_id":"C17","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:CHAHUA 30.5L 抽屉式×2","S09","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:CHAHUA 30.5L 抽屉式×2","S10","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED不等于缺货/无listing"]},{"sku_id":"C17-S03","category_id":"C17","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:JEKO&JEKO 五斗柜 5层","S11","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:JEKO&JEKO 五斗柜 5层","S12","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["BLOCKED不等于缺货/无listing"]},{"sku_id":"C18-S01","category_id":"C18","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:LEGO 10698 经典创意积木盒+赠礼袋","S13","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:LEGO 10698 经典创意积木盒+赠礼袋","S14","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["A需包含赠礼袋捆绑","BLOCKED不等于缺货/无listing"]},{"sku_id":"C18-S02","category_id":"C18","head_status_verified":true,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:POP MART CRYBABY Vacation Mode On 搪胶毛绒挂件盲盒 随机1个","S15","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:POP MART CRYBABY Vacation Mode On 搪胶毛绒挂件盲盒 随机1个","S16","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["冰箱贴≠搪胶毛绒挂件","BLOCKED不等于缺货/无listing"]},{"sku_id":"C18-S03","category_id":"C18","head_status_verified":false,"exact_variant_verified":true,"temu":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:BANDAI RG 1/144 RX-78-2 RGU ver 2.0","S17","ZIP10001"],"access_limitations":["direct_search_blocked; no login/order/contact"]},"aliexpress":{"observation_status":"BLOCKED","offers":[],"search_scope":["exact:BANDAI RG 1/144 RX-78-2 RGU ver 2.0","S18","ZIP10001"],"access_limitations":["direct_search_blocked; secondary index not promoted; no login/order/contact"]},"china_head_us_middle_tail_status":"unresolved","caveats":["配件/武器套件≠完整RG 2.0模型","BLOCKED不等于缺货/无listing"]}],"data_gaps":["seller/item/stock/US-warehouse/region/currency/ordinary-delivered-price to ZIP10001 remain unobserved; unobserved≠out-of-stock","no verified A/B/C offer; no cross-bucket savings","shipping/weight-dimensions/tariff classification-source/quotes remain null","four shipment-structure definitions were not supplied; four separate null slots retained","COACH CV976 overseas color-name mapping unresolved in this session","all model-attested sources await coordinator review"]}
```