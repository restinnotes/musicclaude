"""11-09 晚 截图评委第二版（评委矫正机制 judge_check/scancal：GPT-6、GPT-5.6 独立指向同一根因——
3 分定义太松成了默认安全分；2/3 分界应是“核心处境和感受要不要拼接、逐句读才懂”；让评委写完整理解会诱导它事后拼接；
三张图一起看会让后面的字帮前面加分）。第一版 K11g、K18cM、w23S、极易扫 SP、整段 SL 全在 2.6–3.2，分不开。
改法：
  1. 扫读：每张截图单独一次调用（只测开屏约 3 秒、结束前 1 秒两个时刻）；先写视觉入口和第一眼真正抓到的，抓不到写“不确定”；
     新的 0–4 锚点；评语说核心要拼接或逐句读的，扫读最高 2。
  2. 串起来：另一次调用，看三张图，判文字本身有没有把关系给清楚，不是读者能不能自己拼起来。
  3. 不机械按字数、条数扣分（两位都提醒防止变成偏好碎片）。
python r3/scanjudge2.py judge TAG [轮次]    结果 _video_public_20261104/r3/s24/scanB_{作品}_{评委}_{TAG}_{轮次}_{段}.json
python r3/scanjudge2.py sum TAG [轮次...]
环境变量 SJ_SECS=S03,S05 只测这几屏；SJ_THREADS 线程数（默认 8）。
"""
import json, os, sys, zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
os.environ.setdefault('FILM_DATA', 'line_r79o')
import prompt_lint
from pub24 import S, rd, wr, parse, G6, G56, WORKS
import pub16
sys.path.insert(0, str(Path(__file__).resolve().parent))
import scanjudge as v1
sys.stdout.reconfigure(encoding='utf-8')

SCAN = """你是第一次看这个视频的普通观众：正在听一首钢琴曲，偶尔抬眼扫一下屏幕。屏幕上半是文字，下半是跟着音乐滚动的音符动画，右上角一列小字是全曲的阶段目录。
附件是这一屏{WHEN}的一张真实截图。只评这一张。

【只评一件事：扫读】在一次约 3 秒的快速扫视里，不逐句读、不回看，能不能抓到这一屏的核心：这个人此刻怎么了（处境），什么感受，两者有什么关系。
模型能读懂整张图，不等于普通观众扫一眼能抓到。不要把读完全图后的理解当成第一眼的扫读。

【做法】
1. 先写视觉入口：眼睛第一下落在哪一块（按字号、亮度、位置）。
2. 只把视觉上足够突出、扫一眼就能直接拿到的内容算作“第一眼抓到”。图上有、但要细读或在几块之间来回找才懂的，不算。
3. 写第一眼抓到的处境（一句话）和感受（几个词）。只凭第一眼判断不了的，写“不确定”，不要用细读后的理解补全。
4. 写扫读负担（只写实际存在的）：几块同样显眼的字争夺主视线；独立的块太多、不知道先看哪块；单块太长、一块里有好几层意思；核心意思分散在几块里、要拼起来才懂；小字连续堆叠、要在多条之间挑；放大的词本身说不出处境或感受。
   短语、整句、问句都不自动加分或扣分，字数、条数也不是扣分公式；只看第一眼实际拿到多少。

【扫读 0–4】
4：3 秒内直接抓到核心处境和核心感受，关系也基本清楚；视觉入口明确、主次清楚，不用再找别的字。
3：第一眼已抓到核心处境和核心感受，只是一项辅助信息要再看一眼；核心不依赖几块拼接。
2：第一眼只抓到主题、关键词或部分意思，判断不了核心处境或核心感受；要读完整长句、拼接两块以上，或在几块相近的字里找线索。
1：只看到几个孤立的词，不知道这一屏在说什么；没有明确入口。
0：基本抓不到有意义的东西。
约束：如果你在负担里写了“核心意思要拼接”或“要逐句读才懂核心”，扫读不得高于 2。截图没收到或看不清，valid 写 false，不要猜。

只输出 JSON：{"valid":true,"entry":"视觉入口","grasp_who":"第一眼抓到的处境或“不确定”","grasp_feel":"第一眼抓到的感受或“不确定”","missed":"图上有但第一眼没抓到的重要内容","burden":["…"],"score":0}
"""
LINK = """你是第一次看这个视频的普通观众：正在听一首钢琴曲，屏幕上半是文字，下半是音符动画，右上角一列小字是全曲的阶段目录。
附件是同一屏在三个时刻的真实截图（{STATES}），有些字是随音乐陆续出现的。这一屏停留 {SEC} 秒。

【只评一件事：串起来】正常读完这一屏实际出现的文字后，它们能不能自然理解成同一个人的同一个处境和心理过程：感受挂在他的处境上，而不是一堆互不相干的词或句子。
判断的是文字本身有没有把关系给清楚，不是你能不能凭理解力自己拼起来。是短语还是整句、像不像清单，本身不算好坏。扫不扫得动不在这里评。

【串起来 0–4】
4：各块围绕同一个处境，感受和处境的关系明确；顺序、分组和说法自然引着人理解，不用自己补因果、猜各块挂在哪。
3：整体串成一回事，核心处境和感受关系明确；个别辅助的块归属不够清楚，不影响整体。
2：各块可能有关，但要读者自己推因果、找对应、重新组织；读完仍有部分不知道挂在哪。
1：大部分像彼此独立的句子或词，没有共同主线。
0：完全串不成一回事。
截图没收到或看不清，valid 写 false。

只输出 JSON：{"valid":true,"thread":"读完后这一屏讲的是一件什么事（一句话）","loose":"挂不上的块（没有写无）","link":0}
"""
for t, n in ((SCAN, 'scanjudge2.SCAN'), (LINK, 'scanjudge2.LINK')): prompt_lint.lint(t, n)
SHOTS = {1: '开屏约 3 秒时', 3: '结束前 1 秒时（这一屏的字已全部出现）'}


