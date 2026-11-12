# run147_thread_resume_r6

2026-10-09：主会话从只读 r5 生成新修订，仅修复 Muse 收据的精确类型边界。

主 r5 离线回归 25+24 PASS 不足以放行：完整入口仍接受 verified/source_bound/bytes_verified=1 或 1.0；10 个定向反例失败。

本修订对 expected receipt 字段先比较 exact Python type，再比较值；拒绝数字冒充布尔及 float/bool 冒充整型 seed/size。原26/27字段接口、trusted verifier 必需条件、TEST_ONLY 与真实返回分界不变。

仅 run 标识/模块测试引用机械改名；没有修改音乐 prompt、宪法、旧样本或 production。r5 历史代码及失败证据不覆盖。

COMPLETION_PENDING；独立 review、主动态核验及实际协议仍需分别处置。real gate 与 two-w hold 保留；mock 不等后端调用，工程通过不等音乐验收。
