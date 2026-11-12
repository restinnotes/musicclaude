# W6-C — Regulation / Structural Boundary

**Research as-of：2026-10-06。** 本次网页实际抓取窗口为 **2026-10-06T22:36:52Z–22:39:14Z**。最新读到的政府材料发布日期为 **2026-10-01**（CBP Entry Type 13 信息收集通知）。以下是结构研究，不构成法律意见；未检查任何具体 SKU、海外价格或覆盖率。

## 1. Direct answer / Bottom line

**结论：存在一个法律上有依据的轻资产边界，但必须刻意把“信息/交易编排、报关、运输、进口、零售”拆开。**

| 架构 | purchaser / IOR 边界 | 主要责任跃迁 |
|---|---|---|
| **A 比价/routing** | 消费者仍购买；平台通常不是 IOR | 最轻，但 RF 商品例外：FCC 把“advertising for sale”计入 marketing，纯导购并非当然免责 |
| **B 消费者经 Superbuy** | Superbuy公开称 shopping agent；其页面称进口税由 recipient 承担；**实际美国 IOR 仍须看报关记录** | 可以保持轻，但平台条款本身不能证明法律 IOR |
| **C 平台 buying agent** | 若消费者保持 owner/purchaser、持牌 broker 报关，平台不必当然成为 IOR | 若平台替客户做 classification/value/entry 文书，可能跨入需牌照的 customs business |
| **D 平台集货** | 单纯无产权的收货/仓储/运输并不自动成为进口商 | CPSC 明文保护仅因运输而存在的 3PL/forwarder；但自行转售海运/航空运输会出现 FMC/TSA 独立监管 |
| **E 平台作为 IOR** | 需具备 owner/purchaser 身份，或作为有资格的 customs broker | 关税债务、CPSC 进口商/认证/eFiling、部分 FCC responsible-party 责任显著集中到平台 |
| **F 自营库存/美国仓** | 通常已进入 importer + retailer/distributor 结构 | CPSC 报告/召回责任增加；若同时承载第三方卖家，又触发 INFORM marketplace 义务 |

因此最可证成的轻资产路径是 **A/B/C-lite/D-lite：消费者保持购买/所有权关系；持牌 customs broker 或其他合格主体做 entry；既有 forwarder/carrier 做运输；平台不取得货权、不担任 IOR，也不自行经营受牌照约束的报关业务。** 我没有找到规则规定“谈到规模物流折扣”本身会把平台变成 importer；但这是**法律结构推论，不是对某个具体商业合同的监管批准**。:chatgpt-content-reference{index="0"}

## 2. Evidence table

