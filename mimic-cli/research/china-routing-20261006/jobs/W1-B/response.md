我已严格限定在 **W1-B — US Demand Map**；未研究任何海外具体 SKU 的价格、可得性、覆盖率、进口节省或基于国际化可见性的 SKU 选择。

# W1-B — US Demand Map

**研究状态：WEB RESEARCH AVAILABLE**

**研究 as-of：2026-10-06。**

本次网页研究的可验证 UTC 时钟检查点为：

- 开始检查点：**2026-10-06T20:25:55Z**
- 中间检查点：**2026-10-06T20:32:33Z**
- 结束检查点：**2026-10-06T20:33:25Z**

网页工具没有为每一条 HTTP/source retrieval 暴露独立请求时间。因此，我不会伪造逐来源抓取秒数；后附 JSON 中逐来源 `retrieved_at` 记为 `null`。上述三个时间是真实取得的本次研究会话 UTC 时间检查点。

---

# 1. Direct answer / Bottom line

## 1.1 最重要结论

**第一，美国需求最大的候选集合可以识别，但不能诚实地做 1–18 的精确 GMV 排名。** 最有把握属于美国大需求池的，是 **C01 Smartphones、C02 Laptops/PC、C13 Automotive accessories、C14 Sports/outdoor、C16 Apparel/shoes/bags、C17 Home/household、C18 Toys/collectibles**。但这些数据分别来自 sell-through、产品市场、零售店型、家庭支出和行业追踪，边界不同；把数字直接从大到小排序会产生虚假精确度。

