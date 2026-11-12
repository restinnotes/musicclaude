"""11-12 L34g563（GPT-5.6：写稿层全曲语义去重）有了新证据，交回提出者：它当时把打转在开放评审里排第一的次数从 5/6 降到 2/6，
没成是因为连小字一起重写（人话变差）、交回后又因补回字数规则让大块变多。现在小字已由主线（g68CTRLsk2F：Argon 改写的小字）单独处理好。
请提出者出一份只改大块的去重写法：小字、旁注原样沿用 BASE（主线），每屏至少留一个大块（空屏会被读成主线断档：L39、L38 两次证实）。
python r3/handback_g563c.py → r3/s24/prompt_L34g563c.txt"""
import os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, call, parse, G56
sys.stdout.reconfigure(encoding='utf-8')
ASK = """你是顾问。你在 11-11 出过一份屏幕稿写法（L34 方案三：全曲命题账本、语义去重，附在最后）。这两天的新证据，交回给你：

【你的写法当时的效果】开放评审（三位、两首）把“原地打转”排第一的次数从主线的 5/6 降到 2/6——是这一整批里唯一真正让打转减轻的方案。没成的原因：①它连小字一起重写，小字人话问题翻倍；②交回后补回主线的字数规则、要求核心命题首现完整，大块又变多（36/38 → 40/47），打转回到第一。

【之后发生的事】
- 小字已由新主线单独处理好：主线 = K28b 的大块 + Argon 改写的小字（听的人的具体感受、不复述大字、不长于原条、保住画面比喻）。新形式评法下中等 13/17（K28b 32/27），盲比两首都赢 K28b。现在开放评审排第一的仍是打转，出在大块上。
- 屏幕形式改了：每屏开头大字小字一起出现、留到屏末，不按秒依次出现，旁注不出字（用户：“只要大字小字”“bullet 不是时序”）。
- 有一屏完全没有大块，会被读成“主线断档”（两次证实），所以每屏至少要留一个大块。

【这次请你】写一份只改大块的写法：
- 先读完整条线，建立全曲命题账本；同一个认识、决定、担心、问题，大块里只在第一次出现时放，后面只放真正新增的（新的后果、新的行动、确实不同的体验）。
- 大块必须是线的原话，只切不改（用户定的）；每屏至少一个大块：如果这一屏的线全是重复，放这一屏最不重复、最贴音乐的那一句。
- 小块、旁注原样保留（BASE 里是什么就是什么），只有两种情况动小块：大块删掉后它挂靠的位置变了，改它的 after；大块和某个小块是同一件事，删那个小块。
- 主线写法里关于字数、逗号、accent、emotion、from 的规则照旧；at 和旁注不用写（形式改了）。
- 不许退步：小字的人话、两首盲比对主线不输、核心那件事只看大块看得懂。

只输出 JSON：{"analysis":"…","prompt":"完整写稿提示词"}。占位符原样保留：{BUDGET} {DAGSTD} {FINAL} {BEADS} {BASE}，输出格式和 BASE 一样。提示词里不放具体作品内容。回答时请不要进行联网搜索。

【你原来的写法】
{MINE}

【主线写法（K28b 的大块规则）】
{MAIN}
"""
if __name__ == '__main__':
    p = S/'prompt_L34g563c.txt'
    if not p.exists():
        msg = ASK.replace('{MINE}', (S/'prompt_L34g563.txt').read_text(encoding='utf-8')).replace('{MAIN}', (S/'prompt_K28b.txt').read_text(encoding='utf-8'))
        r = parse(call('hb_L34g563c', msg, G56, 'gpt3s', 'dag-advisor')); p.write_text(r['prompt'], encoding='utf-8'); print('分析：', r.get('analysis'))
    t = p.read_text(encoding='utf-8')
    print('缺占位符：', [x for x in ('{BUDGET}', '{DAGSTD}', '{FINAL}', '{BEADS}', '{BASE}') if x not in t] or '无', '；泛化检查：', prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', t)) or '过')
