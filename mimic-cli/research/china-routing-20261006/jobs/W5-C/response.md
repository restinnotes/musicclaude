# W5-C — Logistics / Superbuy Infrastructure 独立研究报告

**WEB RESEARCH AVAILABLE。** 本报告只执行 W5-C，不执行 W1–W4/W6–W8，也没有重新选择、删除或替换冻结 SKU，没有做海外 SKU 价格比对。冻结样本 SHA256 为 `4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185`，共 **54/54 SKU 保留在分母中**。

研究 as-of 日期为 **2026-10-06（用户本地日期）**。本次工具时钟可核验的 UTC 时间锚点为 **2026-10-07T01:07:38Z、01:09:38Z、01:10:43Z、01:11:45Z**；UTC 已进入 10 月 7 日只是时区转换，不代表使用了 2026-10-06 之后发布的资料。网页工具没有为每一个 URL 暴露精确到秒的独立抓取时间，因此后附 JSON 的单源 `retrieved_at` 均保留 `null`，而不是伪造时间。最新有明确日期的核心供应商资料为 BuckyDrop **2026-09-15**；最新适用的 CBP 用户费表发表于 **2026-07-31、2026-10-01 生效**。[BuckyDrop Blog](https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/)

## 1. Direct answer

| 问题 | W5-C 结论 | 类型 / 信心 |
|---|---|---|
| Superbuy 能否作为基础设施？ | **能承担采购、入库、合单、拆单、国际直发这些基础操作；但还不能据公开资料证明其经济性足够好。** 普通 Taobao/Tmall/JD/1688 采购服务费公开为 0；国际运费以最终包裹、线路和物流商账单结算。 | FACT / high |
| 是否必须自己 physical aggregation？ | **不必然。** Superbuy SBS 明确宣传 dropship，并写有“拆分订单、分别寄给不同用户”；BuckyDrop 还有 API/自动履约。因此“1000 个订单分别直寄”在操作层面是已存在的模式。 | FACT → INFERENCE / medium-high |
| “1000 独立订单”能否拿明显商务物流价？ | **未证明。** 没找到 Superbuy、Sugargoo 或 BuckyDrop 对“1000 单/月”等公开、可审计的运价阶梯或折扣率。营销里的“exclusive discount / volume negotiation”不能当成交价。 | FACT / high |
| 美国实际线路多少钱？ | Superbuy 当前公开包裹流可观察到美国件，例如 **750g CN¥78、2,510g CN¥352.8、2,850g CN¥393.2、3,636g CN¥433.6、3,177g CN¥597.2**。但均缺 ZIP、三边、具体商品限制、完整税费条件，因此只是**公开实物流转样本，不是 ZIP10001 报价**。 | FACT / medium |
| standalone vs consolidated？ | 合单确实可以摊薄首重/外包装，但不是单调变便宜；体积重可能反向吞掉全部收益。一个 2026 Sugargoo 案例中，8.001kg、74×50×34cm 因 `/6000` 算成 **21.25kg 计费重**，原估算 $216 后又被要求补 $223.50。 | FACT anecdote / medium |
| 电池怎么处理？ | 不能写成“电池一律不能寄”或“一律能寄”。Superbuy 当前页面同时存在宽泛“battery cannot ship”提示和线路级“batteried items”可承运表；2025 商业快递线路也明确接受 built-in/attached batteries。必须逐线路判断。 | FACT / high |
| 2026 美国海关与旧模型有何不同？ | **$800 de minimis 不能再当默认免税。** EO 14388 继续对所有运输方式暂停免税；邮政新 informal-entry 规则 2026-07-24 生效。IEEPA 附加关税后来终止，但 Section 301 等其他关税明确没有因此消失。 | FACT / high |
| 冻结 54 SKU 能算出 landed shipping 吗？ | **0/54 达到可审计的 ZIP10001 exact quote 标准；54/54 均完成了非数字化物流分类。** 根本缺口是最终包装实际重量、L/W/H、具体线路以及 SKU HTS/Section 301。没有把任何缺失值填成估值。 | FACT / high |

Superbuy fee page：[https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/)；Superbuy calculator：[https://1688.superbuy.com/en/page/query/freight/](https://1688.superbuy.com/en/page/query/freight/)；Superbuy SBS：[https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)；BuckyDrop pricing：[https://www.buckydrop.com/en/services/pricing/](https://www.buckydrop.com/en/services/pricing/)。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

## 2. Evidence table

### 2.1 核心证据

| Claim | Evidence / 原始数字 | 日期 | Counterevidence / 限制 |
|---|---|---|---|
| C01 低值包裹不能再按旧 de minimis 模型 | EO 14388：无论价值、原产地、运输方式，原 §321 免税不适用；邮政新流程 2026-07-24 生效 | 2026-02-20 / 2026-06-24 | 新邮政流程还有至 2026-10-22 的部分数据字段过渡期；不能把邮政规则机械套到每个快递线路 |
| C02 2026-10-06 CBP 固定费已切换 FY2027 | automated informal entry **$2.77**；manual $8.30/$12.45；express hub per-waybill **$1.38**；formal MPF 0.3464%，min **$34.58**, max **$670.86** | 2026-07-31；生效 2026-10-01 | 哪项真正适用于某件包裹取决于 entry mode，不能全部叠加 |
| C03 Superbuy 零基础采购费不等于零成本 | JD/Taobao/Tmall/1688 标准采购费 0；90 天免费仓储；国际运费按最终重量/路线/目的地；可免费 consolidation | 当前无发布日期 | 可选 VAS、国内运费、国际运费、清关/税仍存在 |
| C04 体积重是关键 | Superbuy 公页：某些线路任何边 ≥60cm 时 `max(actual, L×W×H/6000)`；超长还有限制 | 当前页 | 不同线路公式不同，不能统一 `/6000` |
| C05 当前 Superbuy 美国公开件有真实价格观察值 | 750g ¥78；2510g ¥352.8；2850g ¥393.2；3636g ¥433.6；3177g ¥597.2 | 当前动态包裹流 | 缺 ZIP10001、三边、关税、完整商品属性，不能用于某 SKU landed cost |
| C06 商业直发无需先物理聚合 | SBS 写明 dropship、直接发客户、batch packing、拆单分别寄给不同用户 | 当前页 | 页面没有公开 B2B 运价和最低订单量；页面正文只能通过索引内容读取 |
| C07 BuckyDrop 的商业费层更透明 | Pro ¥199/月；fulfillment **¥9.90/parcel**；>5件 ¥2/件；>8kg ¥2/kg；公司称 carrier final weight/volume + flat ¥9.9；公开 API | 当前页 | “zero-markup”是公司自述，没有独立审计；国际 carrier rate 仍要具体 calculator |
| C08 Sugargoo 也是先估后结算 | 需要目的地、类别、重量、三边；pre-shipment simulation 后按最终重量/体积结算 | 更新至 2026-02-12 / 2026-01-07 | 本次直接打开博客返回 403，因此这些官方资料在 ledger 中降为 snippet_only |
| C09 体积重可使初估严重失真 | 8.001kg、74×50×34cm → 21.25kg billing weight；用户称 $216 后补 $223.50；Sugargoo staff 回复确认 `/6000` | 2026-09-22 附近 | 单一社区个案，不代表典型误差率 |
| C10 1000 separate orders 的“规模聚合”与 bulk import 不等价 | Superbuy/BuckyDrop 均已有 direct-to-customer workflow | 当前 | 1000 张面单仍是 1000 个独立包裹；不会因为商业量大就自动变成一票进口 |
| C11 54 SKU 没有一个具备完整 quote inputs | Frozen 数据没有最终代理仓包装后的重量和三边，HTS 也未逐 SKU 判定 | 2026-10-06 | 若以后补足真实 warehouse pack data 与 route quote，即可改变结果 |
| C12 不能证明 Superbuy 主要靠物流价差赚钱 | 它公开收部分专家/二手/VAS/超期仓储等费用，但不披露 freight gross margin | 当前 | 国际物流费中存在 operation fee 概念；这仍不足以证明其实际毛利率 |

美国政策源：[https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block)；[https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027](https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027)；[https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search](https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search)。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block)

