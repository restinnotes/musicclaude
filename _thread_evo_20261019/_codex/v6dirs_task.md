# 任务：为 Thread 实验实现两个并行方向的运行器 v6dirs.py

工作目录：D:\musicclaude\_thread_evo_20261019（Python 3.12，直接 `python xxx.py`，不要加 -I）。
本机 Windows PowerShell 5.1 会把无 BOM 的 UTF-8 中文文件读成乱码，读写文本一律用 Python（encoding="utf-8"）或 `-Encoding UTF8`。
请自主完成并自行验证，详细过程写到 `_codex/v6dirs_log.md`；最后只回报：成功/失败、主要修改、测试情况、重大风险。

## 背景（只需了解）
- `v6fix.py` 是正在运行中的方向 A1（在 v6 上逐段修补）。它的 `fix(w, T)` 把结果存成 `evaluations/v6fix/{w}_{T}.json`（`{"graph": {...}, "rows": {...}}`）和 `{w}_{T}.md`。
  `v6fix.blind(T)`、`v6fix.join(T)`、`gate_v6.py` 都按这个格式读。新方向必须输出同样格式，这样后面的盲评、结合、评定不用改。
- `v6dirs_prompts.py`（我写的，属于实验语义，**一个字都不能改**）里有新方向的提示词：`WHOLE`、`WHOLE_REV`、`WHAT_RAD`、`RAD`、`RAD_CHK`、`RAD_REV`、`RAD_CENTER`。
- 模型调用一律走 `evo.call(run_id, message, model=..., meta=...)`（默认路线 gpt3s → `gpt3_call.py`，自带并发槽位和提交间隔）。`evo.done(rid)` 已完成就复用；`v6fix.parse(rid)` 解析 json。`evo.G6` 写，`evo.G56` 核对。
- `meta={"web": True}` 表示允许联网（不追加“不要联网”）；核对、Center 调用不加 web。

## 要实现：新文件 v6dirs.py

### 方向 A2（整首一次修补），`python v6dirs.py whole <w> [tag]`，tag 默认 `w1`
1. g6 = v6fix.v6(w)。消息 = `WHOLE.format(NAME=covjudge.NAME[w], WHAT=v6fix.WHAT, CENTER=g6["center"], V6=v6fix.view(g6, ids=True, center=False), BEADS=v6fix.beads(w), DIAG=...)`，
   DIAG = 按 `draft10.segs(w)` 顺序拼接 `f"### {sec}\n" + v6fix.diag_for(w, sec)`，段与段之间空一行。
2. 调用 id `v6w_{w}_{tag}`，model=evo.G6，meta={"stage": "v6-whole", "web": True}。解析失败时用 evo.G56 以 id `v6w_{w}_{tag}b` 再调一次；还失败就报错退出。
3. 组图：对 draft10.segs(w) 的每一段 s（按顺序），在输出 `segments` 里按 `sec` 找对应段，用 `v6fix.seg_graph(seg_out, sec, s)` 转换（找不到就用空 items 并记录错误），组成 `{"center": g6["center"], "segments": [...]}`，再 `v6fix.tidy()`。
4. 逐段核对：对每段调用 `v6fix.check(w, sec, tag, done, cur, new)`，其中 done = 只含前面各段的图（`{"center":..., "segments": 前面的段}`），cur = v6 这一段（同 v6fix.fix 里的写法）。这些核对互不依赖，用 `evo.run_parallel` 最多 4 个并发。
   每段意见 = `v6fix.review_notes(k, new, seg_out)`（seg_out 里带 gaps）。
5. 只要有任何一段有意见，就做一次整首退改：id `v6wr_{w}_{tag}`，消息 = 原消息 + `WHOLE_REV.format(NOTES=..., PREV=v6fix.view(graph, ids=True, center=False))`，NOTES 按段写成 `### S03` 加该段意见行，没有意见的段不写。
   model=evo.G6，meta={"stage": "v6-whole-rev", "web": True}。解析成功就按第 3 步重新组图替换（不再二次核对）；失败就保留第一版并记录。
6. 保存 `evaluations/v6fix/{w}_{tag}.json`：`{"graph": graph, "rows": {sec: {"edit": seg_out(最终那版), "check": k, "notes": notes, "revised": bool}}, "changes": 输出里的 changes}`，
   以及 `{w}_{tag}.md`，标题写 `# Op.60｜关系图（A2 整首修补 {tag}）`（Op.61 同理），正文 `v6fix.view(graph)`，和 v6fix.fix 的 md 一致。每段打印一行：`{w} {sec}: v6 n 条 → m 条 | 意见 k | 退改 bool`。

