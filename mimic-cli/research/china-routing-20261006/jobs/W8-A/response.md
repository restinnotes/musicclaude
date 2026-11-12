# W8-A — Thesis Falsification（仅结构性研究）

**WEB RESEARCH AVAILABLE。** 本报告严格遵守 pre-freeze 边界：**未选择任何国内 SKU，未检查任何具体 SKU 的 Amazon/AliExpress/Temu 价格、覆盖或库存。**  
研究 as-of：**2026-10-06**。检索环境实际 UTC 时钟检查点：**2026-10-06T22:50:37Z、2026-10-06T22:53:35Z**。网页工具没有提供逐页面的精确抓取 UTC，因此证据 JSON 的 `retrieved_at` 按要求记为 `null`，不伪造时间。正文 source ID 对应的**完整字面 URL 均列在文末 JSON**。

## 1. Direct answer / Bottom line

1. **[FACT] 2026 年的税制已明显恶化单件 China-direct economics。** $800 de minimis 已无限期停止；自 **2026-07-24** 起国际邮件启用新的 postal informal-entry 流程，自 **2026-09-22** 起 CBP 在 ACE production 部署 Entry Type 13。与此同时，中国非豁免商品自 2026-07-24 又面临新的 **12.5% Section 301 forced-labor tariff**。这不是旧研究中可忽略的摩擦。S01/S02/S03。[GovDelivery](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0?utm_source=chatgpt.com)  
   **反证：** 存在产品豁免；旧 China-301 也有排除项目，因此绝不能把 12.5% 当所有 SKU 的统一 landed-cost 税率。[United States Trade Representative](https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation?utm_source=chatgpt.com)

2. **[INFERENCE] “国际渠道无法有效套利中国供应”这一宽泛前提受到很强反证。** Alibaba 2026-06 季度披露 AliExpress **已实现 operating profit**，并明确归因为物流优化和成本效率提升，同时继续利用集团供应链丰富供给。S04。[sec.gov](https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm)  
   **反证：** 同一披露没有提供 China-domestic-head 的 exact-SKU coverage 或价差分布，所以不能据此消灭狭义 China-head/US-middle-tail thesis。

3. **[FACT] 单件转运有显著固定成本和风险转嫁。** Superbuy 官方费用页明确国际运费按线路、估重结算；其示例中 1kg UPS 路线首 500g 即 CN¥320，并另有续重和清关费；官方同时明确第三方物流及海关风险由用户承担。S05/S06。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)  
   **反证：** 这只是官方示例，不是代表性美国报价；且普通采购代理服务费可以为 **0**，所以“agent fee 本身必然杀死模式”没有证据。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

