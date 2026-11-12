# W5-B｜Logistics / Superbuy Infrastructure

**WEB RESEARCH AVAILABLE：是。**

研究范围严格限定为 W5-B；未执行 W1–W4/W6–W8，也未改变冻结样本。冻结样本 SHA256：`4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185`。54 个 frozen SKU 全部保留，0 个删除。

**实际网页检索 UTC 窗口：2026-10-07T01:04:04Z 至 2026-10-07T01:09:22Z。** 这对应研究 as-of 2026-10-06 的美国时段。网页工具没有提供逐来源精确 fetch clock，因此下面 JSON 的 `retrieved_at` 全部保留为 `null`，不伪造逐页时间。

最新具有明确日期、且会改变模型的数据是：CBP FY2027 customs user fees **自 2026-10-01 生效**；最新用于本报告的 Federal Register publication 是 2026-07-31。公司实时页面本身没有 `published_at`，只能记录本次检索窗口。 :chatgpt-content-reference{index="0"}

## 1. Direct answer

1. **[FACT] 从“能力”而不是“价格”看，并不需要研究方自己做 physical aggregation 才能实现 China → 美国消费者逐单履约。** BuckyDrop 已公开支持 Shopify/WooCommerce 自动同步订单、自动采购、包裹提交、物流跟踪，并提供 API 集成。Superbuy 的官方商务页搜索提取还明确出现“split orders and ship parcels to different users separately”，但该页正文在本会话动态渲染为空，因此这一条按 **UNVERIFIED official snippet** 处理，而不是 full-page verified。 :chatgpt-content-reference{index="1"}

2. **[INFERENCE] “1000 个独立消费者订单形成商业量，但仍逐票直寄”在操作上可行；是否仅凭商业 volume aggregation 就能获得足够大的运价折扣，公开证据不足。** 我没有发现 Superbuy、Sugargoo 或 BuckyDrop 公开发布“1000票/月 → X%折扣”一类阶梯运价。Superbuy 的 ≥30kg customized logistics 是货物/单票规模入口，不是月度订单量折扣；BuckyDrop Pro 的 unlimited fulfillment 也是软件/履约额度，不是 freight discount。**AUTHENTICATED / NEGOTIATED DATA REQUIRED。** :chatgpt-content-reference{index="2"}

3. **[FACT] 54 个冻结 SKU：54/54 可以做物流属性筛查，但 ZIP 10001 的 quote-grade 实际国际运费为 0/54。** 原因不是“找不到商品”，而是冻结样本没有代理仓重打包后的实际重量和 L×W×H；对于电池、品牌品、大件还缺具体可走线路及必收费项。Superbuy 自己的 calculator 就要求目的地、重量、尺寸、货物类型；BuckyDrop calculator 同样需要重量、尺寸、商品类别，并提供邮编字段。 :chatgpt-content-reference{index="3"}

4. **[FACT] 2026 年最大的结构性变化是美国 de minimis。** 非邮政渠道的 ≤$800 行政豁免自 2026-06-24 无限期暂停；邮政渠道也已暂停，并自 2026-07-24采用新的 low-value informal-entry 体系。邮政新流程要求包括 **10-digit HTSUS、原产国、价值、适用税率、总税额** 等。因此不能再把“低于 $800 = 无关税/清关成本”作为基础假设。 :chatgpt-content-reference{index="4"}

5. **[FACT] 体积重足以改变整个 category 的 economics。** Superbuy 公开 calculator 写明多数空运体积重为 `L×W×H/6000`；其另一个物流说明页显示部分规则在边长达到阈值后按实重与体积重取大。故 C17 收纳箱、C10 扫地机器人、C15 3D 打印设备，以及鞋盒/帐篷等不能仅凭商品净重筛选。 :chatgpt-content-reference{index="5"}

6. **[FACT] BuckyDrop 是三者中公开 unit economics 最清楚的一个。** 当前公开价为 Pro `CNY199/月/店`、fulfillment `CNY9.90/parcel`，≤5 件基础处理包含在内；>5件 `CNY2/件`、>8kg `CNY2/kg`。页面物流部分又称承运商最终重量/体积“zero-markup”结算、另有 flat `CNY9.9` service fee。为了避免把同一个 9.9 重复计费，本报告只将其视为**至少一项公开的 CNY9.9/parcel 固定履约/服务费，需要商务书面确认两处描述是否为同一笔**。若 1000 票均处基础范围，公开表面固定费算术为 **CNY9,900**，另加订阅、实际 freight、关税/清关和其他适用收费；这不是 B2B negotiated rate。 :chatgpt-content-reference{index="6"}

7. **[FACT] Superbuy 的公开收费模式并不是“代购统一抽佣”。** 淘宝/Tmall/JD/1688 普通代购公开采购服务费为 0；可见收费杠杆包括非标准/二手平台采购费、包装/QC 等增值服务，以及国际运输成本结构中的 operation fee 等。但没有公开审计数据证明 Superbuy 在 carrier freight 上赚多少 spread，也没有公开收入分部可据此回答“主要靠什么赚钱”。 :chatgpt-content-reference{index="7"}

8. **[INFERENCE] W5 物流本身最友好的冻结类别是紧凑、非电池或小电池商品；最不友好的是低密度大件。** 这只是物流 screening，不含 demand、美国售价、产品兼容、法规或售后，因此不是总体机会评分。

**A/B/C exact/OEM/comparable 统计：N/A。** W5-B 没有做海外 SKU matching，也没有把三类混算。

---

## 2. Evidence table / 原始数据

