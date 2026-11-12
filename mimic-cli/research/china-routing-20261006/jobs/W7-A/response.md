# 1. Direct answer

**结论：核心命题“没人做过 Amazon→中国国内同款比较”是错的；“至今没有形成主导型、面向美国消费者、能在浏览时给出可信 landed cost 并完成中立路由的产品”则成立。**

至少已有四类非常接近的组件：2019 年开源 **PriceDoge** 已在浏览商品页时跨 Amazon、JD、Newegg、Taobao 搜索；2026 年 **1688 官方采购助手** 已支持 1688/Taobao/Amazon/AliExpress/Alibaba 图片跨平台比价，Chrome 用户约 20 万；**AiPrice** 约 10 万用户，也做 Amazon↔1688/Taobao 等图搜/价格分析；**DSers** 现在甚至明确提供 AliExpress 页面截图→Amazon/Taobao/1688 等同款比价。:chatgpt-content-reference{index="0"}

最接近本研究设想的是 **HandHunt “Buy from China”**：用户浏览 Amazon、Etsy、eBay、Walmart、Temu、AliExpress 时，一键寻找 1688/Taobao 同款或相似款，并进入其中国代购平台。但 Chrome 商店只有约 **19 用户**，版本 1.0.0，最后更新 2025-04-21；更关键的是，它仍要求货物先到仓、实测尺寸重量后再第二次支付国际运费。官网甚至专门回答“为什么最后国际运费比预期贵”。这说明“海外页面→中国 sourcing→代购”已被真实尝试，而**浏览时确定 landed cost**仍是断点。:chatgpt-content-reference{index="1"}

本轮可核实会话时间标记：开始阶段 **2026-10-06T22:37Z（分钟精度）**，结束阶段 **2026-10-06T22:42:26Z**。网页工具不暴露逐页 UTC 抓取时刻，因此下方 JSON 的逐源 `retrieved_at` 均为 `null`，没有伪造。最新观察到的产品数据日期为 **2026-09-28**（Capital One Shopping 更新）。

# 2. Evidence table

| Claim | Evidence | Date | Confidence | Counterevidence |
|---|---|---:|---|---|
| “没人试过”不成立 | PriceDoge 2019 已支持 Amazon/JD/Taobao；1688 官方插件现有 Amazon/Taobao/AliExpress 跨平台比价 | 2019-03-22；2026-09-20 | High | 两者都不是完整 landed-cost routing |
| 最接近完整 thesis 的产品已有 | HandHunt 可从 Amazon/Temu 等页面找中国同/类似商品并接代购 | 2025-04-21 | High | 商店仅约19用户；没有预购买最终运费 |
| 比价 extension 本身可以规模化 | Capital One Shopping Chrome 约1100万用户；1688插件约20万；AiPrice约10万 | 2026-09-28等 | High | 规模不能证明 China-direct consumer routing 有需求 |
| 数据访问不是稳定公共基础设施 | 淘宝禁止未经许可的机器人/爬虫/模拟用户获取内容；AiPrice 明示淘宝/1688验证会导致图搜失败/账号异常 | 2025-12-12生效；页面2026-09 | High | 1688 自己提供官方插件，说明合作/官方路径存在 |
| Amazon 官方 affiliate 数据不天然适合“中立路由” | Associates 条款限制 price tracking、浏览器插件中的 Program Content，并禁止用其内容推广非 Amazon 商品 | 2026-04-14 | High | Capital One 等证明可通过其他数据/商业路径做跨店比价 |
| landed cost 的关键变量晚于商品发现出现 | Superbuy/HandHunt 都是先采购入仓，再按包装、重量、线路提交 parcel/二次付款 | current | High | Shipping calculator 可给参考估值，并非完全不可预测 |
| IP 风险真实但不是“agent 模式天然违法” | Pandabuy 曾受禁令；但后续法院解除禁令；2026 AllChinaBuy 案亦认定此类结构更接近 passive facilitator | 2024–2026 | High | contributory liability、具体事实及其他法域风险仍可能不同 |
| 失败案例不能证明 economics 已被证伪 | Wegobuy 2025 起消失，但2026调查仍找不到可信关闭原因 | checked 2026-06-06 | Medium | 用户报告502、邮件退信及滞留余额，运营连续性风险确实存在 |