4. **[FACT] 可扩展数据抓取存在真实平台边界。** 淘宝/天猫现行法律声明明确禁止未经许可通过机器人、蜘蛛等监视、复制、下载平台内容。2026-08 的开源工具 issue 又展示了已登录、中国大陆 IP 情况下仍可遇到滑块 CAPTCHA、SKU/价格误读。S07/S08。[Alibaba Terms](https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html)  
   **反证：** 京东存在需要 access token 的授权商品搜索 API，并支持按 15/30 日销量/GMV 排序；因此结论应是“匿名抓取脆弱”，而非“国内数据原则上无法获得”。S09。[opendoc.jd.com](https://opendoc.jd.com/iopv2/iopv2/%E5%95%86%E5%93%81/%E6%90%9C%E7%B4%A2%E5%95%86%E5%93%81.html)

5. **[FACT] 受监管品类的 direct-to-consumer 并不等于无合规层。** 自 **2026-07-08**，CPSC 对受监管进口消费品实施强制 certificate eFiling；责任主体可能是 IOR、owner、purchaser 或 consignee。S10/S11。[U.S. Consumer Product Safety Commission](https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports)  
   **反证：** 规则只适用于需要 CPSC certification 的产品，不能外推到全部商品。

6. **结论：目前可强力攻击的是 broad thesis，而不是 narrow thesis。** 结构证据表明税费、固定物流成本、合规和数据接入都比早期 de-minimis 时代差，而 AliExpress 已具备相当强的套利基础设施。但**没有任何本轮结构性证据能够回答“冻结后的中国国内头部 SKU 中，有多少 landed cost 仍比最低便利海外渠道低 ≥20/30/40%”**。因此狭义 thesis 尚未被证伪。

## 2. Evidence table

| Claim | Evidence | Source/date | Confidence | Counterevidence |
|---|---|---|---|---|
| 低值直邮结构性成本上升 | de minimis 无限期停止；postal informal entry + ACE ET13 | S01/S02，2026-07/09实施 | High | 仍可合法直邮，不等于路线消失 |
| 中国进口新增税压缩价差 | 非豁免中国货新 Section 301 = 12.5% | S03，2026-07-23 | High | Annex 豁免；须逐 HTS 算 |
| AliExpress 已有成熟套利能力 | 2026-Q2 实现 operating profit，归因物流/成本效率 | S04，数据至 2026-06-30 | High | 不证明 exact-SKU coverage |
| 单件 freight 可吃掉小价差 | Superbuy 首重/续重/清关结构及风险条款 | S05/S06，current | Medium | 示例不能代表全线路；采购费可为0 |
| 自动抓取不是可靠公共基础设施 | Taobao/Tmall 禁 bot；真实 CAPTCHA/错误价格案例 | S07/S08，2025-09 / 2026-08 | High/Medium | JD 有授权 API |
| 监管品存在进口资料责任 | CPSC eFiling 已生效 | S10/S11，2026-07-08 | High | 非全部商品受 CPSC certificate 约束 |

## 3. Primary sources

最高权重证据为 **CBP/USTR/CPSC、Alibaba SEC filing、淘宝天猫现行条款、Superbuy 官方条款**。最新可用政策状态包括：CBP postal informal entry **2026-07-24 生效**、ACE ET13 **2026-09-22 production deployment**；Alibaba 最新已读取财务期为 **截至 2026-06-30 的季度，2026-08-20 提交**。完整 URL、发布日期和访问状态见 JSON S01–S11。

另外，早期 2026 年 10% Section 122 temporary surcharge 已于 **2026-07-24** 到达法定终点；不能把它错误叠加到 2026-10-06 的 landed-cost 模型。当前新增广覆盖措施应以 7 月的 Section 301 action 为准。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/imposing-a-temporary-import-surcharge-to-address-fundamental-international-payments-problems/?utm_source=chatgpt.com)

## 4. Forum / community evidence

