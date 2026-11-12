import json,pathlib,re,collections,statistics
W=pathlib.Path(__file__).parent/'audit'
fs=json.loads((W/'features.json').read_text(encoding='utf-8'))
NAMES={'A':'核心设计判断','B':'艺术内容审阅','C':'实验工程开发','D':'技术排障','E':'实验执行管理','F':'结果整理与初筛','G':'委托与协调','H':'用户沟通与交付','I':'系统与环境开销'}
RX=lambda p,s:bool(re.search(p,s,re.I))
eng=r'(?:evo|gpt[234]_call|mg_call|nz_call|recover|verify_|test_|transport|watchdog|matching|modeltrace|resume|mimic|browser|bridge|debug|slots|concurrency|cooldown|timeout|retry)'
diagnostic=r'(?:traceback|upstream_|incomplete_response|unusual_activity|websocket|docker|curl |modeltrace|杯题|降智|限流|截断|链路|端口|bridge|curl|taskkill|docker|429|transport|procmon)'
concept=r'(?:Thread|Center|History|Connection|why.?now|串珠|主线|心理机制|因果|解释力|独立稿|珠子|评委|评审|方案|计划|假阳性|覆盖|人话|前史)'
art=r'(?:编造|读起来|听感|温柔|亲近|失去|欲望|起点|回忆|身体|怀念|克制|前史|主轴|写反|说话|幸福|余味|主体|孤独|意象|梦境)'
status=r'(?:tail\b|ps\b|pgrep\b|Get-Process|watchdog\.py|ls\b|find\b|wc\b|stat\b|sleep\b|jobs\b|head\b|Monitor|CronCreate|CronDelete|TaskStop|poll|进度|状态|监[视控]|还在跑|是否完成|等[待候])'
agg=r'(?:Counter\(|statistics|mean\(|median\(|percentile|summari|aggregate|汇总|统计|评分|得分|相反|解释了|labels?|coverage|cover|compare|evaluations/|evaluations\\)'
roots=[]
for f in fs:
 if f['owner']=='main' and f['root_uuid'] and f['root_uuid'] not in [x[0] for x in roots]:roots.append((f['root_uuid'],f['root_text']))
