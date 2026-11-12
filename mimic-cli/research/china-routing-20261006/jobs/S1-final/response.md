# 最终独立裁决报告

## 审计状态：`INPUT_COMPLETE`

我核验了本次上传工件 `final-synthesis-evidence.txt` 的实际 SHA256：

`2be95283fa0dd89ba6dc026cea8642e5c2766fe45fbc1fe0e47f10ae052db4c2`

与用户给出的哈希完全一致。文件共 70,663 行；其中可定位并检查到 **24/24 份原始独立 research report、25/25 个独立 mg source-audit 区块、4/4 个 judge report、冻结样本及最后的机械 denominator/artifact clarification**。原 brief 要求的最终 12 问见附件。final-synthesis-evidence

有两个必须先裁决的工件冲突：

1. **样本最终是已冻结，而不是未冻结。** 顶部 `PREFREEZE IDENTITY VALIDATION LIMITATIONS` 的 `sample_frozen=false` 是冻结前的瞬时状态；文件末尾的机械澄清明确说明随后生成了不可变的 `sample-freeze-v1.json`，共 **54 SKU**、`frozen_at_utc=2026-10-06T22:42:51.415711+00:00`。因此 J1/J2 等把顶部 prefreeze 状态当成最终状态的说法不成立。不过 `C17-S01/C17-S02` 缺 manufacturer model number 的缺口仍然真实存在。final-synthesis-evidence final-synthesis-evidence
2. J2/J3 文本自述核验的是内部 `judge-evidence-pack` 哈希 `0912ea…`，**它不是本次上传文件的哈希**。我不采用它们“当前附件 hash match”的自证；但其正文、引用的 24 个 raw-report SHA 和 source-audit claim 均嵌在本次可检查文件中，所以这属于 **artifact-identity caveat**，不是输入缺失。

最终冻结样本的机械重算结果是：**54 SKU = 18 类 × 3；36 domestic-head + 18 domestic-opportunity；32/54 `head_status_verified=true`；53/54 `exact_variant_verified=true`；0/54 `current_transaction_price_verified=true`。** 唯一 exact-variant 未完全闭合的是 `C14-S03` Naturehike 云尚PRO。样本明确不是 probability sample，GMV weights 未观察。final-synthesis-evidence

---

# 输入完整性表

下面每一项均实际检查，不以 judge 的“已检查”声明代替我的裁决。

| 输入 | Artifact / SHA256 | 具体检查到的发现 | 状态 |
|---|---|---|---|
| W1-A | `c8c930872433332d7a83a7231bcdb7447b68bf6d5e0f9e0b8bd698b76b8e7bfb` | 拒绝把异口径来源硬拼成 18 类精确 GMV 排名；C02 laptop 两个市场模型相差约 4.3×，保持 unresolved | 已检查 |
| W1-B | `a6474c4aa74cce05b3f17ac17423941223bd83b9b6b7360e34839ee75702a1d1` | 能识别大需求池，但 proposed demand weight 混入 growth/fragmentation；C16 retailer-establishment receipts 不能升级为全渠道 GMV | 已检查 |
| W1-C | `489e916b8e9646e4317a6db3d9ae052966d673c8c8dd9777edef9c1346da34ba` | shipment 与 consumer-sales 方向可分叉；continuation 的 CIPA 时点被 audit 纠正 | 已检查 |
| W2-A | `046f9bb84061977ebf1eb89b3f89c6b6337f0359d453e9c18d8860fbf059c024` | 坚持 domestic-first，不因海外可得性换样；当前 transaction price 不可核时留 null | 已检查 |
| W2-B | `2182ad02c9f58435c88b974e1de064cbcb5a6c02fc01f9868229aa33b9cca532` | 登录态到手价与公开标价分开；KINGBANK 等公开价格不能自动当最终成交价 | 已检查 |
| W2-C | `5994f7cefe60ef7d53b913d217c1162ce4cfa85fce25fcf630246b1b41c47e62` | 一些“head”实为精确商品+评论证据而非全市场销量榜；52TOYS ¥168 只能作历史首发价 | 已检查 |
| W3-A | `4f22acab532a65f7392a4212411ec872d3020edfff3edb76aca52c469e38868b` | 不换样；四种物流结构均没有完整 landed chain，`verified landed savings n=0` | 已检查 |
| W3-B | `a00c62dbca6c1950c57060753e2fd19f80a4d5364c4d4a1debbce82395961ef5` | 找到一些海外价格信号，但 A/B exact loop 与 ZIP10001 delivered endpoint 仍未闭合 | 已检查 |
| W3-C | `e440304de201a8f93fd4e211eea560e2ef591999d85095bc90b9f6cb4027ca36` | 更多价格线索仍受 selector、补贴、地区版本和 landed 缺口限制；不能生成分布 | 已检查 |
| W4-A | `39bcd589d0b450a5e187b5d0632dd1edcdc8413733e0ab50664daa04c36e1bc3` | 原始 `BLOCKED` 表述过强；audit 重编码后很多是 Temu page-shell，而非无货 | 已检查 |
| W4-B | `525c6379ac871ac8ecc3806dbcb46d1b52c36248a9d9ac01136e020bf03c60b3` | 17 blocked + 1 login-required 是研究访问缺失，不是市场缺货率 | 已检查 |
| W4-C | `633e5e642b1c31ec6bf043344cecf2e10161b936d1698b7e3deaa18d05a48fed` | 二级索引仅可排除明显错误 variant，不能升级成当前 Ali/Temu exact offer | 已检查 |
| W5-A | `c68db3699dddd62da8b3c8a66455bf385a1983d7e222fb56335b855856ff68f6` | Superbuy 可作为采购/仓/跨境履约组件；1000 个独立消费者包裹的商务运价没有公开证据 | 已检查 |
| W5-B | `f684b48ecbd1594400d5663dcc12027a44082e698cc8b1351a1890316b10fd37` | 54/54 可做物流属性筛查，但 **0/54** 有 ZIP10001 quote-grade 国际运费 | 已检查 |
| W5-C | `cc295668c9ea0c7fe24c84943411a91e0a7e2dd0c96d19f406733afaaf2ff48d` | commercial order aggregation 在操作上可不先物理拼货；这不等于已证明 freight discount | 已检查 |
| W6-A | `1b958a99991c685ebe774ffee0c7d4e319adb0fc2c4e862eacd0418ecfb669c0` | 旧 `<$800 de-minimis = 无税` 模型已不能使用 | 已检查 |
| W6-B | `20090bcef53c54b0f1c22e4c329ba2ecade652c93db347be1187ece6c5100d19` | purchaser、broker、IOR、certification responsibility 必须按合同/entry/法规角色判断，不能由“agent”标签决定 | 已检查 |
| W6-C | `0b194b34f17487cd2df7d90f75bfbb4f5821523fa2db44cc8f48e21583b8977f` | 轻资产结构有法律空间，但 tariff/HTS/IOR 仍须逐交易闭合 | 已检查 |
| W7-A | `a9e71cf2a984b1df88850b7c96eb290b6160bef4c66c2219c627e84afbd41554` | PriceDoge 等证明“没人做过”错误；HandHunt 显示最终运费往往入仓后才准确 | 已检查 |
| W7-B | `857b295ebf977c999388e67eec0fb90b59661ba0703999909b17d2a5e734aaa0` | GP/IK 等 landed-cost 小工具存在；小用户数不能单独证明需求失败 | 已检查 |
| W7-C | `91e96c5b6e7375091ae9b4c817b83d270d1f9a3038c310021f9250c66c87ca56` | 没找到规模化的一体化 neutral exact→authenticated price→final landed chain；但“为什么没有”因果多数仍 speculative | 已检查 |
| W8-A | `6e0b859334d4da5c0b82c715b772d6d4364f0a45a1f31dbe3c5692405a457042` | 税费、单件物流、数据接入是 broad thesis 的强反证；没有 exact landed 数据推翻 narrow thesis | 已检查 |
| W8-B | `56a438d4c0253df9918fe41cb13f1a001c189b329bf67519e41e4286467684d8` | 明确判 broad 变弱、narrow unresolved；10/22 的未来合规点不能提前当成 10/06 已发生摩擦 | 已检查 |
| W8-C | `a6eea15a627e8223d526626546ae0713f9e512ce44d8c5708a9bf2f33babab4c` | AliExpress 的全球化/物流优化是最强 bear evidence；仍未证明 China-head exact prices 已全面收敛 | 已检查 |
| J1 | `J1-methodology` | 正确识别 selection/auditability bias、variant mismatch、blocked≠unavailable、n=0≠zero saving；错误继承 prefreeze 状态 | 已检查并部分推翻 |
| J2 | `J2-economic` | 正确否决 demand-weighted ROI 与现有 unit economics；正确区分 commercial aggregation 与 physical bulk import | 已检查 |
| J3 | `J3-bear` | 最强观点是“足够大市场没有被证成”，不是“市场为零”；这一限定成立 | 已检查 |
| J4 | `J4-bull` | 最强观点是“交易级全球价格发现链存在系统性缺口”，但自己也明确不等于有大套利池 | 已检查 |

