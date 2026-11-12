"""11-09 晚 截图扫读评委（评委矫正机制，judge_check/scanbias_A_*：两位顾问独立认为旧盲比读完整文字稿、测的是“通读舒服”，不是“第一眼抓到什么”）。
用户：“我担心你的评委有问题 因为它这个是要一眼扫的呀”；“如果是评委问题 你也应当去校准一下评委”；“可以渲染了”。
做法（两位顾问的共同建议）：
  1. 每屏用正式渲染器（film_v8）截三个时刻：刚出现约 3 秒、中间、结束前 1 秒（有“到时出现 / 依次出现”的，后两张自然包含累积的内容）。
  2. 评委每次只看一个版本的一屏（三张图），不给全文、不给别的版本；先写“第一眼抓到了什么”（事和人此刻的状态、感受）、漏了什么、要不要逐句读，再给 0–4 分。
     只评首眼扫读，不评文笔；短语不因为不是完整句扣分，长句不因为通顺加分。
  3. 校准：同一版换调用编号重测要接近；K11g（多层长句）、K18cM（十几条短条）、w23S（旧视频的核心短语）三个已知样本看分不分得开；再挑几屏给用户看。
python r3/scanjudge.py shots TAG            只截图 → out/scan/TAG/{作品}_{段}_{1,2,3}.png
python r3/scanjudge.py judge TAG [轮次]      截图 + 两位评委各评每屏 → r3/s24/scanA_{作品}_{评委}_{TAG}_{轮次}_{段}.json
python r3/scanjudge.py sum TAG [轮次...]     汇总
"""
import json, os, sys, zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
os.environ.setdefault('FILM_DATA', 'line_r79o')
import prompt_lint
from pub24 import S, rd, wr, parse, G6, G56, WORKS
import pub16
sys.stdout.reconfigure(encoding='utf-8')
OUT = HERE.parent/'out'/'scan'

SJ = """你是第一次看这个视频的普通观众：正在听一首钢琴曲，偶尔抬眼扫一下屏幕。屏幕上半是文字，下半是跟着音乐滚动的音符动画。
附件是同一屏在三个时刻的真实截图：{STATES}。这一屏一共停留 {SEC} 秒。有些文字是随音乐陆续出现的，所以三张图里的字可能不一样多。

目标只有两条，按这两条评，不评文章写得好不好：
一、一眼扫得过去：边听边扫的人，第一眼能不能抓到这一屏的要点。
二、扫到的东西串得起来：扫到的那几块（他的事、感受、画面）能不能连成一回事——知道这个人此刻怎么了，感受挂在他的处境上，而不是一堆互不相干的词。是短语还是整句、像不像一张清单，本身都不算好坏，只看能不能一眼抓到、抓到的能不能串起来。
规则：
- 只看图里实际显示的东西（字号大小、加亮、位置、条数、每条多长都算），不要用你对这首曲子的任何了解去补。
- 对每一张图，想象你只扫了一眼（约 3 秒），写下你真正抓到的：这个人此刻怎么了（一句话），此刻是什么感受（几个词）；哪些看起来重要但一眼没抓到、要逐句读才行。
- 短语、半句、问句、一声感叹都可以是好的扫读形态，不要因为不是完整句子扣分；一段读起来很通顺的长句，也不因为通顺加分——只看一眼抓不抓得到。
- 条数太多、彼此相近、不知道先看哪条，和单条太长、一条里挤好几层意思，都是扫读负担。
- 扫读 score 0–4 分：4 = 一眼抓到这个人此刻怎么了和核心感受，先看什么很清楚；3 = 主要的抓到，次要的要再看；2 = 只抓到一部分，重要的要逐句读；1 = 只看到几个孤立的词，不知道这一屏在说什么；0 = 抓不到。
- 串起来 link 0–4 分（看完三张图再给）：4 = 扫到的事和感受自然连成一回事；3 = 大体连得上，个别块不知道挂在哪；2 = 一半像散落的词，要自己去拼；1 = 基本是互不相干的词或句子；0 = 完全串不起来。

只输出 JSON：{"states":[{"shot":1,"grasp_who":"一句话","grasp_feel":"几个词","missed":"一眼没抓到的重要内容","score":0}],"score":0,"link":0,"main_problem":"最影响扫读或串起来的一处（没有就写无）"}
"""
prompt_lint.lint(SJ, 'scanjudge.py')
AT = [('刚出现约 3 秒', 3.0), ('中间', .5), ('结束前 1 秒', -1.0)]


