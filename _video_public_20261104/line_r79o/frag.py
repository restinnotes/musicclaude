"""11-09 晚 K20：大字照抄 K11g，只把小字改成一眼扫的核心短语（像 w23）。用户：“因为它这个是要一眼扫的呀 你这不拆我感觉肯定不太对”。K19 是按逗号机械切开（还留着描述音乐的半句），不算真拆。
下面是 K19 reshape.py 原说明：
11-09 傍晚 K19：只动 K11g 里有问题的屏，逐屏重组（两位顾问的路线 B 的局部版）。
起因：K11g、K18b 的绝对验收里，中等问题几乎都是同一类——小字感受是一长串多层意思的句子，几条积在同一屏，扫不完；另有几屏每秒字数偏高。
删字（K12、K14）丢“为什么”和连贯；全曲重组（K18b）把大字压成生硬短句。这里只改形态、不删内容：
挑出“有超过 LONG 字的小字条”或“每秒超过 RATE 字”的屏，把这一屏交给改稿人：长小字拆成各自完整的短条（一条一个画面/感觉/心里话），
或把承担人物处境的那层写进大字；大字保持完整自然的话；不加新内容；这一屏总字数不超过原来、也不超过 RATE×秒数。其余屏一个字不动。
python reshape.py SRC NEW g6|g56      环境变量 RESHAPE_LONG（默认 20）、RESHAPE_RATE（默认 6.5）
"""
import copy, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, blend, pub16
from refit import L, show, conv_rows
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, to_script

RS = """你在改一首钢琴曲大众版“边听边看”视频屏幕稿里的一屏。下半屏是音乐动画，上半屏是文字；普通观众第一次看，边听边扫，一眼扫过去抓几个词。这一屏停留 {SEC} 秒。
大字（话）讲这个人此刻的处境和为什么，这次一个字都不动。小字（感受）是听的人此刻的感受，散开排；现在的小字多是一长串多层意思的句子，扫不动。

请只把小字改成一眼扫得到的核心短语：
1. 每块是一个核心：一个画面、一种身体感觉、一句心里话或一个比喻，大约 3–10 个字，像人随口说出的，一眼读完。
2. 从原来的说法里取最有辨识度的那个东西，尽量用原词，可以浓缩，但不要换成笼统的情绪词；不同的画面、身体感觉、心里话分成不同的块。
3. 不是把一句话按逗号切开：切下来要是单独看不出是什么感受的半句（比如只描述声音怎么走的），就不要；描述音乐本身怎么走（旋律、声线、和弦、音型、上行下行）的部分，只留它带出的那个画面或感受。
4. 同一个意思只留一块；这一屏小字一共不超过 {MAXN} 块。
5. 小字的行数和每行的位置照旧（原来几行感受，改完还是几行，各自挨着原来那句话）；只属于某几小节的仍保留 bars。
6. 不加原来没有的意思；比喻仍是比喻；不写小节号。

只输出 JSON：{"rows":[{"items":[{"text":"…","from":["编号"],"bars":""}]}]}（rows 只列小字行，按原来小字行的顺序，一行对应一行）

【这一屏（现在）】
{CUR}

【这一屏的定稿珠子（内容依据）】
{SRC}
"""
prompt_lint.lint(RS, 'frag.py')
LONG = int(os.environ.get('RESHAPE_LONG', '20')); RATE = float(os.environ.get('RESHAPE_RATE', '6.5'))


def show_rows(s):
    out = []
    for x in s['rows']:
        if x['kind'] == 'line':
            t = x['text']
            for k in x.get('keys') or []: t = t.replace(k, f'【{k}】', 1)
            out.append('大字：' + t)
        else: out.append('小字：' + ' / '.join(i['text'] + (f"（到小节 {i['bars']} 才出现）" if i.get('bars') else '') for i in x['items']))
    return chr(10).join(out)


def one(a):
    w, src, new, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); orig = copy.deepcopy(scr['sections']); win = pub16.windows(w)
    s0 = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}

    def fix(k):
        s = scr['sections'][k]; dur = win[s['sec']][1]-win[s['sec']][0]
        feels = [x for x in s['rows'] if x['kind'] == 'feel']
        if not feels: return None
        maxn = max(3, round(dur/3.5)); src0 = s0[s['sec']]
        msg = (RS.replace('{SEC}', str(round(dur))).replace('{MAXN}', str(maxn)).replace('{CUR}', show_rows(orig[k]))
               .replace('{SRC}', chr(10).join(f"珠子 {b['id']}：{b['text']}" for b in src0['beads'])))
        before = sum(len(i['text']) for x in feels for i in x['items'])
        for t in range(3):
            try:
                r = parse(call(f'frag_{w}_{s["sec"]}_{new}' + ('' if not t else f'_r{t}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-frag'))['rows']
                if len(r) != len(feels):   # 11-09：模型常把每条原小字单列一行；按来源珠子归回原来那一行
                    owner = {i.get('bead'): n for n, x in enumerate(feels) for i in x['items']}
                    groups = [[] for _ in feels]; last = 0
                    for y in r:
                        for i in y.get('items') or []:
                            n = next((owner[f] for f in (i.get('from') or []) if f in owner), last); last = n; groups[n].append(i)
                    r = [{'items': g} for g in groups]
                new_items = []
                for x, y in zip(feels, r):
                    its = [i for i in y.get('items') or [] if (i.get('text') or '').strip()]
                    if not its: raise ValueError('一行小字空了')
                    if any(len(i['text']) > 14 for i in its): raise ValueError('有块太长 ' + max((i['text'] for i in its), key=len))
                    base = x['items'][0]
                    new_items.append([dict(bead=(i.get('from') or [base.get('bead')])[0] if (i.get('from') or [None])[0] else base.get('bead'), text=i['text'].strip().rstrip('，。、；'), bars=i.get('bars') or '', **({'from': i['from']} if i.get('from') else {})) for i in its])
                n = sum(len(v) for v in new_items)
                if n > maxn+1: raise ValueError(f'块太多 {n}/{maxn}')
                for x, v in zip(feels, new_items): x['items'] = v
                after = sum(len(i['text']) for x in feels for i in x['items'])
                return f"{s['sec']} 小字 {before}→{after}字、{n}块"
            except Exception as ex: print('不合格', w, s['sec'], repr(ex)[:150], flush=True)
        return f"{s['sec']} 没改成"
    with ThreadPoolExecutor(8) as ex: log = [x for x in ex.map(fix, range(len(scr['sections']))) if x]
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '小字改成核心短语：', '；'.join(log) or '无', '；全曲', sum(L(s) for s in scr['sections']), '字', flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