J1–J4 的核心共识之所以可信，不是因为 4 票多数，而是因为它们最终都可回溯到 R3/R4 的零可计算 observation、R-W5/R-W6 的官方规则及 W1 的 denominator conflict。机械 denominator 记录明确：每个 W3/W4 logical replicate 的正确分母都是 **54，不是每 batch 的 9，也不能把三 replicate 相加成 162 个独立 SKU**。final-synthesis-evidence

---

# A. What we know with high confidence

**1. Domestic-first 原则基本守住。** 最终 54-SKU universe 在海外研究前冻结，没有看到海外价格后删除难匹配 SKU；exclusion log 为空。这个设计成功避免了上一轮最危险的 international-first survivorship bias。final-synthesis-evidence

**2. 但这个样本不是总体概率样本。** 入样仍受到“能否从国内页面闭合 rank/exact variant”的可审计性影响；因此不能把 54 SKU 中任何比例直接外推为“中国所有热门商品中 X% 有套利机会”。

**3. 国内端有真实的 hot/exact evidence，但成交价严重缺失。** 机械重算是 32/54 verified-head、53/54 exact variant；然而 **0/54 的 current transaction price 被最终标为 verified**。公开标价、首发价、历史价、会员价、国补价都不能偷偷替代当前普通成交价。

**4. 目前没有一个 SKU 能形成经审计的完整 exact landed-savings observation。** 三个 W3 replicate 都是分母 54、`mg_audited_exact_price_comparison_count=0`、`verified_landed_savings_count=0`。这里的 **0 是可计算 observation 的数量，不是节省率等于 0%**。final-synthesis-evidence

**5. Temu/AliExpress coverage 也不能据此写成 0%。** W4 的 0 usable exact-coverage observation 主要来自 `page_shell`、`LOGIN_REQUIRED`、blocked/not-observed；这些状态没有一个等价于 `VERIFIED_UNAVAILABLE`。

**6. 四种物流经济从证据上仍全部是 separate unknowns。** standalone、同消费者 consolidation marginal、1000 个独立消费者包裹商务价、true bulk import 没有可互换的真实 rate。W5 原始报告自己把四种结构全部保持为 `null`。final-synthesis-evidence

