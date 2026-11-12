# 上游参数化离线日志

日期：2026-11-01。结果：成功。未调用任何模型，未提交网络请求。

## 范围、备份与文件

修改前为五个原有脚本逐个创建同目录 `*.bak_param20261101`，复制原始字节；原有提示词不改动，新增 `.param` 模板，保证直接使用旧提示词的其它实验仍可读取原文。

修改的原有文件：

- `D:\musicclaude\_bead_op61_20261020\gen_A\gen.py`
- `D:\musicclaude\_bead_op61_20261020\chain.py`
- `D:\musicclaude\_thread_evo_20261019\center_from_A.py`
- `D:\musicclaude\_thread_evo_20261019\center_dag.py`
- `D:\musicclaude\_thread_evo_20261019\centersel.py`

新增生产文件：`work_meta.py`、`works/op60/work.json`、`works/op61/work.json`、`DAG/新作品上游运行说明.md`；珠子项目 `prompts/` 下新增 11 个参数模板：

- `A_int_v1.param.txt`
- `A_web_v2.param.txt`
- `final_v2.param.md`
- `fix_fresh_head.param.txt`
- `fix_v1.param.md`
- `gen_v1.param.md`
- `piece_v1.param.md`
- `pool_v2.param.md`
- `rev1_v1.param.md`
- `rev2_v1.param.md`
- `struct_spec_v1.param.md`

本目录的 baseline_files.json、comparison.json、new_work_test.json、cli_test.json、dispatch_test.json、scope_check.json、tmp/ 下测试程序、临时登记、夹具和离线渲染结果属于本次自测证据。临时 Op.52 未放入正式 works/。

## 实现及语义边界

- work_meta：统一 UTF-8 读取、作品名两种空格样式、分段校验、中文段数、候选作品列表、时长预算与输出独占创建；支持 WORKS_ROOT 临时登记根目录。
- N02：原来 10 个 GPT 补稿任务原样保留，入口改为 --work / WORK 和参数模板；模块 import 不启动线程。新增显式 --corpus24，计划为四模型 × int/web × 3，GPT 复用原 gpt3 启动及 submitted/pacing；Gemini/Luna 复用原 runner。对 24 份原文使用 SRC 文件名收集，不覆盖已有 A 材料。历史 GPT-5.6 int 第 1 份的 NO_WEB 后缀按原实发内容登记到 a_job_suffixes。
- gen.py 中原 job_directory 正则少了反斜杠转义，会在解析 stdout 时出错；本次在同一允许文件内修正并用离线字符串验证。它不改变提示词、采样或模型参数。
- N03：原 chain.py 只有 pool；七步生产实际上在 sat.py。未改 sat.py，而在允许修改的 chain.py 中配置其本进程运行上下文、参数模板与数据路径，复用原任务、会话、引语核验和调度。Op.60 每小节 4.4 秒／resume fix，Op.61 2.7 秒／fresh fix，保持原样；Op.60 原 Pool 在 inputs/pool 的位置通过登记保留。新作品有独立目录。
- N04：center_from_A 从登记取名字、A 目录和作品选择；center_dag 的 WRITE/WRITE2 按登记取作品和作曲家，候选 OLD 也是登记参数，新作品不默认塞旧句。专属性候选顺序和随机种子不变。默认双作品仍用原 run id，新作品的 spec 用独立 scope。centersel 的 SPEC/FIT/PIECES/RIGHT 对历史 import 保持原值，参数化入口为 spec_for/fit_for。
- 未改 evo、mg_call、gpt3_call、covjudge、v6*、lang_open、dag_src3、dag_run、tgraph4、line8、line_dag、draft9、segcheck、DAG.md；未执行 dag_export；未改缓存保温、watchdog、定时任务。未删除或覆盖历史运行结果。

## 对照方法与计数

以脚本原来 `read_text` 后的 Unicode 字符串逐字比较；保留所有正文、标点、空格和末尾字符。Python 文本读取按其既有行为统一 CRLF/LF，未把物理文件换行编码差异当作模型文本差异；本次新离线导出文件用 LF 保存。

分两层验证：

