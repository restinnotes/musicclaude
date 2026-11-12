"""11-10 午 I02（K25、K26 两轮在“内容全”和“扫得动”之间来回，到了 3 小时绊线后换方向）。
之后三件事变了：标准第 8 条只算大块；覆盖分层重做（units2.py，确认核心 64/73 个）；盲比第五版已校准。
按新口径，K25a、K26c2 的核心覆盖已够，第 8 条的问题几乎没有，剩下的是第 4（不啰嗦）、5（人话）、7（细腻）条。
两位顾问各自独立：诊断 + 三套方案（可以是一步写稿、两步写稿、或在某一版上只改措辞）。
python r3/adv_k27.py → r3/s24/adv_k27_{g6|g56}.json；提示词 r3/s24/prompt_K27_{j}_{n}[_plan].txt
"""
import json, sys, re, os, glob
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint, blend
from pub24 import S, rd, call, parse, G6, G56, view_text
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)
STD = Path('D:/musicclaude/_video_public_20261104/大众版标准.md').read_text(encoding='utf-8').split('## 画面')[0]


def issues(tag, w, nm):
    out = []
    for j in ('g6', 'g56'):
        p = S/f'openA4_{w}_{j}_{tag}_s8.json'
        if not p.exists(): continue
        r = rd(p)
        for s in r.get('screens') or []:
            for x in s.get('issues') or []:
                if x.get('severity') in ('中等', '严重'): out.append(f"- {nm} {s.get('sec')}（标准 {x.get('std')}）「{(x.get('quote') or '')[:60]}」：{(x.get('why') or '')[:120]}")
        for x in r.get('whole') or []:
            if x.get('severity') in ('中等', '严重'): out.append(f"- {nm} 全曲（标准 {x.get('std')}）：{(x.get('why') or '')[:160]}")
    return NL.join(out)


def human(tag):
    out = []
    for f in sorted(glob.glob(str(S/f'vs5_op6*_v5{tag}_*.json'))) + sorted(glob.glob(str(S/f'vs5_op6*_v5b{tag}_*.json'))):
        w = rd(Path(f)).get('why') or ''
        i = w.find('human')
        if i >= 0: out.append('- ' + w[i:i + 240].replace(NL, ' '))
    return NL.join(out[:8]) or '（无）'