### 2.2 四种物流结构必须分开

| 结构 | W5-C 定义 | 当前可观察经济性 | 海关/交付 endpoint | US sales tax |
|---|---|---|---|---|
| **1. Single-item standalone** | 一件 SKU 从中国代理仓单独寄 ZIP10001 | 需要该件最终 packed weight、L/W/H、battery class、线路；本轮 54 件全部缺 | 到 ZIP10001 门口；国际运费 + applicable duty + mandatory entry/carrier fees | **不计入本 W5 landed logistics**；与进口关税分开 |
| **2. Current consolidated-haul marginal** | 同一个美国消费者把多个国内订单合为一包 | Superbuy 免费 consolidation；可能摊薄首重，但体积重可能抵消 | 仍是一件最终国际包裹 | 同上 |
| **3. Commercial aggregation: 1000 separate fulfilled orders** | 商业上贡献 1000 单，但每单分别打包、分别寄消费者 | 运营能力已公开存在；**运价折扣未知**，无可审计公开阶梯 | 每个消费者仍拿独立包裹，不等于一票 bulk import | 同上 |
| **4. True bulk import** | 中国端把货物真正集中成大货，统一国际干线进口，再美国境内履约 | Superbuy calculator 对 ≥30kg/oversize 引导 customized logistics；实际商务价缺失 | 会引入完全不同的 formal entry / broker / bulk freight / US last-mile 结构 | 销售税仍是交易层问题，不应混入进口 freight |

