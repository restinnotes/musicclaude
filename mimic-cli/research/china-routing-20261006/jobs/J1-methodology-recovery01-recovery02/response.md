## J1-methodology-recovery01-recovery02 独立裁决

**INPUT_COMPLETE。** 我已逐份检查证据包中的 24 份完整研究报告及全部 25 份独立 mg source audit；以下只采用审计等级，不把研究员自报 `VERIFIED` 当事实，也不做多数票、引用计数或不同卖家/不同时间价格平均。证据包本身仍标记 `sample_frozen=false`：`C17-S01/C17-S02` 虽已有国内 item_id 与精确容量/颜色/bundle，但制造商 model number 未观察到。judge-evidence-pack

### 1. 选择/幸存者/样本泄漏

**裁决：没有发现“看到海外价后删掉难匹配 SKU”的 post-freeze survivorship/sample leakage；但存在明确的选择偏差，不能向总体外推。置信度：高。** Coordinator 明写 intended population 是“18 类中有国内证据的候选”，且 **not a probability sample**、GMV 权重缺失；W3/W4 三个 replicate 均保留 54/54 行，审计后的 exact-price comparison 全为 0、verified-landed-savings 全为 0。judge-evidence-pack W2/R2 的实际选样又按 `rank+exact → purchase+exact → model-only`、再字典序决胜；访问稳定、榜页能闭合精确版本的商品因此更容易进入冻结集合。R2-batch06 还显示动态换榜会把 W2-A 的安踏候选从原 TOP 位降级，而其他可重现榜位的 SKU 被保留。judge-evidence-pack

这意味着**内部盲化基本守住，但外部代表性没有建立**：不能报告“多少中国头部商品具有某价差”的 population prevalence、GMV-weighted share 或需求加权分布。反证是各 W3/W4 确实没有因海外不可读而删行，因此问题不是后验删样，而是 sampling frame 本身依赖“国内可审计性”。改变此结论的最低证据：预先固定完整候选框及抽取概率/独立 demand weights，保存 freeze-time 榜单快照，并让不可读候选以原抽样概率留在分母，而不是由 auditability 决定入选。

### 2. 版本与价格绑定错误足以否决若干“exact price”观察

**C01-S02 — `R3-batch01 / W3-*:C01-S02`，sources `S03,S05`：CORRECTION_REQUIRED。** `$1628` 是未选择 Silver+256GB 的 parent-listing 价格，且配送上下文是 ZIP50307，不是 ZIP10001；必须置 `overseas exact price=null`。judge-evidence-pack

**C04-S03 SER8 — R3-batch02：** 国内是深空灰 **barebone**，美国官方 `$619` 是 **16GB+512GB、US adapter**，不能作 exact 对价。**C12-S03 — `W3-B-batch04:observation:C12-S03`, source `S12`：CORRECTION_REQUIRED**，¥1898 没有同时绑定“灵动白+64GB+标准套”，当时激活购物车反而是星曜黑64GB摩托套 ¥1988。judge-evidence-pack judge-evidence-pack

**C17-S01 — R4-batch06 sources `S04,S13,S19,S27`：** Temu 线索是 **45L×3**，冻结 SKU 是 CHAHUA **34L×3 奶黄色**，不能升 exact/OEM。**C18-S02** 的冰箱贴也不能替代冻结的 CRYBABY 毛绒挂件。judge-evidence-pack

最低修复：交易页必须把 **item/seller + 容量/颜色/尺码/bundle/地区硬件 + 当前价格 + 目的地** 同时锁在一个观察状态；OEM/B 桶则另需制造商料号或强 OEM 证据。

### 3. 登录态偏差：最严重的覆盖误判风险

W4 的核心“没有可用 offer”可保留，但 **`BLOCKED/page_shell/LOGIN_REQUIRED ≠ unavailable`**。例如 R4-batch02 将 Temu 重分类为 page_shell，AliExpress 为 blocked/unverified；R4-batch06 更明确：9 个 AliExpress US 搜索均为 `LOGIN_REQUIRED`，没有一个可升级为 `VERIFIED_UNAVAILABLE`。judge-evidence-pack judge-evidence-pack

同样的偏差存在于中国价格端：R2 明确只记录公开数值标价，会员、88VIP、定向券、国补和“登录查看到手价”全部留 null。judge-evidence-pack 因此不能把匿名状态价格当“消费者实际买价”，也不能把登录墙导致的海外缺失当成“中国有、美国没有”。最低修复是同一 SKU 在预定义的 logged-out 与 authenticated 状态各做一次时间同步观察，并保存优惠资格、账户条件和 ZIP。

### 4. 陈旧价格与促销污染存在实质纠正