**第二，C16 是最明显的“规模很大、但 Census 店型数据不能当完整商品 GMV”的例子。** 2024 AIES 中，男装、女装、童装、family clothing、服饰配件、其他服装、鞋、luggage/leather goods 这些目标店型的 employer-firm sales 合计约 **$245.66B**；但这不是 C16 的完整全渠道商品 GMV——它会漏掉纯电商/general merchandise 等渠道，也不是 merchandise-line 口径。Census 自己明确提醒，按店型统计的 retail sales **不应被解释为某一商品线的总销售额**。 :chatgpt-content-reference{index="0"}  
URL：[https://data.census.gov/table/AIESBASIC2024.AIES00BASIC?codeset=naics~N0600.44](https://data.census.gov/table/AIESBASIC2024.AIES00BASIC?codeset=naics~N0600.44&utm_source=chatgpt.com)

**第三，C01 Smartphones 需求极大，但市场高度集中，不是典型的高度碎片化 middle-tail 市场。** Counterpoint 报告 Q2 2025 美国 smartphone sell-through revenue 为 **$17.5B**，ASP **$647.53**；到 Q2 2026，实际 consumer sales 同比下降 5%。与此同时，Q2 2026 shipment share 为 Apple 54%、Samsung 30%、Motorola 11%、Google 3%，四者合计约 98%；Q2 2026 五个最畅销型号合计约 53% sell-through share。也就是说，“需求非常大”和“SKU/品牌高度集中”可以同时成立。 :chatgpt-content-reference{index="2"}  
URL：[https://counterpointresearch.com/default.htm/insights/us-smartphone-sales-fall-5-percent-q2-2026](https://counterpointresearch.com/default.htm/insights/us-smartphone-sales-fall-5-percent-q2-2026?utm_source=chatgpt.com)

**第四，C02 PC/Laptops 是消费科技中最强的需求板块之一。** Circana 2026 年 1 月预计美国 consumer technology retail sales 约 **$112B**；其 2026 年 8 月更新指出 PCs 将占 2026 年美国 consumer-tech revenue **接近 20%**，notebook PC 是当年最大的增量贡献者，2025→2026 增加约 **$1.7B**。但 1 月和 8 月是不同预测批次，因此本报告没有用 `$112B × 20%` 人为制造一个精确的 PC GMV。 :chatgpt-content-reference{index="4"}  
URL：[https://www.circana.com/post/circana-us-consumer-technology-forecast-growth-driven-by-premium-products-2026](https://www.circana.com/post/circana-us-consumer-technology-forecast-growth-driven-by-premium-products-2026?utm_source=chatgpt.com)

**第五，C13 Automotive accessories 有本次最干净的 category-level all-channel evidence 之一。** SEMA 表示美国消费者 2024 年在车辆改装、个性化及 specialty-equipment 上支出约 **$52.65B**；更重要的是，SEMA 称这一市场的消费者支出已大体 **线上/线下各半**。这是少数同时有市场规模和 channel split 的 W1 类别。但它不等于整个 replacement/repair auto-parts aftermarket。 :chatgpt-content-reference{index="6"}  
URL：[https://www.sema.org/news-media/press-release/new-sema-research-2025-market-report](https://www.sema.org/news-media/press-release/new-sema-research-2025-market-report?utm_source=chatgpt.com)

**第六，C18 Toys/collectibles 也有较完整的全市场锚点。** Toy Association 引用 Circana Checkout，2025 美国 total toy industry 约 **$45.6B**；Circana Retail Tracking 覆盖约 68% 市场的样本产生 **$30.3B** retail sales，较 2024 增长 6%。Collectibles/licensed/fandom 产品是增长来源之一。这里恰好说明“tracked retail”不能与“total market”混用。 :chatgpt-content-reference{index="8"}  
URL：[https://toyassociation.org/ta/toys/research-and-data/data/us-sales-data.aspx?hkey=acea06b5-22e0-4bcc-a3bc-03532459e00d](https://toyassociation.org/ta/toys/research-and-data/data/us-sales-data.aspx?hkey=acea06b5-22e0-4bcc-a3bc-03532459e00d&utm_source=chatgpt.com)

**第七，C14 Sports/outdoor 确认是大市场，但边界重叠严重。** OIA/Circana 报告 2024 美国 outdoor retail sales 为 **$28B**，覆盖 apparel、footwear、equipment、accessories，因此不能把 $28B 全部归到“器材”；Census 2024 sporting-goods-store employer sales 则为 **$58.714B**，但这是店型销售而非商品 GMV。BLS 的另一独立指标是 2024 每 consumer unit 平均 **$225** 用于 sports/recreation/exercise equipment。三者共同证明需求不小，但不能合并。 :chatgpt-content-reference{index="10"}

**第八，C10/C17 的美国 home demand 很大，但两个 master categories 严重重叠。** Circana 2026 年 9 月最新 Home forecast 为美国 home-industry sales **$43.7B**，其中 robot vacuum 预计 2026 dollar sales +9.1%；BLS 2024 consumer-unit 年均 household furnishings/equipment 支出 **$2,414**，其中 major appliances $385、small appliances and miscellaneous housewares $155。不能把同一 $43.7B 同时计入 C10 和 C17。 :chatgpt-content-reference{index="11"}

**第九，线上需求很重要，但公开数据不足以为 18 个 category 都给出 category-specific online share。** Census Q2 2026 最新发布值为美国整体 retail e-commerce **17.1%**（seasonally adjusted）；Circana 自己覆盖的一篮子 discretionary categories 在 12ME Dec-2025 的 e-commerce 占比则 **超过 25%**。这两个数字定义不同，而且 Census 页面在 2026-09-28 已警告 Q2 数值存在待未来发布反映的修订。因此这两者只能作 benchmark，不能向每个品类硬套。 :chatgpt-content-reference{index="12"}  
URL：[https://www.census.gov/retail/ecommerce.html](https://www.census.gov/retail/ecommerce.html?_sp=333742e8-5611-465d-b38e-1cbe29b04189&utm_source=chatgpt.com)

**第十，最大的 W1 数据缺口不是“有没有需求”，而是缺少同一口径下的 category GMV + online share + units + retail ASP + purchase incidence。** CTA 的 July-2026 U.S. Consumer Technology Forecast 确实覆盖 200+ 产品，提供 shipment volume、wholesale revenue、average wholesale price、household penetration，但精细表需要登录/付费；本次没有访问这些 authenticated values。 :chatgpt-content-reference{index="14"}

---

## 1.2 最新数据日期

| 数据族 | 截至 2026-10-06 的最新可用情况 |
|---|---|
| Census AIES | **reference year 2024**，2026-09-03 发布；AIES 页面 2026-09-29 修订 |
| Census quarterly e-commerce | **Q2 2026**，2026-08-18 发布；页面注明 2026-09-28 后存在待 Q3 release 体现的 revisions |
| BLS Consumer Expenditure | **2024 annual** 仍为最新；2025 annual 计划 **2026-10-29** 发布，因此截至研究日不可用 |
| Counterpoint US smartphone | Q2 2026 market results；部分 model tracker 到 **Jul-2026** |
| Circana consumer tech | 最新公开 forecast **2026-08-06** |
| Circana Home | 最新公开 forecast **2026-09-24** |
| SEMA | 最新公开数字为 **2024 consumer spend** |
| OIA | 最新公开完整年度为 **2024 retail sales** |
| Toy Association/Circana | 最新完整年度 **2025** |

BLS 对 2025 annual release 的官方通知明确写明发布日期是 **2026-10-29**，所以我没有把尚未发布的 2025 CE 数据写进报告。 :chatgpt-content-reference{index="15"}

---

# 2. Evidence table / C01–C18 US Demand Map

以下 “需求层级” 是 **partial order / evidence tier**，不是把不可比数字伪装成统一 GMV 排名。

| ID | Category | 美国需求证据 | Online / channel | ASP / frequency | Fragmentation / middle-tail | W1 demand assessment |
|---|---|---|---|---|---|---|
| **C01** | Smartphones | Q2 2025 sell-through revenue **$17.5B**；Q2 2026 sales -5% YoY | carrier/retail channel 很重要；公开 category e-com share 缺失 | Q2 2025 ASP **$647.53**；replacement frequency 无当前公开可比值 | **极低碎片化**：Q2'26 top-4 OEM shipment share ≈98%，top-5 models ≈53% sales share | **Very High / high confidence** |
| **C02** | Laptops | PCs 预计接近 2026 US consumer-tech revenue 的 **20%**；notebooks 是最大增长贡献者 | 精确 online share 缺失 | retail ASP 缺失；replacement-refresh cycle 明显 | 品牌比 smartphone 更分散，但无公开 HHI | **High / med-high** |
| **C03** | Tablets | Circana：2026 tablets 是 consumer tech 第二大增长来源，增量 revenue **>$200M** | 缺失 | 缺失 | 多品牌，但无可比 concentration ratio | **Medium-High / medium** |
| **C04** | Mini PCs / small desktops | 未找到独立公开 US consumer GMV；被 PCs/desktops 聚合 | 缺失 | 缺失 | SKU 可能多，但没有公开数量指标 | **UNRANKABLE / low** |
| **C05** | PC components / storage / networking | consumer-tech 中 memory revenue 在 unit softness 下仍增长；CTA 有 PC peripherals/parts、home networking 的付费拆分 | 社区显示强线上多渠道，但无市场份额 | 缺失 | 社区/产品结构显示高度碎片化，定量 HHI 缺失 | **Medium-High proxy / med-low** |
| **C06** | Headphones / IEM / DAC / portable audio | portable audio 是 2025 tech 增长贡献项；headphones 是重要 tracked category | open-ear headphone 有单独 online-share tracking，但绝对 share 未公开 | 2025 wired ASP ≈**$13**、Bluetooth ≈**$99**；BT 占 headphone dollars **65%** | 多价位、多品牌 | **Medium / medium** |
| **C07** | PC peripherals | CTA 明确单列 PC peripherals and parts；Circana monitor/gaming-accessory 数据显示活跃，但无公开总 GMV | 社区显示 Amazon/Newegg/Micro Center/B&H/Best Buy 等多渠道 | 缺失 | **高碎片化推断**；缺 HHI | **Medium / med-low** |
| **C08** | Wearables | Parks：接近 **50% US internet households** 拥有并使用 wearable | channel share 缺失 | retail ASP、replacement rate 缺失 | 平台层面趋向 Apple/Wear OS/Garmin，但 form factor 扩张 | **Medium-High / medium** |
| **C09** | Smart home / security / IoT | Parks：**49% US internet households** 至少有 1 个 smart-home device；camera/video doorbell 领先 | category share 缺失 | 缺失 | ecosystem 集中但 device/vendor 层面较分散 | **Medium-High / medium** |
| **C10** | Robot vacuums / small appliances | Circana broad Home market 2026 **$43.7B**；robot vacuum forecast +9.1% | Circana broader retail basket 高度 omnichannel；category share 不公开 | 缺失 | floor care / appliance 品类多；独立 C10 GMV 缺失 | **Medium-High / medium** |
| **C11** | Power tools / electronics tools / repair tools | secondary estimates 对 US power-tools 2025 给出约 **$7.5B vs ~$11.4–11.8B**，差异过大；Census outdoor-power-equipment store sales $11.6B 但边界不同 | 专业零售/大卖场/online 混合；无统一 share | 缺失 | 品类与品牌均较多 | **Medium / low-med** |
| **C12** | Camera / video gear & accessories | digital point-and-shoot volume 2025 **+93%**；H1'25 dollar gains >40%，但总体 US GMV 未公开 | specialist retailer 仍重要，社区证据明显 | 低价 point-and-shoot 增长主要来自 **<$200** models；全品类 ASP 缺失 | camera bodies 相对集中，accessories 长尾 | **Low-Medium / med-low** |
| **C13** | Automotive accessories | SEMA 2024 specialty-equipment consumer spend **$52.65B** | **约 50% online / 50% offline** | 缺失 | parts/accessory categories 多；appearance/accessory 占重要部分 | **Very High / high** |
| **C14** | Sports / outdoor | OIA 2024 outdoor retail **$28B**；Census sporting-goods-store sales **$58.7B**；BLS equipment spend $225/CU | OIA 数据覆盖 chain/e-commerce/specialty，但免费摘要无 channel shares | 缺失 | 高 SKU 广度；但 outdoor $28B 包含 apparel/footwear | **High / med-high** |
| **C15** | Hobby / models / 3D printing / maker | Census hobby/toy/game store 2024 sales **$17.9B**，但与 C18 高度重叠；3D printing/maker 独立 US GMV 缺失 | Reddit 显示 Amazon、Micro Center、direct 都存在 | 缺失 | **很可能高度碎片化**，但定量 evidence 缺失 | **Medium-Low / low** |
| **C16** | Apparel / shoes / bags | 目标 Census store-industry sales 合计约 **$245.66B**；BLS apparel/services $2,001/CU，其中 footwear $461 | Census 4541 PBA 显示纯电商渠道很大，但不是全 category online sales；精确 share 缺失 | retail ASP/transaction frequency 缺失 | 极大 SKU breadth，private label 也占很大比重 | **Very High / high** |
| **C17** | Home / organization / household goods | Circana Home 2026 forecast **$43.7B**；BLS household furnishings/equipment **$2,414/CU** | broad e-commerce exposure高，但没有 clean C17 share | 缺失 | 品类非常分散；与 C10 重叠 | **High / medium** |
| **C18** | Toys / collectibles / official merch | 2025 total toy market **$45.6B**；tracked retail $30.3B，覆盖约 68% | exact online share 未公开 | ASP 2025 +4% YoY，但绝对 ASP 未公开 | subcategory/collectibles 高度多样；licensed/fandom 强 | **High / high** |

### C01 关键来源与反证

Counterpoint Q2 2025 revenue/ASP：  


2026 反证：Q2 consumer sales -5%，但 shipment +6%，说明 shipment 不能代理最终需求。 :chatgpt-content-reference{index="17"}

### C02–C09 关键科技市场来源

Circana 2026 US Consumer Tech：  
  


CTA July-2026 detailed forecast：  


CTA 是重要反证/缺口：它公开说明自己掌握 shipment volume、**wholesale** revenue、average wholesale price 和 penetration；这些不是 retail sell-through，且细项需付费/登录。本报告没有把它们冒充零售 GMV。

### C06 关键来源

2025 Bluetooth headphones 占 headphone dollar sales 65%，wired ASP ≈$13，Bluetooth ASP ≈$99。 :chatgpt-content-reference{index="21"}  
URL：

### C08–C09 关键来源及定义反证

Wearables：近 50% US internet households 拥有并使用 wearable。 :chatgpt-content-reference{index="23"}  
URL：

Smart home：Parks 的 current public figure 为 49% US internet households；而 Circana 早前用更广定义得到约 59% households。两者并不矛盾地证明需求广泛，但说明“smart home penetration”强烈依赖 device definition。 :chatgpt-content-reference{index="25"}

### C10/C17 关键来源及预测反证

最新 Sep-2026 forecast：$43.7B / +2.9%。  


但同一 Circana 在 Mar-2026 的预测还是约 $41.8B / -1.2%。这说明 forward forecast 应设置明显的不确定区间，而不是当“actual GMV”。 :chatgpt-content-reference{index="27"}

### C11 关键来源及强反证

Grand View 对 2025 US power tools 给出约 **$7.54B**；Ken Research 页面给出的 2025 数字约 **$11.4–11.8B**，且其页面自身数字也不完全一致。因此 **C11 不应由 secondary market-size estimate 得出精确排名**。  
URL：  
URL：

### C13 关键来源



注意：SEMA 的 $52.65B 是 **specialty equipment/accessorizing/modifying**，不能与 Census automotive parts store 的 **$85.24B** 直接比较，因为后者是店型销售且包含更广 replacement/repair merchandise。 :chatgpt-content-reference{index="31"}

### C14 关键来源



反证：$28B 包含 apparel 与 footwear，所以不是纯“sports/outdoor goods equipment GMV”。

### C16 关键来源

Census 2024 AIES：  


BLS 2024 CE：  


反证：Census 明确说明按 retailer establishment 类型的 sales 不是特定 commodity 的完整销售额，因此 `$245.66B` 只能视为 **大规模需求证据/店型渠道下限结构**，不能命名为 C16 total GMV。 :chatgpt-content-reference{index="35"}

### C18 关键来源



---

## 2.1 可复现 Demand weighting 方法

建议 W1 synthesis **不要先给所有 category 一个硬数字权重**。应采用以下规则：

**Primary demand score：**

`D = 60% × US all-channel retail product spend + 15% × online addressability + 10% × purchase incidence + 10% × fragmentation/breadth + 5% × recent real growth`

其中：

- GMV 使用 log scale 后 percentile normalization；
- `US all-channel retail product spend` 只接受美国、最终消费者、product retail/sell-through 口径；
- wholesale、store-industry sales、global sales、shipment value 不可直接代入；
- online addressability 优先 category e-commerce dollar share；
- purchase incidence 优先 CE percent-reporting/annual transactions 或可信 household panel；
- fragmentation 优先 `1 - Top4 revenue share` 或 HHI；没有 concentration data 时保持 null；
- growth 优先实际 sell-through，而不是 shipment forecast。

**缺失处理：不插值。** 如果 primary GMV 缺失，则 `D=null`，只给 evidence tier。Census store-industry sales、household spend、ownership penetration 等进入独立 `proxy_vector`，而不是偷偷替代 GMV。

**不确定性：**

1. A 级：US all-channel consumer sell-through/product-spend；
2. B 级：覆盖明确的 retail panel；
3. C 级：retailer-industry sales；
4. D 级：ownership、CPI weight、household-spend proxy；
5. E 级：secondary market-size estimate。

只有当两个品类在 **同口径区间不重叠** 时才赋予明确排名；否则保持 tie/partial order。

据此，本轮只能支持：

**Tier 1 / 明显大需求：C01, C02, C13, C14, C16, C17, C18**

**Tier 2 / 中等至中高、但缺统一 GMV：C03, C05, C06, C07, C08, C09, C10, C11**

**Tier 3 / 独立 US GMV 证据尤其不足：C04, C12, C15**

这不是 opportunity ranking，也不是 China-direct ranking；它仅是 W1 demand evidence tier。

---

# 3. Primary sources

本轮优先级最高的来源如下。

| Source | 类型 | 用途 | URL |
|---|---|---|---|
| U.S. Census 2024 AIES | Government | 2024 retail store-industry sales、e-commerce framework |  |
| Census Q2 2026 E-commerce | Government | 全美 retail online benchmark |  |
| BLS CE 2024 | Government | household expenditure proxies |  |
| BLS 2025-release notice | Government | 确认截至 10/6/26 最新 annual 仍为 2024 |  |
| SEMA 2025 Market Report release | Industry association | auto specialty-equipment spend/channel |  |
| Outdoor Industry Association | Industry association | US outdoor retail sales |  |
| Toy Association / Circana | Industry association | total toy market + tracked-market coverage |  |
| CTA July 2026 Forecast | Industry association | 200+ tech product market/shipment framework |  |
| Parks Associates | Industry research | wearables / smart-home penetration |  |
| Counterpoint | Industry research | US smartphone sell-through/concentration |  |
| Circana | Retail panel / secondary | consumer tech/home actual and forecasts |  |

**重要访问限制：** CTA July-2026 detailed category tables 需要登录或购买。公开页面确认其确实包含 shipment volumes、wholesale revenues、average wholesale prices、household penetration，但本次未访问这些具体数值，故对应字段为 `AUTHENTICATED DATA REQUIRED`。 :chatgpt-content-reference{index="48"}

---

# 4. Forum evidence

论坛证据**未用于 GMV 排名**，只用于检验 channel structure / retailer reliance。

**PC components（C05/C07）：** 2026 r/buildapc 讨论中，美国用户反复同时提到 Amazon、Newegg、Micro Center、Best Buy、B&H，以及 PcPartPicker；讨论强调按价格、seller legitimacy、bundles 和 return/warranty 跨商家选择。这反驳了“PC parts demand ≈ Amazon demand”的简单假设，但它只是社区行为证据，不是渠道份额。 :chatgpt-content-reference{index="49"}  
URL：`https://www.reddit.com/r/buildapc/comments/1u5i1g1/where_to_source_parts_from/`

**3D printing（C15）：** 2025 r/3Dprinting 的 filament 购买讨论中，发帖者原本以 Amazon 为主，回复集中推荐 Micro Center 和 manufacturer-direct；说明 maker 消费存在多渠道行为，不能从 Amazon activity 推算整个 category demand。 :chatgpt-content-reference{index="50"}  
URL：`https://www.reddit.com/r/3Dprinting/comments/1j1r22e/where_are_you_buying_printer_filament_these_days/`

**Camera（C12）：** 2025–2026 摄影社区反复把 B&H、Adorama、KEH、Amazon、eBay 等作为可替代渠道，说明高价值摄影器材的 specialist-retailer reliance 仍然可见。仍不能把单个 Reddit thread 解释成 market share。 :chatgpt-content-reference{index="51"}  
URL：`https://www.reddit.com/r/photography/comments/1s6kxy9/where_do_you_shop_looking_for_alternatives_to/`

**Smart home（C09）：** 社区购买讨论常围绕 Apple/Amazon/Google ecosystem compatibility，而不是单纯 retailer；这支持 compatibility/ecosystem 对 demand structure 有影响，但不提供 GMV。 :chatgpt-content-reference{index="52"}  
URL：`https://www.reddit.com/r/smarthome/comments/1ln6v60/google_homealexa_homeapple_home_for_2025/`

---

# 5. Contrary evidence

| 初看结论 | 反证 | W1 处理 |
|---|---|---|
| Smartphone market 2026 在增长 | Q2'26 **shipments +6%**，但 consumer **sales -5%** | shipments 不当 demand GMV |
| Home 2026 = $43.7B | 3 月同一 Circana 曾 forecast **$41.8B / -1.2%** | forecast 给 uncertainty，不当 actual |
| Smart-home penetration ≈49% | Circana 广定义曾报约 59% households | 明确 device universe |
| Power tools ≈$8B | 另一 secondary source 报 ~$11–12B | 不赋精确 GMV/排名 |
| Toy tracked sales = $30.3B | total-market projection = $45.6B | 区分 panel coverage 与 total market |
| Outdoor = $28B equipment | $28B 实际含 apparel、footwear、equipment、accessories | 不全部记入 C14 equipment |
| Apparel store sales = total C16 | Census 店型统计漏 pure-play/general merchandise 等，并非 merchandise-line | 仅作 channel/scale proxy |
| Consumer tech = $112B | CTA 另有远更大的 “consumer technology industry” revenue numbers，因为可含不同产品/服务、wholesale definition | 不跨定义比较 |
| 全美 e-commerce = 17.1% | Circana tracked discretionary basket >25% | 17.1% 不外推各 category |
| 高 ownership = 高 annual GMV | Wearable/smart-home penetration 高，但 replacement cycle 和 ASP 可能压低当年 spend | ownership 与 flow demand 分开 |

这组反证是本轮最重要的方法论结果之一。尤其是 Census 官方明确指出，按 retailer type 的销售额不是 merchandise-line total，避免了把 `$245B apparel store sales`、`$58.7B sporting-goods stores` 等错误称为品类 TAM。 :chatgpt-content-reference{index="53"}

---

# 6. Confidence

**High confidence**

- C01 美国 smartphone 需求极大且市场高度集中。
- C13 specialty automotive accessories 是数百亿美元级美国 consumer-spend category，线上占比约一半。
- C16 apparel/shoes/bags 是极大消费池，即便只观察相关实体/omnichannel retailer industries 也已 >$200B。
- C18 toys 是约 $45B 级 total market。
- 美国整体 retail e-commerce 已是约十几个百分点至二十几个百分点量级的重要渠道，但 category variation 很大。

**Medium confidence**

- C02 PC/laptops 属于 W1 第一梯队，但精确 retail GMV 需要统一数据集。
- C14 sports/outdoor 属于高需求，但 apparel/footwear overlap 使 C14 独立规模不够干净。
- C10/C17 home demand 均重要，但 taxonomy 必须先拆分。
- C08/C09 household penetration 高，但 annual hardware flow GMV 缺失。

**Low / medium-low confidence**

- C04 mini PCs 的独立需求排名。
- C11 power-tools 精确市场规模。
- C12 cameras/video accessories 的完整 US retail GMV。
- C15 hobby/maker/3D-printing 独立于 toys 的完整 US demand。

---

# 7. Data gaps

1. **18-category 同一口径的 US all-channel retail sell-through GMV 缺失。**
2. C02–C09 的 CTA 细分 shipment / wholesale revenue / ASP 数据需要 **AUTHENTICATED DATA REQUIRED**；且即使取得也需从 wholesale 转成 retail，不能直接混用。
3. 绝大多数 category 缺当前 **online dollar share**；C13 是明显例外。
4. 绝大多数 category 缺 **retail ASP**。
5. 缺统一的 **annual units sold**。
6. 缺可比较的 **purchase frequency / percent of households purchasing in past 12 months**。
7. 缺多数 category 的 **Top-4 revenue share / HHI / SKU concentration**。
8. Amazon、Walmart、specialty retailer 等 **category marketplace reliance** 基本没有免费、审计性强的统一数据。
9. C04 mini PCs、C15 maker/3D printing 尤其需要独立拆分。
10. C10/C17 必须先做 taxonomy de-overlap，例如 robot vac/floor care、小家电、housewares、storage/organization 不可重复计数。
11. C14 必须把 outdoor apparel/footwear 与 equipment/accessories 分开，否则会与 C16 双计。
12. C18 collectible/official merchandise 超出传统 toy tracking 的部分需要额外数据。
13. Census 2024 AIES 的 4541 PBA 可帮助理解 pure-play e-commerce structure，但**不是全品类 online GMV**。
14. Census 最新 benchmarked detailed merchandise-line e-commerce tables 仍主要是 **2022 reference year**；不宜当 2026 current market share。 :chatgpt-content-reference{index="54"}

---

# 8. Most surprising finding

最值得注意的不是某个 category 数字，而是 **美国公开需求数据的定义分裂程度非常高**。

例如：

- Smartphone 可以同时出现 **shipment +6% / consumer sales -5%**；
- Toy 同年可以合法出现 **$45.6B total market / $30.3B tracked retail**；
- Smart home 可以出现 **49% / 59% penetration**，取决于 device universe；
- Home 2026 forecast 在半年内从 **$41.8B/-1.2%** 更新到 **$43.7B/+2.9%**；
- Apparel 的 `$245.66B` 可以是非常有用的“规模证据”，却仍然不能叫 total category GMV。

因此，W1 最危险的错误不是漏掉一个市场报告，而是把 **不同 measurement objects 看成同一个“GMV”**。

另一个较意外结果是 **C13 automotive specialty equipment 的 online penetration 已约 50%**。对一个包含大量复杂、重型、fitment-sensitive 商品的 category，这比“只有轻小电子适合在线购买”的直觉更强。该结论只说明美国需求/渠道结构，不涉及任何 China-direct feasibility。 :chatgpt-content-reference{index="55"}

---

# 9. What would falsify my own conclusion?

以下任一结果都会实质改变本 W1 判断：

1. 一套同口径 2025/2026 U.S. sell-through 数据显示 C01/C02/C13/C14/C16/C17/C18 中多个品类的实际 product GMV 远低于目前 proxies 所暗示的规模。
2. 取得 category-specific e-commerce 后发现多数目标品类线上份额极低，使其对网络 comparison demand 的可触达性显著下降。
3. CE microdata 显示部分表面上高-GMV品类主要由极少数家庭的高额购买驱动，而不是广泛 purchase incidence。
4. 品牌/SKU concentration data 显示 C02、C05、C07、C09、C13、C17 等实际上高度集中在很少 SKU，推翻“middle-tail broadness”推断。
5. C10/C17 去重后发现各自独立商品池远小于 broad Home headline。
6. C14 剥离 apparel/footwear 后 equipment/accessory demand 显著小于当前 tier。
7. C15 将 traditional toys 排除后，maker/3D-printing/model electronics 的美国消费规模极小。
8. 统一 retail-ASP 数据显示某些高美元品类的 units/purchase incidence极低，从而改变“需求广度”判断。

---

# 10. Suggested next experiment

如果 W1 只能再做一个实验，应做：

**建立一个“18-category U.S. Comparable Demand Ledger”，只采同口径字段，不碰任何海外 SKU。**

每个 C01–C18 固定采：

`2025/TTM US retail sell-through dollars`  
`units`  
`retail ASP`  
`online dollars + online share`  
`household purchase incidence`  
`Top-4 brand share`  
`Top-20 SKU share`  
`data universe / exclusions`

优先顺序：

1. 取得 CTA July-2026 authenticated tech tables，明确它们是 wholesale，不直接混入 retail；
2. 对 tech/home/toys/apparel/outdoor 请求或购买同一期 Circana/category extracts；
3. 用 BLS CE public microdata计算 household purchase incidence；
4. 用 Census 只作 independent reconciliation / retailer-channel check；
5. 对每一类生成 `direct_measure / proxy / missing` 三列；
6. 只有完成这张 ledger 后才计算统一 Demand score。

这个实验比继续增加零散 market-size 报告更能减少 W1 的核心 uncertainty，而且完全符合 pre-freeze：**不涉及任何中国 SKU、海外售价、SKU coverage 或价格套利信息。**

下方是与报告对应的机器可读 evidence ledger；由于工具不提供逐来源请求时钟，`retrieved_at` 保留为 `null`，而不是伪造秒级时间。

```json
{
  "job_id": "W1-B",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.census.gov/data/tables/2024/econ/aies/2024-aies-tables.html",
      "title": "2024 AIES Data",
      "published_at": "2026-09-03",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C11", "C14", "C15", "C16", "C17"]
    },
    {
      "source_id": "S02",
      "url": "https://data.census.gov/table/AIESBASIC2024.AIES00BASIC?codeset=naics~N0600.44",
      "title": "AIES00BASIC All Sectors: Summary Statistics for Industry Groups and Industries for Employer Firms in the U.S. and Selected Geographies: 2024",
      "published_at": "2026-09-03",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "snippet_only",
      "claims_supported": ["C11", "C14", "C15", "C16", "C17"]
    },
    {
      "source_id": "S03",
      "url": "https://data.census.gov/table/AIESMISCSECTOR2024.AIES44PBA?codeset=naics~4541",
      "title": "AIES44PBA Retail Trade Supplemental Total and E-commerce Sales for Electronic Shopping and Mail-Order Houses by Primary Business Activity: 2024",
      "published_at": "2026-09-03",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "snippet_only",
      "claims_supported": ["C05", "C06", "C07", "C14", "C16", "C17", "C18"]
    },
    {
      "source_id": "S04",
      "url": "https://www.census.gov/retail/ecommerce.html",
      "title": "Quarterly Retail E-Commerce Sales, Second Quarter 2026",
      "published_at": "2026-08-18",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"]
    },
    {
      "source_id": "S05",
      "url": "https://www.bls.gov/cex/notices/2025/annual-data-release-2024.htm",
      "title": "Consumer Expenditure Surveys 2024 Annual Data Release",
      "published_at": "2025-12-19",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C14", "C16", "C17"]
    },
    {
      "source_id": "S06",
      "url": "https://www.bls.gov/cex/tables/calendar-year/mean/cu-vets-2024.htm",
      "title": "Consumer Expenditure Surveys 2024 Annual Expenditure Means",
      "published_at": "2025-12-19",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C10", "C14", "C16", "C17", "C18"]
    },
    {
      "source_id": "S07",
      "url": "https://www.bls.gov/opub/ted/2026/the-new-year-and-household-spending.htm",
      "title": "The New Year and household spending",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C14"]
    },
    {
      "source_id": "S08",
      "url": "https://www.bls.gov/cex/notices/2026/2026-2-year-tables.htm",
      "title": "Changes with the 2025 annual release of Consumer Expenditure data",
      "published_at": "2026-10-06",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"]
    },
    {
      "source_id": "S09",
      "url": "https://www.circana.com/post/us-consumer-technology-sales-forecast-to-reach-112-billion-in-2026-reports-circana",
      "title": "US Consumer Technology Sales Forecast to Reach $112 Billion in 2026",
      "published_at": "2026-01-06",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C03", "C05", "C06", "C07", "C08", "C12"]
    },
    {
      "source_id": "S10",
      "url": "https://www.circana.com/post/circana-us-consumer-technology-forecast-growth-driven-by-premium-products-2026",
      "title": "Rising Prices and Americans' Focus on Value Keeps Consumer Technology Revenue Growth on a Moderate Track Through 2028",
      "published_at": "2026-08-06",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C03", "C05"]
    },
    {
      "source_id": "S11",
      "url": "https://www.cta.tech/research/cta-us-consumer-technology-one-year-industry-forecast-2022-2027-july-2026/",
      "title": "CTA U.S. Consumer Technology One-Year Industry Forecast, 2022-2027 (July 2026)",
      "published_at": "2026-06-01",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "login_required",
      "claims_supported": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C12"]
    },
    {
      "source_id": "S12",
      "url": "https://counterpointresearch.com/en/insights/us-smartphone-sell-through-up-9-yoy-in-q2-2025",
      "title": "US Smartphone Sell-through Up 9% YoY in Q2 2025",
      "published_at": "2025-08-14",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S13",
      "url": "https://counterpointresearch.com/default.htm/insights/us-smartphone-sales-fall-5-percent-q2-2026",
      "title": "US Smartphone Sales Fall 5% YoY in Q2 2026 as Pricing Pressure Squeezes Low-end Segment",
      "published_at": "2026-08-12",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S14",
      "url": "https://counterpointresearch.com/sitemap.html/insights/us-smartphone-market-share",
      "title": "US Smartphone Market Share: Quarterly",
      "published_at": "2026-09-01",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S15",
      "url": "https://counterpointresearch.com/mailto%3Apress%40counterpointresearch.com/insights/top-5-smartphone-model-share-8-countries",
      "title": "Top 5 Smartphone Models Share For 8 Countries",
      "published_at": "2026-08-01",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C01"]
    },
    {
      "source_id": "S16",
      "url": "https://www.parksassociates.com/blogs/pr-smart-home/nearly-50-of-us-internet-households-own-and-use-a-wearable",
      "title": "Nearly 50% of US internet households own and use a wearable",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S17",
      "url": "https://www.parksassociates.com/blogs/press-releases/parks-associates-to-examine-security-smart-home-and-streaming-video-trends-in-upcoming-webinars",
      "title": "Parks Associates: 49% of US internet households own at least one smart home device",
      "published_at": "2026-08-11",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S18",
      "url": "https://www.circana.com/post/circana-forecasts-u-s-home-market-growth-as-consumers-invest-in-products-that-help-them-save-money",
      "title": "Circana Forecasts U.S. Home Market Growth as Consumers Invest in Products That Help Them Save Money and Simplify Life",
      "published_at": "2026-09-24",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C10", "C17"]
    },
    {
      "source_id": "S19",
      "url": "https://www.circana.com/post/stabilization-and-renewed-growth-forecast-for-home-products-industry-beginning-in-late-2026-reports",
      "title": "Stabilization and Renewed Growth Forecast for Home Products Industry Beginning in Late 2026",
      "published_at": "2026-03-10",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C10", "C17"]
    },
    {
      "source_id": "S20",
      "url": "https://www.grandviewresearch.com/horizon/outlook/power-tools-market/united-states",
      "title": "United States Power Tools Market Outlook",
      "published_at": "2025-12-16",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S21",
      "url": "https://www.kenresearch.com/industry-reports/usa-power-tools-market",
      "title": "USA Power Tools Market",
      "published_at": "2026-05-01",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S22",
      "url": "https://www.circana.com/post/wired-headphones-growth-is-a-throwback-to-2016",
      "title": "Wired Headphones Growth Is a Throwback to 2016",
      "published_at": "2026-02-25",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C06", "C12"]
    },
    {
      "source_id": "S23",
      "url": "https://www.circana.com/post/consumer-technology-growth-that-kicked-off-2025-is-expected-to-soften-in-second-half-of-year-report",
      "title": "Consumer Technology Growth Expected to Slow in Second Half of 2025",
      "published_at": "2025-01-01",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C12"]
    },
    {
      "source_id": "S24",
      "url": "https://www.sema.org/news-media/press-release/new-sema-research-2025-market-report",
      "title": "New SEMA Research: 2025 Market Report",
      "published_at": "2025-06-30",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C13"]
    },
    {
      "source_id": "S25",
      "url": "https://outdoorindustry.org/press-release/new-report-outdoor-market-shows-modest-rebound-to-28b-in-2024-driven-by-casual-consumers/",
      "title": "Outdoor Market Shows Modest Rebound to $28B in 2024",
      "published_at": "2025-04-15",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C14"]
    },
    {
      "source_id": "S26",
      "url": "https://toyassociation.org/ta/toys/research-and-data/data/us-sales-data.aspx?hkey=acea06b5-22e0-4bcc-a3bc-03532459e00d",
      "title": "U.S. Sales Data",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C18"]
    },
    {
      "source_id": "S27",
      "url": "https://www.circana.com/post/retail-enters-a-phase-of-continuance",
      "title": "US Retail in a New Phase: Shopping Habit Shifts & Consumer Spending Trends",
      "published_at": "2026-01-01",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C06", "C07", "C10", "C13", "C14", "C16", "C17", "C18"]
    },
    {
      "source_id": "S28",
      "url": "https://www.reddit.com/r/buildapc/comments/1u5i1g1/where_to_source_parts_from/",
      "title": "Where to source parts from",
      "published_at": "2026-06-14",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C07"]
    },
    {
      "source_id": "S29",
      "url": "https://www.reddit.com/r/3Dprinting/comments/1j1r22e/where_are_you_buying_printer_filament_these_days/",
      "title": "Where are you buying printer filament these days?",
      "published_at": "2025-03-02",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C15"]
    },
    {
      "source_id": "S30",
      "url": "https://www.reddit.com/r/photography/comments/1s6kxy9/where_do_you_shop_looking_for_alternatives_to/",
      "title": "Where do you shop? Looking for alternatives to BH/Adorama/Amazon",
      "published_at": "2026-03-29",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    },
    {
      "source_id": "S31",
      "url": "https://www.reddit.com/r/smarthome/comments/1ln6v60/google_homealexa_homeapple_home_for_2025/",
      "title": "Google Home/Alexa Home/Apple Home for 2025?",
      "published_at": "2025-06-29",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S32",
      "url": "https://www.census.gov/programs-surveys/arts/data/tables.html",
      "title": "Annual Retail Trade Survey Tables",
      "published_at": "2026-08-31",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "US smartphones are a very-high-demand category, but demand is unusually concentrated: Q2 2025 sell-through revenue was $17.5B with ASP $647.53, while Q2 2026 sales fell 5% YoY and the top four OEMs represented about 98% of shipment share.",
      "classification": "FACT",
      "source_ids": ["S12", "S13", "S14", "S15"],
      "confidence": "high",
      "counterevidence": "Q2 2026 shipments grew while sell-through sales declined, so shipment data alone would overstate current consumer demand."
    },
    {
      "claim_id": "C02",
      "claim": "Laptops/PCs are a high-demand U.S. consumer-tech category; Circana says PCs are projected to represent nearly 20% of U.S. consumer-tech revenue in 2026 and notebooks are the largest incremental growth contributor.",
      "classification": "FACT",
      "source_ids": ["S09", "S10", "S11"],
      "confidence": "high",
      "counterevidence": "The January $112B total-market forecast and August PC-share forecast are different forecast vintages, so they should not be multiplied into a fabricated precise PC GMV."
    },
    {
      "claim_id": "C03",
      "claim": "Tablets have meaningful U.S. demand and were forecast by Circana as the second-largest source of consumer-tech revenue growth in 2026, but a clean public annual retail GMV was not found.",
      "classification": "FACT",
      "source_ids": ["S09", "S11"],
      "confidence": "medium",
      "counterevidence": "Incremental growth does not establish absolute category size."
    },
    {
      "claim_id": "C04",
      "claim": "Mini PCs and small desktops could not be independently ranked from public U.S. demand data because they are generally aggregated into desktop/PC categories.",
      "classification": "FACT",
      "source_ids": ["S09", "S11"],
      "confidence": "high",
      "counterevidence": "Paid CTA or retail-panel data may contain a finer split that was not accessed."
    },
    {
      "claim_id": "C05",
      "claim": "PC components, storage and networking appear to be a medium-to-high demand and highly fragmented U.S. market, but public comparable retail GMV and online share were not established.",
      "classification": "INFERENCE",
      "source_ids": ["S10", "S11", "S28"],
      "confidence": "medium",
      "counterevidence": "Community retailer diversity is not quantitative evidence of category GMV or SKU fragmentation."
    },
    {
      "claim_id": "C06",
      "claim": "Headphones and portable audio form a meaningful U.S. consumer-tech category with substantial price-band breadth; in 2025 Bluetooth represented 65% of headphone dollars, with approximately $99 ASP versus approximately $13 for wired headphones.",
      "classification": "FACT",
      "source_ids": ["S22", "S09"],
      "confidence": "medium",
      "counterevidence": "The headphone figures do not cover the full C06 boundary including DACs, IEMs and other portable audio."
    },
    {
      "claim_id": "C07",
      "claim": "PC peripherals have meaningful but not cleanly quantified U.S. demand and a multi-retailer channel structure.",
      "classification": "INFERENCE",
      "source_ids": ["S11", "S28"],
      "confidence": "medium",
      "counterevidence": "No public all-channel retail GMV or concentration ratio was found."
    },
    {
      "claim_id": "C08",
      "claim": "Wearables have broad U.S. adoption, with nearly 50% of U.S. internet households owning and using a wearable, but annual hardware GMV and replacement frequency remain unobserved in public evidence.",
      "classification": "FACT",
      "source_ids": ["S16", "S11"],
      "confidence": "medium",
      "counterevidence": "High ownership penetration does not necessarily imply high annual sales because replacement cycles may be long."
    },
    {
      "claim_id": "C09",
      "claim": "Smart-home/security/IoT demand is broad, with Parks Associates reporting 49% of U.S. internet households own at least one smart-home device.",
      "classification": "FACT",
      "source_ids": ["S17", "S31"],
      "confidence": "medium",
      "counterevidence": "Alternative broader smart-home definitions have produced higher penetration estimates, so device-universe definitions materially affect the number."
    },
    {
      "claim_id": "C10",
      "claim": "Robot vacuums and small appliances participate in a large U.S. home-products market, and robot-vacuum dollar sales were forecast to grow in 2026, but the broad $43.7B Home total cannot be assigned wholly to C10.",
      "classification": "FACT",
      "source_ids": ["S18", "S19", "S06"],
      "confidence": "medium",
      "counterevidence": "Circana's March 2026 Home forecast was materially lower and negative-growth, demonstrating forecast uncertainty and category-boundary overlap with C17."
    },
    {
      "claim_id": "C11",
      "claim": "Power tools represent a material U.S. market, but the exact size is unresolved because public secondary estimates for 2025 differ by several billion dollars.",
      "classification": "FACT",
      "source_ids": ["S20", "S21", "S02"],
      "confidence": "low",
      "counterevidence": "Grand View and Ken Research produce materially different values and likely use different category boundaries."
    },
    {
      "claim_id": "C12",
      "claim": "Camera and video gear is a smaller demand pool than leading electronics categories but contains growing niches; U.S. digital point-and-shoot demand grew sharply in 2025.",
      "classification": "INFERENCE",
      "source_ids": ["S22", "S23", "S30"],
      "confidence": "medium",
      "counterevidence": "Strong percentage growth from a small base does not demonstrate large absolute GMV, and accessories are not fully captured."
    },
    {
      "claim_id": "C13",
      "claim": "U.S. consumers spent approximately $52.65B on automotive specialty equipment in 2024, with spending roughly split between online and offline channels.",
      "classification": "FACT",
      "source_ids": ["S24"],
      "confidence": "high",
      "counterevidence": "SEMA specialty equipment excludes or differs from the broader repair/replacement auto-parts universe, so it is not total automotive-parts GMV."
    },
    {
      "claim_id": "C14",
      "claim": "Sports and outdoor goods are a high-demand U.S. category, supported by a $28B 2024 outdoor retail market, $58.7B of sporting-goods-store sales and $225 annual average consumer-unit spending on sports/recreation/exercise equipment.",
      "classification": "INFERENCE",
      "source_ids": ["S25", "S02", "S07"],
      "confidence": "medium",
      "counterevidence": "The $28B outdoor figure includes apparel and footwear and the Census number is retailer-industry sales, so the three figures cannot be summed or directly compared."
    },
    {
      "claim_id": "C15",
      "claim": "Hobby/models/3D printing/maker demand is real but cannot be independently sized from toys using current public evidence; the $17.9B hobby/toy/game-store figure substantially overlaps C18.",
      "classification": "FACT",
      "source_ids": ["S02", "S29"],
      "confidence": "low",
      "counterevidence": "Maker and 3D-printing demand may be larger through direct and general e-commerce channels not captured by hobby-store industry sales."
    },
    {
      "claim_id": "C16",
      "claim": "Apparel, shoes and bags constitute a very large U.S. demand pool; the relevant 2024 Census employer-store industries sum to approximately $245.66B before pure-play and general-merchandise channels are included.",
      "classification": "FACT",
      "source_ids": ["S02", "S06"],
      "confidence": "high",
      "counterevidence": "Retailer-industry sales are not commodity-line GMV and cannot be treated as complete all-channel C16 sales."
    },
    {
      "claim_id": "C17",
      "claim": "Home, organization and household goods form a high-demand U.S. pool, supported by broad Home-market retail data and $2,414 average annual household-furnishings/equipment expenditure per consumer unit in 2024.",
      "classification": "INFERENCE",
      "source_ids": ["S18", "S19", "S06"],
      "confidence": "medium",
      "counterevidence": "The Circana Home universe overlaps C10 and broad BLS furnishings/equipment includes products outside a narrow organization/household-goods definition."
    },
    {
      "claim_id": "C18",
      "claim": "The U.S. toy market is a high-demand category: estimated total 2025 market size was approximately $45.6B, while Circana tracked retail covering about 68% of the market recorded $30.3B.",
      "classification": "FACT",
      "source_ids": ["S26"],
      "confidence": "high",
      "counterevidence": "Traditional toy-market tracking may not capture all adult collectibles and official merchandise included in the broader C18 brief."
    }
  ],
  "categories": [
    {
      "category_id": "C01",
      "name": "Smartphones",
      "demand_tier": "very_high",
      "confidence": "high",
      "us_sales_value": 17500000000,
      "us_sales_period": "2025-Q2",
      "us_sales_basis": "US retail sell-through revenue for one quarter",
      "online_share": null,
      "asp_usd": 647.53,
      "purchase_frequency": null,
      "fragmentation": "low",
      "notes": "Top-four OEM shipment share approximately 98% in Q2 2026; quarterly revenue must not be annualized without evidence."
    },
    {
      "category_id": "C02",
      "name": "Laptops",
      "demand_tier": "high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2026 forecast",
      "us_sales_basis": "PCs nearly 20% of U.S. consumer-tech revenue; laptop-only GMV unavailable",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": null,
      "notes": "Notebook PCs are forecast as the largest 2026 industry growth contributor."
    },
    {
      "category_id": "C03",
      "name": "Tablets",
      "demand_tier": "medium_high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2026 forecast",
      "us_sales_basis": "Second-largest source of consumer-tech growth; >$200M incremental revenue",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": null,
      "notes": "Incremental revenue is not total GMV."
    },
    {
      "category_id": "C04",
      "name": "Mini PCs / small desktops",
      "demand_tier": "unrankable",
      "confidence": "low",
      "us_sales_value": null,
      "us_sales_period": null,
      "us_sales_basis": null,
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": null,
      "notes": "Public sources aggregate this subcategory into desktop/PC totals."
    },
    {
      "category_id": "C05",
      "name": "PC components / storage / networking",
      "demand_tier": "medium_high_proxy",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": null,
      "us_sales_basis": null,
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "likely_high",
      "notes": "CTA detailed values require authenticated/paid data."
    },
    {
      "category_id": "C06",
      "name": "Headphones / IEM / DAC / portable audio",
      "demand_tier": "medium",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2025",
      "us_sales_basis": null,
      "online_share": null,
      "asp_usd": null,
      "segment_asps_usd": {
        "wired_headphones": 13,
        "bluetooth_headphones": 99
      },
      "purchase_frequency": null,
      "fragmentation": "medium_high",
      "notes": "Bluetooth represented 65% of headphone dollars in 2025; figures do not cover full C06 boundary."
    },
    {
      "category_id": "C07",
      "name": "PC peripherals",
      "demand_tier": "medium",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": null,
      "us_sales_basis": null,
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "likely_high",
      "notes": "Multi-retailer structure visible; quantitative HHI absent."
    },
    {
      "category_id": "C08",
      "name": "Wearables",
      "demand_tier": "medium_high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": null,
      "us_sales_basis": "ownership proxy",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "medium",
      "household_penetration": "nearly 50% of U.S. internet households",
      "notes": "Ownership is a stock measure and must not be treated as annual GMV."
    },
    {
      "category_id": "C09",
      "name": "Smart home / security / IoT",
      "demand_tier": "medium_high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": null,
      "us_sales_basis": "ownership proxy",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "medium_high_at_device_level",
      "household_penetration": "49% of U.S. internet households own at least one smart-home device",
      "notes": "Penetration is definition-sensitive."
    },
    {
      "category_id": "C10",
      "name": "Robot vacuums / small appliances",
      "demand_tier": "medium_high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2026 forecast",
      "us_sales_basis": "subset of broad $43.7B U.S. Home industry",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "medium_high",
      "notes": "Do not assign full Home-market figure to C10; robot-vacuum dollar sales forecast +9.1%."
    },
    {
      "category_id": "C11",
      "name": "Power tools / electronics tools / repair tools",
      "demand_tier": "medium",
      "confidence": "low",
      "us_sales_value": null,
      "us_sales_period": "2025",
      "us_sales_basis": "conflicting secondary estimates",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "medium_high",
      "notes": "Published estimates differ materially; no single number accepted."
    },
    {
      "category_id": "C12",
      "name": "Camera / video gear and accessories",
      "demand_tier": "low_medium",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2025",
      "us_sales_basis": "growth proxy only",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "mixed",
      "notes": "Digital point-and-shoot volume +93% in 2025, but absolute category GMV unavailable."
    },
    {
      "category_id": "C13",
      "name": "Automotive accessories",
      "demand_tier": "very_high",
      "confidence": "high",
      "us_sales_value": 52650000000,
      "us_sales_period": "2024",
      "us_sales_basis": "U.S. consumer spend on automotive specialty equipment",
      "online_share": 0.5,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "high",
      "notes": "Not the entire repair/replacement auto-parts market."
    },
    {
      "category_id": "C14",
      "name": "Sports / outdoor goods",
      "demand_tier": "high",
      "confidence": "medium",
      "us_sales_value": 28000000000,
      "us_sales_period": "2024",
      "us_sales_basis": "Outdoor retail market including apparel, footwear, equipment and accessories",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "high",
      "notes": "The $28B value overlaps C16 and cannot be treated as equipment-only GMV."
    },
    {
      "category_id": "C15",
      "name": "Hobby / models / 3D printing / maker electronics",
      "demand_tier": "medium_low",
      "confidence": "low",
      "us_sales_value": null,
      "us_sales_period": "2024",
      "us_sales_basis": "Hobby/toy/game store proxy overlaps C18",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "likely_high",
      "notes": "Independent maker/3D-printing GMV remains missing."
    },
    {
      "category_id": "C16",
      "name": "Apparel / shoes / bags",
      "demand_tier": "very_high",
      "confidence": "high",
      "us_sales_value": 245655771000,
      "us_sales_period": "2024",
      "us_sales_basis": "sum of relevant U.S. employer retailer-industry sales, not all-channel commodity GMV",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "high",
      "notes": "Excludes jewelry but still excludes/underrepresents pure-play and general-merchandise channels; must not be labeled total category GMV."
    },
    {
      "category_id": "C17",
      "name": "Home / organization / household goods",
      "demand_tier": "high",
      "confidence": "medium",
      "us_sales_value": null,
      "us_sales_period": "2026 forecast",
      "us_sales_basis": "subset of broad U.S. Home industry and household-expenditure proxies",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "high",
      "notes": "Broad Home forecast is $43.7B but overlaps C10."
    },
    {
      "category_id": "C18",
      "name": "Toys / collectibles / official merchandise",
      "demand_tier": "high",
      "confidence": "high",
      "us_sales_value": 45600000000,
      "us_sales_period": "2025",
      "us_sales_basis": "projected total U.S. toy industry market size",
      "online_share": null,
      "asp_usd": null,
      "purchase_frequency": null,
      "fragmentation": "high",
      "notes": "Circana tracked retail sales were $30.3B and covered about 68% of the U.S. toy market; broader collectibles/official merchandise may extend beyond toy tracking."
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    "Comparable current U.S. all-channel retail sell-through GMV for all 18 categories",
    "Category-specific online sales dollars and online share for most categories",
    "Retail ASP for most categories",
    "Annual unit volume for most categories",
    "Comparable household purchase incidence and purchase frequency",
    "Top-four brand revenue share or HHI for most categories",
    "Top-SKU concentration for most categories",
    "Amazon and other marketplace category share",
    "Independent U.S. demand split for mini PCs",
    "Independent maker/3D-printing demand excluding toys",
    "De-overlapped C10 versus C17 home-category taxonomy",
    "De-overlapped C14 outdoor equipment versus C16 apparel/footwear",
    "Authenticated CTA July 2026 detailed category data",
    "Current merchandise-line e-commerce data beyond the benchmarked 2022 Census detail"
  ],
  "pre_freeze_compliance": true
}
```