因此，**“商业量聚合”可以在不物理聚货的情况下发生；但“物流成本聚合”不一定发生**。这是本 workstream 最重要的区别。Superbuy 对 ≥30kg 的提示只是“进入 customized logistics”的门槛，**不是批量折扣阈值**。[SuperBuy](https://1688.superbuy.com/en/page/query/freight/)

### 2.3 可观察的美国运费数字：只能作为 benchmark，不能算 SKU quote

| Provider / route | 公开观察 | Currency | Quote validity |
|---|---:|---|---|
| Superbuy Duty-Free Route (Apparel) | 750g / ¥78 / 8d | CNY | public parcel observation；不是 ZIP10001 exact quote |
| Superbuy YunExpress Clothing Registered | 2510g / ¥352.8 / 7d | CNY | 同上 |
| Superbuy YunExpress Clothing Registered | 2850g / ¥393.2 / 15d | CNY | 同上 |
| Superbuy YunExpress Clothing Registered | 3636g / ¥433.6 / 7d | CNY | 同上 |
| Superbuy YunExpress Air Cargo General | 3177g / ¥597.2 / 17d | CNY | 同上 |
| Superbuy fee-page example | 1000g / ¥428 = ¥320 first 500g + ¥50 continuation + ¥38 customs fee | CNY | 官方**示例**，不是实时美国报价 |
| Sugargoo California 3kg clothing | $55.18–$88.71 depending route | USD | **2025-10-17 以前的历史 estimator screenshot；2026 不可直接使用** |
| BuckyDrop | ¥9.90/parcel fulfillment + current carrier rate | CNY + carrier | fulfillment fee 当前可核；carrier freight 未取得 |

Superbuy public parcel feed：[https://www.superbuy.com/en/page/shoppingagent/](https://www.superbuy.com/en/page/shoppingagent/)。Sugargoo historical estimator source：[https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/](https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/?utm_source=chatgpt.com)。[Superbuy](https://www.superbuy.com/en/page/shoppingagent/)

### 2.4 冻结 54 SKU：逐项物流审计

**共同缺口 Q0**：所有 54 件都缺代理仓**最终 packed actual weight + L/W/H + 2026-10-06 对 ZIP10001 的可用 route/rate + 逐 SKU HTS/Section 301 判定**，所以全部只能评估为 `PARTIAL_NON_NUMERIC`，不能生成 standalone / consolidated / 1000-separate / bulk 四种结构的数字 landed cost。

| sku_id | 物流可评估内容 | 不能完成 exact quote 的额外原因 |
|---|---|---|
| C01-S01 | 手机、内置锂电 | Q0 + battery-special route |
| C01-S02 | 手机、内置锂电 | Q0 + battery-special route |
| C01-S03 | 手机、内置锂电 | Q0 + battery-special route |
| C02-S01 | 游戏本、锂电、较重 | Q0 + battery + dimensional risk |
| C02-S02 | 笔记本、锂电 | Q0 + battery + dimensional risk |
| C02-S03 | 笔记本、锂电 | Q0 + battery + dimensional risk |
| C03-S01 | iPad、锂电 | Q0 + battery |
| C03-S02 | iPad、锂电 | Q0 + battery |
| C03-S03 | 游戏平板、锂电 | Q0 + battery |
| C04-S01 | mini PC + 电源适配器 | Q0 + packed adapter dimensions |
| C04-S02 | 高配 mini PC + adapter | Q0 + high-value / packed dimensions |
| C04-S03 | barebone mini PC | Q0 |
| C05-S01 | M.2 SSD，小件无电池 | Q0；物流上相对容易，但 HTS/route 未补 |
| C05-S02 | 路由器 + adapter | Q0 |
| C05-S03 | DDR5 RAM，小件无电池 | Q0；物流上相对容易 |
| C06-S01 | TWS 耳机、锂电 | Q0 + battery |
| C06-S02 | 开放耳耳机、锂电 | Q0 + battery |
| C06-S03 | 耳夹耳机、锂电 | Q0 + battery |
| C07-S01 | G304，AA 电池体系 | Q0；是否随附电池需最终包裹确认 |
| C07-S02 | 无线鼠标 | Q0 + battery status 尚未在 frozen evidence 闭合 |
| C07-S03 | 有线键盘、无锂电 | Q0 |
| C08-S01 | wearable、内置电池/NFC | Q0 + battery/watch classification |
| C08-S02 | wearable、内置电池/NFC | Q0 + battery/watch classification |
| C08-S03 | smartwatch、内置电池 | Q0 + battery/watch classification |
| C09-S01 | 室内摄像头 | Q0 + 电源/网络设备包装 |
| C09-S02 | 智能门锁，重且安装件复杂 | Q0 + dimensional/weight risk + power details |
| C09-S03 | 220V 智能开关 | Q0；mains compatibility 不直接等于 freight，但影响可交付性 |
| C10-S01 | 扫拖机器人 + 基站 + 锂电 | Q0 + **high volumetric risk** + battery |
| C10-S02 | 自动上下水机器人/基站 | Q0 + **very high volumetric risk** + battery |
| C10-S03 | DJI ROMO P + 基站 + 锂电 | Q0 + **high volumetric risk** + battery |
| C11-S01 | 1050W 电锤，重型 mains tool | Q0 + high actual-weight risk |
| C11-S02 | 16V 双电工具 | Q0 + multiple lithium batteries |
| C11-S03 | 12V 电钻单电 | Q0 + lithium battery |
| C12-S01 | 相机 + 镜头套装 + 电池 | Q0 + high-value/battery |
| C12-S02 | 相机机身 + 电池 | Q0 + high-value/battery |
| C12-S03 | GO 3S + 内置电池 | Q0 + battery |
| C13-S01 | 行车记录仪套装 | Q0 + bundle/power components |
| C13-S02 | 行车记录仪套装 | Q0 + bundle/power components |
| C13-S03 | 充气泵 | Q0 + **power source 未闭合** |
| C14-S01 | 双人帐篷 | Q0 + packed-weight/volume risk |
| C14-S02 | 羽毛球拍，长尺寸 | Q0 + long-parcel dimensional constraint |
| C14-S03 | 帐篷 | Q0 + packed-volume risk + **frozen exact variant 尚 provisional** |
| C15-S01 | P2S Combo，大型 mains 设备 | Q0 + **very high bulky risk** |
| C15-S02 | A1 大陆版打印机 | Q0 + **high bulky risk** |
| C15-S03 | filament dryer/mains | Q0 + bulky/mains |
| C16-S01 | Coach tote | Q0 + branded / dimensional packaging |
| C16-S02 | AF1 鞋 | Q0 + shoe-box volumetric effect |
| C16-S03 | Superstar 鞋 | Q0 + shoe-box volumetric effect |
| C17-S01 | 34L×3 收纳箱 | Q0 + **extreme volumetric risk** |
| C17-S02 | 30.5L×2 抽屉箱 | Q0 + **extreme volumetric risk** |
| C17-S03 | 五层抽屉柜 | Q0 + **extreme volumetric risk** |
| C18-S01 | LEGO box | Q0 + retail-box volume |
| C18-S02 | 单个盲盒挂件 | Q0；相对轻小 |
| C18-S03 | RG 模型盒 | Q0 + collector box-condition packaging |

**结果：54/54 partial reviewed；0/54 exact quoted；0/54 因物流困难被剔除；0/54 被假设为“不可运”。**

## 3. Primary sources

| ID | 来源、日期、访问状态 | URL |
|---|---|---|
| S01 | Superbuy Fee Structure；无发布日期；full page | [https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/) |
| S02 | Superbuy Shipping Calculator；无发布日期；full page | [https://1688.superbuy.com/en/page/query/freight/](https://1688.superbuy.com/en/page/query/freight/) |
| S03 | Superbuy Business Service；当前；正文 open 为 JS 空页，索引内容可读，故 snippet_only | [https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com) |
| S04 | Superbuy public Shoppingagent/package feed；当前；full page | [https://www.superbuy.com/en/page/shoppingagent/](https://www.superbuy.com/en/page/shoppingagent/) |
| S05 | Superbuy restrictions / volumetric policy；当前；full page | [https://www.superbuy.com/en/page/buy/](https://www.superbuy.com/en/page/buy/) |
| S06 | BuckyDrop Pricing；当前；full page | [https://www.buckydrop.com/en/services/pricing/](https://www.buckydrop.com/en/services/pricing/) |
| S07 | BuckyDrop API/automation；当前；full page | [https://www.buckydrop.com/en/](https://www.buckydrop.com/en/) |
| S08 | BuckyDrop US fulfillment cost；2026-09-15；full page | [https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/](https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/) |
| S09 | Sugargoo freight estimator；2025-09-12，updated 2025-10-17；direct open 403 | [https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/](https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/?utm_source=chatgpt.com) |
| S10 | Sugargoo calculator comparison；2026-01-23，updated 2026-02-12；snippet_only | [https://blog.sugargoo.com/sugargoo-superbuy-mulebuy-kakobuy-shipping-calculator/](https://blog.sugargoo.com/sugargoo-superbuy-mulebuy-kakobuy-shipping-calculator/?utm_source=chatgpt.com) |
| S13 | White House EO 14388；2026-02-20；full page | [https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block) |
| S14 | CBP/Federal Register postal rule mirror；2026-06-24；full page mirror，官方站本次 CAPTCHA blocked | [https://regulations.justia.com/regulations/fedreg/2026/06/24/2026-12669.html](https://regulations.justia.com/regulations/fedreg/2026/06/24/2026-12669.html) |
| S15 | CBP/Federal Register FY2027 customs user fees；2026-07-31；full page | [https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027](https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027) |
| S16 | USTR Section 301 HTS search；current；full page | [https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search](https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search) |
| S17 | White House EO 14389；2026-02-20；full page | [https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/](https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/) |

Superbuy 公开 fee structure 还特别说明：国际运费预收只是 estimate，**最终金额按物流商 official bill reconciliation，多退少补**。这直接意味着任何没有最终包装数据的 frozen SKU 都不应得到“精确运费”。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

BuckyDrop 当前价格页给出的 **¥9.90/parcel** fulfillment fee 是本次找到的最清晰的商业直发固定费用，但其 carrier freight 仍要求 destination + package specs，不能拿这 ¥9.90 当“全部物流成本”。[BuckyDrop](https://www.buckydrop.com/en/services/pricing/)

## 4. Forum evidence

社区证据只用来判断实际摩擦，不把单个帖子当市场统计。最强一例是 Sugargoo 2026 年 9 月的大体积箱包案例：用户报告 8kg 包裹先付 $216 estimate，包装后补款 $223.50；Sugargoo staff 在同帖给出 74×50×34cm、`/6000=21.25kg` 的明确解释。URL：[https://www.reddit.com/r/Sugargoo/comments/1wmy1tm/440_to_ship_8kg_to_the_us/](https://www.reddit.com/r/Sugargoo/comments/1wmy1tm/440_to_ship_8kg_to_the_us/)。[Reddit](https://www.reddit.com/r/Sugargoo/comments/1wmy1tm/440_to_ship_8kg_to_the_us/)

另一个 2026 年帖子中，Sugargoo 官方账号明确说 submit parcel 时显示的是 **estimated fee**，要用 rehearsal shipping 后才按实际重量和体积得到 actual shipping fee。URL：[https://www.reddit.com/r/Sugargoo/comments/1wub7dy/sugargoo/](https://www.reddit.com/r/Sugargoo/comments/1wub7dy/sugargoo/)。[Reddit](https://www.reddit.com/r/Sugargoo/comments/1wub7dy/sugargoo/)

线路稳定性也不是常数。Sugargoo logistics staff 2026-05-22 曾披露香港→美国 UPS 因运力紧张排仓 **5–8 business days**；这说明长期产品模型不能把某条 7–10 天线路当固定 SLA。URL：[https://www.reddit.com/r/Sugargoo/comments/1tkdze6/sugargoo_shipping_status_update_522/](https://www.reddit.com/r/Sugargoo/comments/1tkdze6/sugargoo_shipping_status_update_522/)。[Reddit](https://www.reddit.com/r/Sugargoo/comments/1tkdze6/sugargoo_shipping_status_update_522/)

## 5. Contrary evidence

最强的反证不是“物流完全不可行”，而是下面这些会让一个看起来便宜的 China route 在计算时消失。

| 反证 | 对 thesis 的影响 |
|---|---|
| 8kg 实重可因体积变成 21.25kg 计费重 | C10/C15/C17 等低密度或带基站商品很可能被 freight 吞掉优势 |
| Superbuy 当前美国公开件 3kg 左右可达到约 ¥400–¥600 | standalone 并不是天然便宜，尤其对低 ASP SKU |
| de minimis 已停止 | 不能再拿旧研究中的“低于 $800=零关税/零 entry cost”当模型 |
| Section 301 没有随 IEEPA 关税终止而消失 | 必须逐 SKU HTS 查询；统一 tariff proxy 不合格 |
| BuckyDrop 自己明确说没有“可靠的统一美国运费” | 即使物流 API 做得很好，也不能预先把一条固定 $/kg 写进商业模型 |
| Superbuy SBS 的“专享折扣”没有价格表 | 证明存在商务服务，不证明 1000 单足以改变 rate |
| Superbuy 对电池的不同页面表述并不完全一致 | battery eligibility 必须按线路/仓库实时复核 |
| 合单只在同一最终客户的订单里自然产生物理经济性 | 1000 个不同消费者订单不会仅因“平台总量”自动共享首重 |

2026 年 EO 14389 明确只终止相应 IEEPA additional ad-valorem duties，并写明 **不影响 Section 232 / Section 301 duties**。URL：[https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/](https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/)。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/)

## 6. Confidence

| 子问题 | Confidence | 原因 |
|---|---|---|
| Superbuy 有 consumer forwarding / consolidation 能力 | **High** | 当前官方页面直接证明 |
| Superbuy 能把多个不同消费者的订单分别直寄 | **Medium-high** | 官方 SBS 索引正文明确，但 JS 页面本身本次无法全文打开 |
| BuckyDrop 支持 API/direct fulfillment | **High** | 当前官网全文 |
| 1000 separate orders 能得到有意义的运费折扣 | **Low / unproven** | 没有公开价表、阈值或成交报价 |
| physical aggregation 不是技术必需 | **Medium-high** | 两家公开 workflow 支持 direct fulfillment |
| physical aggregation 对成本一定不需要 | **Low** | 技术上不需要 ≠ 经济上不需要 |
| battery goods 可寄美国 | **Medium** | 有支持线路，但线路条件动态且页面存在宽泛相反提醒 |
| 2026 de minimis / CBP fixed fee 状态 | **High** | White House + CBP/Federal Register |
| 54 frozen SKU 的 exact landed shipping | **Low / unavailable** | 核心包裹数据完全缺失 |
| Superbuy 盈利主要来自 freight spread | **Low / unsupported** | 没有公开 margin/revenue mix 证据 |

## 7. Data gaps

`REAL SHIPPING QUOTE REQUIRED`：要给任一 frozen SKU 形成合格的 standalone 报价，至少必须有 **ZIP10001、最终包装实际重量、L/W/H、battery/危险品标记、申报价值、2026-10-06 当日线路、计费重公式、fuel/remote/handling/clearance 等所有 mandatory fee、税费承担方式**。本轮 ZIP 已固定，但其余关键项缺失，因此运费数字保持 `null`。Superbuy 和 BuckyDrop 的 calculator 都把重量、尺寸和商品类别作为核心输入。[SuperBuy](https://1688.superbuy.com/en/page/query/freight/)

`AUTHENTICATED / NEGOTIATED DATA REQUIRED`：Superbuy/Sugargoo/BuckyDrop 对 **1000 separately fulfilled U.S. orders** 的商务运价、volume tier、最低承诺量、fuel surcharge、peak surcharge、退件费、DDP/DAP 责任、账期和 API SLA。本次没有联系任何公司，因此这些全部未知。

`HTS CLASSIFICATION REQUIRED`：54 SKU 的 HTS、MFN、Chapter 99/Section 301、exclusion status 未逐件判定。USTR 当前工具要求先输入 **8-digit HTS subheading** 才能判断 Section 301 rate，所以不能从商品名称反推一个统一税率。[United States Trade Representative](https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search)

`US SALES TAX`：本 W5 对比 endpoint **明确排除美国州/地方 sales/use tax**，因为它是交易/卖方 nexus 层问题，不是 CBP import duty。本轮没有假装为 ZIP10001 自动加一个 NYC sales-tax 数字；后续跨渠道比较时，应对所有渠道采用同一税后/税前口径。BuckyDrop 自身的 2026 指南也把 sales tax 与 import duty 明确分开。[BuckyDrop Blog](https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/)

`SUPERBUY REVENUE MIX REQUIRED`：能确认其免费标准采购、收费 VAS、超期仓储以及部分专家服务；不能从公开资料判断 freight gross margin、支付费收入占比或商务折扣成本。不能回答“Superbuy 到底主要靠什么赚钱”到财务级精度。

## 8. Most surprising finding

最意外的不是某条线路便宜，而是 **“不自己建物流”与“不做物理 aggregation”这两件事在技术上都比预想更现实**。Superbuy 的企业服务已经公开描述“global dropshipping”“parcels delivered to your clients directly”“split orders and ship parcels to different users separately”；BuckyDrop 更进一步公开 API、自动订单同步与 per-parcel fulfillment fee。[superbuy.com](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

但这只解决了**操作架构**，没有解决**单位经济学**。现有证据无法证明“贡献 1000 个独立订单 → 商务价明显下降”。所以 W5-C 的关键判定是：

> **Physical aggregation is not operationally necessary; whether commercial aggregation alone creates sufficient freight economics remains unproven.**

第二个意外点是 2026 的 customs reset：旧 de-minimis 经济模型已经失效，而 FY2027 CBP fee 又刚在 2026-10-01 调整。任何用 2024/2025 freight spreadsheet 直接外推到 2026-10-06 的模型都可能在海关端系统性偏低。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block)

## 9. What would falsify this conclusion?

如果出现以下任一硬证据，我会下调“Superbuy/agent 可以作为轻资产基础设施”的判断：对相同的代表性包裹与 ZIP10001，Superbuy/Sugargoo/BuckyDrop 的最终账单长期显著高于直接消费者快递市场；所有可接受锂电的美国线路在当前海关规则下都变得不可用或异常昂贵；1000 separate-order RFQ 与 retail estimator 基本同价、且 per-parcel handling 增加后无规模收益；高 GMV frozen 类别的大多数商品实测 packed dimensional weight 使 freight 占商品价过高；或者真实 customs/broker/Chapter-99 requirements 迫使这些订单普遍转入 formal-entry 结构，使“低摩擦直邮”不能稳定执行。

反过来，如果 1000-order RFQ 能在**不物理集货、不做美国库存、仍逐单直发消费者**的条件下，稳定得到相对 retail estimator 显著下降且 all-in 的价格，那么 W5 的基础设施结论会明显转强。

## 10. Suggested next experiment

唯一最值得做的下一项实验是一个**标准化三家 RFQ / quote matrix**，而不是继续搜营销页。本次没有执行联系或购买。

固定 8–12 个包裹 archetype，覆盖约 0.3kg / 1kg / 3kg / 8kg、低/高体积重、普通货/内置锂电/双电池，并全部固定 ZIP10001、申报价值和服务时效。然后对 Superbuy、Sugargoo、BuckyDrop 同时取得四组价格：**1 单 standalone；同一客户 consolidation；1000 个不同消费者、分别履约；≥30kg/真正 bulk import**。要求每家公司书面拆出 carrier freight、warehouse/parcel fee、fuel/peak/remote/clearance、duty handling、退件费用以及 DDP/DAP，再与最终 carrier invoice reconciliation 复核。

这个实验一次就能回答当前最大未知：

> **“1000 个商业订单的 volume aggregation，本身是否足以形成物流经济，还是必须走 physical aggregation / bulk import 才有真正的 rate break？”**

---

```json
{
  "job_id": "W5-C",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fee Structure",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C12"]
    },
    {
      "source_id": "S02",
      "url": "https://1688.superbuy.com/en/page/query/freight/",
      "title": "Superbuy International Shipping Cost Estimator",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04", "C11"]
    },
    {
      "source_id": "S03",
      "url": "https://www.superbuy.com/en/page/businessservice/",
      "title": "Superbuy B2B Business Services",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C06", "C10"]
    },
    {
      "source_id": "S04",
      "url": "https://www.superbuy.com/en/page/shoppingagent/",
      "title": "Superbuy Shoppingagent public package feed",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S05",
      "url": "https://www.superbuy.com/en/page/buy/",
      "title": "Superbuy shopping agent logistics limitations",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S06",
      "url": "https://www.buckydrop.com/en/services/pricing/",
      "title": "BuckyDrop Pricing",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C10"]
    },
    {
      "source_id": "S07",
      "url": "https://www.buckydrop.com/en/",
      "title": "BuckyDrop All-in-One Auto Dropshipping Platform",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C10"]
    },
    {
      "source_id": "S08",
      "url": "https://blog.buckydrop.com/us-dropshipping-fulfillment-cost/",
      "title": "How Much Does Dropshipping Fulfillment Cost in the US?",
      "published_at": "2026-09-15",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C11"]
    },
    {
      "source_id": "S09",
      "url": "https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/",
      "title": "Estimate Your International Shipping Costs Online with Sugargoo",
      "published_at": "2025-09-12",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S10",
      "url": "https://blog.sugargoo.com/sugargoo-superbuy-mulebuy-kakobuy-shipping-calculator/",
      "title": "Sugargoo vs Superbuy vs Mulebuy vs Kakobuy Shipping Calculator",
      "published_at": "2026-01-23",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S11",
      "url": "https://www.reddit.com/r/Sugargoo/comments/1wmy1tm/440_to_ship_8kg_to_the_us/",
      "title": "$440 to ship 8kg to the US??",
      "published_at": "2026-09-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S12",
      "url": "https://www.reddit.com/r/Sugargoo/comments/1tkdze6/sugargoo_shipping_status_update_522/",
      "title": "SUGARGOO Shipping Status Update 5.22",
      "published_at": "2026-05-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S13",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02"]
    },
    {
      "source_id": "S14",
      "url": "https://regulations.justia.com/regulations/fedreg/2026/06/24/2026-12669.html",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02"]
    },
    {
      "source_id": "S15",
      "url": "https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027",
      "title": "Customs User Fees To Be Adjusted for Inflation in Fiscal Year 2027",
      "published_at": "2026-07-31",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    },
    {
      "source_id": "S16",
      "url": "https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search",
      "title": "How to Navigate the Section 301 Tariff Process",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C11"]
    },
    {
      "source_id": "S17",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/",
      "title": "Ending Certain Tariff Actions",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C02"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "As of 2026-10-06, the former $800 duty-free de minimis treatment cannot be assumed for China-to-US consumer parcels; the new postal informal-entry rule became effective July 24, 2026.",
      "classification": "FACT",
      "source_ids": ["S13", "S14"],
      "confidence": "high",
      "counterevidence": "The postal rule contains transition provisions and route-specific entry procedures, so it must not be applied as one universal per-parcel fee formula."
    },
    {
      "claim_id": "C02",
      "claim": "FY2027 CBP fees effective October 1, 2026 include $2.77 for automated informal entry not prepared by CBP, up to $1.38 per express-consignment waybill, and formal MPF limits of $34.58 to $670.86 at an unchanged 0.3464% rate; Section 301 duties were not eliminated by EO 14389.",
      "classification": "FACT",
      "source_ids": ["S15", "S16", "S17"],
      "confidence": "high",
      "counterevidence": "These fees are entry-mode specific and must not all be summed for every parcel."
    },
    {
      "claim_id": "C03",
      "claim": "Superbuy currently publishes zero standard purchasing-service fees for Taobao, Tmall, JD and 1688, free parcel consolidation, and final international freight reconciliation based on final parcel data and the logistics provider invoice.",
      "classification": "FACT",
      "source_ids": ["S01"],
      "confidence": "high",
      "counterevidence": "Domestic freight, international freight, customs costs, value-added services and other route fees remain."
    },
    {
      "claim_id": "C04",
      "claim": "Superbuy shipping economics depend materially on package dimensions and item restrictions; one published rule uses the greater of actual and volumetric weight with L*W*H/6000 when a side is at least 60 cm, and battery acceptance is route-specific.",
      "classification": "FACT",
      "source_ids": ["S02", "S05"],
      "confidence": "high",
      "counterevidence": "Not every carrier or route uses the same divisor or 60 cm rule."
    },
    {
      "claim_id": "C05",
      "claim": "The current public Superbuy package feed contains USA observations including CNY78 at 750g, CNY352.8 at 2510g, CNY393.2 at 2850g, CNY433.6 at 3636g and CNY597.2 at 3177g, but these are not valid SKU-specific ZIP10001 quotations.",
      "classification": "FACT",
      "source_ids": ["S04"],
      "confidence": "medium",
      "counterevidence": "The feed omits packed dimensions, destination ZIP, complete contents and customs assumptions."
    },
    {
      "claim_id": "C06",
      "claim": "Superbuy Business Service publicly describes dropshipping and splitting orders so parcels can be shipped separately to different end users.",
      "classification": "FACT",
      "source_ids": ["S03"],
      "confidence": "medium",
      "counterevidence": "The business-service page could not be opened as a normal full text page in this session, so the evidence is indexed-page content rather than a fully opened page."
    },
    {
      "claim_id": "C07",
      "claim": "BuckyDrop publishes a CNY9.90 per-parcel fulfillment fee, CNY2 per additional piece above five, CNY2/kg overweight surcharge above 8kg, and an API-enabled direct fulfillment workflow.",
      "classification": "FACT",
      "source_ids": ["S06", "S07", "S08"],
      "confidence": "high",
      "counterevidence": "Its zero-markup shipping and carrier-rate statements are company claims and do not supply a current ZIP10001 carrier quote."
    },
    {
      "claim_id": "C08",
      "claim": "Sugargoo's published workflow uses destination, product category, weight and dimensions and reconciles estimated shipping with final packed weight or volume; route capacity and timing can vary.",
      "classification": "FACT",
      "source_ids": ["S09", "S10", "S12"],
      "confidence": "medium",
      "counterevidence": "Sugargoo official blog pages returned 403 when directly opened in this session, and historical route prices are too stale for a 2026-10-06 landed-cost calculation."
    },
    {
      "claim_id": "C09",
      "claim": "A 2026 Sugargoo community case demonstrates that volumetric pricing can radically change cost: an 8001g parcel measuring 74x50x34 cm was confirmed by a Sugargoo account as 21.25kg billable weight under a /6000 rule.",
      "classification": "FACT",
      "source_ids": ["S11"],
      "confidence": "medium",
      "counterevidence": "This is a single anecdotal shipment and cannot establish an average or median surcharge."
    },
    {
      "claim_id": "C10",
      "claim": "Commercial aggregation of 1000 separately fulfilled consumer orders appears operationally possible without physical consolidation, but no public evidence establishes a specific 1000-order freight discount or threshold.",
      "classification": "INFERENCE",
      "source_ids": ["S03", "S06", "S07"],
      "confidence": "medium",
      "counterevidence": "A confidential commercial contract could contain meaningful rate tiers that are not publicly visible."
    },
    {
      "claim_id": "C11",
      "claim": "All 54 frozen SKUs could be classified for logistics risk, but none had sufficient packed weight, dimensions, route quotation and HTS data for an auditable ZIP10001 exact landed-shipping calculation.",
      "classification": "FACT",
      "source_ids": ["S02", "S08", "S16"],
      "confidence": "high",
      "counterevidence": "Warehouse rehearsal data or a complete current quote could immediately make individual SKUs numerically evaluable."
    },
    {
      "claim_id": "C12",
      "claim": "Public evidence is insufficient to determine Superbuy's revenue mix or to assert that its main profit source is a freight markup.",
      "classification": "INFERENCE",
      "source_ids": ["S01"],
      "confidence": "high",
      "counterevidence": "Non-public financials or logistics contracts could reveal a freight margin that is not disclosed on the consumer fee page."
    }
  ],
  "categories": [
    {"category_id":"C01","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"integrated lithium batteries; HTS and final package data missing","volumetric_risk":"medium"},
    {"category_id":"C02","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"lithium batteries and laptop package size","volumetric_risk":"medium_high"},
    {"category_id":"C03","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"integrated lithium batteries","volumetric_risk":"medium"},
    {"category_id":"C04","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"power adapters and packed dimensions","volumetric_risk":"medium"},
    {"category_id":"C05","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"HTS and route quote missing; relatively compact goods","volumetric_risk":"low"},
    {"category_id":"C06","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"integrated batteries in audio devices","volumetric_risk":"low"},
    {"category_id":"C07","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"mixed battery status and package data","volumetric_risk":"low_medium"},
    {"category_id":"C08","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"battery/watch route classification","volumetric_risk":"low"},
    {"category_id":"C09","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"mixed mains/power status and installation hardware","volumetric_risk":"medium"},
    {"category_id":"C10","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"battery plus large docking stations","volumetric_risk":"very_high"},
    {"category_id":"C11","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"heavy mains tool or lithium tool batteries","volumetric_risk":"medium_high"},
    {"category_id":"C12","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"lithium batteries and high-value camera equipment","volumetric_risk":"medium"},
    {"category_id":"C13","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"bundle and power-source details unresolved","volumetric_risk":"medium"},
    {"category_id":"C14","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"tent packed volume or long racket parcel","volumetric_risk":"high"},
    {"category_id":"C15","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"large mains-powered equipment","volumetric_risk":"very_high"},
    {"category_id":"C16","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"brand handling and retail-box volume","volumetric_risk":"medium"},
    {"category_id":"C17","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"very low density bulky storage goods","volumetric_risk":"extreme"},
    {"category_id":"C18","sku_count":3,"partial_evaluated":3,"exact_quote_count":0,"primary_logistics_issue":"retail/collector box dimensions","volumetric_risk":"medium"}
  ],
  "sku_candidates": [
    {"sku_id":"C01-S01","category_id":"C01","variant":"iPhone 17 256GB 白色 中国大陆双卡5G","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":6799,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"final packed weight/dimensions, live route, HTS and Section301 missing; integrated lithium battery"},
    {"sku_id":"C01-S02","category_id":"C01","variant":"iPhone 17 Pro 256GB 银色 中国大陆双卡","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"final packed weight/dimensions, live route, HTS and Section301 missing; integrated lithium battery"},
    {"sku_id":"C01-S03","category_id":"C01","variant":"OnePlus Ace 6T 12GB+256GB 闪速黑","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"final packed weight/dimensions, live route, HTS and Section301 missing; integrated lithium battery"},

    {"sku_id":"C02-S01","category_id":"C02","variant":"ASUS 天选7 Pro Ultra 7 251HX/16GB/1TB/RTX5060","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus laptop package; final packed data and HTS missing"},
    {"sku_id":"C02-S02","category_id":"C02","variant":"Lenovo 小新16SE R7/16GB/512GB","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus laptop package; final packed data and HTS missing"},
    {"sku_id":"C02-S03","category_id":"C02","variant":"MECHREVO 无界14 2026 Ultra5 226V/16GB/1TB","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus laptop package; final packed data and HTS missing"},

    {"sku_id":"C03-S01","category_id":"C03","variant":"iPad 11 A16 128GB WLAN 银色","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"integrated lithium battery; packed data and HTS missing"},
    {"sku_id":"C03-S02","category_id":"C03","variant":"iPad 11 A16 256GB WLAN 银色","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":4299,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"integrated lithium battery; packed data and HTS missing"},
    {"sku_id":"C03-S03","category_id":"C03","variant":"Lenovo Y700 五代 12GB+256GB Wi-Fi 碳晶黑","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":4299,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"integrated lithium battery; packed data and HTS missing"},

    {"sku_id":"C04-S01","category_id":"C04","variant":"ASUS 破晓迷你主机 i5-13500H/16GB/512GB","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"adapter and final packed dimensions unknown; live route and HTS missing"},
    {"sku_id":"C04-S02","category_id":"C04","variant":"GMK EVO-X2 Ryzen AI Max+395/128GB/2TB","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"high-value mini PC; final packed dimensions and HTS missing"},
    {"sku_id":"C04-S03","category_id":"C04","variant":"Beelink SER8 8745HS 深空灰准系统","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":2049,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"final packed dimensions, live route and HTS missing"},

    {"sku_id":"C05-S01","category_id":"C05","variant":"Samsung 990 EVO Plus 2TB","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"compact general item but packed data, live route and HTS missing"},
    {"sku_id":"C05-S02","category_id":"C05","variant":"Xiaomi BE6500 router","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"router plus power adapter; final packed data and HTS missing"},
    {"sku_id":"C05-S03","category_id":"C05","variant":"KINGBANK 银爵 32GB DDR5-6000 C36","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":3499,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"compact general item but packed data, live route and HTS missing"},

    {"sku_id":"C06-S01","category_id":"C06","variant":"EDIFIER Lolli Pro SE 云岩白","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery-powered earbuds; route-specific battery acceptance and packed data missing"},
    {"sku_id":"C06-S02","category_id":"C06","variant":"EDIFIER LolliClip SE 云霜金","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery-powered earbuds; route-specific battery acceptance and packed data missing"},
    {"sku_id":"C06-S03","category_id":"C06","variant":"EDIFIER Comfo Clip Q 奶霜白","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery-powered earbuds; route-specific battery acceptance and packed data missing"},

    {"sku_id":"C07-S01","category_id":"C07","variant":"Logitech G304 黑色","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"AA battery ecosystem; whether battery is included plus packed data and HTS unresolved"},
    {"sku_id":"C07-S02","category_id":"C07","variant":"Logitech GPW5 雪豹","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"wireless-device battery status not closed in frozen evidence; packed data and HTS missing"},
    {"sku_id":"C07-S03","category_id":"C07","variant":"ATK RS6+ 白武士 雪刃轴Pro 68键有线磁轴","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"wired non-battery item but packed data, live route and HTS missing"},

    {"sku_id":"C08-S01","category_id":"C08","variant":"Huawei Band 11 NFC 悦动白","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery/watch-category route constraints; packed data and HTS missing"},
    {"sku_id":"C08-S02","category_id":"C08","variant":"Huawei Band 11 Pro NFC 羽砂黑","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery/watch-category route constraints; packed data and HTS missing"},
    {"sku_id":"C08-S03","category_id":"C08","variant":"Xiaomi Watch S5 41mm 海盐蓝","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"battery/watch-category route constraints; packed data and HTS missing"},

    {"sku_id":"C09-S01","category_id":"C09","variant":"Xiaomi 智能摄像机4 800万像素4K","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"power accessories and final package data unresolved; HTS missing"},
    {"sku_id":"C09-S02","category_id":"C09","variant":"Xiaomi 智能门锁4 Pro 双摄版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"heavy installation hardware and power details unresolved; dimensional and HTS data missing"},
    {"sku_id":"C09-S03","category_id":"C09","variant":"Aqara S1E 皎月白 CJPKG01LM","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"220V mains device; packed data, route and HTS missing"},

    {"sku_id":"C10-S01","category_id":"C10","variant":"Roborock P20 Max A2950RR 非自动上下水","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus large base station; high dimensional-weight risk; HTS missing"},
    {"sku_id":"C10-S02","category_id":"C10","variant":"Roborock P20 Max A2950RR 自动上下水版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus plumbing/base components; very high dimensional-weight risk; HTS missing"},
    {"sku_id":"C10-S03","category_id":"C10","variant":"DJI ROMO P 水箱版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":3699,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery plus large base station; high dimensional-weight risk; HTS missing"},

    {"sku_id":"C11-S01","category_id":"C11","variant":"东成 DZC1050-26BT 1050W电锤","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"heavy mains tool; actual packed weight, route and HTS missing"},
    {"sku_id":"C11-S02","category_id":"C11","variant":"东成 WJZ1601S 16V双电套装","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"two lithium batteries; battery-capacity and route restrictions plus packed data missing"},
    {"sku_id":"C11-S03","category_id":"C11","variant":"Worx WU130X.1 12V 40Nm 2.0Ah单电","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"lithium battery; route restrictions, packed data and HTS missing"},

    {"sku_id":"C12-S01","category_id":"C12","variant":"Sony A7C II 银色 28-60mm套装","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"camera battery and high-value kit; packed data and HTS missing"},
    {"sku_id":"C12-S02","category_id":"C12","variant":"Sony Alpha 7 V A7M5 单机身","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"camera battery and high-value body; packed data and HTS missing"},
    {"sku_id":"C12-S03","category_id":"C12","variant":"Insta360 GO 3S 灵动白64G 标准版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"integrated lithium battery; packed data and HTS missing"},

    {"sku_id":"C13-S01","category_id":"C13","variant":"70mai M800Pro 前后双录4K 4G 无卡","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"bundle and vehicle-power components require final pack inspection; packed data and HTS missing"},
    {"sku_id":"C13-S02","category_id":"C13","variant":"DDPAI MINIPro 4K 无卡套餐","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"bundle and vehicle-power components require final pack inspection; packed data and HTS missing"},
    {"sku_id":"C13-S03","category_id":"C13","variant":"70mai 汽车轮胎充气泵青春版2 2026","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"power source not verified in frozen evidence; packed data, route and HTS missing"},

    {"sku_id":"C14-S01","category_id":"C14","variant":"MOBI GARDEN 冷山2PLUS 红灰双人带雪裙","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":799,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"tent packed weight and volume unknown; dimensional route and HTS missing"},
    {"sku_id":"C14-S02","category_id":"C14","variant":"李宁 战戟5000 4U空拍","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"long-parcel dimensions can trigger route restrictions; final dimensions and HTS missing"},
    {"sku_id":"C14-S03","category_id":"C14","variant":"Naturehike 云尚PRO 浅灰红/2人/20D尼龙 provisional mapping","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"frozen exact variant mapping remains provisional plus packed weight/volume and HTS missing"},

    {"sku_id":"C15-S01","category_id":"C15","variant":"Bambu Lab P2S/P2SC 多色套装","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"large bulky mains equipment; final package dimensions and HTS missing"},
    {"sku_id":"C15-S02","category_id":"C15","variant":"Bambu Lab A1 单机大陆版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"large bulky mains equipment; final package dimensions and HTS missing"},
    {"sku_id":"C15-S03","category_id":"C15","variant":"Creality Space Pi V2 Plus 大陆版","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"mains-powered bulky accessory; product URL unresolved in frozen evidence and packed data/HTS missing"},

    {"sku_id":"C16-S01","category_id":"C16","variant":"COACH CV976 CITY33 奶茶色","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"branded item and bag packaging dimensions affect route; final pack and HTS missing"},
    {"sku_id":"C16-S02","category_id":"C16","variant":"NIKE CW2288-111 AF1 白色42码","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"shoe-box volume and branded-item handling; final pack and HTS missing"},
    {"sku_id":"C16-S03","category_id":"C16","variant":"adidas JI0079 Superstar II 37码","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"shoe-box volume and branded-item handling; final pack and HTS missing"},

    {"sku_id":"C17-S01","category_id":"C17","variant":"CHAHUA 34Lx3 奶黄色收纳箱","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"extreme low-density volumetric risk; packed dimensions and HTS missing"},
    {"sku_id":"C17-S02","category_id":"C17","variant":"CHAHUA 30.5L两只装抽屉式收纳箱","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"extreme low-density volumetric risk; packed dimensions and HTS missing"},
    {"sku_id":"C17-S03","category_id":"C17","variant":"JEKO&JEKO 五层抽屉式收纳柜","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"extreme bulky volumetric risk; packed dimensions and HTS missing"},

    {"sku_id":"C18-S01","category_id":"C18","variant":"LEGO 10698 经典创意积木盒赠礼袋","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"retail-box size affects volumetric freight; packed data and HTS missing"},
    {"sku_id":"C18-S02","category_id":"C18","variant":"POP MART CRYBABY Vacation Mode On 随机1个","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"relatively small general good but final packed data, route and HTS missing"},
    {"sku_id":"C18-S03","category_id":"C18","variant":"BANDAI RG 1/144 RX-78-2 RGU ver2.0","observation_date":"2026-10-06","status":"partial_non_numeric","china_price_cny":null,"domestic_shipping_cny":null,"agent_fee_cny":null,"packed_weight_g":null,"dimensions_cm":null,"international_freight_cny":null,"tariff_hts":null,"tariff_usd":null,"customs_fee_usd":null,"us_sales_tax_usd":null,"structures":{"standalone":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null},"reason":"collector-box packaging can increase dimensions; final pack data and HTS missing"}
  ],
  "data_gaps": [
    {
      "gap_id": "G01",
      "gap": "No frozen SKU has final warehouse-packed actual weight and length/width/height.",
      "required_data": "packed actual weight, L/W/H after mandatory protection and package removal choices",
      "state": "REAL SHIPPING QUOTE REQUIRED"
    },
    {
      "gap_id": "G02",
      "gap": "No current auditable ZIP10001 line quotation was generated for any of the 54 SKUs.",
      "required_data": "provider, route, date, battery class, billable-weight formula, all carrier surcharges and final settlement basis",
      "state": "REAL SHIPPING QUOTE REQUIRED"
    },
    {
      "gap_id": "G03",
      "gap": "No public rate tier was found for 1000 separately fulfilled US consumer orders.",
      "required_data": "written commercial rate card or RFQ with volume commitment, parcel profiles and surcharge schedule",
      "state": "AUTHENTICATED DATA REQUIRED"
    },
    {
      "gap_id": "G04",
      "gap": "SKU-level HTS, MFN, Section 301 and exclusion status were not determined.",
      "required_data": "8/10-digit HTS classification and USTR/HTS Chapter 99 lookup per exact product",
      "state": "MANUAL TARIFF CLASSIFICATION REQUIRED"
    },
    {
      "gap_id": "G05",
      "gap": "Superbuy revenue and freight-margin mix is not public.",
      "required_data": "financial statements, carrier contracts or internal unit economics",
      "state": "UNVERIFIED"
    },
    {
      "gap_id": "G06",
      "gap": "Sugargoo official blog detail pages returned 403 during direct retrieval.",
      "required_data": "current public calculator output using identical package assumptions",
      "state": "snippet_only"
    },
    {
      "gap_id": "G07",
      "gap": "US state/local sales tax is not included in W5 landed-logistics values.",
      "required_data": "seller architecture, nexus, marketplace-facilitator status and transaction-specific tax treatment",
      "state": "EXCLUDED_FROM_W5_ENDPOINT"
    },
    {
      "gap_id": "G08",
      "gap": "Commercial aggregation and physical consolidation have not been tested against identical parcel profiles.",
      "required_data": "standalone, same-customer consolidation, 1000 separate-order and true-bulk written quotes under identical assumptions",
      "state": "DECISIVE EXPERIMENT REQUIRED"
    }
  ],
  "pre_freeze_compliance": true
}
```