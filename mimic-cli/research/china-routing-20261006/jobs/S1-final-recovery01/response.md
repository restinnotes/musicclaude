以下是按 `final-repair01-evidence.txt` 封闭证据重建的完整修订版。当前附件已重新机械校验，SHA256 为 `ede1d0384065773b13b84b7d61a6ed682b04d5cf4bb0aa0067e1718f7809bee0`；本报告不引入任何附件外市场事实，不修改或删除冻结 SKU。

# China Domestic → US Consumer Routing Research
## S1-final-recovery01 — 完整最终修订报告

**证据截止日：2026-10-06**  
**研究模式：封闭证据 adjudication；无新增网页研究**  
**当前修订附件 SHA256：`ede1d0384065773b13b84b7d61a6ed682b04d5cf4bb0aa0067e1718f7809bee0`**

---

# 0. Executive Adjudication

本轮修订后的核心结论比上一版更窄，也更可靠：

**第一，现有证据确认的是本研究中的 measurement / access / transaction-chain failure，而不是已经确认的普通消费者或全球 price-discovery failure。** 在冻结 SKU 上，本研究反复无法同时闭合：中国普通当前成交价、精确海外版本、登录态 seller/stock/warehouse、ZIP10001 delivered price、packed dimensions/weight、真实国际运费、逐 SKU HTS/Chapter 99/301、mandatory fees 与 FX。Temu/AliExpress 又大量出现 `page_shell`、`login_required`、`blocked` 或 `not_observed`。这些足以证明**本研究证据链的测量与访问失败**，但不能自动推出“普通消费者在全球市场也无法发现价格”或“市场本身失灵”。最终终审正是因为上一版仍跨越了这条边界而拒收。:chatgpt-content-reference{index="0"}

**第二，盈利 anomaly set 仍未证明。** 在冻结 54 SKU 上，W3-A/B/C 每个独立 replicate 都保留完整 54 行，但 audited usable exact-price comparison 均为 0，verified landed-savings observation 均为 0。这意味着当前无法计算 mean、median、P10/P25/P50/P75/P90，也无法计算节省 ≥10/20/30/40/50% 的比例。这里的 `n=0` 是“没有可计算 observation”，绝不是“平均节省 0%”。:chatgpt-content-reference{index="1"}

**第三，China-head 这一半有真实证据；US-middle-tail 与经济价差这一半没有闭合。** 冻结 54 个物理 SKU 后，36 个 domestic-head slots 中有 32 个 verified-head，4 个是 fallback/unverified head slots；另有 18 个预注册 `domestic_opportunity` SKU。这个抽样足以证明研究不是从国际化 SKU 反向挑选，但它不是概率样本，也不能用于估算 China-head 商品中“多少比例”形成 profitable US anomaly。

**第四，AliExpress/Temu coverage 仍不可量化。** W4 三个 replicate 各自都是全 54 行 logical replicate；source audit 后没有可发布的 exact coverage rate。旧的 W4-B “17 blocked + 1 login-required”是原研究过程中的访问态汇总，不再作为最终数字。最终状态必须按 batch/channel 分别记 `page_shell / login_required / blocked / not_observed`；没有可靠全量审计计数的地方保持 `NA`。

**第五，Superbuy/类似 buying-agent infrastructure 可以支持一次轻资产 transaction-grade pilot，但没有证据证明 1000 个独立美国消费者包裹/月已经存在某个可量化的规模运费折扣。** “商业订单聚合可以不等于物理合包”是可支持的；“因此一定取得某个 freight discount”则未证明。

**第六，重新裁决后：Broad thesis = Rejected；Narrow anomaly thesis = Weak；Thin routing = Weak。** Thin routing 从上一版的 Moderate 降为 Weak，原因不是发现了新的负面市场事实，而是删除了一个原本不合法的正面前提——“global/consumer price-discovery failure 已确认”。Shopping agent = Weak；Full marketplace = Rejected；Logistics aggregation platform = Weak。

---

# 1. 证据工件身份与 hash 解释

## 1.1 三个不同工件，不得把 hash 混为一谈

| 工件 | 作用 | SHA256 / 状态 | 正确解释 |
|---|---|---|---|
| `judge-evidence-pack.txt` | 四名独立 judge 的共同封闭输入 | `0912ea224a51feb4b5bd0cc1e3a04346a5990f71e8856bc3de00d91c7b3635d4` | J1/J2/J3/J4 读的是**同一个** judge evidence pack；不是“读错了文件” |
| `final-synthesis-evidence.txt` | 上一版 synthesizer 的更大输入，包含 brief + research + judge material | `2be95283fa0dd89ba6dc026cea8642e5c2766fe45fbc1fe0e47f10ae052db4c2`，上游声明 70,663 行 | 这是**另一个文件**。当前修订附件只嵌入其 manifest/声明，因此本轮不能对原始上游 bytes 独立重算该 hash；这是 honest data gap，不是 judge input 错误 |
| `final-repair01-evidence.txt` | 本次修订容器：原始 brief、冻结工件、完整研究/审计、4 judge、上一版、最终终审 | `ede1d0384065773b13b84b7d61a6ed682b04d5cf4bb0aa0067e1718f7809bee0` | 本轮实际输入；已重新机械校验 |

四 judge 的共同输入与上一版 synthesis 输入 hash 不同，是因为**文件本来就不同**。最终质量审计也明确把上游 `final-synthesis-evidence.txt` 无法在当前 Q 容器中独立 rehash 记为 honest data gap，而不是说 judge 使用了错误文件。:chatgpt-content-reference{index="2"}

另外，SHA256 是**字节级** hash。Windows 原文件的 CRLF bytes 与将同一文本规范化为 LF 后的 bytes 是不同字节流，即便肉眼文本相同也通常产生不同 SHA256。因此本报告只比较“同一工件、同一 byte representation”的 hash；不把 LF 文本 hash 与 Windows CRLF 原文件 byte hash 混为一条身份链。

---

# 2. 24 份研究报告：具体检查完整性表

24 个顶层 research report 恰好是 W1-A 到 W8-C。W3/W4 内部的六个 9-SKU execution batch 是一个 A/B/C logical replicate 的拆分，**不是额外独立研究报告，也不能把三个 replicate 重复的 54 SKU 相加成 162 个独立 SKU**。机械 denominator 记录确认每个 replicate 都是 54/54 observed-or-missing rows。:chatgpt-content-reference{index="3"}