1. 对参数化前的备份代码、未改的 Op.60/Op.61 sat.py 和原模板，使用相同历史解析结果渲染；核对正文、续接 session_handle、是否附带 sources.zip。N03 前后渲染 173 项全相同。A 合并附件的文件顺序、分隔符和正文也逐字相同。
2. 对 DAG 模板/实发快照及真实 runs 中对应 prompt.txt/input.txt 重放渲染。明细每项有 reference、标签、SHA-256 和结果，写在 comparison.json。

合计 **467 项比较通过，0 项失败**。其中真实历史／DAG 文件按路径去重为 **262 个不同对照文件**；其余是改造前后等价检查和原始模板检查。不能把重复比较次数当作不同历史文件数量。

| 比较组 | 通过 | 不一致 |
|---|---:|---:|
| N02 baseline | 4 | 0 |
| N03 before-after | 173 | 0 |
| N03 historical | 147 | 0 |
| N03 templates | 16 | 0 |
| N04 constants | 4 | 0 |
| N04 historical | 26 | 0 |
| N04 before-after | 4 | 0 |
| DAG snapshot | 14 | 0 |
| DAG actual | 9 | 0 |
| centersel historical | 8 | 0 |
| N02 historical | 62 | 0 |

N03 历史对照包括：两首的 gen_b/rev1_b/rev2_b/final_b 全部分段；Op.60 的 bead_chain/runs/final/pool 全 14 段；Op.61 pool 全 13 段；Op.60 实际 piece/piece_c 与 final2/final2_c；Op.61 piece_b 与实际 final2_b。无实发结果的非点名段 fix 不伪称有历史实发对照，以原函数同数据前后渲染验证。