def ask(rid, msg, m, imgs, need):
    for k in range(3):
        try:
            r = parse(v1.call_img(rid + ('' if not k else f'_r{k}'), msg, m, imgs)); assert need in r and r.get('valid') is not False, '无效'
            return r
        except Exception as ex: print('不合格', rid, repr(ex)[:120], flush=True)


def one(a):
    w, sec, j, m, tag, run = a; p = S/f'scanB_{w}_{j}_{tag}_{run}_{sec}.json'
    if p.exists(): return rd(p)
    win = pub16.windows(w); dur = win[sec][1]-win[sec][0]; ts = v1.times(w)[sec]
    imgs = {i: v1.OUT/tag/f'{w}_{sec}_{i}.png' for i in (1, 2, 3)}
    out = {'shots': {}}
    for i in (1, 3):
        r = ask(f'scanB_{w}_{j}_{tag}_{run}_{sec}_s{i}', SCAN.replace('{WHEN}', SHOTS[i]), m, [imgs[i]], 'score')
        if not r: return
        out['shots'][str(i)] = r
    states = '；'.join(f"第 {i} 张是这一屏开始后第 {t-win[sec][0]:.0f} 秒" for i, t in enumerate(ts, 1))
    r = ask(f'scanB_{w}_{j}_{tag}_{run}_{sec}_link', LINK.replace('{STATES}', states).replace('{SEC}', str(round(dur))), m, [imgs[1], imgs[2], imgs[3]], 'link')
    if not r: return
    out['link'] = r; sc = [float(x['score']) for x in out['shots'].values()]
    out['score'] = sum(sc)/len(sc); out['worst'] = min(sc)
    wr(p, out); return out


def judge(tag, run='run1'):
    v1.shots(tag)
    only = [x for x in os.environ.get('SJ_SECS', '').split(',') if x]
    jobs = [(w, k, j, m, tag, run) for w in WORKS for k in pub16.windows(w) if not only or k in only for j, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(int(os.environ.get('SJ_THREADS', '8'))) as ex: list(ex.map(one, jobs))


def summ(tag, runs):
    only = [x for x in os.environ.get('SJ_SECS', '').split(',') if x]
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                rs = [rd(p) for p in sorted(S.glob(f'scanB_{w}_{j}_{tag}_{run}_S*.json')) if not only or p.stem.split('_')[-1] in only]
                if not rs: row.append('缺'); continue
                sc = [r['score'] for r in rs]; wo = [r['worst'] for r in rs]; lk = [float(r['link']['link']) for r in rs]
                row.append(f"扫读 {sum(sc)/len(sc):.2f}（最低≤2 的屏 {sum(1 for x in wo if x <= 2)}）、串起来 {sum(lk)/len(lk):.2f}（≤2 {sum(1 for x in lk if x <= 2)}），{len(rs)} 屏")
            print(f'截图评委2 {tag} {w} {j}： ' + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    cmd, tag = sys.argv[1], sys.argv[2]
    if cmd == 'judge': run = sys.argv[3] if len(sys.argv) > 3 else 'run1'; judge(tag, run); summ(tag, [run])
    else: summ(tag, sys.argv[3:] or ['run1'])