ASK = """你是顾问。我们在做两首钢琴曲（船歌、幻想波兰舞曲）的大众版“边听边看”视频屏幕稿：上半屏文字，下半屏跟着音乐的音符动画；普通观众边听边扫。原料是线（一个人经历的一件事，分段）和珠子（听的人每段的感受：画面、身体感觉、比喻、心里话；有的只属于某几小节）。

屏幕的形态已定（用户的硬要求，不要改回整句）：字分成块，一块只有一种字号；大块是必看的（只看大块就要明白这一屏最主要的东西，并且一屏屏串得起来），小块是补充（挂在某个大块后面），对着具体声音的细节放动画旁边的旁注（到那几小节才出现）。块内强调只变色。

这次请你做诊断和出方案。上一轮（两套形态各交回提出者两次）停在“内容全”和“看得过来”两头挪；之后三件事变了：
1. 标准第 8 条改了（用户提议）：“看得过来”只要求大块；小块和旁注不要求在停留时间里读完，但要在视觉上退后、不挤掉大块，每个小块仍然短、一块一个意思。
2. 覆盖的分层重做了：以前几乎所有意思单元都算核心（船歌 225 个里 149 个），现在两位评审独立分层、都判核心才算确认核心（船歌 64 个、幻想 73 个）。
3. 盲比的 human（人话）一项校准过，不再因为“不是整句”扣分；在这之后碎块稿的人话仍然输给旧的整句稿，评委点的都是具体措辞。

【现行大众版标准（内容部分，用户同意的现行版）】
{STD}

【按新口径的数字（船歌/幻想；两位评委 GPT-6、GPT-5.6）】
| 版本 | 形态 | 确认核心覆盖 | 重要层覆盖 | 绝对验收中等（船歌两位、幻想两位） | 中等集中在哪几条 | 只算大块最密的屏（字/秒） |
|---|---|---|---|---|---|---|
| K11g（旧主线，整句里放大词，形态已被用户否） | 整句 | 0.94/0.97 | 0.67/0.76 | 12、19 / 37、45 | 第 7、8、4 条 | 6.6/4.5 |
| K25a | 碎块：大块 ≤14 字不许逗号，小块 ≤18 字 | 0.91/0.95 | 0.77/0.73 | 13、18 / 10、7 | 第 4、5、7 条 | 1.8/2.7 |
| K26c2 | 短块关系链：每块 ≤30 字，大块 ≤6、小块 ≤10 | 0.88/0.97 | 0.83/0.77 | 22、13（另 1 严重）/ 28、20 | 第 4、5 条，少量第 1、2、7 条 | 2.5/2.4 |
| K26a3 | 自然句块：大块 ≤3、≤30 字一个逗号，小块 ≤5 | 0.77/0.78 | 0.61/0.68 | 13、17 / 4、13 | 第 4、5 条 | 1.8/2.3 |
走样（意思变了）：K25a 0 处，K26a3 0 处，K26c2 船歌结尾 1 处。盲比对 K11g：三版都不退步或胜，分项里 human 都输（K26a3 3:0、3:1，其余 4:0）。
目标是两首都做到“剩余问题都很微小”：中等问题接近 0。现在离得还远，剩下的主要是第 4 条（大块小块说同一件事、跨屏重复没有新东西）、第 5 条（为了短把话压坏：删掉口语必需的成分、名词堆叠、搭配生硬、书面词、站在外面下判断）、第 7 条（画面被压成笼统词）。

【上一轮为什么没用（我的判断，你可以反驳）】
- 一份提示词里二十来条硬规则（密度、块数、旁注量、去重、保真、登记去向、口语完整……），写手同时守不住；规则越加越多的那版（第 2 次交回）写了 4 遍还剩几十处超限。
- 措辞被压坏和形态无关，是写手为凑字数删字；在同一份提示词里既要短又要说完整，效果有限。
- 局部修补（只改被点名的块）只会删，覆盖掉、还新出走样。

【K26c2 评委点的中等问题（新标准下）】
{ISS_C2}

【K25a 评委点的中等问题（新标准下）】
{ISS_A}

【盲比 human 一项的理由（K26c2、K25a 对 K11g）】
{HUMAN}

【K26c2 船歌全文（“话”是大块，“感受”是小块，“旁注”在动画旁；【】只是变色）】
{C2_60}

【K25a 幻想全文】
{A_61}

【K11g 船歌的几屏（整句旧稿；它的人话评委更喜欢，供对比措辞）】
{K11G}

【可以用的写稿流程（脚本都已支持，三选一或组合）】
A. 一步写稿：一份提示词，从原料直接写。占位符 {{BUDGET}}（每屏停留秒数）、{{DAGSTD}}、{{FINAL}}（线）、{{BEADS}}（珠子）、{{STD}}（上面的标准全文）。
B. 两步写稿：第一步提示词（plan）只分配内容——每屏放哪些、进大块还是小块还是旁注、哪些是重复不写——输出格式由你定（会原样填进第二步的 {{PLAN}}）；第二步提示词照分配写成屏幕稿，只管把每块写成人平常会说的话。两步可以指定不同的写手。
C. 在现有某一版上改：提示词里用 {{BASE}}（那一版的完整 JSON，和输出格式相同），指定底稿是 K25a、K26c2 或 K26a3。可以只改措辞（块的数量、位置、来源不动），也可以只去重，或者先去重再改措辞（当两步用：第一步输出填进第二步的 {{PLAN}}）。
写手可选：GPT-6、GPT-5.6、Argon（Gemini 系的模型，我们以往的经验是它改语言、口气最自然；每次调用宝贵，只适合用在“只改措辞”这一步）。

【机械检查（写完自动查，不过就把清单交回写手重写，最多 3 次；数字由你定）】
可设：大块每块最多几字、每屏最多几个大块、小块每块最多几字、每屏最多几个小块、大块每秒最多几字（只算大块）、每屏旁注最多几条。固定的：大块最多一个逗号、不用分号句号；小块最多两个逗号、不用分号；旁注每条 ≤30 字；正文不写小节号；只来自珠子的大块不能用“他”写成他的经历。请尽量少设规则：上一轮规则多到写手守不住。

【已经试过、没用的】
- 整句里放大几个词（用户否）；每屏只有一句贯穿的话（大块太少，故事挤进小块，覆盖 0.63）；按逗号机械切句；一屏十几条像清单。
- 事后整体改写改不动结构；禁词表无效；局部修补只删不补。
- 把总量压到每秒 3–4 字（连小块旁注一起算）：覆盖掉到 0.7。现在标准已经不这样要求。

【请回答】
1. 诊断：按新口径，离“剩余问题都很微小”主要差在哪一层——写稿提示词、流程（一步还是两步）、写手、形态参数、原料（线本身绕或打转、珠子本身重复）、还是测法？给证据（引用上面的稿子或问题），说主次。原料如果有问题，指出是哪类（不用给改线的提示词，那一层另外做）。
2. 三套方案，每套一个独立假设，说明用 A、B、C 哪种流程、谁写、底稿（如果用 C）、机械检查的数字。至少一套用到“单独一步只改措辞”。
3. 每套给完整的提示词（两步的给两份）。最终输出屏幕稿的那份，输出格式必须是：{"sections":[{"sec":"S01","big":[{"text":"…","accent":"块内要变色的字，可空","emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["S01-1"],"at":0}],"small":[{"text":"…","after":0,"from":["S01-B2"],"bars":"","at":0}],"notes":[{"text":"…","from":["S01-B2"],"pt":"","bars":"…"}]}]}（after 是它挂在第几个大块后面，从 0 数；at 是这一屏第几秒出现，可为 0；from 写原料编号）。提示词里不放任何具体作品的内容或例子（脚本会查，作品原句会被拦）；提示词是给一首曲子用的（写“这首钢琴曲”，不要写“两首”）。
4. 没试过、你认为值得试的办法（一两句一条）。

只输出 JSON：{"diag":"诊断，分层写主次和证据","layer":"主因在哪一层","plans":[{"name":"短名","flow":"A|B|C","writer":"最终写手 g6|g56|argon","plan_writer":"第一步写手（没有就空）","base":"底稿 K25a|K26c2|K26a3（没有就空）","hypothesis":"这套假设什么","checks":{"big_max":30,"big_n":5,"small_max":30,"small_n":8,"big_rate":3,"notes_n":5},"plan_prompt":"第一步提示词（没有就空）","prompt":"最终提示词"}],"untried":["…"]}。回答时请不要进行联网搜索。
"""


