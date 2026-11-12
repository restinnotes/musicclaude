import pathlib,json,re,collections
W=pathlib.Path(__file__).parent/'audit';fs=json.loads((W/'classified.json').read_text(encoding='utf-8'))
def evidence(f):return f['text']+'\n'+'\n'.join(json.dumps(b.get('input',{}),ensure_ascii=False) for b in f['tools'])
def choose(start,end,pattern=None):
 return [f for f in fs if f['owner']=='main' and start<=f['timestamp']<end and (not pattern or re.search(pattern,evidence(f),re.I))]
def pack(a,label):return {'label':label,'requests':len(a),'cost':sum(f['cost'] for f in a),'input_tokens':sum(f['usage']['input_tokens'] for f in a),'cache_read_input_tokens':sum(f['usage']['cache_read_input_tokens'] for f in a),'cache_creation_input_tokens':sum(f['usage']['cache_creation_input_tokens'] for f in a),'output_tokens':sum(f['usage']['output_tokens'] for f in a),'indices':[f['index'] for f in a],'message_ids':[f['message_id'] for f in a]}
cases={}
cases['web_workaround']=pack(choose('2026-10-24T04:40','2026-10-24T04:49',r'NO_WEB|不要进行联网搜索|websocket|no.web|recover\.py'),'传输排障与禁网规则引入；属于有效工程修复与实验条件变更混合，不能全算乌龙')
cases['web_wrong_hypotheses_explicit']=pack(choose('2026-10-27T02:33','2026-10-27T18:29:09',r'draft1[6-9]\.py|\bd1[6-9][ftps]|modeltrace|mt_gpt3|mt_mimic|小模型|账号.{0,30}(?:差|弱|低|退步)|思考强度.{0,30}(?:差|低|问题|水平)'),'明确涉及模型／账号／强度排查与 D16–D19；直接相关请求成本，非全可避免')
cases['web_discovery_restore']=pack(choose('2026-10-27T18:29:09','2026-10-27T20:46',r'NO_WEB|不要联网|联网|draft20|d20[ftps]|D20|toolsUsed|D21'),'变量核对、联网根因调查、小样恢复及记录')
cases['web_influence_window']=pack(choose('2026-10-24T04:45','2026-10-27T20:46'),'受影响时间窗全部请求，仅作上界暴露范围，绝不当成浪费')
cases['judge_early']=pack(choose('2026-10-20T13:19','2026-10-20T17:24',r'judge_v[123]|calib|\bC[234]\b|V3ALL|串珠|评委|排序|Center|History|鲜活'),'早期目标纠偏、用户排序与评委校准')
cases['judge_late']=pack(choose('2026-10-28T12:17','2026-10-28T15:18',r'advisor|顾问|结构缺陷|主线|机制|修准|P4[a-f]|P[567]|包3'),'后期局部覆盖与整首验收冲突的诊断、顾问与修准讨论')
examples=[
 ('Q1','简单格式／JSON 修复','2026-10-20T23:37','2026-10-21T00:01',r'final3_b|measures|小节|S10'),
 ('Q2','跨模型任务回收匹配','2026-10-24T04:22','2026-10-24T04:55',r'recover\.py|find_job|匹配|回收|模型'),
 ('Q3','20 秒跨进程提交间隔','2026-10-27T19:40','2026-10-27T19:48',r'_space_submission|gpt3_call|20|间隔'),
 ('Q4','禁网规则与控制变量','2026-10-24T04:40','2026-10-24T04:49',r'NO_WEB|不要进行联网搜索'),
 ('Q5','评委与用户认可样本冲突','2026-10-20T13:19','2026-10-20T17:24',r'judge_v[123]|排序|calib|串珠|评委'),
 ('Q6','整体 Thread 与局部覆盖冲突','2026-10-28T12:17','2026-10-28T15:18',r'主线|整首|顾问|advisor|包3|P4d'),
 ('Q7','大量 GPT 批次的运行管理','2026-10-27T21:19','2026-10-28T12:17',r'watchdog|Monitor|Cron|P4|p4|pool4|synth3'),
 ('Q8','珠子来源与完整 STRUCT','2026-10-21T23:00','2026-10-22T02:30',r'beadgraph|STRUCT|读者稿|bead_graph|ABC|听法|珠子'),
 ('Q9','成品关系图交付与完整性','2026-10-28T15:26','2026-10-28T16:30',r'关系图|deliver|合并|格式|半成品'),
 ('Q10','模型身份／强度归因','2026-10-27T16:29','2026-10-27T18:30',r'modeltrace|ModelTrace|水杯|杯题|mt_gpt3|mt_mimic|小模型')]
for ident,label,a,b,p in examples:cases[ident]=pack(choose(a,b,p),label)
(W/'case_costs.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
for k,c in cases.items():print(k,c['requests'],round(c['cost'],3),c['input_tokens'],c['cache_read_input_tokens'],c['cache_creation_input_tokens'],c['output_tokens'])
