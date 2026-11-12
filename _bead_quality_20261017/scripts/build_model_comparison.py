"""Display actual experimental readers without changing or rating them."""
from pathlib import Path
import json,re
from build_delivery import cell,clean_old
R=Path(__file__).resolve().parents[1]
def j(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def main():
 calls=j('experiments/ACTUAL_CALLS.json');c={x['job_id']:x for x in calls}
 assert len(c)==12 and all(x['status']=='ok' for x in c.values())
 decisions=j('experiments/CASE_READINGS.json')
 def whole(k):return (R/c[k]['dir']/'response.txt').read_text(encoding='utf-8-sig')
 def reader(k):
  text=whole(k)
  m=re.search(r'^#{1,3}\s*读者正文[^\n]*\n(.*?)(?=^#{1,3}\s*(?:采材证据|取舍)|\Z)',text,re.M|re.S)
  if not m:m=re.search(r'^#{1,3}\s*②[^\n]*\n(.*)\Z',text,re.M|re.S)
  assert m,('Reader marker not found',k)
  s=clean_old(m[1]).strip().strip('-').strip()
  s=re.sub(r'^#{1,6}\s*([^\n]+)',r'**\1**',s,flags=re.M)
  return s
 def link(k):return '['+k+']('+c[k]['dir'].replace('\\','/')+'/response.txt)'
 def pair(a,b,ha,hb):
  return '\n'.join([f'| {ha} | {hb} |','|---|---|','| '+cell(reader(a))+' | '+cell(reader(b))+' |','',link(a)+' · '+link(b),''])
 out=['# 模型与方法：实际写出了什么','',
     '结论限于本次单次受控试写：改任务能使GPT-6w恢复原料的身体触感；Flash没有在三段中显示稳定优势，因此保留GPT-6w作为优先试写通道。A2作为最小写作方案保留，仍需主编辑逐段判断。没有宣布一个不需编辑的自动成稿冠军。','',
     '**以下对照均直接摘取已落盘响应的读者部分**，只移除UI标签／包装和调整标题显示。取材表、选材单、内部稿、完整响应仍在链接中。最终十四段编辑稿不混在外部模型原稿栏。','',
     '## 实际设计与可比较范围','',
     '| 比较 | Pool | 改变什么 | 保持什么 |','|---|---|---|---|',
     '| S02：OLD／A1／A2／B2／C2 | pilot28完整相关原文 | 写作任务；A1→A2是第二轮整体指令修订 | GPT-6w、max、固定4–16、同一来源Pool |',
     '| S02：GPT-6w／Flash，A1与A2 | 同一pilot28 | 请求模型／通道 | 每轮各自的完整prompt文件hash |',
     '| S07：GPT-6w／Flash，A2 | 正式30 | 请求模型／通道 | 完整prompt、51–61、同一事实提示 |',
     '| S13：GPT-6w／Flash，A2 | 正式30 | 请求模型／通道 | 完整prompt、103–110、同一事实提示 |',
     '| S13：OLD／A2 | 正式30 | 写作任务 | GPT-6w、同一Pool及同一事实裁决 |','',
     '共12次实际成功调用：GPT-6w 8次、Flash 4次。第一轮S02 A1未作为合格内容采用；技术成功不等于内容认可。未执行的早期B/C计划不算调用。没有继续第三轮修改提示词，也没有新增A采样。','',
     'GPT请求／服务端标签为gpt-6-thinking，max；Flash请求路由为antigravity-tools/gemini-3.8-flash-high，无法独立核验底层权重。两通道读取同一冻结文件，GPT既有通道会归一换行和末尾空白，Flash未给上游收到文本的独立hash；这里的“同输入”指相同完整冻结文件与相同任务。来源、通道及版本限制见 [SOURCES_AND_LIMITS.md](SOURCES_AND_LIMITS.md)。','',
     '## 第一轮：两种模型都没有达到取材目标','',
     'A1把听觉事实与禁止补写放得过重。两个模型都趋向双音、和声与起伏导览；Flash的弃用说明甚至出现“纯粹听觉形态”。这不支持把首次失败专归GPT-6。','',
     pair('S02_G6_A_initial','S02_FLASH_A_28','GPT-6w · A1完整读者部分','Flash · 同A1完整读者部分'),
     '## 第二轮：同一模型改任务','',
     '### S02：旧方法与A2','',
     pair('S02_G6_OLD_initial','S02_G6_A2_28','GPT-6w · 旧方法','GPT-6w · A2'),
     decisions['S02_old_vs_A2'],'',
     '### S13：同Pool、同事实提示，旧方法与A2','',
     pair('S13_G6_OLD_30','S13_G6_A2_30','GPT-6w · 旧方法＋事实校核','GPT-6w · A2＋同事实校核'),
     decisions['S13_old_vs_A2'],'',
     '## 第二轮：同任务换模型','']
 for sid,count in [('S02',28),('S07',30),('S13',30)]:
  a=f'{sid}_G6_A2_{count}';b=f'{sid}_FLASH_A2_{count}'
  assert c[a]['prompt_sha256']==c[b]['prompt_sha256']
  out += [f'### {sid} · A2','',f'相同冻结prompt SHA256：`{c[a]["prompt_sha256"]}`。','',pair(a,b,'GPT-6w · 完整读者部分','Flash · 完整读者部分'),decisions[sid+'_model'],'']
 out += ['## A／B／C：是否需要显式多一层选材','',
         'A2先以优秀原表达为骨架；B2允许一次直接综合；C2要求先输出选材单，再写正文。三者共用第二版核心任务，S02均使用同一pilot28 Pool、GPT-6w与max。C2是在一次模型调用中增加选材输出，不是独立模型流水线。','',
         '| A2 · 原表达优先 | B2 · 直接综合 | C2 · 先列选材单 |','|---|---|---|',
         '| '+' | '.join(cell(reader(f'S02_G6_{m}_28')) for m in ['A2','B2','C2'])+' |','',
         ' · '.join(link(f'S02_G6_{m}_28') for m in ['A2','B2','C2']),'',decisions['ABC'],'',
         '## 最终稿额外做了什么','',
         'S02留肩膀／皮肤／手掌，删掉模型恢复后又追加的时间哲理；S07选择回放谈话与感觉本身，避免同时串起怀抱、无法抵达他人、语言失效等多套主线；S13保留暴露与笑容发僵，给花饰的转圜留下空间。其余十一段由主编辑按同样的原句优先、范围校核与必要精编方法扩展。完整稿另存 [READER.md](READER.md)，并在 [逐段对照](BEAD_CONTENT_REVIEW.md)展示来源。','',
         '这一步使最终产品更集中，但不能算成模型原样输出的能力。没有做“所有方法×所有模型×十四段”的大矩阵，也没有用模型互评给这些文字打分。','',
         '## 能说与不能说','',
         '- 能说：同一GPT-6w在改变任务后，实际保住了先前丢失的具象细节；三个A2模型对照不支持现在整体切换到Flash。',
         '- 能说：旧方法加事实校核与新方法加事实校核可直接比较；对照中共同改善的事实位置，不能独归新写作方法。',
         '- 不能说：某个提示词句子单独造成全部收益。第一版到第二版同时改变了取材优先级、输出顺序与说明要求；不是逐句消融。',
         '- 不能说：A2在所有音乐或所有重复运行中胜过B2/C2。方法差异只在S02各试一次，模型差异在三段各试一次；支持当前选择，不支持普遍排名。',
         '- 不能说：生产上下文修复版已被这些实验调用完整测试。继承标题和Luna说明在实验后单独修复，最终十四段编辑使用该版本。','',
         '调用清单：[ACTUAL_CALLS.md](experiments/ACTUAL_CALLS.md)；输入、实际字节hash、模型完成证据、原始响应均可追溯。']
 (R/'MODEL_METHOD_COMPARISON.md').write_text('\n'.join(out)+'\n',encoding='utf-8',newline='\n')
 print('Wrote full actual reader comparison for 12 completed calls.')
if __name__=='__main__':main()
