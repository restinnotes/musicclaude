"""11-10 I12 第 1 次交回（K27 六套 + 一套原料对照测完）。两位顾问各看全部结果，改自己的方案，各给两套。
python r3/adv_k27x.py → r3/s24/adv_k27x_{g6|g56}.json；提示词 r3/s24/prompt_K27x_{j}_{n}[_plan].txt
"""
import json, sys, re, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56, view_text
import adv_k27
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

ASK = """你是顾问。上一轮你和另一位顾问各给了三套方案（两步写稿、锁结构只改措辞、一步写稿），都已经两首同跑、测完。请看结果，改方案。背景、标准和输出格式和上次一样（附在最后）。

【结果（船歌/幻想；中等 = 绝对验收两位评委各自的中等问题数；核心 = 确认核心覆盖；必读 = 只看大块时必读内容拿到的比例；走样 = 两位同报；盲比对旧主线 K11g）】
| 版本 | 做法 | 中等（船歌两位 / 幻想两位） | 核心 | 必读 | 走样 | 盲比 |
|---|---|---|---|---|---|---|
| K25a（底稿） | 碎块旧稿 | 13、18 / 10、7 | 0.91/0.95 | 0.70/0.79 | 0 | 不退步；human 4:0 输 |
| K26c2（底稿） | 短块关系链旧稿 | 22、13 / 28、20 | 0.88/0.97 | 0.79/0.93 | 1 | 不退步；human 4:0 输 |
| K27q2 | Argon 在 K25a 上只改措辞（GPT-6 的提示词） | 12、10 / 3、12 | 0.94/0.97 | 0.72/0.85 | 0 | 船歌 1 位稳定选 K11g、幻想 1 位稳定选新稿；human 船歌 4:0 输、幻想 2:2；concise 2:2、1:2 |
| K27p2 | Argon 在 K26c2 上只改措辞（GPT-5.6 的提示词） | 9、17 / 4、20 | 0.83/1.00 | 0.87/0.96 | 1 | 船歌随座位、幻想 2 位稳定选 K11g；human 船歌 2:2、幻想 4:0 输；concise 两首 4:0 输（每块被写长：船歌小块合计 1414 字） |
| K27q1 | 两步：GPT-6 分配、GPT-5.6 落字 | 14、10 / 10、12 | 0.76/0.95 | 0.64/0.79 | 1 | 不稳定输赢；human 4:0 输；concise 胜；听众的感受被写成“他”的经历 |
| K27p1 | 两步：两步都 GPT-6 | 20、24（另 2 严重）/ 20、11 | 0.93/0.95 | 0.78/0.81 | 1 | 两首都 2 位稳定选 K11g（退步）；core、small、concise 输；第 7、8 条各 5–6 条（一屏小块 6–8 个，感受罗列） |
| K27p3 | 一步（GPT-5.6 的提示词） | 19、21 / 21、20 | 0.82/0.91 | 0.64/0.87 | 1 | 幻想 2 位稳定选 K11g |
| K27q3 | 一步（GPT-6 的提示词） | 26、25（各 1 严重）/ 16、14 | 0.91/0.92 | 0.65/0.67 | 2 | 船歌 2 位稳定选 K11g |
结论：没有一版接近“剩余问题都很微小”。只改措辞这一步是有用的（K27q2 是目前最好的一版，一位评委的幻想只剩 3 条中等），但会把块写长；两步写稿这一轮没有带来预期的好处；一步写稿最差。

【我逐条读了 K27q2 剩下的中等问题，分成两类】
一类是写稿造成的：同一屏大块说过、小块又换个说法说一遍；相邻两屏完整重说同一件事；一块里塞两层意思；指代不清（“他”“那”“从前的姿态”指谁指什么）；把一段有画面的心里话压成一句书面的概括；短屏里大块一条接一条出现得太密。
另一类出在原料（珠子）本身，写手只是照搬：
- 相邻两段的珠子里有几乎相同的要点（同一组感官罗列在前后两段各出现一次），照搬就成了跨屏重复。
- 珠子原文就是一串抽象名词并列，或一句泛泛的人生道理，或站在外面分析心理；照搬就被判“不具体”“不是人话”。
- 珠子原文讲的是音乐本身的样子（姿态、音响、像什么乐器），被放进了小块而不是旁注。
- 珠子原文是“也可以听成……”的一整段有来有往的心里话，压成十几个字就只剩一个看不懂的标签。
按现行标准第 6 条，这些内容屏幕上要拿得到；按第 4、5、7 条，照搬又会被扣。珠子内容本身不能改（硬约束），但怎么搬可以定：比如同一要点跨段重复时只在更合适的一段写；抽象并列的要点可以只取其中最具体的一两样；讲音乐样子的进旁注；长的心里话宁可占一个完整的小块也不压成标签。

【K27q2 评委点的中等问题（原文）】
{ISS}

【K27q2 幻想全文】
{Q2_61}

【请回答】
1. 你对上面结果的解读：两步写稿为什么没有带来好处？只改措辞为什么会写长？上面“原料造成的那一类”你同意吗、该怎么在写稿这一层处理（不改珠子原文）？
2. 两套改后的方案，互为独立假设。可用的流程、写手、底稿、机械检查和上次一样（底稿现在还可以选 K27q2、K27p2）；流程 C 里的两步用法：第一步输出原样填进第二步的 {{PLAN}}，第二步同时可以拿到 {{BASE}}。每套给完整提示词。要求和上次相同：最终输出格式不变；提示词里不放具体作品的内容或例子；写“这首钢琴曲”。字数上限如果要写手守，请直接写在提示词正文里（上次有的方案只写在机械检查里，写手第一遍全写超了）。
3. 如果你认为到了该换别的层面（原料、标准、测法）的时候，直说。

只输出 JSON：{"read":"解读","plans":[{"name":"短名","flow":"A|B|C","writer":"g6|g56|argon","plan_writer":"","base":"","hypothesis":"…","checks":{"big_max":30,"big_n":5,"small_max":30,"small_n":8,"big_rate":3,"notes_n":5},"plan_prompt":"","prompt":"…"}],"other_layer":"要不要换层面，换哪层、怎么换"}。回答时请不要进行联网搜索。

==== 上一次给你的背景、标准、流程说明和输出格式（原样）====
{PREV}
"""


