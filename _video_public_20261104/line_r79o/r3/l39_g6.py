"""11-12 对比“谁写改法”：同一个想法（大块只放真正往前走的屏，其余屏只留小块），我写一份（prompt_L39me.txt），GPT-6 按同样的说明写一份（prompt_L39g6.txt）。其余全同（Argon 写稿、r2e、K28b 底稿、同一快筛）。"""
import os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, call, parse, G6
sys.stdout.reconfigure(encoding='utf-8')
ASK = """你是顾问。请为一个大模型写一份完整的“屏幕稿落字”提示词。

背景：我们把钢琴曲做成给普通观众“边听边看”的视频屏幕稿。每屏有大块（主线，必看，来自“线”的原话）、小块（听众的感受，来自“珠子”）、旁注。当前做法（提示词附在下面）把线的每段都放成大块。问题：开放评审一致说只看大块时人物“原地打转”——同一个心思、同一个决定隔几屏又被说一遍。原因之一：线每段都有几句话，音乐会回到前面的情绪，线也跟着把说过的心思再说一遍，大块把它们全放上屏。

要你实现的想法（已经定了，不要换想法）：大块只放这个人真正往前走了一步的地方；线只是把前面的心思再说一遍的屏，不放大块（big 为空数组），只留小块，让音乐和听感撑住这一屏。

必须保留的：大块必须是线的原话，只切不改（这条是用户定的，改写会丢人话）；小块和旁注原样保留；字数、出现时间、accent/emotion/from 的规则、输出格式与下面的现有提示词一致；占位符 {BUDGET} {DAGSTD} {FINAL} {BEADS} {BASE} 原样保留；提示词里不放具体作品的内容或例子。要防的风险：删多了只看大块的人看不懂核心那件事；该放的新一步被当成重复删掉。

只输出 JSON：{"prompt":"完整提示词"}。回答时请不要进行联网搜索。

【现有提示词】
{BASE_PROMPT}
"""
if __name__ == '__main__':
    p = S/'prompt_L39g6.txt'
    if not p.exists():
        r = parse(call('l39_g6', ASK.replace('{BASE_PROMPT}', (S/'prompt_K28b.txt').read_text(encoding='utf-8')), G6, 'gpt3s', 'dag-advisor'))
        p.write_text(r['prompt'], encoding='utf-8')
    t = p.read_text(encoding='utf-8')
    print('GPT-6 提示词', len(t), '字；缺占位符', [x for x in ('{BUDGET}', '{DAGSTD}', '{FINAL}', '{BEADS}', '{BASE}') if x not in t] or '无', '；泛化检查', prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', t)) or '过')