| Report | SHA256 | 本次实际检查的决定性内容 | 完整性 |
|---|---|---|---|
| W1-A | `c8c930872433332d7a83a7231bcdb7447b68bf6d5e0f9e0b8bd698b76b8e7bfb` | 不支持把 PCE、tracking、wholesale、shipment、forecast 等异口径数值拼成统一 18 类精确 GMV；laptop 金额存在未解决冲突 | 完整已检查 |
| W1-B | `a6474c4aa74cce05b3f17ac17423941223bd83b9b6b7360e34839ee75702a1d1` | 原“需求权重”混入 online share、incidence、fragmentation、growth，不可称 consumer-dollar demand weight；部分 category claim 被 R1 要求修正 | 完整已检查 |
| W1-C | `489e916b8e9646e4317a6db3d9ae052966d673c8c8dd9777edef9c1346da34ba` | 含原 partial 与 continuation；仍只计一个独立 W1-C；shipments 不能改称 consumer spend；CIPA 时点被审计校正 | 完整；continuation 不另算 replicate |
| W2-A | `046f9bb84061977ebf1eb89b3f89c6b6337f0359d453e9c18d8860fbf059c024` | domestic-first；不得因海外难找换 SKU；当前成交价无法核实时保持 null | 完整已检查 |
| W2-B | `2182ad02c9f58435c88b974e1de064cbcb5a6c02fc01f9868229aa33b9cca532` | 公开标价与登录后到手价分离；例如 KINGBANK 公开价不能冒充最终 transaction price | 完整已检查 |
| W2-C | `5994f7cefe60ef7d53b913d217c1162ce4cfa85fce25fcf630246b1b41c47e62` | 国内消费者/榜单证据可用于抽样，不自动等于销量/份额；历史首发价不能升级为 2026-10-06 当前价 | 完整已检查 |
| W3-A | `4f22acab532a65f7392a4212411ec872d3020edfff3edb76aca52c469e38868b` | 54 行完整；公开端只有局部价格；四 shipping structure 均未闭合；usable landed n=0 | 完整 logical replicate |
| W3-B | `a00c62dbca6c1950c57060753e2fd19f80a4d5364c4d4a1debbce82395961ef5` | 有若干海外 comparable 价格线索，但 exact/OEM 与 ZIP10001 完整端点仍未闭合；不换样 | 完整 logical replicate |
| W3-C | `e440304de201a8f93fd4e211eea560e2ef591999d85095bc90b9f6cb4027ca36` | 补贴、selector、variant、region 问题得到保留；9/9 batch 内 landed 不完整，整体 replicate 仍 54 行 | 完整 logical replicate |
| W4-A | `39bcd589d0b450a5e187b5d0632dd1edcdc8413733e0ab50664daa04c36e1bc3` | 原报告大量写 BLOCKED；source audit 后 Temu 多数应更准确记为 page_shell；不能等同无货 | 完整；访问态经审计重编码 |
| W4-B | `525c6379ac871ac8ecc3806dbcb46d1b52c36248a9d9ac01136e020bf03c60b3` | 原始 “17 BLOCKED + 1 LOGIN_REQUIRED”仅是研究访问缺失，不是 coverage；最终报告废弃这个汇总数字 | 完整；旧最终计数被推翻 |
| W4-C | `633e5e642b1c31ec6bf043344cecf2e10161b936d1698b7e3deaa18d05a48fed` | 已明确 blocked/login required 要继续留在分母且不能重选 SKU；仍没有可审计 exact coverage rate | 完整 logical replicate |
| W5-A | `c68db3699dddd62da8b3c8a66455bf385a1983d7e222fb56335b855856ff68f6` | Superbuy 等公开服务结构可核；未获得 1000 independent parcels/月真实阶梯价；54/54 无 quote-grade ZIP10001 freight | 完整已检查 |
| W5-B | `f684b48ecbd1594400d5663dcc12027a44082e698cc8b1351a1890316b10fd37` | operational scalability ≠ proven freight discount；缺 packed dimensions/route/quote | 完整已检查 |
| W5-C | `cc295668c9ea0c7fe24c84943411a91e0a7e2dd0c96d19f406733afaaf2ff48d` | API/逐单履约支持“商业订单聚合≠物理合包”；不能由此推断已存在特定运费折扣 | 完整已检查 |
| W6-A | `1b958a99991c685ebe774ffee0c7d4e319adb0fc2c4e862eacd0418ecfb669c0` | 旧 <$800 de-minimis economics 不能用于 2026 当前模型 | 完整已检查 |
| W6-B | `20090bcef53c54b0f1c22e4c329ba2ecade652c93db347be1187ece6c5100d19` | purchaser/importer/broker/IOR 必须按合同和 entry 结构判断，不能由“agent”标签推定 | 完整已检查 |
| W6-C | `0b194b34f17487cd2df7d90f75bfbb4f5821523fa2db44cc8f48e21583b8977f` | routing/agent 架构并非自动等于 importer；但逐 SKU HTS/301/其他 duty/IOR 仍需闭合 | 完整已检查 |
| W7-A | `a9e71cf2a984b1df88850b7c96eb290b6160bef4c66c2219c627e84afbd41554` | PriceDoge/HandHunt 证明“没人尝试过”错误；HandHunt 也展示入仓后才知最终 freight 的 timing problem | 完整已检查 |
| W7-B | `857b295ebf977c999388e67eec0fb90b59661ba0703999909b17d2a5e734aaa0` | 小型工具存在有限用户；低用户数本身不能证明目标市场需求失败 | 完整已检查 |
| W7-C | `91e96c5b6e7375091ae9b4c817b83d270d1f9a3038c310021f9250c66c87ca56` | 优惠券/满减/登录态令“真实价格”困难；PriceDoge 未完成也混有开发者时间约束，不能单归因需求 | 完整已检查 |
| W8-A | `6e0b859334d4da5c0b82c715b772d6d4364f0a45a1f31dbe3c5692405a457042` | 对 broad thesis 有结构性反证；但没有冻结 SKU landed 数据，不能借此证明 narrow anomaly set 不存在 | 完整已检查 |
| W8-B | `56a438d4c0253df9918fe41cb13f1a001c189b329bf67519e41e4286467684d8` | 当前法规/物流摩擦显著；同时校正“2026-10-22 才生效”的规则不能提前当作 10-06 当前约束 | 完整已检查 |
| W8-C | `a6eea15a627e8223d526626546ae0713f9e512ce44d8c5708a9bf2f33babab4c` | 严守 pre-freeze；对 incumbent 压缩 spread 有理论/结构反证，但 narrow frozen set 仍 unresolved | 完整已检查 |

---

# 3. 25 份独立 source audit 完整性

25 个顶层 source-audit job 为：

| 组 | Audit jobs | 数量 | 状态 |
|---|---|---:|---|
| W1 | `R1-W1-A`, `R1-W1-B`, `R1-W1-C` | 3 | 3/3 完整 |
| W2 | `R2-domestic-batch01` … `batch06` | 6 | 6/6 完整 |
| W5-W8 | `R-W5-sources`, `R-W6-sources`, `R-W7-sources`, `R-W8-sources` | 4 | 4/4 完整 |
| W3 | `R3-batch01` … `batch06` | 6 | 6/6 完整 |
| W4 | `R4-batch01` … `batch06` | 6 | 6/6 完整 |
| **总计** |  | **25** | **25/25** |

R2-batch01 内部出现的 recovery/category 子任务属于该 source-audit job 的内部追查，不另冒充独立第 26、27…份 audit。

---

# 4. 四个独立 judge：具体检查完整性表

四名 judge 都读同一 `judge-evidence-pack.txt`（SHA `0912...`），response hash 各不相同。四份裁判完整存在并被检查。:chatgpt-content-reference{index="4"}

| Judge | 主要有效裁决 | 本次需要纠正/限定的部分 | 最终处理 |
|---|---|---|---|
| J1 Methodology | 非概率/可审计性驱动 sampling 不能总体外推；variant mismatch、stale price、coupon contamination、blocked≠unavailable；`n=0` 不是 savings=0 | 使用了 evidence pack 顶部的 prefreeze `sample_frozen=false` 叙述 | 保留方法学结论；以稍后 immutable 54-SKU freeze 为当前冻结状态，C17 model-null 作为正交缺口保留 |
| J2 Economic | demand weights 不合法；当前 unit economics 无正/负可验证结论；commercial aggregation 与 physical bulk import 必须分开；1000-parcel rate 未证明 | 同样受 prefreeze 身份叙述影响的地方不作为最终 freeze 状态 | 保留经济裁决；冻结身份由最终 mechanical artifact 覆盖 |
| J3 Adversarial Bear | “足够大的市场没有被证明”；当前证据不足以把 narrow thesis 当投资前提 | 不能把“未证明”写成“市场很小/为零” | 最终写成 Narrow = Weak、未证明；不声称已证伪真实市场 |
| J4 Adversarial Bull | 跨站 exact matching、agent logistics、动态 transaction data 形成真实工程难题；历史上存在相关产品尝试 | 将这些扩大成“confirmed global consumer price-discovery failure”越界 | 核心范围改为 **Confirmed research measurement/access/transaction-chain failure**；普通消费者/global failure = Unproven |

---

# 5. 七项 material fixes 处理索引

终审 `accepted=false` 的七项 material fixes 已全部进入正文，而不是以勘误形式附加。:chatgpt-content-reference{index="5"}

