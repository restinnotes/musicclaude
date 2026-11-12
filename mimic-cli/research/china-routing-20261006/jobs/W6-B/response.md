# W6-B — Regulation / Structural Boundary

**研究截至：2026-10-06。WEB RESEARCH AVAILABLE。**  
核心来源最终复核批次：**2026-10-06T22:33:03Z**；论坛复核：**2026-10-06T22:34:11Z**；CPSC 最新公告复核：**2026-10-06T22:35:01Z**。本轮看到的最新重要已发布规则是 FCC **2026-09-11** final rule；CBP Entry Type 13 测试已于 **2026-09-22** 开始。FCC 该新规要到 **2026-10-13** 才生效，因此不能把它写成 10 月 6 日已生效规则。未做任何 SKU、海外价格或覆盖率搜索，`pre_freeze_compliance=true`。

## 1. Direct answer

**[INFERENCE，高置信] 核心答案是“存在轻资产合法结构，但不是旧式 de-minimis 无摩擦结构”。** 最稳健的形态是：平台不取得货权、不做 IOR、不自行从事受许可的 customs business；消费者/真实 owner-purchaser 保持交易主体，报关交给 licensed customs broker，仓储/拼包/运输交给 3PL/forwarder。美国法并没有把“物理聚合货物”本身等同于 retailer/importer；CPSA 甚至明确规定，无货权的 3PL/freight forwarder 仅因收货运输，不因此成为 manufacturer/distributor/retailer。[Legal Information Institute](https://www.law.cornell.edu/uscode/text/15/2052)

| 架构 | Purchaser / IOR | 关税责任 | 产品合规跃迁 | W6-B判断 |
|---|---|---|---|---|
| **A Comparison/routing** | 消费者购买；平台通常非 IOR | IOR/其 bond 承担海关法责任，成本可合同转嫁消费者 | 平台最低；但若进一步成交/履约，会进入 marketplace/FCC 边界 | **最轻** |
| **B 消费者通过 Superbuy** | Superbuy 实际代下单，但公开条款不足以证明美国入境时谁是 owner/purchaser/IOR | 必须逐线路看报关文件 | Superbuy 条款不能替代美国法责任分配 | **可轻资产；IOR 未验证** |
| **C 平台 buying agent** | 真正代理结构可让消费者保持 principal；IOR 可是 owner/purchaser 或其 broker | 若平台替别人准备/办理报关，可能进入 customs-broker licensing | 取得货权或承担卖方功能会明显升高 | **可行但结构要刻意设计** |
| **D 平台聚合/拼包** | 聚合本身不改变 purchaser；无货权 freight forwarder 仍需合资格 IOR/broker | 取决于 entry 结构 | 纯 3PL 有法定隔离；电池/危险品、自己经营海运会另触规则 | **可拿物流规模而不必成为 importer** |
| **E 平台成为 IOR** | 平台即 IOR，即使未必是最终经济购买者 | bond、entry、税费/纠错责任直接落到平台 | CPSC/FCC importer 责任显著增加 | **监管悬崖** |
| **F 自有库存/美国仓** | 通常取得货权并成为进口/销售链主体 | 平台承担并计入售价 | importer + retailer/seller 责任最强 | **已接近传统进口零售商** |

**[FACT] 2026 最大结构变化是 $800 de minimis 已不能作为商业模型基础。** CBP 6 月规则分别对邮政和非邮政所有模式无限期暂停 19 U.S.C. 1321(a)(2)(C) 豁免；非邮政低值件必须走适当 formal/informal entry。邮政 Entry Type 13 又明确要求 IOR、HTS、价值、税额和 bond。[Federal Register Public Inspection](https://public-inspection.federalregister.gov/2026-12670.pdf)

**[INFERENCE] 因此答案不是“平台要不要自己进口”，而是“能否把商业量聚合与法律角色拆开”。答案原则上是可以。** 但我没有找到 Superbuy 公布的美国线路 B2B volume-discount 门槛或“1000 个独立终端订单仍分别保持消费者/经纪人 IOR”的合同承诺；该部分必须标记 **AUTHENTICATED DATA REQUIRED**。

## 2. Evidence table

| Claim | Evidence / URL / date | Confidence | Counterevidence |
|---|---|---:|---|
| **C01 [FACT] de minimis 已全面暂停** | CBP 2026-06-24：[https://public-inspection.federalregister.gov/2026-12670.pdf](https://public-inspection.federalregister.gov/2026-12670.pdf)；邮政测试：[https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail](https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail) [Federal Register Public Inspection](https://public-inspection.federalregister.gov/2026-12670.pdf) | 高 | bona-fide gifts / traveler exemptions仍存在；不能说“所有小包所有豁免都消失”。 |
| **C02 [FACT] 代他人做 customs business 有 broker 边界** | 19 CFR 111.1/111.2：[https://www.law.cornell.edu/cfr/text/19/111.1](https://www.law.cornell.edu/cfr/text/19/111.1)；[https://www.law.cornell.edu/cfr/text/19/111.2](https://www.law.cornell.edu/cfr/text/19/111.2) [Legal Information Institute](https://www.law.cornell.edu/cfr/text/19/111.1) | 高 | “mere electronic transmission”明确不属于 customs business；平台并非什么数据动作都必须持 broker license。 |
| **C03 [FACT] CPSC eFiling 已于 2026-07-08 生效** | CPSC：[https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports](https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports)；16 CFR 1110.3：[https://www.law.cornell.edu/cfr/text/16/1110.3](https://www.law.cornell.edu/cfr/text/16/1110.3) [U.S. Consumer Product Safety Commission](https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports) | 高 | broker 即使作为 IOR，也可指定 owner/purchaser/consignee 为 CPSC certificate responsible party；个人自用消费者通常不被 CPSC 当成认证责任 importer。 |
| **C04 [FACT] 无货权纯 3PL 有明确隔离** | 15 U.S.C. 2052：[https://www.law.cornell.edu/uscode/text/15/2052](https://www.law.cornell.edu/uscode/text/15/2052) [Legal Information Institute](https://www.law.cornell.edu/uscode/text/15/2052) | 高 | 隔离只限“solely”收货/持有/运输；一旦取得 title、销售或承担其他功能，结论改变。 |
| **C05 [FACT] FCC责任不是简单等同于 IOR** | 47 CFR 2.1204：[https://www.law.cornell.edu/cfr/text/47/2.1204](https://www.law.cornell.edu/cfr/text/47/2.1204)；2.909：[https://www.law.cornell.edu/cfr/text/47/2.909](https://www.law.cornell.edu/cfr/text/47/2.909) [Legal Information Institute](https://www.law.cornell.edu/cfr/text/47/2.1204) | 高 | 认证设备主要由 certification grantee 负责；个人自用特定 RF 设备还有 ≤3 台例外。 |
| **C06 [FACT] Marketplace 的 FCC 边界正在扩大** | FCC final rule 2026-09-11：[https://www.govinfo.gov/content/pkg/FR-2026-09-11/pdf/2026-18535.pdf](https://www.govinfo.gov/content/pkg/FR-2026-09-11/pdf/2026-18535.pdf) [GovInfo](https://www.govinfo.gov/content/pkg/FR-2026-09-11/pdf/2026-18535.pdf) | 高 | **截至 10/06 尚未生效**；10/13 才生效，FCC-ID display compliance 分别到 2027-03-01/06-01。 |
| **C07 [INFERENCE] 可在不成为 IOR 的情况下获取物流规模经济** | CBP允许 forwarder/consignee 通过 licensed broker；CPSA保护无货权3PL；Superbuy当前已做仓储、合包且国际运输由第三方：[https://www.superbuy.com/en/page/guide/shoppingagent/](https://www.superbuy.com/en/page/guide/shoppingagent/) [Federal Register](https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail) | 中高 | 是否真能获得所需“平台商务价”、门槛及逐终端包裹 IOR 安排没有公开合同证据。 |

## 3. Primary sources

最有决定性的 primary chain 是 **CBP 2026-12670 / 2026-12668 → CPSC Part 1110/eFiling → FCC 2026-18535**。另外，INFORM Consumers Act 会在平台真正允许第三方卖家通过其进行 sale/purchase/payment/storage/shipping/delivery 时增加 marketplace seller-verification 义务：[https://www.ftc.gov/business-guidance/resources/INFORMAct](https://www.ftc.gov/business-guidance/resources/INFORMAct)。[Federal Trade Commission](https://www.ftc.gov/business-guidance/resources/INFORMAct)

Superbuy 的公开操作说明确认其会代用户购买、仓储、合并包裹，且 international delivery 由指定第三方执行：[https://www.superbuy.com/en/page/about/agreement/](https://www.superbuy.com/en/page/about/agreement/)；[https://www.superbuy.com/en/page/guide/shoppingagent/](https://www.superbuy.com/en/page/guide/shoppingagent/)。这些条款**不能证明美国海关意义上的 IOR 身份**。[Superbuy](https://www.superbuy.com/en/page/about/agreement/)

## 4. Forum evidence

Superbuy subreddit 上一则标为公告、署名 “Superbuy Team” 的 2026-06-30/07-01 帖子称 CPSC eFiling 后，部分用户很难从中国卖家取得 CPC/GCC/测试文件；回复中的 Superbuy 账号亦表示代理本身不是 seller/manufacturer。URL：[https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/](https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/)。[Reddit](https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/)

这只能证明**操作摩擦和文件可得性问题**，不能证明所有个人包裹都要证书或都会被扣；同一社区也有成功清关案例，构成反证。

## 5. Contrary evidence

最重要的反证恰恰支持“不要把 D/E/F 的风险错误投射到 A/B”：CPSC 明文称个人购买自用品通常不被视作认证责任 importer；纯 3PL 无货权仅运输不会因此变成 manufacturer/retailer；FCC 对部分个人自用 RF 设备允许最多三台，并且认证设备的持续技术责任首先属于 certification grantee。[Legal Information Institute](https://www.law.cornell.edu/cfr/text/16/1110.3)

但反方向也存在：2026 FCC 已发布的新规则明确把“在线 listing + warehousing/order processing/billing/fulfillment”等组合纳入 marketing。即使**不取得货权**，成熟 marketplace 也不等于完全没有 FCC 平台责任。[GovInfo](https://www.govinfo.gov/content/pkg/FR-2026-09-11/pdf/2026-18535.pdf)

## 6. Confidence

总体 **medium-high**。对 de minimis、broker licensing、CPSC eFiling、3PL carve-out、FCC 现行/即将生效规则为 **high**；对 A–F 具体交易中的 purchaser/title/IOR 分配为 **medium**，因为这取决于合同、POA、bill/entry record，而不是品牌自称“agent”。本报告是架构研究，不替代针对最终合同流的法律意见。

## 7. Data gaps

**AUTHENTICATED DATA REQUIRED：** Superbuy/Sugargoo/BuckyDrop 各美国线路真实 ACE/entry 文件上的 IOR、broker、consignee；商业批量价门槛及“集中议价、分散直寄”是否可签；公开 Superbuy B2B 页面搜索索引曾显示 batch packing / split-to-different-users，但页面正文此次返回空内容，因此该具体能力记为 **UNVERIFIED**。另需在 SKU freeze 后逐品类验证 CPSC/FCC 所需证书是否真实存在，而不能从 HTS 或搜索 snippet 猜测。

## 8. Most surprising finding

**最意外的是监管边界比“是否碰货”更精确。** 美国法明确允许一个实体物理持有、拼包、运输而不因此自动成为 CPSC retailer/manufacturer；真正的 cliff 是 **title / IOR / selling / customs-business / product-certification functions**。与此同时，FCC 2026 新规又说明“无 title”也不是 marketplace 的永久安全港：功能足够深，平台义务仍会上升。[Legal Information Institute](https://www.law.cornell.edu/uscode/text/15/2052)

## 9. What would falsify this conclusion?

若后续真实报关文件显示规模化直邮必须由平台统一成为 IOR；或主要 forwarder 只有在平台取得 title/承担 importer liability 时才给商务价；或 CPSC/FCC 在实际执行中系统性把 buying-agent/consignee 认定为认证责任主体；或平台为生成 HTS/价值/entry 数据所做的核心自动化被认定为未经许可的 customs business，那么“轻资产 + volume logistics”的结论将显著削弱。危险品也有独立边界：执行某项 hazmat pre-transport function 的主体要对该功能负责；若平台自己成为 NVOCC/OFF，还会触发 FMC licensing/financial-responsibility 体系。[Legal Information Institute](https://www.law.cornell.edu/cfr/text/49/171.2)

## 10. Suggested next experiment

**唯一最值钱的 W6 下一步实验：做“同一订单、三种法律角色”的文件级 dry run。** 对已冻结后的同一合规商品，要求 forwarder + licensed broker 提供三套匿名/样例流程：①消费者为 owner/purchaser/IOR；②broker 为 IOR；③平台为 IOR。逐字段比较 POA、ACE entry、bond、HTS/PGA/CPSC 数据、invoice/title、duty debit 与 return/recall responsibility。这样能直接判定：**商业量能否聚合，而法律进口责任仍保持分散。** 在拿到这些文件前，“Superbuy 可以给 volume discount 所以无需成为 importer”只能维持 **INFERENCE，而非 FACT**。

```json
{
  "job_id": "W6-B",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://public-inspection.federalregister.gov/2026-12670.pdf",
      "title": "Indefinite Suspension of the De Minimis Exemption for Merchandise Arriving Through All Modes Other Than the International Postal Network",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S02",
      "url": "https://www.federalregister.gov/documents/2026/06/24/2026-12668/test-of-the-new-electronic-informal-entry-process-for-mail",
      "title": "Test of the New Electronic Informal Entry Process for Mail",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C09"]
    },
    {
      "source_id": "S03",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S04",
      "url": "https://www.law.cornell.edu/cfr/text/19/111.1",
      "title": "19 CFR § 111.1 - Definitions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S05",
      "url": "https://www.law.cornell.edu/cfr/text/19/111.2",
      "title": "19 CFR § 111.2 - License and permit required",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S06",
      "url": "https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports",
      "title": "CPSC Implements Mandatory eFiling for Certificates of Compliance, Targeting Dangerous Foreign Imports",
      "published_at": "2026-07-08",
      "retrieved_at": "2026-10-06T22:35:01Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C10"]
    },
    {
      "source_id": "S07",
      "url": "https://www.law.cornell.edu/cfr/text/16/1110.3",
      "title": "16 CFR § 1110.3 - Definitions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C10"]
    },
    {
      "source_id": "S08",
      "url": "https://www.law.cornell.edu/uscode/text/15/2052",
      "title": "15 U.S. Code § 2052 - Definitions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C09", "C10"]
    },
    {
      "source_id": "S09",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.1204",
      "title": "47 CFR § 2.1204 - Import conditions",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S10",
      "url": "https://www.law.cornell.edu/cfr/text/47/2.909",
      "title": "47 CFR § 2.909 - Responsible party",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C10"]
    },
    {
      "source_id": "S11",
      "url": "https://www.govinfo.gov/content/pkg/FR-2026-09-11/pdf/2026-18535.pdf",
      "title": "Protecting Against National Security Threats to the Communications Supply Chain Through the Equipment Authorization Program",
      "published_at": "2026-09-11",
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S12",
      "url": "https://www.ftc.gov/business-guidance/resources/INFORMAct",
      "title": "Informing Businesses about the INFORM Consumers Act",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S13",
      "url": "https://www.superbuy.com/en/page/about/agreement/",
      "title": "Superbuy Terms of Service",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S14",
      "url": "https://www.superbuy.com/en/page/guide/shoppingagent/",
      "title": "Superbuy User Guidance - Shopping Agent",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08", "C09"]
    },
    {
      "source_id": "S15",
      "url": "https://www.superbuy.com/en/page/businessservice/?tab=channel",
      "title": "Superbuy Business Service",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:34:11Z",
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S16",
      "url": "https://www.faa.gov/hazmat/safecargo/resources/lithium-battery-guide",
      "title": "Interactive Guide to Shipping Lithium Batteries",
      "published_at": "2026-08-28",
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S17",
      "url": "https://www.law.cornell.edu/cfr/text/49/171.2",
      "title": "49 CFR § 171.2 - General requirements",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S18",
      "url": "https://www.fmc.gov/about/bureaus-offices/bureau-of-enforcement-investigations-and-compliance-beic/office-of-compliance/ocean-transportation-intermediaries/",
      "title": "Ocean Transportation Intermediaries",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:33:03Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S19",
      "url": "https://www.reddit.com/r/Superbuy/comments/1uk7eaq/noticeus_cpsc_policy_update_customs_compliance/",
      "title": "Notice: U.S. CPSC Policy Update & Customs Compliance Guide",
      "published_at": "2026-07-01",
      "retrieved_at": "2026-10-06T22:34:11Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "截至2026-10-06，19 U.S.C. 1321(a)(2)(C)的800美元de minimis行政免税已对邮政和非邮政商业进口暂停；低值商品需要适当的formal或informal entry。",
      "classification": "FACT",
      "source_ids": ["S01", "S02", "S03"],
      "confidence": "high",
      "counterevidence": "Bona fide gifts和旅客随身个人/家庭物品的独立豁免未被这些规则取消。"
    },
    {
      "claim_id": "C02",
      "claim": "平台若代表消费者从事报关、归类、估价、准备拟提交CBP的报关文件等customs business，通常需要customs broker license；仅机械传输他人提供的数据明确被排除。",
      "classification": "FACT",
      "source_ids": ["S02", "S04", "S05"],
      "confidence": "high",
      "counterevidence": "进口人可为自己账户办理customs business；部分非商业进口及特定运输活动还有法定例外。"
    },
    {
      "claim_id": "C03",
      "claim": "CPSC对受认证要求约束的进口消费品的eFiling自2026-07-08生效；进口商品的certifier通常是Part 1110定义的importer。",
      "classification": "FACT",
      "source_ids": ["S06", "S07"],
      "confidence": "high",
      "counterevidence": "当licensed broker作为IOR时，可在CPSC数据中识别owner/purchaser/consignee为证书责任方；个人为自用购买或接收商品通常不被CPSC视为认证责任importer。"
    },
    {
      "claim_id": "C04",
      "claim": "无货权且仅在通常业务中接收、持有或运输商品的3PL/freight forwarder，不会仅因该运输行为就在CPSA下被视为manufacturer、distributor或retailer。",
      "classification": "FACT",
      "source_ids": ["S08"],
      "confidence": "high",
      "counterevidence": "该保护取决于其仅从事相应物流行为且不取得title；增加销售、进口或其他职能会改变分析。"
    },
    {
      "claim_id": "C05",
      "claim": "FCC的产品责任不能简单等同于海关IOR：认证设备通常由certification grantee负责；SDoC进口设备则进口商可成为responsible party，且特定个人自用RF设备存在最多三台的进口条件。",
      "classification": "FACT",
      "source_ids": ["S09", "S10"],
      "confidence": "high",
      "counterevidence": "个人自用例外只适用于法规列明的设备和条件，不能推广到商业转售或所有无线产品。"
    },
    {
      "claim_id": "C06",
      "claim": "FCC于2026-09-11发布的新规则把在线marketplace listing与仓储、订单处理、包装、billing或fulfillment等组合明确纳入marketing，并设置FCC ID展示要求；该规则在研究截至日尚未生效。",
      "classification": "FACT",
      "source_ids": ["S11"],
      "confidence": "high",
      "counterevidence": "规则2026-10-13才生效，FCC ID展示的实际compliance dates为2027-03-01和2027-06-01，并有旧listing、低量卖家和二手设备等例外。"
    },
    {
      "claim_id": "C07",
      "claim": "纯comparison/link-out模式较不容易成为INFORM Consumers Act意义下的online marketplace；一旦平台允许第三方卖家通过其完成sale、purchase、payment、storage、shipping或delivery并与消费者存在相应平台合同，INFORM义务明显增加。",
      "classification": "INFERENCE",
      "source_ids": ["S12"],
      "confidence": "medium",
      "counterevidence": "具体产品流程可能即使没有完整checkout也满足法定定义的一部分，需要根据最终合同和功能逐项判断。"
    },
    {
      "claim_id": "C08",
      "claim": "Superbuy公开资料确认其可按用户指示采购、仓储、合并包裹，并由指定第三方进行国际运输；公开资料不足以确认每条美国线路的美国IOR或商业批量折扣结构。",
      "classification": "FACT",
      "source_ids": ["S13", "S14", "S15"],
      "confidence": "medium",
      "counterevidence": "B2B页面的搜索索引曾显示batch packing和split-to-different-users能力，但本次直接页面正文为空，因此该具体功能及商业条件为UNVERIFIED。"
    },
    {
      "claim_id": "C09",
      "claim": "存在一种法律上可行的轻资产结构：平台不取得title、不成为IOR、不自行从事受许可customs business，把报关交给licensed broker，把仓储/拼包/运输交给3PL，同时在商业层面聚合订单量。",
      "classification": "INFERENCE",
      "source_ids": ["S02", "S04", "S05", "S08", "S14"],
      "confidence": "medium",
      "counterevidence": "没有公开合同证明Superbuy或其他代理会按所需规模提供足够大的volume discount，或允许所有终端包裹保持所需的分散IOR结构。"
    },
    {
      "claim_id": "C10",
      "claim": "平台成为IOR、取得商品货权或持有美国库存会显著提高海关和产品合规责任；F类自有库存/美国仓最接近传统进口零售结构。",
      "classification": "INFERENCE",
      "source_ids": ["S06", "S07", "S08", "S10", "S11"],
      "confidence": "high",
      "counterevidence": "IOR并非在所有法规下自动等同于唯一产品认证责任人，例如broker-as-IOR的CPSC责任可分配给owner/purchaser/consignee，FCC认证设备责任也可继续属于grantee。"
    },
    {
      "claim_id": "C11",
      "claim": "即使平台避免成为IOR，若其实际承担危险品pre-transport functions或自行作为NVOCC/Ocean Freight Forwarder提供海运服务，仍会触发独立的DOT/FMC监管义务。",
      "classification": "FACT",
      "source_ids": ["S16", "S17", "S18"],
      "confidence": "high",
      "counterevidence": "这些义务与是否为customs IOR是不同维度；把相关功能外包给合规carrier/OTI可避免平台自身承担部分角色。"
    },
    {
      "claim_id": "C12",
      "claim": "Superbuy社区证据显示2026 CPSC eFiling实施后，中国国内卖家取得美国CPC/GCC/测试资料可能成为现实操作摩擦。",
      "classification": "INFERENCE",
      "source_ids": ["S19"],
      "confidence": "low",
      "counterevidence": "该证据来自社区和平台账号讨论，并存在成功清关的相反个案，不能据此估计扣关率或证明所有个人进口均需同类证书。"
    }
  ],
  "categories": [
    {
      "architecture": "A",
      "name": "comparison/routing layer",
      "purchaser": "consumer",
      "importer_of_record": "consumer/owner/purchaser or appointed licensed broker; platform normally outside role",
      "duty_responsibility": "IOR/bonded party legally; economic cost may be passed to consumer",
      "product_compliance_boundary": "lowest platform exposure if no title, checkout, fulfillment or customs business",
      "regulatory_friction": "low",
      "light_asset_feasibility": "high",
      "confidence": "medium"
    },
    {
      "architecture": "B",
      "name": "consumer buys through Superbuy",
      "purchaser": "contract-dependent; Superbuy publicly states it purchases following user instructions",
      "importer_of_record": "not established by public Superbuy materials; route-specific customs documents required",
      "duty_responsibility": "route and IOR dependent",
      "product_compliance_boundary": "can remain relatively light, but CPSC/FCC requirements still apply to regulated goods and the actual responsible party",
      "regulatory_friction": "medium",
      "light_asset_feasibility": "high",
      "confidence": "medium"
    },
    {
      "architecture": "C",
      "name": "platform acts as buying agent",
      "purchaser": "consumer can remain principal in a genuine agency structure; exact title allocation is contractual",
      "importer_of_record": "owner/purchaser or properly appointed licensed broker",
      "duty_responsibility": "IOR/bonded party legally",
      "product_compliance_boundary": "customs-broker licensing becomes critical if platform performs customs business for others",
      "regulatory_friction": "medium",
      "light_asset_feasibility": "medium_high",
      "confidence": "medium"
    },
    {
      "architecture": "D",
      "name": "platform aggregates shipments",
      "purchaser": "aggregation alone need not change purchaser",
      "importer_of_record": "must still be an eligible owner/purchaser or broker; a nominal freight forwarder cannot simply self-file as owner",
      "duty_responsibility": "entry-specific",
      "product_compliance_boundary": "pure no-title 3PL has CPSA carve-out; hazmat and transportation licensing may arise from functions performed",
      "regulatory_friction": "medium",
      "light_asset_feasibility": "medium_high",
      "confidence": "medium_high"
    },
    {
      "architecture": "E",
      "name": "platform becomes importer of record",
      "purchaser": "may or may not also be economic purchaser",
      "importer_of_record": "platform",
      "duty_responsibility": "platform entry/bond responsibility",
      "product_compliance_boundary": "CPSC/FCC and admissibility obligations materially increase",
      "regulatory_friction": "high",
      "light_asset_feasibility": "low",
      "confidence": "high"
    },
    {
      "architecture": "F",
      "name": "platform owns inventory / US warehouse",
      "purchaser": "platform normally takes title before downstream consumer sale",
      "importer_of_record": "typically platform or broker acting for it",
      "duty_responsibility": "platform economics",
      "product_compliance_boundary": "importer plus retailer/seller responsibilities; highest exposure among studied architectures",
      "regulatory_friction": "very_high",
      "light_asset_feasibility": "low",
      "confidence": "high"
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "Route-specific U.S. IOR identity and broker POA structure for Superbuy, Sugargoo and BuckyDrop",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "Published or contractual volume-discount thresholds and rates for commercially aggregated but individually forwarded U.S. parcels",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "Whether provider contracts allow platform-level commercial volume aggregation while preserving consumer/third-party broker IOR on every parcel",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "Superbuy B2B split-order page terms; direct page returned no body during this session",
      "status": "UNVERIFIED"
    },
    {
      "gap": "Product-by-product CPSC/FCC certificate availability and admissibility",
      "status": "DEFER UNTIL DOMESTIC-FIRST SKU FREEZE"
    }
  ],
  "pre_freeze_compliance": true
}
```