# 3. Primary sources

最重要的一级证据是：**1688官方插件、Amazon Associates政策、淘宝法律声明、Superbuy/HandHunt流程、DSers/BuckyDrop产品页及联邦法院裁判**。它们共同显示市场并非缺少搜索、比价、采购或履约技术，而是这些能力目前被拆在不同商业主体和权限边界中。:chatgpt-content-reference{index="2"}

竞争架构已经明显分层：Capital One 是消费者优惠/affiliate；1688/AiPrice/DSers 是采购与卖家 sourcing；Superbuy 是“给链接→采购→仓库→转运”；BuckyDrop 面向 Shopify/WooCommerce/API 商户。**没有证据表明其中任何一家已把“美国消费者中立比较 + exact identity + 中国国内采购 + 预购 landed cost”做成大规模一体化产品。**这是 FACT（产品现状）加 INFERENCE（产业分层原因），不是“无人想到”。:chatgpt-content-reference{index="3"}

# 4. Forum evidence

PriceDoge 的 V2EX 发布帖（2019-03-22）直接说明其目标是跨 JD/Taobao/Amazon/Newegg 比价；作者还提到因为**用户量不足**，设想中的 P2P 价格分享无法一开始启动。这是一个小型历史实验对 acquisition/bootstrap 难题的直接证据，但不能外推为大众市场不存在。:chatgpt-content-reference{index="4"}

Wegobuy 社区在 2025 年报告全站 502、邮件退信、仓库/余额未解决；但关于“老板被捕/为何关闭”等说法缺乏可靠一级来源，应保持 **UNVERIFIED**。:chatgpt-content-reference{index="5"}

# 5. Contrary evidence

反证非常强。第一，**Capital One Shopping 约1100万 Chrome 用户**说明“浏览时自动比价”绝非没人要。第二，1688 官方自己把 Amazon、Taobao、AliExpress 纳入比价，说明技术上跨生态匹配不是不可做。第三，2026 AllChinaBuy 裁判援引 Pandabuy 案，认为没有制造、持有库存或以卖家身份出现的中介可能更像 passive facilitator；所以不能把 Pandabuy 事件概括为“代购路由模式在美国天然违法”。:chatgpt-content-reference{index="6"}

# 6. Confidence

**High：**“已有大量相邻/近似产品”“数据访问与验证是实质工程约束”“最终物流费用晚于发现阶段才能精确确定”“现有商业模式被分割在 consumer affiliate / seller SaaS / buying-agent 三侧”。

**Medium：**“没有 dominant product 的主因是权限、身份匹配、动态物流报价、变现激励和 IP/运营风险的组合，而非单一原因。”

**Low：**“美国主流消费者需求不足”“CAC过高”“消费者只要便利”等解释——本 W7 没有硬证据，不应列为 confirmed。

# 7. Data gaps

未找到可信的 VC/融资数据库证据证明曾有一家获风投公司明确以“Amazon→Taobao landed-cost comparison”为核心 thesis；**AUTHENTICATED/PAID DATA REQUIRED** 才能系统核实 PitchBook/Crunchbase 私有历史。

HandHunt 的约19用户证明分发很弱，但没有 retention、GMV、conversion、CAC，不能判断是产品失败还是几乎未推广。Wegobuy 的关闭原因仍 **UNVERIFIED**。此外，公开资料不足以判断各平台是否愿意给一个中立 comparison layer 商业 API/redistribution license。

# 8. Most surprising finding