| # | Material fix | 本版处理位置 | 状态 |
|---|---|---|---|
| 1 | 删除“confirmed global/consumer price-discovery failure”越界；重判 Narrow/Thin | A、B、F、I、L | **已落实；Thin 降为 Weak** |
| 2 | Demand-weighted / Feasibility-weighted / Opportunity-seeking 三分 | E1-E3 | **已落实；合法权重不足即 NA** |
| 3 | 36 head slots 显式拆 32 verified + 4 fallback；另18 opportunity；C14-S03/C17 flags 正交 | §7、D | **已落实** |
| 4 | research replicate A/B/C 与 match bucket A/B/C 完全分开，最终按桶列表 | E4 | **已落实** |
| 5 | 删除 W4-B `17 blocked + 1 login-required` 最终计数 | E5 | **已落实；改为 batch/channel 状态，整体 count=NA** |
| 6 | 删除未经校准的 0.xx confidence | 全文、L | **已落实；仅高/中/低定性 confidence** |
| 7 | 增加 metric → source-audit → SKU/denominator artifact 追溯索引 | §21 | **已落实** |

---

# 6. 本报告的 confidence 语言

不再使用 `0.88 / 0.72 / 0.78 / ...` 等伪精确小数。

- **高**：结论直接来自多份独立 audit 或机械工件，且结论本身主要是“证据状态/方法边界”，不是对缺失市场变量的猜测。
- **中**：证据方向一致，但至少一个足以改判的 transaction-level 变量仍缺失。
- **低**：主要依赖间接证据或尚未执行的市场/消费者实验。

这不是临时数值 rubric，也不试图把定性词映射成概率。

---

# 7. 冻结样本与正交身份质量

原始 brief 要求 **China domestic first → freeze → only then inspect overseas**，并明确“海外找不到”不能成为 exclusion reason。:chatgpt-content-reference{index="6"}

## 7.1 物理 SKU 分母

**总物理 SKU = 54。任何下列质量标签都不能新增、删除或互换物理 SKU。**

| Sampling stratum | 数量 | 含义 |
|---|---:|---|
| Domestic-head slots | 36 | 每类 2 个预注册 head slot |
| └ Verified-head | **32** | 头部证据在最终 audit 中闭合 |
| └ Fallback / unverified-head | **4** | `C07-S02`, `C14-S01`, `C14-S02`, `C15-S02` |
| Domestic-opportunity | **18** | 每类 1 个预注册 opportunity SKU |
| **总计** | **54** | 18 类 × 3 |

这 18 个 `domestic_opportunity` 是一个**预注册 sampling stratum**，不是 feasibility weights。

## 7.2 正交身份质量标记

- `C14-S03`：`PROVISIONAL_VARIANT`；属于既有 54 个物理 SKU 之一。它不新增 SKU，也不从 denominator 删除；exact-variant quality 单独为 provisional。
- `C17-S01`、`C17-S02`：manufacturer model number 仍为 `null`，但已有国内 item_id 与精确容量/颜色/bundle 身份。model-null 是正交 identity-quality flag，不能把这两行删除，也不能把它们换成其他 SKU。
- 最终冻结层面：**53/54 exact_variant_verified；1/54 provisional variant。**
- 这与 `32/36 verified-head` 是两套不同维度，不能互换分母。

## 7.3 Current transaction price

冻结工件中 **0/54** 行达到 `current_transaction_price_verified=true`。有些行有公开 list price、历史发布价或官方标价，但这些不能自动升级为 2026-10-06 普通消费者当前 transaction price。

---

# 8. “A/B/C”必须有两个完全不同的含义

## 8.1 Research replicate A/B/C

这是研究独立性：

- W3-A / W3-B / W3-C：三次独立 price-spread research replicate。
- W4-A / W4-B / W4-C：三次独立 coverage research replicate。
- 每个 replicate 的 logical denominator 都是完整 **54 SKU**。
- 每个 replicate 的六个 9-SKU batch 只是 execution chunk：`6 × 9 = 54`。
- A/B/C 三 replicate 研究的是同一冻结 54 SKU，**不能把 54+54+54 写成 162 个独立 SKU。**

## 8.2 Match bucket A/B/C

这是跨市场商品身份：

- **Match A — Exact SKU**：品牌、型号、规格、容量、版本/地区硬件等一致。
- **Match B — Strong same-OEM**：不是同 branding，但有强证据证明同一 OEM/物理商品。
- **Match C — Functional comparable**：功能接近，但不是同一商品。

Match bucket 与 research replicate 没有任何分母继承关系。

---

# A. What We Know With High Confidence

1. **Domestic-first sample 的流程真实存在，并最终形成 immutable 54-SKU frozen universe。** 没有发现研究者因为海外难找而 post-freeze 删除难匹配 SKU。

2. **样本不是概率样本。** W2 的进入机制依赖 domestic ranking/purchase/exact identity 可审计性，再加预注册 priority/tie-break；因此可以研究被冻结的 54 行，但不能估算中国国内总体的 anomaly prevalence。

3. **冻结样本有明确分层：36 head slots = 32 verified-head + 4 fallback/unverified；另18 opportunity。** 不能把 opportunity SKU 代替 head shortfall，也不能把 provisional identity 变成另一 sampling stratum。

4. **当前没有一个冻结 SKU 形成了可审计、完整的 landed-cost observation。** W3-A/B/C 的 `verified_landed_savings_count=0`。:chatgpt-content-reference{index="7"}

5. **`n=0` 不能解释成 0% savings。** 它只说明运费、packed weight/volume、tariff、mandatory fees、exact overseas endpoint 等至少一项未闭合。

6. **W3-A/B/C 确实保留了完整 54 行。** audited exact-coverage observability 分别只有 8、9、7 个，但这些也不等于完整 landed observations。:chatgpt-content-reference{index="8"}

7. **W4-A/B/C 也各保留完整 54 行，但 usable exact coverage observations 为 0。** 这不代表 Temu/AliExpress exact coverage=0%；主要原因是页面壳、登录、阻断及缺乏 listing-level variant/seller/stock/price 证据。

8. **AliExpress/Temu 的访问失败不能升级成 verified unavailable。** 尤其 source audit 多次把 Temu 从泛化的 `blocked` 重编码为 `page_shell`，把 AliExpress 观察分成 `blocked` 或 `login_required`。

9. **本研究确认的是 research measurement/access/transaction-chain failure。** 它在多个 category、batch、channel 上反复出现，是真实可复现的研究/工程困难。

10. **普通消费者/global price-discovery failure 未证明。** 我们不知道真实普通消费者、登录用户、第三方服务或 API 是否能稳定完成本研究环境没有完成的 price discovery。

11. **Profitable anomaly set 未证明。** 因为没有 usable landed distribution，也没有合法 demand weights。

12. **“没有人尝试过”是错误的。** PriceDoge、HandHunt、agent 生态及其他 matching/comparison 产品构成历史 prior art；但它们没有证明本 thesis 已被完整执行或市场已被吃光。

**Confidence：高。** 这里的高 confidence 主要针对证据边界与机械状态，而不是对真实市场价差的预测。

---

# B. What Appears True but Is Not Yet Proven

1. **中国国内 head catalog 很可能包含一些未充分国际化的 SKU。** 这是合理且有 domestic-first evidence 支持的研究假设，但“数量足够大、GMV 足够大、landed 后仍显著便宜”三件事都还没有同时证明。

2. **轻小、标准化、低兼容性摩擦商品更容易形成可行 China-direct route。** 这是 operational feasibility 的方向性判断，不是 price-spread 结论。

3. **重量、体积、电池、区域硬件、售后、fitment、returns 很可能把大品类的裸价优势吃掉一部分。** 当前没有足够 actual quotes 量化吃掉多少。

4. **AliExpress 对已经国际化的中国商品可能显著压缩 spread。** 现有历史/结构证据支持这一机制，但对冻结 54 SKU 的 exact-SKU convergence rate 尚未测出。

5. **商业订单聚合而不进行物理聚货在操作上可行。** API/逐单履约证据支持这一点；是否因此拿到有意义的 freight discount 仍未知。

6. **Thin routing 比 inventory-owning marketplace 更适合做第一轮验证。** 这主要是因为它引入的库存、IOR、退货与仓储义务更少，不等于它已经是一个强业务。

7. **跨市场 transaction-grade data chain 本身可能具有产品价值。** 但目前只确认研究端测量困难，不知道消费者 willingness-to-pay、conversion uplift 或可 monetizable problem size。

**Confidence：中。**

---

# C. What Previous Assumptions Were Wrong