root_idx={u:i for i,(u,t) in enumerate(roots)}
for n,f in enumerate(fs):
 names=[b['name'] for b in f['tools']];ns=set(names)
 inp='\n'.join(json.dumps(b.get('input',{}),ensure_ascii=False) for b in f['tools'])
 commands='\n'.join(str(b.get('input',{}).get('command','')) for b in f['tools'])
 desc='\n'.join(str(b.get('input',{}).get('description','')) for b in f['tools'])
 txt=f['text'];root=f['root_text'];trig=f['trigger_text']
 writes=[b for b in f['tools'] if b['name'] in ['Write','Edit']]
 paths=' '.join(str(b.get('input',{}).get('file_path','')) for b in writes)
 embedded=RX(r"(?:cat\s*>>?\s*\S|write_text\(|write_bytes\(|open\([^\n]{0,180},\s*['\"](?:w|a)['\"]|apply_patch|Set-Content|sed\s+-i\b)",commands)
 iscode=bool(writes) or embedded
 file_writes=RX(r'\.(?:py|sh|ps1|cmd|js|ts)\b',paths) or embedded
 prompt_write=RX(r'(?:prompts[/\\].*\.(?:md|txt)|THREAD_SPEC|PLAN_|prompt_versions|prompt_template)',paths)
 pure_ui=bool(ns) and ns<=set(['mcp__ccd_turn__update_plan','mcp__ccd_turn__wrap_up','mcp__ccd_turn__mark_chapter'])
 pure_monitor=bool(ns) and ns<=set(['Monitor','TaskStop','CronCreate','CronDelete','mcp__ccd_turn__update_plan'])
 scope_text=(txt+' '+desc)
 if ns & {'Agent','SendMessage','mcp__ccd_session__start_session','ListAgents','mcp__ccd_session_mgmt__list_sessions','mcp__ccd_session_mgmt__list_events','mcp__ccd_session_mgmt__search_session_transcripts'}:
  cat,why,conf='G','明确的委托／会话通信工具','high'
 elif f['model']=='claude-haiku-5-5' and f['owner']=='main':
  cat,why,conf='D','主会话 Haiku 请求实际读取语言规则与钩子相关文件；不假定它是摘要服务','manual'
 elif f['owner'].startswith('agent-'):
  cat,why,conf='F','原生 Haiku 按委托检索历史语料并整理证据','high'
 elif pure_ui:
  if len(txt)>300 and RX(concept,txt):cat,why,conf='A','Desktop 工具同请求内包含实质目标／计划说明，保留核心判断','medium'
  elif len(txt)>300:cat,why,conf='H','Desktop 工具同请求内包含实质用户答复','medium'
  else:cat,why,conf='I','仅调用 Desktop 计划／结尾工具；这是请求归因，非纯工具边际成本','medium'
 elif pure_monitor:
  cat,why,conf='E','监视／定时／停止工具管理','high'
 elif iscode:
  if prompt_write and not file_writes:
   cat,why,conf='A','直接修改目标／生成／评审规范文档','medium'
  elif RX(eng,paths+' '+desc) and RX(diagnostic,inp+' '+txt+' '+root):
   cat,why,conf='D','调用器／恢复／并发／基础设施的诊断修复','medium'
  elif not file_writes and RX(r'(?:REPORT|RESULTS|README|\.md|\.txt)',paths):
   cat,why,conf=('A','设计与评审规则文档','medium') if RX(r'(?:spec|plan|prompt|目标|标准|计划)',paths+' '+desc) else ('H','生成报告／交付文档','medium')
  elif RX(r'(?:pack|zip|deliver|format|report|打包|交付|手机|发送|发到|导出|图化|呈现)',desc+' '+paths) and not RX(r'(?:generator|生成器|caller|调用器)',desc):
   cat,why,conf='H','文件打包／导出／交付的实现','medium'
  else:
   cat,why,conf='C','实际编写／修改可执行脚本；艺术提示词成分仍需 Claude 验收','medium'
 elif RX(r'(?:diagnos|debug|fail|error|probe|broken|truncat|transport|quota|cup|修复|排查|失败|报错|限流|截断|探测|试探|降智|故障|链路|水杯)',desc):
  cat,why,conf='D','工具描述明确是故障诊断／技术探测；非凭输出表面归类','high'
 elif RX(diagnostic,commands+' '+desc) and not (RX(r'\bpython\s+[^\n]{0,100}(draft|cover|judge|pool|synth|line|graph)\w*\.py',commands) and not RX(r'(?:debug|docker|curl|traceback)',commands+' '+desc)):
  cat,why,conf='D','实际读取诊断资料／探测服务／调查运行故障','medium'
 elif ns & {'SendUserFile','AskUserQuestion','mcp__Claude_Browser__preview_start','mcp__Claude_Browser__computer'}:
  cat,why,conf='H','交付文件／展示／用户沟通','high'
 elif not ns:
  if f['trigger_kind']=='notification' and len(txt)<260:
   cat,why,conf='E','后台通知后的短状态响应；含少量判断的上界归类','medium'
  elif RX(concept,root+' '+txt) and len(txt)>350:
   cat,why,conf=('B','对具体候选体验／逻辑的直接审阅','medium') if RX(art,txt) and RX(r'(?:S\d|小节|版本|稿|Op\.?\s?6|\d[–—-]\d)',txt) else ('A','目标／机制／评审方向的解释与决策','medium')
  elif f['trigger_kind'] in ['notification','system']:
   cat,why,conf='E','后台事件／定时触发后的状态处理','medium'
  elif RX(diagnostic,root+' '+txt):cat,why,conf='D','无工具输出中的技术诊断结论','medium'
  else:cat,why,conf='H','直接答复／交付说明','medium'
 elif RX(r'(?:progress|run states|whether.*ready|wait loop|what finished|running process|状态|进度|是否完成|是否恢复|后台任务|运行情况)',desc) and not RX(r'(?:全文|full text|艺术|心理|逻辑)',desc):
  cat,why,conf='E','工具意图明确检查进度／完成状态；即使使用 JSON 聚合','high'
 elif RX(r'(?:cat|sed|head|Read|read_text|open\()',commands+' '+' '.join(names)) and RX(r'(?:output\.txt|\.md\b|\.parsed\.json|sections|beads|reader|deliverable)',commands+' '+inp) and RX(art,txt+' '+desc) and not RX(r'Counter\(|mean\(|median\(',commands):
  cat,why,conf='B','读取候选／珠子／原稿并检查具体心理内容','medium'
 elif RX(agg,commands+' '+desc):
  cat,why,conf='F','读取评审文件、聚合评分或初步比较','medium'
 elif RX(status,commands+' '+desc) or RX(r'\b(?:python|bash|nohup)\s+[^\n]{0,180}\.(?:py|sh)',commands):
  cat,why,conf='E','运行批次／进程／日志／完成状态检查','medium'
 elif RX(r'(?:tasks[/\\].*\.output|\.log\b|Stop-Process|Get-CimInstance|Get-PSDrive)',commands) and not iscode:
  cat,why,conf='E','读取任务输出／日志或管理进程的明确工具证据','high'
 elif RX(r'(?:arts\.clean|evo\.output|tg_winners\.view|bead_text|beads\[|bead_graph/|bead_graph\\)',commands) and not iscode:
  cat,why,conf='B','实际展开并阅读作品／珠子内容','medium'
 elif ns & {'Read','Grep'} and RX(r'\.py\b',inp) or RX(r'(?:grep[^\n]*(?:def |def\\|^def|\.py)|sed[^\n]*\.py|cat[^\n]*\.py)',commands):
  cat,why,conf='C','实际阅读或定位工程源代码；未把它归作固定系统成本','medium'
 elif RX(r'(?:Compress-Archive|\.zip\b|打包)',commands+' '+desc):
  cat,why,conf='H','文件归档／交付','medium'
 elif RX(concept,root+' '+scope_text):
  cat,why,conf='A','工具证据与当前设计任务结合；混合任务归类','low'
 else:cat,why,conf='I','工具／环境信息或不能可靠细分的请求','low'
 # A narrowly defined automation-only lower bound excludes artistic interpretation and error diagnosis.
 short=not txt or len(txt)<=220
 simple_statement=not RX(r'(?:但是|不过|因为|说明|意味着|主轴|写反|编造|更容易|应[该对]|需要改|不算|判定|问题在|我[看想]一下|因果|前史|证据)',txt)
 poll_strict=cat=='E' and short and simple_statement and (pure_monitor or (not ns and f['trigger_kind']=='notification') or (ns<=set(['Bash','PowerShell','TaskStop','Monitor']) and RX(status,commands+' '+desc) and not RX(r'(?:cat[^\n]*output|read_text|Counter\(|json\.load|curl|docker|python\s+[^\n]*\.py)',commands)))
 overrides={2039:('A','人工复核：该请求核心是 Center 生成机制回归诊断，代码修改与核心判断混合，保守保留'),1630:('A','人工复核：开始核对 humanizer 历史与用户完整设计要求，保守归设计'),1719:('A','人工复核：回溯并提取用户关于人话的原始约束'),2087:('H','人工复核：给用户打包交接资料，不是技术排障'),3498:('C','人工复核：离线检查脚本规则与提示词接线'),184:('H','人工复核：编写早期实验总报告')}
 if n in overrides:cat,why=overrides[n];conf='manual';poll_strict=False
 f.update({'index':n,'category':cat,'category_name':NAMES[cat],'classification_reason':why,'classification_confidence':conf,'poll_strict':poll_strict,'pure_desktop':pure_ui,'has_wrap_up':'mcp__ccd_turn__wrap_up' in ns,'has_update_plan':'mcp__ccd_turn__update_plan' in ns,'tool_names':names,'iscode':iscode,'root_index':root_idx.get(f['root_uuid'],-1)})
(W/'classified.json').write_text(json.dumps(fs,ensure_ascii=False),encoding='utf-8')
for c in NAMES:
 a=[f for f in fs if f['category']==c];print(c,NAMES[c],len(a),round(sum(f['cost'] for f in a),3),round(100*sum(f['cost'] for f in a)/sum(f['cost'] for f in fs),2))
for tag in ['poll_strict','pure_desktop','has_wrap_up','has_update_plan']:
 a=[f for f in fs if f[tag]];print(tag,len(a),round(sum(f['cost'] for f in a),3))
print('LOW',sum(f['classification_confidence']=='low' for f in fs))
print('C_SAMPLES')
for cat in ['C','D','E','F','B','I']:
 aa=[f for f in fs if f['category']==cat]
 for f in sorted(aa,key=lambda f:f['cost'],reverse=True)[:5]:
  print(cat,f['index'],round(f['cost'],3),f['timestamp'],(' / '.join(str(b.get('input',{}).get('description','')) for b in f['tools']))[:180],f['text'][:160].replace('\n',' '))