| Claim | 分类 | 可审计证据 | 反证/限制 | Confidence |
|---|---|---|---|---|
| Superbuy 标准采购费可为 0 | FACT | Taobao/Tmall/JD/1688 standard purchasing = no service fee；国际运费另算 | 不代表 freight 无利润，也不代表所有采购来源免费 | High |
| Physical aggregation 不是技术必要条件 | FACT/INFERENCE | BuckyDrop 自动逐单履约/API；Superbuy 商务页 snippet 明示可拆单寄不同用户 | Superbuy 该页未完整打开；没有证明这是最低成本结构 | Medium |
| 1000 单商业量可获折扣 | **未证实** | 三家公开资料均未发现 1000 单阶梯表 | 私有商务合同可能存在 | Medium |
| BuckyDrop 固定履约成本 | FACT | CNY9.90/parcel，Pro CNY199/月/店 | 两处 CNY9.9 描述可能为同一费用，不能双计 | High |
| 体积重是主要成本变量 | FACT | Superbuy `/6000`；部分线路实重/体积重取大 | 不是所有路线公式相同 | High |
| 2026 de minimis 已不能继续使用 | FACT | 两份 2026-06-24 CBP interim final rules | 不意味着所有商品统一税率 | High |
| FY2027 customs fee 已更新 | FACT | 2026-10-01 起正式 MPF min $34.58 / max $670.86；informal $2.77/$8.30/$12.45 | 具体一票不会把所有收费相加 | High |
| 54 frozen SKUs 实际 freight quote | FACT | **0/54 quote-grade** | 登录态与人工补充尺寸后可解决 | High |
| 社区实际体验存在 volumetric/customs variance | FACT | Reddit 有实重远低于体积重以及检查/延迟案例 | 严重 selection bias，不能变成发生率 | Medium |
| 州/地方 sales tax 处理 | FACT | CBP 不替州征收 state sales tax | 消费者仍可能依法承担 sales/use tax | High |

Superbuy 当前公开 parcel feed 可看到美国方向的真实历史/近期展示记录，例如：`2510g`、YunExpress clothing Registered Air Mail、`CNY352.8`；`2850g` 同线路 `CNY393.2`；`3177g` YunExpress Air Cargo (General) `CNY597.2`。这些记录**缺 ZIP、尺寸、商品组成、申报价值和完整税费结构，只能证明公开系统中的线路/价位确实存在，不能当本冻结 SKU 的报价**。 :chatgpt-content-reference{index="8"}

---

## 3. Primary sources

| ID | 来源 / 日期 / access state | URL | 用途 |
|---|---|---|---|
| S01 | Superbuy Fee Structure；无发布日期；read_full_page |  | 采购费、增值服务、运费构成、免费合单 |
| S02 | Superbuy Shipping Calculator；无发布日期；read_full_page |  | 重量/尺寸/品类、电池、体积重、≥30kg custom |
| S03 | Superbuy B2B Business Services；snippet_only |  | batch / split-to-different-users；**UNVERIFIED full page** |
| S04 | BuckyDrop Pricing；无发布日期；read_full_page |  | CNY199、CNY9.9、surcharges、storage |
| S05 | BuckyDrop Solution API；snippet_only，直接 open timeout |  | order/parcel/logistics API |
| S06 | BuckyDrop Dropshipping；read_full_page |  | Shopify/WooCommerce 自动逐单履约 |
| S07 | Sugargoo calculator guide，2026-01-23；2026-02-12 update；**blocked on direct open** |  | calculator 存在线索；具体数据 UNVERIFIED ([Invalid URL]()) |
| S08 | Sugargoo Business Solutions，2025-09-17；**blocked on direct open** |  | enterprise service 存在线索；商务价 UNVERIFIED ([Invalid URL]()) |
| S09 | CBP/Federal Register，2026-06-24；read_full_page |  | 非邮政 de minimis 无限期暂停 |
| S10 | CBP/Federal Register，2026-06-24；read_full_page |  | 邮政 de minimis / informal entry / HTS10 |
| S11 | CBP/Federal Register，2026-07-31；FY2027 fees 2026-10-01 生效 |  | 当前 customs user fees |
| S12 | CBP，2026-06-13 |  | state sales tax 与 customs 分开 |

以上来源均仍应由 coordinator 最终 review；尤其 S03/S05/S07/S08 的 access state 必须保留，不能升级成 full-page evidence。

---

## 4. Forum evidence

社区证据只用于“实际 friction 是否存在”，不用于费率或发生率推断。

- **2026-05-22，r/Superbuy**：用户报告一票实重约 5.2kg，而 volume estimate 约 10.9kg，并讨论 rehearsal/Shipping Expert 后的差异。这与官方“体积重可能主导”方向一致，但单个帖子不能推算平均 uplift。 
- **2026-07-13，r/Sugargoo**：美国用户讨论 tax-free/其他线路出现 customs inspection、滞留等情况。它是“风险真实存在”的反证，而不是 seizure probability。 

---

## 5. Contrary evidence

第一，**“不必自建 physical aggregation”不等于“不应该物理合单”**。Superbuy 自己明确说多件商品可免费 consolidation，并可能降低国际运费；首重重复、包装空隙和干线包量仍可能使物理合并更便宜。 :chatgpt-content-reference{index="25"}

第二，体积重也不是所有线路都必然处罚。Superbuy 的公开规则本身显示，不同路线和尺寸阈值可以按不同计费方法，因此不能把 `/6000` 当成每票统一 formula。 :chatgpt-content-reference{index="26"}

