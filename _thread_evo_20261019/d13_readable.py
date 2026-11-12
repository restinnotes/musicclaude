"""Readable evidence exports, generated from immutable recorded responses."""
from d13_experiment import *
from collections import Counter

def export():
 folder=O/'readable';folder.mkdir(exist_ok=True)
 versions={
 'v1':'压缩核心prompt，JSON五字段；未加心理起点澄清。',
 'v2':'增加轻量心理关切起点许可；A/B/C每首各三次，是主要重复实验。',
 'v3':'增加区分：作者的限制不是主人公的心理目标。小样本行为诊断。',
 'v4':'增加主观亲近/安慰可以成立，不等于证实外部回应。小样本行为诊断。',
 'v5':'用户建议原prompt逐字版本，保留五个原始标题。History解析错误，受污染整链排除。',
 'v6':'原prompt加候选心理假说起点澄清。仍受旧解析器影响，整链排除。',
 'v7':'v6相同prompt，修复History解析器后新跑。',
 'v8':'v7相同prompt，只改变宽松Center输入：Op60亲近与牵挂，Op61眷恋与内在力量。',
 }
 save(O/'protocol_versions.json',versions)
 for p in sorted((O/'drafts').glob('*.json')):
  d=load(p);lines=[d['name'],versions.get(d['version'],''),'是否有效试验：'+str(d.get('pipeline_valid',True)),
   '原始稿按实际完成范围呈现；不足目标长度不算完整重复。','']
  for x in d['sections']:
   run=evo.RUNS/x['run_id'];lines+=['='*60,x['sec']+' / '+x['bars'],'实际run_id：'+x['run_id'],
    '实际输入SHA256：'+x['input_sha256'],'原始回答：',rd(run/'output.txt'),
    '程序提取并传给下一段的History：',json.dumps(x['established_history'],ensure_ascii=False,indent=2),'']
  (folder/(p.stem+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
 rows=[]
 for p in sorted(evo.RUNS.glob('D13_*')):
  files=[p/'call.log'] if (p/'call.log').exists() else sorted(p.glob('call_fail*'))
  for f in files:
   j=load(f);rows.append({'run_id':p.name,'started':j.get('started'),'model':j.get('model'),
    'account':j.get('account'),'seconds':j.get('seconds'),'completed':j.get('completed'),
    'submitted':j.get('submitted',j.get('completed')),'error_code':j.get('error_code'),
    'evidence':str(f),'key':j.get('meta',{}).get('key')})
 rows.sort(key=lambda x:(x['started'] or '',x['run_id']))
 save(O/'过程时间线.json',rows)
 index='''D13 实验档案索引

先读外层的《D13_实验报告_20261025.txt》。本档案记录独立生成、验收与失败，不提供新的G25补缺成稿。

prompts：每个版本A/B/C的完整prompt；每次实际发送的全输入另在模型run的input.txt。
drafts：逐段链的结构化记录。readable：逐稿原始回答全文及下一段实际收到的History。
draft_prefixes：与延长链分开的五段重复实验快照；SHA与原始评审一一对应。
inputs：独立乐谱事实、页码、音乐输入来源与不确定性。珠子只用于事后验收。
forensics/inputs：27段来源审计的全集输入，含D10/D11/D12共68篇旧稿的分段与同源前史。
forensics/reviews：首轮来源审计。其sec顶层曾被模型机械输出S01；权威段号以文件名和对应输入为准，原回答未改写。
forensics/*context*：对来源范围、真实最终History和G25自身有效性的后续复核；只有完整返回并校验的才算完成。
forensics/rejected：被拒绝的空目标复核，不计入结果。
reviews：早期评委版本，仅留档。reviews_v2：通过17例强化校准后的审查，使用draft_sha256绑定具体稿件快照。
calibration_v2：GPT5.6和GPT6各17个正负例、实际回答与错误数。
pools：mechanism的前提、桥、结果、History要求和解释对象；无条数上限，不因同结论而合并。
paths：仅从独立池选取的历史路径；不允许补写G25。未完成的后台请求不等于已有路径。
pipeline_invalid_trials：解析错误造成的无效整链，不能用于评价模型/提示词优劣。
过程时间线：已完成与失败调用的真实时间和证据位置；不是内部思维记录。
provenance_verification：实际模型/max、原始输入输出对应、独立后台任务和冻结旧产物校验。

注意：某稿内部History连续，不等于它解释了重要体验。逐颗珠子的gap必须保留；compatible independent不计作explained。
每轮试验的完成范围、样本数和未完成项以报告与manifest为准，不能从目录中出现某个run名称推断它已经成功。
'''
 (O/'README_实验索引.txt').write_text(index,encoding='utf-8')
 print('READABLE',len(list(folder.glob('*.txt'))),'TIMELINE',len(rows))

if __name__=='__main__':export()