最意外的不是某个失败公司，而是 **1688 本身在 2026 年已经官方发布带 Amazon/Taobao/AliExpress 跨平台图片比价的 Chrome 插件**，且约20万用户。与此同时，HandHunt 已把“在 Amazon 等页面找中国货源→代购”真正做成插件。由此看，创新空间若存在，已经不主要在“发现中国同款”，而更可能集中在**可靠 exact-match、权限稳定性、预购 landed cost 和中立成交路由**。:chatgpt-content-reference{index="7"}

# 9. What could make this conclusion wrong?

1. 若发现一家未被公开网页索引的大型产品已经完成 exact-match + landed-cost + consumer routing，本报告对“缺失层”的判断会失效。
2. 若商业 API 合同可轻易、低成本取得 Amazon/Taobao/JD 全量实时字段，数据权限障碍被高估。
3. 若真实包裹重量/体积能从 catalog 高精度预估，landed-cost 时序障碍被高估。
4. 若 HandHunt/类似项目其实有大量 App/非Chrome流量，19-user 信号严重低估采用率。
5. 若后续法院明确把 routing/agent 架构广泛认定为 seller/contributory infringer，当前对法律边界的判断会过于乐观。

# 10. Suggested next experiment

只做一个 **“data-permission / quote-certainty structural spike”**，仍不检查任何冻结前 SKU：逐平台建立字段级矩阵——商品身份、variant、实时价格、境内运费、重量/尺寸、库存、图片、重分发权、自动化访问权——分别标记 `official API / licensed only / browser-accessible / prohibited / authenticated required`；同时让 Superbuy/HandHunt 式公开计算器在**合成重量/尺寸输入**下测试报价可重复性。成功标准不是“找到便宜货”，而是回答：**一个中立 consumer router 能否在购买前、无需违规抓取的情况下生成足够可靠且可持续使用的数据对象。**

**W7-A verdict：**“为什么没有 dominant company”目前最有证据支持的答案不是 convenience/trust，而是**已有组件被商业激励、平台数据许可和物流状态时序切割**；IP/运营事件提高风险，但没有证据证明轻量 routing 架构本身被法律或技术单点封死。置信度：**Medium-High**。

