审计完成。三份材料共 **27 个候选**均逐项保留，没有任何候选满足你限定的可排除理由，因此 `exclusion_log=[]`；因版本、尺码、套装、登录态或电商风控不足的，只降级、不删样本。本次没有查询任何候选的海外价格、销量、覆盖、供货或进口节省。核心口径是：京东 `phb` 页面明确显示“排名/热卖商品”时，可以核验“国内榜单位置”，但旁边的“已有X人评论”只能记为评论存量，不能称为销量；普通 `brand/hprm/cppf/xinghao` 商品页即使同时有“销量”排序选项，若本次打开的是默认“综合”状态，也不能倒推成销量榜。[JD.com](https://www.jd.com/phb/key_6728e5a1cbd85878c58f.html)

C13 中，M800Pro 与 MINIPro 4K 的榜单链接可分别回连到相同 item，并进一步锁定“无卡/无卡套餐”，因此是两项真正的 `rank+exact`。A810Pro 则必须降级：原 W2-A 的“主机+128G卡×双镜头”能定义，但精确卡片当次显示 0+ 评论；其他 A810Pro 的较高评论池不能跨变体转移。充气宝2D、MJCQB06QW、DL8060、青春版2可以取得精确国内商品或实购证据，但通用充气泵页不是已核销量榜，所以都不能算 verified-head。[JD.com](https://www.jd.com/hprm/6704262580d296f9049.html)

C14 的主要问题是“榜位真实、SKU却未完全锁定”：毒刺7代在同一跑鞋榜重复占位，吾跃3.0 ARSV024也存在多颜色/尺码，因此不能把型号级榜位升级成精确SKU级头部；两千公里五代标准版和PRO版虽在榜上分开，但原候选仍缺尺码/配色。相对而言，战戟5000 4U、F4002、冷山2PLUS NXZQU61017可以取得精确国内购买/评论证据，却没有已核的全市场头部排名。云尚PRO引用的社区页明确带 AIGC/AI生成标记，只作低权重线索。故 C14 的 **verified-head 计数为0**。[JD.com](https://www.jd.com/phb/key_1318b0cd67e76e23160b.html)

C15 修正幅度最大：3D打印榜本身存在爱普生2D打印机污染；P2SC/P2S多色套装确实是 TOP2，且精确商品页可锁到 item 100285504398，不能与同榜另一独立“大陆版P2SC”套装合并。A1榜位存在，但原 W2-A 套装边界未锁；反而 A1单机大陆版、A1 mini单机大陆版的精确购买页能直接核验。Space Pi V2 Plus 原报告写 TOP1，经复核实际是“三维打印耗材排行榜” **TOP2**，所以只能作为配套设备机会候选，而不是打印机头部。最终严格口径的 verified-head 为 **C13=2、C14=0、C15=1**。[JD.com](https://www.jd.com/phb/key_6708052b8ebbbc3eabc.html)

价格只记录公开可归属到精确SKU的普通展示价：充气宝2D 159元、米家充气宝2 179元、P2S多色套装4799元、A1单机1599元、A1 mini单机1269元；这些页面均要求登录查看最终到手价。因此会员价、88VIP、定向券、国补、旧价没有证据时全部为 `null`，也没有把社区历史购入价或优惠页旧数字冒充当前价。[JD.com](https://item.jd.com/product/FUQjUkVHZnGJ4JviSEN6_w.html)

```json
{
  "job_id": "R2-domestic-batch05",
  "web_research_available": true,
  "pre_freeze_compliance": true,
  "review_performed": true,
  "category_ids": [
    "C13",
    "C14",
    "C15"
  ],
  "candidate_audits": [
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C13-H1",
      "brand": "70迈 (70MAI)",
      "model": "M800Pro",
      "exact_variant": "2026新款；前后双录；4K；4G停车监控；无卡，item_id 100357791508",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S01",
        "S02"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "京东“行车记录仪吧排行榜”链接到该item；另页把同一item映射为“无卡”。榜单是热卖排名，不是公开成交件数；评论量也不是销量。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C13-H2",
      "brand": "盯盯拍 (DDPAI)",
      "model": "MINIPro 4K",
      "exact_variant": "2026新款；4K；360度旋转；停车监控；无卡套餐，item_id 100323403254",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S01",
        "S03"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "榜单链接与“无卡套餐”item一致；存储卡/供电线等其他套餐不得合并。榜单名次与评论数均不等同真实成交量。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C13-O1",
      "brand": "70迈 (70MAI)",
      "model": "A810Pro",
      "exact_variant": "4K前摄；前后双摄；套餐一：主机+128G卡×双镜头",
      "quality_grade": "VERIFIED_MODEL_ONLY_HEAD_UNVERIFIED",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S04",
        "S05"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "精确套餐可定义，但该精确卡片当次为0+评论；同页其他A810Pro的高评论池不得转移给此套餐。汽车之家仅证明A810Pro型号级国内使用，不证明该128G双镜头套餐的购买量。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C14-H1",
      "brand": "安踏 (ANTA)",
      "model": "毒刺7代",
      "exact_variant": "男款无板竞训缓震跑鞋；黑色；尺码/款号未锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S12"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "榜单中毒刺7代重复占多个名次，说明存在重复/聚合；原候选未锁尺码和款号，不能把型号级榜单直接当精确SKU头部。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C14-H2",
      "brand": "李宁 (LI-NING)",
      "model": "吾跃3.0",
      "exact_variant": "ARSV024；女款网面体测跑鞋；尺码/配色未锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S12"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "可核到吾跃3.0 ARSV024进入该榜，但同型号有多个颜色/尺码条目，评论池可能聚合；精确子变体未锁。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C14-O1",
      "brand": "特步 (XTEP)",
      "model": "两千公里五代",
      "exact_variant": "标准版（非PRO）男子跑鞋；尺码/配色未锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S13",
        "S28"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "特步品牌运动鞋榜可见标准版与PRO版分列，标准版有国内使用文；但该候选尺码/配色未锁，且品牌内榜不能当全市场头部。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C15-H1",
      "brand": "拓竹 (Bambu Lab)",
      "model": "P2SC / P2S Combo",
      "exact_variant": "P2S 多色套装，item_id 100285504398；该标题未标“大陆版”",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S20",
        "S21"
      ],
      "price_audit": {
        "ordinary_cny": 4799,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S21"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "3D打印热卖榜TOP2链接到该精确套装；同榜另有“大陆版P2SC”独立item/名次，二者不得合并。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C15-H2",
      "brand": "拓竹 (Bambu Lab)",
      "model": "A1",
      "exact_variant": "A1 大陆版；单机还是含AMS lite组合未从该榜单item锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": true,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S20",
        "S22"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "A1型号及大陆版榜位可核，但原item的单机/组合边界未锁；官网只能证明型号/规格，不证明销量。"
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C15-O1",
      "brand": "Snapmaker 快造",
      "model": "U1",
      "exact_variant": "U1 独立4打印头桌面FDM机；具体销售包/配件未锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S20",
        "S23"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "榜单可核到U1条目且官网确认硬件型号；原候选销售包未锁，且其榜位只支撑机会样本，不提升为verified-head。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C13-01",
      "brand": "小米",
      "model": "充气宝2D",
      "exact_variant": "无线车载充气泵；型号MJCQB07QWS",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S06",
        "S07"
      ],
      "price_audit": {
        "ordinary_cny": 159,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S07"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确京东商品页可读型号和买家评价；通用充气泵页的高评论量是评论存量，不是销量榜。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C13-02",
      "brand": "70迈",
      "model": "A810Pro",
      "exact_variant": "4K超清夜视/黑光全彩/无卡+监控线",
      "quality_grade": "VERIFIED_MODEL_ONLY_HEAD_UNVERIFIED",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": false,
      "source_ids": [
        "S04"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "该配置名称可在国内商品卡中定义，但可见高评论量来自A810Pro商品族/多变体页，未隔离到“无卡+监控线”精确子SKU；无销量榜证据。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C13-03",
      "brand": "小米",
      "model": "MJCQB06QW",
      "exact_variant": "米家充气宝2 MJCQB06QW",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S06",
        "S08",
        "S09"
      ],
      "price_audit": {
        "ordinary_cny": 179,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S08"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确型号页和国内实购使用文均可核；通用页评论数仅作采用度证据，不解释为销量。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C14-01",
      "brand": "李宁",
      "model": "战戟5000",
      "exact_variant": "4U 空拍",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S14",
        "S15"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "国内零售页可核4U空拍版本并有消费者评论；社区实战只核到战戟5000型号，不单独证明4U。原报告所谓“自营排行”打开后是普通商品/品牌页，不能据此认定头部。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C14-02",
      "brand": "红双喜",
      "model": "F4002",
      "exact_variant": "狂飚四星级升级版横拍/双面反胶/附乒乓球，item_id 100007817692",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S16"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "精确商品卡和item可核且有国内评论；打开页是型号/商品列表，默认不是销量排名，因此不计verified-head。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C14-03",
      "brand": "霜将",
      "model": "青蛇 Pro",
      "exact_variant": null,
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S15"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "国内实测文明确型号并称使用约一个月，但同时列3U/4U、G5/G6，未说明被测组合，也未核到精确零售item。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C15-01",
      "brand": "拓竹",
      "model": "A1",
      "exact_variant": "单机/大陆版",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S24",
        "S25"
      ],
      "price_audit": {
        "ordinary_cny": 1599,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S25"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确A1单机大陆版商品页与买家评价可核；普通品牌页并非默认销量榜，不能把高评论量当头部销量。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C15-02",
      "brand": "拓竹",
      "model": "A1C",
      "exact_variant": "大陆版；具体套装内容未锁定",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S20",
        "S24"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "A1C大陆版型号和榜单条目可核，但原候选套装内容未锁；不能把聚合评论归因到未定义的精确套装。"
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C15-03",
      "brand": "拓竹",
      "model": "A1 mini",
      "exact_variant": "单机/大陆版",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S24",
        "S26",
        "S29"
      ],
      "price_audit": {
        "ordinary_cny": 1269,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S26"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确单机大陆版商品页和买家评价可核；品牌页评论量为采用度信号而非销量排名。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C13-H01",
      "brand": "米家",
      "model": "MJCQB06QW",
      "exact_variant": "米家充气宝2 MJCQB06QW",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S06",
        "S08",
        "S09"
      ],
      "price_audit": {
        "ordinary_cny": 179,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S08"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确型号与国内购买证据成立；原报告把通用页高评论量用作头部信号，但该页默认并非销量榜，因此head未核验。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C13-H02",
      "brand": "得力",
      "model": "DL8060",
      "exact_variant": "DL8060 双缸180W车载充气泵",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S06",
        "S10"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "国内作者明确称在京东下单DL8060并使用；京东通用页“得力双缸”高评论卡不能无条件映射到DL8060，因此只认精确实购，不认头部。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C13-O01",
      "brand": "70迈",
      "model": "青春版2",
      "exact_variant": "汽车轮胎充气泵青春版2 2026新款，item_id 100421361642",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S11"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "精确2026新款国内商品卡与消费者评论可核；评论量低且无销量榜证据，保留机会层。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C14-H01",
      "brand": "Naturehike/挪客",
      "model": "Village 6.0",
      "exact_variant": "屋脊6.0二代_深咖（聚合变体映射未锁）",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S17"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "品牌页把二代、三代、旗舰版、地布等聚合展示；评论池不能精确归属二代深咖，且页面不是销量榜。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C14-H02",
      "brand": "MOBI GARDEN/牧高笛",
      "model": "NXZQU61017",
      "exact_variant": "冷山2PLUS 红灰色 双人 带雪裙",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S18"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "国内商品页可核完整型号、颜色和带雪裙双人版本并有评论；它是普通商品列表，不是已核销量榜。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C14-O01",
      "brand": "Naturehike/挪客",
      "model": "云尚PRO",
      "exact_variant": "浅灰红/2人/20D尼龙（聚合变体映射未锁）",
      "quality_grade": "PROVISIONAL_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": false,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S17",
        "S19"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "京东品牌页存在云尚PRO多颜色/人数聚合；引用的SMZDM内容明确标记AIGC并由AI生成，只作低权重线索，不作为独立真人实测。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C15-H01",
      "brand": "Bambu Lab/拓竹",
      "model": "A1",
      "exact_variant": "A1 单机 大陆版",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S24",
        "S25"
      ],
      "price_audit": {
        "ordinary_cny": 1599,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S25"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确单机大陆版商品页及买家评价成立；其来源不是销量榜，故原“domestic_head”身份不进入verified-head统计。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C15-H02",
      "brand": "Bambu Lab/拓竹",
      "model": "A1 mini",
      "exact_variant": "A1 mini 单机 大陆版",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S24",
        "S26",
        "S29"
      ],
      "price_audit": {
        "ordinary_cny": 1269,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [
          "S26"
        ],
        "note": "仅为未登录公开普通展示价；页面要求登录查看到手价，其他价格字段不推断。"
      },
      "caveat": "精确单机大陆版商品页及买家评价成立；品牌页评论量不是销量。"
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C15-O01",
      "brand": "Creality 3D/创想三维",
      "model": "Space Pi V2 Plus",
      "exact_variant": "Space Pi V2 Plus 大陆版",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "model_exists_verified": true,
      "exact_variant_verified": true,
      "head_status_verified": false,
      "domestic_consumer_evidence_verified": true,
      "source_ids": [
        "S27"
      ],
      "price_audit": {
        "ordinary_cny": null,
        "member_cny": null,
        "vip88_cny": null,
        "targeted_coupon_cny": null,
        "national_subsidy_cny": null,
        "old_price_cny": null,
        "source_ids": [],
        "note": "未登录可见字段不足；不猜成交价。"
      },
      "caveat": "可核为京东“三维打印耗材排行榜”TOP2而非原报告所称TOP1；这是耗材/配套设备子榜，不是3D打印机本体头部榜，因此保留机会层。"
    }
  ],
  "recommended_selection": [
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C13-H1",
      "brand": "70迈 (70MAI)",
      "model": "M800Pro",
      "exact_variant": "2026新款；前后双录；4K；4G停车监控；无卡，item_id 100357791508",
      "category_id": "C13",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "优先级最高：同一国内热卖榜名次与榜单链接item均已核，且同一item可锁到无卡版本；在同级候选中按NFKC/casefold字典序先于盯盯拍。",
      "source_ids": [
        "S01",
        "S02"
      ]
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C13-H2",
      "brand": "盯盯拍 (DDPAI)",
      "model": "MINIPro 4K",
      "exact_variant": "2026新款；4K；360度旋转；停车监控；无卡套餐，item_id 100323403254",
      "category_id": "C13",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "第二个rank+exact候选；榜单链接item与无卡套餐映射一致。评论数不作销量件数解释。",
      "source_ids": [
        "S01",
        "S03"
      ]
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C13-O01",
      "brand": "70迈",
      "model": "青春版2",
      "exact_variant": "汽车轮胎充气泵青春版2 2026新款，item_id 100421361642",
      "category_id": "C13",
      "sampling_stratum": "domestic_opportunity",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "reason": "机会层中与米家充气宝2同为purchase+exact；按品牌/型号/版本NFKC/casefold字典序，70迈先于小米，因此选入。无头部认定。",
      "source_ids": [
        "S11"
      ]
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C14-H02",
      "brand": "MOBI GARDEN/牧高笛",
      "model": "NXZQU61017",
      "exact_variant": "冷山2PLUS 红灰色 双人 带雪裙",
      "category_id": "C14",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "reason": "C14没有rank+exact可用头部；按回退规则先取purchase+exact。与战戟5000、F4002同级时，MOBI GARDEN/牧高笛按NFKC/casefold字典序最先。该记录占head采样槽但不计verified-head。",
      "source_ids": [
        "S18"
      ]
    },
    {
      "original_job_id": "W2-B-batch05",
      "original_candidate_id": "W2B05-C14-01",
      "brand": "李宁",
      "model": "战戟5000",
      "exact_variant": "4U 空拍",
      "category_id": "C14",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "reason": "同为purchase+exact回退头部槽；在剩余同级候选中李宁按NFKC/casefold字典序先于红双喜。原“排行”未核为销量榜，所以不计verified-head。",
      "source_ids": [
        "S14",
        "S15"
      ]
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C14-O01",
      "brand": "Naturehike/挪客",
      "model": "云尚PRO",
      "exact_variant": "浅灰红/2人/20D尼龙（聚合变体映射未锁）",
      "category_id": "C14",
      "sampling_stratum": "domestic_opportunity",
      "quality_grade": "PROVISIONAL_VARIANT",
      "reason": "机会候选均为PROVISIONAL_VARIANT时按NFKC/casefold字典序，Naturehike/挪客先于特步和霜将。AIGC社区页不作为真人实测加分，故仍保持PROVISIONAL。",
      "source_ids": [
        "S17",
        "S19"
      ]
    },
    {
      "original_job_id": "W2-A-batch05",
      "original_candidate_id": "C15-H1",
      "brand": "拓竹 (Bambu Lab)",
      "model": "P2SC / P2S Combo",
      "exact_variant": "P2S 多色套装，item_id 100285504398；该标题未标“大陆版”",
      "category_id": "C15",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "C15中唯一可直接锁定到原头部候选的rank+exact记录；与同榜独立“大陆版P2SC”不合并。",
      "source_ids": [
        "S20",
        "S21"
      ]
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C15-H01",
      "brand": "Bambu Lab/拓竹",
      "model": "A1",
      "exact_variant": "A1 单机 大陆版",
      "category_id": "C15",
      "sampling_stratum": "domestic_head",
      "quality_grade": "VERIFIED_DOMESTIC_PURCHASE_AND_EXACT_VARIANT",
      "reason": "第二头部槽按回退规则取purchase+exact；同级A1/A1 mini及重复候选按品牌/型号/版本NFKC/casefold排序，Bambu Lab/拓竹 A1先。该项不计verified-head。",
      "source_ids": [
        "S24",
        "S25"
      ]
    },
    {
      "original_job_id": "W2-C-batch05-recovery01",
      "original_candidate_id": "C15-O01",
      "brand": "Creality 3D/创想三维",
      "model": "Space Pi V2 Plus",
      "exact_variant": "Space Pi V2 Plus 大陆版",
      "category_id": "C15",
      "sampling_stratum": "domestic_opportunity",
      "quality_grade": "VERIFIED_DOMESTIC_RANK_AND_EXACT_VARIANT",
      "reason": "机会层有精确国内榜单证据；实际是三维打印耗材/配套设备榜TOP2，不是打印机本体榜，因此保留为opportunity而非head。",
      "source_ids": [
        "S27"
      ]
    }
  ],
  "exclusion_log": [],
  "category_gaps": [
    {
      "category_id": "C13",
      "verified_head_count": 2,
      "as_of": "2026-10-06",
      "gap": "仅M800Pro与MINIPro同时满足国内榜单+精确版本。A810Pro及充气泵候选多为普通商品页评论/实购证据；普通页的“销量”标签未被选中，不能把默认综合页当销量榜。",
      "source_ids": [
        "S01",
        "S04",
        "S06"
      ]
    },
    {
      "category_id": "C14",
      "verified_head_count": 0,
      "as_of": "2026-10-06",
      "gap": "跑鞋榜可验证毒刺7代/吾跃3.0的型号级榜位，但尺码/配色未锁；战戟5000、F4002、冷山2PLUS只有精确国内购买/评论证据，未验证全市场头部。C14各研究复本采了跑鞋、球拍、帐篷等不同子类，子榜不可互相当作统一销量榜。",
      "source_ids": [
        "S12",
        "S14",
        "S16",
        "S18"
      ]
    },
    {
      "category_id": "C15",
      "verified_head_count": 1,
      "as_of": "2026-10-06",
      "gap": "P2S多色套装满足rank+exact；A1榜单item的单机/组合边界未锁，A1/A1 mini精确单机页只是购买证据。3D榜有2D打印机污染；Space Pi排名属于耗材/配套设备子榜。",
      "source_ids": [
        "S20",
        "S24",
        "S25",
        "S26",
        "S27"
      ]
    }
  ],
  "sources": [
    {
      "source_id": "S01",
      "url": "https://www.jd.com/phb/key_6728e5a1cbd85878c58f.html",
      "title": "行车记录仪吧排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K01",
        "K02"
      ]
    },
    {
      "source_id": "S02",
      "url": "https://www.jd.com/hprm/6704262580d296f9049.html",
      "title": "70迈M800Pro商品列表 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K02"
      ]
    },
    {
      "source_id": "S03",
      "url": "https://www.jd.com/hprm/6728adf91ff547e9f522.html",
      "title": "盯盯拍MINIPro 4K商品列表 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K02"
      ]
    },
    {
      "source_id": "S04",
      "url": "https://www.jd.com/hprm/73766f9f6ffdcfc0652.html",
      "title": "A810商品列表 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K03"
      ]
    },
    {
      "source_id": "S05",
      "url": "https://club.autohome.com.cn/bbs/thread/6587451d5649173a/114233850-1.html",
      "title": "车主实测｜70迈A810Pro行车记录仪夜视性能",
      "published_at": "2026-01-26T16:07:44+08:00",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K03"
      ]
    },
    {
      "source_id": "S06",
      "url": "https://www.jd.com/cppf/672865591d9c65371676.html",
      "title": "自营车载充气泵怎么样 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K04",
        "K05"
      ]
    },
    {
      "source_id": "S07",
      "url": "https://item.jd.com/product/FUQjUkVHZnGJ4JviSEN6_w.html",
      "title": "小米充气宝2D MJCQB07QWS - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K04",
        "K12"
      ]
    },
    {
      "source_id": "S08",
      "url": "https://item.jd.com/product/ATCZCLlKstYUlIKZlbcjSQ.html",
      "title": "米家充气宝2 MJCQB06QW - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K04",
        "K12"
      ]
    },
    {
      "source_id": "S09",
      "url": "https://post.smzdm.com/talk/p/avprl3n4/",
      "title": "米家充气宝2评测（非pro），好奇为什么大家都在推pro",
      "published_at": "2024-09-09T20:16:25+08:00",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K04"
      ]
    },
    {
      "source_id": "S10",
      "url": "https://post.smzdm.com/p/awz0pp8p/",
      "title": "车载充气泵：省时省力的必备工具",
      "published_at": "2023-08-16T08:24:17+08:00",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K05"
      ]
    },
    {
      "source_id": "S11",
      "url": "https://www.jd.com/tupian/67285a619173cf8b9706.html",
      "title": "车载式充气泵图片 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K05"
      ]
    },
    {
      "source_id": "S12",
      "url": "https://www.jd.com/phb/key_1318b0cd67e76e23160b.html",
      "title": "网面运动排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K06"
      ]
    },
    {
      "source_id": "S13",
      "url": "https://www.jd.com/phb/key_1318b6df3c1e1185f2f6.html",
      "title": "特步运动鞋排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K07"
      ]
    },
    {
      "source_id": "S14",
      "url": "https://www.jd.com/brand/1318ed12af1d8e09ddff.html",
      "title": "李宁羽毛球拍品牌及商品 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K08"
      ]
    },
    {
      "source_id": "S15",
      "url": "https://post.smzdm.com/p/apq2mxx9/",
      "title": "6支小众耐打的中端进攻羽毛球拍实测，400-600元闭眼挑",
      "published_at": "2026-06-22",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K08"
      ]
    },
    {
      "source_id": "S16",
      "url": "https://www.jd.com/xinghao/1318b757d84dbfbcc92b.html",
      "title": "红双喜F4002型号商品页 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K08"
      ]
    },
    {
      "source_id": "S17",
      "url": "https://www.jd.com/brand/131810ce1a7d5f320c68.html",
      "title": "Naturehike帐篷品牌及商品 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K09"
      ]
    },
    {
      "source_id": "S18",
      "url": "https://www.jd.com/hprm/1318d026c8cdf6a64ef5.html",
      "title": "牧高笛冷山2PLUS商品列表 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K09"
      ]
    },
    {
      "source_id": "S19",
      "url": "https://post.smzdm.com/p/aome203r/",
      "title": "云尚2和云尚Pro怎么选？百元差价藏着这些露营关键细节",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K09"
      ]
    },
    {
      "source_id": "S20",
      "url": "https://www.jd.com/phb/key_6708052b8ebbbc3eabc.html",
      "title": "3d打印排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K10",
        "K11"
      ]
    },
    {
      "source_id": "S21",
      "url": "https://item.jd.com/product/H0B82jkuk_UM7WshUKeNtg.html",
      "title": "拓竹P2SC / P2S多色套装 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K11",
        "K12"
      ]
    },
    {
      "source_id": "S22",
      "url": "https://bambulab.cn/zh-cn/a1",
      "title": "拓竹 A1 | 桌面级3D打印机 | Bambu Lab CN",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": [
        "K10"
      ]
    },
    {
      "source_id": "S23",
      "url": "https://www.snapmaker.cn/snapmaker-u1",
      "title": "Snapmaker U1 Toolchanger 3D Printer",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "official",
      "access_state": "read_full_page",
      "claims_supported": [
        "K10"
      ]
    },
    {
      "source_id": "S24",
      "url": "https://www.jd.com/brand/670d97890cd9003d52b.html",
      "title": "A1打印机品牌及商品 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K10",
        "K12"
      ]
    },
    {
      "source_id": "S25",
      "url": "https://item.jd.com/product/m6KOrJemUOxm_GPdewbV4w.html",
      "title": "拓竹A1 单机大陆版 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K12"
      ]
    },
    {
      "source_id": "S26",
      "url": "https://item.jd.com/product/HGkFxgeLz1vbFoSr9nUE-A.html",
      "title": "拓竹A1 mini 单机大陆版 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K12"
      ]
    },
    {
      "source_id": "S27",
      "url": "https://www.jd.com/phb/key_67068e12f834fd813d8.html",
      "title": "三维打印耗材排行榜 - 京东",
      "published_at": null,
      "retrieved_at": "2026-10-06",
      "source_type": "secondary",
      "access_state": "read_full_page",
      "claims_supported": [
        "K13"
      ]
    },
    {
      "source_id": "S28",
      "url": "https://post.smzdm.com/p/apqxk0ww/",
      "title": "特步两千公里五代体验",
      "published_at": "2026-09-03T16:22:18+08:00",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K07"
      ]
    },
    {
      "source_id": "S29",
      "url": "https://post.smzdm.com/p/adz2vnzk/",
      "title": "拓竹A1 Mini一周使用体验",
      "published_at": "2026-05-19",
      "retrieved_at": "2026-10-06",
      "source_type": "community",
      "access_state": "read_full_page",
      "claims_supported": [
        "K12"
      ]
    }
  ],
  "claims": [
    {
      "claim_id": "K01",
      "claim": "2026-10-06打开京东“行车记录仪吧排行榜”：M800Pro为TOP1、MINIPro 4K为TOP2；页面显示的是热卖榜名次和评论数，不是公开成交件数。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S01"
      ]
    },
    {
      "claim_id": "K02",
      "claim": "M800Pro榜单链接的item 100357791508可映射到“无卡”版本；MINIPro 4K榜单链接的item 100323403254可映射到“无卡套餐”；其他存储/供电套餐分开显示，不能合并。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S01",
        "S02",
        "S03"
      ]
    },
    {
      "claim_id": "K03",
      "claim": "A810Pro“主机+128G卡×双镜头”精确卡片当次显示0+评论，而同页其他A810Pro变体显示更高评论量；汽车之家有2026-01-26的A810Pro车主实测，但不能把型号级使用证据转移为该精确套餐销量。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S04",
        "S05"
      ]
    },
    {
      "claim_id": "K04",
      "claim": "小米充气宝2D精确型号MJCQB07QWS与米家充气宝2 MJCQB06QW均有可读京东精确页和买家评价；公开普通展示价分别为159元和179元，页面要求登录查看到手价。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S07",
        "S08"
      ]
    },
    {
      "claim_id": "K05",
      "claim": "京东车载充气泵通用页打开状态为普通商品列表而非已锁定销量榜；得力DL8060的精确购买使用由2023-08-16国内作者明确“京东下单”支持，70迈青春版2 2026新款另有精确国内商品卡。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S06",
        "S10",
        "S11"
      ]
    },
    {
      "claim_id": "K06",
      "claim": "京东“网面运动排行榜”中毒刺7代重复占多个名次，吾跃3.0 ARSV024可见于榜单；两者的尺码/颜色仍未由原候选锁定，因此型号榜位不能自动变成精确SKU榜位。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S12"
      ]
    },
    {
      "claim_id": "K07",
      "claim": "特步运动鞋榜把两千公里五代标准版与PRO版分列；标准版有国内使用体验，但原候选尺码/配色未锁，且品牌内榜不等于全市场销量榜。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S13",
        "S28"
      ]
    },
    {
      "claim_id": "K08",
      "claim": "战戟5000 4U空拍和红双喜F4002均能在国内零售页定义到具体版本并看到消费者评论；这些打开页是品牌/型号商品页，不足以证明全市场头部。青蛇Pro实测文未锁3U/4U与G5/G6的具体测试组合。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S14",
        "S15",
        "S16"
      ]
    },
    {
      "claim_id": "K09",
      "claim": "Village 6.0和云尚PRO的京东品牌页存在多代际/颜色/人数聚合，冷山2PLUS NXZQU61017红灰色双人带雪裙则可精确定义；云尚PRO引用的SMZDM页面明确标记AIGC/AI生成，应降权。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S17",
        "S18",
        "S19"
      ]
    },
    {
      "claim_id": "K10",
      "claim": "2026-10-06打开的京东“3d打印排行榜”存在2D打印机污染；P2SC/P2S多色套装在TOP2，A1在TOP4，A1C在TOP8，U1在TOP9；官网只用于确认A1/U1型号规格，不作销量证据。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S20",
        "S22",
        "S23"
      ]
    },
    {
      "claim_id": "K11",
      "claim": "P2SC榜单TOP2链接到item 100285504398的P2S多色套装；同榜另有独立“大陆版P2SC”条目，属于不同item/套装，不能合并。该精确TOP2套装公开普通展示价为4799元。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S20",
        "S21"
      ]
    },
    {
      "claim_id": "K12",
      "claim": "A1单机大陆版和A1 mini单机大陆版的精确京东页分别公开显示普通价1599元与1269元并有买家评价；都要求登录查看到手价。品牌页的评论量不等于销量排名。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S24",
        "S25",
        "S26"
      ]
    },
    {
      "claim_id": "K13",
      "claim": "Space Pi V2 Plus大陆版在“三维打印耗材排行榜”实际为TOP2而非原报告所称TOP1，并显示2000人评论；该榜属于耗材/配套设备子榜，不是3D打印机本体榜。",
      "classification": "FACT",
      "observed_at": "2026-10-06",
      "source_ids": [
        "S27"
      ]
    }
  ],
  "data_gaps": [
    {
      "scope": "all_candidates",
      "gap": "AUTHENTICATED DATA REQUIRED：多数京东条目缺seller_id、当前库存、可见成交/销量字段及结算态价格。",
      "login_recapture_fields": [
        "selected_item_id",
        "seller_id",
        "selected_exact_variant",
        "ordinary_price_cny",
        "member_price_cny",
        "vip88_price_cny",
        "targeted_coupon_cny",
        "national_subsidy_cny",
        "old_price_cny",
        "visible_sales_or_paid_order_signal",
        "stock_state",
        "capture_timestamp"
      ],
      "reason": "部分直接item页为风险校验/空壳，且可读精确页明确要求登录查看到手价；未登录不能猜。",
      "source_ids": [
        "S07",
        "S08",
        "S21",
        "S25",
        "S26"
      ]
    },
    {
      "scope": "prices",
      "gap": "已核公开普通展示价只写入对应candidate的price_audit；会员价、88VIP、定向券、国补和旧价均未获得可归属到精确SKU的登录态证据，保持null。",
      "login_recapture_fields": [
        "member_price_cny",
        "vip88_price_cny",
        "targeted_coupon_cny",
        "national_subsidy_cny",
        "old_price_cny"
      ],
      "reason": "不同价格机制不得互相替代；京东未观察到88VIP字段，若以后从天猫补证也须单独记录，不能回填为京东价格。",
      "source_ids": [
        "S07",
        "S08",
        "S21",
        "S25",
        "S26"
      ]
    },
    {
      "scope": "variant_mapping",
      "gap": "毒刺7代、吾跃3.0、两千公里五代、Village 6.0、云尚PRO、A1榜单item、A1C、U1仍需登录态或旗舰店选择器锁定精确尺码/颜色/套装。",
      "login_recapture_fields": [
        "selected_variant_text",
        "variant_sku_id",
        "item_id",
        "bundle_contents",
        "seller_id"
      ],
      "reason": "聚合评论、重复榜位或商品族标题不能替代精确变体映射。",
      "source_ids": [
        "S12",
        "S13",
        "S17",
        "S20",
        "S24"
      ]
    },
    {
      "scope": "ranking_semantics",
      "gap": "京东phb页可核“热卖商品/排名”，但未公开排名算法；brand/hprm/cppf/xinghao普通页虽有“销量”筛选标签，本次打开的默认状态不能证明已按销量排序。",
      "login_recapture_fields": [
        "ranking_name",
        "ranking_scope",
        "sort_state",
        "rank_position",
        "capture_timestamp"
      ],
      "reason": "审计必须区分榜单名次、评论数、聚合评论与真实成交量。",
      "source_ids": [
        "S01",
        "S06",
        "S12",
        "S20",
        "S24"
      ]
    },
    {
      "scope": "compliance",
      "gap": "本审计未查询任何候选的海外价格、海外覆盖、海外销量或进口节省；重量、电池、电压、固件、保修等仅作为后续可行性字段，不作排除依据。",
      "login_recapture_fields": [],
      "reason": "遵守本会话预注册限制。",
      "source_ids": []
    }
  ]
}
```