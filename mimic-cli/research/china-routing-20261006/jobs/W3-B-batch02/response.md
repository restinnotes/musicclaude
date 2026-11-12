## 1. 直接回答

本批次 **9/9 个冻结 SKU 均已逐一检索与关键页检查，未删除、未换款、未查看其他复本/批次结果**。冻结前状态原样保留：`head_status_verified=true` 为 6/9，`false` 为 3/9；`exact_variant_verified=true` 为 9/9。

Price Spread Audit 的核心结果是：**本批次没有任何 SKU 能形成 verified landed savings**。不是因为“没有价差”，而是所有 SKU 的四种物流结构至少缺少真实国际运费、实际/体积重、报关 HTS、适用 MFN/Section 301、清关 mandatory charges、汇率或 ZIP10001 到门费用中的一项，所以全部 `landed_total=null`。截至 2026-10-06，美国低值进口不能再默认使用原先的一般 $800 de minimis 免税逻辑；同时 USTR 明确要求先确定 HTS 才能判断 Section 301，因此不能填一个臆测的固定税率。 [GovInfo](https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf)

## 2. 证据表

| SKU | 冻结 H/E | 中国普通公开观察 | 最强海外观察 | bucket / 结果 |
|---|---|---|---|---|
| C04-S01 ASUS 破晓 | T/T | JD 精确页动态壳；当前价未核 | 未找到可核验精确海外页 | 无 A/B/C 可计价；landed null [JD.com](https://item.jd.com/100293974227.html) |
| C04-S02 GMK EVO-X2 | T/T | JD 精确页当前价未核 | GMK 美国站有 128GB+2TB 选项，但该选项即时价未单独暴露且为美区/US plug | 仅 C 级线索；不冒充 A [GMKtec](https://www.gmktec.com/collections/evo-series) |
| C04-S03 Beelink SER8 | F/T | **¥2,049**，深空灰准系统，公开标价；到手价需登录 | Beelink US **$619**，但为带内存/SSD版本，不是准系统 | C；捆绑不一致 [JD.com](https://item.jd.com/product/T0XTZzdZIRILoxOTgqMUUA.html?utm_source=chatgpt.com) |
| C05-S01 Samsung 990 EVO Plus | T/T | JD 当前价未核 | eBay **MZ-V9S2T0BW $497.22**，与三星中国型号一致；Newegg 美版 `/AM` $369.99 | eBay=A 商品价；Newegg=C 地区 SKU；ZIP10001 到门均未核 [Samsung China](https://www.samsung.com.cn/support/model/MZ-V9S2T0BW/) |
| C05-S02 Xiaomi BE6500 | T/T | 小米官方公开目录 **¥599** | eBay 中国卖家 exact BE6500 **$147.51、free shipping 标示**，但未锁定 ZIP10001/进口费 | A 商品价；delivered 未核 [Xiaomi India](https://www.mi.com/micamera?utm_source=chatgpt.com) |
| C05-S03 KINGBANK 银爵 | F/T | **¥3,499** 公开标价；最终到手需登录 | 未找到可打开的精确海外原始销售页 | 无可计算海外端 [JD.com](https://item.jd.com/product/xgX8EKW1Mrj5_OZ5EifFmQ.html?utm_source=chatgpt.com) |
| C06-S01 Lolli Pro SE | T/T | 漫步者直营当前模型价 **¥249**；精确色云岩白由官网产品页确认 | Voptronics **$47.90**、in stock，但颜色未验证 | C；颜色不足以 A [edifierstore.com](https://www.edifierstore.com/home/search) |
| C06-S02 LolliClip SE | T/T | 官网 **¥499 MSRP**，不是已核验成交价 | AliExpress 原页 blocked；eBay.de **€99.99** 只核到型号，精确云霜金/美国配送未核 | C；A 无可用价格 [Edifier](https://cnweb.edifier.com/cate-11.html) |
| C06-S03 Comfo Clip Q | F/T | 漫步者直营模型价 **¥289**；官网确认奶霜白版本存在 | 只找到二手聚合线索，未用作成交价 | 海外可核价缺失 [mall-pc.edifierstore.com](https://mall-pc.edifierstore.com/goods/scene?displayCategoriesId=60) |

比较端点统一为 **美国 ZIP10001、应包含各自 delivery 与 mandatory import costs、排除美国州/地方 sales/use tax**。因此表中海外“商品价”均不等于最终 checkout total。

## 3. 一级来源

型号/规格优先用品牌官网：三星中国确认 `MZ-V9S2T0BW`，小米确认 BE6500，漫步者官网确认三款耳机的精确型号/颜色；销售价格则只在能打开的品牌直营或 retailer 原始页面取值。政府层面采用 Federal Register/CBP/USTR，而非转述文章。 [Samsung China](https://www.samsung.com.cn/support/model/MZ-V9S2T0BW/)

## 4. 论坛证据

论坛只作风险补充，不参与价格或 OEM 认定。Beelink 社区存在 SER8 8745HS BIOS 版本更新讨论；LolliClip SE 有 2026-08-18 的两周使用体验；漫步者论坛也有 Lolli Pro SE 用户体验反馈。这些都不能证明 A/B 匹配或代表整体故障率。 [Bee-Link Forum](https://bbs.bee-link.com/d/4783-ser-series-driver-and-bios-download/519)

## 5. 反证

三个最容易误判的案例均已降级：Samsung Newegg `/AM` 虽更便宜，但冻结样本对应 `BW`，不能用美区 SKU 冒充 A；SER8 美国站 $619 是带 RAM/SSD 的完整机，不是冻结的准系统；Lolli Pro SE 海外页面未证明“云岩白”具体选项，因此不是 A。AliExpress 的价格追踪/搜索摘要也没有被当成成交价。

## 6. 置信度

冻结 SKU 身份与冻结前 `head_status_verified/exact_variant_verified`：**高**。能打开的公开商品价：**中高**。C05-S01/C05-S02 的 A 类“商品本体价格”：**中等**，因为目的地费用尚未锁定。所有 landed total 与 savings：**不可验证，保持 null**。

## 7. 缺口

共同缺口为：真实代理/转运报价、实际及体积重、包装尺寸、电池附费、国际运费、清关/entry mandatory charges、逐 SKU HTS、MFN/301/其他税、以及同一时间点 FX。2026-06-24 起非邮政低值货的一般 de minimis 已被无限期暂停，邮政渠道随后也进入新的低值进口处理框架；不能把进口税费写成 0。 [GovInfo](https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf)

## 8. 意外发现

C05-S02 的中国官网公开价 ¥599 与 eBay exact 商品价 $147.51 看似存在明显方向性差异，但由于 ZIP10001 进口端费用未知，**不能转换成已验证 savings**。另一个异常是 KINGBANK 冻结页公开价 ¥3,499；即使显得异常，也必须保留冻结观察，不能为了“合理”而重新选型号。

## 9. 自我反驳

C05-S01 的 `BW` 相同料号支持 A，但若后续发现销售区域包装、保修或硬件 BOM 不同，应降级。C05-S02 也需进一步确认跨境商品是否仍为完全相同中国固件/硬件。漫步者直营的 ¥249/¥289 是模型级促销页，若结账时指定冻结颜色价格变化，就必须以颜色级结果覆盖当前观察，而不是反向宣称已验证颜色成交价。

## 10. 下一实验

下一轮只需针对这些**同一冻结 SKU**补齐：以 ZIP10001 打开 retailer 配送层、获取四种结构的真实物流报价、称重/包装数据，并由可审计报关来源确定逐 SKU HTS 与当日适用税费；随后按 A/B/C 分开重算。当前小样本只能报告：**A 类商品价观察 2/9、B=0、verified delivered A=0、verified landed=0、verified savings=0**。没有 GMV/ASP 权重，因此不能给 demand-weighted 分布，更不能外推全市场。以下所有网页证据仍待协调器复核。

```json
{
  "job_id": "W3-B-batch02",
  "parent_replicate": "W3-B",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "assigned_sku_ids": ["C04-S01","C04-S02","C04-S03","C05-S01","C05-S02","C05-S03","C06-S01","C06-S02","C06-S03"],
  "comparison_endpoint": {
    "destination": "ZIP10001, United States",
    "include_when_observed": ["delivery","mandatory_import_costs"],
    "exclude": ["US state/local sales tax","US use tax"],
    "final_checkout_total_claimed": false
  },
  "categories": [
    {"category_id":"C04","status":"3/3 frozen SKUs audited; no verified landed total"},
    {"category_id":"C05","status":"3/3 frozen SKUs audited; no verified landed total"},
    {"category_id":"C06","status":"3/3 frozen SKUs audited; no verified landed total"}
  ],
  "sources": [
    {"source_id":"S01","url":"https://item.jd.com/100293974227.html","title":"ASUS 破晓迷你主机 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S02","url":"https://item.jd.com/10147548162123.html","title":"GMK EVO-X2 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S03","url":"https://item.jd.com/product/T0XTZzdZIRILoxOTgqMUUA.html","title":"Beelink SER8 8745HS 深空灰准系统 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02","K05"]},
    {"source_id":"S04","url":"https://www.gmktec.com/collections/evo-series","title":"GMKtec EVO Series","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S05","url":"https://www.gmktec.com/en/products/amd-ryzen%E2%84%A2-ai-max-395-evo-x2-ai-mini-pc","title":"GMKtec EVO-X2 product page","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S06","url":"https://us.bee-link.com/products/beelink-ser8-8745hs","title":"Beelink SER8 8745HS US store","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S07","url":"https://item.jd.com/100144705326.html","title":"Samsung 990 EVO Plus 2TB - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S08","url":"https://www.samsung.com.cn/support/model/MZ-V9S2T0BW/","title":"Samsung 990 EVO Plus 2TB MZ-V9S2T0BW","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03","K05"]},
    {"source_id":"S09","url":"https://www.ebay.com/itm/127946299185","title":"Samsung 990 EVO Plus 2TB MZ-V9S2T0BW - eBay","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S10","url":"https://www.newegg.com/samsung-2tb-990-evo-plus-nvme-2-0/p/N82E16820147900?item=N82E16820147900","title":"Samsung 990 EVO Plus 2TB MZ-V9S2T0B/AM - Newegg","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S11","url":"https://item.jd.com/100134199408.html","title":"Xiaomi BE6500 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":["K01"]},
    {"source_id":"S12","url":"https://www.mi.com/xiaomi-routers/be-6500","title":"Xiaomi Router BE6500","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S13","url":"https://www.mi.com/micamera","title":"Xiaomi official current product catalog containing BE6500","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S14","url":"https://www.ebay.com/itm/396962723194","title":"Xiaomi Router BE6500 - eBay","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K03"]},
    {"source_id":"S15","url":"https://item.jd.com/product/xgX8EKW1Mrj5_OZ5EifFmQ.html","title":"KINGBANK 银爵 32GB DDR5-6000 C36 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S16","url":"https://www.edifier.com/cn/product/product-864.html","title":"EDIFIER Lolli Pro SE","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S17","url":"https://www.edifierstore.com/home/search","title":"EDIFIER official store search","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S18","url":"https://www.voptronics.com/edifier-lolli-pro-se.html","title":"EDIFIER Lolli Pro SE - Voptronics","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S19","url":"https://www.edifier.com/cn/product/product-916.html","title":"EDIFIER LolliClip SE","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S20","url":"https://cnweb.edifier.com/cate-11.html","title":"EDIFIER official earphone catalog","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S21","url":"https://www.aliexpress.us/item/1005013110936399.html","title":"LolliClip SE candidate AliExpress item","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"blocked","claims_supported":["K05"]},
    {"source_id":"S22","url":"https://ms.pricearchive.org/aliexpress.com/item/1005013110936399","title":"AliExpress item pointer for LolliClip SE","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S23","url":"https://www.ebay.de/itm/307023825201","title":"EDIFIER LolliClip SE - eBay.de","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S24","url":"https://post.smzdm.com/p/a26z6722/","title":"LolliClip SE 使用体验","published_at":"2026-08-18","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S25","url":"https://www.edifier.com/cn/product/product-807.html","title":"EDIFIER Comfo Clip Q","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S26","url":"https://mall-pc.edifierstore.com/goods/scene?displayCategoriesId=60","title":"EDIFIER official store Comfo Clip Q","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},
    {"source_id":"S27","url":"https://couponsfromchina.com/edifier-comfo-clip-q-ows-earbuds/","title":"Comfo Clip Q secondary overseas pointer","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K05"]},
    {"source_id":"S28","url":"https://bbs.bee-link.com/d/4783-ser-series-driver-and-bios-download/519","title":"Beelink SER8 8745HS BIOS discussion","published_at":null,"retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S29","url":"https://bbs-pc.edifier.com/product/40158","title":"EDIFIER Lolli Pro SE community page","published_at":null,"retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K08"]},
    {"source_id":"S30","url":"https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf","title":"Federal Register 91 FR 37789 - Indefinite Suspension of the De Minimis Exemption","published_at":"2026-06-24","retrieved_at":"2026-10-06","source_type":"government","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"S31","url":"https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0","title":"CBP CSMS #69183472 postal low-value entry guidance","published_at":"2026-07-08","retrieved_at":"2026-10-06","source_type":"government","access_state":"read_full_page","claims_supported":["K06"]},
    {"source_id":"S32","url":"https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search","title":"USTR Section 301 tariff search guidance","published_at":null,"retrieved_at":"2026-10-06","source_type":"government","access_state":"read_full_page","claims_supported":["K07"]}
  ],
  "claims": [
    {"claim_id":"K01","claim":"All 9 frozen SKUs were retained; frozen head_status_verified is true for 6 and false for 3; exact_variant_verified is true for all 9.","classification":"FACT","source_ids":[],"confidence":"high","counterevidence":"None observed; frozen metadata preserved without upgrade."},
    {"claim_id":"K02","claim":"Post-freeze ordinary public/model-level prices were directly observable for C04-S03 CNY2049, C05-S02 CNY599, C05-S03 CNY3499, C06-S01 CNY249, and C06-S03 CNY289; C06-S02 had a CNY499 MSRP/reference price.","classification":"FACT","source_ids":["S03","S13","S15","S17","S20","S26"],"confidence":"medium","counterevidence":"Some prices are model-level rather than color-specific checkout prices; logged-in/coupon/final-to-hand prices were not inferred."},
    {"claim_id":"K03","claim":"Two directly opened overseas listings support A-bucket item-price observations: Samsung MZ-V9S2T0BW at USD497.22 and Xiaomi BE6500 at USD147.51; neither establishes complete delivered cost to ZIP10001.","classification":"FACT","source_ids":["S08","S09","S14"],"confidence":"medium","counterevidence":"Destination-specific delivery/import charges were not fully exposed."},
    {"claim_id":"K04","claim":"No B-bucket same-OEM/rebrand match was established.","classification":"FACT","source_ids":[],"confidence":"high","counterevidence":"Visual/spec similarity was intentionally not treated as OEM proof."},
    {"claim_id":"K05","claim":"Several cheaper-looking overseas pages were downgraded to C or rejected because region, bundle, capacity, color, or exact variant did not match the frozen SKU.","classification":"FACT","source_ids":["S05","S06","S10","S18","S21","S23","S27"],"confidence":"high","counterevidence":"A later exact-region/exact-bundle source could change individual classifications."},
    {"claim_id":"K06","claim":"As of 2026-10-06 the former general USD800 de minimis treatment cannot be assumed for these imports; current mode-specific entry requirements must be considered.","classification":"FACT","source_ids":["S30","S31"],"confidence":"high","counterevidence":"Specific entry treatment still depends on mode and shipment facts."},
    {"claim_id":"K07","claim":"A Section 301 determination requires the applicable HTS classification; no fixed rate was imputed for unclassified SKUs.","classification":"FACT","source_ids":["S32"],"confidence":"high","counterevidence":"A broker/CBP classification could later establish SKU-specific rates."},
    {"claim_id":"K08","claim":"Community evidence was used only for compatibility/experience signals, not for transaction price, OEM identity, or market-share inference.","classification":"FACT","source_ids":["S24","S28","S29"],"confidence":"high","counterevidence":"None."}
  ],
  "observations": [
    {
      "sku_id":"C04-S01","category_id":"C04","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"JD","url":"https://item.jd.com/100293974227.html","seller_id":null,"item_id":"100293974227","match_bucket":"A","match_evidence":"Frozen exact JD item URL; current page was a dynamic/page shell and no current price was extracted.","region_variant":"CN","currency":"CNY","price":null,"delivery_price":null,"price_type":null,"access_state":"page_shell","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S01"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No live freight/customs quote; de minimis not assumed."},
        {"architecture":"consolidated_marginal","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No 1000-order business quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No physical-bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["current public CN transaction price","convenient overseas exact offer","domestic shipping","agent fee","weight/dimensions","international freight","HTS","MFN/301/other duty","mandatory clearance charges","FX"],
      "evidence_status":"EVALUATED; exact frozen listing retained; current price and landed economics unverified"
    },
    {
      "sku_id":"C04-S02","category_id":"C04","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"JD","url":"https://item.jd.com/10147548162123.html","seller_id":null,"item_id":"10147548162123","match_bucket":"A","match_evidence":"Frozen exact CN listing; current price inaccessible.","region_variant":"CN","currency":"CNY","price":null,"delivery_price":null,"price_type":null,"access_state":"page_shell","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S02"]},
        {"channel":"GMKtec US official","url":"https://www.gmktec.com/en/products/amd-ryzen%E2%84%A2-ai-max-395-evo-x2-ai-mini-pc","seller_id":"GMKtec","item_id":null,"match_bucket":"C","match_evidence":"EVO-X2 page exposes a 128GB+2TB option, but exact option price was not separately observable; US-plug/US-region configuration differs from frozen CN region.","region_variant":"US","currency":"USD","price":null,"delivery_price":null,"price_type":"public product page; exact option price unobserved","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S04","S05"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No live freight/customs quote."},
        {"architecture":"consolidated_marginal","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No 1000-order business quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No physical-bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["current CN price","exact US-region-equivalent price","delivery to ZIP10001","all landed-cost inputs"],
      "evidence_status":"EVALUATED; overseas same-model page found but exact region/option price insufficient for A"
    },
    {
      "sku_id":"C04-S03","category_id":"C04","sampling_stratum":"domestic_opportunity","head_status_verified":false,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"JD","url":"https://item.jd.com/product/T0XTZzdZIRILoxOTgqMUUA.html","seller_id":null,"item_id":null,"match_bucket":"A","match_evidence":"Exact SER8 8745HS, 深空灰, barebone with no RAM/SSD/OS.","region_variant":"CN","currency":"CNY","price":2049.0,"delivery_price":null,"price_type":"public_list_price; logged-in final price unavailable","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S03"]},
        {"channel":"Beelink US official","url":"https://us.bee-link.com/products/beelink-ser8-8745hs","seller_id":"Beelink","item_id":null,"match_bucket":"C","match_evidence":"Same base model and Space Gray, but US page offers populated 16GB+512GB/32GB+1TB configurations rather than frozen barebone bundle.","region_variant":"US","currency":"USD","price":619.0,"delivery_price":null,"price_type":"public_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S06"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":2049.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"Public item price only; no live logistics/import quote."},
        {"architecture":"consolidated_marginal","item_price":2049.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No marginal consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No business-volume quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No physical-bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["China domestic delivery","agent fee","weight/dimensions","international freight","HTS/duties","clearance","FX","exact-bundle overseas A offer"],
      "evidence_status":"EVALUATED; domestic A public list price observed; overseas offer is C because bundle differs"
    },
    {
      "sku_id":"C05-S01","category_id":"C05","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"JD","url":"https://item.jd.com/100144705326.html","seller_id":null,"item_id":"100144705326","match_bucket":"A","match_evidence":"Frozen exact domestic listing; current transaction price not exposed.","region_variant":"CN","currency":"CNY","price":null,"delivery_price":null,"price_type":null,"access_state":"page_shell","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S07"]},
        {"channel":"eBay","url":"https://www.ebay.com/itm/127946299185","seller_id":"Everydayideas","item_id":"127946299185","match_bucket":"A","match_evidence":"Exact Samsung part MZ-V9S2T0BW, matching Samsung China exact product code and 2TB variant.","region_variant":"MZ-V9S2T0BW; seller located US","currency":"USD","price":497.22,"delivery_price":null,"price_type":"public_new_item_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S08","S09"]},
        {"channel":"Newegg","url":"https://www.newegg.com/samsung-2tb-990-evo-plus-nvme-2-0/p/N82E16820147900?item=N82E16820147900","seller_id":"Newegg","item_id":"N82E16820147900","match_bucket":"C","match_evidence":"2TB/7250MB/s/PCIe 4.0 x4 or 5.0 x2 matches function/spec, but US part is MZ-V9S2T0B/AM rather than frozen BW regional part.","region_variant":"US /AM","currency":"USD","price":369.99,"delivery_price":0.0,"price_type":"public_price; page states free shipping but ZIP10001 not pinned","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S10"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"Domestic transaction price and import costs unresolved."},
        {"architecture":"consolidated_marginal","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No 1000-order business quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No bulk quote/classification."}
      ],
      "best_verified_convenient_offer":{"channel":"eBay","seller_id":"Everydayideas","item_id":"127946299185","match_bucket":"A","currency":"USD","item_price":497.22,"delivery_to_ZIP10001_verified":false,"landed_verified":false,"source_ids":["S08","S09"]},
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"observed_overseas_item_price":497.22,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"observed_overseas_item_price":369.99,"landed_total":null,"savings":null}],
      "missing_components":["current CN price","ZIP10001 delivery for A offer","domestic procurement costs","weight/dimensions","freight","HTS","MFN/301","clearance","FX"],
      "evidence_status":"EVALUATED; A-bucket overseas item price verified, but no A delivered or landed comparison"
    },
    {
      "sku_id":"C05-S02","category_id":"C05","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"Xiaomi official","url":"https://www.mi.com/micamera","seller_id":"Xiaomi","item_id":null,"match_bucket":"A","match_evidence":"Official current catalog identifies Xiaomi Router BE6500 with matching Wi-Fi 7/6500-class configuration.","region_variant":"CN","currency":"CNY","price":599.0,"delivery_price":null,"price_type":"public_official_catalog_price; no member/coupon/subsidy assumed","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S12","S13"]},
        {"channel":"eBay","url":"https://www.ebay.com/itm/396962723194","seller_id":"China Electronic Store","item_id":"396962723194","match_bucket":"A","match_evidence":"Exact Xiaomi Router BE6500 China-market model; no evidence of hardware substitution.","region_variant":"CN model exported from China","currency":"USD","price":147.51,"delivery_price":0.0,"price_type":"public_new_item_price; free-shipping label on page; mandatory import costs/ZIP-specific final delivery not established","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S14"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":599.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No live forwarder/customs quote."},
        {"architecture":"consolidated_marginal","item_price":599.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No marginal consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No volume business quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No physical-bulk quote or customs classification."}
      ],
      "best_verified_convenient_offer":{"channel":"eBay","seller_id":"China Electronic Store","item_id":"396962723194","match_bucket":"A","currency":"USD","item_price":147.51,"delivery_to_ZIP10001_verified":false,"landed_verified":false,"source_ids":["S14"]},
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"observed_overseas_item_price":147.51,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["China domestic shipping","agent fee","weight/dimensions","international freight","HTS/MFN/301","clearance","FX","ZIP10001 mandatory import treatment on overseas offer"],
      "evidence_status":"EVALUATED; A item prices observed on both sides but required delivered/landed components missing, so savings null"
    },
    {
      "sku_id":"C05-S03","category_id":"C05","sampling_stratum":"domestic_opportunity","head_status_verified":false,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"JD","url":"https://item.jd.com/product/xgX8EKW1Mrj5_OZ5EifFmQ.html","seller_id":null,"item_id":null,"match_bucket":"A","match_evidence":"Exact KINGBANK 银爵 32GB (16GBx2) DDR5-6000 国产颗粒 C36.","region_variant":"CN","currency":"CNY","price":3499.0,"delivery_price":null,"price_type":"public_list_price; final_to_hand_price_login_required","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S15"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":3499.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"Public list price only."},
        {"architecture":"consolidated_marginal","item_price":3499.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No 1000-order quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["exact overseas original seller page","domestic delivery","agent fee","weight/dimensions","freight","HTS/duties","clearance","FX"],
      "evidence_status":"EVALUATED; frozen public list price retained despite apparent outlier; no verified overseas counterpart"
    },
    {
      "sku_id":"C06-S01","category_id":"C06","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"EDIFIER official store","url":"https://www.edifierstore.com/home/search","seller_id":"EDIFIER","item_id":null,"match_bucket":"A","match_evidence":"Official store model-level Lolli Pro SE sale; official product page separately confirms 云岩白 exists. Color-specific checkout price not independently exposed.","region_variant":"CN","currency":"CNY","price":249.0,"delivery_price":null,"price_type":"public_model_level_sale_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S16","S17"]},
        {"channel":"Voptronics","url":"https://www.voptronics.com/edifier-lolli-pro-se.html","seller_id":"Voptronics","item_id":"V-LPSE","match_bucket":"C","match_evidence":"Exact model and in-stock status observed, but frozen 云岩白 color not verified.","region_variant":"cross-border","currency":"USD","price":47.90,"delivery_price":null,"price_type":"public_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S18"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":249.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"Contains battery; no battery surcharge or live freight quote observed."},
        {"architecture":"consolidated_marginal","item_price":249.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No battery-aware consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No volume quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No battery-aware physical bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"observed_overseas_item_price":47.90,"landed_total":null,"savings":null}],
      "missing_components":["exact-color overseas A offer","China delivery","battery shipping surcharge","weight/dimensions","freight","HTS/duties","clearance","FX"],
      "evidence_status":"EVALUATED; domestic model-level official sale observed; overseas same-model color-unverified offer is C"
    },
    {
      "sku_id":"C06-S02","category_id":"C06","sampling_stratum":"domestic_head","head_status_verified":true,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"EDIFIER official","url":"https://cnweb.edifier.com/cate-11.html","seller_id":"EDIFIER","item_id":null,"match_bucket":"A","match_evidence":"Official catalog identifies LolliClip SE; exact 云霜金 exists on official product page.","region_variant":"CN","currency":"CNY","price":499.0,"delivery_price":null,"price_type":"MSRP/reference_price; not verified transaction price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S19","S20"]},
        {"channel":"AliExpress","url":"https://www.aliexpress.us/item/1005013110936399.html","seller_id":null,"item_id":"1005013110936399","match_bucket":"A","match_evidence":"Secondary pointer identified a candidate exact-model item, but original seller page was blocked; no seller/price/spec claim taken from snippet or tracker.","region_variant":null,"currency":null,"price":null,"delivery_price":null,"price_type":null,"access_state":"blocked","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S21","S22"]},
        {"channel":"eBay.de","url":"https://www.ebay.de/itm/307023825201","seller_id":"GPUTopia_store","item_id":"307023825201","match_bucket":"C","match_evidence":"LolliClip SE model observed, but exact 云霜金 option and US destination delivery were not established.","region_variant":"EU marketplace/cross-border","currency":"EUR","price":99.99,"delivery_price":null,"price_type":"public_new_item_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S23"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"CNY499 is MSRP/reference only, not used as transaction item cost."},
        {"architecture":"consolidated_marginal","item_price":null,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No transaction item price or consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No 1000-order business quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No physical-bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"observed_overseas_item_price":99.99,"landed_total":null,"savings":null}],
      "missing_components":["current ordinary CN transaction price","accessible exact-color overseas A page","ZIP10001 delivery","battery surcharge","weight/dimensions","freight","HTS/duties","clearance","FX"],
      "evidence_status":"EVALUATED; MSRP retained as reference only; AliExpress original blocked and not inferred from secondary price tracker"
    },
    {
      "sku_id":"C06-S03","category_id":"C06","sampling_stratum":"domestic_opportunity","head_status_verified":false,"exact_variant_verified":true,"pre_freeze_mg_audit_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","pre_freeze_current_transaction_price_verified":false,
      "offers":[
        {"channel":"EDIFIER official store","url":"https://mall-pc.edifierstore.com/goods/scene?displayCategoriesId=60","seller_id":"EDIFIER","item_id":null,"match_bucket":"A","match_evidence":"Official store model-level Comfo Clip Q price; official product page confirms 奶霜白 exact color exists, though color-specific checkout price is not separately exposed.","region_variant":"CN","currency":"CNY","price":289.0,"delivery_price":null,"price_type":"public_model_level_sale_price","access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S25","S26"]},
        {"channel":"Banggood pointer","url":"https://couponsfromchina.com/edifier-comfo-clip-q-ows-earbuds/","seller_id":null,"item_id":null,"match_bucket":"C","match_evidence":"Only secondary pointer found; referenced gray configuration and original seller page was not independently verified, so no transaction price is used.","region_variant":"cross-border; color mismatch/unknown","currency":"USD","price":null,"delivery_price":null,"price_type":null,"access_state":"read_full_page","observed_at":"2026-10-06T16:23:00-07:00","source_ids":["S27"]}
      ],
      "landed_by_architecture":[
        {"architecture":"standalone","item_price":289.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"Battery product; no live logistics quote."},
        {"architecture":"consolidated_marginal","item_price":289.0,"item_currency":"CNY","china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No battery-aware consolidation quote."},
        {"architecture":"1000_independent_consumer_orders_business_price","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No volume quote."},
        {"architecture":"true_physical_bulk_import","item_price":null,"item_currency":null,"china_domestic_shipping":null,"agent_fee":null,"actual_weight_kg":null,"volumetric_weight_kg":null,"package_dimensions_cm":null,"packaging_fee":null,"battery_surcharge":null,"international_freight":null,"clearance_mandatory_charges":null,"hts_code":null,"mfn_rate":null,"section301_rate":null,"other_duty_rate":null,"fx_rate":null,"fx_source_id":null,"landed_total":null,"landed_currency":"USD","real_quote":false,"quote_assumptions":"No battery-aware bulk quote."}
      ],
      "best_verified_convenient_offer":null,
      "savings_by_bucket":[{"match_bucket":"A","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"B","overseas_delivered":null,"landed_total":null,"savings":null},{"match_bucket":"C","overseas_delivered":null,"landed_total":null,"savings":null}],
      "missing_components":["verified original overseas offer","China delivery","battery surcharge","weight/dimensions","freight","HTS/duties","clearance","FX"],
      "evidence_status":"EVALUATED; domestic model-level official price observed; secondary overseas pointer not promoted to verified price"
    }
  ],
  "coverage": {
    "assigned_sku_count": 9,
    "evaluated_sku_count": 9,
    "not_evaluated_sku_count": 0,
    "head_status_verified_true": 6,
    "head_status_verified_false": 3,
    "exact_variant_verified_true": 9,
    "post_freeze_ordinary_public_or_model_level_price_observations": 5,
    "additional_MSRP_only_observations": 1,
    "A_bucket_overseas_item_price_observations": 2,
    "B_bucket_matches": 0,
    "A_bucket_delivered_to_ZIP10001_verified": 0,
    "verified_landed_totals": 0,
    "verified_savings": 0,
    "GMV_weight_available": false,
    "ASP_weight_available": false,
    "demand_weighted_distribution_possible": false,
    "marketwide_distribution_claimed": false
  },
  "data_gaps": [
    "No SKU has all mandatory landed-cost components observed.",
    "No live standalone, consolidated-marginal, 1000-independent-order business, or true physical-bulk freight quote was obtained.",
    "Actual/volumetric weights and packaging dimensions were not consistently observable.",
    "SKU-specific auditable HTS classifications were not established; therefore MFN, Section 301 and other duty rates remain null rather than guessed.",
    "Current FY2027 entry/clearance mandatory charges were not imputed from earlier fiscal-year schedules.",
    "No common observed FX rate was applied because no complete landed calculation could be formed.",
    "US state/local sales or use tax is intentionally excluded from the comparison endpoint.",
    "C04-S01, C04-S02 and C05-S01 current domestic transaction prices remain unverified.",
    "C06-S02 has an MSRP/reference price but no verified ordinary transaction price.",
    "All source attestations in this batch await coordinator review."
  ],
  "coordinator_review_pending": true
}
```