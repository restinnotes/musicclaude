"""Write actual measured checkpoint state; never edits model products or ZIP."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B

root = B.ROOT
folder = root / 'runs/_batches/round59_target_coupling'
quick = json.loads((folder / 'r59target_quick.json').read_text(encoding='utf-8'))
assert quick['complete'] == 4 and quick['wins'] == 0 and not quick['pass']
B.write_frozen(folder / 'r59target_final_disposition.json', B.json_text({
    'status': 'archive', 'tag': 'r59target', 'base': 'qu', 'checkpoint_only': True,
    'quick': quick, 'reason': 'All four original balanced votes select old; multiple original conditions fail. Paired new A3/A4 yields more abstract explanation and less late development. No floors/extra4/downstream or quality return; no promotion.',
    'source_output_hashes': {r['rid']: r['output_sha256'] for r in quick['rows']}}))
stamp = datetime.now(ZoneInfo('America/New_York')).isoformat()
lines = [
    'ZIP冻结不改；active目标原I14收敛和脚本最终vsr49b。唯一已验收r54weave，DAG未改。',
    'r59tracebound完整qu快筛4新版/0不退步、+25/+25/+11/-5，原快筛通过；不能另加快筛不退步阈值，qu也不是实际r54最终验收基准。唯一覆盖父47668，两曲原底线4份；Op60两份已全文读/实际输入与完整50颗绑定，Op61待收。',
    'r59target原A3和配套A4双曲均全文读/逐字绑定/机械套用，原13930/25033终态。独立qu快筛75417终态，四份全读/三个实际输入逐字/集合枚举核验，0新版/0不退步、-42/-2/-54/-38，多条件失败归档，不底线/追加票/退回/下游。',
    'r59routefirst原g6a方案2与AnchorFirst完整提示词对照后发现可测顺序差异：先写完分段经历才检查TARGETS；前者先整理支点并结合TARGETS再写。原文冻结，只换A4复用前三步，唯一生产父32687在途，双曲全读后才套用/快筛；不称可观察内部推理或独立上游机制。',
    '仅47668、32687 live；12331/75417/25033及更旧父终态。幸存qu检查点必须重跑受影响N05e/f并对真正当前主线验收。无新收敛结论，不拿旧12:39局部判断替代原I14。',
    '优先gpt3共享6槽、总≤10及20秒间隔；普通60秒、明确suspicious30分钟，不重置同故障计时，不改模型强度联网和标准，不动watchdog/保温；heartbeat PAUSED。']
status = root / 'STATUS.md'
text = '# 当前接续：trace覆盖、RouteFirst真实生产；Target失败归档，尚未收敛\n\n最后更新：' + stamp + '（America/New_York）。\n\n' + '\n'.join('- ' + s for s in lines) + '\n\n---\n以下历史追溯，最新优先。\n\n'
status.write_text(text + status.read_text(encoding='utf-8'), encoding='utf-8')
with (root / '试验记录.md').open('a', encoding='utf-8') as f:
    f.write('\n\n## ' + stamp + ' R59配套Target实际失败与最后顺序变体\n\n' + '\n'.join('- ' + s for s in lines) + '\n')
p = root / 'runs/_batches/round55_current/issue_actions_pending.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['updated_at'] = stamp
d['must_wait'] = {'47668': 'r59tracebound coverage only; full read before floor verdict', '32687': 'r59routefirst original A4 pair; full read before apply'}
d['r59target_actual_disposition'] = 'round59_target_coupling/r59target_final_disposition.json'
d['r59routefirst_actual_test'] = {'batch': 'round59_a4_order', 'parent': 32687, 'reason': 'Original complete prompt order differs from AnchorFirst; once-only actual A4 variant, no upstream changes.'}
p.write_text(B.json_text(d), encoding='utf-8')
print(stamp)