**C05-S01 / `W3-B-batch02:A_bucket_overseas_item_price_observations=2`：CORRECTION_REQUIRED，sources `S08,S11`。** Samsung `MZ-V9S2T0BW` 的 `$497.22` 页面于 **2026-09-30 已结束**，不能作为 10 月 6 日当前价；审计所见 `$474.15` 是另一时点，**二者绝不能平均**。judge-evidence-pack

**C10-S03 / `W3-A-batch04:K04`, source `S02`：CORRECTION_REQUIRED。** 同一 eBay item 的旧 `$2051.52/ZIP78228` 已被审计时 `$1895.65/ZIP50307` 取代；仍是 White/220V/South Korea 的 C 桶观察，不能与国内 ROMO P ¥3699 构成 exact landed comparison，也不得平均两个快照。judge-evidence-pack

补贴也必须隔离：W3-C 已明确把带“国家补贴”的 C02-S01/S02 与普通非补贴价分开；R2-batch04 对 Ace Pro 2 的 ¥2798 因“地区补贴15%+登录到手价”只列未分类展示价。最低修复是同日、同变体、非会员普通价与各类 coupon/subsidy 分栏留痕。

### 5. Freight/tariff：当前唯一可接受结论是“不可计算”，不是“节省为零”

三份 W3 的 coordinator 结果都是 **usable exact price comparison=0，verified landed savings=0 个可计算观察**；这不是 savings=0。真实 packed weight/L×W×H、线路、电池附加费、agent fee、国际运费、HTS/301、mandatory customs 等任一缺失均不能填 0。R3-batch05再次明确四种物流结构全部没有完整真实报价。judge-evidence-pack

具体费用还有两处必须修正。`W5-A:C13` 被 coordinator 判 **CORRECTION_REQUIRED**：报告用了旧 FY2026 MPF，10月6日已进入 FY2027，source `S11`。`W5-A:C07` 与 `W5-C:C07` 同为 **CORRECTION_REQUIRED**：BuckyDrop 页面分别列 CN¥9.90 fulfillment fee 和 flat CN¥9.9 logistics service fee，公开材料没有说明二者是否同一笔，因此既不能擅自只算一次，也不能武断双计。`W5-C:C01` 还需时间修正：特定邮政 HTS10/数量重量字段的合规日是 **2026-10-22**，不能提前到 10 月 6 日。judge-evidence-pack R-W6 同时确认 tariff stack 必须逐 SKU 按 HTS10、origin、entry date、Chapter 99/301/232/豁免映射，不能采用一个 blanket “China tax %”。judge-evidence-pack

**最终方法学裁决：目前证据足以支持“样本中尚无可审计的 verified landed-savings 估计”，但不支持“中国直购无价差”、也不支持“Temu/AliExpress 无货”，更不支持将该非概率、可审计性驱动的冻结样本外推成市场机会比例。** 要改变这一裁决，最低限度需要：修复 C17 两条冻结身份；独立概率/需求权重；同日 exact variant 双端交易价；登录态/券/补贴分层；ZIP10001 实际报价与 packed dimensions；逐 SKU HTS/税费/entry-mode 链。

## 输入完整性表

