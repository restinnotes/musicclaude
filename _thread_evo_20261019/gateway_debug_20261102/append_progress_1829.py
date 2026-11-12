from pathlib import Path

root = Path(__file__).resolve().parents[1]
with (root / '试验记录.md').open('a', encoding='utf-8') as handle:
    handle.write('''

**18:29东部，502续查与T3双曲齐**：Op.61 A4旧重试390f4389再次321秒空正文502；短退避已过后单并发只补缺项3441a1455b128344f5b1，332秒HTTP200、11198字符。完整被动SSE6131560字节、无截断/解析错、DONE；DOM逐秒从Stop到正文到Copy，结束后ERR_ABORTED在成功样例也出现，不是已证实根因。双曲全文读过，1738/1647字、44/40条，形态通过，心理提纲/重复/覆盖待实际盲比；当前Op.61 GPT-6对qu一份评审在途，缺测不当0。R27P2双曲A1也完整读完，无新增外部事实，允许A2但尚未发。新增真实DOM复现Copy两处串轮bug：整轮搜索借用户按钮、几何兜底借下条用户按钮；3新增+13读取+11完整性+4日志+13调度通过。首部分部署ready，最后几何修复须当前评审结束后idle部署。空正文间歇根因仍未定，不能声称根治；普通失败60秒，可疑行为1800秒不变。不动音乐标准、模型、账号、High、成品或DAG。
''')
note = root / '版本说明/r26t3_vs_qu.md'
if not note.exists():
    note.write_text('''# r26t3 对 qu：等待快筛

假设：保留人物具体所求、顾虑及代价，使前面的心理选择持续影响后面；A2以删除中段与交换次序检验积累，A4一次写整条线。提示词原文见 schemes/R26T3.json；A3输入逐字核对后复用旧完整产物，有来源记录。

双曲已全文读过：Op.60 1738字44条，Op.61 1647字40条，每段2–4条、每条一句。Op.60围绕是否让脆弱被理解发展，Op.61围绕新归属与尊严/旧日牵挂发展；仍有心理办法链、后半重复与覆盖风险。

当前仅开始对qu盲比，尚无完整测量，不判改进、不收入主线。成品原文：evaluations/v6fix/op60_r26t3.md、evaluations/v6fix/op61_r26t3.md。网关成功仅证明通路可用。
''', encoding='utf-8')
progress = root / '进度表.md'
source = progress.read_text(encoding='utf-8')
paragraph = '18:29续：r26t3双曲齐，1738/1647字、44/40条，形态通过，已通读；对qu盲比一份在途，质量尚无结论。r27p2双曲A1完整并通读，A2尚未运行。网关空正文根因未定，Copy串轮2处已复现修复，最后补丁待idle部署；缺测不记0。\n\n'
anchor = '| 版本 | 作品 | 字数 |'
assert anchor in source
source = source.replace(anchor, paragraph + anchor, 1)
progress.write_text(source, encoding='utf-8')
