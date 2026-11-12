独立复核结论：三份 W3 均保留了全部 9 个冻结 SKU；冻结的 head 6/9、provisional 3/9 不因本轮网页可读性而升级。对 27 个 job×SKU observation，我没有找到任何一条可升级为 verified landed savings：standalone、consolidated marginal、1000 independent consumer orders、true physical bulk import 四种架构均至少缺真实国内运费/代理费、包装后计费重或体积重、锂电/包装附费、国际运费、逐 SKU HTS/现行税率或豁免、mandatory customs/brokerage、实际结算 FX 中的一项；ZIP10001 的精确 delivered endpoint 也没有闭合。未知项不能置零，因此 A/B/C 的 verified landed savings 仍全部为 n=0。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block)

C01 有两项实质纠错。iPhone 17 中国官网 256GB 白色仍为 ¥6,799；美国官网 $929 对应美国 A3258，而大陆机为 A3521，不能作 exact A；真正 A3521 256GB 白色 eBay 条目当前 $939.95 但已售罄。C01-S02 的 eBay A3524 页面虽然显示 $1,628，但当前 Silver、256GB 都仍是未选 selector，且配送示例为 ZIP50307，所以 W3-A 将 $1,628 绑定到 Silver/256GB 的写法应撤回；W3-B/C 在这一点更谨慎。Ace 6T 京东精确 12+256 闪速黑页当前明确显示 ¥2,958、“登录查看到手价”，因此 W3-C 把当前公开价改成 null 是错误；但最终到手价仍未知。[Apple (中国大陆) - 官方网站](https://www.apple.com.cn/shop/buy-iphone/iphone-17)

C02-S01 不能固定采用 ¥14,499：当前京东活动证据中，同一精确天选7 Pro 标题同时出现 ¥11,999 与 ¥14,499，且处于国补/活动语境，普通非补贴价与唯一当前活动价均未闭合。C02-S02 联想官方精确页可确认配置但显示“商品已下架”、价格为空；京东活动页本次复核受阻。C02-S03 精确京东页仍可读 ¥5,199，但最终到手价要求登录。[JD Pro](https://pro.m.jd.com/mini/active/2EX93wysZDfomDrf4k3fyQ7LXqvU/index.html)

两款 iPad 中国价 ¥3,799/¥4,299、美国 Apple $449/$549，以及当前 Best Buy $399/$499 均可读；Apple 型号资料支持 Wi-Fi 版本同为 A3354。不过三份报告对“跨销售地区但同硬件型号”究竟算 A 还是 C 有分歧，而冻结规则中未给出足以独立裁决该地区键的定义，所以这里保留为 `CONFLICT_UNRESOLVED`，不替协调器做最终判定；且 ZIP10001 到货日期仍需结账地点闭合。Y700 官方 ¥4,299 是“参考价”，当前直达商品页已下架且无成交价；当前 eBay 已选 12+256 Black/CN+Google 为 $796.30+$20，页面目的地仍是 50307，不能沿用早前不同运费快照。[Apple (中国大陆) - 官方网站](https://www.apple.com.cn/shop/buy-ipad/ipad)

另一个系统性纠错是 W3-C 把四种架构的 `section122_rate_now` 全写成 0；没有逐 SKU HTS 与当前适用税项映射时应为 `null`。Fed H.10 的 2026-10-02 参考汇率 6.7038 CNY/USD 可作参考，但不是实际支付 FX。W3-B 的跨品类简单均值和 W3-C 的分类简单均值也不应作为比较结论：其价型含官方价、促销、国补语境及不同当前状态，不能平均不可比快照。[The White House](https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/?trk=article-ssr-frontend-pulse_little-text-block)

受当前聊天链接呈现规则限制，下面机器 JSON 的 `url` 保留为 `null`；`source_id` 对应的原页均已在上述可点击引用中实际复核。

```json
{
  "job_id": "R3-batch01",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "review_performed": true,
  "frozen_sample_sha256": "4e882003a038fc557633b77d0ff9ac4d28f4f4cbf42feac78ef30d38dbbbd185",
  "audited_jobs": [
    "W3-A-batch01",
    "W3-B-batch01",
    "W3-C-batch01"
  ],
  "observation_audits": [
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C01-S01",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Apple China 256GB White CNY6799 verified; Apple US USD929 is A3258 while mainland target is A3521. Exact A3521 eBay unit USD939.95 is out of stock. Four landed architectures remain incomplete.",
      "source_ids": ["S01", "S02", "S03", "S04", "S24", "S25"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C01-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Set overseas exact-variant price to null: USD1628 is an unselected parent-listing price, not bound to Silver 256GB.",
      "caveat": "A3524 mainland hardware is supported, but Silver and 256GB selectors are not jointly selected and delivery shown is for ZIP50307, not ZIP10001.",
      "source_ids": ["S03", "S05"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C01-S03",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Exact JD 12GB+256GB Black page shows CNY2958 publicly; final take-home price requires login. No exact overseas ZIP10001 denominator or complete landed chain.",
      "source_ids": ["S06", "S07", "S24", "S25"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C02-S01",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Ordinary exact JD price remains unverified. Subsidy/campaign evidence for the same exact title is internally inconsistent across current displays, so no ordinary price or overseas denominator is closed.",
      "source_ids": ["S08", "S09", "S24", "S25"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C02-S02",
      "status": "UNVERIFIED_BLOCKED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "Lenovo exact page is off shelf with no price. The JD campaign page used for CNY5199 could not be independently reread in this audit and remains unverified.",
      "source_ids": ["S10", "S11", "S24", "S25"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C02-S03",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Exact JD page displays CNY5199; authenticated take-home price is unobserved. No exact overseas denominator or complete landed costs.",
      "source_ids": ["S12", "S24", "S25"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C03-S01",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "China price CNY3799 and US/Best Buy prices are observable; Wi-Fi hardware is A3354, but whether cross-region retail identity qualifies as strict A is not independently resolvable from the supplied frozen rule. ZIP10001 date is also unclosed.",
      "source_ids": ["S13", "S14", "S17", "S19"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C03-S02",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "China price CNY4299 and US/Best Buy prices are observable; Wi-Fi hardware is A3354, but strict cross-region A classification remains unresolved. ZIP10001 delivery date is unclosed.",
      "source_ids": ["S13", "S15", "S17", "S20"]
    },
    {
      "original_job_id": "W3-A-batch01",
      "sku_id": "C03-S03",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Current China transaction price=null; CNY4299 is an official reference price. Current selected eBay subtotal is USD816.30 (796.30+20) and destination shown is ZIP50307.",
      "caveat": "Lenovo direct exact item is currently off shelf. eBay CN+Google software state is C-type and endpoint is not ZIP10001; older shipping snapshots must not be averaged.",
      "source_ids": ["S21", "S22", "S23"]
    },

    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C01-S01",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "CNY6799 and USD929 are supported, but US A3258 differs from mainland A3521. No ZIP10001 exact delivered endpoint and no complete landed architecture.",
      "source_ids": ["S01", "S02", "S03", "S24", "S25"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C01-S02",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "W3-B correctly did not bind USD1628 to Silver 256GB. Current mainland ordinary price, exact selected overseas price, ZIP10001 delivery and landed chain remain missing.",
      "source_ids": ["S03", "S05", "S24", "S25"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C01-S03",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "JD exact page supports public display CNY2958, not final take-home price. Overseas parent listings do not close exact selected variant/region and ZIP10001.",
      "source_ids": ["S06", "S07", "S24", "S25"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C02-S01",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": null,
      "caveat": "W3-B used CNY14499 as campaign display, but current exact-title subsidy evidence also shows CNY11999 and CNY14499. Ordinary non-subsidy price and a unique campaign price are not closed.",
      "source_ids": ["S08", "S09"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C02-S02",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Lenovo exact 8745HS/16GB/512GB page is off shelf and blank-priced. This proves only that channel state, not whole-market unavailability; no overseas/landed closure.",
      "source_ids": ["S10", "S24", "S25"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C02-S03",
      "status": "INCOMPLETE_REQUIRED_COMPONENTS",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Exact JD page supports CNY5199 public display; final take-home price is login-gated and no exact overseas or landed endpoint is closed.",
      "source_ids": ["S12", "S24", "S25"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C03-S01",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "China CNY3799 and Apple US USD449 are supported; hardware is A3354 but China retail part is region-coded. Strict A versus C depends on an unresolved region-equivalence rule; ZIP10001 delivery date is not closed.",
      "source_ids": ["S13", "S14", "S16", "S17", "S18"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C03-S02",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "China CNY4299 and Apple US USD549 are supported; hardware is A3354 but strict cross-region A classification is unresolved. Exact ZIP10001 delivery timing remains checkout-dependent.",
      "source_ids": ["S13", "S15", "S16", "S17", "S18"]
    },
    {
      "original_job_id": "W3-B-batch01",
      "sku_id": "C03-S03",
      "status": "CONFLICT_UNRESOLVED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": null,
      "caveat": "Earlier W3-B shipping snapshot differs from current page: selected eBay offer now shows USD796.30 plus USD20 shipping to ZIP50307. Lenovo CNY4299 is reference price while direct item is off shelf.",
      "source_ids": ["S21", "S22", "S23"]
    },

    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C01-S01",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Set section122_rate_now to null, not 0, because SKU-specific HTS/current duty applicability is not closed.",
      "caveat": "Core item/model findings are supported, but unknown tax inputs may not be zeroed.",
      "source_ids": ["S01", "S02", "S03", "S04", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C01-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Set section122_rate_now to null, not 0.",
      "caveat": "W3-C correctly treated the eBay parent price as unbound, but the landed tax field still improperly zeroed an unknown input.",
      "source_ids": ["S05", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C01-S03",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Public display price is CNY2958; final take-home price remains null. Also set section122_rate_now=null.",
      "caveat": "W3-C's withdrawal of the current JD display price is contradicted by the currently readable exact page. Overseas exact denominator remains unclosed.",
      "source_ids": ["S06", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C02-S01",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Do not fix a unique campaign price from current evidence; ordinary non-subsidy price remains null. Set section122_rate_now=null.",
      "caveat": "Same exact-title subsidy evidence currently exposes CNY11999 and CNY14499, so W3-C's single CNY14499 snapshot is not a closed current denominator.",
      "source_ids": ["S08", "S09", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C02-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": false,
      "correction": "Set section122_rate_now=null.",
      "caveat": "Lenovo exact page is off shelf with no price; JD campaign evidence could not be independently reread. No unknown tax component may be set to zero.",
      "source_ids": ["S10", "S11", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C02-S03",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Set section122_rate_now=null.",
      "caveat": "CNY5199 public display is supported; authenticated take-home price and overseas/landed components remain incomplete.",
      "source_ids": ["S12", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C03-S01",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Set section122_rate_now=null.",
      "caveat": "CNY3799/USD449 and A3354 hardware identity are supported, but strict cross-region A classification is left unresolved and ZIP10001 delivery timing is not closed.",
      "source_ids": ["S13", "S14", "S16", "S17", "S18", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C03-S02",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Set section122_rate_now=null.",
      "caveat": "CNY4299/USD549 and A3354 hardware identity are supported, but strict cross-region A classification and ZIP10001 delivery timing remain unresolved.",
      "source_ids": ["S13", "S15", "S16", "S17", "S18", "S24", "S25"]
    },
    {
      "original_job_id": "W3-C-batch01",
      "sku_id": "C03-S03",
      "status": "CORRECTION_REQUIRED",
      "usable_exact_price_comparison": false,
      "usable_verified_landed_savings": false,
      "usable_exact_coverage_observation": true,
      "correction": "Current China transaction price=null; CNY4299 is reference price; current selected eBay subtotal is USD816.30 to ZIP50307; set section122_rate_now=null.",
      "caveat": "Lenovo direct page is off shelf. Current marketplace shipping differs from earlier snapshot and cannot be averaged or carried forward.",
      "source_ids": ["S21", "S22", "S23", "S24", "S25"]
    }
  ],
  "claim_audits": [
    {
      "claim_audit_id": "CA01",
      "original_job_id": "W3-A-batch01",
      "claim": "C01-S02 USD1628 is an exact Silver 256GB A price.",
      "status": "CORRECTION_REQUIRED",
      "correction": "Exact selected overseas price is null; USD1628 is the unselected parent-listing price.",
      "source_ids": ["S05"]
    },
    {
      "claim_audit_id": "CA02",
      "original_job_id": "W3-C-batch01",
      "claim": "C01-S03 current JD price is unobserved/null.",
      "status": "CORRECTION_REQUIRED",
      "correction": "Current exact page publicly displays CNY2958; final take-home price remains null.",
      "source_ids": ["S06"]
    },
    {
      "claim_audit_id": "CA03",
      "original_job_id": "W3-B-batch01/W3-C-batch01",
      "claim": "C02-S01 has a uniquely supported current campaign price of CNY14499.",
      "status": "CONFLICT_UNRESOLVED",
      "correction": null,
      "source_ids": ["S08", "S09"]
    },
    {
      "claim_audit_id": "CA04",
      "original_job_id": "W3-C-batch01",
      "claim": "section122_rate_now=0 for all four landed architectures.",
      "status": "CORRECTION_REQUIRED",
      "correction": "Use null until SKU-specific HTS/current applicability is established.",
      "source_ids": ["S24", "S25"]
    },
    {
      "claim_audit_id": "CA05",
      "original_job_id": "W3-A-batch01/W3-B-batch01/W3-C-batch01",
      "claim": "The two iPad US offers can be definitively assigned C or A under the frozen region rule.",
      "status": "CONFLICT_UNRESOLVED",
      "correction": null,
      "source_ids": ["S14", "S15", "S16", "S17"]
    },
    {
      "claim_audit_id": "CA06",
      "original_job_id": "W3-A-batch01/W3-B-batch01/W3-C-batch01",
      "claim": "Y700 CNY4299 is a current transaction price and prior marketplace shipping can be carried forward.",
      "status": "CORRECTION_REQUIRED",
      "correction": "CNY4299 is an official reference price; direct product page is off shelf. Current selected eBay snapshot is USD796.30+USD20 to ZIP50307.",
      "source_ids": ["S21", "S22", "S23"]
    },
    {
      "claim_audit_id": "CA07",
      "original_job_id": "W3-B-batch01/W3-C-batch01",
      "claim": "Simple means across the observed frozen prices are usable comparison results.",
      "status": "CORRECTION_REQUIRED",
      "correction": "Do not average incomparable category, subsidy/promo and channel/time snapshots.",
      "source_ids": []
    },
    {
      "claim_audit_id": "CA08",
      "original_job_id": "W3-A-batch01/W3-B-batch01/W3-C-batch01",
      "claim": "Verified landed savings sample count is zero.",
      "status": "VERIFIED_WITH_CAVEAT",
      "correction": null,
      "source_ids": ["S18", "S24", "S25"]
    }
  ],
  "sources": [
    {
      "source_id": "S01",
      "url": null,
      "title": "Apple China Buy iPhone 17",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K01"]
    },
    {
      "source_id": "S02",
      "url": null,
      "title": "Apple US Buy iPhone 17",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K01"]
    },
    {
      "source_id": "S03",
      "url": null,
      "title": "Apple Support - Identify your iPhone model",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K01", "K02"]
    },
    {
      "source_id": "S04",
      "url": null,
      "title": "eBay iPhone 17 A3521 256GB White exact listing",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K01"]
    },
    {
      "source_id": "S05",
      "url": null,
      "title": "eBay iPhone 17 Pro A3524 parent listing",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K02"]
    },
    {
      "source_id": "S06",
      "url": null,
      "title": "JD OnePlus Ace 6T 12GB+256GB Black exact page",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K03"]
    },
    {
      "source_id": "S07",
      "url": null,
      "title": "eBay OnePlus Ace 6T parent listing",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K03"]
    },
    {
      "source_id": "S08",
      "url": null,
      "title": "JD Tianxuan 7 Pro exact-title subsidy campaign page",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K04"]
    },
    {
      "source_id": "S09",
      "url": null,
      "title": "JD Tianxuan 7 Pro current campaign evidence with conflicting displayed prices",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K04"]
    },
    {
      "source_id": "S10",
      "url": null,
      "title": "Lenovo Xiaoxin 16SE Ryzen 7 8745HS 16GB 512GB official item",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K05"]
    },
    {
      "source_id": "S11",
      "url": null,
      "title": "JD Xiaoxin 16SE campaign page",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "blocked",
      "claims_supported": ["K05"]
    },
    {
      "source_id": "S12",
      "url": null,
      "title": "JD Mechrevo Wujie 14 2026 Ultra 5 226V 16GB 1TB exact page",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K06"]
    },
    {
      "source_id": "S13",
      "url": null,
      "title": "Apple China Buy iPad",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K07", "K08"]
    },
    {
      "source_id": "S14",
      "url": null,
      "title": "Apple China iPad A16 128GB Silver exact retail configuration",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K08"]
    },
    {
      "source_id": "S15",
      "url": null,
      "title": "Apple China iPad A16 256GB Silver exact retail configuration",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K08"]
    },
    {
      "source_id": "S16",
      "url": null,
      "title": "Apple US Buy iPad",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K07", "K08"]
    },
    {
      "source_id": "S17",
      "url": null,
      "title": "Apple Support - iPad A16 model identification",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K08"]
    },
    {
      "source_id": "S18",
      "url": null,
      "title": "Apple US Shipping and Pickup",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K08", "K12"]
    },
    {
      "source_id": "S19",
      "url": null,
      "title": "Best Buy iPad A16 128GB Silver",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K07"]
    },
    {
      "source_id": "S20",
      "url": null,
      "title": "Best Buy iPad A16 256GB Silver",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K07"]
    },
    {
      "source_id": "S21",
      "url": null,
      "title": "Lenovo China Y700 Gen 5 product reference page",
      "published_at": "2026-09-12",
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K09"]
    },
    {
      "source_id": "S22",
      "url": null,
      "title": "Lenovo China Y700 Gen 5 exact direct item page",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K09"]
    },
    {
      "source_id": "S23",
      "url": null,
      "title": "eBay Lenovo Legion Y700 Gen 5 selected 12GB+256GB Black CN+Google listing",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K09"]
    },
    {
      "source_id": "S24",
      "url": null,
      "title": "White House - Continuing the Suspension of Duty-Free De Minimis Treatment for All Countries",
      "published_at": "2026-02-20",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["K10", "K12"]
    },
    {
      "source_id": "S25",
      "url": null,
      "title": "USTR Section 301 tariff process/search guidance",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["K10", "K12"]
    },
    {
      "source_id": "S26",
      "url": null,
      "title": "Federal Reserve H.10 Chinese Yuan exchange rate",
      "published_at": "2026-10-05",
      "retrieved_at": "2026-10-06",
      "source_type": "government",
      "access_state": "read_full_page",
      "claims_supported": ["K11"]
    }
  ],
  "claims": [
    {
      "claim_id": "K01",
      "claim": "C01-S01: Apple China CNY6799 and Apple US USD929 are current public prices, but US A3258 and mainland A3521 are not exact regional hardware matches; exact A3521 USD939.95 listing is out of stock.",
      "classification": "FACT",
      "source_ids": ["S01", "S02", "S03", "S04"],
      "confidence": "high"
    },
    {
      "claim_id": "K02",
      "claim": "C01-S02: A3524 is mainland hardware, but the current USD1628 eBay parent price is not bound to jointly selected Silver and 256GB.",
      "classification": "FACT",
      "source_ids": ["S03", "S05"],
      "confidence": "high"
    },
    {
      "claim_id": "K03",
      "claim": "C01-S03: exact JD page publicly displays CNY2958 and requires login for final take-home price; overseas evidence does not close an exact selected denominator.",
      "classification": "FACT",
      "source_ids": ["S06", "S07"],
      "confidence": "high"
    },
    {
      "claim_id": "K04",
      "claim": "C02-S01: current subsidy/campaign evidence for the exact Tianxuan 7 Pro title shows conflicting CNY11999/CNY14499 values, so neither ordinary non-subsidy price nor a unique current campaign denominator is closed.",
      "classification": "FACT",
      "source_ids": ["S08", "S09"],
      "confidence": "high"
    },
    {
      "claim_id": "K05",
      "claim": "C02-S02: Lenovo exact 8745HS/16GB/512GB page is currently off shelf and blank-priced; JD campaign reread was blocked.",
      "classification": "FACT",
      "source_ids": ["S10", "S11"],
      "confidence": "high"
    },
    {
      "claim_id": "K06",
      "claim": "C02-S03 exact JD page publicly displays CNY5199 while final authenticated take-home price is unobserved.",
      "classification": "FACT",
      "source_ids": ["S12"],
      "confidence": "high"
    },
    {
      "claim_id": "K07",
      "claim": "C03-S01/S02 current observed prices are China CNY3799/CNY4299, Apple US USD449/USD549 and Best Buy USD399/USD499.",
      "classification": "FACT",
      "source_ids": ["S13", "S16", "S19", "S20"],
      "confidence": "high"
    },
    {
      "claim_id": "K08",
      "claim": "The two Wi-Fi iPads share A3354 hardware, but exact cross-region A versus C classification is not independently closed by the supplied frozen region rule; Apple location-specific delivery timing remains checkout-dependent.",
      "classification": "INFERENCE",
      "source_ids": ["S14", "S15", "S16", "S17", "S18"],
      "confidence": "medium"
    },
    {
      "claim_id": "K09",
      "claim": "C03-S03: Lenovo CNY4299 is an official reference price, direct exact item is currently off shelf, and current selected eBay snapshot is USD796.30 plus USD20 shipping to ZIP50307.",
      "classification": "FACT",
      "source_ids": ["S21", "S22", "S23"],
      "confidence": "high"
    },
    {
      "claim_id": "K10",
      "claim": "Duty-free de minimis remains suspended under the reviewed executive action; Section 301 product treatment requires HTS classification, so unknown tariff inputs must not be zeroed.",
      "classification": "INFERENCE",
      "source_ids": ["S24", "S25"],
      "confidence": "high"
    },
    {
      "claim_id": "K11",
      "claim": "Federal Reserve H.10 shows 6.7038 CNY/USD for 2026-10-02; this is a reference rate, not observed settlement FX.",
      "classification": "FACT",
      "source_ids": ["S26"],
      "confidence": "high"
    },
    {
      "claim_id": "K12",
      "claim": "No W3 observation closes all required components for any of the four shipping architectures or a SKU-specific ZIP10001 delivered comparison; verified landed savings remains zero in A/B/C.",
      "classification": "INFERENCE",
      "source_ids": ["S18", "S24", "S25"],
      "confidence": "high"
    },
    {
      "claim_id": "K13",
      "claim": "Simple averages across different product categories, subsidy/promotion states, channels and non-contemporaneous snapshots are not used as an audit comparison result.",
      "classification": "METHOD",
      "source_ids": [],
      "confidence": "high"
    },
    {
      "claim_id": "K14",
      "claim": "Frozen head/provisional status is preserved at 6 head-verified and 3 provisional/opportunity observations per job; current price accessibility does not upgrade those frozen sampling statuses.",
      "classification": "METHOD",
      "source_ids": [],
      "confidence": "high"
    }
  ],
  "data_gaps": [
    "No SKU has a fully verified ZIP10001-specific delivered endpoint including exact delivery timing where location-dependent.",
    "Across the four shipping architectures, at least one required real component remains missing: China domestic shipping, agent fee, packed actual/volumetric weight, packaging or battery surcharge, international freight, mandatory customs/brokerage, or other mandatory charges.",
    "No SKU has a closed 8-digit HTS plus current MFN/Section301/other duty/exemption mapping; unknown duty inputs cannot be set to zero.",
    "No real quote was observed for 1000 independent consumer orders at a commercial rate.",
    "No real quote was observed for true physical bulk import.",
    "No actual settlement FX was observed; Federal Reserve H.10 is reference-only.",
    "C02-S02 JD campaign evidence was blocked during this independent reread.",
    "The frozen rule supplied here does not independently resolve whether same-hardware A3354 Wi-Fi iPads sold under different regional retail parts must be A or C.",
    "No averages of incomparable product, promotion, subsidy, channel or time snapshots are accepted as audit conclusions."
  ]
}
```