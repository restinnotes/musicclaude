以下是独立 W7-C 结果。检索窗口为 **2026-10-06T22:39:56Z–2026-10-06T22:43:23Z**；网页工具不返回逐页精确抓取时钟，因此 JSON 中逐来源 `retrieved_at` 保守填 `null`。可明确识别日期的最新研究来源为 FINDIT 对 BigGo 的 **2026-09-04** 更新；对无发布日期的当前官网，不把抓取日伪装成发布日期。

# 1. Direct answer

**结论：核心概念并非没人尝试过，但我没有找到已规模化的“美国商品页 → 中国国内 exact match → 真实中国成交价 → 转运/税费 landed cost → 中立排序”消费者产品。**

最直接的先例是 **PriceDoge**：2019 年开源 Chrome 插件明确支持 Amazon、JD、Newegg、Taobao，在商品详情页自动搜索其他平台；Taobao 搜索甚至需要后端 Puppeteer。开发者在 V2EX 明说当时是按商品标题返回“类似商品”，P2P 价格共享因“用户量不足、没时间”没有完成，优惠券、满减、返现、商品内部 ID 变化也被讨论为真实价格问题。另一个 `2tao` 仓库直接自称“Compare products of Taobao and Amazon”，但只有 3 个 commits。故“Amazon→Taobao 比价从未有人做过”是错误命题。:chatgpt-content-reference{index="0"}  
URL: [https://github.com/DimensionDev/PriceDoge](https://github.com/DimensionDev/PriceDoge)；[https://v2ex.com/t/547246](https://v2ex.com/t/547246)；[https://github.com/zhanghongyi/2tao](https://github.com/zhanghongyi/2tao)

更重要的是，**所需能力已经分别被不同公司验证，却停留在不同层**：AiPrice 能跨 Amazon/1688/Taobao 以图找同款/相似款，Chrome 商店显示约 100,000 用户；BigGo 做自动比价、价格历史和 affiliate；Capital One Shopping 官方称覆盖 100,000+ 在线零售商并计算运费/会员价；Superbuy 接受商品链接后采购、质检、仓储、合包和国际配送；BuckyDrop/DSers 则把中国 sourcing→fulfillment 自动化卖给商家。:chatgpt-content-reference{index="4"}

因此我的主判断是 **INFERENCE**：缺失的不是某一种“神奇技术”，而是把 **跨站识别、可授权/可靠的中国价格数据、个性化交易价格、跨境履约报价和中立 monetization** 连成同一个消费者级 truth layer。

# 2. Evidence table

| Claim | Evidence / date | Confidence | Counterevidence |
|---|---|---|---|
| 已存在 Amazon↔Taobao 直接尝试 | PriceDoge 2019；2tao 开源仓库 | High | 两者都没有证明商业规模或 landed-cost 能力 |
| Matching 本身可规模化 | AiPrice：Amazon/1688 等图片搜索，Chrome 100k users；BigGo 仍运营 | High | image/similar match ≠ exact SKU |
| 转运能力本身已成熟存在 | Superbuy：link→purchase→warehouse→global delivery | High | 用户必须先知道中国商品/链接，未解决 discovery |
| 数据访问是结构性维护问题 | Alibaba 条款禁止未经授权 robots/spiders；Amazon API 有 Associates 门槛，且价格可能与特定用户看到的不同 | High | 正式 API/licensing 可部分解决 |
| 真实成交价比“页面价”困难 | PriceDoge 社区直接指出 coupon/满减/返现/内部 ID；Capital One 也单列 shipping/member pricing | Med-High | 成熟平台已能解决部分美国站点价格上下文 |
| agent 生态存在真实 IP 风险，但不能说模式本身违法 | Pandabuy 2024 曾被初步禁令；2025 法院又撤销，认为证据更接近 passive facilitator；Nike 案记录 promoter 从 PandaBuy 获得 $270k | High | 撤销禁令本身就是强反证：不能等同“代理=侵权卖家” |

数据访问来源：[https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822114124762/20250822114124762.html](https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822114124762/20250822114124762.html)；[https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction)；[https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/resources/offersV2](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/resources/offersV2)。Alibaba 明确限制未经许可通过 robots/spiders 获取或使用 Taobao/Tmall 内容；Amazon Creators API 要求 Associates 资格及近期 qualifying sales，而 OffersV2 明示 API 默认价格可能与具体客户实际看到的价格不同。:chatgpt-content-reference{index="8"}

# 3. Primary sources

**采购/履约层。** Superbuy 的当前流程是“submit a link→代购→仓库 QC/storage→global delivery”，说明最后一公里之前的中国采购与国际转运不是空白基础设施。其 affiliate 计划按被推荐用户的国际包裹运费奖励，并声称自 2012 年累计支付约 RMB 9.26m commission。BuckyDrop 和 DSers 则明显面向 Shopify/WooCommerce/Amazon 等**卖家工作流**，包括 API、supplier mapping、variant matching、自动下单和 tracking。:chatgpt-content-reference{index="9"}  
URL: [https://www.superbuy.com/](https://www.superbuy.com/)；[https://www.superbuy.com/en/page/about/affiliate/](https://www.superbuy.com/en/page/about/affiliate/)；[https://www.buckydrop.com/en/](https://www.buckydrop.com/en/)；[https://www.dsers.com/en/integration](https://www.dsers.com/en/integration)

**消费者比价层。** BigGo 政府数据库记录其成立于 2016 年、截至 2026-09-04 状态“营运中”；其扩展明确以 affiliate commission 支撑免费比价。Capital One Shopping 2026-03-12 官方材料证明浏览器后台自动比较价格、运费及会员价的消费者行为已经成立。:chatgpt-content-reference{index="14"}  
URL: [https://findit.sme.gov.tw/tw/Startup/UFRKV3BWbXVWMWp2NjYxSEtYS1c0dz09/Basic](https://findit.sme.gov.tw/tw/Startup/UFRKV3BWbXVwMWp2NjYxSEtYS1c0dz09/Basic)；[https://extension.biggo.com/store/overview.php](https://extension.biggo.com/store/overview.php)；[https://www.capitalone.com/learn-grow/money-management/capital-one-shopping/](https://www.capitalone.com/learn-grow/money-management/capital-one-shopping/?msockid=2e5cf69b5ef9656d2148e06a5f866482)

# 4. Forum evidence

PriceDoge 的 2019 V2EX 发布帖是本次最有价值的历史材料：开发者本人说跨站匹配实际是“用当前商品名去其他网站搜索类似商品”；P2P crowdsourcing 因用户不够没有启动；用户指出 coupon、满减、返现、商品 ID 变化会破坏价格真实性；开发者承认跨平台购物车+优惠组合逻辑因时间不足未完成。:chatgpt-content-reference{index="18"}

WeGoBuy 2024 Reddit 讨论出现网站 502、仓库货物担忧和 chargeback 行为，但这是**社区证据**，只能证明用户当时经历服务中断/不确定性，不能证明停运根因或“exit scam”。:chatgpt-content-reference{index="19"}  
URL: [https://www.reddit.com/r/WegobuyOfficial/comments/1co0y1d/is_wegobuy_website_down/](https://www.reddit.com/r/WegobuyOfficial/comments/1co0y1d)

# 5. Contrary evidence

最强反证有三条。第一，AiPrice、BigGo、Capital One Shopping 证明“用户不愿装插件”“跨站匹配不可能”都不是成立解释。第二，Superbuy 长期运营证明消费者代理采购/转运基础设施本身不是不存在。第三，Pandabuy 法律史不能简化成“法院认定代理商就是侵权卖家”：2025-01-14 法院撤销此前 preliminary injunction，认为现有证据更像 passive facilitator；2025-04 Nike v. Fox 也明确说 PandaBuy/agents 是否属于 direct infringers 存在 genuine dispute。:chatgpt-content-reference{index="21"}  
URL: [https://case-law.vlex.com/vid/king-spider-llc-v-1065990420](https://case-law.vlex.com/vid/king-spider-llc-v-1065990420?utm_source=chatgpt.com)；[https://docs.justia.com/cases/federal/district-courts/florida/flmdce/8:2023cv02873/421976/71](https://docs.justia.com/cases/federal/district-courts/florida/flmdce/8%3A2023cv02873/421976/71)

# 6. Confidence

**High confidence:** 过去确有 Amazon↔Taobao 比价原型；今天各子能力分别存在；平台数据权限和 transaction-price context 是真实技术/合同约束。  
**Medium confidence:** 缺乏 dominant product 的主要原因是跨层集成成本和 monetization alignment，而非单一 UI 问题。  
**Low confidence:** “这些原因已经被某家融资创业公司用真实 CAC/LTV 数据证明导致失败。”本次没有找到这种证据，因此不能声称。

# 7. Data gaps

PriceDoge/2tao 没有可靠活跃用户、收入、留存或正式 shutdown post；WeGoBuy/Pandabuy 的最终运营结局和根因没有足够一手公司材料；没有访问 Taobao/Tmall 登录态/API 商务合同；没有任何付费数据集、内部 affiliate conversion、CAC/LTV 或 agent partnership quote。以上均不能由搜索 snippet 补齐；涉及真实站内 feed/API 权限的部分应标记 **AUTHENTICATED DATA REQUIRED**。

# 8. Most surprising finding

最意外的不是“没人做过”，而是**2019 年 PriceDoge 已经非常接近入口形态，却明确停在“标题搜类似商品”这一步**；与此同时，2026 年 AiPrice 已把 Amazon↔中国供应链的 same/similar image-search 做到 100k Chrome 用户，但主要定位仍是 importer/online seller sourcing。:chatgpt-content-reference{index="24"}

这暗示市场可能不是缺 matching primitive，而是 matching 的经济价值目前更容易在 **B2B sourcing** 中兑现。

# 9. What would falsify this conclusion?

如果获得以下任一证据，我会显著下调“跨层集成是缺口”的判断：①存在未发现、已达到大规模美国消费者使用的 China-domestic landed-cost comparator；②正式 API/商业数据合同可以低成本稳定返回 authenticated transaction price 与 SKU-level inventory；③历史创业公司公开 post-mortem 显示 exact matching/landed cost 技术其实稳定，而唯一失败因素是 CAC；④ agent 已有成熟 Amazon-context API，只是公开产品未宣传；⑤真实用户实验显示仅做 title/image match 就足够达到高 precision，无需复杂 variant resolution。

# 10. Suggested next experiment

只做一个结构实验：在**未来已冻结的 domestic-first SKU universe** 上，建立一个“不购物”的技术 probe，测量三个完全独立指标：**exact-match precision、authenticated-price retrievability、landed-cost quote retrievability**。同时分别测试官方/API 路径与 browser-mediated 路径。若三者同时高，则“为什么不存在”更可能是 distribution/monetization；若任一层在合法、稳定条件下持续失败，则形成真正的结构性解释。本实验不在 W7-C 当前阶段选 SKU，也不做任何冻结前海外 coverage/价格检查。

证据账本 JSON 如下；`categories` 表示本次实际研究的**竞争者架构类别**，不是商品 category，`sku_candidates` 按预冻结规则为空。

```json
{
  "job_id": "W7-C",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://github.com/DimensionDev/PriceDoge",
      "title": "DimensionDev/PriceDoge: A Chrome extension for price comparison",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C05", "C08"]
    },
    {
      "source_id": "S02",
      "url": "https://v2ex.com/t/547246",
      "title": "反杀熟的开源小工具 PriceDoge",
      "published_at": "2019-03-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C05", "C08", "C11"]
    },
    {
      "source_id": "S03",
      "url": "https://github.com/zhanghongyi/2tao",
      "title": "zhanghongyi/2tao: A price comparison engine. Compare products of Taobao and Amazon.",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C11"]
    },
    {
      "source_id": "S04",
      "url": "https://www.aiprice.com/en/taobao_tutorials/667_425/Introduction-of-1688-Extension",
      "title": "Introduction of AiPrice Sourcing Tool extension",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S05",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj?hl=en",
      "title": "AiPrice(AliPrice) Search by Image for China Import",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S06",
      "url": "https://www.superbuy.com/",
      "title": "Superbuy - China Shopping Proxy & Shipping Worldwide",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C08"]
    },
    {
      "source_id": "S07",
      "url": "https://www.superbuy.com/en/page/about/affiliate/",
      "title": "Superbuy Affiliate Program",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S08",
      "url": "https://www.buckydrop.com/en/",
      "title": "BuckyDrop | All-in-One Auto Dropshipping Platform",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C09"]
    },
    {
      "source_id": "S09",
      "url": "https://www.dsers.com/en/integration",
      "title": "DSers Integrations",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C09"]
    },
    {
      "source_id": "S10",
      "url": "https://extension.biggo.com/store/overview.php",
      "title": "BigGo Shopping Assistant",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C06", "C10"]
    },
    {
      "source_id": "S11",
      "url": "https://findit.sme.gov.tw/tw/Startup/UFRKV3BWbXVWMWp2NjYxSEtYS1c0dz09/Basic",
      "title": "FINDIT - 樂方 BigGo",
      "published_at": "2026-09-04",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S12",
      "url": "https://www.capitalone.com/learn-grow/money-management/capital-one-shopping/",
      "title": "Capital One Shopping: A free tool to find deals online",
      "published_at": "2026-03-12",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C05"]
    },
    {
      "source_id": "S13",
      "url": "https://help.joinhoney.com/article/30-how-does-honey-make-money",
      "title": "How does Honey make money?",
      "published_at": "2024-11-25",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S14",
      "url": "https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822114124762/20250822114124762.html",
      "title": "Alibaba Legal Statement",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S15",
      "url": "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction",
      "title": "Amazon Creators API Documentation - Introduction",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S16",
      "url": "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/resources/offersV2",
      "title": "Amazon Creators API - OffersV2",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C05"]
    },
    {
      "source_id": "S17",
      "url": "https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1:2024cv02668/619156/80",
      "title": "King Spider LLC v. Panda - Preliminary Injunction Order",
      "published_at": "2024-07-10",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S18",
      "url": "https://case-law.vlex.com/vid/king-spider-llc-v-1065990420",
      "title": "King Spider LLC v. Panda (Hong Kong) Technology Co.",
      "published_at": "2025-01-14",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S19",
      "url": "https://docs.justia.com/cases/federal/district-courts/florida/flmdce/8:2023cv02873/421976/71",
      "title": "Nike Inc. v. Fox - Order",
      "published_at": "2025-04-21",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C06"]
    },
    {
      "source_id": "S20",
      "url": "https://github.com/cachho/jadeship-browser-extension",
      "title": "Jadeship browser extension",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C12"]
    },
    {
      "source_id": "S21",
      "url": "https://www.reddit.com/r/WegobuyOfficial/comments/1co0y1d/is_wegobuy_website_down/",
      "title": "Is WeGoBuy website down?",
      "published_at": "2024-05-09",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "至少已有两个公开项目直接尝试过 Taobao 与 Amazon 的跨平台商品比较；PriceDoge 还在商品详情页自动查询 Amazon、JD、Newegg、Taobao。",
      "classification": "FACT",
      "source_ids": ["S01", "S02", "S03"],
      "confidence": "high",
      "counterevidence": "这些项目没有证明达到商业规模，也没有实现本研究所要求的 exact-SKU landed-cost routing。"
    },
    {
      "claim_id": "C02",
      "claim": "跨平台商品发现和消费者自动比价本身已经分别被 AiPrice、BigGo、Capital One Shopping 等产品验证为可运行能力。",
      "classification": "FACT",
      "source_ids": ["S04", "S05", "S10", "S11", "S12"],
      "confidence": "high",
      "counterevidence": "这些产品没有被证实同时解决中国国内 authenticated transaction price、exact SKU、国际转运和关税后的 landed cost。"
    },
    {
      "claim_id": "C03",
      "claim": "Superbuy 类 buying agent 与 BuckyDrop/DSers 类 merchant SaaS 已解决采购、仓储或商家履约的很多环节，但其默认入口不是美国消费者正在浏览的商品自动发现中国 exact match。",
      "classification": "FACT",
      "source_ids": ["S06", "S08", "S09"],
      "confidence": "high",
      "counterevidence": "Superbuy 也支持关键词搜索，部分 agent/extension 正在向 discovery 扩展，因此边界并非绝对。"
    },
    {
      "claim_id": "C04",
      "claim": "稳定获取跨平台价格数据存在真实访问约束：Alibaba 条款限制未经授权的 robots/spiders，Amazon 官方 API 又有 Associates 资格门槛且 API 价格不保证等于具体客户所见价格。",
      "classification": "FACT",
      "source_ids": ["S14", "S15", "S16"],
      "confidence": "high",
      "counterevidence": "正式授权、affiliate API、商业数据许可或客户端执行可以缓解这一问题，故它不是不可逾越的技术定律。"
    },
    {
      "claim_id": "C05",
      "claim": "跨站价格的 truth problem 不只是抓到标价：优惠券、满减、返现、商品 ID/variant 和用户上下文都会改变可成交价格。",
      "classification": "FACT",
      "source_ids": ["S02", "S12", "S16"],
      "confidence": "high",
      "counterevidence": "Capital One Shopping 等成熟产品已经能处理部分优惠、运费和会员价，说明该问题可以部分工程化。"
    },
    {
      "claim_id": "C06",
      "claim": "Affiliate/referral 是该相邻生态的常见 monetization：Honey、BigGo、Superbuy 均公开披露此类收入或奖励结构。",
      "classification": "FACT",
      "source_ids": ["S07", "S10", "S13", "S19"],
      "confidence": "high",
      "counterevidence": "存在 affiliate 收入不等于必须牺牲推荐中立性，也不证明其他收入模型不可行。"
    },
    {
      "claim_id": "C07",
      "claim": "Pandabuy 生态产生了真实 IP 诉讼和运营风险，但现有法院材料不支持把 buying-agent 模式简单等同于直接侵权卖家。",
      "classification": "FACT",
      "source_ids": ["S17", "S18", "S19"],
      "confidence": "high",
      "counterevidence": "2024 年确有 preliminary injunction；但 2025 年法院随后撤销，并指出 Pandabuy 更接近 passive facilitator，Nike v. Fox 中 shipping-agent direct infringement 也被认定存在事实争议。"
    },
    {
      "claim_id": "C08",
      "claim": "当前缺口更可能是把 matching、可靠交易价格、跨境 landed-cost 和 checkout handoff 组合成一个消费者级 truth layer，而非任何单项能力完全不存在。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02", "S04", "S06", "S08", "S09", "S12", "S14", "S16"],
      "confidence": "medium",
      "counterevidence": "缺少失败创业公司的内部 post-mortem，因此不能证明这种集成难度就是无人规模化的主要因果因素。"
    },
    {
      "claim_id": "C09",
      "claim": "现有跨中国供应链的 matching/automation 工具更明显地向 importer、online seller 和 dropship merchant monetization 聚集。",
      "classification": "INFERENCE",
      "source_ids": ["S04", "S08", "S09"],
      "confidence": "medium",
      "counterevidence": "BigGo、Capital One Shopping 和 Superbuy 都证明消费者端也存在可规模化业务，因此不能推断 B2B 是唯一可行方向。"
    },
    {
      "claim_id": "C10",
      "claim": "完全中立地始终推荐最低 landed-cost 路径，可能与 affiliate-driven monetization 存在激励张力。",
      "classification": "HYPOTHESIS",
      "source_ids": ["S07", "S10", "S13"],
      "confidence": "low",
      "counterevidence": "BigGo 明确披露 affiliate 并仍提供比价功能；没有证据证明这种激励冲突足以阻止该产品成立。"
    },
    {
      "claim_id": "C11",
      "claim": "PriceDoge 和 2tao 的小规模不能被当作市场需求失败的证据。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02", "S03"],
      "confidence": "high",
      "counterevidence": "PriceDoge 开发者确实提到用户量不足以启动 P2P，但同时明确提到时间不足，因此无法区分 cold-start、资源约束与需求不足。"
    },
    {
      "claim_id": "C12",
      "claim": "本次有限公开网页研究未发现一个已规模化、明确同时完成美国零售商品上下文、中国国内 exact match、authenticated price、真实 landed cost 与消费者 routing 的产品。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S03", "S04", "S06", "S08", "S09", "S10", "S20", "S21"],
      "confidence": "medium",
      "counterevidence": "这是 bounded search 的未发现结果，不是全世界不存在此类公司或私有产品的证明；尤其缺少付费数据库及非公开 startup 数据。"
    }
  ],
  "categories": [
    {
      "category": "direct_cross_market_comparison_prototypes",
      "examples": ["PriceDoge", "2tao"],
      "customer": "consumer/developer",
      "solves": ["cross-site search", "onsite comparison"],
      "missing_layers": ["authenticated China transaction price", "exact-SKU validation at scale", "landed cost", "scaled distribution"],
      "evidence_source_ids": ["S01", "S02", "S03"]
    },
    {
      "category": "cross_border_product_matching",
      "examples": ["AiPrice"],
      "customer": "importer/online seller",
      "solves": ["image search", "same/similar product discovery", "SKU data utilities"],
      "missing_layers": ["US-consumer neutral routing", "full landed-cost comparison"],
      "evidence_source_ids": ["S04", "S05"]
    },
    {
      "category": "consumer_price_comparison_extensions",
      "examples": ["BigGo", "Capital One Shopping", "Honey"],
      "customer": "consumer",
      "solves": ["price comparison", "coupon/rewards", "price history"],
      "missing_layers": ["China-domestic procurement route", "agent shipping/tariff landed cost"],
      "evidence_source_ids": ["S10", "S11", "S12", "S13"]
    },
    {
      "category": "buying_agents_forwarders",
      "examples": ["Superbuy"],
      "customer": "consumer already seeking China procurement",
      "solves": ["purchase", "QC", "warehouse", "consolidation", "international shipping"],
      "missing_layers": ["automatic discovery from US retail context", "neutral cross-channel price ranking"],
      "evidence_source_ids": ["S06", "S07"]
    },
    {
      "category": "merchant_dropshipping_automation",
      "examples": ["BuckyDrop", "DSers"],
      "customer": "merchant",
      "solves": ["sourcing", "supplier mapping", "order automation", "fulfillment integration"],
      "missing_layers": ["end-consumer decision interface", "neutral landed-cost recommendation"],
      "evidence_source_ids": ["S08", "S09"]
    },
    {
      "category": "agent_ecosystem_and_legacy_tools",
      "examples": ["Pandabuy", "Wegobuy", "Jadeship"],
      "customer": "agent-community users",
      "solves": ["agent link conversion", "cross-agent workflow", "community-driven sourcing"],
      "missing_layers": ["verified legitimate-only catalog architecture", "stable mainstream US consumer distribution"],
      "evidence_source_ids": ["S17", "S18", "S19", "S20", "S21"]
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "Taobao/Tmall authenticated catalog, transaction-price and API licensing behavior",
      "status": "AUTHENTICATED DATA REQUIRED",
      "impact": "Cannot determine whether stable authorized exact-SKU/price ingestion is economically available."
    },
    {
      "gap": "PriceDoge and 2tao historical MAU, retention, revenue and shutdown/post-mortem",
      "status": "UNVERIFIED",
      "impact": "Cannot distinguish product-market rejection from hobby-project resource constraints."
    },
    {
      "gap": "WeGoBuy closure/root-cause primary company evidence",
      "status": "UNVERIFIED",
      "impact": "Community outage/chargeback reports cannot establish causal failure mechanism."
    },
    {
      "gap": "Private startup and VC attempt database",
      "status": "NOT ACCESSED",
      "impact": "Bounded public search may miss stealth, acquired or quietly discontinued attempts."
    },
    {
      "gap": "Cross-agent commercial referral conversion, CAC/LTV and partnership terms",
      "status": "AUTHENTICATED DATA REQUIRED",
      "impact": "Prevents causal conclusion on whether monetization or acquisition economics killed prior attempts."
    },
    {
      "gap": "Per-source exact retrieval clock",
      "status": "UNAVAILABLE_FROM_WEB_TOOL",
      "impact": "Actual session retrieval window was 2026-10-06T22:39:56Z through 2026-10-06T22:43:23Z; individual source timestamps are left null rather than fabricated."
    }
  ],
  "pre_freeze_compliance": true
}
```