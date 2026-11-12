# W6-A — Regulation / Structural Boundary

**研究截至：2026-10-06。WEB RESEARCH AVAILABLE。** 实际网页检索窗口为 **2026-10-06T21:09:10Z–2026-10-06T21:16:17Z**。检索工具不暴露逐页面的真实抓取时刻，因此 JSON 中逐源 `retrieved_at` 置 `null`，而不伪造时间。相关材料中最新的有日期核心司法裁判是 **2026-08-13**；法规/机构动态页面在 2026-10-06 实时读取。

## 1. Direct answer

**结论：存在一条在法律结构上可行的轻资产路线，但关键不是“把消费者写成 importer”这么简单。** 最干净的边界是：平台不取得货权、不担任 IOR、不自行替他人办理海关业务；采购代理、报关和运输分别由适格主体/持牌 broker/forwarder 完成。法规没有规定“拿规模运价必须同时成为进口商或零售商”；但承运商是否愿意给这种结构 volume rate 是商业事实，本 W6 **未验证**。

| 架构 | purchaser / IOR | 主要结构性边界 | 轻资产判断 |
|---|---|---|---|
| A comparison/routing | 消费者与卖家/agent 成交；平台默认不是 IOR | FCC 对 RF 设备的“marketing”定义可早于进口责任触发 | **最轻** |
| B consumer→Superbuy | **AUTHENTICATED DATA REQUIRED**；取决于合同及实际 entry 文件 | 消费者并不因此自动承担 CPSC certification；CPSC 明说个人自用消费者通常不是认证意义的 importer | **可轻，但责任链须实证** |
| C 平台做 buying agent | principal/平台谁是 purchaser 取决于是否取 title | 若替他人进行 HTS classification、valuation、准备 CBP filing，可能进入 customs-broker 许可边界 | **可轻，需严格分离报关职能** |
| D 平台聚合物流 | 若无 title，仅收货/保管/运输，不当然成为 IOR | CPSA 给纯 3PL/freight forwarder 明确 carve-out；但自己充当 NVOCC/IAC 会进入运输监管 | **可以物理/商业聚合而不必进口** |
| E 平台为 IOR | 平台成为适格 IOR | 直接承担 entry/reasonable-care、duty deposit；CPSC importer/eFiling；部分 FCC SDoC 责任 | **明显监管悬崖** |
| F 自有库存/美国仓 | 平台买货并销售；通常同时叠加 E | 再增加 distributor/retailer 的 CPSC reporting/recall 等责任 | **接近传统进口零售商** |

