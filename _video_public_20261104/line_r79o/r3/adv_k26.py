"""11-10 I02（碎块形态 3 次交回用完后换方向）。K25a 是本轮最好：走样 0、覆盖高于 K11g、中等少一半、骨架 3.6+、过退步检查；
但盲比 human 4:0、core 4:0/3:0 输 K11g，短屏偏密，跨屏和大小块重复。两位顾问各自独立：判断问题出在哪一层（写稿、形态、原料、测法），
给一到两套大改方案（完整提示词），说没试过的办法。
python r3/adv_k26.py → r3/s24/adv_k26_{g6|g56}.json；提示词 r3/s24/prompt_K26_{g6|g56}_{1|2}.txt
"""
import json, sys, re, os, glob
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56, view_text
sys.stdout.reconfigure(encoding='utf-8')
STD = Path('D:/musicclaude/_video_public_20261104/大众版标准.md').read_text(encoding='utf-8')
CUR = (S/'prompt_K24r3_g6.txt').read_text(encoding='utf-8')


def reasons():
    out = []
    for f in sorted(glob.glob(str(S/'vs4_op6*_v4g68K25a_*.json'))):
        r = rd(Path(f)); seat = f[-6]; who = 'K25a' if seat == 'Y' else 'K11g'   # X 座位放 A=K11g
        out.append(f"- {Path(f).stem}（X={'K11g' if seat == 'X' else 'K25a'}，Y={'K25a' if seat == 'X' else 'K11g'}，选 {r['better']}）：{r['why']}")
    return '\n'.join(out)