| Research job | report SHA256 | 我实际检查到的报告特定发现/分歧 |
|---|---|---|
| W1-A | `c8c930872433332d7a83a7231bcdb7447b68bf6d5e0f9e0b8bd698b76b8e7bfb` | 报告拒绝把异口径市场量硬排成统一 18 类 GMV；R1 审计进一步要求 C07/C09/C10/C17 实质修正、C02 保持冲突。judge-evidence-pack |
| W1-B | `a6474c4aa74cce05b3f17ac17423941223bd83b9b6b7360e34839ee75702a1d1` | R1 审计判 4 个 claim `CORRECTION_REQUIRED`；例如 C06 的 65% 是 True Wireless dollar share，不是 Bluetooth share；C11 两个 power-tools 数值禁止平均。judge-evidence-pack |
| W1-C | `489e916b8e9646e4317a6db3d9ae052966d673c8c8dd9777edef9c1346da34ba` | continuation 曾把 CIPA 错写为只到 June；审计确认 10/1 已有 August，同时再次禁止把 shipment 当 consumer GMV。judge-evidence-pack |
| W2-A | `046f9bb84061977ebf1eb89b3f89c6b6337f0359d453e9c18d8860fbf059c024` | 明确不得因海外价格/可得性删除候选；无法核验当前成交价时留空。judge-evidence-pack |
| W2-B | `2182ad02c9f58435c88b974e1de064cbcb5a6c02fc01f9868229aa33b9cca532` | 公开页价格与登录后到手价分离；KINGBANK ¥3499 是公开标价而非最终成交价。judge-evidence-pack |
| W2-C | `5994f7cefe60ef7d53b913d217c1162ce4cfa85fce25fcf630246b1b41c47e62` | 52TOYS ¥168 明确只作报道首发价，不能当 2026-10-06 当前价。judge-evidence-pack |
| W3-A | `4f22acab532a65f7392a4212411ec872d3020edfff3edb76aca52c469e38868b` | 9/9 保留；只有4个干净普通公开价，四种物流结构均无完整报价，landed savings n=0。judge-evidence-pack |
| W3-B | `a00c62dbca6c1950c57060753e2fd19f80a4d5364c4d4a1debbce82395961ef5` | 不为“容易找到海外价”换样；虽有若干 C 桶价格观察，A/B 和 ZIP10001 完整端点仍为0。judge-evidence-pack |
| W3-C | `e440304de201a8f93fd4e211eea560e2ef591999d85095bc90b9f6cb4027ca36` | C02 两项展示价带国补标签，不能升级普通非补贴价；9/9 landed 均不完整。judge-evidence-pack |
| W4-A | `39bcd589d0b450a5e187b5d0632dd1edcdc8413733e0ab50664daa04c36e1bc3` | 报告把大量访问状态记 BLOCKED；后续审计确认 Temu 更准确是 page_shell，不可解释为无货。judge-evidence-pack |
| W4-B | `525c6379ac871ac8ecc3806dbcb46d1b52c36248a9d9ac01136e020bf03c60b3` | 17 BLOCKED + 1 LOGIN_REQUIRED；报告自身已说明这是研究访问缺失率，不是市场无货率。judge-evidence-pack |
| W4-C | `633e5e642b1c31ec6bf043344cecf2e10161b936d1698b7e3deaa18d05a48fed` | 明确要求 LOGIN_REQUIRED/BLOCKED 继续保留且不重选 SKU；其计数不得解释为市场覆盖率。judge-evidence-pack |
| W5-A | `c68db3699dddd62da8b3c8a66455bf385a1983d7e222fb56335b855856ff68f6` | “1000 单有商务折扣”未获公开阶梯价；54/54 没有 ZIP10001 quote-grade 运费。judge-evidence-pack |
| W5-B | `f684b48ecbd1594400d5663dcc12027a44082e698cc8b1351a1890316b10fd37` | 1000 个独立订单在操作上可行不等于已证明 freight discount；0/54 quote-grade。judge-evidence-pack |
| W5-C | `cc295668c9ea0c7fe24c84943411a91e0a7e2dd0c96d19f406733afaaf2ff48d` | 美国公开 parcel 样本缺 ZIP/LWH/商品限制/税费，只是 observation，不能作为 ZIP10001 quote。judge-evidence-pack |
| W6-A | `1b958a99991c685ebe774ffee0c7d4e319adb0fc2c4e862eacd0418ecfb669c0` | 明确不能继续采用旧 <$800 de-minimis 经济模型。judge-evidence-pack |
| W6-B | `20090bcef53c54b0f1c22e4c329ba2ecade652c93db347be1187ece6c5100d19` | owner/purchaser、broker、IOR 等角色必须依合同/entry 判断；不能由“agent”标签推定。judge-evidence-pack |
| W6-C | `0b194b34f17487cd2df7d90f75bfbb4f5821523fa2db44cc8f48e21583b8977f` | ordinary commercial low-value 不能依赖旧 §321 默认免税；HTS10/IOR 等仍需逐单闭合。judge-evidence-pack |
| W7-A | `a9e71cf2a984b1df88850b7c96eb290b6160bef4c66c2219c627e84afbd41554` | PriceDoge/HandHunt 证明“没人做过”错误；HandHunt 最终运费仍须入仓实测后确定。judge-evidence-pack |
| W7-B | `857b295ebf977c999388e67eec0fb90b59661ba0703999909b17d2a5e734aaa0` | GP/IK 等微型工具有少量用户；低用户数不能独立证明消费者需求失败。judge-evidence-pack |
| W7-C | `91e96c5b6e7375091ae9b4c817b83d270d1f9a3038c310021f9250c66c87ca56` | PriceDoge 用户不足同时伴随开发者时间不足；优惠券/满减等使“真实价格”困难，因果不能单归需求。judge-evidence-pack |
| W8-A | `6e0b859334d4da5c0b82c715b772d6d4364f0a45a1f31dbe3c5692405a457042` | 结构证据能攻击 broad thesis，但没有冻结 SKU landed 数据，不能否定 narrow thesis。judge-evidence-pack |
| W8-B | `56a438d4c0253df9918fe41cb13f1a001c189b329bf67519e41e4286467684d8` | 明确指出部分邮政合规条款到 2026-10-22 才到期；在 10-06 提前视为当前摩擦会产生时间偏差。judge-evidence-pack |
| W8-C | `a6eea15a627e8223d526626546ae0713f9e512ce44d8c5708a9bf2f33babab4c` | 严守 pre-freeze、不查具体海外 SKU；结论仅是 broad thesis 受压、narrow thesis 未决。judge-evidence-pack |