| Claim | Evidence / source / date | Counterevidence |
|---|---|---|
| **2026 不能沿用旧 de minimis 模型** | EO 14388 明确 §321(c) 不再适用于通常低值商业包裹；CBP 2026-06-24 又建立新的低值邮件 entry 流程。[https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block&utm_source=chatgpt.com)；[https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail](https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail) | bona fide gift 等其他法定例外仍存在；不能泛化成“所有入境物永无低值例外”。 |
| **消费者/owner-purchaser + broker 的直接包裹结构仍存在** | Entry Type 13 开放给 owner/purchaser 与其指定的持牌 broker；要求 IOR、HTS10、价值、税率、税额等。测试自 **2026-09-22** 开始；最新 CBP 资料为 **2026-10-01**。[https://www.federalregister.gov/documents/2026/10/01/2026-20170/agency-information-collection-activities-revision-entry](https://www.federalregister.gov/documents/2026/10/01/2026-20170/agency-information-collection-activities-revision-entry) | 这是 test；CBP 的 200 万 annual responses 是 PRA burden estimate，不是实际成交量。 |
| **IOR 是真正海关责任跃迁点** | 19 USC 1484：entry 可由 owner/purchaser 或获授权持牌 broker 提交；19 CFR 141.1：进口关税是 importer 对美国的个人债务。[https://www.law.cornell.edu/uscode/text/19/1484](https://www.law.cornell.edu/uscode/text/19/1484)；[https://www.law.cornell.edu/cfr/text/19/141.1](https://www.law.cornell.edu/cfr/text/19/141.1) | broker 可替 importer 缴款，因此“谁实际付款”并不能单独识别 IOR。 |
| **平台不可随意替消费者做报关专业工作** | 19 USC 1641 将 entry/admissibility/classification/valuation/关税及相关文件准备定义为 customs business；为他人经营通常需 broker license；“mere electronic transmission”例外。[https://www.law.cornell.edu/uscode/text/19/1641](https://www.law.cornell.edu/uscode/text/19/1641) | 自己账户的进口商可自行办理；纯数据传输也不等于 brokerage。 |
| **CPSC 对 direct consumer 与商业 importer 区分明显** | 当前 16 CFR 1110.3 称个人自用消费者通常不被视为承担认证责任的 importer；自 **2026-07-08** 起受认证要求的进口消费品须 eFile。[https://www.law.cornell.edu/cfr/text/16/1110.3](https://www.law.cornell.edu/cfr/text/16/1110.3)；[https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates) | 原文是 “not typically”，不是绝对安全港；具体 consignee/owner 仍可能承担证书数据责任。 |
| **纯物流可以与产品销售责任分离** | CPSA 明定仅收货、保管、运输且不取得 title 的 3PL，以及 carrier/freight forwarder，不会“solely”因运输成为 manufacturer/distributor/retailer。[https://www.law.cornell.edu/uscode/text/15/2052](https://www.law.cornell.edu/uscode/text/15/2052) | “solely”很重要：一旦拿货权、进口、销售或承担其他角色，保护不能继续机械套用。 |
| **A 层对无线电子并非零责任** | 47 CFR 2.803 的 RF “marketing”明确包括 advertising for sale；进口也须满足 §2.1204 条件。[https://www.law.cornell.edu/cfr/text/47/2.803](https://www.law.cornell.edu/cfr/text/47/2.803)；[https://www.law.cornell.edu/cfr/text/47/2.1204](https://www.law.cornell.edu/cfr/text/47/2.1204) | §2.1204 有个人自用最多 3 台的有限例外，但只覆盖规定设备类型，也不能明显消除平台自身 marketing 问题。 |

## 3. Primary sources

核心依据以 White House、Federal Register/CBP、CPSC、FTC、FMC 及现行法条为主。特别重要的是：**2026-07-08 CPSC eFiling 已生效；2026-09-22 Entry Type 13 已启动；2026-10-01 CBP 又公布了最新 ET13 信息收集说明。** :chatgpt-content-reference{index="12"}

Superbuy 官方当前页面称其提供“international shopping agent service”，并允许多件商品免费合包；同时称目的国进口税费由 recipient 承担。[https://www.superbuy.com/en/page/about/agreement/](https://www.superbuy.com/en/page/about/agreement/)；[https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/)。**反证：这些合同措辞无法确定美国海关系统中的实际 IOR；必须看具体线路的 entry、broker POA 与运单。**

## 4. Forum evidence

本轮**没有用论坛帖子建立任何法律结论**。社区经验最多能说明实际清关摩擦，不能证明 importer、FCC responsible party 或 CPSC certifier 的法定身份；因此没有把 Reddit/论坛传闻提升为 evidence。

## 5. Contrary evidence

最强反证有三项。第一，轻资产并非“无产品合规”：FCC marketing 定义可穿透到广告/导购。第二，物理集货虽不当然等于 IOR，但若平台自己向航空承运人 offer cargo，49 CFR 1548 对 indirect air carrier 要求 TSA-approved security program，甚至“不实际占有货物”也可能适用；海运若成为 OFF/NVOCC，则 FMC 要求许可/注册及财务担保。[https://www.law.cornell.edu/cfr/text/49/1548.5](https://www.law.cornell.edu/cfr/text/49/1548.5)；[https://www.fmc.gov/licensing-and-certification/apply-for-a-license-or-request-a-foreign-registration/](https://www.fmc.gov/licensing-and-certification/apply-for-a-license-or-request-a-foreign-registration/)。第三，一旦进入第三方 seller marketplace，INFORM Act 是真实且已执行的额外监管层；FTC 2025 年对 Temu 的首宗 INFORM 执法包括 **$2 million** 民事罚款。[https://www.ftc.gov/business-guidance/resources/INFORMAct](https://www.ftc.gov/business-guidance/resources/INFORMAct)；[https://www.ftc.gov/news-events/news/press-releases/2025/09/online-marketplace-temu-pay-2-million-penalty-alleged-inform-act-violations](https://www.ftc.gov/news-events/news/press-releases/2025/09/online-marketplace-temu-pay-2-million-penalty-alleged-inform-act-violations)

## 6. Confidence

**总体：medium-high。** IOR、customs broker、CPSC/FCC 边界有明确法条，confidence high；“A/B/C-lite/D-lite 可以同时取得商业量价而不成为 importer”是从这些法定角色分离推导出来，confidence medium，因为最终取决于交易合同、title/risk transfer、broker POA、运输安排及商品类别。

## 7. Data gaps

`AUTHENTICATED DATA REQUIRED` / 人工文件核验的最大缺口是：Superbuy/Sugargoo 等美国线路真实 entry record 上的 IOR、broker、bond、Incoterm/DDP 结构；快递专线是否以 broker/carrier 自身名义报关；平台若统一采购物流但让每个消费者保持 owner/purchaser 时，具体承运合同怎样写。商业 volume discount 的真实门槛属于 W5，本报告没有推断。FDA、NHTSA、EPA 等类别专门制度也未逐品类展开。

## 8. Most surprising finding

最值得注意的是**责任边界不是简单的“碰不碰货”**。CPSC 对纯运输 3PL 有明确隔离，同时对个人自用进口也给出明显缓和；但 FCC 反而可能在平台还没碰货、没做 IOR 时，就因为“advertising for sale”进入监管范围。:chatgpt-content-reference{index="19"}

## 9. What would falsify this conclusion?

如果实际 broker/CBP 文件表明消费者直邮模型中必须由路由平台统一成为 IOR；如果法院/FCC 明确认定普通中立比较链接不构成 §2.803 marketing；如果典型规模物流合同必须让平台取得 title 或承运人身份；如果 CPSC 把相关 direct-consumer 模式普遍认定为商业 importer；或若后续法规取消 owner/purchaser + licensed-broker 的低值包裹路径，本结论将需要重大修正。

## 10. Suggested next experiment

唯一最有价值的下一步是做一次**“纸面 transaction-flow audit”**：不用真实购买，也不用具体 SKU，选一个普通非受限消费品和一个 FCC RF 设备作为两个假设案例，为 A→D 分别画出 title、付款、POA、IOR、broker、carrier、consignee、CPSC certifier/FCC responsible party 字段，然后让持牌 customs broker 与美国产品合规律师逐字段书面确认。若消费者可持续作为 owner/purchaser、broker 独立报关、平台只提供数据及商业物流编排，核心轻资产边界即得到最直接验证。

```json
{
  "job_id": "W6-C",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06T22:38:20Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S02",
      "url": "https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail",
      "title": "Test of the New Electronic Informal Entry Process for Mail",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T22:38:20Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C03"]
    },
    {
      "source_id": "S03",
      "url": "https://www.federalregister.gov/documents/2026/10/01/2026-20170/agency-information-collection-activities-revision-entry",
      "title": "Agency Information Collection Activities; Revision; Entry",
      "published_at": "2026-10-01",
      "retrieved_at": "2026-10-06T22:38:20Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C03"]
    },
    {
      "source_id": "S04",
      "url": "https://www.law.cornell.edu/uscode/text/19/1484",
      "title": "19 U.S. Code § 1484 - Entry of merchandise",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:39Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C03"]
    },
    {
      "source_id": "S05",
      "url": "https://www.law.cornell.edu/cfr/text/19/141.1",
      "title": "19 CFR § 141.1 - Liability of importer for duties",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:39Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C03"]
    },
    {
      "source_id": "S06",
      "url": "https://www.law.cornell.edu/uscode/text/19/1641",
      "title": "19 U.S. Code § 1641 - Customs brokers",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:39Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S07",
      "url": "https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates",
      "title": "Update: Certificates of Compliance and eFiling",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S08",
      "url": "https://www.law.cornell.edu/cfr/text/16/1110.3",
      "title": "16 CFR § 1110.3 - Definitions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S09",
      "url": "https://www.law.cornell.edu/uscode/text/15/2052",
      "title": "15 U.S. Code § 2052 - Definitions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C07"]
    },
    {
      "source_id": "S10",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.803",
      "title": "47 CFR § 2.803 - Marketing of radio frequency devices prior to equipment authorization",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S11",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.1204",
      "title": "47 CFR § 2.1204 - Import conditions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S12",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.909",
      "title": "47 CFR § 2.909 - Responsible party",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S13",
      "url": "https://www.superbuy.com/en/page/about/agreement/",
      "title": "Terms of Service - Superbuy",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:39:14Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S14",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fees & Pricing / Fee Composition",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:39:14Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S15",
      "url": "https://www.fmc.gov/licensing-and-certification/apply-for-a-license-or-request-a-foreign-registration/",
      "title": "Apply for a License or Request a Foreign Registration",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:39:08Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S16",
      "url": "https://www.law.cornell.edu/cfr/text/49/1548.5",
      "title": "49 CFR § 1548.5 - Adoption and implementation of the security program",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:39:08Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S17",
      "url": "https://www.ftc.gov/business-guidance/resources/INFORMAct",
      "title": "Informing Businesses about the INFORM Consumers Act",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S18",
      "url": "https://www.ftc.gov/news-events/news/press-releases/2025/09/online-marketplace-temu-pay-2-million-penalty-alleged-inform-act-violations",
      "title": "Online Marketplace Temu to Pay $2 Million Penalty for Alleged INFORM Act Violations",
      "published_at": "2025-09",
      "retrieved_at": "2026-10-06T22:38:14Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S19",
      "url": "https://www.cpsc.gov/Business--Manufacturing/Recall-Guidance/Duty-to-Report-to-CPSC-Rights-and-Responsibilities-of-Businesses",
      "title": "Duty to Report to CPSC: Rights and Responsibilities of Businesses",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:38:39Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "As of 2026-10-06, ordinary commercial low-value imports cannot rely on the former Section 321 de minimis duty-free model; appropriate entry and applicable duties/fees are required under the post-suspension regime.",
      "classification": "FACT",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "Separate statutory treatment remains for certain bona fide gifts and other narrow exceptions; suspension should not be generalized beyond its scope."
    },
    {
      "claim_id": "C02",
      "claim": "CBP's Entry Type 13 test demonstrates a current legal/operational path in which an owner or purchaser, or a properly appointed licensed customs broker, can make electronic informal mail entry without a comparison platform itself becoming IOR.",
      "classification": "FACT",
      "source_ids": ["S02", "S03"],
      "confidence": "high",
      "counterevidence": "Entry Type 13 is a voluntary test and its published response volumes are Paperwork Reduction Act estimates, not evidence of actual market adoption."
    },
    {
      "claim_id": "C03",
      "claim": "The importer-of-record boundary is a major architecture transition: qualifying owner/purchaser or licensed broker makes entry, and import duties constitute a debt of the importer.",
      "classification": "FACT",
      "source_ids": ["S02", "S04", "S05"],
      "confidence": "high",
      "counterevidence": "A broker can act as IOR in some structures and can remit duties, so payment flow alone does not identify the legal importer."
    },
    {
      "claim_id": "C04",
      "claim": "A platform that performs classification, valuation, admissibility or prepares customs documents for consumers risks conducting regulated customs business; mere electronic transmission of received data is expressly excluded.",
      "classification": "FACT",
      "source_ids": ["S06"],
      "confidence": "high",
      "counterevidence": "An importer conducting customs business solely for its own account does not require a broker license, and pure data transmission is outside the statutory customs-business definition."
    },
    {
      "claim_id": "C05",
      "claim": "CPSC responsibility changes materially when the platform becomes the commercial importer: regulated imports generally require importer certification/eFiling from July 8, 2026, while CPSC says it will not typically consider a personal-use consumer the importer responsible for certification; transport-only 3PLs also have a statutory role carve-out.",
      "classification": "FACT",
      "source_ids": ["S07", "S08", "S09"],
      "confidence": "high",
      "counterevidence": "The consumer language is 'not typically,' not an absolute exemption, and the 3PL protection applies only when the entity's role is solely receiving, holding or transporting without taking title."
    },
    {
      "claim_id": "C06",
      "claim": "A pure comparison/routing layer can still face FCC issues for RF devices because FCC marketing includes advertising for sale; imported SDoC equipment can make the importer the responsible party.",
      "classification": "FACT",
      "source_ids": ["S10", "S11", "S12"],
      "confidence": "high",
      "counterevidence": "FCC rules contain a narrow personal-use import exception for three or fewer devices in specified categories; whether a particular neutral comparison interface constitutes prohibited marketing is fact-dependent."
    },
    {
      "claim_id": "C07",
      "claim": "Physical or commercial logistics aggregation does not by itself make the platform an importer, but operating as a transportation intermediary can trigger separate regimes such as TSA indirect-air-carrier security requirements or FMC OTI/NVOCC licensing and financial responsibility.",
      "classification": "FACT",
      "source_ids": ["S09", "S15", "S16"],
      "confidence": "high",
      "counterevidence": "Using an already regulated carrier/forwarder and merely negotiating commercial rates need not make the platform itself the regulated transportation intermediary."
    },
    {
      "claim_id": "C08",
      "claim": "Moving into inventory/retail or a third-party marketplace creates additional obligations independent of customs status, including CPSC hazard reporting for manufacturers/importers/distributors/retailers and INFORM Act duties for qualifying online marketplaces.",
      "classification": "FACT",
      "source_ids": ["S17", "S18", "S19"],
      "confidence": "high",
      "counterevidence": "INFORM's marketplace obligations concern third-party sellers and do not by themselves turn an own-inventory retailer into a third-party marketplace."
    },
    {
      "claim_id": "C09",
      "claim": "Superbuy's public operating model is consistent with a shopping-agent/forwarding structure in which users direct purchases, parcels may be consolidated, and destination customs charges are described as borne by the recipient, but these public terms do not establish the actual U.S. IOR for each route.",
      "classification": "FACT",
      "source_ids": ["S13", "S14"],
      "confidence": "medium",
      "counterevidence": "Actual legal status depends on carrier contracts, entry filings, broker powers of attorney and route-specific customs practices, none of which were available on the public pages reviewed."
    },
    {
      "claim_id": "C10",
      "claim": "A plausible light-asset architecture can obtain commercially negotiated logistics scale while keeping the consumer/qualified broker as the customs-side principal, provided the platform avoids taking title, acting as IOR, unlicensed customs brokerage, or independently operating regulated transportation services.",
      "classification": "INFERENCE",
      "source_ids": ["S02", "S04", "S06", "S09", "S15", "S16"],
      "confidence": "medium",
      "counterevidence": "No source reviewed constitutes regulatory approval of this exact business model, and particular logistics contracts may allocate title, IOR, consignee or carrier functions differently."
    }
  ],
  "categories": [
    {
      "architecture": "A_comparison_routing",
      "likely_purchaser": "consumer",
      "importer_of_record": "route-dependent; platform need not be IOR",
      "duty_responsibility": "importer/IOR",
      "product_compliance_boundary": "low for ordinary goods; FCC marketing exposure can arise for RF devices",
      "regulatory_friction": "low_to_medium",
      "source_ids": ["S10", "S11"]
    },
    {
      "architecture": "B_consumer_buys_through_superbuy",
      "likely_purchaser": "consumer acting through shopping agent, subject to actual contract",
      "importer_of_record": "AUTHENTICATED DATA REQUIRED / route-specific customs record required",
      "duty_responsibility": "Superbuy public page states destination import taxes are borne by recipient; legal IOR still unverified",
      "product_compliance_boundary": "depends on actual IOR and product regime",
      "regulatory_friction": "medium",
      "source_ids": ["S13", "S14"]
    },
    {
      "architecture": "C_platform_buying_agent",
      "likely_purchaser": "fact- and contract-dependent",
      "importer_of_record": "consumer/owner-purchaser or licensed broker can remain IOR if structured accordingly",
      "duty_responsibility": "IOR/importer",
      "product_compliance_boundary": "customs-broker licensing risk if platform prepares entry/classification/valuation for others",
      "regulatory_friction": "medium",
      "source_ids": ["S04", "S05", "S06"]
    },
    {
      "architecture": "D_platform_aggregates_shipments",
      "likely_purchaser": "can remain consumer if platform does not take title",
      "importer_of_record": "does not automatically shift merely because of physical aggregation",
      "duty_responsibility": "IOR/importer",
      "product_compliance_boundary": "CPSC transport-only carve-out possible; TSA/FMC transportation-intermediary rules may separately apply",
      "regulatory_friction": "medium_to_high",
      "source_ids": ["S09", "S15", "S16"]
    },
    {
      "architecture": "E_platform_importer_of_record",
      "likely_purchaser": "platform generally must qualify as owner/purchaser or act through an eligible broker structure",
      "importer_of_record": "platform",
      "duty_responsibility": "platform/importer",
      "product_compliance_boundary": "CPSC importer certification/eFiling; FCC importer responsible-party exposure where applicable",
      "regulatory_friction": "high",
      "source_ids": ["S04", "S05", "S07", "S08", "S12"]
    },
    {
      "architecture": "F_platform_inventory_us_warehouse",
      "likely_purchaser": "platform for inventory acquisition",
      "importer_of_record": "typically platform or its import structure",
      "duty_responsibility": "platform/import structure",
      "product_compliance_boundary": "importer plus retailer/distributor reporting and recall obligations; INFORM if qualifying third-party marketplace",
      "regulatory_friction": "very_high",
      "source_ids": ["S17", "S18", "S19"]
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "Actual IOR, broker, bond and Incoterm/DDP structure used by Superbuy/Sugargoo/BuckyDrop U.S. routes",
      "required_evidence": "real entry documents, carrier/broker terms or authenticated shipment records",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "Whether a proposed platform's negotiated parcel-volume contract would make it an indirect air carrier, NVOCC/OFF, consignee or principal",
      "required_evidence": "specific carrier/forwarder contract and legal review",
      "status": "unresolved"
    },
    {
      "gap": "Actual adoption and operating performance of Entry Type 13 after its September 22, 2026 launch",
      "required_evidence": "CBP operational statistics rather than PRA estimates",
      "status": "unresolved"
    },
    {
      "gap": "Product-category-specific regimes outside the core CPSC/FCC analysis, including FDA, EPA and NHTSA where relevant",
      "required_evidence": "category-specific regulatory analysis after domestic sample freeze",
      "status": "not_researched_in_W6-C"
    },
    {
      "gap": "Commercial thresholds for logistics volume discounts",
      "required_evidence": "real carrier/forwarder quotations or W5 research",
      "status": "outside_W6_scope"
    }
  ],
  "pre_freeze_compliance": true
}
```