第三，BuckyDrop 的 `CNY9.9/parcel` 很透明，但其两处“fulfillment fee / flat service fee”措辞是否为同一收费，公开页没有足够清晰地消除歧义；本报告拒绝把它们加成 CNY19.8。

第四，代理商公开“business service”本身不能证明 commercial-volume discount。Superbuy 明确接受 business cooperation，但没有公开 rate card；Sugargoo 也给出企业服务入口，但本会话无法完整打开其页面。 :chatgpt-content-reference{index="27"}

第五，2026 customs 架构削弱了过去小包直邮最强的结构性优势。每票都需要更完整的 classification/entry 数据，意味着“软件上能逐单发”与“逐单发仍然便宜”是两个完全不同的问题。 :chatgpt-content-reference{index="28"}

---

## 6. Confidence、四种 shipment structure 与 category logistics map

### 四种结构必须分开

| Structure | 当前能证明什么 | 当前成本结果 |
|---|---|---|
| 1. Single-item standalone | 三家基础设施均面向单包裹国际运输；电池/类别影响可选线路 | **null：0/54 quote-grade** |
| 2. Current agent consolidated-haul marginal | Superbuy 免费 consolidation；Sugargoo 也公开宣传 combine package | **null**；需具体组合和重打包尺寸 |
| 3. Commercial aggregation：1000 个独立订单、仍分别寄消费者 | BuckyDrop 自动逐单 fulfillment 已验证；Superbuy split-to-different-users 为 official snippet | **negotiated freight=null**；BuckyDrop 公开基础固定费可做 CNY9.9/parcel 算术，但不是商务折扣 |
| 4. True bulk import | Superbuy 对 ≥30kg/oversized 提供 customized logistics；与逐单包裹完全不同 | **null**；需要货盘/箱规、清关/进口结构、美国境内配送 |

**比较终点：** 中国商品价格 + 中国境内运费 + mandatory agent/warehouse/processing fee + 国际运费 + applicable duty + mandatory customs/entry/carrier processing fee，**送达 ZIP10001，州/地方 sales/use tax 之前**。Sales/use tax 单列，不假定为 0；CBP 明确其不代州征收州销售税。 :chatgpt-content-reference{index="29"}

### Logistics-only category map

| Category | W5物流可行性 | 核心原因 |
|---|---|---|
| C01 Smartphones | Medium | 小体积但锂电、高货值 |
| C02 Laptops | Medium-Low | 锂电 + 较重/高货值 |
| C03 Tablets | Medium | 锂电但体积相对可控 |
| C04 Mini PCs | Medium-High | 无内置电池、体积尚可 |
| C05 Components/networking | High | SSD/RAM 很紧凑；路由器仍需适配器空间 |
| C06 Audio | Medium-High | 小，但 TWS 为锂电敏感品 |
| C07 Peripherals | High | 多数紧凑，ATK 有线尤其友好 |
| C08 Wearables | Medium-High | 极轻但电池线路受限 |
| C09 Smart home | Medium | 电源/安装部件及包装差异 |
| C10 Robot vacuum | Low | 大体积 + 电池 + 基站 |
| C11 Tools | Low-Medium | 重量、锂电池包或市电工具 |
| C12 Camera/video | Medium | 高值、易损、电池 |
| C13 Automotive | Medium | 通常体积可控，但 bundle/power 需闭合 |
| C14 Sports/outdoor | Medium-Low | 帐篷体积、球拍超长/易损 |
| C15 3D printing | Low-Medium | 大件/高体积重 |
| C16 Apparel/shoes/bags | Medium | 鞋盒/包体积，品牌线路需核 |
| C17 Home organization | Low | 最明显的 volumetric-weight 风险 |
| C18 Toys/collectibles | Medium-High | 无电池，但保护包装/盒况增加体积 |

这些评级全部是 **INFERENCE、logistics-only**，不能用于总体投资或 demand 结论。

---

## 7. Data gaps + frozen SKU ledger

统一 blocker 定义：

**B1**＝电池/锂电类：缺代理重打包重量及尺寸、当前 battery-eligible route、HTS10 与必收费项。  
**B2**＝紧凑非电池/外接电源：缺重打包重量尺寸、当前线路、HTS10。  
**B3**＝大件/明显体积重风险：缺 packed dimensions/chargeable volumetric weight、线路、HTS10。  
**B4**＝工具/市电/电池包：缺包装尺寸、充电器/电池线路及 HTS10。  
**B5**＝冻结样本自身电源或套装边界尚未闭合，再叠加尺寸/HTS 缺口。  
**B6**＝品牌包鞋：缺包装体积、鞋盒策略、品牌敏感线路、HTS10。  
**B7**＝一般/易损/收藏品：缺最终保护包装尺寸和 HTS10。  
**B8**＝冻结 exact variant 自身仍为 PROVISIONAL，但**不删除**；另缺物流输入。

