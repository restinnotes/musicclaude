# W5-A — Logistics / Superbuy Infrastructure 独立研究报告

**研究范围仅限 W5。** 未执行 W1/W2/W3/W4/W6/W7/W8，也未修改冻结样本。冻结样本 SHA256：`4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185`。本轮没有进行海外 SKU 价格检查，因此不存在 pre-freeze overseas leakage；A/B/C exact-match 统计不属于本 workstream，均保持未计算。

**网页研究可用。** 最后核验阶段的实际 UTC 时钟记录为 **2026-10-07T01:00:36Z–2026-10-07T01:03:52Z**，对应美国当地仍为 2026-10-06。网页工具不返回每一个 URL 的精确请求时间，因此 JSON 中逐来源 `retrieved_at` 保守填 `null`，不伪造秒级时间。当前无日期的 Superbuy/BuckyDrop 价目页为本次实时访问页面；本次使用的最新有日期运营证据包括 BuckyDrop 2026-09-20、社区 2026-10-05；政府关税资料截至 USTR 2026-07-23。

---

## 1. Direct answer / Bottom line

1. **FACT — Superbuy 可以充当“采购+中国仓+逐件跨境直发”基础设施，但目前公开资料不足以证明它能提供可量化的 1,000 单商务物流折扣。** Superbuy 公开 B2B 页面写明可做 dropship、批量打包，并支持把订单拆开后“ship parcels to different users separately”。这意味着**商业订单量聚合不要求先把 1,000 个消费者订单物理合成一个包裹**。但商务页仅宣传“exclusive discounts”，没有公开阶梯、最低量或 ZIP10001 费率，因此“1,000 单→X%优惠”必须标为 **NEGOTIATED DATA REQUIRED**。 [Superbuy](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)  
   [https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

2. **FACT — 普通 Taobao/Tmall/JD/1688 采购服务费当前公开为 0，但这不等于 Superbuy 整条链路无利润。** 其价目页明确列出国际运费、首重/续重、清关、燃油、仓库操作以及大量增值服务费；但 Superbuy 没有公开其物流采购成本、承运商返点或毛利率。因此“Superbuy 到底靠什么赚钱”的可审计答案只能是：**公开收费项目集中在物流/履约/增值服务；具体利润构成和承运商 spread 未披露。** [Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)  
   [https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/)

3. **FACT — 同一消费者的多商品 consolidation 确实可能改善经济性。** Superbuy 免费合包，公开计价又存在首重+续重；因此避免重复首重具有真实机制基础。但合包不是总能省：一旦尺寸增大导致体积重，或某一个电池/液体商品迫使整包使用特殊线路，节省可以反转。 [Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

4. **FACT — 体积重是本样本里最容易被低估的物流变量。** Superbuy 当前页面称多数空运使用 `L×W×H/6000`；Sugargoo 则明确说明不同承运商可能用 `/5000 /6000 /7000`。2026 社区实例中出现 2.590kg 实重对应 3.675kg 计费重，以及约 8kg 实重对应 19kg 体积重。社区数字不是正式报价，但很好地反驳“按商品净重估运费”的方法。 [Superbuy](https://login.superbuy.com/en/page/query/freight/)  
   [https://login.superbuy.com/en/page/query/freight/](https://login.superbuy.com/en/page/query/freight/)  
   [https://blog.sugargoo.com/save-money-international-shipping-sugargoo/](https://blog.sugargoo.com/save-money-international-shipping-sugargoo/?utm_source=chatgpt.com)

5. **FACT — 电池并非“一律不能寄”，而是线路约束。** Superbuy 公开计算器把 Built-in Battery、Power Bank、单电池分别作为商品类别，这意味着手机、笔记本、耳机、手表、电动工具等理论上存在适配线路；代价是可选线路减少、特殊计费或拆包风险。 [Superbuy](https://login.superbuy.com/en/page/query/freight/)

6. **FACT — 2026 年不能再使用旧的美国 `$800 de minimis = 免税` 模型。** 2026-02-20 EO 14388 明确继续暂停 19 U.S.C. 1321(a)(2)(C) 低值免税，非邮政包裹须承担所有适用 duties/taxes/fees。 [The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/)  
   [https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/)

7. **FACT — 也不能给全部中国商品统一套一个 2026 税率。** USTR 2026-07 行动对“其他被调查经济体”设 12.5% Section 301 附加税，中国属于调查对象；但存在产品豁免，同时历史 China Section 301 是否叠加必须用 8 位 HTS 查询。因此本轮 54 个 SKU 的 tariff rate 全部保持 `null`。 [United States Trade Representative](https://ustr.gov/about/policy-offices/press-office/press-releases/2026/june/ustr-makes-findings-and-proposes-action-60-section-301-investigations-relating-failures-take-action?trk=public_post_comment-text\&utm_source=chatgpt.com)  
   [https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search](https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search?utm_source=chatgpt.com)

8. **FACT — BuckyDrop 的公开集成能力比 Superbuy 核心产品更明确。** BuckyDrop 明确提供 API Integration、Shopify/WooCommerce 自动同步、自动采购/打包/物流追踪；当前公开价目为 Pro `CN¥199/月/店`、履约 `CN¥9.90/parcel`，并自称国际运费 “zero-markup” 按 carrier final weight/volume 结算。后一个“zero-markup”是公司自述，不是审计后的成本证明。 [BuckyDrop](https://www.buckydrop.com/en/services/pricing/)  
   [https://www.buckydrop.com/en/services/pricing/](https://www.buckydrop.com/en/services/pricing/)  
   [https://www.buckydrop.com/en/dropshipping/](https://www.buckydrop.com/en/dropshipping/)

9. **INFERENCE — 因而薄型 routing/agent 架构并不天然要求平台自己做 physical aggregation/import。** 采购、仓内 QC、逐消费者拆单和直发都有现成服务证据。**但是否仅靠“商业 volume aggregation”就能获得足以改变 unit economics 的运价，尚未证明。**

10. **最重要的负面结论：冻结的 54/54 个 SKU 本轮都无法得到合格的 ZIP10001 当前实际运价。** 不是因为商品“不可寄”，而是冻结数据没有完整**最终包装重量+长宽高+具体线路+申报/税费条款**，且当前公共计算器不能在本研究工具中完成交互提交。因此我没有制造任何 per-SKU 运费、landed cost 或 savings。

### 四种结构必须分开

| 结构 | 本轮可证实的内容 | 当前数字状态 |
|---|---|---|
| 1. 单件 standalone DTC | 每单独立首重/续重；按实际或体积计费；电池影响线路 | **当前 ZIP10001 rate = null** |
| 2. 同一消费者 consolidated-haul marginal | Superbuy 可免费合包，理论上省重复首重；体积重/敏感品可能反向抵消 | **marginal rate = null** |
| 3. 1,000 个商业订单、仍分别寄 1,000 位消费者 | Superbuy B2B 明示可拆单分别寄用户；BuckyDrop 有 API/自动履约 | **商务 rate/折扣阈值 = null；NEGOTIATED DATA REQUIRED** |
| 4. 真正 bulk import | Superbuy ≥30kg/超大货走 customized logistics；海运还涉及美国进口节点、MPF/HMF、美国仓/末端派送 | **bulk rate = null；与 DTC 不可混用** |

**统一比较终点：**结构 1–3 应比较到 **ZIP10001 消费者门口 delivered cost**；结构 4 若只算到美国港/仓不合格，必须再加美国仓储、拆包履约和 last-mile。

**美国 sales/use tax：**W5 运费/landed 模型中**暂时对所有比较端都排除美国州/地方销售税**，避免把 marketplace collection 与进口费用混为一谈；CBP 本身不代州政府征收销售税。最终消费者 checkout 比较时必须对各渠道一致处理。 [CBP Help Center](https://www.help.cbp.gov/s/article/Article-1225?language=en_US\&utm_source=chatgpt.com)

---

## 2. Evidence table + frozen-SKU logistics audit

### 核心 evidence table

| Claim | Evidence / date | Counterevidence / limitation | Confidence |
|---|---|---|---|
| Superbuy 主流平台采购费 0 | 当前官方 fee page；URL：[https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/) | 0 采购费≠0 物流利润；毛利未公开 | High |
| Superbuy 支持同客合包 | 同页写 multiple items 可免费 consolidate | 大包可能触发体积重/线路限制 | High |
| Superbuy 能拆订单分别寄不同用户 | 当前 B2B 索引页；URL：[https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?tab=channel&utm_source=chatgpt.com) | 动态页正文提取失败；具体 SLA/API/价格未公开 | Medium-high |
| “1,000 单即可获商务价” | **无公开证据** | B2B 页面只说 exclusive discounts；无量级表 | High confidence that rate is unknown |
| Superbuy 多数空运体积重 /6000 | 当前 calculator；URL：[https://login.superbuy.com/en/page/query/freight/](https://login.superbuy.com/en/page/query/freight/) | 每条 carrier route 可不同 | High |
| 电池存在专门线路分类 | 同 calculator 有 Built-in Battery / Power Bank / Battery | 不表示每类/每目的地均可寄 | High |
| BuckyDrop ¥9.90/parcel | 当前官方 pricing；URL：[https://www.buckydrop.com/en/services/pricing/](https://www.buckydrop.com/en/services/pricing/) | “zero markup” 为公司自述 | High for published price |
| BuckyDrop API/自动履约 | 当前官方 dropshipping 页；URL：[https://www.buckydrop.com/en/dropshipping/](https://www.buckydrop.com/en/dropshipping/) | 未测试 API 稳定性/字段范围 | High for availability |
| Sugargoo 曾公开 US 3kg California 路线 $55.18–$88.71 | 2025-09-12 文章；URL：[https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/](https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/?utm_source=chatgpt.com) | **不是 2026-10-06、不是 ZIP10001、不是本样本 SKU，禁止作为当前报价** | High historical only |
| 美国 de minimis 已暂停 | EO 14388, 2026-02-20 | 无 | High |
| 中国货总税率不能统一 | USTR 2026-07 + 8-digit HTS search | 产品豁免、MFN、旧 S301/232 均可改变结果 | High |

### 54 个冻结 SKU：能评估什么、不能评估什么

**汇总：54/54 可做 W5 路由风险分类；0/54 可给合格的当前 ZIP10001 实际运费或 landed cost。** 共通缺失字段为：最终包装实重、最终 L/W/H、申报值/HTS、具体承运线路、报价时点及 duty/clearance 是否 prepaid。下面没有删除任何 SKU。

| Category | Frozen sku_id | W5 状态与精确原因 |
|---|---|---|
| C01 | C01-S01, C01-S02, C01-S03 | `CLASSIFIED_NO_QUOTE`；3 款均含锂电，可归 Built-in Battery；缺 packed weight/dimensions + live line quote + HTS |
| C02 | C02-S01, C02-S02, C02-S03 | `CLASSIFIED_NO_QUOTE`；笔记本锂电，中等重量且尺寸敏感；缺最终箱规/计费重/线路/HTS |
| C03 | C03-S01, C03-S02, C03-S03 | `CLASSIFIED_NO_QUOTE`；平板内置锂电；缺最终包装及路线报价 |
| C04 | C04-S01, C04-S02, C04-S03 | `CLASSIFIED_NO_QUOTE`；Digital/Electrical + 电源适配器；电池状态不做额外推断；缺包装数据/HTS |
| C05 | C05-S01, C05-S02, C05-S03 | `CLASSIFIED_NO_QUOTE`；SSD/路由/RAM 属轻小电子，体积风险较低，但缺包装重尺寸、线路、HTS |
| C06 | C06-S01, C06-S02, C06-S03 | `CLASSIFIED_NO_QUOTE`；耳机均有电池线路约束；缺 packed data/route |
| C07 | C07-S01 | `CLASSIFIED_NO_QUOTE`；AA 电池鼠标，电池处理取决于是否随货 |
|  | C07-S02 | `LIMITED_NO_QUOTE`；冻结数据自身仍要求核 battery/charging dependency |
|  | C07-S03 | `CLASSIFIED_NO_QUOTE`；有线键盘、无电池；缺箱规和运价 |
| C08 | C08-S01, C08-S02, C08-S03 | `CLASSIFIED_NO_QUOTE`；可穿戴内置电池；缺 packed data + route |
| C09 | C09-S01 | `CLASSIFIED_NO_QUOTE`；网络摄像机/电子设备；缺箱规 |
|  | C09-S02 | `LIMITED_NO_QUOTE`；智能锁供电细节冻结样本未核 |
|  | C09-S03 | `CLASSIFIED_NO_QUOTE`；220V 智能开关，物流可按电子品，但兼容性不是 W5 运价 |
| C10 | C10-S01, C10-S02, C10-S03 | `CLASSIFIED_NO_QUOTE`；扫地机器人锂电+大型基站，**高体积重风险**；上下水版本还增大箱规/安装复杂度 |
| C11 | C11-S01 | `CLASSIFIED_NO_QUOTE`；有线 1050W 工具，无冻结锂电标记，偏重；缺箱规 |
|  | C11-S02, C11-S03 | `CLASSIFIED_NO_QUOTE`；工具电池+充电器，特殊线路且重量较高 |
| C12 | C12-S01, C12-S02, C12-S03 | `CLASSIFIED_NO_QUOTE`；相机/运动相机锂电、价值较高、易碎；缺最终包装和 HTS |
| C13 | C13-S01, C13-S02 | `CLASSIFIED_NO_QUOTE`；车载供电电子，套餐/附件改变重量 |
|  | C13-S03 | `LIMITED_NO_QUOTE`；冻结样本中 power source 尚未锁定 |
| C14 | C14-S01 | `CLASSIFIED_NO_QUOTE`；帐篷压缩后体积关键；缺 packed dimensions |
|  | C14-S02 | `CLASSIFIED_NO_QUOTE`；羽毛球拍轻但长边可能触发超长/体积规则 |
|  | C14-S03 | `LIMITED_NO_QUOTE`；冻结样本本身为 `PROVISIONAL_VARIANT_MAPPING`，且 packed weight 未核 |
| C15 | C15-S01, C15-S02 | `CLASSIFIED_NO_QUOTE`；3D 打印机属**大型/较重电器**，可能进入大货/customized service；无箱规 |
|  | C15-S03 | `LIMITED_NO_QUOTE`；商品链接未解析、箱规/电源数据未核 |
| C16 | C16-S01 | `CLASSIFIED_NO_QUOTE`；包类主要是体积重 |
|  | C16-S02, C16-S03 | `CLASSIFIED_NO_QUOTE`；鞋类鞋盒显著影响体积重；Superbuy 有折鞋盒服务但不能假定消费者接受 |
| C17 | C17-S01, C17-S02, C17-S03 | `CLASSIFIED_NO_QUOTE`；**全样本最明显的体积重反例之一**，收纳箱/柜轻而巨大；没有 packed L/W/H 就无法经济估值 |
| C18 | C18-S01 | `CLASSIFIED_NO_QUOTE`；LEGO 一般货但盒体/保护包装影响体积 |
|  | C18-S02 | `CLASSIFIED_NO_QUOTE`；盲盒一般货，随机内容不改变 W5 分类 |
|  | C18-S03 | `CLASSIFIED_NO_QUOTE`；模型件一般货但 collector box condition 导致加固包装/体积风险 |

**没有任何一条被标成“proven unavailable”。** 本轮只有“可分类但报价缺失”和“规格尚不足以完整分类”两种状态，不能把 `not quoted` 写成 `unshippable`。

---

## 3. Primary sources

**Superbuy 当前官方费用结构**：普通 Taobao/Tmall/JD/1688 purchasing service 免费；90 天免费仓储；国际费按最终重量、线路和目的地计算；提供拆单、去包装、真空包装、加固等服务。  
[https://www.superbuy.com/en/page/guide/feecomposition/](https://www.superbuy.com/en/page/guide/feecomposition/) [Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

**Superbuy 当前 Shipping Calculator**：要求目的地、重量、L/W/H、商品类别；列出 built-in battery 等敏感分类；多数空运体积重 `/6000`；≥30kg/超大件导向 customized service。  
[https://login.superbuy.com/en/page/query/freight/](https://login.superbuy.com/en/page/query/freight/) [Superbuy](https://login.superbuy.com/en/page/query/freight/)

**Superbuy Business Service**：公开描述 dropship、Shopify 自动履约、batch shipping、拆单分别寄用户和 customized logistics。动态页正文未由 open 完整提取，因此对应能力证据标为“官方页面索引可读，但 full-page rendering 未验证”；任何商务折扣数字仍需商务报价。  
[https://www.superbuy.com/en/page/businessservice/](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com) [Superbuy](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

**BuckyDrop 当前官方 pricing/API**：CN¥9.90/parcel；Pro CN¥199/月/店；公开 API/Shopify/WooCommerce 自动履约。  
[https://www.buckydrop.com/en/services/pricing/](https://www.buckydrop.com/en/services/pricing/)  
[https://www.buckydrop.com/en/dropshipping/](https://www.buckydrop.com/en/dropshipping/) [BuckyDrop](https://www.buckydrop.com/en/services/pricing/)

**BuckyDrop 2026-09-08 shipping guide** 很明确地警告不存在 universal shipping price，正式核价需要真实 postcode、packed dimensions、actual/volumetric weight、category、route 和所有 fee layers。这与本项目的 landed-cost protocol 高度一致。  
[https://blog.buckydrop.com/dropshipping-shipping-costs-from-china/](https://blog.buckydrop.com/dropshipping-shipping-costs-from-china/?utm_source=chatgpt.com) [BuckyDrop](https://blog.buckydrop.com/dropshipping-shipping-costs-from-china/?utm_source=chatgpt.com)

**美国政府**：EO 14388、CBP 费率、USTR Section 301。  
[https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/)  
[https://www.help.cbp.gov/s/article/Article-1128?language=en_US](https://www.help.cbp.gov/s/article/Article-1128?language=en_US&utm_source=chatgpt.com)  
[https://www.help.cbp.gov/s/article/Article-1225?language=en_US](https://www.help.cbp.gov/s/article/Article-1225?language=en_US&utm_source=chatgpt.com)  
[https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-takes-action-forced-labor-section-301-investigations](https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-takes-action-forced-labor-section-301-investigations)

CBP FY2026 MPF：formal entry 为 0.3464%，最低 $33.58、最高 $651.50；informal entry 为 $2.69/$8.06/$12.09 三档。海运 commercial cargo 另有 0.125% HMF；空运不收 HMF。实际某个消费者包裹走哪种 entry type 仍不能提前假定。 [CBP Help Center](https://www.help.cbp.gov/s/article/Article-1128?language=en_US\&utm_source=chatgpt.com)

---

## 4. Forum / community evidence

社区证据只用于验证实际摩擦，不作为正式费率：

- **2026-10-05**：Superbuy 用户/版主讨论称，商品入仓后才能更准确确认尺寸和重量；Shipping Expert 是更接近最终 carrier charge 的 rehearsal，而非固定报价。 [Reddit](https://www.reddit.com/r/Superbuy/comments/1wxmp0z/shipping_fee_question/?utm_source=chatgpt.com)  
  [https://www.reddit.com/r/Superbuy/comments/1wxmp0z/shipping_fee_question/](https://www.reddit.com/r/Superbuy/comments/1wxmp0z/shipping_fee_question/?utm_source=chatgpt.com)

- **2026-08-23**：用户报告实重 2,590g、应用显示 3,675g；解释是尺寸触发体积重，且液体导致特殊空运线路。另一评论建议把液体拆出，避免整包都走特殊线路。 [Reddit](https://www.reddit.com/r/Superbuy/comments/1vvs196/question_about_shipping/?utm_source=chatgpt.com)  
  [https://www.reddit.com/r/Superbuy/comments/1vvs196/question_about_shipping/](https://www.reddit.com/r/Superbuy/comments/1vvs196/question_about_shipping/?utm_source=chatgpt.com)

- **2026-08-19**：另一用户称约 8kg 实重出现 19kg 体积重；社区建议去原包装、真空压缩。 [Reddit](https://www.reddit.com/r/Superbuy/comments/1vt36t4/volumetric_weight_vs_actual_weight/?utm_source=chatgpt.com)  
  [https://www.reddit.com/r/Superbuy/comments/1vt36t4/volumetric_weight_vs_actual_weight/](https://www.reddit.com/r/Superbuy/comments/1vt36t4/volumetric_weight_vs_actual_weight/?utm_source=chatgpt.com)

- 关于美国 “tax-free” 路线，社区中有人报告没另付关税；**这不能证明法律上的免税**，因为当前美国 de minimis 已暂停。更合理的解释可能是 DDP/预付/承运商清关机制，具体 route terms 必须逐线确认。 [Reddit](https://fr.reddit.com/r/Superbuy/comments/1pmt24w/anyone_had_successful_hauls_to_the_us_recently/?utm_source=chatgpt.com)

---

## 5. Contrary evidence

**反证 1：Superbuy 自己的费用示例存在可见算术问题。** 官方页给出的 UPS 示例写 `CN¥428 = 320 + 50 + 38`，但三项相加是 **408**。因此这类页面示例不适合直接进入精确 landed-cost 数据集；必须依赖实际 calculator/最终账单。 [Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

**反证 2：“商业规模一定更便宜”没有被证明。** Superbuy 宣传 exclusive logistics discounts；BuckyDrop 也宣传依靠全局货量获得 agreement pricing，但都没有公开 100、1,000、10,000 单对应的折扣表。营销承诺不能替代报价。 [Superbuy](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

**反证 3：合箱并非单调降低成本。** 体积重、特殊品混装和线路重量上限都可能让合包更贵，甚至迫使拆包。 [Superbuy](https://login.superbuy.com/en/page/query/freight/)

**反证 4：旧的 US duty-free 社区经验已经结构性过时。** 2025/2026 社区仍使用“tax-free line”这个产品名，但法律上低值免税已被暂停，不能把线路名称解释成 Section 321/de minimis 法律豁免。 [The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/)

**反证 5：部分品类可能几乎没有物流套利空间。** C17 收纳箱/柜、C10 大型扫地机基站、C15 打印机都是明显体积/重量风险；即使中国商品裸价低，也可能被国际运输吞掉。没有真实包装数据前，不能判定它们有正 spread。

---

## 6. Confidence

**High confidence：**
- Superbuy 主流采购 0 服务费；
- Superbuy 存在合包、首重/续重、体积重、built-in battery 路由分类；
- BuckyDrop 当前 ¥9.90/parcel、API/自动 fulfillment；
- 美国 de minimis 已停止；
- per-SKU HTS 是税率计算必要条件。

**Medium confidence：**
- Superbuy 能作为较大规模 consumer-routing 后端而无需平台自己建中国仓；公开 SBS 功能充分支持这一推断，但未实际 API/订单压测。
- 商业量聚合可能获得 better rates；存在官方营销语言，但没有可审计的梯度。

**Low confidence / 未证明：**
- “1,000 单/月”这一具体量级是否足以改变 rate；
- Superbuy/BuckyDrop 相对零售公开 rate 的实际 carrier discount；
- Superbuy 的物流 gross margin；
- 任何冻结 SKU 到 ZIP10001 的当前美元运费或 duty。

---

## 7. Data gaps

最关键缺口不是再搜更多营销页，而是以下字段：

1. **54 SKU 的最终 packed weight + L/W/H**，不是产品净重。
2. ZIP **10001** 当前公开 calculator 输出：route name、billable weight、首重/续重、fuel/operation/customs/DDP fee、ETA、battery eligibility。
3. 每一 SKU 的 **HTS 8/10 digit**、MFN、既有 China Section 301、新 2026 Section 301 exemption、Section 232/AD-CVD（如适用）。
4. “Tax-free / duty-prepaid”线路到底包含哪项税、谁作为 customs filer/importer、是否有补税条款。
5. Superbuy SBS 商务 rate card：100/1,000/10,000 parcels per month，按 weight bands 和 battery/non-battery 拆分。
6. 商务 rate 是否允许**独立消费者地址、独立 tracking、独立申报**，还是优惠仅适用于 physical bulk consolidation。
7. 失败件成本：退运、拒收、清关失败、二次派送、损坏、保险。
8. Core Superbuy 是否提供可公开集成的通用 API；当前公开证据对 Shopify/plugin 较明确，对通用 API 不如 BuckyDrop 明确。

这些字段均应标为 **AUTHENTICATED DATA REQUIRED / REAL SHIPPING QUOTE REQUIRED / NEGOTIATED DATA REQUIRED**，而不是用搜索结果代填。

---

## 8. Most surprising finding

最意外的不是“Superbuy 能否寄”，而是 **Superbuy 已公开描述“拆分订单分别寄给不同用户”这一 B2B 场景**。

这直接削弱了一个常见假设：

> 想获得供应链规模化能力，就必须先让平台把货物物理聚合成大货、进口到美国，再二次履约。

至少从**操作能力**看，这个假设不成立；现成服务商已把“商业客户批量下单”和“每个终端客户独立包裹”放在同一产品体系里。 [Superbuy](https://www.superbuy.com/en/page/businessservice/?utm_source=chatgpt.com)

但真正关键的经济学问题仍未回答：

> **这种“commercial aggregation without physical consolidation”是否真的带来足够大的每包运价折扣？**

公开资料没有答案。

---

## 9. What would falsify my conclusion?

以下任一结果都会明显推翻“现成 agent infrastructure 足够”的判断：

1. 实际书面商务报价显示 1,000–10,000 独立 DTC 包裹与公开 retail calculator **几乎同价**。
2. Superbuy 的“split to different users”实际上只支持低频人工流程，无法 API/批量稳定履约。
3. 电池 SKU 在美国方向可用线路太少，费用使 C01/C02/C03/C06/C08/C10/C11/C12 的 landed advantage 普遍消失。
4. 2026 HTS+Section 301+MPF 后，大多数高价值 SKU 的 duty stack 足以吃掉价格差。
5. C10/C15/C17 的真实 packed dimensions 导致计费重大幅高于实重，从而使重/大品类全面失去经济性。
6. 商务 discount 只适用于物理 bulk cargo，不适用于各自直寄 1,000 个消费者地址。
7. 每包清关/entry fee 在 de minimis 取消后的实际执行成本显著高于当前模型预期。

---

## 10. Suggested next experiment

如果只能做一个实验，应该是一个**受控的“12 包真实报价矩阵”**，而不是继续搜索网页。

从已冻结样本中按物流属性预先选 12 个 SKU：轻小普通品、轻小电池、笔记本/平板、中型电器、大体积轻货各若干。**不按预期价差选样本。**

对每个 SKU 固定：

- ZIP10001；
- 精确冻结 variant；
- warehouse-packed weight；
- L/W/H；
- battery/special classification；
- 商品申报价值；
- 8/10-digit HTS；
- 相同保险/追踪/SLA；
- 同一个观察日。

然后取得四组完全独立数字：

1. retail standalone；
2. 同一消费者 consolidation 后的 marginal shipping；
3. 书面商务报价：**1,000 个独立消费者订单/月，不物理合箱**；
4. 1,000 件真正 bulk-import + US fulfillment。

对结构 3 的询价必须明确写成：

> 1,000 independent DTC parcels/month, each with a different US recipient/address and individual tracking; no physical consolidation into one US-bound master shipment.

只有这个实验能直接回答 W5 最大未知量：

> **“物流规模经济是否可以通过商业订单聚合获得，而无需平台自己成为物理聚合商/importer？”**

---

```json
{
  "job_id": "W5-A",
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
      "claims_supported": ["C01", "C02", "C08"]
    },
    {
      "source_id": "S02",
      "url": "https://login.superbuy.com/en/page/query/freight/",
      "title": "International Shipping Cost Estimator - Superbuy",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C02", "C03", "C04"]
    },
    {
      "source_id": "S03",
      "url": "https://www.superbuy.com/en/page/businessservice/",
      "title": "Superbuy B2B Business Services",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "snippet_only",
      "claims_supported": ["C05", "C06"]
    },
    {
      "source_id": "S04",
      "url": "https://www.buckydrop.com/en/services/pricing/",
      "title": "Pricing - BuckyDrop",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S05",
      "url": "https://www.buckydrop.com/en/dropshipping/",
      "title": "Dropshipping from China - BuckyDrop",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07", "C09"]
    },
    {
      "source_id": "S06",
      "url": "https://blog.buckydrop.com/dropshipping-shipping-costs-from-china/",
      "title": "Dropshipping Shipping Costs from China: How to Calculate the Real Cost Before You Sell",
      "published_at": "2026-09-08",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C10"]
    },
    {
      "source_id": "S07",
      "url": "https://blog.sugargoo.com/estimate-international-shipping-costs-sugargoo/",
      "title": "Estimate Your International Shipping Costs Online with Sugargoo",
      "published_at": "2025-09-12",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S08",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/",
      "title": "Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    },
    {
      "source_id": "S09",
      "url": "https://www.help.cbp.gov/s/article/Article-1128?language=en_US",
      "title": "Customs User fee - Merchandise Processing Fees",
      "published_at": "2026-03-02",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "snippet_only",
      "claims_supported": ["C13"]
    },
    {
      "source_id": "S10",
      "url": "https://www.help.cbp.gov/s/article/Article-1225?language=en_US",
      "title": "Duty, Taxes and other Fees required to import goods into the United States",
      "published_at": "2026-02-13",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "snippet_only",
      "claims_supported": ["C13", "C14"]
    },
    {
      "source_id": "S11",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-takes-action-forced-labor-section-301-investigations",
      "title": "USTR Takes Action in Forced Labor Section 301 Investigations",
      "published_at": "2026-07-23",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C15"]
    },
    {
      "source_id": "S12",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/june/ustr-makes-findings-and-proposes-action-60-section-301-investigations-relating-failures-take-action",
      "title": "USTR Makes Findings and Proposes Action in 60 Section 301 Investigations",
      "published_at": "2026-06-02",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C15"]
    },
    {
      "source_id": "S13",
      "url": "https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search",
      "title": "How to Navigate the Section 301 Tariff Process",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C15"]
    },
    {
      "source_id": "S14",
      "url": "https://www.reddit.com/r/Superbuy/comments/1wxmp0z/shipping_fee_question/",
      "title": "Shipping fee question",
      "published_at": "2026-10-04",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C16"]
    },
    {
      "source_id": "S15",
      "url": "https://www.reddit.com/r/Superbuy/comments/1vvs196/question_about_shipping/",
      "title": "Question about shipping",
      "published_at": "2026-08-23",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C04", "C16"]
    },
    {
      "source_id": "S16",
      "url": "https://www.reddit.com/r/Superbuy/comments/1vt36t4/volumetric_weight_vs_actual_weight/",
      "title": "volumetric weight vs. actual weight",
      "published_at": "2026-08-19",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C03", "C16"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "Superbuy公开称Taobao、Tmall、JD、1688标准采购服务费为0。",
      "classification": "FACT",
      "source_ids": ["S01"],
      "confidence": "high",
      "counterevidence": "0采购服务费不代表国际物流或整体服务没有利润；公司未披露物流毛利。"
    },
    {
      "claim_id": "C02",
      "claim": "Superbuy支持同一客户多商品免费合包，并按最终重量、线路及目的地计算国际运费。",
      "classification": "FACT",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "合包可能增加体积重，且特殊品可能迫使使用更贵线路。"
    },
    {
      "claim_id": "C03",
      "claim": "体积重是China-direct成本模型的关键变量，净重不足以形成可靠报价。",
      "classification": "FACT",
      "source_ids": ["S02", "S06", "S15", "S16"],
      "confidence": "high",
      "counterevidence": "部分线路按实际重量计费，因此并非所有SKU都受体积重影响。"
    },
    {
      "claim_id": "C04",
      "claim": "含电池商品并非整体禁运；Superbuy计算器为Built-in Battery、Power Bank和单电池提供独立商品分类，但线路选择受限。",
      "classification": "FACT",
      "source_ids": ["S02", "S15"],
      "confidence": "high",
      "counterevidence": "具体目的地和路线仍可能拒收特定电池配置。"
    },
    {
      "claim_id": "C05",
      "claim": "Superbuy公开B2B材料描述了拆分订单并将包裹分别寄给不同终端用户的能力。",
      "classification": "FACT",
      "source_ids": ["S03"],
      "confidence": "medium",
      "counterevidence": "该动态页面本次完整正文无法由open工具提取，证据来自官方页面索引内容；实际吞吐量和API范围未验证。"
    },
    {
      "claim_id": "C06",
      "claim": "现有公开证据不足以证明1000个独立DTC订单会触发某一具体Superbuy商务折扣。",
      "classification": "FACT",
      "source_ids": ["S03"],
      "confidence": "high",
      "counterevidence": "Superbuy营销材料称存在专享物流折扣，但未披露量级和费率。"
    },
    {
      "claim_id": "C07",
      "claim": "BuckyDrop当前公开价目列出CN¥9.90/parcel履约费、CN¥199/月Pro计划，并自称国际运输zero-markup按承运商最终重量/体积结算。",
      "classification": "FACT",
      "source_ids": ["S04"],
      "confidence": "high",
      "counterevidence": "zero-markup是公司自述，未经过独立审计。"
    },
    {
      "claim_id": "C08",
      "claim": "Superbuy具体利润来源无法仅凭公开资料完整确定；公开可见收费集中于国际物流和增值履约服务。",
      "classification": "INFERENCE",
      "source_ids": ["S01"],
      "confidence": "medium",
      "counterevidence": "公司未公开carrier rebates、物流采购成本或业务分部毛利。"
    },
    {
      "claim_id": "C09",
      "claim": "BuckyDrop公开支持API Integration以及Shopify/WooCommerce自动订单同步、采购、打包和追踪。",
      "classification": "FACT",
      "source_ids": ["S05"],
      "confidence": "high",
      "counterevidence": "本研究未实际调用API或验证稳定性、限额和异常处理。"
    },
    {
      "claim_id": "C10",
      "claim": "现有agent基础设施在操作层面允许商业订单聚合但仍逐消费者独立履约，因此不天然要求平台自己物理聚货。",
      "classification": "INFERENCE",
      "source_ids": ["S03", "S05", "S06"],
      "confidence": "medium",
      "counterevidence": "是否能因此取得足够大的运价优势尚无公开商务报价证明。"
    },
    {
      "claim_id": "C11",
      "claim": "Sugargoo曾公开2025年3kg服装寄California的示例费率约US$55.18至US$88.71，但这些数字不是2026-10-06 ZIP10001现行报价。",
      "classification": "FACT",
      "source_ids": ["S07"],
      "confidence": "high",
      "counterevidence": "路线、政策、季节、地区及商品类别均不同，不能外推至冻结SKU。"
    },
    {
      "claim_id": "C12",
      "claim": "截至研究基准，美国19 USC 1321(a)(2)(C)低值de minimis免税继续暂停，非邮政低值货物不能按旧$800免税模型计算。",
      "classification": "FACT",
      "source_ids": ["S08"],
      "confidence": "high",
      "counterevidence": "特定法定豁免及邮政entry机制仍需按具体法规判断。"
    },
    {
      "claim_id": "C13",
      "claim": "FY2026 CBP MPF对formal entry为0.3464%，最低$33.58、最高$651.50；informal entry存在固定fee，海运商业货物还可能有0.125% HMF。",
      "classification": "FACT",
      "source_ids": ["S09", "S10"],
      "confidence": "high",
      "counterevidence": "具体消费者包裹采用formal、informal、mail或express hub哪种entry必须逐线路确认。"
    },
    {
      "claim_id": "C14",
      "claim": "本W5比较端暂不把美国州/地方sales/use tax计入物流landed cost，并要求未来所有渠道一致处理。",
      "classification": "INFERENCE",
      "source_ids": ["S10"],
      "confidence": "high",
      "counterevidence": "实际checkout税务责任取决于卖方、marketplace和业务架构，需在后续合规/经济模型中加入。"
    },
    {
      "claim_id": "C15",
      "claim": "2026年中国货物税负不能用单一百分比代理；新Section 301行动、产品豁免、MFN及既有China Section 301均要求先确定8位HTS。",
      "classification": "FACT",
      "source_ids": ["S11", "S12", "S13"],
      "confidence": "high",
      "counterevidence": "具体SKU税率在完成HTS分类和豁免核对前仍为未知。"
    },
    {
      "claim_id": "C16",
      "claim": "2026社区样本显示入仓后的实际包装尺寸会显著改变最终计费重和可用线路。",
      "classification": "FACT",
      "source_ids": ["S14", "S15", "S16"],
      "confidence": "medium",
      "counterevidence": "社区案例不是随机样本，也不是正式价格表。"
    }
  ],
  "categories": [
    {"category_id":"C01","sku_ids":["C01-S01","C01-S02","C01-S03"],"dominant_logistics_risk":"built_in_lithium_battery","volumetric_risk":"low_to_medium","current_zip10001_quote_available":false},
    {"category_id":"C02","sku_ids":["C02-S01","C02-S02","C02-S03"],"dominant_logistics_risk":"lithium_battery_plus_laptop_size","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C03","sku_ids":["C03-S01","C03-S02","C03-S03"],"dominant_logistics_risk":"built_in_lithium_battery","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C04","sku_ids":["C04-S01","C04-S02","C04-S03"],"dominant_logistics_risk":"digital_electrical_and_power_adapter","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C05","sku_ids":["C05-S01","C05-S02","C05-S03"],"dominant_logistics_risk":"electronics_hts_and_route","volumetric_risk":"low","current_zip10001_quote_available":false},
    {"category_id":"C06","sku_ids":["C06-S01","C06-S02","C06-S03"],"dominant_logistics_risk":"built_in_battery","volumetric_risk":"low","current_zip10001_quote_available":false},
    {"category_id":"C07","sku_ids":["C07-S01","C07-S02","C07-S03"],"dominant_logistics_risk":"mixed_battery_and_general_peripherals","volumetric_risk":"low","current_zip10001_quote_available":false},
    {"category_id":"C08","sku_ids":["C08-S01","C08-S02","C08-S03"],"dominant_logistics_risk":"built_in_battery","volumetric_risk":"low","current_zip10001_quote_available":false},
    {"category_id":"C09","sku_ids":["C09-S01","C09-S02","C09-S03"],"dominant_logistics_risk":"mixed_power_and_electronics","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C10","sku_ids":["C10-S01","C10-S02","C10-S03"],"dominant_logistics_risk":"lithium_battery_plus_large_base_station","volumetric_risk":"high","current_zip10001_quote_available":false},
    {"category_id":"C11","sku_ids":["C11-S01","C11-S02","C11-S03"],"dominant_logistics_risk":"heavy_tool_or_lithium_tool_battery","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C12","sku_ids":["C12-S01","C12-S02","C12-S03"],"dominant_logistics_risk":"lithium_high_value_fragile","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C13","sku_ids":["C13-S01","C13-S02","C13-S03"],"dominant_logistics_risk":"vehicle_electronics_and_bundle_variation","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C14","sku_ids":["C14-S01","C14-S02","C14-S03"],"dominant_logistics_risk":"tent_volume_or_long_side_oversize","volumetric_risk":"medium_to_high","current_zip10001_quote_available":false},
    {"category_id":"C15","sku_ids":["C15-S01","C15-S02","C15-S03"],"dominant_logistics_risk":"bulky_heavy_electrical","volumetric_risk":"high","current_zip10001_quote_available":false},
    {"category_id":"C16","sku_ids":["C16-S01","C16-S02","C16-S03"],"dominant_logistics_risk":"apparel_shoe_box_volume","volumetric_risk":"medium","current_zip10001_quote_available":false},
    {"category_id":"C17","sku_ids":["C17-S01","C17-S02","C17-S03"],"dominant_logistics_risk":"extreme_bulky_volumetric","volumetric_risk":"very_high","current_zip10001_quote_available":false},
    {"category_id":"C18","sku_ids":["C18-S01","C18-S02","C18-S03"],"dominant_logistics_risk":"general_goods_with_box_condition_volume","volumetric_risk":"medium","current_zip10001_quote_available":false}
  ],
  "sku_candidates": [
    {"sku_id":"C01-S01","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed weight/dimensions, live ZIP10001 route quote and HTS unavailable"},
    {"sku_id":"C01-S02","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C01-S03","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C02-S01","status":"class_evaluated_quote_missing","shipping_class":"lithium_laptop","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"final packed size/weight and route unavailable"},
    {"sku_id":"C02-S02","status":"class_evaluated_quote_missing","shipping_class":"lithium_laptop","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C02-S03","status":"class_evaluated_quote_missing","shipping_class":"lithium_laptop","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C03-S01","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_tablet","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed dimensions and live route unavailable"},
    {"sku_id":"C03-S02","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_tablet","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C03-S03","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_tablet","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C04-S01","status":"class_evaluated_quote_missing","shipping_class":"digital_electrical","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data and live route unavailable"},
    {"sku_id":"C04-S02","status":"class_evaluated_quote_missing","shipping_class":"digital_electrical","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C04-S03","status":"class_evaluated_quote_missing","shipping_class":"digital_electrical","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C05-S01","status":"class_evaluated_quote_missing","shipping_class":"small_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data, route and HTS unavailable"},
    {"sku_id":"C05-S02","status":"class_evaluated_quote_missing","shipping_class":"small_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C05-S03","status":"class_evaluated_quote_missing","shipping_class":"small_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C06-S01","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_audio","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"battery route and final packed data unavailable"},
    {"sku_id":"C06-S02","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_audio","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C06-S03","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_audio","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C07-S01","status":"class_evaluated_quote_missing","shipping_class":"AA_battery_peripheral","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"whether battery ships with item plus packed data/route unresolved"},
    {"sku_id":"C07-S02","status":"limited_classification_quote_missing","shipping_class":"wireless_peripheral_battery_status_to_verify","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"frozen data itself leaves battery/charging dependency unverified"},
    {"sku_id":"C07-S03","status":"class_evaluated_quote_missing","shipping_class":"wired_general_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data and live route unavailable"},
    {"sku_id":"C08-S01","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_wearable","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data/route unavailable"},
    {"sku_id":"C08-S02","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_wearable","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C08-S03","status":"class_evaluated_quote_missing","shipping_class":"built_in_battery_wearable","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C09-S01","status":"class_evaluated_quote_missing","shipping_class":"smart_home_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data and route unavailable"},
    {"sku_id":"C09-S02","status":"limited_classification_quote_missing","shipping_class":"smart_lock_power_details_unknown","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"power details plus packed data unresolved"},
    {"sku_id":"C09-S03","status":"class_evaluated_quote_missing","shipping_class":"mains_smart_switch","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed data/HTS/route unavailable"},
    {"sku_id":"C10-S01","status":"class_evaluated_quote_missing","shipping_class":"lithium_robot_vacuum_large_base","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"high volumetric risk; final packed dimensions essential"},
    {"sku_id":"C10-S02","status":"class_evaluated_quote_missing","shipping_class":"lithium_robot_vacuum_large_plumbed_base","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"high volumetric risk; final packed dimensions essential"},
    {"sku_id":"C10-S03","status":"class_evaluated_quote_missing","shipping_class":"lithium_robot_vacuum_large_base","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"high volumetric risk; final packed dimensions essential"},
    {"sku_id":"C11-S01","status":"class_evaluated_quote_missing","shipping_class":"heavy_mains_power_tool","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed weight/dimensions and live route unavailable"},
    {"sku_id":"C11-S02","status":"class_evaluated_quote_missing","shipping_class":"lithium_power_tool","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"battery line plus packed weight/dimensions unavailable"},
    {"sku_id":"C11-S03","status":"class_evaluated_quote_missing","shipping_class":"lithium_power_tool","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C12-S01","status":"class_evaluated_quote_missing","shipping_class":"lithium_high_value_camera","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"battery, fragile/high-value handling, packed data and HTS unresolved"},
    {"sku_id":"C12-S02","status":"class_evaluated_quote_missing","shipping_class":"lithium_high_value_camera","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C12-S03","status":"class_evaluated_quote_missing","shipping_class":"lithium_action_camera","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"battery and packed data unresolved"},
    {"sku_id":"C13-S01","status":"class_evaluated_quote_missing","shipping_class":"vehicle_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"bundle/packed weight/route unresolved"},
    {"sku_id":"C13-S02","status":"class_evaluated_quote_missing","shipping_class":"vehicle_electronics","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"bundle/packed weight/route unresolved"},
    {"sku_id":"C13-S03","status":"limited_classification_quote_missing","shipping_class":"inflator_power_source_to_verify","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"power source not verified in frozen sample"},
    {"sku_id":"C14-S01","status":"class_evaluated_quote_missing","shipping_class":"compressible_outdoor_tent","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed weight/dimensions unresolved"},
    {"sku_id":"C14-S02","status":"class_evaluated_quote_missing","shipping_class":"long_side_sporting_goods","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"long-side surcharge/packed dimensions unresolved"},
    {"sku_id":"C14-S03","status":"limited_classification_quote_missing","shipping_class":"tent_variant_provisional","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"frozen exact variant mapping and packed weight remain provisional"},
    {"sku_id":"C15-S01","status":"class_evaluated_quote_missing","shipping_class":"bulky_heavy_3d_printer","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"potential customized/bulk service; package data unavailable"},
    {"sku_id":"C15-S02","status":"class_evaluated_quote_missing","shipping_class":"bulky_3d_printer","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"package data unavailable"},
    {"sku_id":"C15-S03","status":"limited_classification_quote_missing","shipping_class":"mains_filament_dryer","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"product URL unresolved and packed/electrical details incomplete"},
    {"sku_id":"C16-S01","status":"class_evaluated_quote_missing","shipping_class":"bag_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed dimensions/route unavailable"},
    {"sku_id":"C16-S02","status":"class_evaluated_quote_missing","shipping_class":"shoe_box_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"shoe-box treatment and packed dimensions unresolved"},
    {"sku_id":"C16-S03","status":"class_evaluated_quote_missing","shipping_class":"shoe_box_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"shoe-box treatment and packed dimensions unresolved"},
    {"sku_id":"C17-S01","status":"class_evaluated_quote_missing","shipping_class":"extreme_bulky_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"final packed dimensions are decisive and unavailable"},
    {"sku_id":"C17-S02","status":"class_evaluated_quote_missing","shipping_class":"extreme_bulky_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C17-S03","status":"class_evaluated_quote_missing","shipping_class":"extreme_bulky_volumetric","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"same"},
    {"sku_id":"C18-S01","status":"class_evaluated_quote_missing","shipping_class":"general_toys_box_volume","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed dimensions and route unavailable"},
    {"sku_id":"C18-S02","status":"class_evaluated_quote_missing","shipping_class":"general_collectible","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"packed dimensions and route unavailable"},
    {"sku_id":"C18-S03","status":"class_evaluated_quote_missing","shipping_class":"general_collectible_box_condition_sensitive","standalone_quote":null,"consolidated_marginal_quote":null,"commercial_1000_separate_quote":null,"bulk_import_quote":null,"hts":null,"tariff_rate":null,"reason":"protective packaging may increase volume; packed data unavailable"}
  ],
  "data_gaps": [
    "REAL SHIPPING QUOTE REQUIRED: all 54 frozen SKUs need final packed weight and L/W/H plus ZIP10001 route output.",
    "HTS REQUIRED: no frozen SKU has an adjudicated US 8/10-digit HTS classification; tariff rates remain null.",
    "NEGOTIATED DATA REQUIRED: no public Superbuy rate card establishes a 1000-independent-parcel volume threshold or discount.",
    "AUTHENTICATED/COMMERCIAL DATA REQUIRED: exact duty-prepaid/tax-free line terms, customs filer/importer allocation and surcharge treatment.",
    "API TEST REQUIRED: core Superbuy generic API scope and bulk-order exception handling were not technically validated.",
    "REAL WORKFLOW DATA REQUIRED: refunds, failed delivery, customs exception, insurance and reshipment costs.",
    "US sales/use tax excluded symmetrically from W5 logistics endpoint; later checkout comparison must apply channel-specific tax consistently.",
    "Source-level exact retrieval timestamps are unavailable from the web tool; final verification clock was 2026-10-07T01:00:36Z to 2026-10-07T01:03:52Z.",
    "Sources and claims attested by this model still await coordinator review."
  ],
  "pre_freeze_compliance": true
}
```