最重要的 2026 变化是：**不能再用旧的 $800 de minimis 经济模型。** CBP 当前 FAQ 说明，$800 以下、所有运输模式的商业货件均受 suspension，需 formal/informal entry；2026-08-13 CIT 又判定最高法院否定 IEEPA 加征 tariff 并没有恢复 de minimis，并支持该 suspension。且 Public Law 119-21 已规定从 **2027-07-01** 法定删除 commercial-shipment de minimis。  
https://www.cbp.gov/trade/basic-import-export/e-commerce/faqs  
https://www.cit.uscourts.gov/sites/cit/files/26-94.pdf  
https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm [LTNR](https://ltnr.ca/morty/?mortyurl=https%3A%2F%2Fwww.cbp.gov%2Ftrade%2Fbasic-import-export%2Fe-commerce%2Ffaqs)

## 2. Evidence table

| Claim | Evidence / source / date | Confidence | Counterevidence |
|---|---|---|---|
| De minimis 当前不是可依赖架构 | EO 14388，2026-02-20；CBP 91 FR 37801，2026-06-24；CIT 26-94，2026-08-13。https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/ ；https://www.federalregister.gov/documents/2026/06/24/2026-12669/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry ；https://www.cit.uscourts.gov/sites/cit/files/26-94.pdf | High | 最高法院确实在 2026-02-20 否定 IEEPA tariff 权限；但该案未裁定 de minimis suspension，CIT 后续明确区分。 [The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block) |
| IOR 是真正 customs liability cliff | 19 USC 1484 要求适格 IOR entry/reasonable care；19 USC 1505 要求 IOR deposit duties。https://www.law.cornell.edu/uscode/text/19/1484 ；https://www.law.cornell.edu/uscode/text/19/1505 | High | 商业合同可以把经济成本转嫁给另一方，但不会因此改变 CBP 法定 entry 责任。 [Legal Information Institute](https://www.law.cornell.edu/uscode/text/19/1484) |
| 自动化报关功能可触及 broker 许可 | 19 CFR 111.1 把 classification、valuation、duty、为 CBP filing 准备文件列为 customs business；纯数据传输除外；111.2 通常要求 broker license。https://www.law.cornell.edu/cfr/text/19/111.1 ；https://www.law.cornell.edu/cfr/text/19/111.2 | High | 纯购物前 tariff estimate、没有替客户准备/提交 entry，不等同于上述 customs business；精确边界仍需按产品流程审查。 [Legal Information Institute](https://www.law.cornell.edu/cfr/text/19/111.1) |
| CPSC 责任不是简单推给终端消费者 | CPSC 规则把进口商品 certifier 与 IOR/适格 entry party 联系；并明确个人自用消费者通常不视为 certification importer；2026-07-08 eFiling 已生效。https://www.cpsc.gov/FAQ/GCC ；https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports | High | 并非所有商品都有 CPSC certificate 要求；必须逐产品判断 applicable rule。 [U.S. Consumer Product Safety Commission](https://www.cpsc.gov/FAQ/GCC) |
| 纯物流聚合本身不必变 retailer/importer | 15 USC 2052：不取 title、仅收货/保管/运输的 3PL，以及 carrier/freight forwarder，不仅因运输行为成为 CPSA manufacturer/distributor/retailer。https://www.law.cornell.edu/uscode/text/15/2052 | High | 若平台取 title、销售、进口，或超越纯物流职能，该 carve-out 不再回答全部责任。 [Legal Information Institute](https://www.law.cornell.edu/uscode/text/15/2052) |
| FCC 风险可能在 IOR 之前出现 | 47 CFR 2.803 的 marketing 包含 advertising/offering for sale；2.909 对进口 SDoC 产品以 importer 为 responsible party。https://www.law.cornell.edu/cfr/text/47/2.803 ；https://www.law.cornell.edu/cfr/text/47/2.909 | High | §2.1204 有“三台以内个人自用”等 import exception；但个人进口例外不能自动推出平台可公开营销未经授权设备。https://www.law.cornell.edu/cfr/text/47/2.1204 [Legal Information Institute](https://www.law.cornell.edu/cfr/text/47/2.803) |

## 3. Primary sources

最关键原始材料是 CIT **Axle of Dearborn**（2026-08-13）、CBP 的 2026-06-24 interim final rule、CPSC 2026-07-08 eFiling 实施公告、Public Law 119-21 §70531，以及当前 CBP/CPSC 官方 FAQ。特别值得注意：PL 119-21 已把 commercial de minimis 的法定删除日期写成 **2027-07-01**，因此即使当前行政 suspension 后续继续诉讼，也不能据此假设旧 $800 模式长期回归。https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm [GovInfo](https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm)

对于 marketplace 边界，FTC 的 INFORM 指南定义覆盖允许第三方卖家参与 sale/purchase/payment/storage/shipping/delivery 的 consumer-directed marketplace；2025-09-05 FTC 对 Temu 宣布 $2m INFORM settlement，是实际执法而不是理论风险。https://www.ftc.gov/business-guidance/resources/INFORMAct ；https://www.ftc.gov/news-events/news/press-releases/2025/09/online-marketplace-temu-pay-2-million-penalty-alleged-inform-act-violations [Federal Trade Commission](https://www.ftc.gov/business-guidance/resources/INFORMAct)

## 4. Forum evidence

社区材料只作为实施摩擦的佐证，不作为法律依据。Superbuy subreddit 上署名 “Superbuy Team”的 2026-06-30 公告已要求用户关注 CPC/GCC/eFiling；回复中又称 Superbuy 自身“不是 seller or manufacturer”，用户集中反映从国内卖家取得美国认证资料困难。该帖无法证明 Superbuy 的真实 IOR、broker 或 contractual status，因此这些字段仍为 **AUTHENTICATED DATA REQUIRED**。https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/ [Reddit](https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/)

## 5. Contrary evidence

轻资产 thesis 有三个重要反例/限制。第一，FCC 允许某些 RF 设备三台以内个人自用进口，所以并非所有 DTC RF shipment 都被禁止；第二，CPSA 对无 title 的 3PL 有明确保护，因此“物理碰货=零售商”是错误概括；第三，CPSC 又明确说个人消费者通常不是 certificate-responsible importer，因此也不能通过把消费者列为收件人就让产品合规责任消失。对 de minimis，当前 CIT 判决仍可能被上诉；但 2027 法定 repeal 是独立的不利事实。 [Legal Information Institute](https://www.law.cornell.edu/cfr/text/47/2.1204)

## 6. Confidence

**High**：de minimis、IOR/duty、customs-broker、CPSC、FCC、INFORM 的规则边界。  
**Medium**：B/C/D 具体谁是 purchaser/IOR，因为这取决于 Superbuy/forwarder 的合同、POA、entry data 和实际 shipping line。  
**Medium**：能够“不做 IOR 仍拿 volume discount”在法律上没有发现禁止，但**实际商业可得性未验证**。

## 7. Data gaps

最关键缺口是：Superbuy/Sugargoo 等对美线路的实际 Terms、POA、ACE entry/IOR 字段、bond holder、broker identity 和 DDP/DAP 安排；这些需要真实合同或去标识 entry packet，不能靠公开宣传推断，标记 **AUTHENTICATED DATA REQUIRED**。其次，若平台自己承包海运，FMC 对 NVOCC 有 licensing/financial-responsibility/tariff 规则；https://www.fmc.gov/about/bureaus-offices/bureau-of-enforcement-investigations-and-compliance-beic/office-of-compliance/ocean-transportation-intermediaries/ 。航空聚合、50 州 marketplace-facilitator/product-liability、具体 PGA/HTS 也需后续按真实流程审查。 [Federal Maritime Commission](https://www.fmc.gov/about/bureaus-offices/bureau-of-enforcement-investigations-and-compliance-beic/office-of-compliance/ocean-transportation-intermediaries/)

## 8. Most surprising finding

最反直觉的是两个边界同时成立：**平台只做无 title 的物流聚合，CPSA 明确允许它不因此变成 manufacturer/distributor/retailer；但终端个人消费者又通常不是 CPSC certification importer。** 因而合法轻资产结构确实有空间，但必须设计一个真实承担 certification/entry 责任的上游或适格进口主体，不能让责任链“凭空消失”。 [Legal Information Institute](https://www.law.cornell.edu/uscode/text/15/2052)

## 9. What would falsify this conclusion?

如果后续真实 entry packets 显示代理物流的低价线路普遍要求平台本身成为 IOR/merchant；如果 carrier 的规模价只给 NVOCC/IAC/shipper-of-record、无法通过既有持牌商实现；如果州法把这种 routing/buying-agent 模式普遍认定为 seller；或者监管机构把平台的商品页面认定为对大量未经 FCC authorization 设备的违法 marketing，那么“轻资产 + volume economics”结论会明显变弱。

## 10. Suggested next experiment

唯一优先实验应是**责任链文件审计，而不是更多理论搜索**：选同一代理的一条邮政线和一条 express line，获取/审阅去标识的 purchase terms、broker POA、entry type、IOR、bond、HTS filer、duty payer、CPSC certificate filer 和 transport contracting party，并逐字段映射到 A–F。该实验能直接回答“规模物流经济是否必须伴随 IOR/title”。本轮没有联系商家、购买商品或访问付费/登录数据。

```json
{
  "job_id": "W6-A",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S02",
      "url": "https://www.cit.uscourts.gov/sites/cit/files/26-94.pdf",
      "title": "Axle of Dearborn, Inc. v. Department of Commerce, Slip Op. 26-94",
      "published_at": "2026-08-13",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S03",
      "url": "https://www.cbp.gov/trade/basic-import-export/e-commerce/faqs",
      "title": "E-Commerce Frequently Asked Questions",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03"]
    },
    {
      "source_id": "S04",
      "url": "https://www.federalregister.gov/documents/2026/06/24/2026-12669/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03"]
    },
    {
      "source_id": "S05",
      "url": "https://www.law.cornell.edu/uscode/text/19/1484",
      "title": "19 U.S. Code § 1484 - Entry of merchandise",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C10", "C11"]
    },
    {
      "source_id": "S06",
      "url": "https://www.law.cornell.edu/uscode/text/19/1505",
      "title": "19 U.S. Code § 1505 - Payment of duties and fees",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C11"]
    },
    {
      "source_id": "S07",
      "url": "https://www.law.cornell.edu/cfr/text/19/111.1",
      "title": "19 CFR § 111.1 - Definitions",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S08",
      "url": "https://www.law.cornell.edu/cfr/text/19/111.2",
      "title": "19 CFR § 111.2 - License and permit required",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C10"]
    },
    {
      "source_id": "S09",
      "url": "https://www.law.cornell.edu/uscode/text/15/2052",
      "title": "15 U.S. Code § 2052 - Definitions",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S10",
      "url": "https://www.cpsc.gov/FAQ/GCC",
      "title": "General Certificate of Conformity (GCC) FAQ",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C11"]
    },
    {
      "source_id": "S11",
      "url": "https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports",
      "title": "CPSC Implements Mandatory eFiling for Certificates of Compliance, Targeting Dangerous Foreign Imports",
      "published_at": "2026-07-08",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C11"]
    },
    {
      "source_id": "S12",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.803",
      "title": "47 CFR § 2.803 - Marketing of radio frequency devices prior to equipment authorization",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S13",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.909",
      "title": "47 CFR § 2.909 - Responsible party",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C11"]
    },
    {
      "source_id": "S14",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.1204",
      "title": "47 CFR § 2.1204 - Import conditions",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S15",
      "url": "https://www.ftc.gov/business-guidance/resources/INFORMAct",
      "title": "Informing Businesses about the INFORM Consumers Act",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S16",
      "url": "https://www.ftc.gov/news-events/news/press-releases/2025/09/online-marketplace-temu-pay-2-million-penalty-alleged-inform-act-violations",
      "title": "Online Marketplace Temu to Pay $2 Million Penalty for Alleged INFORM Act Violations",
      "published_at": "2025-09-05",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S17",
      "url": "https://www.fmc.gov/about/bureaus-offices/bureau-of-enforcement-investigations-and-compliance-beic/office-of-compliance/ocean-transportation-intermediaries/",
      "title": "Ocean Transportation Intermediaries",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C09", "C10"]
    },
    {
      "source_id": "S18",
      "url": "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
      "title": "Public Law 119-21",
      "published_at": "2025-07-04",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S19",
      "url": "https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/",
      "title": "U.S. CPSC Policy Update & Customs Compliance Guide",
      "published_at": "2026-07-01",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "As of 2026-10-06, the commercial de minimis exemption is suspended for low-value shipments across modes; formal or informal entry and applicable duties/fees are required, and the August 13, 2026 CIT decision upheld the de minimis rescission notwithstanding the Supreme Court's separate invalidation of IEEPA tariffs.",
      "classification": "FACT",
      "source_ids": ["S01", "S02", "S03", "S04"],
      "confidence": "high",
      "counterevidence": "The Supreme Court held that IEEPA did not authorize the challenged tariffs, but the CIT expressly stated the de minimis rescission was not decided in that case; the CIT judgment itself may remain subject to appellate review."
    },
    {
      "claim_id": "C02",
      "claim": "Public Law 119-21 repeals the commercial-shipment de minimis exception effective July 1, 2027.",
      "classification": "FACT",
      "source_ids": ["S18"],
      "confidence": "high",
      "counterevidence": "A future Congress could amend the statute before the effective date, but no such change was found in this bounded research."
    },
    {
      "claim_id": "C03",
      "claim": "The importer of record is the central customs-liability role: an eligible party must make entry using reasonable care, and the IOR is required to deposit estimated duties and fees.",
      "classification": "FACT",
      "source_ids": ["S03", "S05", "S06"],
      "confidence": "high",
      "counterevidence": "Commercial agreements can shift the economic incidence of duties to another party, but that does not by itself change statutory entry responsibility."
    },
    {
      "claim_id": "C04",
      "claim": "A platform that conducts classification, valuation, duty work, or prepares CBP entry documents on behalf of others can enter the customs-business licensing boundary; mere electronic transmission of received data is expressly excluded.",
      "classification": "FACT",
      "source_ids": ["S07", "S08"],
      "confidence": "high",
      "counterevidence": "A pre-purchase comparison estimate that is not prepared for or transmitted as a CBP filing is not clearly within the cited definition; exact implementation matters."
    },
    {
      "claim_id": "C05",
      "claim": "For CPSC-regulated imported finished products, certification responsibility is tied to the responsible importer/eligible entry party; CPSC states that an individual consumer purchasing for personal use is not typically treated as the importer responsible for certification, and mandatory eFiling took effect July 8, 2026.",
      "classification": "FACT",
      "source_ids": ["S10", "S11"],
      "confidence": "high",
      "counterevidence": "Not every consumer product is subject to a CPSC certification requirement; applicable rules must be determined product by product."
    },
    {
      "claim_id": "C06",
      "claim": "Under the CPSA, a third-party logistics provider that solely receives, holds, or transports goods without taking title, as well as carriers and freight forwarders, is not deemed a manufacturer, distributor, or retailer solely because of those logistics activities.",
      "classification": "FACT",
      "source_ids": ["S09"],
      "confidence": "high",
      "counterevidence": "The statutory protection does not cover additional conduct such as taking title, selling, importing in another capacity, or other activities beyond ordinary logistics."
    },
    {
      "claim_id": "C07",
      "claim": "FCC exposure can arise before a platform becomes importer of record because marketing includes advertising or offering RF devices for sale; for imported devices subject to Supplier's Declaration of Conformity the importer can be the responsible party, while limited personal-use import exceptions exist.",
      "classification": "FACT",
      "source_ids": ["S12", "S13", "S14"],
      "confidence": "high",
      "counterevidence": "The personal-use exception permits specified categories of three or fewer devices, and whether a passive comparison link itself constitutes prohibited marketing would depend on facts not resolved by the cited rules."
    },
    {
      "claim_id": "C08",
      "claim": "Moving from routing into an online marketplace can trigger INFORM Consumers Act seller-verification, disclosure, suspension and reporting-mechanism duties; federal enforcement against Temu demonstrates this is an enforced boundary.",
      "classification": "FACT",
      "source_ids": ["S15", "S16"],
      "confidence": "high",
      "counterevidence": "A comparison service or buying-agent arrangement does not automatically satisfy the statutory definition of an online marketplace; coverage depends on platform and seller relationships."
    },
    {
      "claim_id": "C09",
      "claim": "If a platform itself holds out or operates as an ocean transportation intermediary/NVOCC, separate FMC licensing, financial-responsibility and tariff-related requirements can arise.",
      "classification": "FACT",
      "source_ids": ["S17"],
      "confidence": "high",
      "counterevidence": "Using an already regulated NVOCC or forwarder does not by itself make the technology platform an NVOCC."
    },
    {
      "claim_id": "C10",
      "claim": "A legally plausible light-asset architecture exists in which the platform does not take title or become IOR and outsources customs and transport functions to eligible/licensed parties; regulation does not itself require IOR status merely to aggregate commercial demand.",
      "classification": "INFERENCE",
      "source_ids": ["S05", "S08", "S09", "S17"],
      "confidence": "medium",
      "counterevidence": "The research did not establish that carriers or buying agents will grant material volume discounts under this allocation of roles; specific carrier contracts could require a regulated shipper or intermediary."
    },
    {
      "claim_id": "C11",
      "claim": "Architectures E and F represent the clearest regulatory cliff because becoming IOR or inventory-owning importer directly adds customs duty/entry responsibility and, for relevant products, CPSC importer/eFiling and FCC responsible-party obligations.",
      "classification": "INFERENCE",
      "source_ids": ["S05", "S06", "S10", "S11", "S13"],
      "confidence": "high",
      "counterevidence": "The exact compliance burden varies by product; certification-based FCC devices can place primary technical responsibility on the certification grantee rather than automatically on every importer."
    },
    {
      "claim_id": "C12",
      "claim": "Community evidence indicates that 2026 CPSC eFiling/certificate requirements are already creating practical documentation friction for buying-agent users, but this does not establish the agent's legal IOR or seller status.",
      "classification": "INFERENCE",
      "source_ids": ["S19"],
      "confidence": "low",
      "counterevidence": "The Reddit account and user comments are not a substitute for authenticated contracts, entry records, or agency determinations."
    }
  ],
  "categories": [
    {
      "architecture_id": "A",
      "architecture": "comparison/routing layer",
      "purchaser": "consumer contracts with seller or external agent",
      "importer_of_record": "not platform by default",
      "customs_duty": "IOR bears statutory entry/deposit obligation; economic incidence contract-dependent",
      "certification_responsibility": "no CPSC importer role solely from comparison; FCC marketing risk may arise for RF-device advertising",
      "customs_broker_risk": "low if no preparation or filing of customs entries",
      "transport_regulatory_risk": "low",
      "light_asset_feasibility": "high",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C03", "C04", "C07"]
    },
    {
      "architecture_id": "B",
      "architecture": "consumer buys through Superbuy or similar buying agent",
      "purchaser": "AUTHENTICATED DATA REQUIRED: contract-specific",
      "importer_of_record": "AUTHENTICATED DATA REQUIRED: entry-document-specific",
      "customs_duty": "depends on actual IOR/entry arrangement",
      "certification_responsibility": "consumer is not typically CPSC certification importer merely because purchase is personal",
      "customs_broker_risk": "depends on who prepares/files entry",
      "transport_regulatory_risk": "agent/forwarder arrangement specific",
      "light_asset_feasibility": "potentially high but unverified",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C01", "C03", "C05"]
    },
    {
      "architecture_id": "C",
      "architecture": "platform acts as buying agent",
      "purchaser": "principal versus agent status depends on contract and title",
      "importer_of_record": "not automatically platform; must be determined from eligibility and entry facts",
      "customs_duty": "IOR bears statutory deposit obligation",
      "certification_responsibility": "rises materially if platform becomes importer",
      "customs_broker_risk": "material if platform performs customs business for others",
      "transport_regulatory_risk": "moderate depending logistics role",
      "light_asset_feasibility": "medium-high with strict role separation",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C03", "C04", "C05"]
    },
    {
      "architecture_id": "D",
      "architecture": "platform aggregates shipments",
      "purchaser": "underlying purchaser can remain unchanged if platform takes no title",
      "importer_of_record": "aggregation alone does not establish platform as IOR",
      "customs_duty": "remains with applicable IOR/entry arrangement",
      "certification_responsibility": "CPSA no-title 3PL carve-out applies to logistics activity alone",
      "customs_broker_risk": "material if platform itself prepares customs entries",
      "transport_regulatory_risk": "can become material if platform itself is NVOCC or other regulated transportation intermediary",
      "light_asset_feasibility": "medium-high through licensed third parties",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C04", "C06", "C09", "C10"]
    },
    {
      "architecture_id": "E",
      "architecture": "platform becomes importer of record",
      "purchaser": "platform must have qualifying IOR status under applicable entry facts",
      "importer_of_record": "platform",
      "customs_duty": "platform directly responsible for IOR duty/fee deposit obligations",
      "certification_responsibility": "direct CPSC importer/eFiling responsibility for applicable regulated goods; FCC importer responsibility for relevant SDoC equipment",
      "customs_broker_risk": "platform may use licensed broker but remains IOR",
      "transport_regulatory_risk": "separate from IOR status",
      "light_asset_feasibility": "low-medium",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C03", "C05", "C07", "C11"]
    },
    {
      "architecture_id": "F",
      "architecture": "platform owns inventory / U.S. warehouse",
      "purchaser": "platform purchases inventory for resale",
      "importer_of_record": "typically platform if self-importing; exact structure contract-dependent",
      "customs_duty": "E-level customs obligations if platform imports",
      "certification_responsibility": "E-level importer obligations plus distributor/retailer safety reporting responsibilities",
      "customs_broker_risk": "broker can be outsourced but importer responsibility remains",
      "transport_regulatory_risk": "depends on transport activities",
      "light_asset_feasibility": "low",
      "regulatory_friction_score": null,
      "evidence_claim_ids": ["C05", "C06", "C11"]
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap_id": "DG01",
      "gap": "Actual Superbuy/Sugargoo U.S. terms, broker POA, entry type, IOR field, bond holder, duty payer and certificate filer.",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap_id": "DG02",
      "gap": "Whether a platform can obtain meaningful forwarder/carrier volume discounts while never taking title, acting as IOR, or becoming a regulated transportation intermediary.",
      "status": "commercial evidence required; belongs primarily to W5"
    },
    {
      "gap_id": "DG03",
      "gap": "Fifty-state marketplace-facilitator, sales-tax and product-liability treatment of a buying-agent/routing architecture.",
      "status": "state-by-state legal review required"
    },
    {
      "gap_id": "DG04",
      "gap": "Exact TSA/IAC or FMC/NVOCC classification for any proposed physical aggregation flow.",
      "status": "requires exact transport contracts and operating facts"
    },
    {
      "gap_id": "DG05",
      "gap": "Product-specific HTS, Section 301/232 or other duties, and Partner Government Agency requirements.",
      "status": "intentionally not researched pre-freeze; requires frozen SKU/category facts"
    }
  ],
  "pre_freeze_compliance": true
}
```