| Category | Frozen SKU status |
|---|---|
| C01 | `C01-S01` iPhone 17 256GB — screened / no quote / B1；`C01-S02` iPhone 17 Pro — B1；`C01-S03` OnePlus Ace 6T — B1 |
| C02 | `C02-S01` ASUS 天选7 Pro — B1；`C02-S02` 小新16SE — B1；`C02-S03` MECHREVO 无界14 — B1 |
| C03 | `C03-S01` iPad 128GB — B1；`C03-S02` iPad 256GB — B1；`C03-S03` Y700 五代 — B1 |
| C04 | `C04-S01` ASUS 破晓 mini PC — B2；`C04-S02` GMK EVO-X2 — B2；`C04-S03` Beelink SER8 barebone — B2 |
| C05 | `C05-S01` Samsung 990 EVO Plus 2TB — B2；`C05-S02` Xiaomi BE6500 — B2；`C05-S03` KINGBANK DDR5 — B2 |
| C06 | `C06-S01` Lolli Pro SE — B1；`C06-S02` LolliClip SE — B1；`C06-S03` Comfo Clip Q — B1 |
| C07 | `C07-S01` Logitech G304/AA — B1；`C07-S02` GPW5 rechargeable status/route — B1；`C07-S03` ATK RS6+ wired — B2 |
| C08 | `C08-S01` Huawei Band 11 NFC — B1；`C08-S02` Band 11 Pro — B1；`C08-S03` Xiaomi Watch S5 — B1 |
| C09 | `C09-S01` Xiaomi Camera 4 — B2；`C09-S02` Smart Lock 4 Pro，power detail 未闭合 — B5；`C09-S03` Aqara S1E 220V — B4 |
| C10 | `C10-S01` Roborock P20 Max — B3；`C10-S02` P20 Max 自动上下水 — B3；`C10-S03` DJI ROMO P — B3 |
| C11 | `C11-S01` 东成 DZC1050 — B4；`C11-S02` WJZ1601S 双电 — B4；`C11-S03` Worx WU130X.1 — B4 |
| C12 | `C12-S01` Sony A7C II kit — B1；`C12-S02` Sony A7 V body — B1；`C12-S03` Insta360 GO 3S — B1 |
| C13 | `C13-S01` 70mai M800Pro — B2；`C13-S02` DDPAI MINIPro — B2；`C13-S03` 70迈充气泵，power source 未闭合 — B5 |
| C14 | `C14-S01` 牧高笛冷山2PLUS — B3；`C14-S02` 李宁战戟5000，超长/易损 — B7；`C14-S03` Naturehike 云尚PRO — **B8 / frozen provisional retained** |
| C15 | `C15-S01` Bambu P2S Combo — B3；`C15-S02` Bambu A1 — B3；`C15-S03` Space Pi V2 Plus — B3 |
| C16 | `C16-S01` COACH CV976 — B6；`C16-S02` Nike AF1 42 — B6；`C16-S03` adidas JI0079 37 — B6 |
| C17 | `C17-S01` CHAHUA 34L×3 — B3；`C17-S02` CHAHUA 30.5L×2 — B3；`C17-S03` JEKO 5-layer cabinet — B3 |
| C18 | `C18-S01` LEGO 10698 — B7；`C18-S02` POP MART blind box — B7；`C18-S03` BANDAI RG RX-78-2 — B7 |

所以分母严格保持 **54**；“0/54 获得 quote”不能被解释为“不支持运输”，而是 **54 个都是 quote inputs incomplete / authenticated quote not obtained**。

所有 HTS10 和 tariff rate 在本报告保持 `null`。2026 邮政规则本身明确要求适用的 10-digit HTSUS，因此没有逐 SKU classification 就不能制造统一 tariff。 :chatgpt-content-reference{index="30"}

---

## 8. Most surprising finding

最意外的不是“Superbuy 可以合单”，而是成熟 infrastructure 已经相当接近**商业订单路由层**：BuckyDrop 有自动 order sync、采购、仓储、包裹提交、物流 tracking 和 API；Superbuy 的商务页面则公开描述 batch shipping 与 split-to-different-users 两种方向。

因此 W5 的主要技术未知已经不是“有没有中国仓能替消费者发包裹”，而是：

**独立消费者包裹的商业量是否能换来足够低的真实 freight + customs processing economics，而不需要把这 1000 个订单先物理合成一个进口批次。**

这一点目前仍**没有公开数据证明**。 :chatgpt-content-reference{index="31"}

---

## 9. What would falsify this conclusion?

1. 如果取得三家之一正式、可复核的 `1,000 separate consumer parcels/month` rate card，显示无需物理合单即可获得与批量干线接近的阶梯折扣，那么目前“commercial-rate advantage unproven”的结论会被推翻。

2. 如果对同一批 frozen SKU 做实际仓库重打包后发现 C10/C15/C17 的 chargeable weight 基本仍等于实重，则我对 bulky categories 的 volumetric-risk 判断会显著下降。

3. 如果 2026 后美国线路的代理报价已经在一个明确 DDP/税包机制中完全内含 duty、entry/broker costs，且价格与旧 de minimis 小包经济接近，那么 customs 结构变化对消费者 economics 的负面影响会低于本报告判断。

4. 如果 Superbuy 有未公开但成熟、稳定的生产 API + consumer-order orchestration，并有明确 SLA，那么 BuckyDrop 在 integration 层面的公开证据优势会消失。

5. 如果大样本线路数据证明 Reddit 所见 customs/volume-weight friction 是极端异常，而正常延误/费用方差很小，则社区风险证据的重要性会下降。

---

## 10. Suggested next experiment

如果只能再做一个研究实验，应做一个**authenticated, no-purchase logistics quote matrix**：

从冻结集预注册抽取 12 个 SKU，覆盖 compact/no-battery、compact/lithium、medium/heavy-lithium、bulky/volumetric 四个物流 strata。对每个 SKU 获取**代理最终打包 weight + L×W×H**，然后在同一天、同一目的地 **ZIP10001** 下分别保存 Superbuy、Sugargoo、BuckyDrop 的完整 quote 页面/截图/JSON，包括：