def one(jm):
    j, model = jm; p = S/f'adv_k27x_{j}.json'
    if not p.exists():
        prev = (S/f'adv_k27_ask_{j}.txt').read_text(encoding='utf-8')
        a = prev.find('【K26c2 评委点的中等问题'); b = prev.find('【可以用的写稿流程')
        prev = prev[:a] + prev[b:]   # 上次的旧稿全文和问题清单不再附
        msg = (ASK.replace('{ISS}', adv_k27.issues('g68K27q2', 'op60', '船歌') + NL + adv_k27.issues('g68K27q2', 'op61', '幻想'))
               .replace('{Q2_61}', view_text('op61', 'g68K27q2')).replace('{{', '{').replace('}}', '}').replace('{PREV}', prev))
        (S/f'adv_k27x_ask_{j}.txt').write_text(msg, encoding='utf-8')
        if os.environ.get('DRY'): print(j, len(msg)); return
        for k in range(3):
            try:
                r = parse(call(f'pub24ADV27X_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'public24-adv27x')); assert r.get('plans'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p)
    print('====', j); print('解读：', r.get('read')); print('换层面：', r.get('other_layer'))
    for n, pl in enumerate(r['plans'], 1):
        for key, suf in (('prompt', ''), ('plan_prompt', '_plan')):
            if (pl.get(key) or '').strip():
                f = S/f'prompt_K27x_{j}_{n}{suf}.txt'; f.write_text(pl[key], encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|BASE|PLAN|STD)\}', '', pl[key]))
                print(f"  方案 {n}{suf} {pl.get('name')}｜{pl.get('flow')}｜写手 {pl.get('writer')}｜第一步 {pl.get('plan_writer')}｜底稿 {pl.get('base')}｜{pl.get('checks')}｜{len(pl[key])} 字｜泛化检查 {h or '过'}")
        print('    假设：', pl.get('hypothesis'))


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