**7. Superbuy/类似基础设施证明了“操作能力”，没有证明“规模折扣经济”。** 普通采购费为 0、免费 consolidation、国际履约和电池线路输入均有官方依据；但 1000 个独立美国消费者包裹/月的成交商务价没有公开 rate card。R-W5 进一步降级了 Superbuy business-service 的 page-shell 证据，而 BuckyDrop API/逐单履约页仍支撑“不必先做 physical aggregation 才能逐单发货”。final-synthesis-evidence

**8. 2026 年旧 de-minimis 假设已经失效，且 tariff 必须逐 SKU。** 不能统一套一个“中国税率”；HTS、Chapter 99、301/豁免、entry mode、MPF 等必须分别计算。10 月 22 日才生效的部分邮政字段要求，不能倒灌成 10 月 6 日已经发生的成本。final-synthesis-evidence

**9. “从来没人做过”是错误假设。** PriceDoge、2tao、1688 cross-platform tools、AiPrice、HandHunt、GP/IK 等已经覆盖了 matching、price discovery、agent/landed-estimation 的不同片段；Capital One/Honey 又证明一般 shopping-assistant 可以达到大规模。真正没被证实的是“完整、neutral、exact、transaction-grade final-landed router 已经规模化”。

**10. 最大的已确认 gap 是信息/测量链，而不是已确认的利润池。** `exact SKU → 当前中国成交价 → 海外 exact convenience price → warehouse packed dimensions → actual freight → HTS/tariff/fees → delivered cost` 在证据包中系统性断裂。这是 J4 最强、且由原始工件支持的正向发现。final-synthesis-evidence

---

# B. What appears true but is not yet proven

- **Probable：** 某些 China-head / US-middle-tail anomaly 确实存在；但频率、节省幅度和 GMV 尚未测出来。
- **Probable：** 小体积、高 ASP、低兼容摩擦商品比大件/高体积重/强地区兼容商品更容易形成可行 route；这是物流机制推断，不是 price-spread distribution。
- **Probable：** 一个 thin routing layer 可以在不拿 title、不做 IOR、不持库存的情况下先运行。
- **Probable：** 商业订单量可以在操作层聚合、仍逐消费者发货，不需要一开始就做物理 bulk import。
- **Probable：** AliExpress 已把一部分国际化中国 SKU 的价差压薄；但对本冻结 China-head universe 的深度没有测量。
- **Unproven：** “修好 price discovery 后，会出现大量 ≥20%/≥30% 的 landed savings。”
- **Unproven：** “有足够 GMV 支撑 venture-scale general consumer product。”

---

# C. What previous assumptions were wrong

| 原假设 | 最终裁决 |
|---|---|
| 样本最终 `sample_frozen=false` | **错误。** 那是 prefreeze note；后来 54 SKU 已 immutable freeze |
| W3 `0 verified savings` = 没有节省 | **错误。** 是 `n=0 calculable` |
| Temu/Ali `blocked` = 无货 | **错误。** page-shell/login-required/not-observed 不能升为 unavailable |
| 公开 list price = 当前普通成交价 | **错误。** 冻结样本 current-transaction-price verified = 0/54 |
| parent listing 最低价可以当 exact variant 价 | **错误。** C01-S02、C04-S03、C12-S03 等已被 audit 纠正 |
| 1000 个订单自然带来可量化 freight discount | **未证实。** 需要 negotiated rate card |
| 中国商品可以套一个统一 2026 tariff | **错误。** 必须逐 HTS/entry |
| 2026 还能套旧 <$800 de minimis economics | **错误** |
| 18 类可以直接从公开异口径市场数字精确排序/加总 | **错误。** shipment、PCE、wholesale、retail-model、forecast 不能混 |
| “没人试过 Amazon→China comparison” | **错误。** 有 PriceDoge 等前例 |
| agent 操作可行 = agent unit economics 已证明 | **错误** |
| full marketplace 的合规问题可以用来否定 thin router | **错误。** 架构必须分开 |

---

# 最终 12 问直接回答

| # | 问题 | 最终答案 | 置信度 / 决定性证据 |
|---|---|---|---|
| 1 | 中国国内正规热销商品 vs Amazon 的真实 landed advantage？ | **不可估。** 没有 audited exact landed pair，因此没有 median/mean/quantile | 高；R3 A/B/C `n=0` |
| 2 | vs AliExpress？ | **不可估。** Ali exact price/variant/ZIP delivered observations 未闭合 | 高；R3 + R4 |
| 3 | vs cheapest convenient overseas option？ | **不可估。** comparator 经常不是 exact、不是同 ZIP 或不是当前价 | 高 |
| 4 | 哪些 category spread 最大？ | **没有数据支持排名。** 任何“mini-PC/外设/玩具价差最大”目前都只是 hypothesis | 极高 |
| 5 | 哪些 category demand 最大？ | 粗 band 中 C01 smartphones、C13 automotive、C14 broad sports/outdoor、C16 apparel 属 Very High；C02/C08–C11/C17/C18 为 High；不能精确 1–18 排名 | 中高；W1 |
| 6 | 哪些 category 同时位于 demand×feasibility 右上？ | **当前不能认定。** Demand 有粗 band，但 price feasibility 缺失。仅能选“下一轮优先测量对象”，不能叫已证明 opportunity | 高 |
| 7 | China-head / US-middle-tail gap 是否真实？ | **国内 head 侧真实；US-middle/tail + economic spread 侧未证实。** 所以完整 economic gap = **Unproven**；price-discovery gap = **Confirmed** | 高 |
| 8 | gap 是偶发还是结构性？ | **价格发现摩擦是结构性的；有利可图 anomaly 的 prevalence 未知。** | 中高 |
| 9 | Temu 已解决哪些部分？ | 本 evidence pack **无法量化其解决了冻结 exact China-head universe 的多少**；W4 访问问题不能当覆盖率。Temu 只能被视为 head-SKU efficiency 的潜在 incumbent benchmark | 高 |
| 10 | AliExpress 已解决哪些部分？ | 已确认其具有全球国际化、库存/物流优化能力，并能主动压缩部分跨境摩擦；但 frozen exact coverage 与 price convergence 未测 | 高 |
| 11 | Superbuy 是否足够做基础设施？ | **操作层面：足够支持 pilot/agent/routing 测试。经济层面：尚不够证明 scale economics。** 不需要先自建 physical aggregation | 高 |
| 12 | 为什么没有 dominant consumer product？ | 有若干 confirmed operational/data/platform-shock reasons；但“需求不足/CAC/消费者不信任”等不能升级为 confirmed cause | 中高 |

