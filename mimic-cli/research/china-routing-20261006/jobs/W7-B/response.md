以下为 W7-B 独立报告。仅研究竞争格局、历史尝试与结构性“为什么没有主导产品”；**未选择国内 SKU，未检查任何具体 SKU 的海外价格、库存或覆盖率**。Web research 可用；本轮实际检索窗口为 **2026-10-06T22:38:37Z–2026-10-06T22:46:54Z**。浏览工具不提供逐 URL 的精确抓取秒级时间，因此 JSON 中逐源 `retrieved_at` 保守填 `null`，不伪造。最新明确发布日期证据为 **2026-09-29** 的波兰 UODO Pandabuy 数据事件页面。

# 1. Direct answer / Bottom line

1. **[FACT] “Amazon → 淘宝/中国平台同款比较”不是没人做过。** 2019 年开源 PriceDoge 已在 Amazon、JD、Newegg、Taobao 商品页之间搜索并显示其他平台结果；作者明确说按当前商品标题查 TB/Amazon/Newegg/JD。  
[https://github.com/DimensionDev/PriceDoge](https://github.com/DimensionDev/PriceDoge)  
[https://www.v2ex.com/t/547246](https://www.v2ex.com/t/547246) :chatgpt-content-reference{index="2"}

2. **[FACT] 2026 年甚至已有非常接近目标架构的微型产品。** GP Sourcing 可在 Amazon/Shopify/AliExpress 页面寻找 1688 货源并估算 DDP/landed cost；IK Sourcing 明确从 Amazon US/UK 找 1688 并估算 landed UK cost；另一个 Amazon-to-1688 扩展直接做供应商匹配。但抓取时分别只有约 **56、5、8 名 Chrome 用户**，且主要服务卖家/进口商，而非普通消费者。  
[https://chromewebstore.google.com/detail/gp-sourcing-dropshipping/habbjbbidapgddblimhdjjgpnceeihab](https://chromewebstore.google.com/detail/habbjbbidapgddblimhdjjgpnceeihab?utm_source=header-cta)  
[https://chromewebstore.google.com/detail/ik-sourcing-%E2%80%94-1688-profit/kdmdebiinfbkgmncenjcjfafdagkkikd](https://chromewebstore.google.com/detail/ik-sourcing-%E2%80%94-1688-profit/kdmdebiinfbkgmncenjcjfafdagkkikd)  
[https://chromewebstore.google.com/detail/amazon-to-1688-sourcing-a/bkggnbelomjlmjnmiffalchkocnkijbn](https://chromewebstore.google.com/detail/amazon-to-1688-sourcing-a/bkggnbelomjlmjnmiffalchkocnkijbn) :chatgpt-content-reference{index="6"}

3. **[FACT] 同款发现本身已经能达到明显规模。** AiPrice/AliPrice 的 Chrome 扩展抓取时显示约 **200,000 users**；公司自报截至 2025-08 累计用户约 100 万、注册用户约 65 万，并支持 Amazon、1688、Taobao 等图片找货。它证明 discovery layer 并非空白，但定位偏跨境卖家采购，不是中立的美国消费者购买路由。  
[https://www.aiprice.com/information/index/page/about](https://www.aliprice.com/information/index/page/about)  
[https://chromewebstore.google.com/detail/aipricealiprice%E8%B7%A8%E5%A2%83%E5%8D%96%E5%AE%B6%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/lenipkahddombkldhfmcnnjakmcepdlk](https://chromewebstore.google.com/detail/aipricealiprice%E8%B7%A8%E5%A2%83%E5%8D%96%E5%AE%B6%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/lenipkahddombkldhfmcnnjakmcepdlk) :chatgpt-content-reference{index="9"}

4. **[INFERENCE] 真正没有看到公开规模化证据的是这一整条链同时成立：美国消费者 intent → exact identity → 中国国内 catalog → 实时可买价格 → forwarding/tax/volumetric landed cost → 与美国渠道中立比较 → 一键执行。** 本次 bounded search 只能说明“未发现公开 dominant product”，不能证明私人公司、stealth 产品或未索引产品绝对不存在。

5. **Confirmed 的结构障碍首先是上游平台依赖。** ezbuy 曾获 US$20m B 轮，并拥有数百万用户；但 2017 年其大量 Taobao 采购账号和仓库地址被限制，导致 Buy-For-Me 服务中断。Alibaba 对媒体称相关行为涉及其所称的“scalping/代购规则”问题。此事证明规模化代理可以遭遇 source-platform counterparty shock。反证是：ezbuy 后来仍以约 **US$85.55m** 对价被 LightInTheBox 收购，所以这并不是“代理模式被证明失败”。 :chatgpt-content-reference{index="10"}

6. **Probable，而不是 Confirmed：行业被按用户和盈利模式拆层。** Superbuy/Baopals 做消费者代购履约；AiPrice/DSers/BuckyDrop 做商家采购自动化；Honey 证明购物扩展本身可以做到千万级 MAU。缺口更像“跨层 orchestration + identity + reliable landed-cost state + consumer monetization”，而不是“没人想到浏览器插件”或“物流基础设施不存在”。 :chatgpt-content-reference{index="11"}

# 2. Evidence table

| 结论 | 证据 / 日期 | 置信度 | 反证 |
|---|---|---|---|
| Amazon↔Taobao 比价早已被尝试 | PriceDoge，2019；标题匹配“similar products” | 高 | 不是严格 exact-SKU；GitHub 当前仅 72 stars |
| 2026 已有 Amazon→1688+landed-cost 产品 | GP/IK 等当前 Chrome listings | 高 | 用户数极小，且面向 seller/importer |
| 数据访问/匹配是持续摩擦 | PriceDoge 用 Puppeteer；Shopping Hub 记录登录、滑块、限流/API约束 | 中 | Baopals 明示部分商品信息来自平台 API，故“无法正规接入”不能普遍成立 |
| 上游平台能打断大型代理 | ezbuy 2017 批量账号/仓址被限制 | 高 | ezbuy 有 >3m customers 且随后被收购 |
| 法律/安全暴露真实存在 | UODO：约 130 万 Pandabuy 用户数据事件；2026 美案仍有程序进展 | 高（事件） | 法院此前在相关 Pandabuy 分析中曾因其偏被动 facilitator 而解除 PI，不能写成“代理必然承担卖家责任” |
| 浏览器扩展不是天然增长瓶颈 | Honey 2019 约 17m MAU，PayPal 约 US$4b 收购 | 高 | Honey 的 affiliate/merchant economics 与 China-direct router 不同 |

# 3. Primary sources

最关键 primary evidence：PriceDoge 官方 GitHub；Superbuy 官方 about；Baopals 当前站及隐私政策；AiPrice 官方页面；DSers/BuckyDrop 当前官方资料；ezbuy 自身 2017 service-disruption statement；SEC 的 ezbuy 收购文件；PayPal 的 Honey 收购公告；波兰 UODO 2026-09-29 公告。Baopals 隐私政策尤其构成反证：其称部分商品/店铺数据由电商平台通过 API 提供，因此“只能非法 scraping，所以没人能做”不成立。 :chatgpt-content-reference{index="12"}

# 4. Forum / community evidence

PriceDoge 作者在 2019 V2EX 帖中直接承认：跨站查询基于标题，优惠券/满减、商品内部 ID 等会让最终价格与匹配复杂；其计划中的 P2P price-sharing 没继续，一项明确原因是“没有足够多的用户量”并且作者时间有限。这是**一个项目的失败机制证据**，不能升级成全市场 CAC 结论。当前 Shopping Hub GitHub 又独立记录了 Taobao/Tmall/1688 匿名抓取所遇到的登录、滑块验证码以及 API/限流问题。 :chatgpt-content-reference{index="13"}

# 5. Contrary evidence

对“为什么不存在”的浅层解释，证据有明显反驳：  
**“技术做不到”**——AiPrice 和 2026 的 GP/IK 已做到相当部分；**“没有代购基础设施”**——Superbuy 自 2012 年运营，Baopals 当前公开展示大量历史订单；**“extension 用户不会装”**——Honey 曾有约 17m MAU；**“平台一定不给数据”**——Baopals 披露存在 API 来源；**“法律必然把代理当 retailer”**——Pandabuy 相关法院材料并不支持这种绝对说法。 :chatgpt-content-reference{index="14"}

# 6. Confidence

**高置信度：** 概念已有多次实现；供应/代购/扩展各层均存在成熟参与者；ezbuy 证明 source-platform dependency 能造成真实规模性中断。  
**中置信度：** dominant consumer router 缺失主要来自多层数据状态、身份解析、平台依赖及商业激励同时耦合。  
**低置信度：** “中立比价与 affiliate monetization 天然冲突”“消费者获客成本过高”——目前没有足够失败案例证明因果。

# 7. Data gaps

`AUTHENTICATED DATA REQUIRED`：本研究未登录 Taobao/Tmall/JD，无法验证 2026 各平台对第三方搜索/API 的完整权限边界。Wegobuy 主页本次无法可靠打开；JadeShip 将其列为 legacy，但属于第三方，因此其当前状态 **UNVERIFIED**。Sugargoo/CSSBuy/CNFans 公共页面可触达但本轮没有提取到足以审计其历史/规模的 primary text。没有付费 VC 数据库、公司内部数据、创始人访谈或 Chrome 安装历史时间序列，因此可能遗漏已关闭/stealth 尝试。

# 8. Most surprising finding

最令人意外的不是“没人做”，而是**2026 年已经出现多个几乎贴着该架构边界的微型产品，却仍停留在卖家/power-user niche**。因此正确问题应从 *Why doesn’t this exist?* 改成：

> **Why has this repeatedly existed, but not crossed from sourcing/proxy tooling into a mainstream neutral consumer router?**

# 9. What would falsify this conclusion?

以下任一证据会显著改变判断：①发现已有 >100 万美国消费者使用的 neutral US→China landed-cost router；②证明国内平台可通过稳定官方 API 获得全量实时价格与身份数据，且不存在显著平台依赖；③找到大型同类 consumer startup 的关闭材料，明确证明唯一主因是“消费者没有需求”；④证明 ezbuy 2017 事件与规模化代购架构无关、纯属一次孤立违规；⑤证明 exact identity + landed cost 在现实中已被某通用基础设施商品化成低成本稳定 API。

# 10. Suggested next experiment

只再做一个 W7 实验，我会做**2015–2026 competitor archaeology**：固定一份结构化名单，利用官方公司记录、Chrome 商店历史、GitHub commit/release、Wayback/公开融资与收购记录，逐个重建“上线→用户规模→商业模式→pivot/停止→可证明原因”。目标不是再找更多现存工具，而是确认**是否存在被今天搜索结果埋掉的、已经真正测试过 consumer-first neutral routing 的失败公司**。这会直接区分“市场没人完整做过”和“做过但被某个结构机制杀死”。

```json
{
  "job_id": "W7-B",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://github.com/DimensionDev/PriceDoge",
      "title": "DimensionDev/PriceDoge",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03"]
    },
    {
      "source_id": "S02",
      "url": "https://www.v2ex.com/t/547246",
      "title": "PriceDoge creator discussion on V2EX",
      "published_at": "2019-03-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03"]
    },
    {
      "source_id": "S03",
      "url": "https://www.aiprice.com/information/index/page/about",
      "title": "AiPrice About",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C08"]
    },
    {
      "source_id": "S04",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice%E8%B7%A8%E5%A2%83%E5%8D%96%E5%AE%B6%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/lenipkahddombkldhfmcnnjakmcepdlk",
      "title": "AiPrice/AliPrice Chrome Web Store listing",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C08"]
    },
    {
      "source_id": "S05",
      "url": "https://chromewebstore.google.com/detail/gp-sourcing-dropshipping/habbjbbidapgddblimhdjjgpnceeihab",
      "title": "GP Sourcing — Dropshipping Chrome extension",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S06",
      "url": "https://chromewebstore.google.com/detail/ik-sourcing-%E2%80%94-1688-profit/kdmdebiinfbkgmncenjcjfafdagkkikd",
      "title": "IK Sourcing — 1688 Profit Chrome extension",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C09"]
    },
    {
      "source_id": "S07",
      "url": "https://chromewebstore.google.com/detail/amazon-to-1688-sourcing-a/bkggnbelomjlmjnmiffalchkocnkijbn",
      "title": "Amazon to 1688 Sourcing Assistant",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S08",
      "url": "https://github.com/aon082910/shopping-hub",
      "title": "Shopping Hub",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C09"]
    },
    {
      "source_id": "S09",
      "url": "https://www.superbuy.com/en/page/about/aboutus/",
      "title": "Superbuy About Us",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C08"]
    },
    {
      "source_id": "S10",
      "url": "https://www.baopals.com/",
      "title": "Baopals",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C08"]
    },
    {
      "source_id": "S11",
      "url": "https://www.baopals.com/privacy",
      "title": "Baopals Privacy Policy",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C05"]
    },
    {
      "source_id": "S12",
      "url": "https://www.businesstimes.com.sg/startups-tech/technology/2-online-shopping-sites-bag-venture-funding",
      "title": "2 online shopping sites bag venture funding",
      "published_at": "2016-03-23",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S13",
      "url": "https://www.acnnewswire.com/press-release/english/40224/media-statement:-ezbuy.sg---update-on-service-disruption",
      "title": "Media Statement: ezbuy.sg - Update on Service Disruption",
      "published_at": "2017-12-08",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S14",
      "url": "https://www.straitstimes.com/singapore/singapore-based-ezbuys-founder-accuses-taobao-of-bullying-alibaba-responds",
      "title": "Singapore-based ezbuy's founder accuses Taobao of bullying; Alibaba responds",
      "published_at": "2017-12-09",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S15",
      "url": "https://www.sec.gov/Archives/edgar/data/1523836/000110465918066939/a18-39726_1ex99d1.htm",
      "title": "LightInTheBox agreement to acquire Ezbuy",
      "published_at": "2018-11-08",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C05"]
    },
    {
      "source_id": "S16",
      "url": "https://newsroom.paypal-corp.com/paypal-to-acquire-honey",
      "title": "PayPal to Acquire Honey",
      "published_at": "2019-11-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S17",
      "url": "https://help.dsers.com/what-is-dsers-a-quick-overview-for-beginners/",
      "title": "What is DSers? A Quick Overview for Beginners",
      "published_at": "2026-05-25",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S18",
      "url": "https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/",
      "title": "US Dropshipping Fulfillment Cost",
      "published_at": "2026-09-15",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08", "C09"]
    },
    {
      "source_id": "S19",
      "url": "https://www.uodo.gov.pl/pl/138/4589",
      "title": "Polish data protection authority page concerning Pandabuy customer data incident",
      "published_at": "2026-09-29",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S20",
      "url": "https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2024cv02668/619156/185",
      "title": "Federal court filing concerning Pandabuy defendants",
      "published_at": "2026-04-15",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S21",
      "url": "https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2024cv08336/631089/68",
      "title": "Federal court order discussing Pandabuy facilitator analysis",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S22",
      "url": "https://www.jadeship.com/",
      "title": "JadeShip",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "Amazon-to-Taobao/JD cross-platform comparison was actually implemented by PriceDoge by 2019.",
      "classification": "FACT",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "PriceDoge described title-based similar-product search rather than guaranteed exact-SKU identity resolution, and its public GitHub footprint is small."
    },
    {
      "claim_id": "C02",
      "claim": "By 2026 multiple public tools implement substantial portions of Amazon-to-China sourcing, including Amazon-to-1688 matching and in some cases landed-cost estimation.",
      "classification": "FACT",
      "source_ids": ["S03", "S04", "S05", "S06", "S07"],
      "confidence": "high",
      "counterevidence": "The closest 2026 Chrome extensions observed have very small public user counts and are primarily seller/importer tools rather than mainstream consumer routers."
    },
    {
      "claim_id": "C03",
      "claim": "Product identity, dynamic price state, authentication, CAPTCHA, rate limiting and source-platform access are recurring technical frictions, but authorized/API-based access can mitigate at least some of them.",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02", "S08", "S11"],
      "confidence": "medium",
      "counterevidence": "Baopals states that some shop and product information is supplied via e-commerce-platform APIs, so platform access should not be characterized as universally impossible."
    },
    {
      "claim_id": "C04",
      "claim": "A scaled buying-agent business can suffer severe operational disruption from source-platform counterparty actions; ezbuy experienced large-scale Taobao account and warehouse-address restrictions in 2017.",
      "classification": "FACT",
      "source_ids": ["S12", "S13", "S14", "S15"],
      "confidence": "high",
      "counterevidence": "Ezbuy had millions of customers and was subsequently acquired; the incident therefore does not establish that the agent model itself is commercially nonviable."
    },
    {
      "claim_id": "C05",
      "claim": "Consumer proxy-purchasing and forwarding infrastructure already exists at meaningful scale, so absence of forwarding infrastructure alone does not explain the missing neutral router.",
      "classification": "INFERENCE",
      "source_ids": ["S09", "S10", "S11", "S15"],
      "confidence": "high",
      "counterevidence": "Existing agents optimize their own procurement/forwarding workflows rather than proving that a channel-neutral U.S.-consumer comparison layer is economically attractive."
    },
    {
      "claim_id": "C06",
      "claim": "Browser-extension distribution is not by itself a structural reason a shopping-assistance product cannot reach mass scale.",
      "classification": "INFERENCE",
      "source_ids": ["S16"],
      "confidence": "high",
      "counterevidence": "Honey's merchant and affiliate economics differ substantially from a China-direct neutral routing product."
    },
    {
      "claim_id": "C07",
      "claim": "Security and litigation exposure are real risks for proxy-shopping platforms, but available court evidence does not establish that a passive facilitator is necessarily treated like the underlying seller or manufacturer.",
      "classification": "INFERENCE",
      "source_ids": ["S19", "S20", "S21"],
      "confidence": "medium",
      "counterevidence": "Pandabuy-related proceedings and default issues show continuing legal exposure, while prior judicial analysis cited in related litigation cut against an automatic seller-equivalence theory."
    },
    {
      "claim_id": "C08",
      "claim": "Commercialization is currently fragmented across consumer agents, seller sourcing tools, dropshipping automation and agent interoperability rather than concentrated in one neutral U.S.-consumer routing layer.",
      "classification": "INFERENCE",
      "source_ids": ["S03", "S04", "S09", "S10", "S17", "S18", "S22"],
      "confidence": "medium",
      "counterevidence": "Bounded public-web research cannot rule out private, stealth, mobile-only or poorly indexed integrated competitors."
    },
    {
      "claim_id": "C09",
      "claim": "The closest publicly visible 2026 tools suggest that landed-cost computation itself is implementable; the unresolved scaling problem appears to be integration of reliable identity, data state, execution, platform access and consumer distribution.",
      "classification": "INFERENCE",
      "source_ids": ["S05", "S06", "S08", "S18"],
      "confidence": "medium",
      "counterevidence": "The observed products are tiny or seller-focused, so their existence does not prove the same architecture works economically for ordinary U.S. consumers."
    },
    {
      "claim_id": "C10",
      "claim": "A neutrality-versus-affiliate or merchant-funded monetization conflict may help explain why sourcing/comparison products cluster around sellers and affiliate workflows rather than neutral consumer routing.",
      "classification": "HYPOTHESIS",
      "source_ids": ["S03", "S16", "S17", "S18"],
      "confidence": "low",
      "counterevidence": "No identified failed company directly attributed its failure to this incentive conflict; alternative explanations such as data reliability, operations or insufficient consumer demand remain viable."
    }
  ],
  "categories": [
    {
      "category": "cross_market_discovery_comparison",
      "representatives": ["PriceDoge", "AiPrice/AliPrice"],
      "structural_role": "same-or-similar product discovery across marketplaces",
      "current_or_historical_scale_signal": {
        "aiprice_chrome_users_at_retrieval": 200000,
        "pricedoge_github_stars_at_retrieval": 72
      },
      "source_ids": ["S01", "S03", "S04"]
    },
    {
      "category": "seller_sourcing_and_landed_cost",
      "representatives": ["GP Sourcing", "IK Sourcing", "Amazon to 1688 Sourcing Assistant", "DSers", "BuckyDrop"],
      "structural_role": "China sourcing, supplier matching, fulfillment and in some cases landed-cost estimation",
      "current_or_historical_scale_signal": {
        "gp_sourcing_chrome_users_at_retrieval": 56,
        "ik_sourcing_chrome_users_at_retrieval": 5,
        "amazon_to_1688_chrome_users_at_retrieval": 8
      },
      "source_ids": ["S05", "S06", "S07", "S17", "S18"]
    },
    {
      "category": "consumer_proxy_and_forwarding",
      "representatives": ["Superbuy", "Baopals", "ezbuy"],
      "structural_role": "proxy purchasing, warehousing, international forwarding and consumer-facing execution",
      "current_or_historical_scale_signal": {
        "ezbuy_customers_reported_2018": 3000000,
        "baopals_happy_customers_self_reported_at_retrieval": 142477,
        "baopals_orders_self_reported_at_retrieval": 1904954,
        "baopals_goods_delivered_self_reported_at_retrieval": 7012337
      },
      "source_ids": ["S09", "S10", "S12", "S15"]
    },
    {
      "category": "agent_interoperability",
      "representatives": ["JadeShip"],
      "structural_role": "agent-agnostic link conversion and navigation across multiple buying agents",
      "current_or_historical_scale_signal": {
        "agents_claimed_supported": 35
      },
      "source_ids": ["S22"]
    },
    {
      "category": "mainstream_shopping_assistant",
      "representatives": ["Honey"],
      "structural_role": "browser-based shopping assistance and merchant-funded savings",
      "current_or_historical_scale_signal": {
        "monthly_active_users_2019": 17000000,
        "announced_acquisition_value_usd": 4000000000
      },
      "source_ids": ["S16"]
    },
    {
      "category": "open_source_multi_market_landed_cost",
      "representatives": ["Shopping Hub"],
      "structural_role": "multi-market search, matching, landed-cost estimation and agent deep linking",
      "current_or_historical_scale_signal": {
        "github_stars_at_retrieval": 6,
        "github_commits_at_retrieval": 58
      },
      "source_ids": ["S08"]
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "Current authenticated access behavior for Taobao, Tmall, JD and related ranking/search endpoints was not tested.",
      "status": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap": "No paid venture/startup database was accessed, so stealth or discontinued companies may be missing.",
      "status": "UNRESOLVED"
    },
    {
      "gap": "Wegobuy could not be reliably opened in this session; third-party legacy labels are insufficient to establish current corporate status.",
      "status": "UNVERIFIED"
    },
    {
      "gap": "Sugargoo, CSSBuy and CNFans public sites were reachable but this bounded session did not obtain sufficiently auditable primary history or scale data to make material claims about them.",
      "status": "UNRESOLVED"
    },
    {
      "gap": "No Chrome extension install-history time series was available; reported user counts are retrieval-time snapshots only.",
      "status": "UNRESOLVED"
    },
    {
      "gap": "No founder interviews, direct company contacts, purchases, quotations or paid datasets were used.",
      "status": "UNRESOLVED"
    },
    {
      "gap": "Public evidence does not establish causal consumer acquisition economics for a neutral U.S.-to-China routing product.",
      "status": "UNRESOLVED"
    },
    {
      "gap": "The browsing interface does not expose exact per-source retrieval timestamps; only the overall session retrieval window 2026-10-06T22:38:37Z to 2026-10-06T22:46:54Z was independently recorded, so per-source retrieved_at fields are null.",
      "status": "UNRESOLVED"
    }
  ],
  "pre_freeze_compliance": true
}
```