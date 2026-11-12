# 1. Direct answer

**W8-C 结论：结构性证据明显削弱 broad thesis，但尚不足以在 SKU freeze 前否定 narrow thesis。** 我没有选择任何国内 SKU，也没有检查任何具体 SKU 的 Amazon/AliExpress/Temu 价格或覆盖，符合 pre-freeze 约束。

最强反证有四条。第一，美国旧的 **<$800 de minimis 免税结构已经消失**。CBP 2026-06-24 规则确认无限期暂停邮政低值免税；FY2024 邮政 de-minimis entries 为 7,480 万件，而 2025-09—11 仅 725.5 万件，CBP 年化为 2,910 万件，即相对 FY2024 约低 **61%**。CBP 明确把下降与新增关税、de-minimis 暂停及临时邮政流程共同联系起来，并预计不会回到 2025 年前水平。URL：[https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf](https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf?utm_source=chatgpt.com) :chatgpt-content-reference{index="1"}

第二，**国际平台正在主动内生化中国供应链套利**。Alibaba 2026 20-F 称 AliExpress 覆盖 200+ 国家/地区、FY26 推出利用 30+ 国家库存的 AliExpressDirect；2026-06 季度公司又披露 AliExpress 已实现季度经营利润，原因包括物流优化和成本效率提升，本地供给销售占比继续显著上升。这不能证明 exact-SKU coverage 足够广，但强烈反驳“国际渠道不会持续压缩价差”。URL：[https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm](https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm?utm_source=chatgpt.com)；[https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm](https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm) :chatgpt-content-reference{index="4"}