W1 的可辩护 demand bands 本身明确只是定性 band，不是伪精确统一 GMV 排名。final-synthesis-evidence

---

# D. Category Opportunity Matrix — 全 18 类

下面的 “Net feasibility” **只表示物流/兼容/架构操作可行性，不表示已有正价差**。所有经济机会仍必须视为 `UNMEASURED`。

`H=x/3` 指冻结样本中 `head_status_verified=true` 的数量；不是全国市场份额。

| Category | US demand | CN domestic maturity | CN-US landed spread | Ali coverage | Temu coverage | Shipping economics | Compatibility / regulatory friction | Net feasibility | Evidence confidence |
|---|---|---|---|---|---|---|---|---|---|
| C01 Smartphones | Very High | H=2/3；exact 3/3 | **不可估** | 不可估 | 不可估 | Medium | **高**：锂电、频段、ROM/firmware、保修 | 中低 | 中高 |
| C02 Laptops | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium-Low | 中高：电池、重量、键盘/OS/保修 | 中低 | 中 |
| C03 Tablets | Medium-high | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium | 中：电池；Wi-Fi-only 较手机简单 | 中 | 中高 |
| C04 Mini PCs | Low-medium | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium-High | 中：电源、OS、barebone/配置匹配 | 中高（操作） | 中 |
| C05 Components/storage/networking | Medium-high | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | **High** | 低至中；router firmware/region 是例外 | **高（操作）** | 中 |
| C06 Audio | Medium | H=2/3；exact 3/3；但 head 榜是品牌窄榜 | 不可估 | 不可估 | 不可估 | Medium-High | 低中：电池/app/codec | 中高 | 中 |
| C07 PC peripherals | Medium | H=1/3；exact 3/3 | 不可估 | 不可估 | 不可估 | **High** | 低：多数标准 USB/无线；driver 例外 | 高（操作） | 中 |
| C08 Wearables | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium-High | 中高：NFC/app/region ecosystem | 中 | 中 |
| C09 Smart home/IoT | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium | **高**：协议、云区、FCC/无线、供电 | 中低 | 中 |
| C10 Robot vacuum/small appliances | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | **Low** | **高**：体积、重量、电池、供电、安装 | 低 | 中高 |
| C11 Tools | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Low-Medium | 中高：电池系统、安全、插头/电压、bundle | 中低 | 中 |
| C12 Camera/video | Medium | H=2/3；exact 3/3，但部分 head 证据弱 | 不可估 | 不可估 | 不可估 | Medium | 中：电池、高货值、warranty/bundle | 中 | 中 |
| C13 Automotive accessories | Very High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium | **高**：year/make/model fitment、安全关键件 | 中 | 中高 |
| C14 Sports/outdoor | Very High broad | **H=0/3；exact 2/3** | 不可估 | 不可估 | 不可估 | Medium-Low | 中：尺码、超长/超大、用途差异 | 中低 | 低中 |
| C15 Hobby/maker/3D print | Medium | H=1/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Low-Medium | 中：大件 printer vs 小电子高度异质 | 中低 | 中 |
| C16 Apparel/shoes/bags | Very High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium | **高商业摩擦**：size/returns/color/IP authenticity | 中 | 中高 |
| C17 Home/organization | High | H=2/3；exact variant 3/3；**2 条 manufacturer model null** | 不可估 | 不可估 | 不可估 | **Low** | 技术兼容低，但**体积重最高风险之一** | 低 | 中 |
| C18 Toys/collectibles | High | H=2/3；exact 3/3 | 不可估 | 不可估 | 不可估 | Medium-High | 低中：bundle/盒况/official-merch exactness | 中高（操作） | 中高 |

W5-B 的物流定性图给出的相对次序就是：C05/C07 高；C04/C06/C18 中高；C10/C17 低；其它居中或中低。它只能用于研究优先级，不能替代 landed cost。final-synthesis-evidence

### 哪些值得下一轮最先测？

不是“已经证明 opportunity 最大”，而是 **最能减少 uncertainty** 的组合：

- **高 demand + 相对可寄：** C03、C05、C07、C08、C13、C18。
- **高 demand + 最大结构摩擦，用来主动证伪：** C01、C09、C10、C11、C16、C17。
- **不能目前宣称 price-spread winner：** 所有 18 类。

---

# E. Price Spread Distribution

这是整个研究最重要的否决项。

## E1. Demand-weighted distribution

| 指标 | 结果 |
|---|---:|
| Frozen denominator | 54 SKU |
| Probability sample? | **No** |
| Valid demand weights | **0 套统一可比权重** |
| Audited exact landed-price observations | **0/54** |
| Mean savings | **不可估** |
| Median / P50 | **不可估** |
| P10 | **不可估** |
| P25 | **不可估** |
| P75 | **不可估** |
| P90 | **不可估** |
| % saving ≥10% | **不可估** |
| ≥20% | **不可估** |
| ≥30% | **不可估** |
| ≥40% | **不可估** |
| ≥50% | **不可估** |

**不允许**把缺失值当 0，也不允许拿 public list price + 假运费 + blanket tariff 造一条 synthetic distribution。

