"""Record terminal R59 outcomes while the two original review collectors run."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B

stamp = datetime.now(ZoneInfo('America/New_York')).isoformat()
dispositions = {}
for batch, tag in [('round59_a4_order', 'r59routefirst'),
                   ('round59_trace_repair', 'r59tracebound'),
                   ('round59_target_coupling', 'r59target')]:
    path = B.ROOT / 'runs/_batches' / batch / f'{tag}_final_disposition.json'
    text = path.read_text(encoding='utf-8')
    value = json.loads(text)
    assert value['status'] == 'archive'
    dispositions[tag] = {'path': path.relative_to(B.ROOT).as_posix(), 'sha256': B.digest(text)}
lines = [
    'ZIP按用户最新要求冻结不动，唯一已验收主线r54weave；DAG无新收，尚未证明I14收敛。',
    'R59全部质量机制终态：target四票0新版/0不退步，净胜-42/-2/-54/-38；routefirst四票0新版/0不退步，净胜-36/-4/-52/-44，四票全文读/实际三输入逐字和集合枚举绑定；均多条件失败归档，不补底线、额外票、退回或下游。',
    'tracebound原快筛4/4通过；覆盖唯一确定失败Op60 S06，Op61 G56漏S06-B5保留不完整且上下界不改变失败集合。原作者最后返回r59tracebound_feedback_g56_v3/session10530终态全文读/完整附件及字节manifest绑定，明确abandon、candidate:null：固定P1没有足够经历依据恢复缺失听感，不能靠A4编事实；两次实际质量生产后归档。',
    '仅父97622（collect_i14_after_r59.py collect）与96642（round50_measure fair r54weave --base r49b --phase all）在途，各自收原请求，不重复提交。fresh10原I01评审需全部全文读并逐项匹配冻结48项具体意见；直接8票不累计父版本票。',
    'I14范围runs/_batches/i14_after_r59/audit_scope.json于fresh提交前冻结，主线SHA未变；R55/R56连续零接纳，后续R57–R59均未接纳，仍有旧问题与分歧不能称全部解决。fresh如有确实新增中等以上问题必须继续I01/I02，不重问同稿到有利。',
    '优先gpt3共享6槽、总≤10、提交间隔20秒；普通故障60秒、明确suspicious30分钟，不重置同一故障；原标准/模型强度联网不改，不动watchdog/保温，heartbeat PAUSED。'
]
p = B.ROOT / 'STATUS.md'
head = '# 当前接续：R59全部归档；收取原I14与直接vsr49b，尚未收敛\n\n最后更新：' + stamp + '（America/New_York）。\n\n' + '\n'.join('- ' + x for x in lines) + '\n\n---\n以下历史追溯，最新优先。\n\n'
p.write_text(head + p.read_text(encoding='utf-8'), encoding='utf-8')
with (B.ROOT / '试验记录.md').open('a', encoding='utf-8') as f:
    f.write('\n\n## ' + stamp + ' R59全部终态与原收敛检查\n\n' + '\n'.join('- ' + x for x in lines) + '\n')
p = B.ROOT / 'runs/_batches/round55_current/issue_actions_pending.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['updated_at'] = stamp
d['completed_dispositions'].update(dispositions)
for issue in d['issues']:
    for tag in issue.pop('pending_mechanisms', []):
        if tag not in issue['actual_trials']:
            issue['actual_trials'].append(tag)
d['must_wait'] = {'97622': 'fresh unchanged I01 ten reviews: full read and specific novelty audit',
                  '96642': 'actual direct r54weave vs r49b eight votes: full read and binding'}
d['deferred_proposals']['RouteFirstFit'] = 'Actual original production pair and balanced quick4 terminal, all four old; archived.'
d['deferred_proposals']['RecurrenceTrace'] = 'Two actual quality productions; original author final return explicitly abandons, bound full evidence preserved.'
p.write_text(B.json_text(d), encoding='utf-8')
print(stamp)
