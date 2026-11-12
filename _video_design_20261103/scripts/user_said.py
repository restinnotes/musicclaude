import re,sys
sys.stdout.reconfigure(encoding='utf-8')
F=r'D:\musicclaude\project_dialogues\02_切换前_阶段02_视听呈现与包装规范_合集.md'
txt=open(F,encoding='utf-8',errors='replace').read()
parts=re.split(r'(?m)^### (You|ChatGPT|Assistant|GPT|🧑 User|Claude)[^\n]*\n',txt)
# parts: [pre, role, body, role, body...]
seen=set();out=[]
kw=re.compile(r'可视化|屏|字幕|画面|视频|排版|滚动|动画|配色|颜色|钢琴卷|瀑布|谱|观众|读者|阅读|注意力|听众|小节')
for i in range(1,len(parts)-1,2):
    if parts[i] not in('You','🧑 User'):continue
    b=parts[i+1].strip()
    b=b[:1400]
    if len(b)<14 or b[:80] in seen: continue
    seen.add(b[:80])
    if kw.search(b): out.append(b)
print(len(out))
for b in out: print('---\n'+b[:700])
