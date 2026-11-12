"""Persist actual R60 checks and the sole original R61 adviser collector."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B

stamp = datetime.now(ZoneInfo('America/New_York')).isoformat()
root = B.ROOT
assessment = json.loads((root / 'runs/_batches/i14_after_r59/assessment.json').read_text(encoding='utf-8'))
direct = json.loads((root / 'runs/_batches/round50_from_r49b/r54weave_vsr49b_direct8_verified.json').read_text(encoding='utf-8'))
assert assessment['status'] == 'not_converged_new_medium_findings'
assert direct['formal']['complete'] == 8 and not direct['formal']['pass']
lines = [
    'ZIP冻结不改；唯一已验收主线r54weave，DAG无新接纳，goal继续至原I14收敛及脚本最终vsr49b。',
    'R59 Target/RouteFirst全部快筛明显失败归档；tracebound两次质量生产后原作者最后反馈abandon，完整证据见各final_disposition。所有R59原父终态，没有残留生产或质量退回。',
    '原fresh I01十份97622终态全部全文读/实际输入逐字/冻结manifest及输出哈希核验，30项中等以上实例原评级保留。I14未过：至少Op60 S04克制未说尽→S05自然露出缺少过渡为新增具体中等，不能把旧S05听感错位意见当精确匹配；S06-B1纯净新鲜感另记新子项，但R59trace相关失败已知，不自动重复A4措辞补法。轻微死亡歧义及旧问题分歧完整保留。assessment.json为not_converged，未重问同稿到有利。',
    '实际直接r54weave vs r49b八票96642终态全部全文读/输入逐字/段集合枚举绑定：5选新、4不退步，四维净胜+26/-6/0/+12，原逐段底线pass，但原完整八票门槛未通过。Op61两评委座位分歧保留，不挑座位或累计父票。对父r50progress1rr原7新版6不退步验收有效，不能由此称全面胜r49b。',
    '最终版本_vs_r49b.md及receipt已由build_version_comparison.py重新生成，明确阶段性/未证明收敛、直接8票未通过，完整逐段差异与真实来源均列出；没有手工改MD或正文。',
    '唯一在途父65069：python round61_advisors.py collect，r61_advisor_g6a/g6b/g56各4/3/3套上限，共读当前双曲、原四步/写后prompt、上游、旧/新I01、完整直接8票、失败prompt与原处置。三份约122万字节附件由原父收取，先完整读泛化/接口/历史才选独立机制生产，不自动实施。',
    '标准/模型强度/联网/原门槛不改；gpt3优先共享6槽总≤10间隔20秒，普通60秒、明确suspicious30分钟，不重置同故障；watchdog/保温不动，heartbeat PAUSED。'
]
p = root / 'STATUS.md'
head = '# 当前接续：I14新中等问题未收敛；R61三顾问在途\n\n最后更新：' + stamp + '（America/New_York）。\n\n' + '\n'.join('- ' + x for x in lines) + '\n\n---\n以下历史追溯，最新优先。\n\n'
p.write_text(head + p.read_text(encoding='utf-8'), encoding='utf-8')
with (root / '试验记录.md').open('a', encoding='utf-8') as f:
    f.write('\n\n## ' + stamp + ' R60原I14未过及实际固定起点比较\n\n' + '\n'.join('- ' + x for x in lines) + '\n')
p = root / 'runs/_batches/round55_current/issue_actions_pending.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['updated_at'] = stamp
d['status'] = 'not_converged_new_specific_medium_findings'
d['must_wait'] = {'65069': 'R61 three advisers original collector; all three full read before candidate selection'}
d['fresh_i14_assessment'] = {'path': 'runs/_batches/i14_after_r59/assessment.json',
    'sha256': B.digest((root / 'runs/_batches/i14_after_r59/assessment.json').read_text(encoding='utf-8'))}
d['actual_fixed_start_direct8'] = direct
d['next_batch'] = 'round61_new_findings'
p.write_text(B.json_text(d), encoding='utf-8')
print(stamp)
