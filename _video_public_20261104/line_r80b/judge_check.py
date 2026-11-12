"""11-07 评委矫正机制（用户：“你认为他目前评委有问题的时候 可以再给一个新的agent问问他 是不是这个提示词问题 然后怎么修 这样就可以印证你的”）。
怀疑某个评委有问题时，把评委提示词、它的输出样本、看到的症状交给两位顾问（GPT-6、GPT-5.6），各自独立回答：
  A 轮（不给我的结论）：是不是评委的问题？根因是什么？怎么改提示词？还是评委其实对、是我的预期错了？
  B 轮（给出我的诊断和改法）：我的改法对不对、漏了什么、会不会带来新的偏差？
两位顾问的 A 轮都独立指向同一根因，才算印证；有分歧就照他们的意见再改，或者报给用户。
python judge_check.py CASE      CASE 是 judge_check/CASE.md（节标题：==== 背景 ====、==== 评委提示词 ====、==== 症状和证据 ====、==== 我的诊断和改法 ====）
结果：judge_check/CASE_{A|B}_{g6|g56}.txt
"""
import re, sys, zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'line_r79o'))
from pub2 import G6, G56, call

D = Path(__file__).resolve().parent/'judge_check'

A = """我们用大模型当评委，给一首钢琴曲“边听边看”视频的屏幕稿打分。现在怀疑下面这个评委量得不准，请你当独立顾问来查。

请回答：
1. 这是评委提示词的问题，还是评委其实量对了、是我们的预期错了？两种可能都认真考虑，给出你的判断和理由。
2. 如果是提示词的问题，根因是什么（具体到提示词里哪一句、哪种设计）。
3. 怎么改：给出改后的提示词关键段落（可以直接写出替换文字），以及怎么验证改对了（比如同一版测两次看是否接近、和哪个已知结论对照）。
4. 改了以后可能带来什么新偏差，要防什么。

【背景】
{BG}

【评委提示词】
{PROMPT}

【症状和证据】
{EVIDENCE}
"""

B = """接着上面的问题。下面是我们自己的诊断和已经做的改法，以及改后的测量结果。请对照你上一轮的判断：
1. 我们的诊断和你的一致吗？哪里不同？
2. 我们的改法有没有漏掉什么、改过头、或者引入新的偏差？
3. 你建议再怎么改（给具体文字），或者可以就这样用？

【你上一轮的回答】
{MINE}

【我们的诊断和改法】
{FIX}
"""


def sec(t, name):
    # 节标题用独占一行的 ==== 名称 ====，避免材料里自带的【】小标题被误当成分节（11-07 第一次就因此截断了改法）
    m = re.search(r'^==== ' + name + r' ====\n(.*?)(?=^==== [^=\n]+ ====\n|\Z)', t, re.S | re.M); return m.group(1).strip() if m else ''


def run(case):
    t = (D/f'{case}.md').read_text(encoding='utf-8')
    msgA = A.replace('{BG}', sec(t, '背景')).replace('{PROMPT}', sec(t, '评委提示词')).replace('{EVIDENCE}', sec(t, '症状和证据'))
    def one(nm):
        name, model = nm; pa = D/f'{case}_A_{name}.txt'
        if not pa.exists(): pa.write_text(call(f'jc_{case}_A_{name}_{zlib.crc32(msgA.encode()):08x}', msgA, model, 'gpt3s', 'judge-check') or '', encoding='utf-8')
        pb = D/f'{case}_B_{name}.txt'
        if not pb.exists() and sec(t, '我的诊断和改法'):
            msgB = msgA + '\n\n' + B.replace('{MINE}', pa.read_text(encoding='utf-8')).replace('{FIX}', sec(t, '我的诊断和改法'))
            pb.write_text(call(f'jc_{case}_B_{name}_{zlib.crc32(msgB.encode()):08x}', msgB, model, 'gpt3s', 'judge-check') or '', encoding='utf-8')
        print(case, name, '完成', flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for c in sys.argv[1:]: run(c)