| 旧假设/表述 | 最终裁决 |
|---|---|
| “Global / consumer exact price-discovery failure = Confirmed” | **错误。** 只能确认本研究的 measurement/access/transaction-chain failure |
| “研究工具打不开 Temu/AliExpress = 市场没有货” | **错误。** `page_shell/login_required/blocked/not_observed` ≠ unavailable |
| “W4-B 17 blocked + 1 login-required 可以作为最终 access/coverage 统计” | **错误。** 它是旧研究过程汇总，且审计后部分状态需要重编码 |
| “18 domestic-opportunity SKU = feasibility-weighted sample” | **错误。** 它只是预注册 opportunity-seeking stratum |
| “Demand-weighted 与 feasibility-weighted 可以从当前数据自然推出来” | **错误。** 两套合法权重都没有闭合 |
| “三 replicate × 54 = 162 个样本” | **错误。** 三次重复研究同一 54-SKU universe |
| “单 batch 的 9/9 可以代表整个 replicate denominator” | **错误。** 每个 replicate 是六批合计 54 行 |
| “A/B/C n=0 = 0% savings 或 coverage” | **错误。** 只是没有 usable observations |
| “公开 list price / launch price / subsidy price 可视为 current ordinary transaction price” | **错误。** 必须分开 |
| “一个统一 China tariff % 足够算最终 landed cost” | **错误。** 必须 SKU→HTS10→origin/entry date→Chapter 99/301/232/exemption/fees |
| “小工具用户少 = 市场需求失败” | **错误。** 存在开发时间、功能完整度、分发等多种混杂 |
| “Thin routing 已有 Moderate 证据” | **不再成立。** 去掉越界的 global consumer failure 前提后，重判为 Weak |

---

# 9. 最终 12 个业务问题

| # | 问题 | 最终答案 |
|---|---|---|
| 1 | 中国国内正规热销商品相比 Amazon 的真实 landed-price advantage 多大？ | **不可估 / NA。** usable landed n=0 |
| 2 | 相比 AliExpress 呢？ | **不可估 / NA。** exact current comparator + landed chain 未闭合 |
| 3 | 相比 cheapest convenient overseas option 呢？ | **不可估 / NA** |
| 4 | 哪些 category spread 最大？ | **不可回答。** 没有合法 spread distribution |
| 5 | 哪些 category demand 最大？ | 只能给 W1 的**定性 demand band**；广义 smartphone、automotive、sports/outdoor、apparel 等属于较大消费域，但不能据现有异口径数值做精确 18 类统一 GMV 排名 |
| 6 | 哪些 category 同时落在 demand × feasibility 右上角？ | **经济意义上的右上角未证明。** 只能指出优先测量候选，不能宣称已找到右上角 |
| 7 | China-head / US-middle-tail gap 是否真实存在？ | **China-head 一侧成立；完整经济 gap 未证明。** US exact availability、price、GMV 与 landed spread 未闭合 |
| 8 | gap 是偶发异常还是结构性？ | **研究测量/访问失败具有重复性；消费者市场 anomaly 的结构性未证明** |
| 9 | Temu 已经解决哪些部分？ | 冻结样本 exact coverage 无法量化；source audit 主要得到 page shell/access limitation，不能给 0% 或 X% coverage |
| 10 | AliExpress 已经解决哪些部分？ | 结构上它是重要国际化 benchmark；但冻结 54 exact coverage 与 price convergence 未可靠测出 |
| 11 | Superbuy 足够成为基础设施而无需自己重做物流吗？ | **足够做 transaction pilot；不足以证明最终 scale economics。** 初期没有证据要求平台必须自己 physical aggregate/import |
| 12 | 为什么仍没有 dominant consumer product？ | 有若干 confirmed operational/data/counterparty friction；但没有一条被证实的单一原因可以解释市场空缺 |

---

# D. Category Opportunity Matrix — 全18类

**解释：**  
`US demand` 是 W1 的定性 band，不是统一 GMV weight。  
`CN-US spread / Ali / Temu` 在没有完整 transaction evidence 时全部保持 `NA`。  
`Net operational feasibility` 只描述物流/兼容性操作难度，**不是经济 opportunity score**。  
`Economic opportunity` 因缺 spread + demand weights，统一为 `NA`。

| Category | US demand | Verified head /2 | Opportunity slot | Identity note | CN-US spread | Ali exact coverage | Temu exact coverage | Shipping | Compatibility / regulatory friction | Net operational feasibility | Economic opportunity | Evidence confidence |
|---|---|---:|---:|---|---|---|---|---|---|---|---|---|
| C01 Smartphones | Very High | 2/2 | 1 | exact identity可定义 | NA | NA | NA | 中 | 电池、US bands、ROM/firmware、warranty | 中低 | NA | 中高 |
| C02 Laptops | High | 2/2 | 1 | exact配置重要 | NA | NA | NA | 中低 | 电池、重量、键盘、OS、warranty | 中低 | NA | 中 |
| C03 Tablets | Medium-high | 2/2 | 1 | Wi-Fi/capacity需锁定 | NA | NA | NA | 中 | 电池、region/account ecosystem | 中 | NA | 中高 |
| C04 Mini PCs | Low-medium | 2/2 | 1 | barebone vs RAM/SSD config风险高 | NA | NA | NA | 中高 | power adapter、OS、memory/storage config | 中高 | NA | 中 |
| C05 Storage / Networking | Medium-high | 2/2 | 1 | router/SSD/RAM版本需精确 | NA | NA | NA | 高 | firmware/region、host compatibility | 高 | NA | 中 |
| C06 Audio | Medium | 2/2 | 1 | 品牌窄榜不可外推全类 | NA | NA | NA | 中高 | 电池、app、codec | 中高 | NA | 中 |
| C07 PC Peripherals | Medium | **1/2** | 1 | `C07-S02` fallback head | NA | NA | NA | 高 | wireless/driver/firmware | 高 | NA | 中 |
| C08 Wearables | High | 2/2 | 1 | NFC/region版本重要 | NA | NA | NA | 中高 | NFC、app ecosystem、battery | 中 | NA | 中 |
| C09 Smart Home / IoT | High | 2/2 | 1 | exact ecosystem/version关键 | NA | NA | NA | 中 | cloud region、protocol、FCC/power | 中低 | NA | 中 |
| C10 Robot Vacuums / Appliances | High | 2/2 | 1 | voltage/region配置风险高 | NA | NA | NA | **低** | bulky、battery、power、installation/service | 低 | NA | 中高 |
| C11 Power / Repair Tools | High | 2/2 | 1 | bundle与battery platform需锁 | NA | NA | NA | 低中 | battery system、safety、plug/voltage | 中低 | NA | 中 |
| C12 Camera / Video | Medium | 2/2 | 1 | bundle/颜色/容量 mismatch 已出现 | NA | NA | NA | 中 | battery、高价值、warranty | 中 | NA | 中 |
| C13 Automotive Accessories | Very High | 2/2 | 1 | fitment 必须 exact | NA | NA | NA | 中 | fitment/safety/regulatory | 中 | NA | 中高 |
| C14 Sports / Outdoor | Very High broad | **0/2** | 1 | `C14-S01/S02` fallback；`C14-S03` = PROVISIONAL_VARIANT | NA | NA | NA | 中低 | size/oversize/use-case variance | 中低 | NA | 低中 |
| C15 Hobby / Maker / 3D Printing | Medium | **1/2** | 1 | `C15-S02` fallback head | NA | NA | NA | 低中 | 3D printer与small electronics高度异质 | 中低 | NA | 中 |
| C16 Apparel / Shoes / Bags | Very High | 2/2 | 1 | 颜色/尺码/正品授权关键 | NA | NA | NA | 中 | returns、fit、IP/authenticity | 中 | NA | 中高 |
| C17 Home / Organization | High | 2/2 | 1 | `C17-S01/S02 model=null`，但 exact item/variant 已锁 | NA | NA | NA | **低** | 兼容性低，但 volumetric freight 高 | 低 | NA | 中 |
| C18 Toys / Collectibles | High | 2/2 | 1 | official merch/bundle/box condition重要 | NA | NA | NA | 中高 | authenticity、bundle、collector condition | 中高 | NA | 中高 |