ASK = """你是顾问。我们在做两首钢琴曲（船歌、幻想波兰舞曲）的大众版“边听边看”视频屏幕稿：上半屏文字，下半屏跟着音乐的音符动画；普通观众边听边扫。原料是线（一个人经历的一件事，分段）和珠子（听的人每段的感受：画面、身体感觉、比喻、心里话；有的只属于某几小节）。

这次请你做诊断和换方向，不是修补。碎块形态（每块一种字号；大块是骨架，小块是补充，旁注在动画旁）已经写了三轮、交回提出者三次，到了上限。

【用户的原话（按时间，最近的在后）】
- 11-08：“不能像截断；bullet 不是时序；珠子重体验、不重音乐描述。”“人是扫读抓关键词。”
- 11-09 晚：“扫的动的意思是：光看那些关键的东西，就可以给他把整个在表达什么在脑海里自己拼起来。”“很可能就是骨架来看他到底是不是独立读的通的。”
- 11-09 晚：“一句话里有大字是不是就不对劲啊……一句话里不应该有的字大有的字小，最多粗体、斜体、颜色。”“拆成碎块这个，我感觉我提了好多遍了。”
- 11-09 晚：“自身成立 + 串起来要能一起成立。”“23b 的人话呢，看起来倒退了。”
- 11-09 晚：“和整件事的核心连着，这个感觉现在确实强调的不太够。”“不啰嗦……逻辑上不应该要搞特别的复杂，能够尽量短的给他串起来就不要搞一堆转折弯弯绕绕的。”
- 11-09 晚：一颗珠子里的几种听法是几种理解，不能当重复砍。
- 目标：两首都做出剩余问题都很微小的一版。

【现行大众版标准（8 条，用户同意）】
{STD}

【现在的数字（两位评委 GPT-6、GPT-5.6）】
- K11g（旧格式：整句，句里放大几个词；当前主线）：绝对验收中等约 40 条/首；骨架测 3.0/3.5（0–4）；覆盖核心 0.83/0.82（船歌/幻想）。
- K25a（碎块，本轮最好，GPT-6 写）：中等 20/10（船歌两位评委）、12/5（幻想）；骨架 3.6/3.7；覆盖 0.84/0.85；走样 0；旧视频 w23 覆盖船歌 0.71–0.83、幻想 0.89–0.90。
- 盲比（K11g 对 K25a，两种座位，各项选更好的一边）：big、load 一直 K25a 赢；human 两首都 4:0 K11g 赢；core 船歌 4:0、幻想 3:0 K11g 赢；concise、fine 来回。
- 局部修补版（只改被点名的块）：问题数再减一半，但覆盖掉到 0.69–0.75，又新出走样——修补只会删，不会补出“串起来”。
- 我自己读 K25a：短屏偏密（幻想一屏 22 秒 135 字、每秒 6.2 字；船歌几屏每秒 5.3 字）；同一组身体感受跨屏重复；个别大块为塞进 14 字变拗口；每块都带“他”，读起来像一条条陈述排队。

【盲比评委的理由（原文）】
{REASONS}

【K25a 船歌（碎块；“大：”是大块，缩进的“小：”是挂在前一个大块后的小块，“旁注”在动画旁；括号里的秒是出现时刻）】
{K25A60}

【K25a 幻想】
{K25A61}

【K11g 船歌（整句，【】是放大的词）】
{K11G60}

【现在的写稿提示词（K25a 用的，占位符在跑的时候填原料）】
{CUR}

【已经试过、没用的】
- 事后改写改不动结构；禁词表无效；局部修补连续只删不补。
- 整句里放大几个词（K11g、K23b）：用户否（一句里字号混着，不知道要不要读；线大字、珠子小字分得泾渭分明不是预期）。
- 删得太狠（全曲一千多字）会把珠子的颗粒度压粗。
- 只按逗号机械切句像截断；一屏十几条像清单。

【请回答】
1. 诊断：human 和 core 输，主要出在哪一层——写稿（提示词）、形态（碎块的格式本身，例如每块 ≤14 字、不许逗号、每块单独成句）、原料（线和珠子本身打转或已经碎）、还是测法（评委偏爱整句）？给证据（引用上面的稿子或理由），别泛泛说。可以判几层都有，但要说主次。
2. 一到两套大改方案。每套是一个独立假设，优先只改一层；可以改格式规则（例如允许大块里有一个逗号、大块之间用连接词接、每屏先有一句贯穿的话再挂碎块等），但必须守住用户的硬要求：一块一种字号、块内强调只变色、只看大块能拼出整件事并串起来、不丢珠子的颗粒度、不写音乐术语和小节号。改了格式的，把新的机械检查规则写清楚（数字）。
3. 每套方案给完整的写稿提示词，占位符用 {{BUDGET}}、{{DAGSTD}}、{{FINAL}}、{{BEADS}}；输出格式保持：{"sections":[{"sec":"S01","big":[{"text":"…","accent":"…","emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["S01-1"],"at":0}],"small":[{"text":"…","after":0,"from":["S01-B2"],"bars":"","at":0}],"notes":[{"text":"…","from":["S01-B2"],"pt":"","bars":"…"}]}]}。提示词里不放任何具体作品的内容或例子（脚本会查，作品原句会被拦）。提示词是给这一首用的（“这首钢琴曲”），不要写“两首”。
4. 没试过、你认为值得试的办法（一两句一条）。

只输出 JSON：{"diag":"诊断，分层写主次和证据","layer":"写稿|形态|原料|测法（主因）","plans":[{"name":"短名","hypothesis":"这套假设什么、改哪一层","checks":"新的机械检查规则（没改就写沿用）","prompt":"完整提示词"}],"untried":["…"]}。回答时请不要进行联网搜索。
"""


def one(jm):
    j, m = jm; p = S/f'adv_k26_{j}.json'
    if p.exists(): r = rd(p)
    else:
        msg = (ASK.replace('{STD}', STD).replace('{REASONS}', reasons()).replace('{K25A60}', view_text('op60', 'g68K25a'))
               .replace('{K25A61}', view_text('op61', 'g68K25a')).replace('{K11G60}', view_text('op60', 'g68K11g')).replace('{CUR}', CUR))
        print('材料', j, len(msg), flush=True); r = None
        for k in range(3):
            try: r = parse(call(f'adv_k26_{j}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-adv')); assert r.get('plans') and r['plans'][0].get('prompt'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"== {j} 主因 {r.get('layer')}：{(r.get('diag') or '')[:1500]}", flush=True)
    for i, pl in enumerate(r.get('plans') or [], 1):
        tpl = pl['prompt'].replace('{{', '{').replace('}}', '}')
        try: prompt_lint.lint(re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|CURRENT)\}', '', tpl), f'adv_k26_{j}_{i}')
        except SystemExit as ex: print('泛化检查没过', j, i, ex, flush=True)
        (S/f'prompt_K26_{j}_{i}.txt').write_text(tpl, encoding='utf-8')
        print(f"-- {j} 方案 {i} {pl.get('name')}：{pl.get('hypothesis', '')[:500]}\n   检查：{pl.get('checks', '')[:500]}", flush=True)
    print(f"-- {j} 没试过：{r.get('untried')}", flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
