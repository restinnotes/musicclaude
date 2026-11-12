已完成独立 live-source 审计，并严格保持 pre-freeze：**没有查任何海外 exact-SKU、价格、库存或 coverage，也没有购买、联系或付费访问。**我把三份报告的重叠内容折叠成 14 个证伪威胁族。总体结论是：**制度、物流、合规与数据接入摩擦确有硬证据；但没有硬证据证明 narrow China-head/US-middle-tail opportunity set 已消失，亦没有证据证明市场价格已经普遍收敛。**凡从“存在风险/成本机制/平台规模”跳到“市场级失败”的推论都应降格。

海关证据最扎实。CBP 明确确认 de minimis 行政豁免无限期暂停，2026-07-24 启用新的 postal informal-entry 流程，ET13 于 09-22 部署生产环境。Federal Register 还明确：Chapter 98/99、PGA 等项目的延迟合规窗口到 **10-22**；所以 W8-B:C03 在 10-06 只能说“未来制度变化已确定”，不能写成已经观察到的额外摩擦。W8-C:C02 的 74.8m → 7,254,980、年化 29,099,645（约 -61.1%）数字正确，但这是 91 天状态口径的年化，而且 CBP 同时列举新增 duties、de-minimis suspension 与 interim process，不能把下降单因归于某一机制，更不能直接等同套利失败。[GovDelivery](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0)

