# r5 / r6 主工程处置（2026-10-09）

## r5 原证据不覆盖

主 `run144145_main_verify_20261009_r1/report.json`：25+24 suite PASS，三个 worker 每个6负向隔离检查PASS；scoped protected unchanged；实现 attempt001–008共64 stdout/stderr hash+size checks MATCH，manifest两组15/10 checks MATCH（含重复source，不等25 distinct）。实现 before/after三个collection等值，30 fixed entries当前匹配（29存在，1missing）。presence-only `hold=false`/`production=false`只是指定路径不存在，不是全局解除hold或无production。

主读回实际 fullmock：run144126；run145600、secondreuse600/new0、first4match/second4match重验、Center matchlineage4、100 TEST_ONLY Musepacks；都不是后端提交或音乐验收。只读预检run144--real3、run145--strict0/--real3，不改变生产。

**新增 confirmed C5**：两个完整 Muse ingestion entry 都仅做 `!=`，把数值1/1.0当作true。run144 verified/source_bound共4反例，run145 verified/bytes_verified/source_bound共6反例，10/10错误接受；两个合法TEST_ONLY正控通过。challenges returncode=1，原失败raw/report永久保留，r5 **NOT_ACCEPTED**。

实现 matrix item10不能推广为两driver四artifact/parser前write：run145 localmock三artifact，先内存parse并catch，落盘后传播failed；durable成立，不是parser调用前落盘。原report不改。

## r6 收据局部修复与第二层缺口

主新增run146/run147，不覆盖r5：只机械run/module id改名并让receipt expected字段先exact Python type再等值。新增helper/fullingress type negatives。正式prompt/宪法/原验收/production不改。

主 `run146147_main_verify_20261009_r1/report.json`：25+24suite PASS，原2正控+10 C5反例全12 PASS；samefullmock126/600、second0；每worker6guards PASS；protectedunchanged；r6 manifest15/10 MATCH。C5 **收据本层**动态确认修复，但不能据此整体放行。

该复用probe preflight的direct run144仍绑定旧r5（明确保留），run145通过r6 namespace但label沿旧名；新r6suite自身各direct blocked入口有断言。不得把此三preflight label当两r6 CLI独立调用证据。

独立r6 review已发出，状态仅running，不能预测报告或当完成。

**新增 confirmed C6：run146完整外部入口的上游typed binding仍宽松。** `run146_numeric_binding_probe_20261009_r1/report.json`：合法正控接受，以下六定向非法输入均错误接受，rc1（所有实际提交/CLI=0）：

1. pack seed换等值float，并让独立TEST_ONLY receipt seed也为float；receipt exacttype从错误pack expected推导而失守。
2. pack order_index换等值float。
3. result seed换等值float。
4. metadata raw_output_size换等值float。
5. metadata identity.seed换等值float。
6. terminal identity.seed换等值float，同时metadata只更新terminal SHA以绑定真实新字节。

这些是完整入口 `validate_external_review_results` 的反例，不是单helper臆测；所有六task仍规范化为TEST_ONLY/sourcebound、realcount0。C6不声称后端被伪造或实际提交：trusted verifier来源认证仍是外部依赖。问题是冻结协议的JSON类型身份被Python数值等值绕过。

**当前处置：r5 NOT_ACCEPTED；r6 C5局部闭合，但run146 C6未修，因此r6也不能整体ACCEPTED。下一新修订仅收紧该完整入口typed identities，不覆run146失败。run147没有从此run146证据推断出同缺陷。**

## 不变的边界

- two-w held、REAL_EXECUTION_APPROVED=False；production仍run124 B gpt56w。
- real gateway/proof producer/远端归一化/私有配置/外部服务未验。
- 音乐验收NOT_PERFORMED，三作品原验收/全部ZIP未完成。
- 有限Python audit不是OS sandbox；mock receipt不backend attestation。
- 独立review未终局不能解除第19条。旧source/run/prompt/失败/report只读。
