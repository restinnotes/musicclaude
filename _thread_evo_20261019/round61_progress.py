"""Persist the live frozen R61 selection, leaving all prior evidence intact."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B

stamp = datetime.now(ZoneInfo('America/New_York')).isoformat()
lines = [
    '用户澄清：正式成品候选对最新已验收主线（当前r54weave），接纳即推进基准；r49b仅最后收敛MD，已终态旧8票保留但不再提前购买。qu只可作为当前上游同层检查点，绝不当作最终r54验收。',
    'R61两顾问g6a/g56答复全文读、冻结实际附件与字节manifest绑定；均提出相邻事件状态交接，选择无BEADS/REVIEWS的g6a原prompt代表r61bridge，不为同义方案再买双曲。g6a诊断把tracebound快筛口头称未通过不采纳：原4票快筛通过、后续覆盖失败的脚本记录优先。',
    '已冻结round61_boundary/candidates.json及prompt_review；原prompt逐字提取，当前双曲r54为LINE，SECTIONS/CENTER原值，机械replace接口及全部元数据不改。唯一生产父83139（round54_candidates collect --base r54weave --batch round61_boundary --route gpt3s --only r61bridge），2份实际结果未读前不套用或评审。',
    '原三顾问父65069仍收g6b；不重复提交，待第三份完整读后再判断是否有独立机制。两份已完成的独立方案先推进，不额外等待第三份才开始生产。',
    '原R60 I14发现新增具体中等，仍未收敛；当前唯一已验收r54weave，未收候选不入DAG。ZIP冻结，标准及原4票/8票/底线不改，gpt3优先，watchdog/保温不动，heartbeat PAUSED。'
]
p = B.ROOT / 'STATUS.md'
head = '# 当前接续：r61bridge对当前r54写后生产；原g6b顾问在途\n\n最后更新：' + stamp + '（America/New_York）。\n\n' + '\n'.join('- ' + s for s in lines) + '\n\n---\n以下历史追溯，最新优先。\n\n'
p.write_text(head + p.read_text(encoding='utf-8'), encoding='utf-8')
with (B.ROOT / '试验记录.md').open('a', encoding='utf-8') as f:
    f.write('\n\n## ' + stamp + ' R61相邻状态交接代表试验\n\n' + '\n'.join('- ' + s for s in lines) + '\n')
p = B.ROOT / 'runs/_batches/round55_current/issue_actions_pending.json'
d = json.loads(p.read_text(encoding='utf-8'))
d.update({'updated_at': stamp, 'must_wait': {'65069': 'original g6b adviser; two other completed replies read and bound',
    '83139': 'r61bridge actual pair; read original results before apply/measurement'}, 'next_batch': 'round61_boundary'})
p.write_text(B.json_text(d), encoding='utf-8')
print(stamp)
