审计结论：三份 W3 的核心保守结论成立——**本批 A/B/C 三桶均无可验证 landed savings**。四种物流架构（standalone、consolidated marginal、1000 独立消费者订单商务价、true physical bulk import）均未见完整真实报价；国内运费、agent fee、计费重/尺寸、国际运费、逐 SKU HTS、301/其他附加税、mandatory customs fees 任一缺失都足以使 landed numerator 无效，不能补 0，也不能把“商业折扣假设”当报价。CBP 当前规则继续暂停通常的 $800 de minimis；USTR 明确需先确定 HTS 才能判断传统中国 Section 301，2026 强迫劳动 301 又增加独立税层；178 项旧中国 301 排除目前延至 2026-11-10，但未证明本批任何 SKU 命中。[Federal Register](https://www.federalregister.gov/documents/2026/06/24/2026-12669/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry)

有两组需要明确纠正。第一，**C14-S02 SHEIN** 当前原页可读到 Li-Ning HALBERTEC/战戟5000、4U、单拍、未穿线、AYPT373，公开非会员价 **$125.70** 且有 Add to Cart；所以 W3-A 的 $107.43 已不是当前值，W3-B/C 的“当前无价/无美国 exact item-price endpoint”也已过时。但页面没有给 ZIP10001 运费，所以仍不能成为 delivered 分母。[SHEIN](https://us.shein.com/Li-Ning-HALBERTEC-5000-4U-Series-Badminton-Racket-High-Composite-Density-Shock-Absorption-System-Single-Racket-Unstrung-High-Rigidity-Carbon-Fiber-Weight-80-85g-Max-Stringing-Tension-30lbs-Model-AYPT373-p-133702364.html) 第二，**C15-S02 京东 A1 大陆版**的可访问别名页当前仍明确显示 **¥1599.00**，并写“登录查看到手价”；因此 W3-A 对公开展示价的观察得到支持，而 W3-B/C 的“当前中国普通数值价 0/9”需修正为至少 1/9。¥1599 不是最终成交价，国内送达/代理成本仍未知。[JD.com](https://item.jd.com/product/m6KOrJemUOxm_GPdewbV4w.html)

其余主要端点大体得到复核：B&H P2S Combo 当前 **$749、In Stock、PF004-U+SA007-US1、100–120VAC、Free Next Day Shipping**；A1 当前 **$299、PF002-A-US2、100–120VAC、Free 2-Day Shipping**。两者均是明确美国区硬件，只能作为 C 桶，不应冒充大陆 exact-A；公开页也未执行 ZIP10001 guest 地址报价，因此“免费配送”可观察，但不是我独立取得的 ZIP 特定 checkout quote。[B&H Photo Video](https://www.bhphotovideo.com/c/product/1940049-REG/bambu_lab_pf004_u_sa007_us1_p2s_combo.html/overview) Naturehike 灰/Standard Cloud Up Pro 2P 当前 **$159、available、20D、packed weight 1.53kg**，但 shipping calculated at checkout，且冻结 C14-S03 的中国聚合变体仍未锁。[Naturehike](https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent)

DDPAI MINI PRO 4K 当前 **$59 且 Sold out**；70mai M800 Front+Rear 当前 **$169.99**，不是 M800Pro，页面同时出现“shipping calculated at checkout”和“美国订单满 $99 免费配送”的一般政策，不能转成 ZIP10001 实报。[DDPAI Global](https://store.ddpai.com/products/mini-pro-4k) C13-S03 官方全球页只证明 Lite 2/TP10、12V、130 PSI；波兰官方店为 PLN189、有货，但“青春版2=Lite2/TP10”缺 OEM/料号跨区证明，所以 A 报告的 B 桶与 B 报告的 C 桶不能由当前材料裁决。[70mai](https://wwwpp.70mai.com/global/tp10/)

Creality VIP 当前 **$102.49 对应已选 EU Plug**；US Plug 仅能确认 item 4005010154 存在，不能把 $102.49 自动转写给 US。Creality 美国店另有 V2 Plus **$89、Sold Out**，是另一地区/库存快照，不应平均。[Creality VIP Mall](https://mvip.creality.com/en/goods/goodsDetail/2645) C15-S03 京东耗材榜当前仍列 Space Pi V2 Plus 大陆版 TOP2，并解析到 10164238923584，但 PDP 仍为壳；这不升级冻结 head 状态。[JD.com](https://www.jd.com/phb/key_67068e12f834fd813d8.html)

因此，本审计不改变 frozen SKU，也不把 provisional 样本并入 verified-head。三个 W3 的 **verified landed savings=0** 可保留；但单项当前价格覆盖必须按上述两处纠正。Fed H.10 的 2026-10-02 参考汇率确为 **6.7038 CNY/USD**，只可作为参考 FX，不能补齐缺失 landed 链。[Federal Reserve](https://www.federalreserve.gov/releases/h10/current/?cxd=36297_413305\&refid=36297\&utm_source=chatgpt.com)

```json
{
  "job_id": "R3-batch05",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "review_performed": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "audited_jobs": [
    "W3-A-batch05",
    "W3-B-batch05",
    "W3-C-batch05"
  ],
  "observation_audits": [
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C13-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Current 70mai page supports M800 Front+Rear USD169.99, not M800Pro; CN PDP is a shell and ZIP10001-specific delivery was not quoted.",
      "source_ids": ["S07", "S25"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C13-S02",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "DDPAI official page currently shows USD59 and Sold out; frozen 2026/360/no-card equivalence and ZIP10001 delivered endpoint remain unverified.",
      "source_ids": ["S06", "S26"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C13-S03",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Lite 2/TP10 official specifications are verified, but no OEM/part-number crosswalk proves frozen CN 青春版2 equals the global TP10; B versus C bucket remains unresolved.",
      "source_ids": ["S08", "S09", "S27"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C14-S01",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "CN PDP remains a shell. A Peru retailer currently exposes NXZQU61017 at PEN699 but color is orange and fulfillment is Peru, not frozen red-gray/snow-skirt to ZIP10001.",
      "source_ids": ["S14", "S28"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C14-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Current SHEIN USA page shows USD125.70 for HALBERTEC 5000 4U single unstrung AYPT373, not USD107.43.",
      "caveat": "ZIP10001 shipping is not exposed, so current exact item price is not a delivered denominator.",
      "source_ids": ["S04", "S29"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C14-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Naturehike gray/Standard variant is currently USD159 and available with 20D materials; shipping is calculated at checkout and frozen CN variant mapping remains unresolved.",
      "source_ids": ["S05", "S30"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C15-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "B&H currently shows USD749, in stock, free next-day shipping, US1 and 100-120VAC; this is a regional C-bucket offer, not CN exact-A.",
      "source_ids": ["S02", "S31"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C15-S02",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "JD currently shows Mainland A1 public display CNY1599 with login required for final hand price; B&H US2 is USD299 with 100-120VAC and free 2-day shipping. Region mismatch prevents A.",
      "source_ids": ["S01", "S03", "S32"]
    },
    {
      "original_job_id": "W3-A-batch05",
      "sku_id": "C15-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "VIP Mall currently shows USD102.49 with EU Plug selected; US Plug item 4005010154 exists but its price association is not shown.",
      "source_ids": ["S10", "S12", "S13"]
    },

    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C13-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Current 70mai page confirms M800 Front+Rear USD169.99, but M800 is not M800Pro; no ZIP10001-specific quote was obtained.",
      "source_ids": ["S07", "S25"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C13-S02",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "DDPAI USD59/Sold out is current. eBay evidence supports USD106.99, Last one, Brand=Unbranded and delivery display to 27709, but its accessible snapshot is older and not ZIP10001.",
      "source_ids": ["S06", "S17", "S26"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C13-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Poland 70mai page currently shows TP10 PLN189 and available, but this is not a US convenient exact offer and CN-to-global identity remains unproved.",
      "source_ids": ["S08", "S09", "S27"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C14-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Equipak exposes NXZQU61017 at PEN699 and available, but the page specifies orange and Peru fulfillment; target red-gray/snow-skirt and ZIP10001 are not locked.",
      "source_ids": ["S14", "S28"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C14-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "SHEIN USA current page now exposes USD125.70 for the exact 4U single unstrung AYPT373 identity.",
      "caveat": "The report's statement that the opened SHEIN page exposes no current price is no longer current. ZIP10001 delivery remains unobserved.",
      "source_ids": ["S04", "S18", "S29"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C14-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Naturehike gray/Standard SKU 6927595777008 is currently available at USD159 with 20D materials; shipping remains checkout-only and frozen CN exact flag remains false.",
      "source_ids": ["S05", "S30"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C15-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "B&H USD749/In Stock/free next-day/US1/100-120VAC is current; CN price and complete landed stack remain absent.",
      "source_ids": ["S02", "S31"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C15-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "A current public JD alias page shows Mainland A1 display price CNY1599; therefore the report-level current-CN-numeric count cannot remain 0/9.",
      "caveat": "CNY1599 is only a public display price; JD says login is required for final hand price. B&H US2 remains a C-bucket USD299 offer.",
      "source_ids": ["S01", "S03", "S32"]
    },
    {
      "original_job_id": "W3-B-batch05",
      "sku_id": "C15-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "JD ranking currently shows Space Pi V2 Plus Mainland at TOP2 and resolves item 10164238923584, whose PDP remains a shell. VIP USD102.49 is selected EU Plug.",
      "source_ids": ["S10", "S12", "S13"]
    },

    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C13-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "M800 Front+Rear USD169.99 is current, but it is not frozen M800Pro and ZIP10001-specific delivered price was not quoted.",
      "source_ids": ["S07", "S25"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C13-S02",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "DDPAI USD59 Sold out is current; eBay evidence supports the title/Brand=Unbranded conflict and non-10001 destination, but is not a fresh ZIP10001 quote.",
      "source_ids": ["S06", "S17", "S26"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C13-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "No US convenient exact endpoint was verified. Global TP10 specifications and a Poland PLN189 offer exist but do not close the frozen exact/US-delivery comparison.",
      "source_ids": ["S08", "S09", "S27"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C14-S01",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "No US exact delivered endpoint was verified. Peru NXZQU61017 offer is orange and local to Peru; CN current ordinary price remains unavailable.",
      "source_ids": ["S14", "S28"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C14-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Current SHEIN USA page provides an exact item-price endpoint: USD125.70, HALBERTEC 5000 4U, single, unstrung, AYPT373.",
      "caveat": "It is still not a ZIP10001 delivered endpoint because shipping is not exposed.",
      "source_ids": ["S04", "S29"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C14-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Naturehike USD159, gray/Standard, available, 20D and 1.53kg packed weight are supported; frozen CN variant mapping remains provisional and shipping is checkout-only.",
      "source_ids": ["S05", "S30"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C15-S01",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Micro Center USD749.98/In Store Only observation is supported. Separately, B&H currently has a USD749 shippable US1 offer; snapshots are different offers and must not be averaged.",
      "source_ids": ["S02", "S15", "S31"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C15-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Current JD alias page shows Mainland A1 public display CNY1599; the report's current-CN-price-null statement is therefore no longer correct.",
      "caveat": "Final hand price remains login-gated. Bambu US official currently shows A1 from USD349, while B&H independently shows US2 at USD299; these are separate US offers and not averaged.",
      "source_ids": ["S01", "S03", "S16", "S32"]
    },
    {
      "original_job_id": "W3-C-batch05",
      "sku_id": "C15-S03",
      "status": "VERIFIED_WITH_CAVEAT",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Creality US currently shows V2 Plus USD89 Sold Out; JD ranking still shows Mainland V2 Plus TOP2 and resolved PDP remains a shell. No delivered exact pair exists.",
      "source_ids": ["S11", "S12", "S13"]
    }
  ],
  "claim_audits": [
    {
      "audit_id": "A01",
      "original_job_id": "W3-A-batch05",
      "claim": "C14-S02 SHEIN price USD107.43",
      "status": "CORRECTION_REQUIRED",
      "correction": "Current opened SHEIN page shows USD125.70.",
      "source_ids": ["S04"]
    },
    {
      "audit_id": "A02",
      "original_job_id": "W3-B-batch05",
      "claim": "SHEIN C14-S02 opened page exposes no current price",
      "status": "CORRECTION_REQUIRED",
      "correction": "Current page exposes USD125.70 and Add to Cart.",
      "source_ids": ["S04"]
    },
    {
      "audit_id": "A03",
      "original_job_id": "W3-C-batch05",
      "claim": "C14-S02 has no US convenient exact item-price endpoint",
      "status": "CORRECTION_REQUIRED",
      "correction": "Current SHEIN USA page is exact at item level, USD125.70; delivered ZIP10001 remains incomplete.",
      "source_ids": ["S04"]
    },
    {
      "audit_id": "A04",
      "original_job_id": "W3-B-batch05",
      "claim": "Current CN ordinary numeric price verified 0/9",
      "status": "CORRECTION_REQUIRED",
      "correction": "JD Mainland A1 alias page currently shows public display CNY1599, though final hand price is login-gated.",
      "source_ids": ["S01"]
    },
    {
      "audit_id": "A05",
      "original_job_id": "W3-C-batch05",
      "claim": "Current CN ordinary numeric price verified 0/9",
      "status": "CORRECTION_REQUIRED",
      "correction": "At least C15-S02 has current public display CNY1599; this is not a verified final transaction price.",
      "source_ids": ["S01"]
    },
    {
      "audit_id": "A06",
      "original_job_id": "W3-A-batch05",
      "claim": "B&H P2S USD749 and A1 USD299 with US regional power variants",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S02", "S03"]
    },
    {
      "audit_id": "A07",
      "original_job_id": "W3-A-batch05",
      "claim": "Naturehike gray/Standard Cloud Up Pro 2P USD159, available, 20D",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S05"]
    },
    {
      "audit_id": "A08",
      "original_job_id": "W3-A-batch05",
      "claim": "DDPAI MINI PRO 4K USD59 and Sold out",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S06"]
    },
    {
      "audit_id": "A09",
      "original_job_id": "W3-B-batch05",
      "claim": "70mai M800 Front+Rear USD169.99",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S07"]
    },
    {
      "audit_id": "A10",
      "original_job_id": "W3-A-batch05",
      "claim": "Creality VIP USD102.49 applies to selected EU Plug; US Plug price unobserved",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S10"]
    },
    {
      "audit_id": "A11",
      "original_job_id": "W3-C-batch05",
      "claim": "Creality US V2 Plus USD89 Sold Out",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S11"]
    },
    {
      "audit_id": "A12",
      "original_job_id": "ALL",
      "claim": "No verified landed savings under any of the four architectures",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S19", "S20", "S21", "S22", "S23"]
    }
  ],
  "sources": [
    {
      "source_id": "S01",
      "url": "https://item.jd.com/product/m6KOrJemUOxm_GPdewbV4w.html",
      "title": "JD Bambu Lab A1 Mainland",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q02"]
    },
    {
      "source_id": "S02",
      "url": "https://www.bhphotovideo.com/c/product/1940049-REG/bambu_lab_pf004_u_sa007_us1_p2s_combo.html/overview",
      "title": "B&H Bambu Lab P2S Combo US1",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q04"]
    },
    {
      "source_id": "S03",
      "url": "https://www.bhphotovideo.com/c/product/1946339-REG/bambu_lab_pf002_a_us2_a1_3d_multi_color_printer.html/overview",
      "title": "B&H Bambu Lab A1 US2",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q04"]
    },
    {
      "source_id": "S04",
      "url": "https://us.shein.com/Li-Ning-HALBERTEC-5000-4U-Series-Badminton-Racket-High-Composite-Density-Shock-Absorption-System-Single-Racket-Unstrung-High-Rigidity-Carbon-Fiber-Weight-80-85g-Max-Stringing-Tension-30lbs-Model-AYPT373-p-133702364.html",
      "title": "SHEIN USA Li-Ning HALBERTEC 5000 4U Unstrung AYPT373",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q03"]
    },
    {
      "source_id": "S05",
      "url": "https://www.naturehike.com/products/cloud-up-pro-2-person-ultralight-backpacking-tent",
      "title": "Naturehike Cloud Up Pro 2-Person",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q05"]
    },
    {
      "source_id": "S06",
      "url": "https://store.ddpai.com/products/mini-pro-4k",
      "title": "DDPAI MINI PRO 4K",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q06"]
    },
    {
      "source_id": "S07",
      "url": "https://70mai.store/products/4k-m800",
      "title": "70mai Dash Cam 4K M800",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q07"]
    },
    {
      "source_id": "S08",
      "url": "https://wwwpp.70mai.com/global/tp10/",
      "title": "70mai Air Compressor Lite 2 TP10",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q13"]
    },
    {
      "source_id": "S09",
      "url": "https://sklep.70mai.pl/pl/p/Przewodowy-kompresor-samochodowy-12V-70mai-TP10/490",
      "title": "70mai Poland TP10",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q13"]
    },
    {
      "source_id": "S10",
      "url": "https://mvip.creality.com/en/goods/goodsDetail/2645",
      "title": "Creality VIP Mall Space Pi V2 Plus",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q08"]
    },
    {
      "source_id": "S11",
      "url": "https://store.creality.com/products/creality-space-pi-filament-dryer-plus",
      "title": "Creality US Space Pi Filament Dryer V2 Plus",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q08"]
    },
    {
      "source_id": "S12",
      "url": "https://www.jd.com/phb/key_67068e12f834fd813d8.html",
      "title": "JD 3D Printing Consumables Ranking",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q12"]
    },
    {
      "source_id": "S13",
      "url": "https://item.jd.com/10164238923584.html",
      "title": "JD Space Pi V2 Plus Mainland PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": ["Q12"]
    },
    {
      "source_id": "S14",
      "url": "https://www.equipak.pe/mobi-garden-carpa-2-personas-cold-mountain-plus/p",
      "title": "Equipak Mobi Garden Cold Mountain Plus NXZQU61017",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q14"]
    },
    {
      "source_id": "S15",
      "url": "https://www.microcenter.com/product/701917/p2s-combo-3d-printer",
      "title": "Micro Center Bambu Lab P2S Combo",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q15"]
    },
    {
      "source_id": "S16",
      "url": "https://bambulab-us.myshopify.com/collections/a1-series",
      "title": "Bambu Lab US A1 Series",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["Q16"]
    },
    {
      "source_id": "S17",
      "url": "https://www.ebay.com/itm/327051640726",
      "title": "eBay DDPAI MINI Pro 4K listing",
      "published_at": "2026-08-12",
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q17"]
    },
    {
      "source_id": "S18",
      "url": "https://www.shopnings.com/li-ning-halbertec-5000-3u-4u-badminton-racket-white-pearl-purple/",
      "title": "ShopNings Li-Ning Halbertec 5000 3U/4U",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["Q18"]
    },
    {
      "source_id": "S19",
      "url": "https://www.federalregister.gov/documents/2026/06/24/2026-12669/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q09"]
    },
    {
      "source_id": "S20",
      "url": "https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search",
      "title": "USTR How to Navigate the Section 301 Tariff Process",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q10"]
    },
    {
      "source_id": "S21",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation",
      "title": "USTR Extends 178 China Section 301 Exclusions",
      "published_at": "2025-11-26",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q10"]
    },
    {
      "source_id": "S22",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-takes-action-forced-labor-section-301-investigations",
      "title": "USTR Takes Action in Forced Labor Section 301 Investigations",
      "published_at": "2026-07-23",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q10"]
    },
    {
      "source_id": "S23",
      "url": "https://www.usitc.gov/harmonized_tariff_information/hts/archive/list",
      "title": "USITC HTS Archive 2026 Revision 20",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q10"]
    },
    {
      "source_id": "S24",
      "url": "https://www.federalreserve.gov/releases/h10/current/",
      "title": "Federal Reserve H.10 October 5 2026",
      "published_at": "2026-10-05",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["Q11"]
    },
    {
      "source_id": "S25",
      "url": "https://item.jd.com/100357791508.html",
      "title": "JD C13-S01 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S26",
      "url": "https://item.jd.com/100323403254.html",
      "title": "JD C13-S02 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S27",
      "url": "https://item.jd.com/100421361642.html",
      "title": "JD C13-S03 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S28",
      "url": "https://item.jd.com/1328287.html",
      "title": "JD C14-S01 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S29",
      "url": "https://item.jd.com/100105223480.html",
      "title": "JD C14-S02 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S30",
      "url": "https://item.jd.com/100216295221.html",
      "title": "JD C14-S03 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S31",
      "url": "https://item.jd.com/100285504398.html",
      "title": "JD C15-S01 PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    },
    {
      "source_id": "S32",
      "url": "https://item.jd.com/10093039784165.html",
      "title": "JD C15-S02 numeric-ID PDP",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "page_shell",
      "claims_supported": []
    }
  ],
  "claims": [
    {
      "claim_id": "Q01",
      "claim": "No assigned SKU has a verified landed total or verified landed savings under any of the four shipping architectures.",
      "source_ids": []
    },
    {
      "claim_id": "Q02",
      "claim": "C15-S02 Mainland A1 currently exposes a public CNY1599 display price, while final hand price is login-gated.",
      "source_ids": ["S01"]
    },
    {
      "claim_id": "Q03",
      "claim": "C14-S02 SHEIN USA currently shows USD125.70 for HALBERTEC 5000 4U single unstrung AYPT373, but ZIP10001 shipping is not exposed.",
      "source_ids": ["S04"]
    },
    {
      "claim_id": "Q04",
      "claim": "B&H currently shows P2S Combo US1 at USD749 and A1 US2 at USD299, with US-region 100-120VAC power specifications and public free-shipping labels.",
      "source_ids": ["S02", "S03"]
    },
    {
      "claim_id": "Q05",
      "claim": "Naturehike gray/Standard Cloud Up Pro 2P is currently USD159 and available, with 20D materials and approximately 1.53kg packed weight; shipping is calculated at checkout.",
      "source_ids": ["S05"]
    },
    {
      "claim_id": "Q06",
      "claim": "DDPAI MINI PRO 4K is currently USD59 and Sold out.",
      "source_ids": ["S06"]
    },
    {
      "claim_id": "Q07",
      "claim": "70mai M800 Front+Rear is currently USD169.99; it is not M800Pro and no ZIP10001-specific quote was obtained.",
      "source_ids": ["S07"]
    },
    {
      "claim_id": "Q08",
      "claim": "Creality VIP USD102.49 is shown with EU Plug selected; the US Plug item number exists but that price is not tied to it. Creality US separately shows V2 Plus USD89 Sold Out.",
      "source_ids": ["S10", "S11"]
    },
    {
      "claim_id": "Q09",
      "claim": "The ordinary Section 321(a)(2)(C) de minimis administrative exemption is suspended; applicable duties, taxes, fees and entry requirements therefore cannot be presumed zero.",
      "source_ids": ["S19"]
    },
    {
      "claim_id": "Q10",
      "claim": "SKU-level HTS classification is required before applying China Section 301 rates/exclusions; 178 exclusions run through 2026-11-10, and 2026 forced-labor Section 301 actions add another potentially relevant layer.",
      "source_ids": ["S20", "S21", "S22", "S23"]
    },
    {
      "claim_id": "Q11",
      "claim": "Federal Reserve H.10 reports 6.7038 CNY per USD for 2026-10-02; it is a reference rate, not a payment-channel FX quote.",
      "source_ids": ["S24"]
    },
    {
      "claim_id": "Q12",
      "claim": "JD currently lists Space Pi V2 Plus Mainland as TOP2 on the 3D-printing-consumables ranking and resolves to item 10164238923584, whose PDP remains a shell.",
      "source_ids": ["S12", "S13"]
    },
    {
      "claim_id": "Q13",
      "claim": "70mai global confirms Lite 2/TP10 at 12V and 130 PSI; Poland store currently lists TP10 at PLN189 and available, but this does not prove frozen CN-to-global exact equivalence.",
      "source_ids": ["S08", "S09"]
    },
    {
      "claim_id": "Q14",
      "claim": "Equipak exposes Mobi Garden NXZQU61017 at PEN699 and available, but the page identifies orange color and Peru delivery context.",
      "source_ids": ["S14"]
    },
    {
      "claim_id": "Q15",
      "claim": "Micro Center currently exposes P2S Combo at USD749.98 and In Store Only.",
      "source_ids": ["S15"]
    },
    {
      "claim_id": "Q16",
      "claim": "Bambu Lab US official A1 collection currently shows A1 from USD349.",
      "source_ids": ["S16"]
    },
    {
      "claim_id": "Q17",
      "claim": "The inspected eBay DDPAI listing shows USD106.99, Last one, Brand=Unbranded and a delivery estimate to ZIP27709 rather than 10001.",
      "source_ids": ["S17"]
    },
    {
      "claim_id": "Q18",
      "claim": "ShopNings currently shows HALBERTEC 5000 3U/4U at USD139.99 and in stock, but the displayed price is not locked to a specific 4U/unstrung selector state.",
      "source_ids": ["S18"]
    }
  ],
  "data_gaps": [
    "No complete real quote was found for standalone, consolidated marginal, 1000 independent consumer orders business pricing, or true physical bulk import for any assigned SKU.",
    "ZIP10001-specific guest shipping was not independently obtained for SHEIN, Naturehike, Creality VIP, 70mai, eBay, Equipak, or ShopNings; generic free-shipping labels are not treated as ZIP-specific quotes.",
    "Most China PDPs remain page shells; only C15-S02 currently exposes a public numeric display price through an alternate JD page, and its final hand price remains login-gated.",
    "China domestic shipping, agent fees, chargeable weight/dimensions, export packing or battery surcharges, and real international freight remain incomplete across the sample.",
    "Per-SKU final HTS classification, legacy China Section 301 applicability, 2026 forced-labor Section 301 applicability, exclusions, and mandatory customs/broker charges remain unresolved.",
    "No missing freight, dimensions, fees, duties, customs charges or FX spreads were set to zero.",
    "Verified-head and frozen exact-variant flags were not upgraded from current post-freeze browsing; C14-S03 remains provisional for exact mapping.",
    "Different retailer, region, date, stock-state and fulfillment snapshots were not averaged."
  ]
}
```