"""11-11 I12 交回（K28 一轮 + 体检 + 不给标准的开放评审 测完）。两位顾问各看全部结果，各给三套 DAG2 方案 + 一到两套改线（DAG）方案。
python r3/adv_k28.py → r3/s24/adv_k28_{g6|g56}.json；提示词 r3/s24/prompt_K29_{j}_{n}[_plan].txt、改线 r3/s24/prompt_L29_{j}_{n}.txt
"""
import json, sys, re, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint, blend
from pub24 import S, R2, rd, call, parse, G6, G56, view_text
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

ASK = """你是顾问。我们在做一首钢琴曲的大众版“边听边看”视频屏幕稿（两首曲子一起做，同一套提示词）。这一轮的全部结果、体检和不给标准的开放评审都附在下面，请看完后给下一轮的方案。你看到的是交给你的材料，没有全部历史；判断的最终取舍在我们这边，所以请把理由写清楚。

【现行大众版标准（内容部分，只有用户能改）】
{STD}

【体检报告（我们写的，含四版数字、开放评审、用户指出过的问题逐条、流程问题和我们自己的判断；你可以反驳）】
{REPORT}

【当前最好的一版 K28b 全文】
=== 船歌 ===
{K28B_60}
=== 幻想 ===
{K28B_61}

【K28b 用的写稿提示词（底稿 K28a；规则：大字只用线的原话，只在停顿处切开或删整个分句）】
{P28B}

【以往实验里已经证明的经验（请遵守，除非你有证据反驳）】
- 压缩改写会丢质感和人话；把连着的心理过程拆成几块会丢连贯；删掉大字里的小句会丢“为什么”；只删整句多余的、留下的字不动，才不坏。
- 事后整篇改写改不动内容结构（打转、同一个两难反复说），结构要在写线那一步修；局部修订加盲比理由回补能赢，整篇重写输。
- 固定禁词表无效。机械约束会直接塑造写法（“大字最多一个逗号”逼出了标签腔）。
- 线不编外加的事件、前史、对白、物件来推动故事，珠子的比喻不写成他真的发生的事；“没有外部动作”不算缺点。允许一个从头到尾不变的轻处境加小动作。
- 用户：“跳只是人话的一个判别标准”；大字小字按这一刻的重要性定，不按来源分；一颗珠子里不同的听法是不同的理解，不能砍成一种；泛泛的道理可以不写。

【可以用的写稿流程（DAG2）】
{FLOWS}

【改线（DAG）可以怎么做】
线的格式：每段几条，每条一句完整自然的话，有编号（如 S05-2），后面标它对应哪几颗珠子；线的编号和对应关系 DAG2 要用，最好保留。可以做的：在现有线上逐条改写、合并、删条、加条（加的条用新编号如 S05-4，并写明对应珠子）。改完以后同一份 DAG2 提示词两版原料各写一次，端到端比，好了才收。

【请回答】
1. 你对结果的解读：K28b 剩下的问题里，哪些是写稿造成的、哪些出在线、哪些出在珠子原料、哪些出在画面；体检报告里我们的判断（尤其“不靠编事件补”“大字保留线的说法、把重要的珠子体验织进大字”）你同不同意。
2. 三套 DAG2 方案，互为独立假设；每套给完整提示词（输出格式同上面的屏幕稿 JSON；提示词里不放具体作品的内容或例子；写“这首钢琴曲”；字数上限写在正文里）。可以用 {BASE}（底稿，可选 K28b、K28a、K27xde、K11g）、{PLAN}（两步写稿时第一步的输出）。
3. 一到两套改线方案：给完整提示词（输入占位符 {LINE} 是全部线带编号和对应珠子，{CENTER} 是全曲核心，{BEADS} 是珠子；输出 JSON {"sections":[{"sec":"S01","lines":[{"id":"S01-1","text":"…","beads":["S01-B1"]}]}]}，每段都要有，没改的照抄）。说明它治哪几条、怎么验证没有变坏。
4. 流程上你看到的漏洞（哪条规则让错的东西过了线、缺什么测法），直说。

只输出 JSON：{"read":"解读","plans":[{"name":"短名","flow":"A|B|C","writer":"g6|g56|argon","plan_writer":"","base":"","rule":"std8|std9","hypothesis":"…","checks":{"big_max":40,"big_n":5,"small_max":30,"small_n":6,"big_rate":3,"notes_n":5},"plan_prompt":"","prompt":"…"}],"line_plans":[{"name":"短名","writer":"g6|g56","hypothesis":"…","verify":"…","prompt":"…"}],"process":"流程漏洞"}。回答时请不要进行联网搜索。
"""

