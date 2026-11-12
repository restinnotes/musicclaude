# run138：二阶审核的删句反事实，冻结派生（2026-10-09）

## 问题与单变量

run128 在旧生产珠子上有 GPT-5.6w v1 两作品全部 30 站 × 每站 2 条关系。旧案例挖掘提出了“图像化重述被判 insight”的风险，尚须逐条独立核证，不能把案例标签当真值。本轮不是比较 GPT-6 与 GPT-5.6，也不是重测 NONE 率或新珠子的生成者。本轮固定同一组已完成且可核对原 prompt/output 的关系与原体验、固定当前 Gemini Flash 审核者，比较历史 `MECH_AUDIT_v0` 与增加**一句删句反事实判据**的新模板。

新的 `prompts/tooling/MECH_AUDIT_v1_counterfactual_20261009.txt` 必须与历史 v0 逐 byte 比对：除这一句外全部一致。模型身份、两组输入、格式、参数、并发与信息权限相同。审核顺序按保存的随机种子打乱；来源/生成者不进入 judge prompt。

新增句：

> 只有你能指出删掉这条关系而保留全部原体验后，听者会失去哪一种尚未由原体验说出的、有本处依据的理解，才可判 insight，并在 why 中说出该损失；若只是换词、合并或换一个比喻呈现已有理解，判 restatement。

## 来源

- `notes/handoff_20261003_v2/05_SECOND_ORDER_UNDERSTANDING.md` §1/§2/§5：二阶不是去重，不是 Outer/新比喻，不强制每颗珠子有关系，关系与 vivid anchor 分存。
- `reference/PRODUCT_CONSTITUTION_V2.md` B3/B4/B5、C6、D1：局部先成立，体验具体自然；独立层需真实信息增量；当前不能依赖未来。
- 原验收 `06_ACCEPTANCE_CRITERIA.md` Second-order：dedicated task、NONE 不被硬造、机制 grounded canonical bead。本轮不改这些验收，不把稀疏化数字当证明。
- `notes/PRODUCT_AND_AUTHORITY.md` §2：删去后是否丢失独立听法，而非只优化数字。

## 固定治理附言（两组完全相同）

为了符合最新评审纪律，两个已填模板后都附同一段：

“评审纪律补充：戏剧化、笃定、单一故事线本身不扣分，不追求 NONE 或空白率；只依据本次给出的体验与关系，不把来源模型或长度当证据。若现有证据确实无法区分类别，可以输出 {\"class\":\"undetermined\",\"why\":\"明确指出缺哪份证据\"}，不要猜测。”

因此本轮 v0 条件是**历史 v0＋统一治理附言**，不是声称逐 byte 重跑旧 run128 审核；v1 除新增一句也有完全相同附言。治理附言只用于本轮审核工具，不改 production prompt。

## 输入及身份限制

主输入：run128 已完成的 gpt56w × v1 在 Op.52/Op.60 的关系，共 60 条（应由脚本核完整，不以本笔记数字硬填通过）。从每条成功 output 与相应原始生成 prompt 提取同站原体验；重新 parse 并验证 cache parsed/output 一致，prompt_sha10、model_key、status、正文 SHA（有则强核）。旧 producer 实现 hash 没记录时明确写“旧冻结输入，不能证明 exact producer”，不补造。旧 source/run/prompt 不写。

新版 audit 只看到当前站原体验与候选关系，不看到全曲结局、以前 judge verdict、A/B真身份或本笔记案例答案。每关系 v0/v1 当作独立新 job，禁止共享 sampling key 把两样本合为一个。

## 判决与不测理由

- 逐条列两组分类及 why，保留分歧，不平均成一个分数。
- 重点核原先真增量能否保留、重述/矛盾是否被识别、删句后失去什么是否具体而非泛泛“理解更深”。
- 至少一名与关系生成者独立的审核。Flash 与 gpt56w 来源不同；另为有变化/边界案例导出 Muse、Luna 全文评审任务，保存 seed、mapping、prompt SHA、实际路由、自评身份。
- 两w评审受 run135 queue hold 阻塞，记为缺项，不以 Flash/Muse 代替用户最终全阵容要求。
- 本轮不重复旧生成 v0/v1 对 NONE 率的无效差异，不补旧 Opus，不把“审核少留了几条”直接当胜利。
- 不把旧生产珠子审核通过称作 canonical 新珠子 E5、三作品验收或 production ready；未上主屏仍有独立表达价值的 vivid anchors 不因 restatement 自动删除，必须另存去向。