**矩阵裁决：** 当前无法给任何类别合法的“高经济 opportunity score”。比较可靠的是**研究优先级**：C04/C05/C07/C18 等标准化程度较高，适合作为低摩擦 measurement pilot；C01/C10/C11/C13/C16 等高需求但高摩擦类别必须继续保留，以免实验只筛选“最好寄的小东西”。

---

# E. Price Spread Distribution

## E1. Demand-weighted distribution

### 目标
回答：

> 美国消费者实际花出去的每一美元，落在 China-direct 可节省多少的 SKU 上？

合法的权重至少需要：

1. 同一年度；
2. 不重叠的 category taxonomy；
3. all-channel consumer-dollar spend，而不是把 PCE、批发额、shipment、tracking panel、forecast 混用；
4. 若从 category 下沉到 SKU，需要明确的 category→SKU spend allocation 或可审计 inclusion probability；
5. 权重定义必须在看到 savings outcome 前固定。

### 当前状态
**不可构造，NA。**

W1 的数据可以支持 qualitative demand bands，但不足以生成合法 18 类 consumer-dollar weights。现有 54 SKU 又不是概率样本。因此：

- weighted mean = NA
- weighted median = NA
- weighted P10/P25/P50/P75/P90 = NA
- weighted ≥10/20/30/40/50% share = NA

不得看到结果后再发明权重。

---

## E2. Feasibility-weighted sample / distribution

### 目标
回答：

> 在预先定义的、操作上更可能成功的跨境交易中，landed savings 分布是什么？

它不是“挑看起来便宜的 SKU”，也不是“18 opportunity SKU”。

一个合法的 feasibility design 必须在海外价差结果出现**之前**，仅用 ex-ante feasibility variable 定义权重或抽样概率，例如：

- packed weight / volumetric class；
- 是否含锂电；
- 特殊运输限制；
- 电压/插头；
- region / radio compatibility；
- 尺寸；
- product restriction；
- warranty/returns friction；
- 事先固定的 category balance。

### 当前状态
**不可构造，NA。**

原因：

- 没有预冻结的 feasibility weights；
- 大量真实 packed L×W×H、weight、route eligibility 尚未观察；
- 不能利用已经看到的 search/access outcome 或未来 savings 反向设计权重；
- 18 个 `domestic_opportunity` SKU **不是** feasibility weight。

因此 feasibility-weighted mean/median/quantile/threshold share 全部 NA。

---

## E3. Opportunity-seeking sample / distribution

### 目标
回答：

> 如果系统有意识地扫描国内市场中“预先看起来更可能存在未国际化机会”的 SKU，能发现多少 anomaly？

### 抽样定义
这一对象已经有合法、预注册的 sampling stratum：

**18 个 `domestic_opportunity` SKU = 每个 category 1 个。**

这是一个 sampling stratum，不是权重。

### 当前状态

- **Opportunity-seeking sample：可定义，n=18。**
- **Opportunity-seeking landed-savings distribution：不可构造，NA。**

原因仍是 usable landed observations = 0。未来如果这18行都闭合，可以先发布“18-SKU stratum 内的 unweighted descriptive distribution”；若要外推到机会宇宙，仍需额外 sampling design。

---

## E4. Final A/B/C match-bucket table

下面的 A/B/C 指 **match bucket**，不是 research replicate。

### W3 — usable landed-savings observations

| Research replicate | Match A exact | Match B strong same-OEM | Match C comparable | 解释 |
|---|---:|---:|---:|---|
| W3-A | **n=0** | **n=0** | **n=0** | 没有任何 bucket 形成完整 audited landed-savings observation |
| W3-B | **n=0** | **n=0** | **n=0** | 同上 |
| W3-C | **n=0** | **n=0** | **n=0** | 同上 |

这里的 `n=0` 不等于每个 bucket 的平均 savings=0%。

其他“原始搜索结果到底有多少条 A/B/C candidate listing”没有统一、可靠的全量审计口径，因此**raw offer count = NA**，不杜撰。

### W4 — usable marketplace-coverage observations

| Research replicate | Match A exact | Match B strong same-OEM | Match C comparable | 解释 |
|---|---:|---:|---:|---|
| W4-A | **n=0 usable** | **n=0 usable** | **n=0 usable** | 缺 listing-level variant/seller/stock/price 证据 |
| W4-B | **n=0 usable** | **n=0 usable** | **n=0 usable** | 旧 `17 blocked + 1 login` 不再使用 |
| W4-C | **n=0 usable** | **n=0 usable** | **n=0 usable** | access missingness 不能转成 coverage=0% |

这些也是“usable observation count”，不是 0% market coverage。

---

## E5. W4 最终 access-state adjudication

不再发布一个伪精确的 54-SKU 总状态计数，因为 audit 状态同时受 batch、channel、search endpoint 与 item endpoint 影响。

| R4 batch | Temu | AliExpress | 最终能说什么 |
|---|---|---|---|
| batch01 / C01-C03 | 多数 exact-search URL 为 dynamic/page shell | 多数 search URL blocked/unverified；个别 candidate item login-required | 不能判 unavailable |
| batch02 / C04-C06 | 9 条 search 基本为 page_shell/unverified | search URLs blocked/unverified | exact coverage unknown |
| batch03 / C07-C09 | Temu 9 条主要 page_shell | G304 search blocked；其他多出现 login sync / login_required；候选页仍不可审计 | exact coverage unknown |
| batch04 / C10-C12 | Temu page_shell | 9 条 exact-search URL login_required | exact coverage unknown |
| batch05 / C13-C15 | Temu page_shell | 9 条 search login_required | exact coverage unknown |
| batch06 / C16-C18 | 多数 page_shell；LEGO search 有 404/blocked 情况 | 9 条 US exact-search URL login_required；已知 item 也可能 blocked | exact coverage unknown |

**全量 `page_shell/login_required/blocked/not_observed` 数量：NA。**  
原因不是没做研究，而是 source audit 没有提供一个可无歧义、endpoint-consistent 的 54×channel 最终状态表；后验拼出一个总数反而会制造假精确。

---

## E6. Distribution statistics

因为所有 usable landed observations 均为 0，以下一律：

| Statistic | Demand-weighted | Feasibility-weighted | Opportunity-seeking |
|---|---|---|---|
| Mean | NA | NA | NA |
| Median | NA | NA | NA |
| P10 | NA | NA | NA |
| P25 | NA | NA | NA |
| P50 | NA | NA | NA |
| P75 | NA | NA | NA |
| P90 | NA | NA | NA |
| ≥10% | NA | NA | NA |
| ≥20% | NA | NA | NA |
| ≥30% | NA | NA | NA |
| ≥40% | NA | NA | NA |
| ≥50% | NA | NA | NA |

不以 blank=0、不以假运费、不以统一 tariff proxy、不以 accessory variant 最低价合成 synthetic distribution。

---

# F. China-head / US-middle-tail Gap

这个 thesis 必须拆成三段：

### F1. “China-head”——有支持

冻结集合中有 32 个 verified-head slot，外加 4 个按预注册优先级保留的 fallback/unverified head slot。还有 18 个 domestic-opportunity SKU。说明本研究确实从国内 catalog 与国内购买/榜单证据出发，而不是从 Amazon/AliExpress 搜得到的国际化 SKU 出发。

**裁决：Supported。Confidence：高。**

### F2. “US-middle/tail”——未闭合

要证明 frozen China-head SKU 在美国处于 middle/tail，需要 transaction-grade 观察至少回答：

- Amazon 是否有 exact SKU；
- AliExpress 是否有 exact SKU；
- Temu 是否有 exact SKU；
- US/global brand store 是否有；
- reseller 是否存在；
- ordinary delivered price；
- stock / warehouse / seller；
- 是 unavailable、marked-up reseller，还是仅仅研究环境未观察到。

目前这些字段没有全量闭合。

**裁决：Unproven。Confidence：高。**

### F3. “Gap 是经济机会”——未证明

即使一个中国 head SKU 在美国难找，也还必须证明：

`CN ordinary transaction price + domestic shipping + agent fee + actual freight + tariff + customs/processing`

显著低于：

`cheapest convenient overseas delivered price`

并且其 demand 足够大。

目前两边都缺关键量。

**裁决：Unproven。**

因此最终不能写：