最有价值的社区证据不是“有人觉得运费贵”，而是**可复现的数据完整性故障**：OpenCLI 2026-08-25 issue 显示，已登录淘宝、CN IP 环境仍出现 CAPTCHA 页面被当商品成功返回，以及优惠券金额被误识别为商品价。S08。[GitHub](https://github.com/jackwener/OpenCLI/issues/2391?utm_source=chatgpt.com)

历史上 PriceDoge 已在 2019 年直接实现 Amazon/JD/Taobao/Newegg 跨平台比价，Taobao 搜索甚至需要服务端 Puppeteer；GitHub 当前只有 26 commits、72 stars。S12/S13。[GitHub](https://github.com/DimensionDev/PriceDoge) **但没有证据证明它“因经济模型失败而死亡”**，所以只能作为“概念并非无人尝试”的弱证伪材料。

## 5. Contrary evidence

最强反证有三项。第一，Superbuy 普通采购服务费可为零，说明 agent economics 并非天然需要高 percentage take-rate。S05。第二，JD 官方 API 可按销量和 15/30 日 GMV 排序，说明授权式 domestic data access 有现实路径。S09。第三，AliPrice Chrome extension 截至 2026-06-25 更新，商店显示 **200,000 users**，并支持跨 1688/Amazon/AliExpress 等找同源商品，说明跨平台 sourcing/comparison 本身存在实际使用规模。S14。[Superbuy](https://www.superbuy.com/en/page/guide/feecomposition/)

因此，“抓取太难”“没人要比价”“agent 一定太贵”均不能作为已证实的致命反证。

## 6. Confidence

**Broad thesis 的证伪力度：Medium-High。** “中国国内商品普遍存在巨大、国际渠道未套利的价差”与 2026 的税制和 AliExpress 物流成熟度明显冲突。

**Narrow thesis 的证伪力度：Low-Medium。** “仍存在数量/GMV 足够大的 China-head/US-middle-tail anomaly set”依然是开放问题；本 workstream 按 protocol 不得在 freeze 前做具体 SKU 海外核查，因此不能假造结论。

## 7. Data gaps

关键缺口：① frozen domestic-first 样本的 exact-match spread distribution；② 每 SKU HTS、当前 12.5% action 豁免和旧 Section-301 是否叠加；③ 真实美国 standalone 与 consolidated freight quotes；④ Superbuy 等的商务 volume pricing——**AUTHENTICATED/COMMERCIAL DATA REQUIRED**；⑤ 受 CPSC/FCC 等规则影响的 frozen 样本占比；⑥ 海外退货后的真实 reverse-logistics cost；⑦ AliExpress 对 China-head 的 exact coverage，而非总平台规模。

## 8. Most surprising finding

最意外的是：**2026 的最大结构变化不是某个 agent 涨价，而是美国已把“低值包裹免税、简化清关”这个历史底座系统性移除，同时新建电子 entry 流程。** 与此同时 AliExpress 自报达到 operating profit。两股力量都朝同一方向作用：压缩“自己绕过国际化渠道逐件进口”的相对优势。[GovDelivery](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0?utm_source=chatgpt.com)

## 9. What would falsify this report’s own conclusion?

以下任一结果会显著推翻本报告的 bearish 判断：冻结样本中，按美国需求加权后仍有例如 **≥20–30% 的 GMV** 在计入真实运费、现行 HTS duty、处理费后保持 **≥30%** 优势；AliExpress exact coverage 对 domestic-head 明显低；商务转运能把 marginal parcel cost 降到接近 AliExpress/Cainiao 水平；受 CPSC/兼容性约束的 SKU 占机会集很低；或对同一 frozen sample，数据可通过正式 API/合作接口稳定取得且 coupon/variant 匹配误差很低。

## 10. Suggested next experiment

唯一最有判别力的实验是：**冻结一份真正 domestic-first、需求分层的 SKU universe 后，做一次盲化 landed-cost audit。** 对每个 SKU 先锁定型号/规格/重量/HTS，再由独立研究者只在 freeze 后查询 AliExpress、Temu、Amazon 与其他便利渠道，并计算 standalone 与 consolidated 两种成本。核心输出不是“找到几个便宜例子”，而是 **demand-weighted exact-SKU savings distribution**。如果这张分布在 2026 税费和物流条件下仍有厚实右尾，W8 的主要结构性反证就会失败。

```json
{
  "job_id": "W8-A",
  "web_research_available": true,
  "sources": [
    {
      "source_id": "S01",
      "url": "https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0",
      "title": "CSMS # 69183472 - Updated Global Guidance for International Mail",
      "published_at": "2026-07-08",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02"]
    },
    {
      "source_id": "S02",
      "url": "https://content.govdelivery.com/accounts/USDHSCBP/bulletins/4214706",
      "title": "CSMS # 69289734 - Implementation of Entry Type 13 Test in ACE for U.S. Mail Processing",
      "published_at": "2026-07-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C01", "C02"]
    },
    {
      "source_id": "S03",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/ustr-takes-action-forced-labor-section-301-investigations",
      "title": "USTR Takes Action in Forced Labor Section 301 Investigations",
      "published_at": "2026-07-23",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C03"]
    },
    {
      "source_id": "S04",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm",
      "title": "Alibaba Group Holding Limited June Quarter 2026 Results",
      "published_at": "2026-08-20",
      "retrieved_at": null,
      "source_type": "filing",
      "access_state": "read_full_page",
      "claims_supported": ["C04"]
    },
    {
      "source_id": "S05",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fee Structure",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05", "C06"]
    },
    {
      "source_id": "S06",
      "url": "https://login.superbuy.com/en/page/newguide/shoppingagent/",
      "title": "Superbuy User Guidance - Shopping Agent",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C05"]
    },
    {
      "source_id": "S07",
      "url": "https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html",
      "title": "淘宝天猫法律声明",
      "published_at": "2025-08-26",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S08",
      "url": "https://github.com/jackwener/OpenCLI/issues/2391",
      "title": "taobao detail: 没有 SKU 输出，价格和可选规格在普通商品上都取错了",
      "published_at": "2026-08-25",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C07"]
    },
    {
      "source_id": "S09",
      "url": "https://opendoc.jd.com/iopv2/iopv2/%E5%95%86%E5%93%81/%E6%90%9C%E7%B4%A2%E5%95%86%E5%93%81.html",
      "title": "京东开放平台：搜索商品 API",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["C08"]
    },
    {
      "source_id": "S10",
      "url": "https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports",
      "title": "CPSC Implements Mandatory eFiling for Certificates of Compliance, Targeting Dangerous Foreign Imports",
      "published_at": "2026-07-08",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S11",
      "url": "https://www.cpsc.gov/efiling/importers",
      "title": "eFiling Resources for Importers",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C09"]
    },
    {
      "source_id": "S12",
      "url": "https://github.com/DimensionDev/PriceDoge",
      "title": "PriceDoge: A Chrome extension for price comparison",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C10"]
    },
    {
      "source_id": "S13",
      "url": "https://v2ex.com/t/547246",
      "title": "反杀熟的开源小工具 PriceDoge",
      "published_at": "2019-03-22",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["C10"]
    },
    {
      "source_id": "S14",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice%E8%B7%A8%E5%A2%83%E5%8D%96%E5%AE%B6%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/lenipkahddombkldhfmcnnjakmcepdlk",
      "title": "AiPrice(AliPrice) Sourcing Tool - Chrome Web Store",
      "published_at": "2026-06-25",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["C11"]
    },
    {
      "source_id": "S15",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation",
      "title": "USTR Extends Exclusions from China Section 301 Tariffs Related to Forced Technology Transfer Investigation",
      "published_at": "2025-11-26",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C03"]
    },
    {
      "source_id": "S16",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/imposing-a-temporary-import-surcharge-to-address-fundamental-international-payments-problems/",
      "title": "Imposing a Temporary Import Surcharge to Address Fundamental International Payments Problems",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["C12"]
    }
  ],
  "claims": [
    {
      "claim_id": "C01",
      "claim": "截至2026-10-06，美国低值包裹的de minimis行政免税已停止，国际邮件自2026-07-24进入新的postal informal-entry制度，并在2026-09-22部署ACE Entry Type 13生产环境。",
      "classification": "FACT",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "这增加清关和数据提交摩擦，但并未禁止消费者直邮或证明任何给定SKU不再具有价格优势。"
    },
    {
      "claim_id": "C02",
      "claim": "取消de minimis使逐件China-direct相对于旧制度产生结构性成本劣化。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02"],
      "confidence": "high",
      "counterevidence": "实际新增成本随HTS、承运方式、申报机制和物流商商业安排变化，不能从制度变化直接推导具体节省幅度。"
    },
    {
      "claim_id": "C03",
      "claim": "自2026-07-24起，中国非豁免进口商品适用新的12.5% Section 301 forced-labor tariff；同时存在产品豁免及其他China-301 exclusions。",
      "classification": "FACT",
      "source_ids": ["S03", "S15"],
      "confidence": "high",
      "counterevidence": "必须逐HTS核对豁免和其他现行税项，12.5%不能被当作所有SKU的统一总税率。"
    },
    {
      "claim_id": "C04",
      "claim": "Alibaba披露AliExpress在截至2026-06-30季度实现operating profit，并将其归因于物流优化和成本效率提升。",
      "classification": "FACT",
      "source_ids": ["S04"],
      "confidence": "high",
      "counterevidence": "盈利能力和物流效率不能证明AliExpress覆盖全部中国国内头部SKU，也不能证明exact-SKU价差已消失。"
    },
    {
      "claim_id": "C05",
      "claim": "Superbuy官方成本结构显示单件国际运输存在首重、续重及可能的清关等固定/半固定成本，并将第三方物流及海关风险部分转嫁给用户。",
      "classification": "FACT",
      "source_ids": ["S05", "S06"],
      "confidence": "high",
      "counterevidence": "公开的1kg费用仅为示例而非代表性美国报价；合箱和不同线路可能显著降低边际运费。"
    },
    {
      "claim_id": "C06",
      "claim": "“buying-agent服务费本身必然使消费者routing模式无法成立”没有得到支持，因为Superbuy普通采购代理服务可不收采购服务费。",
      "classification": "FACT",
      "source_ids": ["S05"],
      "confidence": "high",
      "counterevidence": "零采购费不等于整体经济为零摩擦，国际运费、支付、增值服务、退货和税费仍存在。"
    },
    {
      "claim_id": "C07",
      "claim": "依赖未经授权的淘宝/天猫自动抓取具有明确合同和技术脆弱性。",
      "classification": "INFERENCE",
      "source_ids": ["S07", "S08"],
      "confidence": "high",
      "counterevidence": "单个开源工具故障不是全行业失败率；经授权接口、合作关系或用户侧获取可能规避部分问题。"
    },
    {
      "claim_id": "C08",
      "claim": "国内平台数据并非原则上无法结构化取得：京东官方商品搜索API要求授权token，并支持15/30日销量和GMV排序。",
      "classification": "FACT",
      "source_ids": ["S09"],
      "confidence": "high",
      "counterevidence": "本次未进行认证访问，无法确认该API对研究所需完整消费者catalog、账号资质或实际可调用范围；AUTHENTICATED DATA REQUIRED。"
    },
    {
      "claim_id": "C09",
      "claim": "自2026-07-08起，受CPSC certification要求的进口消费品必须进行eFiling，责任主体可落在IOR、owner、purchaser或consignee等链条参与者。",
      "classification": "FACT",
      "source_ids": ["S10", "S11"],
      "confidence": "high",
      "counterevidence": "这不是覆盖所有消费品的普遍进口许可制度，不能用来否定不受相关CPSC规则约束的商品或纯comparison层。"
    },
    {
      "claim_id": "C10",
      "claim": "Amazon/JD/Taobao等跨平台商品比价的直接前例至少在2019年已存在，PriceDoge甚至为Taobao搜索设置了服务端Puppeteer。",
      "classification": "FACT",
      "source_ids": ["S12", "S13"],
      "confidence": "high",
      "counterevidence": "无法从当前仓库规模证明项目商业失败、停止日期或失败原因；因此不能作为startup failure的决定性证据。"
    },
    {
      "claim_id": "C11",
      "claim": "跨平台同源商品发现具有实际使用证据：Chrome Web Store显示AliPrice Sourcing Tool约200,000用户，并持续至2026-06-25更新。",
      "classification": "FACT",
      "source_ids": ["S14"],
      "confidence": "high",
      "counterevidence": "AliPrice主要面向跨境卖家，不能证明美国普通消费者愿意使用landed-cost routing产品。"
    },
    {
      "claim_id": "C12",
      "claim": "2026年2月实施的10% Section 122临时进口附加税依法仅运行至2026-07-24，除非国会延长，因此不应被继续机械加入2026-10-06的模型。",
      "classification": "FACT",
      "source_ids": ["S16"],
      "confidence": "high",
      "counterevidence": "其到期并不意味着税负回到旧de-minimis时代；2026-07-24起已有新的Section 301措施生效。"
    },
    {
      "claim_id": "C13",
      "claim": "结构性证据足以削弱“广泛中国国内catalog普遍存在巨大未套利价差”的broad thesis，但不足以证伪经domestic-first冻结样本定义的China-head/US-middle-tail narrow thesis。",
      "classification": "INFERENCE",
      "source_ids": ["S01", "S02", "S03", "S04", "S05", "S07", "S10"],
      "confidence": "medium",
      "counterevidence": "只有冻结后的exact-SKU、真实landed-cost、demand-weighted价差分布才能决定狭义命题；本workstream按pre-freeze协议没有进行该测试。"
    }
  ],
  "categories": [
    {
      "structural_category": "customs_and_de_minimis",
      "falsification_pressure": "high",
      "key_current_date": "2026-09-22",
      "quantified_effect": null,
      "source_ids": ["S01", "S02"]
    },
    {
      "structural_category": "tariffs",
      "falsification_pressure": "high",
      "key_current_date": "2026-07-24",
      "quantified_effect": "12.5% additional Section 301 for non-exempt China goods under the 2026 forced-labor action",
      "source_ids": ["S03", "S15"]
    },
    {
      "structural_category": "international_channel_arbitrage",
      "falsification_pressure": "high_for_broad_thesis",
      "key_current_date": "2026-06-30",
      "quantified_effect": null,
      "source_ids": ["S04"]
    },
    {
      "structural_category": "forwarding_logistics",
      "falsification_pressure": "medium_to_high_for_single_item",
      "key_current_date": null,
      "quantified_effect": null,
      "source_ids": ["S05", "S06"]
    },
    {
      "structural_category": "catalog_data_access",
      "falsification_pressure": "medium",
      "key_current_date": "2026-08-25",
      "quantified_effect": null,
      "source_ids": ["S07", "S08", "S09"]
    },
    {
      "structural_category": "product_compliance",
      "falsification_pressure": "high_for_regulated_categories_only",
      "key_current_date": "2026-07-08",
      "quantified_effect": null,
      "source_ids": ["S10", "S11"]
    },
    {
      "structural_category": "historical_predecessors",
      "falsification_pressure": "low",
      "key_current_date": null,
      "quantified_effect": null,
      "source_ids": ["S12", "S13", "S14"]
    }
  ],
  "sku_candidates": [],
  "data_gaps": [
    "Pre-freeze protocol prevents any specific-SKU overseas price or availability check in W8-A.",
    "Frozen domestic-first exact-SKU sample and demand-weighted landed-cost distribution are not yet available.",
    "Current duty liability must be adjudicated per SKU/HTS, including 2026 Section 301 exemptions and any legacy Section 301 exposure.",
    "Representative standalone and consolidated U.S. freight quotes are unavailable without a controlled frozen basket or real quote collection.",
    "Negotiated Superbuy/Sugargoo/BuckyDrop commercial-volume parcel rates are not public; AUTHENTICATED/COMMERCIAL DATA REQUIRED.",
    "JD API documentation was public, but actual authorized API scope was not tested; AUTHENTICATED DATA REQUIRED.",
    "No representative dataset quantifies post-export return, warranty, fraud, chargeback and reverse-logistics costs.",
    "No structural source establishes AliExpress exact-SKU coverage of China domestic head products.",
    "No verified failed startup was found whose documented failure causally demonstrates that consumer Amazon-to-Taobao landed-cost comparison is economically impossible."
  ],
  "pre_freeze_compliance": true
}
```