FLOWS = """A. 一步写稿：一份提示词，从原料直接写。占位符 {BUDGET}（每屏停留秒数）、{DAGSTD}（标准）、{FINAL}（线）、{BEADS}（珠子）。
B. 两步写稿：第一步提示词只分配内容（每屏放哪些、进大块还是小块还是旁注、哪些是重复不写），输出原样填进第二步的 {PLAN}；第二步照分配写成屏幕稿。两步可以指定不同的写手。
C. 在现有某一版上改：提示词里用 {BASE}（那一版的完整 JSON，和输出格式相同）。可以和 B 组合（第一步的输出填 {PLAN}，第二步同时拿到 {BASE}）。
写手可选：GPT-6、GPT-5.6、Argon（改语言和口气最自然，调用很宝贵，只适合用在落字这一步）。
机械检查（写完自动查，不过就交回写手重写，最多 3 次）：可设大块每块最多几字、每屏最多几个大块、小块每块最多几字、每屏最多几个小块、只算大块的每秒字数、每屏旁注条数。规则 std8 = 大块最多一个逗号；std9 = 大块最多两个逗号；两者都不用分号句号；小块最多两个逗号；旁注每条不超过 30 字；正文不写小节号；只来自珠子的大块不能用“他”写成他的经历。请尽量少设规则。"""


def one(jm):
    j, model = jm; p = S/f'adv_k28_{j}.json'
    if not p.exists():
        flows = FLOWS
        msg = (ASK.replace('{STD}', blend.DAGSTD).replace('{REPORT}', Path('D:/musicclaude/_dag2_video_20261104/体检报告_1111.md').read_text(encoding='utf-8'))
               .replace('{K28B_60}', view_text('op60', 'g68K28b')).replace('{K28B_61}', view_text('op61', 'g68K28b'))
               .replace('{P28B}', (S/'prompt_K28b.txt').read_text(encoding='utf-8')).replace('{FLOWS}', flows))
        (S/f'adv_k28_ask_{j}.txt').write_text(msg, encoding='utf-8')
        if os.environ.get('DRY'): print(j, len(msg)); return
        r = None
        for k in range(3):
            try:
                r = parse(call(f'pub24ADV28_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'public24-adv28')); assert r.get('plans'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p)
    print('====', j); print('解读：', r.get('read')); print('流程：', r.get('process'))
    for n, pl in enumerate(r['plans'], 1):
        for key, suf in (('prompt', ''), ('plan_prompt', '_plan')):
            if (pl.get(key) or '').strip():
                f = S/f'prompt_K29_{j}_{n}{suf}.txt'; f.write_text(pl[key], encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|BASE|PLAN|STD)\}', '', pl[key]))
                print(f"  方案 {n}{suf} {pl.get('name')}｜{pl.get('flow')}｜写手 {pl.get('writer')}｜第一步 {pl.get('plan_writer')}｜底稿 {pl.get('base')}｜{pl.get('rule')}｜{pl.get('checks')}｜{len(pl[key])} 字｜泛化检查 {h or '过'}")
        print('    假设：', pl.get('hypothesis'))
    for n, pl in enumerate(r.get('line_plans') or [], 1):
        f = S/f'prompt_L29_{j}_{n}.txt'; f.write_text(pl['prompt'], encoding='utf-8')
        h = prompt_lint.find(re.sub(r'\{(LINE|CENTER|BEADS)\}', '', pl['prompt']))
        print(f"  改线 {n} {pl.get('name')}｜写手 {pl.get('writer')}｜{len(pl['prompt'])} 字｜泛化检查 {h or '过'}"); print('    假设：', pl.get('hypothesis')); print('    验证：', pl.get('verify'))


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
