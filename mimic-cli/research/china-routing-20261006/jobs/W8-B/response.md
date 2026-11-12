# W8-B — Thesis Falsification（结构性证伪）

**研究边界：**仅做 W8-B；未选择国内 SKU、未查询任何具体 SKU 的 Amazon/AliExpress/Temu 价格或覆盖，因此符合 pre-freeze protocol。  
**检索时点：**2026-10-06 UTC；本次检索批次结束时间记录为 **2026-10-06T22:59:02Z–23:01:48Z**。JSON 中 `retrieved_at` 是每批页面读取后立即记录的 UTC batch timestamp，而非网站服务器日志。  
**最新纳入的官方数据日期：**USITC 2026 HTS Revision 20，**2026-09-28**。最新社区材料日期：**2026-09-21**。

## 1. Direct answer

W8-B **没有找到足以结构性否定整个 narrow thesis 的证据**，但找到三项足以显著削弱 broad thesis 的硬事实。

第一，过去依赖的“<$800 中国包裹基本无关税、极低报关摩擦”架构已经不存在。截至 2026-10-06，美国仍暂停 duty-free de minimis；非邮政低值货物须走 formal/informal entry，国际邮件也已进入新的报关体系。最重要的是，**2026-10-22** 起邮政规则的新增合规条款才正式到期，因此把它描述为“目前所有这类包裹已经必须 formal entry”会提前 16 天。[Federal Register](https://www.federalregister.gov/d/2026-12669)  
URL: [https://www.federalregister.gov/d/2026-12669](https://www.federalregister.gov/d/2026-12669?utm_source=chatgpt.com)  
URL: [https://www.federalregister.gov/d/2026-12670](https://www.federalregister.gov/d/2026-12670?utm_source=chatgpt.com)

第二，**不能沿用 2025 年的 IEEPA 中国额外税率来证伪 thesis**。2026-02-20 后相关 IEEPA additional duties 已终止，但 de minimis suspension 保留，Section 301 等其他措施也未因此消失。因此真正的 2026 falsification test 必须逐 HTS 判断，而不是套统一“中国税率”。USITC 最新 2026 HTS 版本为 Revision 20（2026-09-28）。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/)  
URL: [https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/](https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/?utm_source=chatgpt.com)  
URL: [https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search](https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search?utm_source=chatgpt.com)

第三，最危险的结构性摩擦可能不是税率，而是**进口数据/认证要求 + catalog access**。CPSC 自 2026-07-08 对需要认证的进口消费品实施 eFiling；而历史上绕过淘宝/1688 等反爬措施进行大规模数据抓取已有行政处罚案例。不过，淘宝同时存在正式 Open API，所以证据支持的是“未经授权的数据层不可假定可规模化”，而不是“自动化一定不可行”。[U.S. Consumer Product Safety Commission](https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports)

**结论：Broad thesis 明显变弱；Narrow China-head/US-middle-tail thesis 仍是 UNRESOLVED，而非 REJECTED。** 没有 frozen domestic sample，就无法严谨证明价差集合太小。

## 2. Evidence table

| Claim | 分类 | 硬证据 | Confidence | 反证/限制 |
|---|---|---|---|---|
| C01：旧式 <$800 frictionless route 已消失 | FACT | CBP 2026-06-24 两项规则继续暂停 de minimis | High | informal/formal entry 仍可进口，不等于 economics 必然失败 |
| C02：2025 IEEPA 税率不能继续当 2026 baseline | FACT | EO 14389 终止相关 additional duties；Sec.301 独立存在 | High | 部分产品仍有 Sec.301/其他税费 |
| C03：2026-10-22 后邮政路线对 Chapter 99/PGA 商品摩擦进一步增加 | INFERENCE | CBP 邮政规则及未来 compliance date | Med-High | 截至 10-06 尚未生效；快递/非邮政/经纪模式不同 |
| C04：受 CPSC 认证商品存在前置电子合规数据要求 | FACT | 2026-07-08 eFiling 已实施 | High | eFiling 本身没有新增测试义务；并非所有商品受 CPSC 管辖 |
| C05：物流可吞噬低 ASP/低密度货品价差，但 agent 规模化并未被证伪 | FACT+INFERENCE | Superbuy 按实重/体积重/线路收费；同时公开提供 dropship、拆单、商务折扣 | Medium | 无公开大客户 rate card，无法判断真实规模曲线 |
| C06：无授权 scraping 是实际法律/运营风险 | FACT | 绕过多平台反爬、抓取 3143 万余条记录的案例罚款 30 万元 | High | 淘宝存在正式 API；授权渠道可能解决 |
| C07：AliExpress/Temu 有持续压缩跨境价差的基础设施 | INFERENCE | Alibaba/PDD filings 描述全球物流与中国商家国际化 | Medium | filings 不能证明 China-hot exact SKU coverage 或价格平价 |

## 3. Primary sources

最关键的 primary/government evidence 是 CBP 的 2026-06-24 de minimis rules、White House 2026-02-20 EO 14388/14389、USTR Section 301 查询、USITC HTS，以及 CPSC eFiling。它们共同说明：**2026 的 landed-cost 模型已经不同于 2024/2025，但也不是简单“所有中国商品再加一个统一关税”。** [Federal Register](https://www.federalregister.gov/d/2026-12669)

Superbuy 官方费用页则是重要反证：淘宝/Tmall/JD/1688 标准采购服务本身可无基础服务费；国际运费依目的地、线路和最终计费重量决定，且存在体积重计算。其商务页还宣传 direct-to-client、拆分订单及专属物流折扣，但没有公开可验证的 volume breakpoint/rate card。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)  
URL: [https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/?utm_source=chatgpt.com)  
URL: [https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

## 4. Forum evidence

社区证据只支持“运费可能足够大且波动很大”，不能推断市场平均值。例如 2026 年 Reddit 用户自报过约 **3.54kg/$70**、**5.8kg/$140**，以及两个包裹合计 **26kg/$700+** 的美国路线；也有用户认为结果可接受并成功收货。这说明 shipping 是必须真实报价的变量，而不是证明“shipping always kills spread”。[Reddit](https://www.reddit.com/r/Superbuy/comments/1qovw41/haul/?utm_source=chatgpt.com)

## 5. Contrary evidence

最强的反证有四个：一是 IEEPA 额外关税已终止；二是 Superbuy 本身公开支持商业 dropshipping/拆单直发，故“必须自己物理聚合才能规模化”未得到证明；三是淘宝正式 API 表明合法自动化并非不存在；四是 AiPrice 已长期提供淘宝/1688/Amazon 等跨平台图片找同款和价格比较，说明基础 matching 技术不是未知难题。其“百万用户”等数字属于企业自报，不能当独立审计数据。[Alibaba Developer](https://developer.alibaba.com/docs/doc.htm?articleId=23559\&docType=2\&treeId=34)

本次**未找到一个具有可审计经营结果、能证明“Amazon→中国同款 landed-cost consumer routing 因经济性失败”的历史 startup failure**。不能把“没找到”解释为不存在。

## 6. Confidence

对“**监管和报关摩擦较旧模型显著增加**”为 **High**；对“**未经授权 catalog scraping 难以作为稳定规模化基础**”为 **High**；对“**这些摩擦已经足以摧毁整体商业机会**”仅 **Medium-Low**。

原因是关键 outcome variable——冻结样本上的 China landed cost vs cheapest convenient overseas option distribution——按照本项目 protocol 尚不能测。

## 7. Data gaps

仍缺：AUTHENTICATED DATA REQUIRED 的国内正常交易数据；冻结 SKU 后逐项 HTS/Section 301/CPSC/PGA 分类；2026-10-22 后真实 broker/bond/entry admin cost；Superbuy/Sugargoo/BuckyDrop 商务级独立包裹 rate card；实际退货/拒付/欺诈成本；授权 API/affiliate 商务许可范围；以及一例经过验证且失败原因可追踪的 consumer-routing startup。

AliExpress/Temu exact coverage **有意未查**，不是“未发现”。

## 8. Most surprising finding

最重要的反直觉点是：**最高法院相关变化消除了旧 IEEPA additional tariffs，但并没有恢复 de minimis。** 因此 2026 年的结构性 bear case 应是“报关、逐品类税则和 PGA 合规摩擦”，而不是继续引用 2025 年那些已经过时的中国附加税率。[Federal Register](https://www.federalregister.gov/d/2026-12669)

## 9. What would falsify my conclusion?

若冻结样本后的实验显示以下任一结果，我目前“结构摩擦严重但 narrow thesis 尚未被证伪”的结论会被推翻：①绝大多数 demand-relevant frozen SKUs 在合法 landed cost 后只剩 <10% spread；②实际 2026-10-22 后报关/经纪成本对低 ASP 商品形成近固定最低成本；③绝大多数高潜商品都触发 Chapter 99/PGA/formal-entry friction；④授权 catalog API 无法覆盖研究所需字段且禁止商业用途；⑤商务转运 rate 并不随 volume 显著改善。

反方向，如果固定样本在所有这些成本之后仍大量保持 ≥20–30% spread，则本 W8 的结构性 bear case会明显减弱。

## 10. Suggested next experiment

唯一值得优先做的 experiment 是：**W1/W2 完成 domestic-first freeze 后，对固定、不可更换的分层 SKU 子样本做“进口可执行性审计”**。在看海外价格前锁定 SKU/hash；随后逐一记录实际重量/体积、HTS、Section 301、PGA/CPSC、可用运输线、agent quote、bond/broker/processing，再与 cheapest convenient overseas option 比较。

这能一次性区分两种解释：究竟是“真正存在未套利 spread”，还是“国内裸价看起来便宜，但合法 landed architecture 系统性吞掉了价差”。

```json
{
  "job_id": "W8-B",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06T23:01:34Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C10"]
    },
    {
      "source_id": "S02",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/",
      "title": "Ending Certain Tariff Actions",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06T23:01:34Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C10"]
    },
    {
      "source_id": "S03",
      "url": "https://www.federalregister.gov/d/2026-12669",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T23:01:48Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03", "C10"]
    },
    {
      "source_id": "S04",
      "url": "https://www.federalregister.gov/d/2026-12670",
      "title": "Indefinite Suspension of the De Minimis Exemption for Merchandise Arriving Through All Modes Other Than the International Postal Network",
      "published_at": "2026-06-24",
      "retrieved_at": "2026-10-06T23:01:48Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C10"]
    },
    {
      "source_id": "S05",
      "url": "https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search",
      "title": "USTR Section 301 Product Search",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:02Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C03"]
    },
    {
      "source_id": "S06",
      "url": "https://www.usitc.gov/harmonized_tariff_information/hts/archive/list",
      "title": "USITC Harmonized Tariff Schedule Archive; 2026 HTS Revision 20 dated 2026-09-28",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:02Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S07",
      "url": "https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports",
      "title": "CPSC Implements Mandatory eFiling for Certificates of Compliance",
      "published_at": "2026-07-08",
      "retrieved_at": "2026-10-06T22:59:02Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C04", "C10"]
    },
    {
      "source_id": "S08",
      "url": "https://www.cpsc.gov/Business--Manufacturing/Testing-Certification/Third-Party-Testing",
      "title": "CPSC Third Party Testing and Certification",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:02Z",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S09",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Service Fee Composition",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:20Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C10"]
    },
    {
      "source_id": "S10",
      "url": "https://www.superbuy.com/en/page/query/freight/",
      "title": "Superbuy Freight Calculator",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:20Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S11",
      "url": "https://www.superbuy.com/en/page/businessservice/",
      "title": "Superbuy Business Service",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:20Z",
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S12",
      "url": "https://m.cqn.com.cn/ms/content/2024-04/10/content_9044609.htm",
      "title": "Administrative penalty decision reproduced by China Quality News concerning unauthorized multi-platform crawling",
      "published_at": "2024-04-10",
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S13",
      "url": "https://developer.alibaba.com/docs/doc.htm?articleId=23559&docType=2&treeId=34",
      "title": "Taobao Open Platform Item Detail API Documentation",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:13Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S14",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm",
      "title": "Alibaba Group Holding Limited 2026 Form 20-F",
      "published_at": "2026-05-20",
      "retrieved_at": "2026-10-06T22:59:32Z",
      "source_type": "filing",
      "access_state": "snippet_only",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S15",
      "url": "https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm",
      "title": "PDD Holdings 2025 Form 20-F filed 2026",
      "published_at": "2026-04-29",
      "retrieved_at": "2026-10-06T22:59:32Z",
      "source_type": "filing",
      "access_state": "snippet_only",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S16",
      "url": "https://www.aiprice.com/",
      "title": "AiPrice Cross-Platform Sourcing and Price Comparison",
      "published_at": null,
      "retrieved_at": "2026-10-06T22:59:32Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S17",
      "url": "https://www.aliprice.com/en/taobao_tutorials/2493_459/AliPrice-Sourcing-Tool",
      "title": "AliPrice Sourcing Tool",
      "published_at": "2026-01-18",
      "retrieved_at": "2026-10-06T22:59:32Z",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S18",
      "url": "https://www.reddit.com/r/Superbuy/comments/1qovw41/haul/",
      "title": "Superbuy community haul report to the United States",
      "published_at": "2026-01-28",
      "retrieved_at": "2026-10-06T22:59:55Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S19",
      "url": "https://www.reddit.com/r/Superbuy/comments/1quvhu7/is_shipping_really_this_expensive/",
      "title": "Superbuy community discussion of United States shipping cost",
      "published_at": "2026-02-03",
      "retrieved_at": "2026-10-06T22:59:55Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S20",
      "url": "https://www.reddit.com/r/Superbuy/comments/1taahmj/shipped_out_26kg_using_hkups/",
      "title": "Superbuy community report of 26kg United States shipment",
      "published_at": "2026-05-11",
      "retrieved_at": "2026-10-06T22:59:55Z",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "As of 2026-10-06, the U.S. duty-free de minimis exemption remains suspended for low-value merchandise, removing the former largely entry-free Section 321 architecture for ordinary China-direct consumer parcels.",
      "classification": "FACT",
      "source_ids": ["S01", "S03", "S04"],
      "confidence": "high",
      "counterevidence": "Low-value merchandise remains importable through formal or informal entry procedures; suspension alone does not demonstrate that the economics are unviable."
    },
    {
      "claim_id": "C02",
      "claim": "The IEEPA additional tariffs terminated in February 2026 must not be carried forward as a blanket 2026 China tariff assumption; remaining duties, including Section 301, require HTS-specific analysis.",
      "classification": "FACT",
      "source_ids": ["S02", "S05", "S06"],
      "confidence": "high",
      "counterevidence": "Section 301 and other product-specific duties remain, while exclusions also exist, so effects are heterogeneous rather than uniformly favorable."
    },
    {
      "claim_id": "C03",
      "claim": "The 2026-10-22 compliance provisions for the new postal process are likely to increase friction for international-mail goods that trigger Chapter 99 or partner-government-agency data requirements.",
      "classification": "INFERENCE",
      "source_ids": ["S03", "S05", "S07"],
      "confidence": "medium",
      "counterevidence": "The relevant compliance date is sixteen days after the 2026-10-06 research cutoff, and non-postal, express, or broker-mediated architectures may face different procedures."
    },
    {
      "claim_id": "C04",
      "claim": "CPSC mandatory eFiling is in effect for imported consumer products that are subject to CPSC certification requirements, creating an additional structured compliance-data requirement for affected categories.",
      "classification": "FACT",
      "source_ids": ["S07", "S08"],
      "confidence": "high",
      "counterevidence": "CPSC states that eFiling itself does not create new testing or certification obligations, and many products are outside CPSC certification scope."
    },
    {
      "claim_id": "C05",
      "claim": "Forwarder economics are structurally weight-, volume-, route- and destination-dependent, but public Superbuy materials also indicate direct-to-client, split-order and business-discount capabilities, so a claim that scale necessarily requires self-operated physical aggregation is not established.",
      "classification": "FACT",
      "source_ids": ["S09", "S10", "S11"],
      "confidence": "medium",
      "counterevidence": "No authenticated negotiated U.S. business rate card or volume breakpoint was available, so whether commercial discounts are large enough to support the thesis is unresolved."
    },
    {
      "claim_id": "C06",
      "claim": "Unauthorized large-scale scraping that bypasses platform safeguards has produced real administrative enforcement in China, making unrestricted scraping an unsafe assumption for a durable catalog layer; authorized Taobao API access nevertheless exists.",
      "classification": "FACT",
      "source_ids": ["S12", "S13"],
      "confidence": "high",
      "counterevidence": "The enforcement example concerned unauthorized circumvention at large scale and does not establish that licensed API, affiliate or negotiated commercial access is unavailable."
    },
    {
      "claim_id": "C07",
      "claim": "AliExpress and Temu already possess global merchant and logistics infrastructure capable of internationalizing Chinese supply and therefore create a plausible mechanism for discovered price spreads to compress.",
      "classification": "INFERENCE",
      "source_ids": ["S14", "S15"],
      "confidence": "medium",
      "counterevidence": "Corporate filings do not establish exact-SKU coverage, China-head SKU coverage, or price parity with domestic Chinese channels."
    },
    {
      "claim_id": "C08",
      "claim": "Cross-platform China sourcing and product-matching tooling already exists, including AiPrice, which weakens any claim that basic cross-market discovery is technically unprecedented but does not demonstrate a successful U.S. consumer landed-cost routing business.",
      "classification": "FACT",
      "source_ids": ["S16", "S17"],
      "confidence": "medium",
      "counterevidence": "AiPrice usage figures are company-reported and its core positioning includes sourcing and cross-border sellers; it is not evidence that the proposed consumer economics work."
    },
    {
      "claim_id": "C09",
      "claim": "Recent community reports demonstrate that international forwarding charges can be economically material and highly variable, including reported U.S. shipments around $70 for 3.54kg, $140 for 5.8kg, and more than $700 for a 26kg two-parcel shipment.",
      "classification": "FACT",
      "source_ids": ["S18", "S19", "S20"],
      "confidence": "medium",
      "counterevidence": "These are self-reported anecdotes, not representative samples; users also reported successful deliveries, and consolidation or high merchandise value can make these freight costs acceptable."
    },
    {
      "claim_id": "C10",
      "claim": "Structural evidence materially weakens the broad thesis that China-direct consumer purchasing retains the old low-friction economics, but it does not falsify the narrower hypothesis that a sufficiently large China-head/US-middle-tail anomaly set remains after full legal landed cost.",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02", "S03", "S04", "S07", "S09", "S11", "S12"],
      "confidence": "medium",
      "counterevidence": "The decisive frozen domestic SKU sample, exact HTS classification, actual logistics quotes and overseas convenient-option benchmarks were intentionally not examined before sample freeze."
    }
  ],
  "categories": [
    {
      "category": "low-value lightweight non-regulated goods",
      "structural_falsification_mechanism": "loss of duty-free de minimis plus entry/data friction",
      "risk_level": "high",
      "confidence": "high",
      "measured_price_spread": null
    },
    {
      "category": "CPSC-regulated and children's products",
      "structural_falsification_mechanism": "certification/eFiling/PGA requirements and post-2026-10-22 postal-entry friction",
      "risk_level": "very_high",
      "confidence": "high",
      "measured_price_spread": null
    },
    {
      "category": "bulky or low-density goods",
      "structural_falsification_mechanism": "volumetric-weight international freight",
      "risk_level": "high",
      "confidence": "high",
      "measured_price_spread": null
    },
    {
      "category": "high-ASP lightweight non-PGA goods",
      "structural_falsification_mechanism": "HTS-specific duty and freight rather than a universal structural blocker",
      "risk_level": "medium",
      "confidence": "medium",
      "measured_price_spread": null
    },
    {
      "category": "comparison/routing data layer",
      "structural_falsification_mechanism": "permissioned API dependency, anti-scraping controls and platform access durability",
      "risk_level": "high",
      "confidence": "high",
      "measured_price_spread": null
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap_id": "G01",
      "gap": "Frozen domestic-first exact-SKU landed-cost distribution was intentionally not measured before W1/W2 sample freeze.",
      "required_method": "post-freeze manual/API price and landed-cost audit"
    },
    {
      "gap_id": "G02",
      "gap": "Normal Chinese consumer transaction prices, ranking data and some marketplace fields may require authenticated state.",
      "required_method": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap_id": "G03",
      "gap": "No authenticated Superbuy, Sugargoo or BuckyDrop negotiated high-volume individual-forwarding rate card or volume breakpoint was accessed.",
      "required_method": "real commercial quotation or authenticated contract/rate data"
    },
    {
      "gap_id": "G04",
      "gap": "Actual per-parcel bond, broker, entry and administrative costs under the post-2026-10-22 postal regime are not yet observed.",
      "required_method": "real post-effective-date shipping and customs quotes"
    },
    {
      "gap_id": "G05",
      "gap": "HTS, Section 301, CPSC, FCC and other PGA treatment is unknown for the eventual frozen SKU universe.",
      "required_method": "SKU-by-SKU classification after freeze"
    },
    {
      "gap_id": "G06",
      "gap": "No audited failed startup was verified that directly implemented U.S. consumer Amazon-to-China same-item landed-cost routing and failed for demonstrated structural economic reasons.",
      "required_method": "founder records, archived product history, filings or independently documented shutdown evidence"
    },
    {
      "gap_id": "G07",
      "gap": "Current commercial permissions and economics for sustained catalog access through negotiated platform APIs or affiliate programs remain unresolved.",
      "required_method": "official commercial API terms or authenticated partner documentation"
    },
    {
      "gap_id": "G08",
      "gap": "AliExpress and Temu exact-SKU coverage was intentionally not examined because the domestic-first SKU sample has not yet been frozen.",
      "required_method": "post-freeze exact-match coverage audit"
    }
  ],
  "pre_freeze_compliance": true
}
```