## E2. Opportunity-seeking / feasibility-weighted distribution

结果同样是 **不能构造**。

虽然冻结层里有 18 个 `domestic_opportunity` SKU，W3 三个 replicate 对同一 54 SKU 分别产生 8、9、7 个 `exact_coverage_observation`，但 **exact-price-comparison 仍全部是 0，landed-savings 仍全部是 0 个可计算 observation**。这 8/9/7 是“证据可观察性”，不是 savings，也不能相加成 24 个独立 SKU。W4 三 replicate 的 usable exact-coverage observation 又全部为 0。final-synthesis-evidence

因此：

> **本报告没有、也不会制造 mean、median、P10/P25/P50/P75/P90 或任何 ≥10/20/30/40/50% 分布。**

---

# F. China-head / US-middle-tail Gap

## 最终裁决

**经济意义上的 China-head / US-middle-tail gap：`UNPROVEN`。**

但这需要拆成三层：

**Domestic-head side：有证据。** 32/54 frozen rows 具备经 audit 的 `head_status_verified`，53/54 exact variant 闭合；这些不是从 Amazon 反向找回来的国际化 SKU。

**US-middle/tail availability side：没有足够证据。** W4 没有 authenticated listing-level exact coverage。`LOGIN_REQUIRED/page_shell` 不能证明商品在 AliExpress/Temu 不存在。

**Price spread side：完全没闭合。** 即使某件商品在美国渠道难搜到，也还要证明中国 current transaction price + freight + tariff + mandatory fee 后仍显著便宜；目前 `n=0`。

所以最准确的表述是：

> **Confirmed：China domestic head goods 的可审计样本真实存在。**  
> **Confirmed：全球 exact landed-price discovery 链存在明显缺口。**  
> **Unproven：这些商品系统性成为 US middle/tail 且形成足够大的正 landed spread。**

### 偶发还是结构性？

- **结构性的是“测量/发现摩擦”**：登录价、变体、动态优惠、仓后体积重、税则、平台访问、地区型号。
- **是否结构性地产生 ≥20%/≥30% 的消费者 surplus：未知。**
- 因此不能把 J4 的 “price-discovery failure” 偷换成 “arbitrage failure = profit pool”。

---

# G. Logistics Infrastructure Verdict

## Superbuy 能否作为基础设施？

**能，作为 pilot/轻资产路线的 operational infrastructure：YES。**

证据支持其具备采购、中国仓、合包、线路选择、国际发货等组件；BuckyDrop 又进一步验证 API/自动订单履约能力。Superbuy 公布普通 Taobao/Tmall/JD/1688 采购服务费为 0；免费 consolidation 也有依据。final-synthesis-evidence

**但作为已经证明的 economic moat / scale-rate infrastructure：NO EVIDENCE YET。**

公开证据没有：

- 1000 独立消费者包裹/月的 negotiated rate；
- 54 个 SKU 的 ZIP10001 actual quote；
- 完整 packed L×W×H；
- 完整 battery surcharge；
- SKU-level HTS/tariff/mandatory fee；
- 商务折扣 threshold。

R-W5 还发现 BuckyDrop 页面同时出现 CN¥9.90 fulfillment fee 和 Global Logistics flat CN¥9.9 service fee，页面没有说明两者关系，所以不能擅自单计或双计。final-synthesis-evidence

## 四种 shipping structure

| Structure | 已确认 | 未确认 | 裁决 |
|---|---|---|---|
| 1. Single-item standalone | 首重/续重、实重/体积重、电池影响线路是真机制 | **54/54 无 ZIP10001 quote-grade rate** | 可运行，经济未知 |
| 2. Same-consumer consolidation marginal | 免费合包存在；可能省重复首重 | 真正 marginal cost、体积重反转点未知 | 有潜力，不能量化 |
| 3. Commercial aggregation, 1000 independent consumer parcels | API/逐订单 fulfillment 操作可行 | **negotiated 1000-order rate = null** | 操作成立，折扣 thesis 未证 |
| 4. True physical bulk import | 大货/custom logistics 作为另一模式存在 | bulk freight + IOR + brokerage + US warehouse + pick/pack + last-mile 全成本未知 | 必须独立建模 |

**是否必须自己 aggregate/import？——不必须，至少在验证 thesis 阶段完全没有证据支持这样做。**

---

## Separate business architectures

| 架构 | Title/Inventory | Customs/IOR 暴露 | 产品合规/returns 暴露 | 当前证据下的结构判断 |
|---|---|---|---|---|
| A. Comparison / routing-only | 不持货 | 最低 | 最低 | **最轻、最合理的验证架构** |
| B. 用户跳转/通过 Superbuy 等自行购买 | 平台不持货 | 主要由实际交易链确定 | 较低 | 可行 |
| C. Platform acts as buying agent / checkout | 可代购但未必拿 title | 明显上升 | payment/fraud/returns 上升 | 可行但责任边界需合同化 |
| D. Commercially aggregated individual forwarding | 不必 physical aggregation | 每票 role/entry 要明确 | 中 | 操作上存在路径，rate 未证 |
| E. Platform becomes importer of record / bulk import | 高控制 | **高** | 高 | 在 economics 未证明前不合理 |
| F. Marketplace + US inventory | 持货/美国仓 | 高 | **最高**：seller/retailer/returns/inventory | 当前最不受证据支持 |

R-W6 的主要结论是：法律角色可拆分，没有找到“为了拿物流 volume rate 就必须拿 title 或成为 IOR”的规则；但真实合同、POA、entry 和 certification responsibility 不能由产品 UI 名称推断。final-synthesis-evidence

---

# H. Strongest 10 arguments AGAINST the thesis

