"""11-10 I12 式交回（不计入碎块的 3 次）：GPT-5.6 的 K26 方案每屏 1–2 个大块、每块最多 72 字，是成段连贯读，和用户硬要求“拆成碎块”冲突（11-09 晚：“我也仍然认为你这种连贯读根本不是什么扫的动”）。请它守住碎块重出方案。"""
import json, sys, re, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G56
sys.stdout.reconfigure(encoding='utf-8')
prev = (S/'adv_k26_g56.json').read_text(encoding='utf-8')
MSG = """你上一轮的诊断我们接受（主因是形态：14 字、禁逗号切断了句子内部和块之间的关系）。但你的方案（每屏 1–2 个大块、每块最多 72 字、一两个完整句子）和用户的硬要求冲突：用户 11-09 晚多次说要“拆成碎块”，并且明确否过成段的连贯读——“我也仍然认为你这种连贯读根本不是什么扫的动”“扫的动的意思是：光看那些关键的东西，就可以给他把整个在表达什么在脑海里自己拼起来”。
另一位顾问已经出了两套：A 自然句块（大块每屏 1–3 块、每块 ≤28 字、最多一个逗号）；B 一屏一句（每屏 1 个贯穿句 ≤36 字 + 小块）。这两套都在跑。
请你在守住碎块（一屏多块、单块一眼看完，不超过约 30 字；一块一种字号；块内强调只变色）的前提下，给一套和 A、B 不同的独立假设，并给完整写稿提示词。比如你诊断里说的“块与块之间缺连接、主语反复重来、关系被压成结论”，可以从块和块怎么接（承接词、省主语、顺序）入手，而不是靠加长单块。
要求同上一轮：占位符 {{BUDGET}}、{{DAGSTD}}、{{FINAL}}、{{BEADS}}；输出格式不变；提示词里不放任何具体作品的内容或例子；写“这首钢琴曲”。机械检查规则写清楚（数字）。
只输出 JSON：{"name":"短名","hypothesis":"…","checks":"…","prompt":"完整提示词"}。回答时请不要进行联网搜索。

【你上一轮的回答】
""" + prev
p = S/'adv_k26r_g56.json'
if not p.exists():
    for k in range(3):
        try: r = parse(call('adv_k26r_g56' + ('' if not k else f'_r{k}'), MSG, G56, 'gpt3s', 'public24-adv')); assert r.get('prompt'); break
        except Exception as ex: print('不合格', repr(ex)[:150], flush=True); r = None
    if r: p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
r = rd(p); tpl = r['prompt'].replace('{{', '{').replace('}}', '}').replace('\\"', '"').replace('S01-L1', 'S01-1')
(S/'prompt_K26_g56_2.txt').write_text(tpl, encoding='utf-8')
try: prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS)\}', '', tpl), 'prompt_K26_g56_2'); print('泛化检查过')
except SystemExit as ex: print('泛化检查没过', ex)
print('==', r.get('name'), r.get('hypothesis'), '\n检查：', r.get('checks'), flush=True)