第三，**buying-agent 路径不是本地零售等价物**：运费按实重/体积重、路线和品类变化；电池、电器、液体等受线路限制；Superbuy 条款把海关退运、延误、损失等国际物流风险大量留给用户，5 日无理由退换主要发生在中国仓库阶段。反证是 Taobao/Tmall/JD/1688 的标准采购服务费为 **0**，还能免费合包，所以“agent fee 本身必然吃掉套利”并不成立。URL：[https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/)；[https://www.superbuy.com/en/page/query/freight/](https://www.superbuy.com/en/page/query/freight/?htag=20pc-service5&htag=agt_home_recwords)；[https://www.superbuy.com/en/page/about/statementagreement/](https://www.superbuy.com/en/page/about/statementagreement/) :chatgpt-content-reference{index="8"}

第四，**数据入口存在平台依赖风险**。淘宝现行托管法律声明明确禁止未经许可通过机器人、蜘蛛等方式擅自获取/使用站内内容。因此未经授权的大规模抓取不是稳健基础设施。另一方面，AiPrice 等插件确实长期实现了跨 Amazon、1688、Taobao、AliExpress 的图搜/价格工具，说明匹配技术本身并非“不可能”。URL：[https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201908081411_65986.html](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201908081411_65986.html)；[https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj](https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj) :chatgpt-content-reference{index="11"}

**总体判断：**“中国国内 catalog 普遍存在巨大且稳定未套利价差”受到**中强度结构性反证**；“仍存在足够大的 China-head / US-middle-tail anomaly set”则**未被本 workstream 证伪**，因为证明或否定它必须等 domestic-first frozen sample 后做 exact-SKU landed-cost audit。

检索 UTC 窗口为 **2026-10-06T22:56:22Z–2026-10-06T23:00:37Z**。最新一手经营数据基准期为 **2026-06-30**（Alibaba 2026-08-20、PDD 2026-08-24 发布）；最新发现的平台法律公示为 **2026-09-30**、生效日 2026-10-07，因此本报告没有把尚未生效版本当成 10 月 6 日现行规则。

# 2. Evidence table

| Claim | Evidence | Date / URL | Counterevidence | Confidence |
|---|---|---|---|---|
| 旧 de-minimis 套利已被结构性削弱 | 74.8m FY2024 → 29.10m 年化状态口径，约 -61% | 2026-06-24；[https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf](https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf?utm_source=chatgpt.com) | 不是进口禁令；仍有新的 informal-entry 路径 | High |
| 关税不能用统一百分比 | USTR 要求按 HTS 判断 Section 301；178 项 exclusions 延至 2026-11-10 | 2025-11-26；[https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation](https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation?utm_source=chatgpt.com) | 某些 frozen SKU 可能税负低或获 exclusion | High |
| AliExpress 有持续压平价差的能力 | 200+ 国家、30+ 国家库存；2026-06 季度经营利润 | 2026-05-20/08-20；上述 SEC URLs | 不能推出 exact-SKU coverage | High / inference Medium |
| agent 物流会产生非线性成本 | 体积重=L×W×H/6000；敏感品路线限制 | 当前 Superbuy 页面；上述 URLs | 合包及去包装可降低成本 | High |
| 未授权 catalog 抓取有结构风险 | 淘宝法律声明禁止机器人/蜘蛛未经许可获取内容 | 现行托管声明；上述 URL | 授权/API/用户端工具可能规避此问题 | High |
| 这类 sourcing 工具并非没人做过 | AiPrice Chrome 扩展 100,000 users，2026-08-15 更新 | [https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj](https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj) | 目标用户主要是卖家/采购，不是完整 consumer landed-cost router | High |

# 3. Primary sources

CBP/Federal Register 是本报告最重要的 hard evidence；其经济分析还明确预计新增 duties/data requirements 会进一步压低进口量。PDD 自己也在 2025 年 20-F 中警告，取消 de minimis 可能导致消费者价格上涨、订单减少和 merchant participation 下降。URL：[https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm](https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm?utm_source=chatgpt.com) :chatgpt-content-reference{index="16"}

但截至 2026 Q2，PDD 整体收入仍同比增长 8%，说明政策冲击并未自动摧毁大型跨境平台；这也是对最强 bearish interpretation 的反证。URL：[https://www.sec.gov/Archives/edgar/data/1737806/000110465926100534/tm2623874d1_ex99-1.htm](https://www.sec.gov/Archives/edgar/data/1737806/000110465926100534/tm2623874d1_ex99-1.htm) :chatgpt-content-reference{index="18"}

# 4. Forum evidence

社区证据支持“物流既贵又不稳定”，但不能当市场统计。2026-04-17 一名 Sugargoo 美国用户报告约 6kg 估算运费 $180；相反，2026-09-21 一名 Superbuy 美国用户报告 duty-free air 路线约 35 天成功送达。两者共同说明**forwarding 仍能运作，但成本/时效离散度很大**。URLs：[https://www.reddit.com/r/Sugargoo/comments/1sobfm1/shipping_costs/](https://www.reddit.com/r/Sugargoo/comments/1sobfm1/shipping_costs/?utm_source=chatgpt.com)；[https://www.reddit.com/r/Superbuy/comments/1wmf8cy/third_superbuy_haul/](https://www.reddit.com/r/Superbuy/comments/1wmf8cy/third_superbuy_haul/?utm_source=chatgpt.com) :chatgpt-content-reference{index="21"}

AiPrice 自有论坛也出现 2026 年 1688 搜索突然失效、清 cookie/重新登录仍失败的反馈。这只是单点故障证据，却说明依赖第三方页面结构的匹配基础设施存在真实维护负担。URL：[https://www.aiprice.com/bbsforum/index.html?from=www_index&page=6](https://www.aiprice.com/bbsforum/index.html?from=www_index&page=6) :chatgpt-content-reference{index="23"}

# 5. Contrary evidence

最重要的反向证据是：**没有找到结构性事实证明 consumer China-direct route 已经失去经济可行性。** Superbuy 主流采购费为零、允许免费合包；美国转运在 2026 年仍实际发生；Section 301 需逐 HTS 判断且存在 exclusions；CBP 新规则是加税与加申报，不是禁止个人低值进口；AliExpress 的规模同样不能证明中国国内所有 head SKU 都已国际化。因此 W8-C 不能把“高摩擦”偷换成“无机会”。

# 6. Confidence

现行 de-minimis、CBP entry process、Section 301 分类要求、Superbuy 公示规则、淘宝 robot 条款：**High**。  
“这些因素显著缩小可套利 SKU 集合”：**Medium-High inference**。  
“它们足以否定 China-head / US-middle-tail opportunity”：**Low**，目前证据不足。

# 7. Data gaps

**AUTHENTICATED DATA REQUIRED：** 淘宝/Tmall/JD 登录态交易价、销量/排名、普通券与会员券差异。另缺 frozen SKU 后逐项 HTS、真实实重/体积重、美国线路实时 duty-paid quote、payment/FX/chargeback 成本、跨境退货实际损失率、Superbuy/Sugargoo 商务量价合同，以及淘宝/Tmall 授权 API/商业数据访问条件。任何这些缺口都没有用搜索 snippet 替代。

# 8. Most surprising finding

最意外的不是 de-minimis 消失本身，而是**两个方向同时成立**：CBP 数据显示旧低值包裹经济结构遭到巨大冲击；与此同时 AliExpress 已在 2026 年通过物流优化做到季度经营盈利并扩大本地供给。这意味着新产品不是在对抗一个静态价差，而是在与会主动吸收套利、优化物流的 incumbent 竞争。

# 9. What would falsify its own conclusion?

以下任一结果都会削弱本报告的 bearish 结论：① frozen domestic-head 样本中，高需求 SKU 有显著比例在真实 landed cost 后仍比 cheapest convenient overseas option 便宜 ≥20%；②这种优势在非轻小件上也稳定存在；③经纪/agent 可给出规模化、稳定的 duty-paid individual-parcel 商务价；④退货、欺诈、支付损失没有吃掉 savings；⑤存在合规、可持续的官方 catalog/API 数据路径，解除 scraping 单点风险。

# 10. Suggested next experiment

**唯一优先实验：冻结样本后的 blind landed-cost falsification audit。** 先锁定国内-first SKU universe/hash，再让独立研究者不得删样本地计算 China transaction price + domestic freight + agent + real volumetric freight + SKU-specific HTS/MFN/Section-301 + processing，并只在此后查询 AliExpress/Amazon/Temu/其他方便渠道。预先定义“若 demand-relevant exact-SKU 中很少有 ≥20% 优势，则 narrow thesis 失败”的判定阈值。这个实验能一次性区分“结构性摩擦很大”和“结构性摩擦已经把机会消灭”。

```json
{
  "job_id": "W8-C",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C03"]
    },
    {
      "source_id": "S02",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S03",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation",
      "title": "USTR Extends Exclusions from China Section 301 Tariffs",
      "published_at": "2025-11-26",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S04",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm",
      "title": "Alibaba Group Holding Limited 2026 Form 20-F",
      "published_at": "2026-05-20",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S05",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm",
      "title": "Alibaba June Quarter 2026 Results",
      "published_at": "2026-08-20",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S06",
      "url": "https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm",
      "title": "PDD Holdings Inc. 2025 Form 20-F",
      "published_at": "2026-04-29",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S07",
      "url": "https://www.sec.gov/Archives/edgar/data/1737806/000110465926100534/tm2623874d1_ex99-1.htm",
      "title": "PDD Holdings Announces Second Quarter 2026 Unaudited Financial Results",
      "published_at": "2026-08-24",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S08",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fee Structure",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S09",
      "url": "https://www.superbuy.com/en/page/query/freight/",
      "title": "Superbuy International Shipping Cost Estimator",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S10",
      "url": "https://www.superbuy.com/en/page/about/statementagreement/",
      "title": "Superbuy Glocalization Program Agreement",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S11",
      "url": "https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201908081411_65986.html",
      "title": "淘宝平台服务协议 / 淘宝网法律声明",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C10"]
    },
    {
      "source_id": "S12",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj",
      "title": "AiPrice(AliPrice) Search by Image for China Import",
      "published_at": "2026-08-15",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S13",
      "url": "https://www.aiprice.com/bbsforum/index.html?from=www_index&page=6",
      "title": "AiPrice Feedback Discussion Forum",
      "published_at": null,
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    },
    {
      "source_id": "S14",
      "url": "https://www.reddit.com/r/Sugargoo/comments/1sobfm1/shipping_costs/",
      "title": "Shipping Costs?! - r/Sugargoo",
      "published_at": "2026-04-17",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C13"]
    },
    {
      "source_id": "S15",
      "url": "https://www.reddit.com/r/Superbuy/comments/1wmf8cy/third_superbuy_haul/",
      "title": "Third Superbuy haul - r/Superbuy",
      "published_at": "2026-09-21",
      "retrieved_at": "2026-10-06T23:00:37Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C13"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "As of 2026-10-06, the U.S. de minimis administrative exemption for most low-value imports remains suspended; CBP's postal rule is in force.",
      "classification": "FACT",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "The policy is not an import ban; a new postal informal-entry process remains available, and some separate statutory exemptions survive."
    },
    {
      "claim_id": "C02",
      "claim": "CBP reports 74.8 million postal de-minimis entries in FY2024 versus 7,254,980 entries from September-November 2025, annualized to 29,099,645, about 61% below FY2024.",
      "classification": "FACT",
      "source_ids": ["S01"],
      "confidence": "high",
      "counterevidence": "CBP attributes the change to a combination of new duties, de minimis suspension and the interim mail process; the data do not isolate a single causal factor."
    },
    {
      "claim_id": "C03",
      "claim": "The removal of the old de minimis regime materially weakens the economics of very low-value direct-to-consumer arbitrage and raises data/compliance requirements.",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "High-margin lightweight goods may still retain sufficient spreads, and the new process still permits low-value imports."
    },
    {
      "claim_id": "C04",
      "claim": "China-related Section 301 duties cannot be modeled as one universal rate; liability depends on HTS classification and exclusions, with 178 exclusions extended into November 2026.",
      "classification": "FACT",
      "source_ids": ["S03"],
      "confidence": "high",
      "counterevidence": "Many HTS classifications remain subject to additional duties, so individual frozen SKUs may still face substantial tariff burden."
    },
    {
      "claim_id": "C05",
      "claim": "AliExpress has large-scale mechanisms capable of compressing China-to-overseas spreads: it covers more than 200 countries and regions, introduced AliExpressDirect using inventories in more than 30 countries, and reported operating profit in the June 2026 quarter driven partly by logistics optimization and cost efficiency.",
      "classification": "FACT",
      "source_ids": ["S04", "S05"],
      "confidence": "high",
      "counterevidence": "Scale, profitability and local inventory do not establish exact-SKU coverage of China-domestic head products or prove price parity."
    },
    {
      "claim_id": "C06",
      "claim": "PDD identifies de minimis removal as a risk that can increase consumer prices and reduce orders or merchant participation, but PDD's consolidated Q2 2026 revenue still grew 8% year over year.",
      "classification": "FACT",
      "source_ids": ["S06", "S07"],
      "confidence": "high",
      "counterevidence": "The Q2 financial results are consolidated and do not isolate Temu's U.S. economics."
    },
    {
      "claim_id": "C07",
      "claim": "Superbuy currently states that standard purchasing from Taobao, Tmall, JD and 1688 carries no purchasing service fee and that multiple items can be consolidated without a consolidation charge.",
      "classification": "FACT",
      "source_ids": ["S08"],
      "confidence": "high",
      "counterevidence": "International freight, customs, fuel/operation charges, payment costs and optional services remain separate costs."
    },
    {
      "claim_id": "C08",
      "claim": "Agent forwarding has structural logistics penalties: chargeable freight can use volumetric weight and batteries, appliances, liquids and other sensitive categories face route restrictions.",
      "classification": "FACT",
      "source_ids": ["S09", "S14"],
      "confidence": "high",
      "counterevidence": "Consolidation, package removal, vacuum packing and alternative routes can materially reduce some of these penalties."
    },
    {
      "claim_id": "C09",
      "claim": "Superbuy's published terms allocate substantial international logistics and customs risks to the user, and its no-reason return/exchange mechanism is principally a pre-international-shipment China-stage service.",
      "classification": "FACT",
      "source_ids": ["S10"],
      "confidence": "high",
      "counterevidence": "Insurance, claims assistance and re-delivery mechanisms can mitigate some losses."
    },
    {
      "claim_id": "C10",
      "claim": "Taobao's hosted legal statement prohibits unauthorized acquisition or use of platform content through robots, spiders or similar automated mechanisms.",
      "classification": "FACT",
      "source_ids": ["S11"],
      "confidence": "high",
      "counterevidence": "Authorized APIs, commercial partnerships, or user-side interaction could create a compliant data-access path; these were not verified in this workstream."
    },
    {
      "claim_id": "C11",
      "claim": "Cross-platform China sourcing and matching functionality has historical precedent: AiPrice's Chrome listing reports 100,000 users and supports image/product research across Amazon, AliExpress, 1688, Taobao and other platforms.",
      "classification": "FACT",
      "source_ids": ["S12"],
      "confidence": "high",
      "counterevidence": "AiPrice is primarily positioned toward sellers, sourcing and operations rather than a complete U.S.-consumer landed-cost routing product."
    },
    {
      "claim_id": "C12",
      "claim": "AiPrice's own forum contains 2026 reports of cross-platform search functions failing, providing anecdotal evidence that third-party matching integrations can be operationally brittle.",
      "classification": "FACT",
      "source_ids": ["S13"],
      "confidence": "medium",
      "counterevidence": "Individual support incidents do not establish systemic or persistent failure."
    },
    {
      "claim_id": "C13",
      "claim": "Community evidence in 2026 shows both high forwarding costs and successful U.S. deliveries, implying substantial cost/time dispersion rather than categorical infeasibility.",
      "classification": "INFERENCE",
      "source_ids": ["S14", "S15"],
      "confidence": "medium",
      "counterevidence": "Community posts are self-selected anecdotes and cannot establish population-level shipping economics."
    }
  ],
  "categories": [
    {
      "category": "customs_de_minimis",
      "falsification_strength": "high",
      "newest_data_date": "2026-06-24",
      "metrics": {
        "fy2024_postal_de_minimis_entries": 74800000,
        "sep_nov_2025_postal_entries": 7254980,
        "annualized_sep_nov_2025_entries": 29099645,
        "approx_decline_vs_fy2024_pct": 61.1
      },
      "counterevidence": "Low-value imports remain possible under new entry processes."
    },
    {
      "category": "international_platform_price_compression",
      "falsification_strength": "medium_high",
      "newest_data_date": "2026-06-30",
      "metrics": {
        "aliexpress_countries_regions": "200+",
        "aliexpressdirect_inventory_countries": "30+",
        "june_2026_quarter_operating_profit": true
      },
      "counterevidence": "No pre-freeze exact-SKU coverage or price comparison was performed."
    },
    {
      "category": "agent_logistics",
      "falsification_strength": "medium",
      "newest_data_date": null,
      "metrics": {
        "mainstream_procurement_service_fee_pct": 0,
        "free_storage_days": 90,
        "air_volumetric_divisor_cm3_per_kg": 6000
      },
      "counterevidence": "Free procurement and consolidation preserve viability for some lightweight, high-spread goods."
    },
    {
      "category": "returns_and_risk_allocation",
      "falsification_strength": "medium",
      "newest_data_date": null,
      "metrics": {
        "china_stage_no_reason_return_window_days": 5
      },
      "counterevidence": "Insurance and claims support can mitigate but not eliminate the consumer-experience gap."
    },
    {
      "category": "source_platform_access",
      "falsification_strength": "medium_high",
      "newest_data_date": "2026-09-30",
      "metrics": {
        "unauthorized_bot_scraping_restricted": true
      },
      "counterevidence": "Authorized/API/partnership routes remain unresolved."
    },
    {
      "category": "historical_matching_precedent",
      "falsification_strength": "mixed",
      "newest_data_date": "2026-08-15",
      "metrics": {
        "aiprice_chrome_users": 100000,
        "aiprice_rating_count": 585,
        "aiprice_rating": 4.9
      },
      "counterevidence": "Existing tool adoption proves technical demand/predecessors, but not the economics of a consumer landed-cost router."
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "Domestic-first frozen SKU transaction prices, sales rankings and coupon states",
      "requirement": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "Exact-SKU overseas prices and coverage after freeze",
      "requirement": "Manual frozen-sample audit"
    },
    {
      "gap": "Actual weight, volumetric weight and current U.S. forwarding quotations",
      "requirement": "Real shipping quotes"
    },
    {
      "gap": "SKU-specific HTS, MFN, Section 301 and exclusions",
      "requirement": "Per-SKU customs classification"
    },
    {
      "gap": "Negotiated B2B/volume agent rates for individually forwarded parcels",
      "requirement": "Commercial quotation or contract; not publicly verified"
    },
    {
      "gap": "Cross-border return, fraud, payment and chargeback loss rates",
      "requirement": "Operational dataset or paid/partner data"
    },
    {
      "gap": "Authorized Taobao/Tmall/JD catalog and transaction-data access suitable for a comparison product",
      "requirement": "Platform API/partnership verification"
    }
  ],
  "pre_freeze_compliance": true
}
```