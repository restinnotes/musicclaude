"""11-09 傍晚 K19：只动 K11g 里有问题的屏，逐屏重组（两位顾问的路线 B 的局部版）。
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

RS = """你在改一首钢琴曲大众版“边听边看”视频屏幕稿里的一屏。下半屏是音乐动画，上半屏是文字；普通观众第一次看，边听边扫。这一屏停留 {SEC} 秒。
大字（连贯）讲这个人此刻的处境和为什么；小字（散落）是听的人此刻的感受，散开排，一眼扫一条。

验收里这一屏的问题：{WHY}

请重组这一屏的形态，不删内容：
1. 小字每一条只放一个画面、一种身体感觉、一句心里话或一个比喻，大约 18 个字以内，单独读得懂。原来一长串多层意思的小字，拆成几条各自完整的短条（不是把一句话从中间切开），或者把其中承担人物处境的那层意思写进大字。原来的具体说法尽量用原词，不换成笼统的说法。
2. 原来同一屏里意思相同的两说，只留更具体的那一个；除此之外不删内容。
3. 大字保持完整、自然的话，因果和转折的连接词留着；不压成短句或电报句。
4. 不加原来没有的意思；疑问仍是疑问，比喻仍是比喻，不写成他真的经历的事；不写小节号。
5. 和前后两屏接得上。只属于某几小节的感受仍写成小字并保留 bars。
6. 这一屏总字数不超过 {CAP} 字。

只输出 JSON：{"rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的 1–2 处关键词"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["编号"]},{"form":"散落","items":[{"text":"…","from":["编号"],"bars":""}]}]}

【前一屏】
{PREV}

【这一屏（现在）】
{CUR}

【后一屏】
{NEXT}

【这一屏的定稿线和珠子（内容依据）】
{SRC}
"""
prompt_lint.lint(RS, 'reshape.py')
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
        s = scr['sections'][k]; dur = win[s['sec']][1]-win[s['sec']][0]; now = L(s)
        long = [i['text'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items'] if len(i['text']) > LONG]
        dense = now > RATE*dur
        if not long and not dense: return None
        why = '；'.join(([f"有 {len(long)} 条小字是一长串多层意思的句子，扫不动"] if long else []) + ([f"每秒约 {now/dur:.1f} 字，偏密"] if dense else []))
        cap = min(now, round(RATE*dur)) if dense else now
        src0 = s0[s['sec']]
        msg = (RS.replace('{SEC}', str(round(dur))).replace('{WHY}', why).replace('{CAP}', str(cap))
               .replace('{PREV}', show_rows(orig[k-1]) if k else '（无）').replace('{CUR}', show_rows(orig[k]))
               .replace('{NEXT}', show_rows(orig[k+1]) if k+1 < len(orig) else '（无）')
               .replace('{SRC}', chr(10).join([f"线 {l['id']}：{l['text']}" for l in src0['lines']] + [f"珠子 {b['id']}：{b['text']}" for b in src0['beads']])))
        for t in range(3):
            try:
                r = parse(call(f'reshape_{w}_{s["sec"]}_{new}' + ('' if not t else f'_r{t}'), msg, G56 if who == 'g56' else G6, 'gpt3s', 'public24-reshape'))
                rows = conv_rows(w, {'sections': [{'sec': s['sec'], 'rows': r['rows']}]})
                n = L({'rows': rows})
                if n > cap*1.08: raise ValueError(f'超了 {n}/{cap}')
                if n < now*0.75: raise ValueError(f'删多了 {n}/{now}')
                s['rows'] = rows; return f"{s['sec']} {now}→{n}字（{why}）"
            except Exception as ex: print('不合格', w, s['sec'], repr(ex)[:150], flush=True)
        return f"{s['sec']} 没改成"
    with ThreadPoolExecutor(8) as ex: log = [x for x in ex.map(fix, range(len(scr['sections']))) if x]
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '重组了：', '；'.join(log) or '无', '；全曲', sum(L(s) for s in scr['sections']), '字', flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