```json
{
  "job_id": "W7-A",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://chromewebstore.google.com/detail/1688%E5%AE%98%E6%96%B9%E9%87%87%E8%B4%AD%E5%8A%A9%E6%89%8B/kphldkppgfpjadpabfkghmjbhpcmgpdg?hl=en",
      "title": "1688 Purchasing Assistant Plugin - Chrome Web Store",
      "published_at": "2026-09-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03", "C09"]
    },
    {
      "source_id": "S02",
      "url": "https://github.com/DimensionDev/PriceDoge",
      "title": "DimensionDev/PriceDoge",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S03",
      "url": "https://v2ex.com/t/547246",
      "title": "PriceDoge launch discussion on V2EX",
      "published_at": "2019-03-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C08"]
    },
    {
      "source_id": "S04",
      "url": "https://chromewebstore.google.com/detail/buy-from-china-handhunt/kkclaagbdmhkeaenndgfkbkbkfipfold",
      "title": "Buy from China - HandHunt - Chrome Web Store",
      "published_at": "2025-04-21",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S05",
      "url": "https://handhunt.ai/",
      "title": "HandHunt - Chinese Products Sourcing and Dropshipping",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C06"]
    },
    {
      "source_id": "S06",
      "url": "https://handhunt.ai/manual/handhunt-purchasing-service",
      "title": "Purchasing service Of HandHunt",
      "published_at": "2024-06-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C06"]
    },
    {
      "source_id": "S07",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj?hl=en-US",
      "title": "AiPrice(AliPrice) Search by Image for China Import - Chrome Web Store",
      "published_at": "2026-08-15",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03", "C05"]
    },
    {
      "source_id": "S08",
      "url": "https://www.aiprice.com/information/index/page/helps",
      "title": "AiPrice Help Center",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S09",
      "url": "https://chromewebstore.google.com/detail/capital-one-shopping-save/nenlahapcbofgnanklpelkaejcehkggg?gl=US&hl=en-US",
      "title": "Capital One Shopping: Save Now - Chrome Web Store",
      "published_at": "2026-09-28",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C10"]
    },
    {
      "source_id": "S10",
      "url": "https://affiliate-program.amazon.com/help/operating/policies?ac-ms-src=ac-nav",
      "title": "Amazon Associates Program Policies",
      "published_at": "2026-04-14",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C05"]
    },
    {
      "source_id": "S11",
      "url": "https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201811121436_80276.html",
      "title": "淘宝网法律声明",
      "published_at": "2025-12-12",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S12",
      "url": "https://www.superbuy.com/en/page/about/aboutus/",
      "title": "About Superbuy",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C09"]
    },
    {
      "source_id": "S13",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fee Structure",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C06"]
    },
    {
      "source_id": "S14",
      "url": "https://www.dsers.com/en/dsers-chrome-extension",
      "title": "DSers Chrome Extension",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C09"]
    },
    {
      "source_id": "S15",
      "url": "https://www.buckydrop.com/en/",
      "title": "BuckyDrop | All-in-One Auto Dropshipping Platform",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C09"]
    },
    {
      "source_id": "S16",
      "url": "https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2024cv08336/631089/68/",
      "title": "RVRG Holdings LLC v. Hangzhou Taohaowu Technology Co. et al., Document 68",
      "published_at": "2026-03-11",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S17",
      "url": "https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2024cv02668/619156/80",
      "title": "King Spider LLC v. Panda (Hong Kong) Technology Co., Ltd. - Preliminary Injunction Order",
      "published_at": "2024-07-10",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S18",
      "url": "https://kakoguide.com/agents/wegobuy",
      "title": "Wegobuy Review 2026: Fees, Payment & Verdict",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S19",
      "url": "https://www.reddit.com/r/WegobuyOfficial/comments/1i6b3yp/wegobuy_status_and_future/",
      "title": "WeGoBuy status and future? - Reddit",
      "published_at": "2025-01-21",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S20",
      "url": "https://chromewebstore.google.com/detail/goodscouter-google-lens-a/gplmnpekfefelffdjabffhicllemehpl",
      "title": "Goodscouter: Image Search & Price Comparison - Chrome Web Store",
      "published_at": "2026-08-12",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C03"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "Amazon/全球电商页面与淘宝、1688、JD等中国平台之间的跨平台同款搜索和价格比较已经被多次实际实现，因此“没人尝试过”不成立。",
      "classification": "FACT",
      "source_ids": ["S01", "S02", "S03", "S07", "S14", "S20"],
      "confidence": "high",
      "counterevidence": "这些产品大多面向采购或卖家，且通常不提供面向美国消费者的最终landed cost与中立成交路由。"
    },
    {
      "claim_id": "C02",
      "claim": "HandHunt是本轮发现最接近目标架构的公开实例：从Amazon、Temu等海外页面寻找1688/淘宝同款或相似商品并连接中国代购，但其公开Chrome采用规模极小，且国际运费仍在入库后确定。",
      "classification": "FACT",
      "source_ids": ["S04", "S05", "S06"],
      "confidence": "high",
      "counterevidence": "Chrome用户数不代表其全部网站、App或B2B流量，也不能单独证明产品市场需求失败。"
    },
    {
      "claim_id": "C03",
      "claim": "消费者浏览器比价和中国供应链跨平台比价本身都可以获得显著采用，因此单纯的UI、用户不会安装插件或用户不理解比价并不是有证据支持的核心阻碍。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S07", "S09", "S20"],
      "confidence": "high",
      "counterevidence": "相邻产品的采用并不证明美国消费者愿意接受中国直购的交付、退货和跨境风险。"
    },
    {
      "claim_id": "C04",
      "claim": "稳定的数据取得是结构性约束：淘宝公开法律声明限制未经许可的爬虫、机器人及模拟用户获取内容；第三方工具也记录了淘宝和1688验证、账号异常导致功能失败；Amazon官方affiliate数据亦有严格使用限制。",
      "classification": "FACT",
      "source_ids": ["S08", "S10", "S11"],
      "confidence": "high",
      "counterevidence": "1688官方插件表明通过官方产品或商业合作可以获得部分跨平台能力，因此这不是绝对技术封锁。"
    },
    {
      "claim_id": "C05",
      "claim": "现有玩家的变现激励彼此错位：Amazon affiliate体系希望流量回到Amazon，AiPrice存在广告链接跳转，BuckyDrop/DSers服务卖家，而购买代理主要从采购和物流环节获利；一个真正中立的消费者路由器需要新的数据和收入安排。",
      "classification": "INFERENCE",
      "source_ids": ["S07", "S10", "S15"],
      "confidence": "medium",
      "counterevidence": "Capital One Shopping证明多商户affiliate网络可以支撑大型中立度较高的比较产品，故变现冲突并非不可解。"
    },
    {
      "claim_id": "C06",
      "claim": "可靠landed cost存在时序问题：购买代理通常在国内货物入仓、重新打包并测量实际重量和体积后才确定最终国际运费，因此浏览商品页时的全包价格天然包含估计误差。",
      "classification": "FACT",
      "source_ids": ["S05", "S06", "S12", "S13"],
      "confidence": "high",
      "counterevidence": "公开shipping calculator和历史包裹数据理论上可提供预估值，问题是精度而非完全不可计算。"
    },
    {
      "claim_id": "C07",
      "claim": "知识产权执法是购买代理规模化的真实风险，但现有美国判例并不支持“代理/路由模式天然等同卖家并必然承担直接商标侵权责任”的简单结论。",
      "classification": "FACT",
      "source_ids": ["S16", "S17"],
      "confidence": "high",
      "counterevidence": "直接侵权只是法律风险的一部分；contributory infringement、特定品牌事实、其他法域及平台政策仍可能产生重大责任。"
    },
    {
      "claim_id": "C08",
      "claim": "Wegobuy等消失案例证明购买代理存在运营连续性和托管风险，但公开证据不足以把其关闭归因于特定法律事件或失败的商业经济性。",
      "classification": "FACT",
      "source_ids": ["S18", "S19"],
      "confidence": "medium",
      "counterevidence": "社区确实报告502错误、邮件退信、余额与仓库货物问题，说明最终用户遭受的连续性风险并非理论问题。"
    },
    {
      "claim_id": "C09",
      "claim": "截至本轮研究，最有证据支持的“无主导产品”解释是功能被分割在消费者比价、采购工具、卖家SaaS和购买代理之间，并同时受到数据许可和动态物流报价的约束，而不是一个单一不可逾越的技术障碍。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S12", "S14", "S15"],
      "confidence": "medium",
      "counterevidence": "尚未取得完整创业失败数据库、融资数据库或内部经营数据，因此不能排除CAC、retention或需求不足才是最终决定因素。"
    },
    {
      "claim_id": "C10",
      "claim": "本W7研究没有硬证据证明美国消费者对这种China-direct comparison/routing产品的需求不足，因此“消费者只想要方便”“没人愿意等”只能保持为假设。",
      "classification": "HYPOTHESIS",
      "source_ids": ["S09"],
      "confidence": "medium",
      "counterevidence": "Capital One Shopping的大规模采用只证明一般在线比价需求，并不直接测量跨境中国直购意愿。"
    }
  ],
  "categories": [
    {
      "category": "consumer_price_comparison_extensions",
      "representatives": ["Capital One Shopping"],
      "primary_user": "consumer",
      "china_domestic_integration": false,
      "buying_agent_integration": false,
      "prepurchase_landed_cost": false,
      "observed_users": 11000000,
      "structural_role": "证明浏览器内自动比价可以达到大众规模"
    },
    {
      "category": "china_cross_platform_sourcing_extensions",
      "representatives": ["1688 Purchasing Assistant", "AiPrice"],
      "primary_user": "seller_or_procurement",
      "china_domestic_integration": true,
      "buying_agent_integration": false,
      "prepurchase_landed_cost": false,
      "observed_users": null,
      "structural_role": "证明Amazon与1688/Taobao等跨平台匹配和比价已经产品化"
    },
    {
      "category": "near_exact_consumer_china_router",
      "representatives": ["HandHunt Buy from China"],
      "primary_user": "consumer_and_seller",
      "china_domestic_integration": true,
      "buying_agent_integration": true,
      "prepurchase_landed_cost": false,
      "observed_users": 19,
      "structural_role": "最接近目标架构的公开实例，但采用弱且运费后置"
    },
    {
      "category": "shopping_agents",
      "representatives": ["Superbuy"],
      "primary_user": "cross_border_buyer",
      "china_domestic_integration": true,
      "buying_agent_integration": true,
      "prepurchase_landed_cost": false,
      "observed_users": null,
      "structural_role": "提供购买、QC、仓储、合包和国际运输基础设施"
    },
    {
      "category": "merchant_dropshipping_saas",
      "representatives": ["DSers", "BuckyDrop"],
      "primary_user": "merchant",
      "china_domestic_integration": true,
      "buying_agent_integration": true,
      "prepurchase_landed_cost": null,
      "observed_users": null,
      "structural_role": "已把sourcing与订单履约自动化，但商业对象是卖家而非终端消费者"
    },
    {
      "category": "open_source_historical_comparators",
      "representatives": ["PriceDoge"],
      "primary_user": "consumer",
      "china_domestic_integration": true,
      "buying_agent_integration": false,
      "prepurchase_landed_cost": false,
      "observed_users": null,
      "structural_role": "直接历史证据：2019年已有人实现Amazon/JD/Taobao跨平台比价"
    },
    {
      "category": "agent_failure_and_legal_cases",
      "representatives": ["Pandabuy", "Wegobuy", "AllChinaBuy"],
      "primary_user": "cross_border_buyer",
      "china_domestic_integration": true,
      "buying_agent_integration": true,
      "prepurchase_landed_cost": false,
      "observed_users": null,
      "structural_role": "展示IP执法、平台连续性和中介法律身份的实际边界"
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    {
      "gap": "是否存在未被公开网页索引、已获得VC融资且明确以Amazon到Taobao/1688 landed-cost comparison为核心的历史公司",
      "requirement": "AUTHENTICATED DATA REQUIRED: PitchBook/Crunchbase/公司档案或创始人历史资料"
    },
    {
      "gap": "HandHunt真实MAU、GMV、conversion、retention、CAC及非Chrome流量",
      "requirement": "公司内部数据或可信第三方analytics"
    },
    {
      "gap": "Wegobuy关闭的官方原因及用户余额/仓库资产最终处理",
      "requirement": "官方公告、公司/法院/监管记录；当前原因UNVERIFIED"
    },
    {
      "gap": "Amazon、Taobao/Tmall、JD、1688是否愿意向中立消费者比较层授予商业API和再展示权限",
      "requirement": "商业API合同或书面平台许可"
    },
    {
      "gap": "在商品入仓前利用catalog/历史包裹特征预测最终计费重量和体积的可实现误差",
      "requirement": "真实历史包裹级数据或代理商内部数据"
    },
    {
      "gap": "消费者跨境China-direct routing真实需求、留存和愿意容忍的报价误差",
      "requirement": "独立需求实验；本W7未进行"
    }
  ],
  "pre_freeze_compliance": true
}
```