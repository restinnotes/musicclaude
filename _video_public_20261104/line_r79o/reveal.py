"""11-09 傍晚 依次出现（“更精细的动画”）。
起因：K11g、K18b、K18c 的绝对验收里，中等问题几乎都是第 7 条“扫得动”：小字一长串，或十几条短条一开屏就同时挂在屏幕上。
写法两头都试过（长句扫不动、拆短条太多），每屏能放的感受总量就那么多；删字又丢“为什么”和覆盖。
用户 11-08 原话：“我们不是应该更精细的会给他做动画吗 然后也没有试要不要打碎？”
做法：内容一字不动，给每一行（大字）和每一条小字一个出现时刻 at（距这一屏开始的秒数），按阅读顺序、按字数比例铺在这一屏前 85% 的时间里；
标了小节的小字仍按小节出现（不改）。渲染器（film_v8.py，FILM_REVEAL）：到 at 才淡入，刚出现的加亮，下一条出现后恢复常色、留到这一屏结束。
python reveal.py SRC NEW [铺开比例，默认 0.85]
"""
import copy, sys
import pub16
from pub24 import S, rd, wr, WORKS, to_script
SPAN = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85


def one(w, src, new):
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); win = pub16.windows(w)
    for s in scr['sections']:
        dur = win[s['sec']][1]-win[s['sec']][0]
        units = []   # (对象, 字数)，按阅读顺序
        for x in s['rows']:
            if x['kind'] == 'line': units.append((x, len(x['text'])))
            else: units += [(i, len(i['text'])) for i in x['items'] if not i.get('bars')]
        tot = sum(n for _, n in units) or 1; acc = 0
        for o, n in units:
            o['at'] = round(dur*SPAN*acc/tot, 1); acc += n
    wr(S/f'screen_{w}_{new}.json', scr); to_script(w, new, scr)
    print(w, new, '每条加了出现时刻', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for w in WORKS: one(w, sys.argv[1], sys.argv[2])