N02 额外对照已有音乐项目 run05/run08/run106 的真实 A 提示词及 gen_A/out/*.meta.json 指向的十个 gpt3 prompt.txt。Op.60 调性“升F大调”取自原 stage.py；Op.61“降A大调”及中文名取自原 .op61.txt，候选清单逐项取自原 centersel.py。

N04 覆盖 WRITE、WRITE2 两个版本及双方评委、两种洗牌样本；同时核对沿用的 centersel 旧 csp/cfit 与 DAG 中 N04a/b/c/d 实发快照。

## 初次比较差异及处理依据

这些是不同记录层之间的既有差别，未通过改动提示词正文“对齐”：

- Center 最初有 8 项 raw-message 与 input.txt 相差 `\n\n回答时请不要进行联网搜索。`。只读检查 evo.py:107–108、mg_call.py:84–85、gpt3_call.py:138–139 证实这是原调用层自动追加的 NO_WEB。重放同一既有后缀后全部逐字一致。历史 10-21 cA/csp/cfit 早于这项发送规则，对照保留其真实 raw 文本。
- N02 十个 gpt3 服务侧 prompt.txt 比输入模板少最后的换行。只读检查 `gpt2agent-safechain/tools/chatgpt_web/gpt3_cli.py:151` 证实原 CLI 先移除 BOM、统一换行，再 rstrip()。离线仅重放同样处理，服务侧十个对照全部逐字一致；基础模板和 DAG 模板的末尾换行保留，与各自层的对照一致。
- run106 的 gpt56w-int-1 实发自带 NO_WEB，gen.py 的原十份补稿没有这一任务。--corpus24 用登记的 a_job_suffixes 保留这份历史变体，未把后缀加到其它原补稿。

最终同层的提示词差异为 0；没有需要改变实验语义才能匹配的项目。

## 临时作品、命令行和调度验证

临时 Op.52 登记及三段 segmentation 位于 tmp/works/op52；所有阶段材料为明确标注的离线夹具，未伪造为模型结果。运行四个实际 CLI 离线入口，产生 **32 份完整提示词 + 24 任务计划**；排除“作品：”候选清单这一行后，检查 `幻想波兰舞曲`、`船歌`、`PTNA`、`塚田`、`Op.61`、`Op.60`，全部 0 命中；同时检查作品、分段、Pool、评审等占位符全部展开。额外用“测试作曲家”验证 SPEC 和 WRITE2 不再残留“肖邦”。详见 new_work_test.json。

Op.60/61 的四个实际 CLI 离线入口另生成 **207 个 txt 文件**；其中 N04 write/spec/fit/cA 共 **12 个命令行产物**与对应历史完整输入逐字一致。输出覆盖边界由 Python audit hook 限制在本次 _codex 目录。详见 cli_test.json。

N02 的 --corpus24 调度用 mock GPT 和 mock runner 验证：12 个 GPT + 12 个其它模型任务，24 个收集文件逐字等于假后端的输出，int/web 的工具策略分开，完整 A 目录第二次运行跳过；默认 JOBS 与备份中的 10 项完全一致。未触发真实启动器。两首 N04a 合并附件均逐字一致。详见 dispatch_test.json。

所有测试程序在 import 业务脚本前禁用 subprocess.run/Popen、os.system 和 socket connect/create_connection，且 `python -B` 禁止生成业务目录 pyc。**真实进程／网络尝试记录均为空。** 测试使用的 model call 均在渲染入口替换为收集器或明确的 mock，未调用真实 evo.call、gpt3 或其它模型接口。

实际执行的测试程序（均在 tmp 下）：

```powershell
python -B ...\tmp\verify.py
python -B ...\tmp\verify_new.py
python -B ...\tmp\verify_cli.py
python -B ...\tmp\verify_dispatch.py
```

verify.py 可重跑；其余测试保存了独占输出，重跑时应在测试脚本中换一个新的临时输出目录，不删除已有证据。六个生产 Python 文件另已 compile() 检查语法，未生成 pyc。

## 尚未参数化的边界和风险

- sat.py、finish.py、build_op61.py 及原始提示词按允许范围保留不动，直接使用它们仍会固定作品；新曲必须走 chain.py production。旧 chain 的 synth/audit/display/all/build 为其它旧实验接口，不是这次七步生产路径；production 输出逐段机器可读定稿，不新增下游成品打包器。
- centersel 的历史 pool 仍固定旧研究比赛来源；它不是新 DAG 的候选来源，新作品走 center_dag，SPEC/FIT 的历史 import 兼容接口不变。
- 模型路由、账号保护、配额、会话过期和现有非 GPT runner 的可用性未做联网探测，24 任务正式执行只做了 mock 调度验证；不能把离线通过理解为已验证线上服务可用。
- 新作品专属性候选清单和分段来源的真实性由登记者准备，本次只校验结构。已有成功缓存不会因编辑 work.json 自动失效；新实验需另用新 key/目录，不覆盖旧结果。

## 并发变更观察

初始只读记录两个项目下 75,514 个已有脚本／DAG 提示词／runs／evaluations 文件的 size 和 mtime，保存在 baseline_files.json。结束时无文件缺失；其中五个允许脚本由本轮修改，另外发现以下八个已有文件在工作期间发生并发变化：

- `D:\musicclaude\_thread_evo_20261019\dag_src3.py`
- `D:\musicclaude\_thread_evo_20261019\runs\calls.jsonl`
- `D:\musicclaude\_thread_evo_20261019\runs\run_alone_q8w.log`
- `D:\musicclaude\_thread_evo_20261019\runs\run_src3.log`
- `D:\musicclaude\_thread_evo_20261019\runs\al_op60_g6_q8w\mg_request.json`
- `D:\musicclaude\_thread_evo_20261019\runs\al_op61_g6_q8w\mg_request.json`
- `D:\musicclaude\_thread_evo_20261019\runs\tr_op61_g56_q8w\mg_request.json`
- `D:\musicclaude\_thread_evo_20261019\runs\tr_op61_g6_q8w\mg_request.json`

本轮未写入、删除或回滚这些八个文件；仅依据 size/mtime 记录并发变化，未推断具体写入进程。未修改的 DAG 快照和其余禁改脚本未发现 size/mtime 变化。scope_check.json 保存完整检查结果。

## 备份校验和

- `gen.py.bak_param20261101`：`fe0f341f905bbef5d182a35de2b6d803c7148ee580e5863665ccb3d1d033bfe1`
- `chain.py.bak_param20261101`：`f29394a47e622be93121b67344ba90af26613e00c89cee004d9efa459cecadad`
- `center_from_A.py.bak_param20261101`：`7b336cb62d1d289683a49e7a694dc2ee407425043a97a01f84a262dee17f2dcc`
- `center_dag.py.bak_param20261101`：`c59998b8af95ac0ed022e7db60fecb4833123d08aef2cb1ab83fcc286a4e6ce5`
- `centersel.py.bak_param20261101`：`a35e04b8128205fdb07e28e0bc2ed04a7e9be8c28b12452e651f95a38c85794a`