### 方向 B1（激进：不给 v6，逐段生成），`python v6dirs.py rad <w> [tag]`，tag 默认 `s1`
1. 按 draft10.segs(w) 顺序逐段（串行，后一段依赖前一段）：
   消息 = `RAD.format(NAME=covjudge.NAME[w], SEC=sec, A=s["start"], B=s["end"], WHAT=WHAT_RAD, SEGS=..., DONE=..., BEADS=v6fix.beads(w, sec))`。
   SEGS = 每段一行 `f"{x['id']}｜{x['start']}–{x['end']} 小节"`；DONE = 已写好各段的 `view(..., ids=True, center=False)`，第一段写 `（这是第一段，前面还没有）`。
   注意：B1 的段在 Center 写出之前没有 relation。请给 `v6fix.view` 加一个向后兼容的行为：段的 relation 为空（None 或 ""）时，标题只写 `### {sec}｜{bars} 小节`，不写括号。有 relation 时输出必须和现在**逐字相同**（A1 正在用）。
2. 调用 id `v6s_{w}_{sec}_{tag}`，G6，meta={"stage": "v6-rad", "web": True}；解析失败用 G56、id 加 `b` 再调一次；再失败就停并报错。
   转换用 v6fix.seg_graph（它会把 relation 默认成“正在面对”——B1 这里要把 relation 置为空，等第 4 步再填）。
3. 每段核对：id `v6sk_{w}_{sec}_{tag}`，`RAD_CHK.format(DONE=..., NEW=v6fix.view({"center":"", "segments":[new]}, ids=True, center=False) + v6fix._links(new), BEADS=v6fix.beads(w, sec))`，G56，meta={"stage": "v6-rad-check"}。
   意见：照 v6fix.review_notes 的写法，但没有 lost；`progress == "否"` 时加一条 `- 递进不够：{progress_why}`。其余（越界、箭头勉强/不成立、读不懂、不在 gaps 里的 unexplained、wordy）同 review_notes。
   有意见就退改一次：id `v6sr_{w}_{sec}_{tag}`，消息 = 原消息 + `RAD_REV.format(NOTES=..., PREV=该段 view(ids=True))`，G6，web True；解析成功就用退改版。
   每段写完立即把当前进度存盘（同 v6fix.fix），并打印 `{w} {sec}: n 条 | 意见 k | 退改 bool | gaps [...]`。
4. 全部段写完后：id `v6sc_{w}_{tag}`，`RAD_CENTER.format(NAME=covjudge.NAME[w], LINE=v6fix.view({"center":"", "segments": graph的段}, ids=False, center=False))`，G6，meta={"stage": "v6-rad-center"}。
   把 center 写进 graph，把 relations[sec] 写进每段（缺的填“正在面对”，并记录）。然后存 json 和 md（标题 `（B1 激进逐段 {tag}）`）。

### 其他
- `python v6dirs.py dry <w>`：不调模型，把 A2 消息、B1 第一段和第二段消息（第二段用假的第一段）、RAD_CHK 消息、RAD_CENTER 消息写到 `_codex/dry_{w}_*.txt`，打印各自字数，供我检查。
- 不要启动真实的模型调用（不要跑 whole / rad）；我来启动。

## 验证要求
1. `python v6dirs.py dry op60`、`dry op61` 能跑通；检查消息里没有残留的 `{` `}` 占位符问题（json 示例里的单个花括号是对的）。
2. 用 monkeypatch 写一个离线测试 `_codex/test_v6dirs.py`：把 evo.call / evo.done / evo.output 换成假的（返回构造的 json 回答，写到临时目录而不是 runs/），把 v6fix.OUT 指到临时目录，完整跑一遍 whole 和 rad（含退改、Center），确认输出 json/md 格式能被 `v6fix.graph_of`、`v6fix.blind` 的组图部分（可只测 graph_of + view）和 `v6fix.join` 读取。测试不得写入真实的 runs/ 或 evaluations/v6fix/。
3. 确认 `v6fix.view` 对 relation 非空的段输出与修改前逐字相同（用 v6 两首对比修改前后的输出）。

## 边界（必须遵守）
- 不得改变实验语义：`v6dirs_prompts.py`、v6fix.py 里的所有提示词常量（WHAT、DIAG、FIX、CHK、REV、BLIND）、联网权限、模型和推理参数、珠子输入、评审标准都不能改。只允许给 v6fix.view 加上面说的“relation 为空时不写括号”的兼容行为。自查这些没被改动并在回报里说明。
- 不改 evo.py、gpt3_call.py、mg_call.py；不动缓存保温机制和 watchdog，不新增定时任务或轮询。
- 正在后台运行的 `python -u v6fix.py fix op60 r2` / `fix op61 r2` 不要停、不要动它们的 runs/ 目录和 evaluations/v6fix/op6x_r2.*。
- 无法完成、必须改变实验语义、或有明显质量风险时，停下来回报。