1. **最核心：54 SKU 中 audited landed-savings 可计算数为 0。** 商业核心变量根本没有被测出来。
2. **0/54 当前中国普通 transaction price 最终 verified。** 甚至 landed equation 的第一项多数还没有 transaction-grade 输入。
3. **没有合法的 demand-weighted distribution。** 样本非概率、18 类定义重叠、W1 来源口径混杂。
4. **Ali/Temu exact coverage 未测，而不是已发现巨大空白。** 登录墙造成的 missingness 很可能夸大“美国没有”印象。
5. **2026 de-minimis suspension 和逐 SKU tariff/entry 成本是真实结构性逆风。**
6. **没有任何 1000-parcel negotiated rate。** “规模后物流便宜很多”仍是商业假设。
7. **体积重会重创 C10/C17 等大件，同时电池限制影响 C01/C02/C03/C06/C08/C11。**
8. **最大 GMV 类别往往也是兼容/退货/fitment 最麻烦类别**：手机、服饰、汽车、smart home、appliances。
9. **AliExpress 本身在持续内生化 arbitrage。** Alibaba 披露物流优化、成本效率和 AliExpress operating profit，是“spread 会被 incumbent 压缩”的强硬证据。
10. **完整链条的数据获取本身可能成本很高且脆弱**：动态登录价、coupon、CAPTCHA、variant identity、仓后 freight、税则变化都持续变化。

W8 独立 source audit 的最后裁决也是：这些机制足以显著压制 **broad thesis**，但没有足够证据把 narrow thesis 判死。final-synthesis-evidence

---

# I. Strongest 10 arguments FOR the thesis

1. **Domestic-first sample 真正冻结了。** 最难找海外对应的商品没有因为搜索失败而被删掉。
2. **国内供给面不是虚构的 long-tail 垃圾池。** 冻结样本中存在大量可核验国内 head/exact products。
3. **price discovery 链确实非常差。** 连经过大量人工研究后，exact current landed price 仍系统性闭合不了；这本身是产品问题。
4. **agent 采购层并非天然昂贵。** Superbuy 普通主流平台采购费可为 0，免费 consolidation 存在。
5. **不必先建仓/进口才能提供服务。** 现有 agent/fulfillment API 支持逐单操作。
6. **跨站 matching 技术不是 science project。** PriceDoge、1688 插件、AiPrice、2tao 等已存在。
7. **购物辅助产品可以规模化。** Capital One Shopping/Honey 等反驳“消费者不会使用购物助手”这种简单 bear。
8. **法规没有显示 routing-only 必须升级成 retailer/IOR。** 轻架构有真正的法律空间。
9. **W8 的 dedicated falsification 没有找到 narrow anomaly set 已消失的硬证据。**
10. **Incumbent coverage 很强 ≠ exact China-head convergence 已证明。** AliExpress 的全球规模和利润说明它是强竞争者，但没有回答冻结 54 SKU 的 exact-coverage/spread。

因此最强 bull case 不是：

> “中国显然便宜 30%。”

而是：

> **“现有消费者渠道没有可靠回答另一市场 exact SKU 的真实 delivered price；如果在修复这条链之后还能稳定找到净价差，thin router 会有价值。”**

---

# J. Why no dominant company exists today

这里严格区分证据层级。R-W7 明确要求：产品存在、失败事件和具体功能可以 Confirm；把它们解释成整个市场没有 dominant player 的总因果，多数只能 Probable/Speculative。final-synthesis-evidence

## Confirmed

| 原因/事件 | 能确认到什么 | 不能确认到什么 |
|---|---|---|
| **PriceDoge 项目没有完成 P2P** | 开发者明确提到用户不足 **和**开发时间不足 | 不能单因归结“市场无需求” |
| **HandHunt final freight 依赖入仓后实际重量尺寸** | landed price 在 browsing 阶段存在时序断点 | 不能证明该问题技术上不可解决 |
| **ezbuy 遭 Taobao 账户/仓库地址限制** | 上游平台 counterparty action 曾直接造成 buy-for-me service disruption | 不能证明所有 agent/router 必然被封 |
| **Alibaba/marketplace 数据访问存在许可/自动化约束** | robot/spider、登录、API permission 是实际工程边界 | 不能证明合法 API/合作不可能 |
| **Pandabuy 等发生诉讼/数据事件** | agent 模型存在集中运营/合规风险 | 不能直接否定 routing-only |
| **已有比价/匹配/agent 产品** | “没人尝试过”不成立 | 不代表目标产品已被充分竞争 |

## Probable

1. **链条过于碎片化。** Matching、authenticated price、warehouse measurements、freight、tariff、checkout、returns 分散在不同主体。
2. **真正价格不是一个静态字段。** 中国会员/券/补贴、海外 seller/warehouse、运费和关税都动态变化。
3. **国际需求出现后 incumbent 会主动压缩 spread。** AliExpress 是最明显机制。
4. **高 GMV 类目和高 routing-friction 有正相关倾向。** 手机频段、服饰退货、汽车 fitment、大件体积重等提高服务成本。
5. **neutral recommendation 与 affiliate/merchant monetization 存在潜在张力。** 有证据存在不同 monetization model，但“必然冲突”还没有被证明。

## Speculative — 不得升级成事实

- “美国消费者不信中国平台。”
- “消费者只在乎 next-day shipping。”
- “CAC 一定太高。”
- “affiliate 模式一定破坏中立性。”
- “法规本身已经杀死过这一精确 business model。”
- “现有小工具用户少，所以总市场就小。”
- “Amazon/Temu/AliExpress 已完全解决问题。”

---

# K. Decisive Unknowns

真正还会改变投资判断的只剩这些，不需要继续做泛泛 desk research：

### 1. 54-SKU transaction-grade landed spread

必须同时锁定：

`selected exact variant + seller + 中国普通当前成交价 + ZIP10001 cheapest-convenient comparator + packed L/W/H + packed weight + actual route quote + HTS + tariff/Chapter99 + mandatory fee + FX`

