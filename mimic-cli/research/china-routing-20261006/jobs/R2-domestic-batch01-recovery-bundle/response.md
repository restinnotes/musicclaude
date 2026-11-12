This is one logical mg sample audit assembled mechanically from three completed single-category mg audits. The original larger audit failed and is preserved; no new model synthesis was invented. Source IDs are mechanically prefixed by category to avoid collisions.

=== UNEDITED MG CATEGORY AUDIT R2-domestic-batch01-recovery-C01; SHA256 96009a70c4c6b8241c44c0b0fe82363bb6bbb99c3fba555ba4191881931f54e2 ===
审计结论：可复现4条“榜单+精确版本”head记录，但 iPhone 17 两条实际指向同一京东 item，推荐时去重。两个京东自营榜URL当前口径确有冲突：A榜为 iPhone 17 Pro/17 TOP1/2，B榜为 iPhone 18 Pro/17 TOP1/2，因此只认各自榜页，不外推成统一销量榜。[jd.com](https://www.jd.com/phb/key_9987dadff159556152fd.html)

OnePlus、REDMI K90、vivo X300均复现国内精确版本零售条目；评论数不作为销量排名。一加原称“20000+”未在给定完整页复现，当前该页为0+，但精确款仍存在。[JD.com](https://www.jd.com/hprm/98478710c0c450aa4d9a.html) W2-C两个head不进入verified-head：Mate 80“12+512雪域白”未闭环；Xiaomi 17 Pro“白色12+256普通版”只复现到合约专享，不能与普通版合并。[JD.com](https://www.jd.com/hprm/998798f39c6efd1fa6e4.html)

推荐去重后：iPhone 17、iPhone 17 Pro；机会样本同级按字典序取 OnePlus Ace 6T。未用壳页、评论数或社区转述推断成交价/销量。

```json
{
  "job_id": "R2-domestic-batch01-recovery-C01",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "review_performed": true,
  "category_ids": ["C01"],
  "candidate_audits": [
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-H01",
      "brand": "Apple",
      "model": "iPhone 17 Pro",
      "exact_variant": "256GB 银色，中国大陆京东自营双卡双待版本",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S01"],
      "caveat": "S01当前明确TOP1并给出精确款及item链接；商品详情为JS壳，未核验当日普通成交价。"
    },
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-H02",
      "brand": "Apple",
      "model": "iPhone 17",
      "exact_variant": "256GB 白色，中国大陆京东自营双卡双待5G版本",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S01"],
      "caveat": "S01当前明确TOP2；与W2-B C01-H02同一京东item 100209267857，推荐阶段去重。"
    },
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-O01",
      "brand": "OnePlus",
      "model": "Ace 6T",
      "exact_variant": "12GB+256GB 闪速黑",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": ["S03", "S04"],
      "caveat": "京东完整列表复现精确新机款；该给定列表当前显示0+评价，原20000+不沿用。社区对榜首的转述不作为销量/排名证据。"
    },
    {
      "original_job_id": "W2-B-batch01",
      "original_candidate_id": "C01-H01",
      "brand": "Apple",
      "model": "iPhone 18 Pro",
      "exact_variant": "256GB 勃艮第酒红色，5G双卡双待",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S02"],
      "caveat": "S02当前明确TOP1；仅认该具体榜页口径，不与S01合成为统一销量榜。当前成交价未核验。"
    },
    {
      "original_job_id": "W2-B-batch01",
      "original_candidate_id": "C01-H02",
      "brand": "Apple",
      "model": "iPhone 17",
      "exact_variant": "256GB 白色，5G双卡双待",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S02"],
      "caveat": "S02当前明确TOP2；与W2-A C01-H02指向同一京东item，推荐阶段不重复抽样。"
    },
    {
      "original_job_id": "W2-B-batch01",
      "original_candidate_id": "C01-O01",
      "brand": "REDMI",
      "model": "K90",
      "exact_variant": "12GB+256GB 白色，骁龙8至尊版，7100mAh",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": ["S05", "S06", "S07"],
      "caveat": "国内自营完整列表复现精确款；原item购买页需先选门店才能确认价格且当前无评价。原“推荐榜TOP1”不作为本次销量排名证据。"
    },
    {
      "original_job_id": "W2-C-batch01",
      "original_candidate_id": "C01-H1",
      "brand": "HUAWEI",
      "model": "Mate 80",
      "exact_variant": "全网通版 12GB+512GB 雪域白",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S08", "S09"],
      "caveat": "官方确认Mate 80及12GB+512GB容量；当前京东完整页复现其他12+512颜色/雪域白其他配置，但未闭环该精确组合。评论量不能证明head。"
    },
    {
      "original_job_id": "W2-C-batch01",
      "original_candidate_id": "C01-H2",
      "brand": "Xiaomi",
      "model": "Xiaomi 17 Pro",
      "exact_variant": "12GB+256GB 白色 5G",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": false,
      "source_ids": ["S10", "S11", "S12"],
      "caveat": "普通自营页可见17 Pro的12+256黑色/冷烟紫及白色其他容量；白色12+256仅复现“重合约专享”，按规则不得与普通版合并。"
    },
    {
      "original_job_id": "W2-C-batch01",
      "original_candidate_id": "C01-O1",
      "brand": "vivo",
      "model": "X300",
      "exact_variant": "V2509A 全网通 12GB+256GB 惬意紫",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": ["S13", "S14", "S15"],
      "caveat": "京东完整自营页复现12+256惬意紫；vivo官方参数确认V2509A、容量与配色，国内社区有长期使用体验；不以评论数证明销量。"
    }
  ],
  "recommended_selection": [
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-H02",
      "brand": "Apple",
      "model": "iPhone 17",
      "exact_variant": "256GB 白色，中国大陆京东自营双卡双待5G版本",
      "category_id": "C01",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "榜单+精确版本已核验；同一物理SKU跨研究去重后保留W2-A记录；同级按brand/model/variant字典序优先。",
      "source_ids": ["S01"]
    },
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-H01",
      "brand": "Apple",
      "model": "iPhone 17 Pro",
      "exact_variant": "256GB 银色，中国大陆京东自营双卡双待版本",
      "category_id": "C01",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "榜单+精确版本已核验；在剩余同级唯一SKU中按NFKC/casefold字典序优先于iPhone 18 Pro。",
      "source_ids": ["S01"]
    },
    {
      "original_job_id": "W2-A-batch01",
      "original_candidate_id": "C01-O01",
      "brand": "OnePlus",
      "model": "Ace 6T",
      "exact_variant": "12GB+256GB 闪速黑",
      "category_id": "C01",
      "sampling_stratum": "domestic_opportunity",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "reason": "精确国内零售款及社区来源均可复现；与REDMI、vivo同级时按brand/model/variant NFKC/casefold字典序最先。",
      "source_ids": ["S03", "S04"]
    }
  ],
  "exclusion_log": [],
  "category_gaps": [
    "W2-C的两个domestic_head均无可复现的销量/榜单位次，因此不计入verified-head。",
    "两个京东自营手机榜URL当前TOP排序不同；本审计不把任一榜页解释成全站统一销量排名。",
    "未用评论数、推荐榜、社区转述替代销量排名。"
  ],
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.jd.com/phb/key_9987dadff159556152fd.html",
      "title": "自营手机排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K01"]
    },
    {
      "source_id": "S02",
      "url": "https://www.jd.com/phb/key_9987edf2c0f03f1afc7f.html",
      "title": "京东手机自营手机排行榜",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K02"]
    },
    {
      "source_id": "S03",
      "url": "https://www.jd.com/hprm/98478710c0c450aa4d9a.html",
      "title": "一加6T 256g商城 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K03"]
    },
    {
      "source_id": "S04",
      "url": "https://post.smzdm.com/p/a5rdwdkl/",
      "title": "一加Ace 6T，骁龙8 Gen5+8300mAh大电池",
      "published_at": "2026-08-31T23:58:18+08:00",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["K03"]
    },
    {
      "source_id": "S05",
      "url": "https://www.jd.com/hprm/17329832487437f65220b.html",
      "title": "REDMI K90京东公开商品列表",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K04"]
    },
    {
      "source_id": "S06",
      "url": "https://item.m.jd.com/product/100215674663.html",
      "title": "REDMI K90 京东商品页",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K04", "K08"]
    },
    {
      "source_id": "S07",
      "url": "https://post.smzdm.com/p/aog30mgn/",
      "title": "倒反天罡还是金玉其外？红米K90评测",
      "published_at": "2025-12-25",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["K04"]
    },
    {
      "source_id": "S08",
      "url": "https://consumer.huawei.com/cn/support/content/zh-cn16075602/",
      "title": "HUAWEI Mate 80 用户指南适用产品",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K05"]
    },
    {
      "source_id": "S09",
      "url": "https://www.jd.com/hprm/998798f39c6efd1fa6e4.html",
      "title": "京东 HUAWEI Mate 系列公开商品列表",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K05"]
    },
    {
      "source_id": "S10",
      "url": "https://www.jd.com/hprm/17329969fd646058e5007.html",
      "title": "京东 Xiaomi 17 系列公开商品列表",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K06"]
    },
    {
      "source_id": "S11",
      "url": "https://www.jd.com/hprm/99878754483b6d828074.html",
      "title": "小米合约机套餐 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K06"]
    },
    {
      "source_id": "S12",
      "url": "https://www.mi.com/shop/buy/detail?product_id=21932",
      "title": "Xiaomi 17 Pro立即购买-小米商城",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K06"]
    },
    {
      "source_id": "S13",
      "url": "https://www.jd.com/hprm/6706f331bf4044a6c1b.html",
      "title": "京东 vivo X300 公开商品列表",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": ["K07"]
    },
    {
      "source_id": "S14",
      "url": "https://www.vivo.com.cn/vivo/param/x300",
      "title": "vivo X300 官方规格参数",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": ["K07"]
    },
    {
      "source_id": "S15",
      "url": "https://post.smzdm.com/p/awwzn20p/",
      "title": "vivo X300半年使用体验报告",
      "published_at": "2026-09-08",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": ["K07"]
    }
  ],
  "claims": [
    {"claim_id": "K01", "text": "S01当前明确iPhone 17 Pro 256GB银色TOP1、iPhone 17 256GB白色TOP2。", "source_ids": ["S01"]},
    {"claim_id": "K02", "text": "S02当前明确iPhone 18 Pro 256GB勃艮第TOP1、iPhone 17 256GB白色TOP2；榜序与S01不同。", "source_ids": ["S02"]},
    {"claim_id": "K03", "text": "OnePlus Ace 6T 12GB+256GB闪速黑国内精确零售条目及社区来源可复现；社区榜首转述不计作排名。", "source_ids": ["S03", "S04"]},
    {"claim_id": "K04", "text": "REDMI K90 12GB+256GB白色、骁龙8至尊版、7100mAh精确零售款可复现；当前item价格需选门店。", "source_ids": ["S05", "S06", "S07"]},
    {"claim_id": "K05", "text": "Mate 80及12GB+512GB型号容量存在，但12GB+512GB雪域白精确组合未闭环。", "source_ids": ["S08", "S09"]},
    {"claim_id": "K06", "text": "Xiaomi 17 Pro白色12GB+256GB仅复现合约专享；不得与普通版合并。", "source_ids": ["S10", "S11", "S12"]},
    {"claim_id": "K07", "text": "vivo X300 V2509A、12GB+256GB惬意紫及国内精确自营条目可闭环，并有国内长期使用社区证据。", "source_ids": ["S13", "S14", "S15"]},
    {"claim_id": "K08", "text": "未把评论数、未登录页、壳页、社区转述或补贴标识当作当日普通成交价或销量排名。", "source_ids": ["S01", "S02", "S03", "S06", "S10", "S13"]}
  ],
  "data_gaps": [
    "本轮未核验任何候选的2026-10-06普通非会员实际成交价；会员价、券价、国补价、历史/首发价均未拿来替代，未知保持null。",
    "Apple若干精确item详情为JS壳；head结论仅依可读京东榜页。",
    "OnePlus给定完整京东列表当前显示0+评价，原研究的20000+未在该页复现；评价数未参与裁决。",
    "HUAWEI Mate 80 12GB+512GB雪域白精确组合仍缺可读闭环证据。",
    "Xiaomi 17 Pro白色12GB+256GB普通版仍缺可读精确购买证据；已找到的合约专享版本不合并。"
  ]
}
```
=== UNEDITED MG CATEGORY AUDIT R2-domestic-batch01-recovery-C02; SHA256 2031de1f11ba6e9bcee143468af58b1b36647f01f03278c2c58027d19f69417d ===
结论：当前同一京东自营榜可直接核到小新16SE TOP1、天选7 Pro 1TB青 TOP2、R9000P 2026黑 TOP9；按最多2个head及同级字典序，保留天选7 Pro与小新16SE。[jd.com](https://www.jd.com/phb/key_67079ee30ffcf56ea8d.html) W2-B的10万评论阈值、W2-C的评论量筛选均不能升级成销量排名；前者页面当前是“综合”列表。[JD.com](https://www.jd.com/hotitem/6709c8e2fc71cca0b50.html) 机械革命无界14 2026灰的完整京东页核到226V/16G/1T/2.8K、买家评价及公开价5199元，“登录查看到手价”未知，故选为opportunity。[JD.com](https://item.jd.com/product/r4ApbAO8qxc4swIo6MqmFQ.html) 小米精确配置只有社区历史国补价与当前型号存在证据；a豆的H465/32G/1T有国内证据，但“风信子蓝”未闭合且官网产品页403，均不升级。[什么值得买](https://post.smzdm.com/p/arz0pz9q/)

```json
{"job_id":"R2-domestic-batch01-recovery-C02","web_research_available":true,"pre_freeze_compliance":true,"review_performed":true,"category_ids":["C02"],"candidate_audits":[{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H01","brand":"Lenovo","model":"小新16SE高能本","exact_variant":"标压锐龙R7 / 16GB / 512GB / 可扩展硬盘位","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":true,"source_ids":["S01"],"caveat":"京东自营榜TOP1；精确商品链接对应原item_id。单品详情为JS壳，当前价格未知。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H02","brand":"ASUS","model":"天选7 Pro 酷睿版","exact_variant":"16英寸 / Core Ultra 7 251HX / 16GB / 1TB / RTX 5060 / 2.5K 300Hz / 青","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":true,"source_ids":["S01"],"caveat":"京东自营榜TOP2；标题完整匹配1TB/RTX5060/青，链接对应原item_id；当前成交价未知。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-O01","brand":"Xiaomi","model":"Xiaomi Book Pro 14","exact_variant":"Ultra 5 325 / 24GB / 1TB","quality_grade":"PROVISIONAL_VARIANT","model_exists_verified":true,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S05","S06"],"caveat":"社区明确点名该配置并给出体验；小米官网确认当前型号及系列9499元起，但未闭合该24GB+1TB当前精确零售SKU。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-H01","brand":"REDMI","model":"REDMI Book 14 2025","exact_variant":"Core 5-210H; RAM/SSD未解析","quality_grade":"PROVISIONAL_VARIANT","model_exists_verified":true,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":["S02"],"caveat":"京东综合列表可核Core5-210H、自营及原item_id；RAM/SSD未闭合。10万+评论不作为销量排名。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-H02","brand":"Lecoo","model":"斗战者 战7000","exact_variant":"Ryzen 9 8940HX / 16GB / 1TB / RTX5070 / 2.5K 180Hz / 灰","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":["S02"],"caveat":"当前京东自营列表完整匹配配置及原item_id；但原head依据为综合列表中的评论阈值，不能认定销量头部。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-O01","brand":"MECHREVO","model":"无界14 2026","exact_variant":"Core Ultra 5 226V / 16GB / 1TB / 2.8K / 灰","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S04"],"caveat":"完整京东商品页核到精确版本、购买控件、多条买家评价及公开5199元；登录后到手价未知。未采用原AIGC文章作消费者证据。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-H1","brand":"HP","model":"战66 14 2026","exact_variant":"14英寸 AMD Ryzen 7 H255 / 16GB / 512GB SSD；颜色未声明","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":["S03"],"caveat":"当前京东自营列表与原item_id完整匹配H255/16G/512G；20万+评论不能作为销量排名。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-H2","brand":"Lenovo","model":"拯救者 R9000P 2026","exact_variant":"AMD Ryzen 9 8945HX / 16GB / 1TB SSD / RTX 5060 8GB / 碳晶黑","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":true,"source_ids":["S01","S03","S07"],"caveat":"京东自营榜当前TOP9；京东item匹配黑色配置，联想官方页确认8945HX/16G/1T/RTX5060/碳晶黑及型号LEGION R9000P ADR10M。联想商城该页同时显示已下架，价格为空。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-O1","brand":"ASUS","model":"a豆14 Air 2026","exact_variant":"AMD Ryzen AI 9 H465 / 32GB / 1TB SSD / 2.8K / 风信子蓝","quality_grade":"PROVISIONAL_VARIANT","model_exists_verified":true,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S03","S05","S08"],"caveat":"京东自营列表核到H465/32G/1T/2.8K/蓝，社区亦点名H465/32G+1T；精确色名“风信子蓝”未由可读官方页闭合，ASUS产品页403。"}],"recommended_selection":[{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H02","brand":"ASUS","model":"天选7 Pro 酷睿版","exact_variant":"16英寸 / Core Ultra 7 251HX / 16GB / 1TB / RTX 5060 / 2.5K 300Hz / 青","category_id":"C02","sampling_stratum":"domestic_head","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","reason":"真实京东自营TOP2+精确版本；同级按brand/model/variant字典序优先。","source_ids":["S01"]},{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H01","brand":"Lenovo","model":"小新16SE高能本","exact_variant":"标压锐龙R7 / 16GB / 512GB / 可扩展硬盘位","category_id":"C02","sampling_stratum":"domestic_head","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","reason":"真实京东自营TOP1+精确SKU；在剩余同级Lenovo候选中字典序先于拯救者R9000P。","source_ids":["S01"]},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-O01","brand":"MECHREVO","model":"无界14 2026","exact_variant":"Core Ultra 5 226V / 16GB / 1TB / 2.8K / 灰","category_id":"C02","sampling_stratum":"domestic_opportunity","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","reason":"完整国内商品页同时闭合精确版本、购买信号和真实买家评价；公开普通价5199元。","source_ids":["S04"]}],"exclusion_log":[],"category_gaps":["W2-B的评论阈值及W2-C的评论量筛选均未核成销量排名。","多数原JD数字item详情直接打开仅返回page_shell；未登录，故普通/会员/券/国补到手价多数为null。","Xiaomi Book Pro 14的24GB+1TB当前精确零售SKU未闭合；a豆“风信子蓝”精确色名未闭合。"],"sources":[{"source_id":"S01","url":null,"title":"自营笔记本排行榜 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["小新16SE TOP1","天选7 Pro 1TB青 TOP2","R9000P 2026黑 TOP9","对应商品链接及晒单评论"]},{"source_id":"S02","url":null,"title":"新款笔本电脑排行 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["REDMI Book 14 2025 Core5-210H自营","Lecoo战7000精确配置自营","页面默认为综合排序并显示评论数"]},{"source_id":"S03","url":null,"title":"笔记本电脑京东自营 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["HP战66 H255/16G/512G精确列表","R9000P黑色精确列表","a豆14 Air H465/32G/1T/2.8K/蓝列表"]},{"source_id":"S04","url":null,"title":"机械革命无界14 2026（Ultra 5 226V/16G/1T/2.8K/灰）京东商品页","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["精确版本","买家评价","公开价格5199元","登录查看到手价"]},{"source_id":"S05","url":null,"title":"涨价还减配 2026新生笔记本怎么选？28款实测笔记本选购指南来了","published_at":"2026-07-21T09:59:39+08:00","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["Xiaomi Book Pro 14 Ultra5-325/24G+1T历史国补约6725","a豆14 Air H465/32G+1T历史国补约6975","国内使用体验"]},{"source_id":"S06","url":null,"title":"Xiaomi Book Pro 14 - 小米官网","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["型号当前存在","系列9499元起；不能映射为24GB+1TB精确价"]},{"source_id":"S07","url":null,"title":"联想拯救者R9000P 2026 碳晶黑 - 联想商城","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["LEGION R9000P ADR10M","8945HX/16GB/1TB/RTX5060/碳晶黑","页面显示商品已下架且当前价为空"]},{"source_id":"S08","url":null,"title":"a豆14 Air 2026 M5451GA - ASUS中国产品页","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"blocked","claims_supported":[]}],"claims":[{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H01","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"精确SKU当前价格未核到。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-H02","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"精确SKU当前价格未核到。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C02-O01","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":6725,"old_price_type":"historical_subsidy","price_note":"2026-07-21社区记录京东国补后约6725；当前精确配置普通价未知。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-H01","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"当前精确内存/存储未闭合，价格不分配。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-H02","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"当前价格未核到。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C02-O01","ordinary_price_cny":5199,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"公开商品页显示5199；另显示“登录查看到手价”，未登录。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-H1","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"当前精确SKU价格未核到。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-H2","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"京东精确SKU当前价未核到；联想官方精确商品页显示已下架且价格为空。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C02-O1","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":6975,"old_price_type":"historical_subsidy","price_note":"2026-07-21社区记录京东国补后约6975；当前精确色名及当前价格未闭合。"}],"data_gaps":[{"gap":"JD direct item pages returned page_shell","affected_item_ids":["100309811503","100352388758","100167105512","100412589176","100252158679","100349257480","100236629447"],"impact":"不能据壳页确认当前成交价、会员价、券价或国补到手价；未重复请求、未登录。"},{"gap":"ASUS exact product crosscheck blocked","affected":["W2-C-batch01/C02-O1"],"access_state":"blocked","impact":"风信子蓝精确色名未闭合。"},{"gap":"Xiaomi exact live retail mapping unresolved","affected":["W2-A-batch01/C02-O01"],"impact":"型号和社区配置存在，但当前24GB+1TB精确零售item及普通价未知。"}]}
```
=== UNEDITED MG CATEGORY AUDIT R2-domestic-batch01-recovery-C03; SHA256 cd1c473521fdcbda1b00dcd38729b9ef7f5bc4f4e06803c211d85a4d778e7aad ===
审计完成9/9。京东自营榜现为A16 256银#1、128银#2、Air M4 256深空灰#3、紫#4；因此W2-A紫色款虽“排名+精确版本”成立，却不是其family去重规则下第二family的首SKU，不计verified-head。[JD.com](https://www.jd.com/phb/key_67011e02cc61d0fb721.html)

REDMI 16+512深邃黑、MatePad Mini 12+256曜石黑均有当前国内自营精确条目，但评论量不能升格销量头部。MatePad 11.5榜6未标2026，官方只能证明2026柔光12+256配置存在；Pad 8当前公开列表仅见12+256冰晶蓝及8+256黑色，12+256黑色未闭环。[JD.com](https://www.jd.com/brand/67079349596d1459d1f.html)

推荐两个不同容量A16头部；跨研究重复的256GB同一SKU只荐一条。机会层Lenovo Y700五代与REDMI同级，按NFKC/casefold品牌字典序选Lenovo；其12+256 Wi-Fi碳晶黑有联想商城精确购买页及国内社区实测。[Lenovo](https://s.lenovo.com.cn/search?key=%E6%8B%AF%E6%95%91%E8%80%85y700\&page=2\&type=home)

```json
{"job_id":"R2-domestic-batch01-recovery-C03","web_research_available":true,"pre_freeze_compliance":true,"review_performed":true,"category_ids":["C03"],"candidate_audits":[{"original_job_id":"W2-A-batch01","original_candidate_id":"C03-H01","brand":"Apple","model":"iPad 11英寸（A16，2025）","exact_variant":"256GB WLAN 银色","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":false,"source_ids":["S01","S02"],"caveat":"京东自营榜#1；Apple中国精确购买页。普通公开价4299元；会员/券/国补/旧价未核验。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C03-H02","brand":"Apple","model":"iPad Air 11英寸（M4，2026）","exact_variant":"256GB WLAN 紫色","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S01","S03","S04"],"caveat":"实际为榜#4；榜#3是同family的256GB深空灰，故不满足原family去重后的第二family首SKU规则。"},{"original_job_id":"W2-A-batch01","original_candidate_id":"C03-O01","brand":"REDMI","model":"REDMI K Pad","exact_variant":"16GB+512GB 深邃黑 / 天玑9400+ / 8.8英寸3K","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S05","S06"],"caveat":"京东自营精确条目成立；2026-08-24社区2704元为历史到手价且优惠构成不明，不作当前普通价。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C03-H01","brand":"Apple","model":"iPad 11英寸（A16，2025）","exact_variant":"256GB WLAN 银色","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":false,"source_ids":["S01","S02"],"caveat":"京东自营榜#1；与W2-A/C03-H01为同一物理SKU/item 100195510718，审计记录不合并，推荐层去重。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C03-H02","brand":"Apple","model":"iPad 11英寸（A16，2025）","exact_variant":"128GB WLAN 银色","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":true,"domestic_consumer_evidence_verified":true,"source_ids":["S01","S02"],"caveat":"京东自营榜#2且有晒单评价；Apple中国同配置普通公开价3799元。会员/券/国补/旧价未核验。"},{"original_job_id":"W2-B-batch01","original_candidate_id":"C03-O01","brand":"HUAWEI","model":"MatePad 11.5","exact_variant":"柔光版 / 12GB+256GB / 深空灰；年份未闭环","quality_grade":"PROVISIONAL_VARIANT","model_exists_verified":true,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S07","S08","S16"],"caveat":"京东榜#6精确到柔光/12+256/深空灰，但标题未标2026；官方证明2026柔光Wi-Fi 12+256存在，壳页不足以同一年份。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C03-H1","brand":"HUAWEI","model":"MatePad Mini","exact_variant":"SIM卡版/可通话 / 12GB+256GB / 曜石黑","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":["S09","S10"],"caveat":"当前京东自营精确条目可见；10万+评论仅是评论量，不是销量排名，故原head未核验。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C03-H2","brand":"Xiaomi","model":"Xiaomi Pad 8","exact_variant":"12GB+256GB 黑色","quality_grade":"PROVISIONAL_VARIANT","model_exists_verified":true,"exact_variant_verified":false,"head_status_verified":false,"domestic_consumer_evidence_verified":false,"source_ids":["S11","S12","S15"],"caveat":"小米国内官网确认Pad 8机型；当前京东自营列表见12+256冰晶蓝和8+256黑色，候选12+256黑色未闭环，指定item页为壳页。"},{"original_job_id":"W2-C-batch01","original_candidate_id":"C03-O1","brand":"Lenovo","model":"拯救者 Y700 五代","exact_variant":"8.8英寸 / 12GB+256GB / Wi-Fi / 碳晶黑","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","model_exists_verified":true,"exact_variant_verified":true,"head_status_verified":false,"domestic_consumer_evidence_verified":true,"source_ids":["S13","S14"],"caveat":"联想商城精确版本当前可买，标示4299元并另标“下单立减”；减免额、会员/券/国补/旧价未核验。"}],"recommended_selection":[{"original_job_id":"W2-B-batch01","original_candidate_id":"C03-H02","brand":"Apple","model":"iPad 11英寸（A16，2025）","exact_variant":"128GB WLAN 银色","category_id":"C03","sampling_stratum":"domestic_head","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","reason":"京东自营榜#2精确SKU；128GB与256GB按要求不合并，同级按规范化variant字典序在前。","source_ids":["S01","S02"]},{"original_job_id":"W2-A-batch01","original_candidate_id":"C03-H01","brand":"Apple","model":"iPad 11英寸（A16，2025）","exact_variant":"256GB WLAN 银色","category_id":"C03","sampling_stratum":"domestic_head","quality_grade":"VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT","reason":"京东自营榜#1精确SKU；与W2-B/C03-H01完全相同物理SKU，推荐层仅保留一条。","source_ids":["S01","S02"]},{"original_job_id":"W2-C-batch01","original_candidate_id":"C03-O1","brand":"Lenovo","model":"拯救者 Y700 五代","exact_variant":"8.8英寸 / 12GB+256GB / Wi-Fi / 碳晶黑","category_id":"C03","sampling_stratum":"domestic_opportunity","quality_grade":"VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT","reason":"联想官方商城精确购买证据+国内社区实测；与REDMI同级时按NFKC/casefold品牌字典序Lenovo优先。","source_ids":["S13","S14"]}],"exclusion_log":[],"category_gaps":["W2-A/C03-H02虽有精确榜位，但不满足其原family去重抽样规则，不进入verified-head统计。","W2-C两个head均以评论量列表为依据，未核验销量榜位，不进入verified-head统计。","去除跨job完全重复SKU后，本轮可核验的推荐head仅A16 128GB与256GB两个物理SKU。"],"sources":[{"source_id":"S01","url":"https://www.jd.com/phb/key_67011e02cc61d0fb721.html","title":"京东自营商品平板排行榜","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K01"]},{"source_id":"S02","url":"https://www.apple.com.cn/shop/buy-ipad/ipad/md4g4ch/a","title":"购买 iPad 无线局域网机型 256GB - 银色 - Apple 中国大陆","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K02"]},{"source_id":"S03","url":"https://www.apple.com.cn/shop/buy-ipad/ipad-air/mh394ch/a","title":"购买 11 英寸 iPad Air 无线局域网机型 256GB - 紫色","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S04","url":"https://www.apple.com.cn/newsroom/2026/03/apple-introduces-the-new-ipad-air-powered-by-m4/","title":"Apple 推出新款 iPad Air，由 M4 芯片强势驱动","published_at":"2026-03-02","retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K03"]},{"source_id":"S05","url":"https://www.jd.com/brand/67079349596d1459d1f.html","title":"小米/REDMI平板商品列表 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K04"]},{"source_id":"S06","url":"https://post.smzdm.com/p/aqrxpzzv/","title":"7.3折！REDMI K Pad开启“清仓模式”","published_at":"2026-08-24T20:22:42+08:00","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K04","K05"]},{"source_id":"S07","url":"https://www.jd.com/phb/key_67067bf6d9ab64fd861.html","title":"平板笔记本排行榜 - 京东","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K06"]},{"source_id":"S08","url":"https://consumer.huawei.com/cn/support/content/zh-cn16079506/","title":"HUAWEI MatePad 11.5 2026 用户指南","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K06"]},{"source_id":"S09","url":"https://www.jd.com/hprm/9987cc1220ccf6c641d5.html","title":"京东 MatePad Mini 自营商品列表","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K07"]},{"source_id":"S10","url":"https://consumer.huawei.com/cn/tablets/matepad-mini/specs/","title":"HUAWEI MatePad Mini 规格参数","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K07"]},{"source_id":"S11","url":"https://www.jd.com/hprm/670ca81522efb20c111.html","title":"小米平板京东自营商品列表","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"read_full_page","claims_supported":["K08"]},{"source_id":"S12","url":"https://www.mi.com/shop/buy/detail?product_id=21872","title":"Xiaomi Pad 8 - 小米商城","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K08"]},{"source_id":"S13","url":"https://s.lenovo.com.cn/search/?key=%E6%8B%AF%E6%95%91%E8%80%85y700&page=2&type=home","title":"拯救者Y700 - 联想商城搜索结果第2页","published_at":null,"retrieved_at":"2026-10-06","source_type":"official","access_state":"read_full_page","claims_supported":["K09","K10"]},{"source_id":"S14","url":"https://post.smzdm.com/p/aggmm973/","title":"谁说小屏难称王？联想AI平板拯救者Y700五代评测！","published_at":"2026-04-02T11:19:22+08:00","retrieved_at":"2026-10-06","source_type":"community","access_state":"read_full_page","claims_supported":["K09"]},{"source_id":"S15","url":"https://item.jd.com/100279475542.html","title":"京东商品 100279475542","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":[]},{"source_id":"S16","url":"https://item.jd.com/100230964203.html","title":"京东商品 100230964203","published_at":null,"retrieved_at":"2026-10-06","source_type":"secondary","access_state":"page_shell","claims_supported":[]}],"claims":[{"claim_id":"K01","statement":"京东自营平板榜：A16 256GB银#1、A16 128GB银#2、Air M4 256GB深空灰#3、紫色#4。","source_ids":["S01"]},{"claim_id":"K02","subject":"Apple iPad A16 WLAN银色","ordinary_price_cny":{"128GB":3799,"256GB":4299},"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"source_ids":["S02"]},{"claim_id":"K03","statement":"Apple中国当前精确页面确认11英寸iPad Air WLAN 256GB紫色，页面机型比较确认M4。","source_ids":["S03","S04"]},{"claim_id":"K04","statement":"REDMI K Pad 16+512GB深邃黑当前京东自营精确条目可见；国内社区明确推荐16+512版本。","source_ids":["S05","S06"]},{"claim_id":"K05","subject":"REDMI K Pad 16+512GB","ordinary_price_cny":null,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":2704,"price_note":"2026-08-24社区所述到手价；优惠构成不明，不作当前普通价。","source_ids":["S06"]},{"claim_id":"K06","statement":"京东榜#6为MatePad 11.5柔光12+256深空灰但未标2026；华为官方2026指南列有柔光Wi-Fi 12+256，二者年份不能凭现有证据同一。","source_ids":["S07","S08"]},{"claim_id":"K07","statement":"MatePad Mini SIM卡可通话12+256曜石黑当前京东自营条目可见；评论量不构成销量排名。","source_ids":["S09","S10"]},{"claim_id":"K08","statement":"Xiaomi Pad 8机型存在，但当前公开自营列表只闭环12+256冰晶蓝与8+256黑色，未闭环12+256黑色。","source_ids":["S11","S12"]},{"claim_id":"K09","statement":"联想商城闭环Y700五代8.8英寸12+256 Wi-Fi碳晶黑；国内社区有2026-04-02实测。","source_ids":["S13","S14"]},{"claim_id":"K10","subject":"Lenovo 拯救者Y700五代12+256 Wi-Fi碳晶黑","ordinary_price_cny":4299,"member_price_cny":null,"coupon_price_cny":null,"subsidy_price_cny":null,"old_price_cny":null,"price_note":"官网同时标注“下单立减”，减免额未核验，未并入4299。","source_ids":["S13"]}],"data_gaps":["W2-B/C03-O01的京东精确item页为page_shell，无法锁定榜#6商品年份为2026。","W2-C/C03-H2的京东精确item页为page_shell，12+256黑色版本未获完整国内页面闭环。","除已列Apple A16、Lenovo及REDMI历史到手价外，其余当前普通价及未核验会员/券/国补/旧价均保持null。"]}
```