"""11-11 准则第八节：每轮复盘交两位顾问独立找流程漏洞（顾问提出的漏洞全部由我判断改不改，写进流程复盘）。
材料：迭代准则全文、流程复盘最近三条、要求清单里最近的用户原话、STATUS 顶部（当前节点和待修问题）。
python r3/procreview.py 轮次名     → r3/s24/procrev_{轮次}_{g6|g56}.txt
"""
import sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pub24 import S, call, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
D = Path('D:/musicclaude/_dag2_video_20261104')

ASK = """你是独立顾问，审查一个用大模型迭代内容的流程本身。我们在把两首钢琴曲做成给普通观众“边听边看”的视频屏幕稿：上游（DAG）产出一条“线”和听众的感受“珠子”，下游（DAG2）写成屏幕稿；用若干大模型评委测量，按一份《迭代准则》推进，目标是做出一版开放评审挑不出大问题的成品。
用户的期望是：只要严格照这份准则走，就能自己往前推进、不走偏；用户不必反复指出同样的问题。

【先后：效果第一，速度第二】目标是最后做出好的成品。任何提速建议都不能削弱“提效果”的机制；提速只能靠并行、合并重复的调用、去掉确实无效的步骤、更早查测法。
下面这些是用户定下的规矩，是提效果用的，不能为了提速削弱、减次数、加门槛或改成只对部分候选适用；你认为某条该改，只能写成“建议问用户”，并说清代价：
- 没过的方案一律交回提出它的顾问继续改，除非提出者判断这条路不可能修成功（11-12 用户：“我之前说要给他继续试 除非这种解法被认为是不可能修成功”）；要快就并行交回，不是少交回。
- 开放评审每个候选必跑，不许关，不许改成不开放的评委，只能按目的校准。
- 两首一起过线，不单首处理、不拼版本。
- 收敛 = 开放评审挑不出大问题、绝对验收只剩轻微；不能降低这个线。
- 评委怀疑有问题时校准评委，不另做检查单；待修问题写在 STATUS、由评委测。
- 大众版标准只有用户能改。

请只审流程，不审内容本身。回答：
0. 先看结果：这几轮最好的版本有没有变好（看试验记录）？没有的话，是哪一步的产出错了（诊断错、原因没验证就开批、方案只在同一类里换、测法有问题、根在设定或标准却没早点问用户），本该在哪一步更早发现？流程该怎么改才能让它下次自己发现、自己改？这是最重要的一问。
1. 照这份准则字面执行，哪些地方仍会让错的东西过线、或让该停的事继续做（指出条文，说清后果）？
2. 哪些步骤在实际执行中最容易被跳过或省掉？准则里缺什么能防止跳过的东西？
3. 缺哪些测量或校准，导致用户比评委先发现问题？
4. 怎么更快：哪些步骤可以并行、合并、去掉；怎样用更少的轮次走到收敛。每条提速建议都要写“对效果的影响：提高 / 不变 / 可能降低（为什么）”；可能降低效果的不要当提速建议提。
6. 这一轮所有失败的方案，共同没动过的东西是什么（设定、输入、哪一层、哪个评委）？逐条列出。
5. 准则里有没有自相矛盾、写得含糊、执行者可以随意解释的地方。
每条写：问题、依据（引准则或材料原文）、建议的改法（可以直接给替换文字）、它要改善复盘记分表里哪一个数字、预期怎么变、是否碰到上面用户定下的规矩（碰到就只能写“建议问用户”）。不要客套，不要泛泛而谈。

【迭代准则全文】
{RULES}

【流程复盘（最近几轮）】
{RETRO}

【用户最近的原话和要求（要求清单节选）】
{REQS}

【当前状态（STATUS 顶部：当前节点、待修问题）】
{STATUS}

【试验记录（最近几轮全文）】
{TRIALS}
"""


def run(tag):
    rules = Path('D:/musicclaude/_thread_evo_20261019/迭代准则.md').read_text(encoding='utf-8')
    retro = D.joinpath('流程复盘.md').read_text(encoding='utf-8'); retro = retro[retro.find('## 第 3 条'):] if '## 第 3 条' in retro else retro[-12000:]
    reqs = D.joinpath('要求清单.md').read_text(encoding='utf-8').split('## 原料')[0][-9000:]
    st = D.joinpath('STATUS.md').read_text(encoding='utf-8'); st = st[:st.find('## 在做什么')]
    trials = Path('D:/musicclaude/_thread_evo_20261019/试验记录.md').read_text(encoding='utf-8')[-80000:]   # 11-12 Fable 审查：不截尾，给足最近几轮
    msg = ASK.replace('{TRIALS}', trials).replace('{RULES}', rules).replace('{RETRO}', retro).replace('{REQS}', reqs).replace('{STATUS}', st)

    def one(jm):
        j, m = jm; p = S/f'procrev_{tag}_{j}.txt'
        if not p.exists(): p.write_text(call(f'procrev_{tag}_{j}', msg, m, 'gpt3s', 'process-review') or '', encoding='utf-8')
        print(j, '完成', len(p.read_text(encoding='utf-8')), flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))


if __name__ == '__main__':
    run(sys.argv[1])