def times(w):
    win = pub16.windows(w); out = {}
    for k, (a, b) in win.items():
        out[k] = [a+min(3., (b-a)*.3), a+(b-a)*.5, b-1.]
    return out


def shots(tag):
    import skia, film_v8
    d = OUT/tag; d.mkdir(parents=True, exist_ok=True)
    for w in WORKS:
        todo = [(k, i, t) for k, ts in times(w).items() for i, t in enumerate(ts, 1) if not (d/f'{w}_{k}_{i}.png').exists()]
        if not todo: continue
        f = film_v8.Film8(w, tag)
        for k, i, t in todo: f.frame(t).save(str(d/f'{w}_{k}_{i}.png'), skia.EncodedImageFormat.kPNG, 100)
        print('截好', tag, w, len(todo), '张', flush=True)


def call_img(rid, msg, model, imgs):
    """和 pub2.call 一样按调用编号分到 gpt3/gpt4，只是带上附件。"""
    sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); os.environ.setdefault('JV', '2')
    import evo
    evo.TL.route = 'gpt4s' if zlib.crc32(rid.encode()) % 2 else 'gpt3s'
    return evo.call(rid, msg, model=model, meta={'stage': 'public24-scan', 'web': True, 'attach': [str(x) for x in imgs]})   # 11-09：gpt3/gpt4 调用从 meta['attach'] 读附件；第一次放在 attach 参数里，评委回复“没收到截图”，那批作废


def one(a):
    w, sec, j, m, tag, run = a; p = S/f'scanA_{w}_{j}_{tag}_{run}_{sec}.json'
    if p.exists(): return rd(p)
    win = pub16.windows(w); dur = win[sec][1]-win[sec][0]; ts = times(w)[sec]
    states = '；'.join(f"第 {i} 张是这一屏开始后第 {t-win[sec][0]:.0f} 秒" for i, t in enumerate(ts, 1))
    msg = SJ.replace('{STATES}', states).replace('{SEC}', str(round(dur)))
    imgs = [OUT/tag/f'{w}_{sec}_{i}.png' for i in (1, 2, 3)]
    import time
    for k in range(3):
        t0 = time.time()
        try:
            r = parse(call_img(f'scanA_{w}_{j}_{tag}_{run}_{sec}' + ('' if not k else f'_r{k}'), msg, m, imgs)); assert 'score' in r
            wr(p, r); FAST[0] = 0; return r
        except Exception as ex:
            print('不合格', w, sec, j, tag, repr(ex)[:120], flush=True)
            if time.time() - t0 < 5:   # 11-09 晚：准则第九节第 8 条，连续零秒失败就停，不让流水线空转
                FAST[0] += 1
                if FAST[0] >= 6: print('== 通路连续零秒失败，停下', flush=True); os._exit(3)


FAST = [0]


def judge(tag, run='run1'):
    shots(tag)
    only = [x for x in os.environ.get('SJ_SECS', '').split(',') if x]   # 11-09 晚：校准对照只测几屏
    jobs = [(w, k, j, m, tag, run) for w in WORKS for k in pub16.windows(w) if not only or k in only for j, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(int(os.environ.get("SJ_THREADS", "8"))) as ex: list(ex.map(one, jobs))


def summ(tag, runs):
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                sc = [rd(p).get('score') for p in sorted(S.glob(f'scanA_{w}_{j}_{tag}_{run}_S*.json'))]
                sc = [float(x) for x in sc if isinstance(x, (int, float)) or str(x).replace('.', '').isdigit()]
                lk = [float(rd(p).get('link')) for p in sorted(S.glob(f'scanA_{w}_{j}_{tag}_{run}_S*.json')) if isinstance(rd(p).get('link'), (int, float))]
                row.append((f"扫读 {sum(sc)/len(sc):.2f}（≤2 分 {sum(1 for x in sc if x <= 2)} 屏）" if sc else '扫读缺') + (f"、串起来 {sum(lk)/len(lk):.2f}（≤2 分 {sum(1 for x in lk if x <= 2)} 屏）" if lk else '') + f"，{len(sc)} 屏")
            print(f'截图评委 {tag} {w} {j}： ' + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    cmd, tag = sys.argv[1], sys.argv[2]
    if cmd == 'shots': shots(tag)
    elif cmd == 'judge': judge(tag, sys.argv[3] if len(sys.argv) > 3 else 'run1'); summ(tag, [sys.argv[3] if len(sys.argv) > 3 else 'run1'])
    else: summ(tag, sys.argv[3:] or ['run1'])
