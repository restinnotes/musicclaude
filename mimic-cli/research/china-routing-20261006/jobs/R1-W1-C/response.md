## R1-W1-C 独立来源审计结论

**总体结论：W1-C 的方法论主张“不要强做 18 类精确排序”仍成立，但不能判为 all claims verified。** 我实际打开并核对了原报告的政府、行业、品牌研究及论坛页面。Census 顶层基线可以通过：Q2 2026 经季调美国电商销售 $340.2B、总零售 $1,986.5B、占比 17.1%，同比分别 +12.2% 与 +6.7%；同一页面也明确写明自 2026-09-28 起该稿“不再包含最新估计”，修订要等 11 月发布。E-Stats FAQ 也确实说明独立电商部门可能归 NAICS 4541，因此 store-industry e-commerce ratio 不能直接当产品级线上渗透率。[Census.gov](https://www.census.gov/retail/ecommerce.html)

**最重要的数值修正有三项。** 当前 BEA/FRED 2025 annual vintage 显示 household appliances 是 **$89.344B**，不是报告 C10 的 $89.654B；household utensils 是 **$61.565B**，不是早期正文 $61.954B；motor vehicle parts & accessories 是 **$130.530B**，不是早期 $131.214B。后两项在 continuation 已改成当前值，但整份待审报告仍混用了不同 vintage。C16 Clothing & Footwear $559.768B、C01 telephone-related $35.942B、information-processing $326.628B、video/audio $92.593B、tools $61.557B 则与当前发布值一致；这些全部是 **PCE**，不能改名为产品零售 GMV。[FRED](https://fred.stlouisfed.org/series/DCLORC1A027NBEA)

**CIPA 是明确的 continuation 错误。** 原始早段称截至 2026-10-01 已有 2026 年 8 月数据是正确的；我打开原来的 `dc-2025.html`，其当前官方页面明确列出 10 月 1 日 August、9 月 1 日 July、8 月 3 日 June。因此 continuation 的 CL11/C12“只验证到 June 2026”必须纠正，不应继续列作 post-June data gap。CIPA 数据仍只是 production/shipment 体系，不能填美国 consumer retail GMV。[CIPA](https://www.cipa.jp/e/stats/dc-2025.html)

**行业金额可以保留，但必须重贴口径标签。** Toy Association 的 $45.6B 是 Circana Checkout **projected to 100% of market** 的总市场估计，而 $30.3B 是 Retail Tracking Services 覆盖约 **68%** 市场的追踪 panel，两者不是两个可平均的市场规模。OIA 的 $28B 是 2024 outdoor retail universe，并明确覆盖 chain、e-commerce、specialty，且包含 apparel/footwear，与 C16 交叉。SEMA 的 $52.92B 可确认是 2025 accessory/performance-parts sales/consumer spending 量级且约四分之一车主购买，但公开摘要不足以把它严格改写成统一定义的“全市场 retail GMV”；更重要的是 SEMA 自己的报告索引页存在一处把 2026 Report 说明成 2024、另外两处说 2025 的内部文案冲突，应保留年份 caveat。[The Toy Association](https://www.toyassociation.org/ta/toys/research-and-data/data/us-sales-data.aspx)

科技部分最需要降级的是 **Counterpoint**。原报告引用的 smartphone market-share 和 sales 页面当前均只有标题、日期和空的 “Summary” 页面壳；页面正文没有 54%/30%/11%、shipments +6% 等数字。搜索摘要即使出现这些数字，也不符合本审计的全文核验规则，所以 CL05 及 C01 的这些字段保持 **UNVERIFIED_PAGE_SHELL**。相较之下，IDC 的美国 tablet shipments -31.6%、Omdia 的 PC shipments +1.0% / revenue +13.1% / sell-in ASP >$1,000，以及 Circana 年初的 $112B technology revenue forecast 都能从正文核到，但分别属于 shipment、sell-in/revenue 和 forecast，不能互换为消费者 sell-through。CTA 页面也确实说明 200+ 产品数据包含 shipments、**wholesale revenues**、average wholesale prices、household penetration，实际报告会员登录/非会员 $2,000，不能用公开 landing page 补付费数值。[Counterpoint Research](https://counterpointresearch.com/sitemap.html/insights/us-smartphone-market-share)

18 类的交叉重复足以阻止直接权重化：C02/C03/C04/C05/C07 共用 information-processing 上层桶；C06 的 video+audio 明显宽于 portable audio；C10 与 C17 同时落入 Home/household 宽桶；C14 的 apparel/footwear 与 C16 重叠；C13 SEMA 是 BEA motor-parts 大桶中的 specialty 子集；C18 toy universe 又不能覆盖全部 official merchandise；C15 与 toy/craft/electronics 边界天然交叉。论坛方面，我实际打开了 buildapc 评论和 3D-printing purchase-advice megathread，确有多零售商比较及持续选购讨论，但它们只是 self-selected community evidence，不能量化 GMV、SKU fragmentation 或 demand weight。

**对最终排序的影响：** C16 是巨型消费池、C13/C18/C14 为数百亿美元量级这一“粗粒度量级判断”仍可保留，但不是严格 apples-to-apples 排名；其余类别不能因缺数据被排在后面。下一轮若要形成 Y-axis，应先取得同一年、同产品 taxonomy 的 consumer retail/sell-through GMV，并建立 PCE↔retail、wholesale↔retail、shipment↔sell-through crosswalk；在此之前，报告提出的“缺 GMV 则 demand score=null、proxy 不相加、fragmentation 不进入支出权重”比强制 1–18 排名更可靠。

```json
{
  "job_id": "R1-W1-C",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "audited_job_id": "W1-C",
  "input_report_sha256": "489e916b8e9646e4317a6db3d9ae052966d673c8c8dd9777edef9c1346da34ba",
  "review_performed": true,
  "all_claims_verified": false,
  "claim_audits": [
    {
      "original_claim_id": "CL01",
      "original_source_ids": ["S01"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Census confirms Q2 2026 adjusted e-commerce $340.2B, total retail $1,986.5B, share 17.1%, e-commerce YoY +12.2% and total retail +6.7%. The page also says the release no longer contains the latest estimates as of 2026-09-28 and will be revised with Q3.",
      "source_ids": ["S01"]
    },
    {
      "original_claim_id": "CL02",
      "original_source_ids": ["S02"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Census FAQ explicitly describes separate e-commerce divisions being classified in NAICS 4541 rather than the brick-and-mortar store industry. The FAQ is a 2021-revised methodology page, not a current product-level penetration dataset.",
      "source_ids": ["S02"]
    },
    {
      "original_claim_id": "CL03",
      "original_source_ids": ["S03", "S21", "S22", "S23"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "The cited magnitudes are supportable, but C16 is BEA PCE, C13 is specialty-auto industry sales/consumer spending, C18 $45.6B is a projected-to-100%-of-market estimate, and C14 is 2024 outdoor retail. Only coarse scale comparison is defensible.",
      "source_ids": ["S03", "S21", "S22", "S23"]
    },
    {
      "original_claim_id": "CL04",
      "original_source_ids": ["S12"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Circana states a 2026 U.S. consumer-technology revenue forecast of $112B, computers adding more than $600M and tablets more than $200M versus 2025. These are January forecasts, not realized sales.",
      "source_ids": ["S12"]
    },
    {
      "original_claim_id": "CL05",
      "original_source_ids": ["S13", "S14"],
      "status": "UNVERIFIED_PAGE_SHELL",
      "supported": null,
      "correction": null,
      "caveat": "The cited Counterpoint pages currently expose titles/date and an empty Summary shell but not the numerical body needed to verify shipments +6%, sales -5%, or the vendor shares. Search snippets were not accepted as evidence.",
      "source_ids": ["S13", "S14"]
    },
    {
      "original_claim_id": "CL06",
      "original_source_ids": ["S15"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Omdia confirms Q2 2026 U.S. PC shipments excluding tablets of 18.8M, +1.0% YoY, revenue +13.1%, and average PC sell-in price above $1,000. This is PC channel/sell-in evidence, not laptop-only consumer retail.",
      "source_ids": ["S15"]
    },
    {
      "original_claim_id": "CL07",
      "original_source_ids": ["S16", "S12"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "IDC confirms U.S. tablet shipments -31.6% YoY in Q2 2026. It is valid contrary directional evidence to Circana's early revenue forecast, but shipment units and revenue are different metrics and are not a same-metric contradiction.",
      "source_ids": ["S16", "S12"]
    },
    {
      "original_claim_id": "CL08",
      "original_source_ids": ["S18"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "CTA's public landing page confirms 200+ U.S. products/services and fields including shipment volumes, wholesale revenues, average wholesale prices and household penetration. Actual report data require member login or $2,000 nonmember purchase.",
      "source_ids": ["S18"]
    },
    {
      "original_claim_id": "CL09",
      "original_source_ids": ["S20"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Circana confirms the 2026 U.S. Home forecast of $43.7B, +2.9%, while unit demand remains pressured. It is a forecast universe overlapping C10 and C17, not either target category's exact GMV.",
      "source_ids": ["S20"]
    },
    {
      "original_claim_id": "CL10",
      "original_source_ids": ["S24"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Circana confirms H1 2026 toy dollars +17%, units +12%, ASP +4%, and licensed toys at 39% of sales. Trading cards and collectibles were material growth drivers.",
      "source_ids": ["S24"]
    },
    {
      "original_claim_id": "CL11",
      "original_source_ids": ["S25"],
      "status": "CORRECTION_REQUIRED",
      "supported": false,
      "correction": "As of 2026-10-06, the CIPA official page explicitly states that August 2026 digital-camera statistics became available on 2026-10-01; July was posted 2026-09-01 and June 2026-08-03.",
      "caveat": "CIPA remains a production/shipment source and does not establish U.S. consumer retail GMV.",
      "source_ids": ["S25"]
    },
    {
      "original_claim_id": "CL12",
      "original_source_ids": ["S01", "S02", "S18"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "The audit independently confirms severe missing-data and metric-comparability problems. A numeric 1-18 ranking is not justified from the cited public evidence; authenticated product-level data could change that conclusion.",
      "source_ids": ["S01", "S02", "S18"]
    },
    {
      "original_claim_id": "C01",
      "original_source_ids": ["S04", "S13", "S14"],
      "status": "UNVERIFIED_PAGE_SHELL",
      "supported": null,
      "correction": null,
      "caveat": "BEA/ALFRED verifies the 2025 $35.942B telephone-and-related-communication-equipment PCE proxy. Counterpoint's cited pages do not currently expose the numerical body needed to verify +6% shipments, -5% sales, or Apple/Samsung/Motorola 54/30/11 shares.",
      "source_ids": ["S04", "S13", "S14"]
    },
    {
      "original_claim_id": "C02",
      "original_source_ids": ["S15", "S12", "S18"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "No laptop-only U.S. GMV is established. Omdia's 18.8M, +1.0% and >$1,000 ASP are PC sell-in measures; BEA information-processing $326.628B is a shared broad PCE bucket. Gartner's older Q1 2025 U.S. PC data also combine desktops and laptops.",
      "source_ids": ["S05", "S12", "S15", "S18", "S28"]
    },
    {
      "original_claim_id": "C03",
      "original_source_ids": ["S16", "S12"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "IDC verifies U.S. Q2 2026 tablet shipments -31.6% YoY. Circana's >$200M incremental-revenue statement is a January forecast; shipment units and forecast revenue cannot be averaged or substituted.",
      "source_ids": ["S16", "S12"]
    },
    {
      "original_claim_id": "C04",
      "original_source_ids": ["S16"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "IDC qualitatively identifies low-cost mini-PCs/laptops as competition at the sub-$200 tablet end. It supplies no clean U.S. mini-PC market-size measurement.",
      "source_ids": ["S16"]
    },
    {
      "original_claim_id": "C05",
      "original_source_ids": ["S05", "S18", "S26"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "The $326.628B information-processing figure is verified only as a broad shared PCE bucket spanning multiple target categories. CTA product data are gated; actual Reddit comments support multi-retailer shopping behavior but not market size or quantitative fragmentation.",
      "source_ids": ["S05", "S18", "S26", "S31"]
    },
    {
      "original_claim_id": "C06",
      "original_source_ids": ["S06"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "BEA verifies 2025 video-and-audio-equipment PCE of $92.593B, which is far broader than portable audio. Circana separately verifies wired-headphone +3% in 2025, roughly $15M incremental, wired ASP about $13 versus Bluetooth about $99, and True Wireless at 65% of headphone dollars.",
      "source_ids": ["S06", "S29"]
    },
    {
      "original_claim_id": "C07",
      "original_source_ids": ["S18", "S26"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "CTA confirms Accessories among forecast categories but product values are gated. Reddit comments show multi-retailer enthusiast purchasing, not U.S. peripheral GMV or SKU concentration.",
      "source_ids": ["S18", "S26", "S31"]
    },
    {
      "original_claim_id": "C08",
      "original_source_ids": ["S17"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Circana confirms more than 1.3M fitness trackers purchased Jan-Jul 2025, revenue +88%, smart-ring revenue $217M, traditional wrist-tracker units -6%, smart-ring units +195%, and smart-ring ASP nearly four times wrist trackers. This is not the full wearables/smartwatch universe.",
      "source_ids": ["S17"]
    },
    {
      "original_claim_id": "C09",
      "original_source_ids": ["S19", "S18"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "CTA's public article supports the statement that four of the five fastest-growing technology products are smart-home products. It does not establish target-category GMV, online share, or a unified concentration measure.",
      "source_ids": ["S19", "S18"]
    },
    {
      "original_claim_id": "C10",
      "original_source_ids": ["S07", "S20"],
      "status": "CORRECTION_REQUIRED",
      "supported": null,
      "correction": "Use 2025 BEA household-appliances PCE of $89.344B, not $89.654B. Keep Circana's $43.7B 2026 Home forecast separate; the two universes are not additive.",
      "caveat": "Circana does verify robotic-vacuum dollar-sales forecast +9.1%. Its replacement percentages are shares among recent purchasers in the cited survey, not annual category purchase frequencies.",
      "source_ids": ["S07", "S20"]
    },
    {
      "original_claim_id": "C11",
      "original_source_ids": ["S08"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "BEA verifies 2025 tools and equipment for house and garden PCE of $61.557B. The taxonomy includes garden equipment and is not equivalent to the target power/electronics/repair-tool category.",
      "source_ids": ["S08"]
    },
    {
      "original_claim_id": "C12",
      "original_source_ids": ["S25", "S18"],
      "status": "CORRECTION_REQUIRED",
      "supported": false,
      "correction": "Replace 'CIPA public page verified through June 2026' with 'CIPA official page lists data through August 2026, posted 2026-10-01.'",
      "caveat": "The underlying CIPA measures remain shipments/production rather than U.S. consumer retail GMV.",
      "source_ids": ["S25", "S18"]
    },
    {
      "original_claim_id": "C13",
      "original_source_ids": ["S21", "S09"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": "For the broader BEA comparison use the current 2025 motor-vehicle-parts-and-accessories PCE value of $130.530B; the early-report $131.214B is not the current vintage.",
      "caveat": "SEMA supports $52.92B accessory/performance-parts sales and about one in four vehicle owners purchasing in 2025. The public wording supports consumer spending/sales but does not establish an apples-to-apples market-wide retail-GMV concept. SEMA's report index also contains one conflicting 2024 reference amid 2025 references.",
      "source_ids": ["S21", "S09"]
    },
    {
      "original_claim_id": "C14",
      "original_source_ids": ["S22"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "OIA verifies 2024 U.S. outdoor retail sales of $28B, +1%, with chain, e-commerce and specialty channels and apparel/footwear/equipment/accessories. It overlaps C16 apparel/footwear and supplies no public whole-category online share.",
      "source_ids": ["S22"]
    },
    {
      "original_claim_id": "C15",
      "original_source_ids": ["S27"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Actual 3D-printing purchase-advice megathreads are accessible and contain sustained shopping discussions. They cannot establish U.S. hobby/maker GMV, volume, ranking, or quantitative fragmentation.",
      "source_ids": ["S27", "S32"]
    },
    {
      "original_claim_id": "C16",
      "original_source_ids": ["S03"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "BEA/FRED verifies 2025 Clothing and Footwear PCE of $559.768B and 2024 $529.730B. It is consumer expenditure, not a retailer sales panel; bags are not fully represented and outdoor apparel/footwear overlaps C14.",
      "source_ids": ["S03"]
    },
    {
      "original_claim_id": "C17",
      "original_source_ids": ["S10", "S11", "S20"],
      "status": "CORRECTION_REQUIRED",
      "supported": null,
      "correction": "Use current 2025 household-utensils PCE of $61.565B, not the early-report $61.954B. The continuation's furniture/furnishings $291.665B is current. Do not add either to Circana Home or C10.",
      "caveat": "C10/C17 have substantial taxonomy overlap and the cited PCE proxies cover different product universes.",
      "source_ids": ["S10", "S11", "S20"]
    },
    {
      "original_claim_id": "C18",
      "original_source_ids": ["S23", "S24"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Toy Association verifies about $45.6B as Circana Checkout sales projected to 100% of the U.S. toy market and $30.3B as Retail Tracking Services covering about 68%. These are model-total and tracking-panel measures respectively, not interchangeable. Official merchandise outside toys remains excluded.",
      "source_ids": ["S23", "S24"]
    },
    {
      "original_claim_id": "FORUM-PC",
      "original_source_ids": ["S26"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Actual comments, not search snippets, mention Amazon, Newegg, Micro Center, B&H and Best Buy and discuss price, bundles and seller legitimacy. The self-selected enthusiast sample cannot quantify national channel fragmentation.",
      "source_ids": ["S26", "S31"]
    },
    {
      "original_claim_id": "FORUM-3D",
      "original_source_ids": ["S27"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "The cited purchase-advice megathreads contain substantive user discussion. They are evidence of community shopping activity only and have zero defensible weight for market-size estimation.",
      "source_ids": ["S27", "S32"]
    },
    {
      "original_claim_id": "METH01",
      "original_source_ids": [],
      "status": "UNVERIFIED_NOT_CHECKED",
      "supported": null,
      "correction": null,
      "caveat": "The proposed 70/15/10/5 demand formula is a normative preregistration choice, not an empirical claim that can be source-verified. The audit does support the accompanying discipline of keeping incompatible metrics and fragmentation separate.",
      "source_ids": []
    }
  ],
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.census.gov/retail/ecommerce.html",
      "title": "Quarterly Retail E-Commerce Sales",
      "published_at": "2026-08-18",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["CL01", "CL12"]
    },
    {
      "source_id": "S02",
      "url": "https://www.census.gov/programs-surveys/e-stats/about/faqs.html",
      "title": "E-Stats FAQs",
      "published_at": "2021-10-08",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["CL02", "CL12"]
    },
    {
      "source_id": "S03",
      "url": "https://fred.stlouisfed.org/series/DCLORC1A027NBEA",
      "title": "Personal consumption expenditures: Clothing and footwear",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["CL03", "C16"]
    },
    {
      "source_id": "S04",
      "url": "https://alfred.stlouisfed.org/series?seid=DTCERC1A027NBEA",
      "title": "PCE: Telephone and related communication equipment",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S05",
      "url": "https://alfred.stlouisfed.org/series?seid=DIPERC1A027NBEA",
      "title": "PCE: Information processing equipment",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C05"]
    },
    {
      "source_id": "S06",
      "url": "https://alfred.stlouisfed.org/series?seid=DVAARC1A027NBEA",
      "title": "PCE: Video and audio equipment",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S07",
      "url": "https://fred.stlouisfed.org/series/DAPPRC1A027NBEA",
      "title": "PCE: Household appliances",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C10"]
    },
    {
      "source_id": "S08",
      "url": "https://alfred.stlouisfed.org/series?seid=DTOORC1A027NBEA",
      "title": "PCE: Tools and equipment for house and garden",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S09",
      "url": "https://fred.stlouisfed.org/series/DMVPRC1A027NBEA",
      "title": "PCE: Motor vehicle parts and accessories",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C13"]
    },
    {
      "source_id": "S10",
      "url": "https://fred.stlouisfed.org/series/DUTERC1A027NBEA",
      "title": "PCE: Glassware, tableware, and household utensils",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C17"]
    },
    {
      "source_id": "S11",
      "url": "https://alfred.stlouisfed.org/series?seid=DFFFRC1A027NBEA",
      "title": "PCE: Furniture and furnishings",
      "published_at": "2026-09-30",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C17"]
    },
    {
      "source_id": "S12",
      "url": "https://www.circana.com/post/us-consumer-technology-sales-forecast-to-reach-112-billion-in-2026-reports-circana",
      "title": "US Consumer Technology Sales Forecast to Reach $112 Billion in 2026",
      "published_at": "2026-01-06",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL04", "CL07", "C02", "C03"]
    },
    {
      "source_id": "S13",
      "url": "https://counterpointresearch.com/sitemap.html/insights/us-smartphone-market-share",
      "title": "US Smartphone Market Share: Quarterly",
      "published_at": "2026-08-31",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S14",
      "url": "https://counterpointresearch.com/default.htm/insights/us-smartphone-sales-fall-5-percent-q2-2026",
      "title": "US Smartphone Sales Fall 5% YoY in Q2 2026",
      "published_at": "2026-08-13",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S15",
      "url": "https://omdia.tech.informa.com/pr/2026/sep/us-pc-shipments-grew-1point0percent-in-2q26-while-full-year-market-forecast-to-decline-10point7-percent",
      "title": "US PC shipments grew 1.0% in 2Q26",
      "published_at": "2026-09-09",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL06", "C02"]
    },
    {
      "source_id": "S16",
      "url": "https://www.idc.com/resource-center/blog/the-tablet-market-hits-a-wall/",
      "title": "The Tablet Market Hits a Wall",
      "published_at": "2026-08-13",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL07", "C03", "C04"]
    },
    {
      "source_id": "S17",
      "url": "https://www.circana.com/post/spending-on-fitness-trackers-grows-88-in-2025-circana-reports",
      "title": "Spending on Fitness Trackers Grows 88% in 2025",
      "published_at": "2025-09-18",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S18",
      "url": "https://www.cta.tech/research/cta-us-consumer-technology-one-year-industry-forecast-2022-2027-july-2026/",
      "title": "CTA U.S. Consumer Technology One-Year Industry Forecast, 2022-2027 (July 2026)",
      "published_at": "2026-06",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "login_required",
      "claims_supported": ["CL08", "CL12", "C02", "C05", "C07", "C09", "C12"]
    },
    {
      "source_id": "S19",
      "url": "https://www.cta.tech/articles/from-connected-to-intelligent-how-ai-is-transforming-the-smart-home/",
      "title": "From Connected to Intelligent: How AI Is Transforming the Smart Home",
      "published_at": "2026-07-21",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S20",
      "url": "https://www.circana.com/post/circana-forecasts-u-s-home-market-growth-as-consumers-invest-in-products-that-help-them-save-money",
      "title": "Circana Forecasts U.S. Home Market Growth",
      "published_at": "2026-09-24",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL09", "C10", "C17"]
    },
    {
      "source_id": "S21",
      "url": "https://www.sema.org/news-media/enews/2026/29/want-grow-your-aftermarket-business-start-2026-sema-market-report",
      "title": "Want to Grow Your Aftermarket Business? Start With the 2026 SEMA Market Report",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL03", "C13"]
    },
    {
      "source_id": "S22",
      "url": "https://outdoorindustry.org/2025-outdoor-retail-sales-trends-report/",
      "title": "2025 Outdoor Retail Sales Trends Report",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL03", "C14"]
    },
    {
      "source_id": "S23",
      "url": "https://www.toyassociation.org/ta/toys/research-and-data/data/us-sales-data.aspx",
      "title": "U.S. Sales Data",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL03", "C18"]
    },
    {
      "source_id": "S24",
      "url": "https://www.circana.com/post/us-toy-industry-posts-strongest-first-half-in-six-years-circana-reports",
      "title": "US Toy Industry Posts Strongest First Half in Six Years",
      "published_at": "2026-08-12",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["CL10", "C18"]
    },
    {
      "source_id": "S25",
      "url": "https://www.cipa.jp/e/stats/dc-2025.html",
      "title": "CIPA Digital Cameras Statistics",
      "published_at": "2026-10-01",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["CL11", "C12"]
    },
    {
      "source_id": "S26",
      "url": "https://www.reddit.com/r/buildapc/comments/1u5i1g1/where_to_source_parts_from/",
      "title": "Where to source parts from",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C07", "FORUM-PC"]
    },
    {
      "source_id": "S27",
      "url": "https://www.reddit.com/r/3Dprinting/comments/1ttj9ij/purchase_advice_megathread_june_2026/",
      "title": "Purchase Advice Megathread - June 2026",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C15", "FORUM-3D"]
    },
    {
      "source_id": "S28",
      "url": "https://www.gartner.com/en/newsroom/press-releases/2025-04-14-gartner-says-worldwide-pc-shipments-increased-4-point-8-percent-in-first-quarter-of-2025",
      "title": "Gartner Says Worldwide PC Shipments Increased 4.8% in First Quarter of 2025",
      "published_at": "2025-04-14",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S29",
      "url": "https://www.circana.com/post/wired-headphones-growth-is-a-throwback-to-2016",
      "title": "Wired Headphones Growth Is a Throwback to 2016",
      "published_at": "2026-02-25",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S30",
      "url": "https://www.cta.tech/research/2025-technology-lifecycle-consumer-ownership-upgrade-insights/",
      "title": "2025 Technology Lifecycle: Consumer Ownership & Upgrade Insights",
      "published_at": "2025-10",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "login_required",
      "claims_supported": []
    },
    {
      "source_id": "S31",
      "url": "https://www.reddit.com/r/buildapc/comments/1pmm4vt/where_to_buy_components/",
      "title": "Where to buy components",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C07", "FORUM-PC"]
    },
    {
      "source_id": "S32",
      "url": "https://www.reddit.com/r/3Dprinting/comments/1kc1pr8/purchase_advice_megathread_may_2025/",
      "title": "Purchase Advice Megathread - May 2025",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C15", "FORUM-3D"]
    }
  ],
  "claims": [],
  "data_gaps": [
    {
      "gap": "Product-based U.S. online GMV/share across all 18 categories",
      "reason": "Census 17.1% is aggregate retail and store-industry e-commerce classifications are not product-category penetration."
    },
    {
      "gap": "Clean same-year consumer retail/sell-through GMV, units and ASP for C01-C09 and C12",
      "reason": "Public evidence mixes PCE, forecast revenue, wholesale revenue, shipments and partial retail trackers."
    },
    {
      "gap": "Counterpoint Q2 2026 smartphone numerical claims from the cited primary pages",
      "reason": "Current cited URLs are page shells; search snippets were rejected as verification."
    },
    {
      "gap": "CTA product-level values",
      "reason": "Landing page exposes methodology/fields but the underlying product data require login or paid access and are wholesale-based."
    },
    {
      "gap": "SKU concentration and quantitative middle-tail fragmentation",
      "reason": "Forum comments establish shopping behavior only; category PCE and market totals cannot identify SKU concentration."
    },
    {
      "gap": "Non-overlapping crosswalk for all 18 categories",
      "reason": "C02/C03/C04/C05/C07 share information-processing; C10/C17 overlap Home; C14/C16 overlap apparel/footwear; C13 is a specialty subset; C18 omits non-toy merchandise; C15 crosses hobby/toy/electronics boundaries."
    },
    {
      "gap": "Canonical SEMA report-period wording",
      "reason": "SEMA's public 2026 report index contains inconsistent 2024 versus 2025 copy, although the summary article and multiple index locations support 2025."
    }
  ]
}
```