关税方面，W8-A:C03 的核心事实成立：USTR 最终文件列中国为受调查经济体，而非特殊 10%/MFN-cap 组，因此非豁免商品落入“其他经济体”12.5%，自 07-24 生效；同时确有产品豁免，旧 China-301 的 178 项 exclusions 又延至 2026-11-10。反方向，W8-B:C02 与 W8-A:C12 也成立：2025 IEEPA additional duties 已被 EO 14389 终止，Section 122 的 10% surcharge 法定期限到 07-24。故任何“一律给中国商品叠一个统一税率”的模型都是错误的。[United States Trade Representative](https://ustr.gov/sites/default/files/files/Press/Releases/2026/FLIP%20301%20Investigation%20Final%20Action%20FRN%207-23-26%20FINAL.pdf)

CPSC eFiling 已自 07-08 生效，但只针对**本来就需要 CPSC certification 的进口产品**；CPSC 还明确说，个人自用消费者通常不会被视为承担 certification 的 importer。因此它是品类相关摩擦，不是全 catalog blocker。Superbuy 的零标准采购费、免费合包、首重/续重及用户承担部分海关/退运风险均可现场核实；但 W8-A 用的 CN¥320 首 500g 是官方示例，页面没有把它定义为代表性美国报价，不能外推市场平均。更重要的是，W8-B:S11 business-service 页面此次只返回页面壳，因此“direct-to-client/商务折扣已公开验证”应撤回。[U.S. Consumer Product Safety Commission](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates?utm_source=chatgpt.com)

数据层方面，现行淘宝天猫法律声明确实禁止未经许可的 robot/spider 获取内容；OpenCLI #2391 也确实展示了登录态、CN IP 下单个工具出现 CAPTCHA、coupon-price 误读。但这只能证明**脆弱性实例**，不是行业失败率。W8-C:C10 的原始 S11 实际指向 2019《淘宝平台服务协议》，不是承载 robot 条款的现行法律声明，需更换引用。W8-B:S12 的“3143万条、罚30万元”此次只能找到媒体转载，15 分钟预算内未定位一手处罚决定，因此不得当作 primary hard evidence。相反，JD 官方文档要求 token 且提供 15/30 日销量、GMV 排序，淘宝也有正式 item-detail API；这否定“结构化国内数据原则上不可获得”，但不证明商业授权范围足够。[Alibaba Terms](https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html)

incumbent 证据同样需要限界。Alibaba 确实披露 AliExpress 2026-06 季度实现 operating profit，并归因于物流优化和成本效率；20-F 也支持 200+ 国家/地区及 AliExpressDirect 利用 30+ 国家库存。但这些都**没有测 China-head exact-SKU coverage 或价差**。PDD 20-F 的 de-minimis 描述是风险披露，不是已发生损失；Q2 总收入 +8% 又是 PDD consolidated，不能当成 Temu-US 韧性数据。AiPrice 的 200,000 与 100,000 用户数字也都是真的——它们是**两个不同 Chrome 扩展**，并不冲突；PriceDoge 的跨 Amazon/JD/Taobao 前例也存在。但这些只证明 matching/sourcing 有使用者，不证明 consumer landed-cost router 的经济性。[Securities and Exchange Commission](https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm?utm_source=chatgpt.com)

因此三份报告最可保留的是“**broad thesis 面临明显结构压力**”；必须删除或降格的是任何“这些压力已经证明 narrow thesis 失败”的暗示。最强 contrary evidence 仍是：旧 blanket tariffs 已退出、普通 agent procurement fee 可为零且可免费合包、正式 API 路径存在、matching 工具持续被使用。社区运费和单次插件故障都是 cherry-picked observations，不应有 market-wide 权重。

```json
{
  "job_id": "R-W8-sources",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "review_performed": true,
  "audited_jobs": ["W8-A", "W8-B", "W8-C"],
  "claim_audits": [
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C01",
      "original_source_ids": ["S01", "S02"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "de minimis暂停、2026-07-24 postal informal entry及2026-09-22 ET13 PROD均由CBP一手材料确认；制度变化不证明任一SKU不再有套利空间。",
      "source_ids": ["R01", "R02", "R03"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C01",
      "original_source_ids": ["S01", "S03", "S04"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "事实成立，但本次FederalRegister原始网页入口呈页面壳；同一规则通过官方GovInfo Federal Register PDF和CBP材料独立核实，不能沿用原报告的read_full_page访问声明。",
      "source_ids": ["R01", "R03", "R28", "R29"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C02",
      "original_source_ids": ["S01"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "74.8m、7,254,980及年化29,099,645均正确，约下降61.1%；年化基于91天，且CBP描述的是新增关税、暂停豁免和interim process共同环境，不是单变量因果实验。",
      "source_ids": ["R03"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C03",
      "original_source_ids": ["S03", "S05", "S07"],
      "status": "CONFLICT_UNRESOLVED",
      "supported": null,
      "correction": null,
      "caveat": "2026-10-22合规日及Chapter 98/99、PGA涉及的规则变化已核实；但研究截止日为10-06，所谓摩擦增加尚未成为观察结果，只能保留为前瞻推断。",
      "source_ids": ["R02", "R03"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C03",
      "original_source_ids": ["S03", "S15"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "中国属于该行动受调查经济体且落入12.5%组，自2026-07-24生效；产品豁免及既有China-301 exclusions要求逐HTS处理，不能用12.5%代表总税率。",
      "source_ids": ["R04", "R05"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C02",
      "original_source_ids": ["S02", "S05", "S06"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "EO 14389明确终止所列IEEPA additional ad valorem duties，同时明确不影响Section 301等其他税项；逐HTS分析仍必要。",
      "source_ids": ["R06", "R04", "R05"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C12",
      "original_source_ids": ["S16"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Section 122的10% surcharge文本规定运行至2026-07-24，除非国会延长；本次未发现应继续机械计入10-06模型的依据。",
      "source_ids": ["R07"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C09",
      "original_source_ids": ["S10", "S11"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "eFiling已生效且责任链可涉及IOR、owner、purchaser、consignee或broker；仅适用于需CPSC certification的产品，且CPSC通常不把个人自用消费者视为负责certification的进口商。",
      "source_ids": ["R08", "R09", "R10"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C05",
      "original_source_ids": ["S05", "S06"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "首重、续重、路线、目的地及海关/退运风险条款真实存在；CN¥320首500g只是官方计算示例，并非代表性美国单件报价，不能据此量化美国市场普遍固定成本。",
      "source_ids": ["R11", "R12", "R13"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C06",
      "original_source_ids": ["S05"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Superbuy明确称Taobao/Tmall/JD/1688标准采购不收采购服务费，并可免费合包；这仅否定agent fee必然杀死模式，不代表完整landed cost低。",
      "source_ids": ["R11"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C05",
      "original_source_ids": ["S09", "S10", "S11"],
      "status": "CORRECTION_REQUIRED",
      "supported": null,
      "correction": "保留按重量/路线/目的地收费及拆单能力；删除或降格“direct-to-client及商务物流折扣已由公开页面验证”，因为本次S11对应business-service页面仅返回页面壳。",
      "caveat": "没有公开、可审计的美国商务rate card或volume breakpoint。",
      "source_ids": ["R11", "R12", "R14"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C09",
      "original_source_ids": ["S10"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "用户承担某些国际退运、海关及敏感品风险的条款已核实；5日无理由退换条款也存在，但公开文本本身没有量化这些风险的实际发生率。",
      "source_ids": ["R13"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C07",
      "original_source_ids": ["S07", "S08"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "现行淘宝天猫法律声明确有限制，OpenCLI #2391也是真实技术故障实例；单个开源适配器故障不能代表全行业抓取失败率或授权数据路径。",
      "source_ids": ["R15", "R19"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C10",
      "original_source_ids": ["S11"],
      "status": "CORRECTION_REQUIRED",
      "supported": true,
      "correction": "W8-C:S11指向2019年《淘宝平台服务协议》，不是本次核到robot/spider禁令的现行法律声明；应改引W8-A:S07所对应的2025-08-26《法律声明》。",
      "caveat": "主张本身正确，但原始source ID与证据文本不匹配。",
      "source_ids": ["R15", "R16"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C06",
      "original_source_ids": ["S12", "S13"],
      "status": "CORRECTION_REQUIRED",
      "supported": null,
      "correction": "把“3143万余条、罚款30万元”的行政执法实例从hard primary evidence降为secondary report，直至取得广东市监原始处罚决定；授权API存在部分可保留。",
      "caveat": "15分钟边界内仅核到China Quality News转载，未定位一手行政处罚公示。",
      "source_ids": ["R17", "R18", "R27"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C08",
      "original_source_ids": ["S09"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "JD官方文档明确要求access token，并列出15/30日销量及GMV排序参数；没有进行认证调用，因此不能证明研究所需完整catalog、商业授权或稳定配额。",
      "source_ids": ["R17"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C04",
      "original_source_ids": ["S04"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "Alibaba确实披露AliExpress季度operating profit并明确提及logistics optimization和cost efficiency；盈利不等于China-head exact-SKU coverage或价差收敛。",
      "source_ids": ["R20"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C05",
      "original_source_ids": ["S04", "S05"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "200+国家/地区、AliExpressDirect利用30+国家库存及季度盈利均有Alibaba一手披露；只能证明压缩价差的基础设施机制，不能证明exact-SKU覆盖。",
      "source_ids": ["R20", "R21"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C06",
      "original_source_ids": ["S06", "S07"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "PDD 20-F确实把取消de minimis列为可能导致涨价、订单减少及商家参与下降的风险；Q2 2026总收入同比+8%也是事实，但为PDD consolidated数据，不能推断Temu美国业务表现。",
      "source_ids": ["R22", "R23"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C10",
      "original_source_ids": ["S12", "S13"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "PriceDoge仓库明确实现Amazon、JD、Newegg、Taobao比较，并为Taobao使用Puppeteer；不存在可据此证明其因经济模型失败而终止的证据。",
      "source_ids": ["R26"]
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C11",
      "original_source_ids": ["S14"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "指定Chrome扩展当前页面确显示200,000 users并标示2026-06-25更新；这是卖家/采购导向工具使用规模，不是美国普通消费者landed-cost routing需求。",
      "source_ids": ["R24"]
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C11",
      "original_source_ids": ["S12"],
      "status": "VERIFIED_WITH_CAVEAT",
      "supported": true,
      "correction": null,
      "caveat": "指定的另一AiPrice扩展显示100,000 users、2026-08-15更新。它与W8-A的200,000-user扩展具有不同extension ID，因此两个数字并不冲突。",
      "source_ids": ["R25"]
    },
    {
      "original_job_id": "W8-B",
      "original_claim_id": "C09",
      "original_source_ids": ["S18", "S19", "S20"],
      "status": "UNVERIFIED_NOT_CHECKED",
      "supported": null,
      "correction": null,
      "caveat": "在时间边界内未逐条重新审计三篇Reddit帖；即使帖子数字准确，也只是自选择社区样本，不能用于美国转运成本分布或市场均值。",
      "source_ids": []
    },
    {
      "original_job_id": "W8-C",
      "original_claim_id": "C12",
      "original_source_ids": ["S13"],
      "status": "UNVERIFIED_NOT_CHECKED",
      "supported": null,
      "correction": null,
      "caveat": "未在时间边界内重新审计AiPrice论坛单点故障；此类支持案例即使真实也只能证明维护负担实例，不证明系统性失败。",
      "source_ids": []
    },
    {
      "original_job_id": "W8-A",
      "original_claim_id": "C13",
      "original_source_ids": ["S01", "S02", "S03", "S04", "S05", "S07", "S10"],
      "status": "CONFLICT_UNRESOLVED",
      "supported": null,
      "correction": null,
      "caveat": "结构证据可以合理提高对broad thesis的怀疑，但没有frozen demand-weighted exact-SKU数据，无法观察机会集大小、价差分布或市场级convergence；narrow thesis仍未决。",
      "source_ids": ["R01", "R03", "R04", "R08", "R11", "R15", "R20"]
    }
  ],
  "sources": [
    {
      "source_id": "R01",
      "url": "https://content.govdelivery.com/accounts/USDHSCBP/bulletins/41fa7f0",
      "title": "CSMS # 69183472 - Updated Global Guidance for International Mail",
      "published_at": "2026-07-08",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T01"]
    },
    {
      "source_id": "R02",
      "url": "https://content.govdelivery.com/accounts/USDHSCBP/bulletins/4214706",
      "title": "CSMS # 69289734 - Implementation of Entry Type 13 Test in ACE for U.S. Mail Processing",
      "published_at": "2026-07-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T01", "T03"]
    },
    {
      "source_id": "R03",
      "url": "https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/FR-2026-06-24.pdf",
      "title": "Federal Register Vol. 91 No. 120, including CBP de minimis and postal entry rules",
      "published_at": "2026-06-24",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T01", "T02", "T03"]
    },
    {
      "source_id": "R04",
      "url": "https://ustr.gov/sites/default/files/files/Press/Releases/2026/FLIP%20301%20Investigation%20Final%20Action%20FRN%207-23-26%20FINAL.pdf",
      "title": "Notice of Actions in Section 301 Investigations Related to Forced Labor",
      "published_at": "2026-07-23",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T04"]
    },
    {
      "source_id": "R05",
      "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2025/november/ustr-extends-exclusions-china-section-301-tariffs-related-forced-technology-transfer-investigation",
      "title": "USTR Extends Exclusions from China Section 301 Tariffs",
      "published_at": "2025-11-26",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T04", "T05"]
    },
    {
      "source_id": "R06",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/ending-certain-tariff-actions/",
      "title": "Ending Certain Tariff Actions",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T05"]
    },
    {
      "source_id": "R07",
      "url": "https://www.whitehouse.gov/presidential-actions/2026/02/imposing-a-temporary-import-surcharge-to-address-fundamental-international-payments-problems/",
      "title": "Imposing a Temporary Import Surcharge to Address Fundamental International Payments Problems",
      "published_at": "2026-02-20",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T05"]
    },
    {
      "source_id": "R08",
      "url": "https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Implements-Mandatory-eFiling-for-Certificates-of-Compliance-Targeting-Dangerous-Foreign-Imports",
      "title": "CPSC Implements Mandatory eFiling for Certificates of Compliance",
      "published_at": "2026-07-08",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T06"]
    },
    {
      "source_id": "R09",
      "url": "https://www.cpsc.gov/efiling/importers",
      "title": "eFiling Resources for Importers",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T06"]
    },
    {
      "source_id": "R10",
      "url": "https://www.cpsc.gov/FAQ/CPC",
      "title": "Children's Product Certificate FAQ",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["T06"]
    },
    {
      "source_id": "R11",
      "url": "https://www.superbuy.com/en/page/guide/feecomposition/",
      "title": "Superbuy Fee Structure",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T07", "T08"]
    },
    {
      "source_id": "R12",
      "url": "https://www.superbuy.com/en/page/query/freight/",
      "title": "Superbuy International Shipping Cost Estimator",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T07"]
    },
    {
      "source_id": "R13",
      "url": "https://www.superbuy.com/en/page/about/statementagreement/",
      "title": "Superbuy Glocalization Program Agreement",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T08"]
    },
    {
      "source_id": "R14",
      "url": "https://www.superbuy.com/en/page/businessservice/",
      "title": "Superbuy Business Service",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "page_shell",
      "claims_supported": ["T07"]
    },
    {
      "source_id": "R15",
      "url": "https://terms.alicdn.com/legal-agreement/terms/c_platform_service_agreement/20250822113153903/20250822113153903.html",
      "title": "淘宝天猫法律声明",
      "published_at": "2025-08-26",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T09"]
    },
    {
      "source_id": "R16",
      "url": "https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao201908081411_65986.html",
      "title": "淘宝平台服务协议（2019）",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T09"]
    },
    {
      "source_id": "R17",
      "url": "https://opendoc.jd.com/iopv2/iopv2/%E5%95%86%E5%93%81/%E6%90%9C%E7%B4%A2%E5%95%86%E5%93%81.html",
      "title": "京东开放平台：搜索商品 API",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T12", "T13"]
    },
    {
      "source_id": "R18",
      "url": "https://developer.alibaba.com/docs/doc.htm?articleId=23559&docType=2&treeId=34",
      "title": "淘宝开放平台 taobao.tae.item.detail.get",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T12", "T13"]
    },
    {
      "source_id": "R19",
      "url": "https://github.com/jackwener/OpenCLI/issues/2391",
      "title": "taobao detail: 没有 SKU 输出，价格和可选规格取错",
      "published_at": "2026-08-25",
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["T10"]
    },
    {
      "source_id": "R20",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000110465926099220/tm2623667d1_ex99-1.htm",
      "title": "Alibaba Group Holding Limited June Quarter 2026 Results",
      "published_at": "2026-08-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T14"]
    },
    {
      "source_id": "R21",
      "url": "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm",
      "title": "Alibaba Group Holding Limited 2026 Form 20-F",
      "published_at": "2026-05-20",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T14"]
    },
    {
      "source_id": "R22",
      "url": "https://www.sec.gov/Archives/edgar/data/1737806/000110465926050727/pdd-20251231x20f.htm",
      "title": "PDD Holdings Inc. 2025 Form 20-F",
      "published_at": "2026-04-29",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T14"]
    },
    {
      "source_id": "R23",
      "url": "https://www.sec.gov/Archives/edgar/data/1737806/000110465926100534/tm2623874d1_ex99-1.htm",
      "title": "PDD Holdings Announces Second Quarter 2026 Unaudited Financial Results",
      "published_at": "2026-08-24",
      "retrieved_at": null,
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["T14"]
    },
    {
      "source_id": "R24",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice%E8%B7%A8%E5%A2%83%E5%8D%96%E5%AE%B6%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/lenipkahddombkldhfmcnnjakmcepdlk",
      "title": "AiPrice(AliPrice) Sourcing Tool",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": []
    },
    {
      "source_id": "R25",
      "url": "https://chromewebstore.google.com/detail/aipricealiprice-search-by/aadbahhifnekkkcbapdfandpimaoacmj",
      "title": "AiPrice(AliPrice) Search by Image for China Import",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": []
    },
    {
      "source_id": "R26",
      "url": "https://github.com/DimensionDev/PriceDoge",
      "title": "PriceDoge: A Chrome extension for price comparison",
      "published_at": null,
      "retrieved_at": null,
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": []
    },
    {
      "source_id": "R27",
      "url": "https://m.cqn.com.cn/ms/content/2024-04/10/content_9044609.htm",
      "title": "China Quality News reproduction of an administrative penalty concerning unauthorized crawling",
      "published_at": "2024-04-10",
      "retrieved_at": null,
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["T11"]
    },
    {
      "source_id": "R28",
      "url": "https://www.federalregister.gov/d/2026-12669",
      "title": "Indefinite Suspension of the De Minimis Exemption for Mail Shipments and New Postal Informal Entry Process",
      "published_at": "2026-06-24",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "page_shell",
      "claims_supported": ["T01", "T03"]
    },
    {
      "source_id": "R29",
      "url": "https://www.federalregister.gov/d/2026-12670",
      "title": "Indefinite Suspension of the De Minimis Exemption for Merchandise Arriving Through All Modes Other Than the International Postal Network",
      "published_at": "2026-06-24",
      "retrieved_at": null,
      "source_type": "government",
      "access_state": "page_shell",
      "claims_supported": ["T01"]
    }
  ],
  "claims": [
    {
      "threat_id": "T01",
      "original_refs": ["W8-A:C01[S01,S02]", "W8-A:C02[S01,S02]", "W8-B:C01[S01,S03,S04]", "W8-C:C01[S01,S02]", "W8-C:C03[S01,S02]"],
      "finding": "de minimis暂停和新postal-entry架构属已验证制度摩擦，但不能证明SKU级经济性失败。"
    },
    {
      "threat_id": "T02",
      "original_refs": ["W8-C:C02[S01]"],
      "finding": "邮政低值件量明显下降属观察事实；91天年化且多因素共同变化，不能当单因或价差收敛证据。"
    },
    {
      "threat_id": "T03",
      "original_refs": ["W8-B:C03[S03,S05,S07]"],
      "finding": "10月22日规则切换已确定，但截止10月6日尚属未来结果，额外实际成本未观察。"
    },
    {
      "threat_id": "T04",
      "original_refs": ["W8-A:C03[S03,S15]", "W8-C:C04[S03]"],
      "finding": "中国非豁免品新的12.5% forced-labor Section 301成立，但产品豁免和旧301 exclusions使税负高度SKU/HTS异质。"
    },
    {
      "threat_id": "T05",
      "original_refs": ["W8-A:C12[S16]", "W8-B:C02[S02,S05,S06]"],
      "finding": "旧IEEPA duties和临时Section122 surcharge不能继续作为10月统一baseline；这反而是重要contrary evidence。"
    },
    {
      "threat_id": "T06",
      "original_refs": ["W8-A:C09[S10,S11]", "W8-B:C04[S07,S08]"],
      "finding": "CPSC eFiling是受监管、需认证商品的真实摩擦，不是全消费品许可层。"
    },
    {
      "threat_id": "T07",
      "original_refs": ["W8-A:C05[S05,S06]", "W8-B:C05[S09,S10,S11]", "W8-C:C08[S09,S14]"],
      "finding": "转运成本依首重、重量、路线、目的地和品类而变化；没有代表性美国报价或商业volume curve，不能推市场失败。"
    },
    {
      "threat_id": "T08",
      "original_refs": ["W8-C:C09[S10]", "W8-A:C05[S05,S06]"],
      "finding": "退运、海关、延误和敏感品风险确有合同转嫁，但未观测实际发生率或平均损失。"
    },
    {
      "threat_id": "T09",
      "original_refs": ["W8-A:C07[S07,S08]", "W8-C:C10[S11]"],
      "finding": "未经授权bot抓取存在明确平台限制；W8-C:C10原source指错文本。"
    },
    {
      "threat_id": "T10",
      "original_refs": ["W8-A:C07[S07,S08]", "W8-C:C12[S13]"],
      "finding": "存在真实技术故障实例，但单个开源工具或论坛故障不能估计行业级数据错误率。"
    },
    {
      "threat_id": "T11",
      "original_refs": ["W8-B:C06[S12,S13]"],
      "finding": "所谓大规模抓取行政处罚目前只有二手转载被核到，不能升级成已验证一手执法证据。"
    },
    {
      "threat_id": "T12",
      "original_refs": ["W8-A:C08[S09]", "W8-B:C06[S12,S13]"],
      "finding": "授权API路径确实存在，因此“国内数据原则上无法取得”被反证；商业权限、完整度和稳定性仍未知。"
    },
    {
      "threat_id": "T13",
      "original_refs": ["W8-A:C04[S04]", "W8-B:C07[S14,S15]", "W8-C:C05[S04,S05]"],
      "finding": "AliExpress已有大规模国际化和盈利基础设施，是合理压价机制，但没有exact-SKU coverage/convergence观察。"
    },
    {
      "threat_id": "T14",
      "original_refs": ["W8-C:C06[S06,S07]", "W8-B:C07[S14,S15]", "W8-B:C09[S18,S19,S20]", "W8-C:C13[S14,S15]"],
      "finding": "PDD风险披露、平台整体增长及社区转运实例只能说明冲击与继续运营并存，不能推导Temu-US或整个consumer-routing市场结果。"
    }
  ],
  "data_gaps": [
    "Immutable domestic-first frozen SKU universe尚未提供；因此没有进行任何海外exact-SKU价格、coverage或库存研究。",
    "冻结后仍需逐SKU确认HTS、MFN、2026 forced-labor Section 301、legacy Section 301 exclusions及PGA/CPSC适用性。",
    "没有代表性美国standalone/consolidated forwarding报价，也没有Superbuy/Sugargoo/BuckyDrop商业volume rate card。",
    "JD/Taobao API只验证了公开文档，实际授权范围、商业用途、配额和catalog完整性未认证测试。",
    "Superbuy business-service公开页面本次为page shell，公开商务折扣和direct-to-client能力未硬验证。",
    "W8-B:S12所述中国行政处罚在时间预算内未找到原始监管机关决定书，只找到二手转载。",
    "W8-B三篇Reddit运费帖及W8-C AiPrice论坛故障未逐条重新核验；即使真实也不得作为市场级统计。",
    "没有可审计的跨境退货、欺诈、chargeback、warranty和reverse-logistics总体损失数据。",
    "没有冻结样本上的AliExpress/Temu exact-SKU coverage或demand-weighted landed-cost spread distribution。",
    "仍未验证一例因consumer Amazon-to-China landed-cost routing结构性经济失败而关闭、且失败原因有一手经营记录支持的startup。",
    "本浏览环境未提供可靠逐页面精确抓取UTC，因此retrieved_at统一记为null而非推算。"
  ]
}
```