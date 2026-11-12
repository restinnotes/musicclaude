"""11-09 晚 I12：K22 四套方案写出的稿子在 I04a（我读第一屏）就不对，把结果交回各自的提出者：
这条路本来不行（写明为什么），还是方向对、某处没做好（给改过的提示词）。同一方案最多 3 次，这是第 1 次。
我给顾问的材料漏了版面容量（旁注区只有一行、主文字区舒服的字号下一屏约 120–180 字），这次补上。
python r3/adv_k22r.py   → r3/s24/adv_k22r_{g6|g56}.json；改过的提示词 r3/s24/prompt_K22r_{g6|g56}_{方案}_{用途}.txt
"""
import json, sys, re, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10); D = Path('D:/musicclaude/_dag2_video_20261104/读稿')

PLAN = {'g56': [('P1', 'g68K22a', None), ('P2', 'g68K22b', 'r2k22b')], 'g6': [('P1', 'g68K22c', 'r2k22c'), ('P2', 'g68K22d', None)]}

ASK = """你上一轮当顾问，给两首钢琴曲的大众版屏幕稿出了两套大改方案（下面附你的原回答）。写手（GPT-6）照你的提示词把两首都写了。我在“一屏样片”这一步先自己读，还没跑任何测量，就发现不对。请你判断每套方案：这条路本来不行（写明为什么），还是方向对、某处没做好（给改过的完整提示词）。

【我上一轮漏给你的版面容量（这是我的疏漏）】
- 主文字区约 1370×650 像素。大字 46 号时一行约 29 字，小字 26 号一行约 52 字。字多了渲染器会自动整体缩小字号；在舒服的字号下，一屏大约放得下 120–180 字（大字小字合计，不含旁注）。停留短的屏更少。
- 旁注区只有一行宽：26 号字，从播放点右侧到屏幕右边，约 30 字，不换行；同一时刻最多叠两三条。超过 30 字的旁注会被截掉或冲出屏幕。
- 大众版标准第 7 条：讲观众此刻的体验，音乐本身只在帮人对上声音时才提；正文（包括旁注）不写小节号——到时出现已经由 bars 字段管，文字里不用再写“第几小节”。

【四套稿子的共同问题（四套都有，两位顾问的方案都写出来了）】
1. 旁注被当成“放下整颗珠子的地方”：一条 60–200 字，把珠子原文差不多整颗搬进去，里面还写着“第几小节”和调性、声部、左手波浪这类音乐描述。
2. 全曲变长：船歌 3800–4700 字、幻想 4100–4400 字（现在的 K11g 约 3100 字，旧视频约 2600 字）。最密的屏每秒 9–13 字。
3. 小字仍多是带分号、两三层意思的长句（40–60 字一块），没有变成一眼抓得到的东西；大字也仍是一屏两三条整句。
4. 写手一被要求“珠子内容不丢”，就逐颗原样搬运；这和以前试过的“写手自己补覆盖就逐颗扩写、写到两倍长”是同一个现象。

【你的方案各自的稿子】
{RESULTS}

【你上一轮的原回答】
{ORIG}

请对每套方案回答，并给出改过的完整提示词（占位符和输出格式同上一轮；改线的方案连同改线、对应的提示词一起给，不需要改的就原样给）。要求：
- 提示词里不放任何具体作品的内容或例子。
- 篇幅要能在上面的容量里放下，同时不能靠删掉“为什么”和具体的画面、身体感觉、比喻来变短——以前单纯删短总是丢“为什么”、变笼统。说清楚你的提示词用什么办法同时做到。
- “珠子不丢”指珠子里最核心、最有辨识度的那一个画面、身体感觉、比喻或心里话要在屏幕上找得到，不是每句话都搬上屏。
只输出 JSON：{"plans":[{"id":"P1","verdict":"不行|方向对","why":"…","fix":"改了什么、为什么这样能放进容量又不丢为什么和细腻","prompt_screen":"…","prompt_line":"…","prompt_map":"…"},{"id":"P2",…}]}。回答时请不要进行联网搜索。
"""


def sample(tag, src):
    out = [f"=== 稿子 {tag}（原料 {src or 'r2c 原线'}）==="]
    for w, secs in (('op60', ('S05', 'S06')), ('op61', ('S03',))):
        t = (D/f'{tag}_{w}.md').read_text(encoding='utf-8'); out.append(t.splitlines()[0])
        for s in secs:
            m = re.search(rf'^## {s}（.*?(?=^## |\Z)', t, re.S | re.M); out.append(m.group(0).strip() if m else '')
    if src:
        t = (D/f'线_{src}_op60.md').read_text(encoding='utf-8')
        out.append('改过的船歌线（前五段）：' + NL + NL.join(t.splitlines()[1:28]))
    return NL.join(out)


NOTE = {'g68K22c': '我读改过的线：情节骨架和原线几乎一样，主要是每条写长、写成解释（“他此前担心……但眼下并没有出现他害怕的疏远”），船歌线从 1529 字变成 2276 字；原线里来回说“对方没退开”的几段仍然都在。对应那一步把后面几段的珠子挂到了前面的线上（例如第 2 段的线挂了第 4、第 7 段的珠子），屏幕稿会把后面的感受提前。',
        'g68K22b': '我读改过的线：一条一个意思、句子短，这点好；但情节骨架和原线一样，原线里来回说“对方没退开”的几段都还在（第 2、6、8、9 段）。稿子里有一处把听的人的感受写成了他的经历（小字写“他从……跌回自己心里”，原珠子是听者的比喻）。'}


def one(jm):
    j, m = jm; p = S/f'adv_k22r_{j}.json'
    if p.exists(): r = rd(p)
    else:
        res = NL.join(sample(tag, src) + NL + NOTE.get(tag, '') for _, tag, src in PLAN[j] if (D/f'{tag}_op60.md').exists())
        orig = json.dumps(rd(S/f'adv_k22_{j}.json'), ensure_ascii=False)
        msg = ASK.replace('{RESULTS}', res).replace('{ORIG}', orig)
        print('材料', j, len(msg), flush=True); r = None
        for k in range(3):
            try: r = parse(call(f'adv_k22r_{j}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-adv')); assert r.get('plans'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    for pl in r.get('plans') or []:
        print(f"== {j} {pl.get('id')}：{pl.get('verdict')}；{(pl.get('why') or '')[:300]}{NL}   改法：{(pl.get('fix') or '')[:500]}", flush=True)
        for kind in ('screen', 'line', 'map'):
            tpl = (pl.get('prompt_' + kind) or '').replace('{{', '{').replace('}}', '}')
            if len(tpl) < 50: continue
            bare = re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|CURRENT|CENTER|LINE|SEGS)\}', '', tpl)
            try: prompt_lint.lint(bare, f'adv_k22r_{j}_{pl.get("id")}_{kind}')
            except SystemExit as ex: print('泛化检查没过', j, pl.get('id'), kind, ex, flush=True)
            (S/f"prompt_K22r_{j}_{pl.get('id')}_{kind}.txt").write_text(tpl, encoding='utf-8')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