> “China-head / US-middle-tail gap 已被证明是结构性、盈利的 anomaly set。”

最强合法表述是：

> **本项目建立了一个真实 domestic-first China-head frozen sample，但没有完成其 US distribution/availability 与 landed economics，因此 China-head / US-middle-tail economic gap 仍是需要 transaction-grade falsification 的核心假设。**

---

# G. Logistics Infrastructure Verdict

## G1. Superbuy 能否成为基础设施？

**答案：足够作为第一阶段 transaction pilot 的候选基础设施；不足以证明规模后的最终 economics。**

已支持：

- buying-agent procurement/forwarding 模块真实存在；
- 某些采购场景公开服务费可以为 0；
- consolidation、仓储、转运等基础流程存在；
- commercial orders 可以逐单履约，不必先把不同消费者货物物理拼成一票。

未支持：

- 1000 independent US consumer parcels/月的书面 negotiated freight rate；
- 每类 battery/oversize/restricted item 的真实附加费；
- 每个 frozen SKU 的 packed dimensional weight；
- 规模后 payment/fraud/returns economics；
- true bulk import 的完整增量成本。

因此：

> **不需要先自建物流/仓库才能验证 thesis；但也不能把代理基础设施的存在等同于 scale economics 已经成立。**

---

## G2. 四种 shipping structure 必须独立

| Structure | 定义 | 已知 | 未知 | 最终裁决 |
|---|---|---|---|---|
| 1. Single-item standalone | 一个消费者买一个商品，单独跨境发出 | 路径存在 | 54 SKU 的真实 packed quote、tariff、fees | **Economics unknown** |
| 2. Same-consumer consolidated marginal | 同一消费者多件入仓后合包；看某单品边际运费 | consolidation 机制存在 | 实际合包体积重、route、边际 break-even | **Economics unknown** |
| 3. Commercial aggregation / 1000 independent parcels | 平台聚合商业订单量，但每位消费者仍独立 parcel | API/逐单履约 operationally plausible | 1000 parcels/月 negotiated rate | **Rate unknown** |
| 4. True physical bulk import | 大批货物物理进口美国，再仓储/last-mile | 传统路径理论上存在 | freight、IOR、brokerage、warehouse、pick-pack、returns、last mile | **Full economics unknown** |

结构 3 和结构 4 绝不能互换费率或合规假设。

---

## G3. 业务/监管结构边界

| 架构 | 平台负担 | 当前意义 |
|---|---|---|
| Comparison/routing-only | 最轻 | 可先验证 search/value without owning goods |
| Consumer buys through agent | 较轻 | 让 agent 承担既有采购/履约流程的一部分 |
| Platform as buying agent | 增加支付、欺诈、退款、代理责任 | economics 未验证 |
| Commercially aggregated individual forwarding | 不需自动物理聚货 | 真实 rate 未得到 |
| Platform as importer / physical bulk | IOR/customs/warehouse 显著上升 | 不应在 thesis 未验证前作为默认 |
| Marketplace with US inventory | 库存、returns、product compliance 全面上升 | 当前不合理作为起点 |

---

# H. Strongest 10 Arguments AGAINST the Thesis

1. **最重要：0 个 usable landed observations。** 研究最初要回答的 price-spread distribution 到现在仍没有一个完整 transaction-grade datapoint。

2. **0/54 current domestic transaction price verified。** 公开 list/launch/subsidy price 与普通实际成交价之间仍存在缺口。

3. **没有合法 demand weights。** 即使未来发现几个漂亮 savings，也不能把 SKU count 或 cherry-picked example 当 TAM。

4. **AliExpress/Temu exact coverage 没测出来。** Missingness 本身可能夸大“美国没有”的感觉。

5. **2026 的跨境低值政策与 tariff stack 已经不能沿用旧 de-minimis 假设。** 每 SKU 税费复杂度真实存在。

6. **没有 1000-parcel/month negotiated freight quote。** 因此物流规模经济只是可能性，不是数字。

7. **Volumetric weight、battery、oversize 能轻易吃掉裸价 spread。** C10/C11/C17 等尤其敏感。

8. **需求最大的若干类别同时拥有较高 compatibility/returns/fitment/warranty friction。** 高 GMV 不自动等于高 feasibility。

9. **AliExpress 作为成熟 internationalization channel 有机制把一旦出现的高需求 spread 压缩。** 即便当前冻结 universe 没测出 exact convergence rate，这仍是 thesis 的强结构性反论点。

10. **transaction-grade data chain 本身昂贵且脆弱。** selector、login、coupon、promotion、variant、seller、warehouse、freight、tariff 全部动态变化，可能使 routing product 的维护成本显著高于普通 price comparison。

**Bear verdict：Broad thesis 面临很强反证；Narrow thesis 仍只是未证明，而非已证明不存在。**

---

# I. Strongest 10 Arguments FOR the Thesis

1. **Domestic-first freeze 是真实的。** 本研究没有再从 Amazon/AliExpress 容易找到的国际化 SKU 反向选样。

2. **冻结集合中确实存在大量经过国内榜单/购买信号核验的 head SKU。** 这比上一轮国际化 branded exact-SKU convenience sample 更接近最初研究目标。

3. **本研究跨多个 category 重复出现 transaction-chain measurement/access failure。** 这确认了一个真实工程问题：把国内真实 transaction state、跨境 logistics 与海外 exact comparator 自动闭合并不容易。**但这只证明研究/工程链难，不证明消费者/global market failure。**

4. **成熟 buying-agent infrastructure 已经存在。** 这降低了验证 thesis 所需的初始资本，不必一开始自己进口和仓储。

5. **商业订单流可以逐单履约。** 因此“拿商业量”与“物理合成一大票”不是同义词，给轻资产 scale experiment 留出了空间。

6. **PriceDoge、HandHunt 等证明 cross-site matching/comparison 并非技术幻想。** 历史存在只是说明有人做过，不等于该 thesis 已被充分商业化。

7. **一般购物助手/price-comparison 行为已经有邻近需求证据。** 这不能直接证明 China-routing demand，却说明“减少购物 search cost”不是陌生行为。

8. **Routing-only 结构不必自动承担 bulk importer/warehouse 的全部合规责任。** 因此最轻模式仍值得单独 falsify。

9. **专门的 W8 falsification 没有找到可以直接证明 narrow frozen anomaly set 已不存在的 hard evidence。** Broad thesis 可以被压低，但 narrow thesis 仍需交易实验。

10. **Incumbent channel 很强不等于覆盖冻结 China-head universe 的每一个 exact SKU。** 正确下一步是量化，而不是凭访问失败断言“有 gap”，也不是凭 AliExpress 强大断言“没有 gap”。

**Bull case 最终只能到这里：值得做 transaction-grade 实验；不能写成“中国普遍便宜30%+”。**

---

# J. Why No Dominant Company Exists Today

## J1. Confirmed

### 1. “没人做过”不是事实
PriceDoge、HandHunt、Taobao-agent、matching extensions 等说明有人尝试不同部分。

**能证明：**问题被注意过。  
**不能证明：**存在一个完整、规模化、以 US consumer exact landed routing 为核心的成功产品。

### 2. PriceDoge 没有完成预想的 P2P/完整形态
开发者资料同时出现用户不足与开发时间/资源因素。

**能证明：**该尝试未完整发展。  
**不能证明：**失败原因唯一是 consumer demand 不足。

### 3. HandHunt 展示了 warehouse-after-arrival freight uncertainty
最终包裹重量/尺寸可能到仓后才完全确定。

**能证明：**浏览阶段计算真实 landed cost 有 timing problem。  
**不能证明：**这个问题技术上不可解决。

### 4. ezbuy 类历史事件展示上游平台/账户/仓储关系风险
跨平台采购业务可能被上游政策或账户措施冲击。

**能证明：**counterparty platform risk 真实存在。  
**不能证明：**所有合法 routing/agent model 都会被封。

### 5. Alibaba 等平台存在 robot/login/API/permission boundary
数据抓取不是无限开放。

**能证明：**数据获取有工程、合同与权限边界。  
**不能证明：**合作/API/授权路径不存在。