def k11g_part():
    t = view_text('op60', 'g68K11g'); parts = t.split('\n### ')
    return '### ' + '\n### '.join(parts[1:4])


def one(jm):
    j, model = jm; p = S/f'adv_k27_{j}.json'
    if not p.exists():
        msg = (ASK.replace('{STD}', STD).replace('{ISS_C2}', issues('g68K26c2', 'op60', '船歌') + NL + issues('g68K26c2', 'op61', '幻想'))
               .replace('{ISS_A}', issues('g68K25a', 'op60', '船歌') + NL + issues('g68K25a', 'op61', '幻想'))
               .replace('{HUMAN}', human('g68K26c2') + NL + human('g68K25a'))
               .replace('{C2_60}', view_text('op60', 'g68K26c2')).replace('{A_61}', view_text('op61', 'g68K25a')).replace('{K11G}', k11g_part())
               .replace('{{', '{').replace('}}', '}'))
        (S/f'adv_k27_ask_{j}.txt').write_text(msg, encoding='utf-8')
        if os.environ.get('DRY'): print(j, len(msg)); return
        for k in range(3):
            try:
                r = parse(call(f'pub24ADV27_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'public24-adv27')); assert r.get('plans'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p)
    print('====', j, '主因：', r.get('layer')); print(r.get('diag')); print('没试过：', r.get('untried'))
    for n, pl in enumerate(r['plans'], 1):
        for key, suf in (('prompt', ''), ('plan_prompt', '_plan')):
            if (pl.get(key) or '').strip():
                f = S/f'prompt_K27_{j}_{n}{suf}.txt'; f.write_text(pl[key], encoding='utf-8')
                try: prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|BASE|PLAN|STD)\}', '', pl[key]), f.name); ok = '过泛化检查'
                except Exception as ex: ok = '泛化检查没过：' + repr(ex)[:200]
                print(f"  方案 {n}{suf} {pl.get('name')}｜{pl.get('flow')}｜写手 {pl.get('writer')}｜第一步 {pl.get('plan_writer')}｜底稿 {pl.get('base')}｜{pl.get('checks')}｜{len(pl[key])} 字｜{ok}")
        print('    假设：', pl.get('hypothesis'))


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
