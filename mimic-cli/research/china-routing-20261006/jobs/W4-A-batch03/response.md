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