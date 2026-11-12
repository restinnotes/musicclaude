**成功。** 已完成 N02、N03、N04 的作品参数化，全程只做代码修改和离线验证，未调用模型、未提交网络请求。

**修改和新增文件：**

- 修改 `_bead_op61_20261020` 下的 [gen_A/gen.py](D:/musicclaude/_bead_op61_20261020/gen_A/gen.py)、[chain.py](D:/musicclaude/_bead_op61_20261020/chain.py)。
- 修改 `_thread_evo_20261019` 下的 [center_from_A.py](D:/musicclaude/_thread_evo_20261019/center_from_A.py)、[center_dag.py](D:/musicclaude/_thread_evo_20261019/center_dag.py)、[centersel.py](D:/musicclaude/_thread_evo_20261019/centersel.py)。
- 新增公共读取模块 [work_meta.py](D:/musicclaude/_thread_evo_20261019/work_meta.py)，以及 [op60/work.json](D:/musicclaude/_thread_evo_20261019/works/op60/work.json)、[op61/work.json](D:/musicclaude/_thread_evo_20261019/works/op61/work.json)。
- 在珠子项目 `prompts/` 下新增 **11 个参数模板**：A 稿两个、珠子七阶段及结构规范八个、fresh fix 前文一个。原有提示词文件保留原样。
- 新增中文说明 [新作品上游运行说明.md](D:/musicclaude/_thread_evo_20261019/DAG/新作品上游运行说明.md)，详细日志写入 [log.md](D:/musicclaude/_thread_evo_20261019/_codex/param_20261101/log.md)。

五个修改过的原有脚本，均已在修改前创建同目录 `.bak_param20261101` 备份。

**比对结果：**

共 **467 项比较通过，0 项失败**；其中按路径去重，覆盖 **262 个历史提示词或快照对照文件**：

| 对照范围 | 逐字一致的不同文件数 |
|---|---:|
| N02 历史 A 稿提示词 | 62 |
| N03 历史各阶段提示词 | 147 |
| N04 历史 Center 提示词 | 30 |
| DAG 模板及实发快照 | 23 |
| **合计** | **262** |

此外，N03 改造前后 **173 项渲染完全一致**，续会话标识及附件使用方式也一致；两首作品的 N04a 合并附件逐字一致。实际命令行离线重放另验证了 **12 份 Center 输出与对应历史完整输入逐字一致**。

最终没有未解决的不一致。比较时保留了原发送层的处理：Center 的 `NO_WEB` 后缀，以及 gpt3 CLI 的末尾空白清理。模板层和实发层分别与对应对照比较，没有为匹配而改写正文。

临时 Op.52 放在指定 `tmp/` 下，渲染 **32 份完整提示词**并检查 **24 个 A 稿任务参数**，残留检查通过：除专属性候选清单外，没有“幻想波兰舞曲”“船歌”“PTNA”“塚田”“Op.61”“Op.60”。额外更换作曲家后，Center 提示词也没有残留“肖邦”。

**尚未参数化的地方：**

- 未修改的 `sat.py`、`finish.py`、`build_op61.py` 及旧提示词，直接运行时仍可能固定作品。新作品通过 `chain.py production` 配置并复用原生产任务。
- `centersel.py` 自身旧 `pool` 仍保留历史研究候选来源；新作品使用 `center_dag.py`。其 `SPEC/FIT/PIECES/RIGHT` 历史导入接口保持兼容。
- 珠子旧 `synth/audit/display/all/build` 实验入口不属于本次七步生产路径；新入口输出逐段机器可读定稿，没有扩展下游成品打包器。

**风险：**

- 模型服务、账号保护、配额和会话有效期均未联网探测；新增 24 任务入口只做了离线计划及 mock 调度验证。
- 已有成功缓存不会因修改 `work.json` 自动失效；新实验应使用独立 key／目录。
- 范围核查发现，工作期间 `dag_src3.py` 和 **7 个已有 runs 文件**发生并发变更。本轮未写入或回滚这些文件，具体路径已记录在日志中。