没有这张表，所有商业 verdict 都只能是 provisional。

### 2. Authenticated AliExpress / Temu exact coverage

要知道的是：

- exact SKU 是否存在；
- seller/stock；
- variant；
- US warehouse vs China ship；
- ordinary delivered price。

不是 Google 是否搜得到。

### 3. 可比的 US demand weights

必须建立 **不重叠、同年度、consumer-dollar、all-channel** taxonomy。不能再用 PCE、wholesale、shipment、Amazon keyword sales、market forecast 混合成权重。

### 4. 1000 个独立美国消费者包裹的真实 commercial rate

至少 Superbuy、BuckyDrop、Sugargoo/另一家各一份书面 quote。没有这个，commercial aggregation thesis 未测试。

### 5. True bulk import 的完整 incremental economics

进口、broker、MPF/HMF（如适用）、美国收货、仓储、pick/pack、last-mile 必须全部进来，不能拿中国→美国港价对比 DTC doorstep price。

### 6. Consumer behavior only after economics closes

如果真实净节省是 3%，消费者行为几乎无所谓；如果真实净节省稳定 30%，才值得测 latency tolerance、conversion、returns 和 repeat usage。因此 consumer experiment 应排在 transaction-economics 之后。

---

# L. Final Verdict

以下评级表示 **“基于当前冻结证据，是否值得把该命题当作已成立的决策前提”**。`Rejected` 不等于数学上证明永远不存在，而是“当前证据不足以继续当作成立前提”。

| Thesis / Business | Verdict | Confidence | Decisive evidence | Strongest counterargument | 什么数据会让我改判 |
|---|---|---:|---|---|---|
| **Broad thesis**：“中国国内 catalog 普遍存在巨大未套利价差” | **Rejected** | **0.88** | 0/54 audited landed observations；无 demand weights；AliExpress/物流/税制存在强套利压缩机制 | 当前数据是 missing，不是证明真实 spread 小 | 概率/需求加权 frozen sample 中出现稳定、大比例 ≥20–30% exact landed savings |
| **Narrow thesis**：“有足够大的 China-head / US-middle-tail anomaly set 可持续自动发现” | **Weak** | **0.72** | domestic-head side 存在，但 US coverage、spread、GMV 三者都未闭合 | dedicated falsification 也没证伪 narrow set；price-discovery failure 很真实 | 预注册样本中出现可重复的 exact anomaly，且有真实 GMV/demand weight |
| **Thin comparison/routing business** | **Moderate** | **0.78** | 最轻法规/资产结构；价格发现摩擦 confirmed；已有 matching/shopping-assistant demand precedent | monetization、coverage API、真实 savings pool 未证明 | 用完整 landed engine 在真实用户 query 上持续找到有意义 savings，并有点击/转化 |
| **Shopping agent / agent checkout** | **Weak** | **0.77** | 可借现有 agent infra，但一旦介入 checkout，payment/fraud/returns/customs role 上升；unit economics 未证 | Superbuy/BuckyDrop 已证明许多操作模块可以外包 | 真实订单 pilot 证明净节省在 agent fee/returns 后仍强，并明确 POA/IOR/contract chain |
| **Full marketplace business** | **Rejected** | **0.91** | 在核心 price-arbitrage economics 都未证明时，提前承担 marketplace、inventory、returns、seller/product compliance 没有证据基础 | 如果 narrow opportunity 后来极大，marketplace 可获得更多 margin/control | 先证明巨大 transaction volume、repeat demand，并证明库存/US fulfillment 显著提高全生命周期毛利 |
| **Logistics aggregation platform** | **Weak** | **0.84** | commercial aggregation 操作可行，但 negotiated rate 是完全缺失的关键变量；physical bulk 成本也未知 | 大规模订单确实可能带来私有 carrier economics，公开资料本来就未必披露 | 至少 2–3 家 provider 的书面 1000-parcel rate card + 与 standalone/current consolidation 对照 |
| **Physical bulk-import architecture** | **Rejected as starting architecture** | **0.93** | 增加 IOR、仓、inventory/handling、last mile，而没有已证明 spread 支撑 | 某些体积/固定费结构可能在足够规模后反而优于 DTC | 真正 all-in bulk quote 明显优于 individual forwarding，并有足够稳定 GMV 支持 |

### 一句话总裁决

> **这份研究没有证明“中国商品普遍便宜很多”，也没有证明“China-head / US-middle-tail 套利机会不存在”。它真正证明的是：当前 exact-SKU global landed-price discovery 非常差，而在修复这条数据链之前，任何关于套利规模、分位数、TAM 或 marketplace economics 的强结论都超出了证据。**

因此目前最合理的方向不是 full marketplace，也不是自建物流；是：

> **先把 thin routing / measurement layer 当作一个可证伪的研究产品，而不是把 price spread 当作已成立事实。**

---

# 核心来源 URL 与 evidence IDs

以下是最终判决中权重最高的外部来源；这里只列实际改变裁决的来源，而不是把全部 source ledger 再复制一次。

