"""Offline before/after latency comparison; makes no provider requests."""
import json,re,statistics
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/'evaluations/d13_20261025'
DEST=Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def stats(group):
 g=[r for r in group if r['ok'] and isinstance(r.get('sec'),(int,float))]
 if not g:return {'n':0}
 return {'n':len(g),'median_seconds':statistics.median(r['sec']for r in g),
  'mean_seconds':statistics.mean(r['sec']for r in g),'min_seconds':min(r['sec']for r in g),
  'max_seconds':max(r['sec']for r in g),'median_response_characters':statistics.median(r['chars']for r in g)}
def main():
 rows=read(O/'latency_change_initial_rows.json')
 groups={}
 for side in ['before','after']:
  a=[r for r in rows if r['side']==side]
  groups[side]={'all_successful_tasks':stats(a),
   'music_generation_only':stats([r for r in a if r['kind']=='generation']),
   'music_excluding_invalid_v5_v6':stats([r for r in a if r['kind']=='generation'and r['version']not in ['v5','v6']]),
   'v2_only':stats([r for r in a if r['version']=='v2'])}
 strat=defaultdict(list)
 for r in rows:
  if r['ok']and r['version']=='v2':
   m=re.match(r'D13_d13v2([ABC])_56_(op\d+)_r\d+_S(\d+)',r['rid'])
   if m:strat[(m[1],m[2],m[3])].append(r)
 matched=[]
 for key,g in strat.items():
  if {x['side']for x in g}=={'before','after'}:
   matched.append({'variant':key[0],'work':key[1],'section':key[2],
    'before':stats([x for x in g if x['side']=='before']),
    'after':stats([x for x in g if x['side']=='after']),
    'runs':[{k:x[k]for k in ['rid','t','side','sec','chars']}for x in g],
    'control_limit':'Same version/variant/work/section; distinct self-generated histories, not identical full input.'})
 result={'created_utc':datetime.now(timezone.utc).isoformat(),
  'breakpoint':'2026-10-25T17:54:00-04:00, first ASYNC_TOPIC_REQUIRED start; not a proven model-routing change',
  'group_assignment':'Request start time; successful backend jobs on gpt4 only',
  'snapshot_source':'latency_change_initial_rows.json, collected before new ModelTrace probes',
  'groups':groups,'same_section_controls':matched,
  'limitations':['Elapsed wall time includes waiting/transport/output; internal thinking time and reasoning-token usage are unavailable.',
   'Post-breakpoint successful answers are a selected subset; incomplete calls cannot be treated as fast answers.',
   'v1/v2/v3 versus v4-v8 differ in prompt and context; full same-input pre/post pairs were not found.',
   'The completed independent quality reviews do not supply a balanced matched pre/post sample; quality change is not statistically established.',
   'No claim that preserved requested/returned model slugs authenticate serving weights or compute allocation.']}
 (O/'latency_change_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['D13 故障前后耗时核查（离线，没有新增模型调用）',
  '分界：2026-10-25 17:54 EDT，按请求开始时间归组。这是首次接收异常的开始时间，不是已证实的模型切换时间。','',
  '口径 | 故障前样本数/中位秒/平均秒 | 故障后样本数/中位秒/平均秒']
 for key,label in [('all_successful_tasks','全部成功任务（混合审计/评审/生成）'),('music_generation_only','仅音乐主生成 GPT5.6'),('music_excluding_invalid_v5_v6','音乐主生成且排除管道无效的v5/v6'),('v2_only','相同v2提示词版本')]:
  a=groups['before'][key];b=groups['after'][key]
  lines.append(f"{label} | {a['n']}/{a['median_seconds']:.2f}/{a['mean_seconds']:.2f} | {b['n']}/{b['median_seconds']:.2f}/{b['mean_seconds']:.2f}")
 lines+=['','全部混在一起时平均耗时下降，但音乐主生成单独比较时耗时上升。前期混有耗时很长的评审/来源审计；不能把任务构成差异当成模型缩短思考。',
  '相同v2提示词版本的成功生成，中位耗时也从约24秒升到约47秒。不过段落、变体和History构成仍不同，不能称为严格受控实验。','',
  '唯一跨分界的同版本/同变体/同作品/同段落组：']
 for x in matched:
  lines.append(f"{x['variant']} {x['work']} S{x['section']}: 前{x['before']['n']}条、中位{x['before']['median_seconds']:.2f}秒；后{x['after']['n']}条、中位{x['after']['median_seconds']:.2f}秒。每条自生History不同。")
 lines+=['','最新完整音乐回答（19:20发起的v8/S02）后台耗时61.64秒、正文1197字符。','',
  '当前结论：没有发现故障后成功音乐回答整体突然变快；已记录的墙钟耗时方向相反。内部实际思考时间/推理token不可见，因此不能用墙钟耗时单独证实或排除算力缩减。',
  '质量下降：目前缺乏平衡、同条件、经过独立评审的故障前后样本。新旧提示词、前史、段落和成功样本选择均有混杂，不能声称已经证明显著退步。',
  '后续ModelTrace独立保存，只评数字行为归因，不将指纹得分当音乐质量分数。']
 DEST.mkdir(exist_ok=True)
 report=DEST/'D13_故障前后耗时核查_20261025.txt';report.write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'report':str(report),'groups':groups,'same_section_controls':matched},ensure_ascii=False))
if __name__=='__main__':main()