### 6. Agent ecosystem 的合规/运营事件证明集中式代理会承担额外风险
尤其一旦控制支付、货物、仓储，风险比纯 routing 高。

---

## J2. Probable

1. **真实交易链过于碎片化。** 国内 SKU identity、优惠、seller、海外 comparator、freight、税费不在一个稳定 API 中。
2. **“真实价格”高度动态。** coupon/member/subsidy/login state 使静态抓价容易产生误导。
3. **一旦商品国际化，AliExpress/其他 seller 可能压缩 spread。**
4. **高需求 category 往往伴随更高 compatibility、returns、warranty friction。**
5. **中立推荐与 affiliate/marketplace monetization 可能产生激励张力。**

这些都有多条间接证据，但没有哪个足以单独解释“为什么没有 dominant company”。

---

## J3. Speculative

以下不能写成 confirmed explanation：

- 美国消费者普遍不信任中国平台；
- 消费者只在乎 next-day shipping；
- CAC 必然过高；
- affiliate monetization 必然毁掉产品；
- regulation 已经“杀死”该商业模式；
- 小工具用户少所以市场一定小；
- Amazon/Temu/AliExpress 已经完全解决所有 price discovery。

这些在逻辑上可能成立，但当前封闭 evidence base 不支持升级。

---

# K. Decisive Unknowns

真正足以改变评级的未知数只保留以下几项：

1. **冻结54 SKU的 transaction-grade landed ledger。** 必须同时获得 CN ordinary transaction price、exact overseas delivered comparator、packed dimensions/weight、真实 freight、agent fee、HTS/Chapter99/301/其他 duty、mandatory processing 与 FX。

2. **Authenticated AliExpress/Temu exact coverage。** 对每一行需要 selected variant、seller、stock、warehouse、ordinary price、delivered price、登录/地区状态。

3. **18类合法 demand weights。** 同年度、不重叠、all-channel consumer-dollar taxonomy；闭合前不得发布 demand-weighted market distribution。

4. **预注册的 feasibility-weighted design。** 必须在看到 savings 以前按物流/兼容性变量定 sampling probability 或 weight；不能事后发明。

5. **至少 2–3 家 provider 的 1000 independent US parcels/month 书面 commercial quote。**

6. **True bulk-import full economics。** 包括 IOR、brokerage、仓储、pick/pack、last-mile、returns，而不是只比较跨境主干运费。

7. **把研究工具失败与消费者现实分离。** 普通消费者/真实账户/API/合作方是否也存在可重复的 exact-SKU cross-market price-discovery failure？如果有，其中多少最后形成足够大的消费者 surplus / margin pool？

8. **只有上述经济链闭合后，才值得测 consumer conversion。** 在真实 savings 未知时提前测“愿不愿意等10天”很容易测错命题。

---

# L. Final Verdict

本表评级的是：

> **“当前证据是否足以把该命题当作业务/投资前提。”**

`Rejected` 不意味着数学证明市场为零；`Weak` 也不意味着一定失败。

| 命题 / 架构 | 最终评级 | Confidence | Decisive evidence | Strongest counterargument | 什么数据会改判 |
|---|---|---|---|---|---|
| **Broad thesis**：“中国国内 catalog 普遍存在巨大未套利价差” | **Rejected** | **高** | 0 usable landed observations；无合法 demand weights；incumbent/物流/税费有强结构性反证 | 数据缺失本身不是“没有 spread” | 概率/需求加权样本中，transaction-grade landed spread 持续显著且跨大需求类别成立 |
| **Narrow thesis**：“存在数量/GMV 足够大的 China-head / US-middle-tail anomaly set” | **Weak** | **中** | China-head 已建立；US-middle-tail availability、spread、GMV 三者未闭合 | narrow set 尚未被 falsify，missingness 可能隐藏真实机会 | 预注册 sample 中出现稳定 exact anomalies，并用合法 demand weights 证明经济规模 |
| **Thin comparison / routing SaaS** | **Weak** | **中** | 轻资产架构可行，但仅确认 research transaction-chain difficulty；消费者/global discovery failure与可 monetizable surplus 未证明 | 即使市场价差中等，统一数据/路由层仍可能有独立价值 | 真实用户 query 上反复出现可行动 savings/coverage uplift，并有 conversion/retention |
| **Shopping agent / agent checkout** | **Weak** | **中** | 基础 agent 模块存在，但增加 payment/fraud/refund/returns/customs friction，底层 savings 又未证明 | 一站式 checkout 可能显著降低 adoption friction | 完整 landed margin + payment/returns loss + consumer conversion 均闭合 |
| **Full marketplace / US inventory** | **Rejected** | **高** | 在 thesis 未证明前就增加库存、IOR、returns、compliance、working capital | 若 narrow anomaly pool 非常大且 repeatable，marketplace 后续可能合理 | 大规模复购、稳定 margin 与可预测 SKU turnover 先被证明 |
| **Logistics aggregation platform** | **Weak** | **中** | 商业订单 aggregation operationally plausible，但 negotiated rate 与 realized savings 均未获得 | 私下商务价可能显著优于公开报价 | 2–3 provider 的书面 1000-parcel quotes + realized pilot economics |

## L.1 Physical bulk-import architecture

**作为起始架构：Rejected；Confidence：高。**

不是因为 bulk import 永远不可行，而是当前连 route-level consumer surplus 都未证明，提前承担 IOR、brokerage、仓储、pick/pack、last-mile 与 inventory risk 没有证据基础。

---

# 20. 最小 final-metric → source-audit → artifact 追溯索引

| Final metric / statement | Source-audit claim/job | SKU / denominator artifact |
|---|---|---|
| Frozen physical SKUs = 54 | R2 domestic audits + coordinator mechanical freeze | `sample-freeze-v1.json`；18×3 |
| Head slots =36；verified=32；fallback=4 | `R2-domestic-batch01..06` 最终身份审计 | head stratum；fallback=`C07-S02,C14-S01,C14-S02,C15-S02` |
| Opportunity stratum =18 | R2 selection audit | 每类1个 `domestic_opportunity` |
| Exact variant =53/54；C14-S03 provisional | R2 final identity audit | `C14-S03` |
| C17 manufacturer model null | R2 identity limitation record | `C17-S01`,`C17-S02` |
| Current transaction price verified =0/54 | R2 domestic audits | frozen 54 ledger |
| W3-A rows=54；exact coverage observability=8；landed n=0 | `R3-batch01..06` + mechanical denominator | W3-A logical replicate / frozen54 |
| W3-B rows=54；coverage obs=9；landed n=0 | `R3-batch01..06` + mechanical denominator | W3-B / frozen54 |
| W3-C rows=54；coverage obs=7；landed n=0 | `R3-batch01..06` + mechanical denominator | W3-C / frozen54 |
| W4-A/B/C rows each=54；usable exact coverage n=0 | `R4-batch01..06` K01/K02 families + mechanical denominator | each W4 replicate / frozen54 |
| W4 access global count = NA | `R4-batch01..06` | channel/batch-specific access states；不制造全局计数 |
| Demand weights = NA | `R1-W1-A/B/C` | `weights_policy`；non-probability sample |
| Feasibility weights = NA | R2/R3/R5 combined missing operational variables | no preregistered feasibility-weight artifact |
| Opportunity sample =18；distribution=NA | R2 opportunity stratum + R3 landed n=0 | 18 frozen opportunity rows |
| 1000 independent-parcel negotiated freight rate = null | `R-W5-sources`, W5-A/B/C | logistics evidence ledger |
| Four shipping structures all lack complete SKU economics | R3 + R-W5 | 54-SKU logistics ledger |
| Current broad/narrow spread distribution = NA | R3 + R1 | usable landed n=0 + demand weights null |

机械 denominator 本身直接记录了 W3/W4 每个 replicate 的 `frozen_denominator=54` 与当前可计算计数。:chatgpt-content-reference{index="9"}

---

# 21. Core Source URLs / Evidence IDs

以下 URL **只按封闭 evidence ledger 原样保留**，本轮没有重新访问网页。