| Evidence IDs | 用途 | Explicit URL |
|---|---|---|
| `W1-A:C13/C16`, `R1-W1-A` | 美国消费需求锚点 | `https://fred.stlouisfed.org/release/tables?eid=44183&rid=53` |
| `W1-A:C13` | 汽车 aftermarket / marketplace demand | `https://www.autocare.org/data-and-information/market-research/joint-e-commerce-trends-and-outlook-forecast` |
| `W1-A:C10/C17` | housewares/small-appliance consumer dollars | `https://housewares.org/press-releases/second-annual-state-of-the-industry-report/` |
| `W5-A:C01-C04`, `R-W5:S01/S02` | Superbuy fee/consolidation/freight inputs | `https://www.superbuy.com/en/page/guide/feecomposition/` |
| `W5-A:C03/C04` | Superbuy freight calculator inputs | `https://login.superbuy.com/en/page/query/freight/` |
| `W5-A:C07`, `R-W5:S06` | BuckyDrop pricing/fulfillment | `https://www.buckydrop.com/en/services/pricing/` |
| `W5-C`, `R-W5` | BuckyDrop order/API workflow | `https://www.buckydrop.com/en/dropshipping/` |
| `W5/W8`, `R-W5/R-W8` | 2026 de-minimis suspension | `https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/` |
| `R-W5` | FY2027 customs user fees | `https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027` |
| `W5/W6/W8` | Section 301 SKU-specific lookup | `https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search` |
| `W8-A:C03`, `R-W8:R04/R05` | 2026 Section 301 action / exemptions | `https://ustr.gov/sites/default/files/files/Press/Releases/2026/FLIP%20301%20Investigation%20Final%20Action%20FRN%207-23-26%20FINAL.pdf` |
| `W8-C:C02`, `R-W8:R03` | CBP low-value entry/de-minimis operating environment | `https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0` |
| `W6`, `R-W8` | CPSC certification/eFiling boundary | `https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates` |
| `W7-A:C01`, `R-W7` | Prior Amazon/JD/Taobao comparison attempt | `https://github.com/DimensionDev/PriceDoge` |
| `W7-A:C02`, `R-W7` | HandHunt / warehouse-after-arrival freight limitation | `https://chromewebstore.google.com/detail/buy-from-china-handhunt/kkclaagbdmhkeaenndgfkbkbkfipfold` |
| `W7-A:C03`, `R-W7` | large shopping-assistant precedent | `https://chromewebstore.google.com/detail/capital-one-shopping-save/nenlahapcbofgnanklpelkaejcehkggg?gl=US&hl=en-US` |
| `W7`, `R-W7` | ezbuy platform restriction event | `https://www.acnnewswire.com/press-release/english/40224/media-statement%3A-ezbuy.sg---update-on-service-disruption` |
| `W7/W8`, `R-W7/R-W8` | Alibaba automated-access terms | `https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html` |
| `W8-C:C05`, `R-W8` | AliExpress logistics optimization / operating profit | `https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm` |

---

# If We Spend $10,000 on Research, What Should We Do Next?

目标不是再找 500 个网页例子，而是**把最大 uncertainty 转成 transaction-grade observations**。预算精确到 $10,000：

| 项目 | 预算 | 具体执行 | 能消掉的 uncertainty |
|---|---:|---|---|
| **1. 54-SKU 双端 authenticated recapture** | **$3,000** | 对已冻结 54 SKU，不换样；中国侧记录 seller/selected variant/普通价/会员价/券/补贴分栏；海外侧同步采 Amazon、AliExpress、Temu、品牌/专业零售商，目标 ZIP10001 | 当前价格 + exact coverage |
| **2. 12-SKU physical warehouse/ship pilot** | **$3,000** | 在看结果前按 demand × logistics strata 预注册抽 12 个 SKU；真实购买入 agent 仓，记录 packed weight、L/W/H、电池标签、可用线路、最终 freight quote | W5 最大未知：真实 freight/volumetric weight |
| **3. Licensed customs/broker HTS audit** | **$1,500** | 对上述 12 SKU 做 HTS10、origin、Chapter 99/301、豁免、entry mode、MPF/mandatory fee memo | tariff/fee 不再靠 proxy |
| **4. Commercial-rate RFP** | **$1,000** | 向 Superbuy、BuckyDrop、Sugargoo/另一家各索取约 **1,000 个独立美国消费者包裹/月** 的书面报价；另索一份 true-bulk 场景，明确两者不可混 | commercial aggregation 是否真的有规模经济 |
| **5. US demand crosswalk** | **$1,000** | 为 18 类建立同年度、不重叠、consumer-dollar taxonomy；购买必要的小型付费数据/人工 crosswalk；不能闭合的类别继续 NA | 合法 demand weights |
| **6. Independent QA / repeat snapshot** | **$500** | 第二研究员复核 exact identity，并在预定时间再次抓价格，检查 promotion/date sensitivity；所有 null 原样保留 | 防止又被 variant/promo/stale-price 污染 |

**总计：$10,000。**

## 预注册规则

这轮实验开始前必须锁定：

1. 54 SKU 不因海外找不到而删除。
2. 12 个 physical pilot SKU 在看到最终 spread 前确定。
3. 所有 `LOGIN_REQUIRED / blocked / unavailable / variant mismatch` 分开编码。
4. 普通价、会员价、coupon、国补绝不混。
5. comparator 必须记录 Amazon 和 **cheapest convenient overseas** 两套。
6. 四种 shipping structures 独立计算。
7. 任何重量、运费、税率、brokerage 缺失则 landed cost 保持 `null`。
8. **只有实际 complete landed observations 才进入 mean/median/P10/P25/P50/P75/P90 和 ≥10/20/30/40/50% 统计。**
9. Demand-weighted distribution 只有在 common-dollar weights 真正闭合后才发布。
10. 在看数据前写下 change-of-mind threshold，避免结果出来后重新定义“成功”。

### 这 $10,000 最有价值的最终产物

不是另一篇长报告，而是一张 54 行、能逐格审计的 transaction ledger。只要它能把足够多行从：

`domestic price = null / overseas exact = unknown / freight = null / HTS = null`

推进到：

`exact CN checkout + exact overseas delivered + packed dimensions + freight + tariff + mandatory fee = final landed cost`

那么下一轮才第一次有资格回答这项研究最初真正的问题：**中国国内 head catalog 中，到底有多大一块消费者支出能够产生可实现、可持续、足以补偿等待和风险的净价格优势。**