"""11-08 用户：“可能应该需要把所有的标准都再次修订一下……从刚开始制定标准到现在的所有聊天记录……只看我自己说的”。
两位顾问各自只读用户原话（10-17 至 11-08），独立整理出正交的标准维度（DAG 和 DAG2 各一套，标出共用的），再对照现行标准找缺漏、重复、冲突。结果 r3/std_review_{g6|g56}.md"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pub24 import G6, G56, call
sys.stdout.reconfigure(encoding='utf-8')
EVO = Path('D:/musicclaude/_thread_evo_20261019'); PUB = Path('D:/musicclaude/_video_public_20261104')
ASK = """你是独立顾问。我们在做古典音乐“边听边读/边听边看”的文字：
- DAG（第一段流水线）产出定稿：珠子（逐段记录听的人此刻心里和身上的感受）和线（一个人在这首曲子里经历的一件事，把珠子串起来）。
- DAG2（第二段）把定稿做成给普通观众扫读的视频屏幕稿（大众版）。
下面是用户从开始定标准到现在说过的全部原话（只收用户自己说的，按时间；夹杂着很多关于工具、并发、账号的话，那些不用管）。用户认为现在的标准维度不正交，例如“单独成立”和“接得上珠子、不翻译珠子”像是一个东西，“不啰嗦”写得太少；他要求从原话出发把标准全部重新修订。

请只依据用户原话（不要依据现行标准的写法），完成：
1. 逐条摘出所有关于“成品应该是什么样”的评判和要求（内容、语言、结构、和珠子的关系、视频呈现等），每条注明日期和原话片段。这些原话是一个开发过程的故事：用户是在看样片、看试验结果的过程中一步步想清楚的，前后会不一致。请连着上下文读（当时在看什么、刚发生了什么、这句话在回应什么），不要机械地“后说的覆盖先说的”：对前后不一致的地方，写出想法怎么演变的，再给出你的判断——按哪个版本更准确、为什么（例如后来的话只是针对某个样片的局部反应，还是真的改了方向）。
2. 把这些要求归成一组正交的维度：每个维度只回答一个问题，维度之间不重叠，合起来覆盖所有要求。对每个维度写：它回答的问题（一句话）、用户原话依据（日期 + 片段）、和其他维度的边界（容易混的地方怎么分）。分清哪些维度属于 DAG 的定稿、哪些属于 DAG2 的屏幕稿、哪些两边都适用（DAG2 要继承的不能丢）。
3. 对照下面的现行标准：哪些维度现行标准没有，哪些写重了（两条其实是一件事），哪些和用户原话冲突或写偏了，哪些写得太少（如“不啰嗦”）。
4. 每个维度怎么单独测（让它和别的维度分得开），一两句。
用中文，结论先行，不要客套。回答时请不要进行联网搜索。

【用户原话】
{QUOTES}

【现行 DAG 标准（标准.md）】
{STD1}

【现行 DAG2 标准修订草稿】
{STD2}
"""
q = (EVO/'标准_材料/用户原话_1017_1108.md').read_text(encoding='utf-8')
s2 = (PUB/'大众版标准_修订草稿_1108.md').read_text(encoding='utf-8'); s2 = s2[:s2.index('## 和现在门槛的差别')]
msg = ASK.replace('{QUOTES}', q).replace('{STD1}', (EVO/'标准.md').read_text(encoding='utf-8')).replace('{STD2}', s2)
print(len(msg), flush=True)
def one(a):
    name, model = a; ans = call(f'std_review2_{name}', msg, model, 'gpt3s', 'std-review')
    (Path(__file__).resolve().parent/f'std_review_{name}.md').write_text(ans or '', encoding='utf-8'); print(name, len(ans or ''), flush=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
