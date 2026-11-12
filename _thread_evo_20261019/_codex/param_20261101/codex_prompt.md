# 任务：把音乐流水线上游三步（A 稿、珠子、Center）改成“换一首作品只改参数就能跑”

## 背景
项目目录 D:\musicclaude\_thread_evo_20261019，流水线说明见其中 DAG.md（N02 A 稿、N03 珠子、N04 Center）。现在这几步的提示词和脚本把作品写死了，换一首新作品跑不起来：
- N02 A 稿：D:\musicclaude\_bead_op61_20261020\gen_A\gen.py，提示词文件按作品复制（如 `*.op61.txt`），正文写死“肖邦《幻想波兰舞曲》降A大调 Op.61”。
- N03 珠子：D:\musicclaude\_bead_op61_20261020\chain.py 及其 prompts\（pool/gen/rev1/rev2/final/piece/fix 和结构规范），写死“肖邦《幻想波兰舞曲》Op.61”、“PTNA／塚田冻结十三段”等。
- N04 Center：_thread_evo_20261019\center_from_A.py、center_dag.py（WORK 字典只有 op60/op61）、centersel.py 里被沿用的 SPEC/FIT 提示词（专属性测试的 10 首候选曲目写死、写死“肖邦”）。
- 分段已有：_thread_evo_20261019\works\<作品>\segmentation.json。

## 目标
1. 建一个作品登记：_thread_evo_20261019\works\<key>\work.json，至少包含 作曲家、中文曲名（带书名号的写法）、调性、作品号、分段来源的说明文字、专属性测试用的候选作品清单（10 首左右，同作曲家）。先填 op60、op61 两份（内容从现有提示词里原样取）。
2. 上述三步的脚本和提示词改成从 work.json 读这些参数，不再写死作品、作曲家、分段来源、候选清单。作品 key 用命令行参数或环境变量传入，沿用这些脚本现有的风格。
3. 写一份说明：_thread_evo_20261019\DAG\新作品上游运行说明.md（中文），写清换一首新作品时要准备什么（work.json、segmentation.json）、按什么顺序运行哪些命令。

## 硬性约束（必须遵守）
- **不改实验语义**：对 op61 和 op60，改造后渲染出来的提示词必须和现在逐字一致（作品名等原来就是这首的地方替换后结果不变）。验证方法：离线渲染（不调用任何模型），和现有真实发出的提示词比对——对照物在 _thread_evo_20261019\DAG\prompts\N02_*、N03*、N04* 下的 模板/实发 文件，以及 D:\musicclaude\_bead_op61_20261020\runs\ 和 _thread_evo_20261019\runs\ 里对应调用的 prompt.txt / input.txt。若有任何字不同，要说明原因；能做到一致就必须一致。
- **不调用任何模型**（GPT、Gemini、Argon 都不调），不提交任何网络请求；只做代码和离线渲染。
- **只准修改这些文件**：D:\musicclaude\_bead_op61_20261020\ 下的 gen_A\gen.py、chain.py、prompts\ 里的文件（可新增模板文件）；_thread_evo_20261019\ 下的 center_from_A.py、center_dag.py、centersel.py、works\*\work.json（新增）、DAG\新作品上游运行说明.md（新增）。如需新增一个小的公共读取模块，放在 _thread_evo_20261019\work_meta.py。
- **绝对不要改**：_thread_evo_20261019 下的 evo.py、mg_call.py、gpt3_call.py、covjudge.py、v6*.py、lang_open.py、dag_src3.py、dag_run.py、tgraph4.py、line8.py、line_dag.py、draft9.py、segcheck.py、DAG.md，以及 runs\、evaluations\ 下任何已有文件——另一条实验正在用它们跑，改了会破坏实验。也不要删除或覆盖任何已有的运行结果。
- centersel.py 如被其它脚本 import，改动后它对 op60/op61 的行为必须不变。
- 改前先备份要改的文件（同目录 *.bak_param20261101）。
- 本机 Windows PowerShell 5.1 会把无 BOM 的 UTF-8 中文文件读成乱码，读写文本一律用 Python（encoding="utf-8"）或 `-Encoding UTF8`。
- 不动缓存保温机制和 watchdog，不新增定时任务或轮询。

## 自测
- op61、op60：渲染 N02、N03 各提示词、N04 各提示词，和对照物逐字比对，报告结果。
- 假想新作品：新建一份临时的 work.json（例如 key=op52，肖邦《第四叙事曲》f小调 Op.52，配一份临时的 segmentation.json，可以随便分 3 段，放在 _codex\param_20261101\tmp\ 下，不要放进 works\），渲染全部提示词，确认里面没有残留“幻想波兰舞曲”“船歌”“PTNA”“塚田”“Op.61”“Op.60”等字样（候选清单里列出的作品名除外）。测试完删除临时文件或留在 tmp 下。
- 详细日志写到 _thread_evo_20261019\_codex\param_20261101\log.md。

## 回报
最后只回报：成功/失败、改了哪些文件、比对结果（逐字一致的有几个提示词、不一致的有哪些及原因）、还没参数化的地方、风险。遇到必须改变实验语义或无法做到逐字一致时，停下来回报，不要硬改。
