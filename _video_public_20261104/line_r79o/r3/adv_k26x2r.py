"""11-10 交回 GPT-6：第 2 次交回给的方案把大块放宽到 42 字、两个逗号，和 K11g 的整句一样长，和用户硬要求“拆成碎块”冲突。请它守住碎块重出（不计入交回次数，同 11-10 早上对 GPT-5.6 的处理）。"""
import json, sys, re, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6
sys.stdout.reconfigure(encoding='utf-8')
prev = (S/'adv_k26x2_g6.json').read_text(encoding='utf-8')
MSG = """你这次的诊断我们接受（措辞被压坏、旁注要算进负担、去重要单独查）。但大块放宽到 42 字、两个逗号，已经和旧主线 K11g 的整句一样长（K11g 一句约 30–40 字），等于回到整句，和用户的硬要求冲突：用户多次要求“拆成碎块”，并否过“你这现在看上去也完全没有去给他把连贯的句子给拆成碎块”“我也仍然认为你这种连贯读根本不是什么扫的动”。
请在守住碎块的前提下改：大块不超过 30 字、最多一个逗号；小块不超过 30 字。措辞问题不靠加长解决，靠每块说完整的口语说法、去掉同义重复来腾出字数。其余（旁注算进负担、去重、保真、覆盖）照你的方案。
要求同上一轮：占位符 {{BUDGET}}、{{DAGSTD}}、{{FINAL}}、{{BEADS}}；输出格式不变；提示词里不放任何具体作品的内容或例子；写“这首钢琴曲”；机械检查写清所有数字。
只输出 JSON：{"changes":"…","checks":"…","prompt":"完整提示词"}。回答时请不要进行联网搜索。

【你这次的回答】
""" + prev
p = S/'adv_k26x2r_g6.json'
if not p.exists():
    r = None
    for k in range(3):
        try: r = parse(call('adv_k26x2r_g6' + ('' if not k else f'_r{k}'), MSG, G6, 'gpt3s', 'public24-adv')); assert r.get('prompt'); break
        except Exception as ex: print('不合格', repr(ex)[:150], flush=True); r = None
    if r: p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
r = rd(p); tpl = r['prompt'].replace('{{', '{').replace('}}', '}').replace('\\"', '"').replace('S01-L1', 'S01-1')
(S/'prompt_K26x2_g6.txt').write_text(tpl, encoding='utf-8')
try: prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS)\}', '', tpl), 'prompt_K26x2_g6'); print('泛化检查过')
except SystemExit as ex: print('泛化检查没过', ex)
print('==', r.get('changes', '')[:1200], '\n检查：', r.get('checks'), flush=True)