`route → actual weight → volumetric weight → chargeable weight → first/additional freight → mandatory handling/operation fee → battery/sensitive surcharge → insurance mandatory/optional → duty handling model → customs/broker/entry fees → ETA → tax treatment`。

同时单独获取一份书面问题完全固定的商务 rate request：

> `1,000 separate US consumer parcels/month, individually addressed and fulfilled; no physical consolidation after warehouse receipt; provide rate tiers by monthly parcels/chargeable kg and all mandatory per-parcel fees.`

结果必须分别保存四个结构：standalone、current consolidated marginal、commercial-1000-separate、true bulk import；不能把任何商务报价外推给另一结构。

在拿到这一步以前，**“Superbuy/BuckyDrop 能当基础设施”是 operationally supported；“不做 physical aggregation 仍能获得足够强的 scale economics”仍然是未证实命题。**

```json
{"job_id":"W5-B","web_research_available":true,"sources":[{"source_id":"S01","url":"https:\/\/www.superbuy.com\/en\/page\/guide\/feecomposition\/","title":"Superbuy Fee Structure","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"read_full_page","claims_supported":["C01","C11"]},{"source_id":"S02","url":"https:\/\/login.superbuy.com\/en\/page\/query\/freight\/","title":"Superbuy Shipping Calculator","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"read_full_page","claims_supported":["C01","C07","C10"]},{"source_id":"S03","url":"https:\/\/www.superbuy.com\/en\/page\/businessservice\/?tab=channel","title":"Superbuy B2B Business Services","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"snippet_only","claims_supported":["C02","C10"]},{"source_id":"S04","url":"https:\/\/www.buckydrop.com\/en\/services\/pricing\/","title":"BuckyDrop Pricing","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"read_full_page","claims_supported":["C03","C10"]},{"source_id":"S05","url":"https:\/\/solution-api.buckydrop.com\/","title":"BuckyDrop Solution API","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"snippet_only","claims_supported":["C02","C03"]},{"source_id":"S06","url":"https:\/\/www.buckydrop.com\/en\/dropshipping\/","title":"BuckyDrop Dropshipping","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"read_full_page","claims_supported":["C02","C03"]},{"source_id":"S07","url":"https:\/\/blog.sugargoo.com\/sugargoo-superbuy-mulebuy-kakobuy-shipping-calculator\/","title":"Sugargoo Shipping Calculator Guide","published_at":"2026-01-23","retrieved_at":null,"source_type":"official","access_state":"blocked","claims_supported":["C04","C07"]},{"source_id":"S08","url":"https:\/\/blog.sugargoo.com\/sugargoo-business-solutions-enterprise-brands\/","title":"Sugargoo Business Solutions","published_at":"2025-09-17","retrieved_at":null,"source_type":"official","access_state":"blocked","claims_supported":["C04","C10"]},{"source_id":"S09","url":"https:\/\/thefederalregister.org\/documents\/2026-12670\/indefinite-suspension-of-the-de-minimis-exemption-for-merchandise-arriving-through-all-modes-other-than-the-internationa","title":"Indefinite Suspension of De Minimis - Nonpostal","published_at":"2026-06-24","retrieved_at":null,"source_type":"government","access_state":"read_full_page","claims_supported":["C05"]},{"source_id":"S10","url":"https:\/\/thefederalregister.org\/documents\/2026-12669\/indefinite-suspension-of-the-de-minimis-exemption-for-mail-shipments-and-new-postal-informal-entry-process","title":"Indefinite Suspension of De Minimis - Postal","published_at":"2026-06-24","retrieved_at":null,"source_type":"government","access_state":"read_full_page","claims_supported":["C05","C06"]},{"source_id":"S11","url":"https:\/\/thefederalregister.org\/documents\/2026-15530\/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027","title":"Customs User Fees FY2027","published_at":"2026-07-31","retrieved_at":null,"source_type":"government","access_state":"read_full_page","claims_supported":["C06"]},{"source_id":"S12","url":"https:\/\/www.help.cbp.gov\/s\/article\/Article-1114?language=en_US","title":"CBP: State Sales Tax on Imports","published_at":"2026-06-13","retrieved_at":null,"source_type":"government","access_state":"read_full_page","claims_supported":["C09"]},{"source_id":"S13","url":"https:\/\/www.reddit.com\/r\/Superbuy\/comments\/1tkco3b\/is_the_shipping_expert_worth_it_in_this_case\/","title":"r/Superbuy volumetric-weight case","published_at":"2026-05-22","retrieved_at":null,"source_type":"community","access_state":"read_full_page","claims_supported":["C08"]},{"source_id":"S14","url":"https:\/\/www.reddit.com\/r\/Sugargoo\/comments\/1uvh6ea\/to_my_usa_users_and_buyers_shipping_info\/","title":"r/Sugargoo USA customs/shipping discussion","published_at":"2026-07-13","retrieved_at":null,"source_type":"community","access_state":"read_full_page","claims_supported":["C08"]},{"source_id":"S15","url":"https:\/\/www.superbuy.com\/en\/page\/shoppingagent\/","title":"Superbuy public parcel feed","published_at":null,"retrieved_at":null,"source_type":"official","access_state":"read_full_page","claims_supported":["C07"]}],"claims":[{"claim_id":"C01","claim":"Superbuy标准平台代购公开采购服务费为0；国际运费仍受线路、实重/体积重、目的地和货物类型影响，最终账单会结算差额。","classification":"FACT","source_ids":["S01","S02"],"confidence":"high","counterevidence":"线路规则不同，不能把/6000或任何一条线路费率推广到全部线路。"},{"claim_id":"C02","claim":"成熟代理基础设施能够支持逐单直寄消费者而非必须由研究方先物理聚合：BuckyDrop有自动履约/API；Superbuy商务页搜索提取显示可拆单寄不同用户。","classification":"FACT","source_ids":["S03","S05","S06"],"confidence":"medium","counterevidence":"Superbuy商务页正文在本会话未完整渲染；能力存在不等于单位成本最优。"},{"claim_id":"C03","claim":"BuckyDrop公开标准价包括Pro CNY199/月/店和CNY9.90/包裹履约费；公开页面同时称运费按承运商最终重量/体积结算并加固定CNY9.9服务费，二者是否同一费用需避免双计。","classification":"FACT","source_ids":["S04"],"confidence":"high","counterevidence":"私有商务合同可能不同，页面两处9.9的关系需要书面澄清。"},{"claim_id":"C04","claim":"Sugargoo公开搜索可发现计算器和企业服务，但本会话直接打开相关页面返回403，故具体费率/API/商务折扣均为UNVERIFIED。","classification":"FACT","source_ids":["S07","S08"],"confidence":"high","counterevidence":"登录态或不同网络环境可能可访问完整页面。"},{"claim_id":"C05","claim":"截至2026-10-06，美国≤800美元de minimis行政豁免对非邮政与邮政均已暂停；旧的<$800自动免税假设不能用于当前landed cost。","classification":"FACT","source_ids":["S09","S10"],"confidence":"high","counterevidence":"具体SKU税率仍由HTSUS及适用贸易措施决定，暂停不等于统一税率。"},{"claim_id":"C06","claim":"FY2027自2026-10-01起的CBP费率包括正式MPF 0.3464%（$34.58–$670.86）、非正式自动$2.77、非正式手工$8.30/$12.45、快件中心每运单$1.38；并非每票全部叠加。","classification":"FACT","source_ids":["S10","S11"],"confidence":"high","counterevidence":"邮政、快件、空运、海运和特定豁免对应不同费用组合。"},{"claim_id":"C07","claim":"54个冻结SKU中实际ZIP10001 quote-grade国际运费=0个；冻结数据缺代理重打包后的精确重量/尺寸，且未获得当前线路的全部必收费项。","classification":"FACT","source_ids":["S02","S07","S15"],"confidence":"high","counterevidence":"可另行人工补采包装数据和登录态报价，但本次没有。"},{"claim_id":"C08","claim":"社区案例证明体积重惊喜和海关延迟/检查是现实风险，但不能估计总体发生率。","classification":"FACT","source_ids":["S13","S14"],"confidence":"medium","counterevidence":"社区存在严重选择偏差，线路和申报条件也不同。"},{"claim_id":"C09","claim":"比较终点采用送达ZIP10001、美国州/地方sales/use tax之前；州税单列且不假定为0。","classification":"FACT","source_ids":["S12"],"confidence":"high","counterevidence":"最终消费者仍可能有纽约州/地方税义务。"},{"claim_id":"C10","claim":"公开资料没有给出1000个独立订单触发的物流阶梯折扣；Superbuy的≥30kg是单票/批货定制入口，BuckyDrop Pro的unlimited fulfillment也不是运价折扣。","classification":"INFERENCE","source_ids":["S02","S03","S04","S08"],"confidence":"medium","counterevidence":"未公开的商务合同可能存在按月票量/重量阶梯价。"},{"claim_id":"C11","claim":"Superbuy公开可见的收费/收入杠杆包括非标准代购费、增值服务和国际运输中的操作费；其承运商采购价差或收入占比没有公开审计数据。","classification":"FACT","source_ids":["S01"],"confidence":"medium","counterevidence":"公开费率结构不能证明公司实际利润构成。"}],"categories":[{"category_id":"C01","category":"Smartphones","n":3,"quote_n":0,"feasibility":"medium","basis":"lithium_battery; compact; HTS/route required"},{"category_id":"C02","category":"Laptops","n":3,"quote_n":0,"feasibility":"medium_low","basis":"lithium_battery; higher weight/value"},{"category_id":"C03","category":"Tablets","n":3,"quote_n":0,"feasibility":"medium","basis":"lithium_battery; compact"},{"category_id":"C04","category":"Mini PCs / small desktops","n":3,"quote_n":0,"feasibility":"medium_high","basis":"no built-in battery in frozen sample; moderate size"},{"category_id":"C05","category":"PC components / storage / networking","n":3,"quote_n":0,"feasibility":"high","basis":"mostly compact; some mains adapter/firmware; low volumetric risk"},{"category_id":"C06","category":"Headphones / IEM / audio","n":3,"quote_n":0,"feasibility":"medium_high","basis":"small but lithium batteries restrict routes"},{"category_id":"C07","category":"PC peripherals","n":3,"quote_n":0,"feasibility":"high","basis":"mostly compact; one wired, one AA, one rechargeable"},{"category_id":"C08","category":"Wearables","n":3,"quote_n":0,"feasibility":"medium_high","basis":"small but lithium batteries"},{"category_id":"C09","category":"Smart home / security / IoT","n":3,"quote_n":0,"feasibility":"medium","basis":"mains/power details and installation; moderate size"},{"category_id":"C10","category":"Robot vacuums / small appliances","n":3,"quote_n":0,"feasibility":"low","basis":"bulky volumetric + lithium + mains base"},{"category_id":"C11","category":"Power tools / electronics tools","n":3,"quote_n":0,"feasibility":"low_medium","basis":"mains/charger or lithium; heavier tools"},{"category_id":"C12","category":"Camera / video gear","n":3,"quote_n":0,"feasibility":"medium","basis":"high value + lithium; fragile"},{"category_id":"C13","category":"Automotive accessories","n":3,"quote_n":0,"feasibility":"medium","basis":"vehicle-installation; some power-source uncertainty"},{"category_id":"C14","category":"Sports / outdoor","n":3,"quote_n":0,"feasibility":"medium_low","basis":"tents/racket are bulky/long/fragile"},{"category_id":"C15","category":"Hobby / 3D printing / maker","n":3,"quote_n":0,"feasibility":"low_medium","basis":"bulky mains equipment; dimensional weight"},{"category_id":"C16","category":"Apparel / shoes / bags","n":3,"quote_n":0,"feasibility":"medium","basis":"shoe/bag volume; brand route sensitivity"},{"category_id":"C17","category":"Home / organization","n":3,"quote_n":0,"feasibility":"low","basis":"very high volumetric-weight risk"},{"category_id":"C18","category":"Toys / collectibles","n":3,"quote_n":0,"feasibility":"medium_high","basis":"no battery; package/collector box sensitivity"}],"sku_candidates":[{"sku_id":"C01-S01","category_id":"C01","variant":"iPhone 17 256GB 白色，中国大陆京东自营双卡双待5G版本","cn_price_cny":6799,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C01-S02","category_id":"C01","variant":"iPhone 17 Pro 256GB 银色，中国大陆京东自营双卡双待版本","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C01-S03","category_id":"C01","variant":"OnePlus Ace 6T 12GB+256GB 闪速黑","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C02-S01","category_id":"C02","variant":"ASUS 天选7 Pro 酷睿版 16英寸/Core Ultra 7 251HX/16GB/1TB/RTX5060/2.5K 300Hz/青","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C02-S02","category_id":"C02","variant":"Lenovo 小新16SE高能本 标压锐龙R7/16GB/512GB/可扩展硬盘位","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C02-S03","category_id":"C02","variant":"MECHREVO 无界14 2026 Core Ultra 5 226V/16GB/1TB/2.8K/灰","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C03-S01","category_id":"C03","variant":"Apple iPad 11英寸(A16,2025) 128GB WLAN 银色","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C03-S02","category_id":"C03","variant":"Apple iPad 11英寸(A16,2025) 256GB WLAN 银色","cn_price_cny":4299,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C03-S03","category_id":"C03","variant":"Lenovo 拯救者Y700五代 8.8英寸/12GB+256GB/Wi-Fi/碳晶黑","cn_price_cny":4299,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C04-S01","category_id":"C04","variant":"ASUS 破晓迷你主机 Core i5-13500H/16GB/512GB SSD/Wi-Fi 6","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C04-S02","category_id":"C04","variant":"GMK EVO-X2 Ryzen AI Max+ 395/128GB/2TB","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C04-S03","category_id":"C04","variant":"Beelink SER8 8745HS 深空灰/准系统(无内存、硬盘、系统)","cn_price_cny":2049,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C05-S01","category_id":"C05","variant":"Samsung 990 EVO Plus 2TB/PCIe4.0x4或5.0x2/读取7250MB/s","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C05-S02","category_id":"C05","variant":"Xiaomi BE6500 Wi-Fi7/6500兆级/全2.5G网口/高通4核","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C05-S03","category_id":"C05","variant":"KINGBANK 银爵 32GB(16GBx2)/DDR5-6000/国产颗粒/C36","cn_price_cny":3499,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C06-S01","category_id":"C06","variant":"EDIFIER Lolli Pro SE 云岩白/真无线主动降噪","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C06-S02","category_id":"C06","variant":"EDIFIER LolliClip SE 云霜金/耳夹式开放耳","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C06-S03","category_id":"C06","variant":"EDIFIER Comfo Clip Q 奶霜白/耳夹式","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C07-S01","category_id":"C07","variant":"Logitech G G304 黑色(非G304X)","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C07-S02","category_id":"C07","variant":"Logitech G GPW5雪豹无线电竞游戏鼠标","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C07-S03","category_id":"C07","variant":"ATK RS6+ 白武士/雪刃轴Pro/68键/有线磁轴","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C08-S01","category_id":"C08","variant":"Huawei 手环11 NFC版 悦动白/铝合金表壳/1.62英寸","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C08-S02","category_id":"C08","variant":"Huawei 手环11 Pro NFC 羽砂黑/铝合金表壳","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C08-S03","category_id":"C08","variant":"Xiaomi Watch S5 41mm 海盐蓝/澎湃OS4","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C09-S01","category_id":"C09","variant":"Xiaomi 智能摄像机4 室内云台/800万像素/4K","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C09-S02","category_id":"C09","variant":"Xiaomi 智能门锁4 Pro双摄版 双摄/人脸/掌静脉/猫眼大屏","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B5"},{"sku_id":"C09-S03","category_id":"C09","variant":"Aqara 妙控开关S1E 皎月白/CJPKG01LM","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B4"},{"sku_id":"C10-S01","category_id":"C10","variant":"Roborock P20 Max A2950RR 非自动上下水版","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C10-S02","category_id":"C10","variant":"Roborock P20 Max/A2950RR 自动上下水版/自动集尘/热水洗拖布","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C10-S03","category_id":"C10","variant":"DJI ROMO P 水箱版/透明机器人+透明基站","cn_price_cny":3699,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C11-S01","category_id":"C11","variant":"东成 DZC1050-26BT 1050W电锤电镐两用/安全离合","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B4"},{"sku_id":"C11-S02","category_id":"C11","variant":"东成 WJZ1601S 16V双电套装","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B4"},{"sku_id":"C11-S03","category_id":"C11","variant":"Worx WU130X.1 12V/40Nm/2.0Ah单电","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B4"},{"sku_id":"C12-S01","category_id":"C12","variant":"Sony Alpha 7C II/A7C2/A7CM2 银色/FE 28-60mm套装","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C12-S02","category_id":"C12","variant":"Sony ILCE-7M5/Alpha 7 V A7M5单机身/官方标配","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C12-S03","category_id":"C12","variant":"Insta360 GO 3S 灵动白64G/标准版","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B1"},{"sku_id":"C13-S01","category_id":"C13","variant":"70mai M800Pro 2026新款/前后双录/4K/4G停车监控/无卡","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C13-S02","category_id":"C13","variant":"DDPAI MINIPro 4K 2026新款/4K/360度旋转/停车监控/无卡","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B2"},{"sku_id":"C13-S03","category_id":"C13","variant":"70迈 青春版2 汽车轮胎充气泵/2026新款","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B5"},{"sku_id":"C14-S01","category_id":"C14","variant":"MOBI GARDEN NXZQU61017 冷山2PLUS 红灰色/双人/带雪裙","cn_price_cny":799,"cn_coupon_cny":539.13,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C14-S02","category_id":"C14","variant":"李宁 战戟5000 4U空拍","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B7"},{"sku_id":"C14-S03","category_id":"C14","variant":"Naturehike 云尚PRO 浅灰红/2人/20D尼龙(聚合变体映射未锁)","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B8"},{"sku_id":"C15-S01","category_id":"C15","variant":"Bambu Lab P2SC/P2S Combo P2S多色套装(标题未标大陆版)","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C15-S02","category_id":"C15","variant":"Bambu Lab A1 单机/大陆版","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C15-S03","category_id":"C15","variant":"Creality Space Pi V2 Plus 大陆版","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C16-S01","category_id":"C16","variant":"COACH CV976 CITY33大号托特包/奶茶色","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B6"},{"sku_id":"C16-S02","category_id":"C16","variant":"NIKE CW2288-111 Air Force 1 白色/42码","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B6"},{"sku_id":"C16-S03","category_id":"C16","variant":"adidas JI0079 Superstar II/37码","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B6"},{"sku_id":"C17-S01","category_id":"C17","variant":"CHAHUA 斜口前开/侧开收纳箱 奶黄色34L×3/45.5×38×31cm","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C17-S02","category_id":"C17","variant":"CHAHUA 抽屉式单层收纳箱30.5L/两只装","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C17-S03","category_id":"C17","variant":"JEKO&JEKO 抽屉式收纳柜/五斗柜/5层","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B3"},{"sku_id":"C18-S01","category_id":"C18","variant":"LEGO 10698 经典创意积木盒/赠礼袋","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B7"},{"sku_id":"C18-S02","category_id":"C18","variant":"POP MART CRYBABY Vacation Mode On 搪胶毛绒挂件盲盒/随机1个","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B7"},{"sku_id":"C18-S03","category_id":"C18","variant":"BANDAI RG 1/144 RX-78-2 元祖 RGU ver2.0","cn_price_cny":null,"cn_coupon_cny":null,"observed":"2026-10-06","screened":true,"quote":null,"weight_g":null,"dims_cm":null,"hts10":null,"tariff":null,"single":null,"consolidated_marginal":null,"commercial_1000_separate":null,"bulk_import":null,"blocker":"B7"}],"data_gaps":[{"code":"B1","gap":"锂电/电池类：代理重打包重量和L×W×H缺失；当前可走电池线路、必收费项及HTS10未核。"},{"code":"B2","gap":"紧凑非电池/外接电源类：重打包重量尺寸缺失；当前线路和HTS10/关税未核。"},{"code":"B3","gap":"大件/体积重高风险：重打包尺寸/计费体积重缺失；当前线路、HTS10及必收费项未核。"},{"code":"B4","gap":"工具/市电类：重量尺寸、充电器/插头或电池包线路及HTS10未核。"},{"code":"B5","gap":"冻结样本中的电源/套装细节仍未闭合，同时缺重量尺寸、线路和HTS10。"},{"code":"B6","gap":"品牌包鞋：包装体积/鞋盒处理、品牌敏感线路和HTS10未核。"},{"code":"B7","gap":"一般/易损/收藏品：包装重量尺寸、保护包装后的体积和HTS10未核。"},{"code":"B8","gap":"冻结变体本身仍为PROVISIONAL，同时缺包装重量尺寸、线路和HTS10；保留在分母。"},{"code":"G1","gap":"1000个分别履约订单的书面B2B阶梯运价：AUTHENTICATED/NEGOTIATED DATA REQUIRED。"},{"code":"G2","gap":"每条美国线路在2026 de minimis暂停后的entry type、broker/clearance传导费用及税费代收机制。"},{"code":"G3","gap":"Superbuy面向第三方平台的生产API文档未核；BuckyDrop API能力有公开证据。"},{"code":"G4","gap":"Sugargoo关键费率/企业服务页本会话直开403；只能保留为UNVERIFIED。"},{"code":"G5","gap":"退件、清关滞留、保险赔付、重新寄送率缺乏可审计线路级数据。"},{"code":"G6","gap":"美国sales/use tax按实际merchant-of-record交易另算；本物流终点不假定为0。"}],"pre_freeze_compliance":true}
```