| Evidence IDs / jobs | Source URL | 本报告使用范围 |
|---|---|---|
| `W1-A:C13/C16`, `R1-W1-A` | `https://fred.stlouisfed.org/release/tables?eid=44183&rid=53` | US spending / category evidence；不升级成完整18类权重 |
| `W1-A:C13` | `https://www.autocare.org/data-and-information/market-research/joint-e-commerce-trends-and-outlook-forecast` | automotive demand/context |
| `W1-A:C10/C17` | `https://housewares.org/press-releases/second-annual-state-of-the-industry-report/` | housewares demand/context |
| `W5-A:C01-C04`, `R-W5:S01/S02` | `https://www.superbuy.com/en/page/guide/feecomposition/` | Superbuy fee structure |
| `W5-A:C03/C04` | `https://login.superbuy.com/en/page/query/freight/` | freight query structure；不是54-SKU真实quote |
| `W5-A:C07`, `R-W5:S06` | `https://www.buckydrop.com/en/services/pricing/` | BuckyDrop fee evidence |
| `W5-C`, `R-W5` | `https://www.buckydrop.com/en/dropshipping/` | dropshipping / individual fulfillment capability |
| `W5/W8`, `R-W5/R-W8` | `https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/` | 2026 de-minimis policy context |
| `R-W5` | `https://www.federalregister.gov/documents/2026/07/31/2026-15530/customs-user-fees-to-be-adjusted-for-inflation-in-fiscal-year-2027` | current fiscal-year fee audit |
| `W5/W6/W8` | `https://www.ustr.gov/issue-areas/enforcement/section-301-investigations/search` | Section 301 framework |
| `W8-A:C03`, `R-W8:R04/R05` | `https://ustr.gov/sites/default/files/files/Press/Releases/2026/FLIP%20301%20Investigation%20Final%20Action%20FRN%207-23-26%20FINAL.pdf` | tariff/regulatory evidence |
| `W8-C:C02`, `R-W8:R03` | `https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0` | CBP operational/regulatory evidence |
| `W6`, `R-W8` | `https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates` | product-certification boundary |
| `W7-A:C01`, `R-W7` | `https://github.com/DimensionDev/PriceDoge` | historical price-comparison prior art |
| `W7-A:C02`, `R-W7` | `https://chromewebstore.google.com/detail/buy-from-china-handhunt/kkclaagbdmhkeaenndgfkbkbkfipfold` | HandHunt prior art |
| `W7-A:C03`, `R-W7` | `https://chromewebstore.google.com/detail/capital-one-shopping-save/nenlahapcbofgnanklpelkaejcehkggg?gl=US&hl=en-US` | adjacent shopping-assistant context |
| `W7`, `R-W7` | `https://www.acnnewswire.com/press-release/english/40224/media-statement%3A-ezbuy.sg---update-on-service-disruption` | historical counterparty/service disruption |
| `W7/W8`, `R-W7/R-W8` | `https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html` | platform data/access boundary |
| `W8-C:C05`, `R-W8` | `https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm` | incumbent/company evidence |

这些核心 URL 与 evidence IDs 在上一版封闭 evidence ledger 中已有明确映射；本版只纠正它们能够支撑的 claim 范围。:chatgpt-content-reference{index="10"}

---

# 22. If We Spend $10,000 on Research, What Should We Do Next?

目标不是再写一轮 24-agent 长报告，而是第一次把 frozen 54 中足够多行推进成 **transaction-grade ledger**。

| 实验 | 预算 | 具体执行 | 最大减少的不确定性 |
|---|---:|---|---|
| **1. 54-SKU 双端 authenticated transaction recapture** | **$3,000** | 对54 SKU逐行取得 CN selected variant、seller、普通价/会员价/coupon/补贴分栏；同时抓 Amazon/Ali/Temu/brand/niche exact comparator 到 ZIP10001，保存时间与账户状态 | exact coverage、当前价与 comparator |
| **2. 12-SKU physical warehouse / shipping pilot** | **$3,000** | 在看到最终 spread 前预注册12个 SKU；真实买到 agent warehouse，记录 packed weight、L×W×H、battery/restriction、可用线路、实际 freight | 真实 standalone/consolidated landed cost |
| **3. Licensed customs / broker HTS audit** | **$1,500** | 对12个 physical pilot SKU 给出 HTS10、origin、Chapter99/301/其他 duty、exemption、entry mode、MPF/mandatory fees | tariff stack |
| **4. Commercial-rate RFP** | **$1,000** | 向 Superbuy/BuckyDrop/Sugargoo/其他至少2–3家 provider 请求约1000 independent US consumer parcels/月书面报价；另要 true bulk scenario | commercial aggregation 是否真有规模经济 |
| **5. US demand crosswalk** | **$1,000** | 建同年度、不重叠、all-channel consumer-dollar taxonomy；必要时购买/人工 crosswalk；无法闭合的权重保留 NA | demand-weighted distribution |
| **6. Independent QA + repeat snapshot** | **$500** | 第二研究员复核 exact identity；预定时点重复抓价，专门检测 promotion/date/variant sensitivity | 防止再次被 stale/promo/variant 污染 |
| **总计** | **$10,000** |  |  |

## 22.1 必须预注册的规则

1. 54 个 physical SKU 不因海外找不到、页面打不开、价格难看而删除。
2. 12 个 physical pilot SKU 在看到最终 landed spread 以前锁定。
3. `page_shell / login_required / blocked / verified unavailable / not observed / variant mismatch` 分开编码。
4. 普通价、会员价、coupon、国补、历史首发价分栏，不混。
5. comparator 同时保留 Amazon 与 **cheapest convenient overseas option**。
6. 四种 shipping structure 分开，不互借费率。
7. 缺 actual weight/LWH/freight/HTS/mandatory fee 的 landed cost 保持 `null`。
8. 只有完整 landed observations 才进入 mean/median/P10/P25/P50/P75/P90 与 ≥10/20/30/40/50%。
9. Demand-weighted distribution 只有 common-dollar weights 闭合后才发布。
10. Feasibility weighting / sampling rule 必须在 outcome 出现以前固定；**严禁看完 savings 再设计 weight**。
11. 18 个 `domestic_opportunity` SKU 继续作为 opportunity-seeking stratum，不改名成 feasibility sample。
12. 在实验前写下 change-of-mind thresholds。

这 $10,000 最有价值的最终工件应该是一张 54 行 transaction ledger，而不是另一篇无法闭合价格链的 narrative report。上一版预算结构本身是终审明确通过的部分；本版增加的关键修订是把 feasibility weighting 也纳入预注册纪律。:chatgpt-content-reference{index="11"}

---

# 23. 最终总裁决

本研究已经成功做到了一件重要但比最初 thesis 更基础的事情：

> **它建立了一个不依赖海外可搜索性的 domestic-first frozen SKU universe，并揭示了要把“国内真实成交价 → exact海外可买价 → 真实跨境 landed cost”闭合成可审计交易数字时，会遭遇持续的身份、登录、页面访问、动态价格、物流和税务链问题。**

它**尚未**成功证明另外三件更大的事情：

> 普通消费者存在广泛的 global price-discovery failure；

> China-head / US-middle-tail profitable anomaly set 足够大；

> 一个 routing product 可以持续捕获足够 GMV 和 consumer surplus。

因此最合理的当前 research posture 不是“这个市场已经被证实”，也不是“这个市场已经被证伪”，而是：

**Broad thesis 不应再作为成立前提；Narrow thesis 仍值得进行一次真正 transaction-grade 的、预注册的 $10,000 falsification experiment。**

只有当 54 行中的相当一部分真正从：

`CN current price = null / exact overseas = unknown / freight = null / HTS = null`

推进到：

`exact CN checkout + exact overseas delivered comparator + packed dimensions + actual freight + SKU-level tariff + mandatory fees = final landed cost`

之后，项目才第一次有资格回答原始 brief 最核心的问题：

> **中国国内 head catalog 中，到底有多大一块美国消费者支出能够产生可实现、可持续、足以补偿等待、兼容性和风险的净价格优势？**

截至本次封闭证据终审，答案仍然是：

# **Unknown — not zero, not proven, and not safely inferable from access failure.**

这版已把终审要求的 7 项 material fixes 全部内化进正文，尤其重新裁决了依赖越界前提的 Narrow/Thin 评级，并保留所有不可估统计为 `NA` 而非补数。