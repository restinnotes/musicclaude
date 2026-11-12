"""11-09 凌晨 过密屏修补：绝对尺度验收（r3/openabs.py）里，各版本稳定剩下的中等问题，主要是停留短的屏字太多（船歌第 5 段 18 秒约 220 字、每秒 12 字以上；
现在的视频 w23 这一屏也有每秒 10 字）。这里只改每秒字数超过上限的屏，其余屏一字不动。
做法：把这一屏的话和感受一起交给模型，按停留秒数给字数上限；话里放大的关键词必须原样在（它们是因果主干），心里话短块保留；
可以删次要的小句、把两句话并成一句，但不加原来没有的意思。机械检查：放大词都在、总字数不超上限的 1.1 倍，否则这一屏退回原样。
python dense.py SRC NEW [每秒字数上限，默认 8]
"""
import copy, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script
import pub16

DEN = """下面是一首钢琴曲大众版“边听边看”视频里的一屏。普通观众第一次看，边听边扫，这一屏只停留 {SEC} 秒，现在约 {NOW} 字，太密，读不完。请把这一屏改到约 {BUD} 字以内。
“话”是大字，讲这个人的事，【】里是放大的关键词；“感受”是小字，用 / 隔开。

怎么改：
1. 【】里的关键词一个字都不改、都要留在话里，它们串起了这一刻的因果；关键词之间必要的因果连接也要在，观众要看得懂他为什么这样。
2. 先删：重复交代的、可有可无的修饰和补充、感受里和话重复的意思。再考虑把两句话并成一句。
3. 感受里像人说出来的一句心里话、一句自问，原样留着；留下的感受要具体（那个画面、那种身体感觉），不换成笼统的词。
4. 不加原来没有的意思；疑问仍是疑问，猜测仍是猜测；不写数字、不写小节号。
5. 改后的话要像一个人平常在讲：句子完整、通顺，不要省成电报式的短语（不要把主语、助词、连接词都删掉，把几个动作硬挤在一起）；宁可删掉一整个次要的意思，也不要把每个意思都压缩得读不顺。
6. 行的先后和种类照旧：原来是话的还是话，原来是感受的还是感受；一行可以删空（整行不要了）。

只输出 JSON：{"rows":[{"kind":"line","text":"改后的话（照原样带【】）"},{"kind":"feel","items":["短语","短语"]}]}，按原来的行顺序给全这一屏。

【这一屏】
{SCREEN}
"""
if os.environ.get('DENSE_V3'):   # 11-09：K11d 船歌第 5 段收紧后为什么 0:7（删了“先前藏着时还能装作……如今对方看出来了”这一前后对比）、细腻 0:7（具体画面被压缩改写）
    DEN = DEN.replace("6. 行的先后和种类照旧", "6. 交代他为什么这样的前后对比（先前怎样、如今怎样）和因果，一句都不删。" + chr(10) + "7. 感受里的具体画面要么整条原样留下，要么整条删掉，不要把它改写缩短。" + chr(10) + "8. 行的先后和种类照旧")
    assert '8. 行的先后' in DEN
if not os.environ.get('DENSE_V2') and not os.environ.get('DENSE_V3'): DEN = DEN.replace(DEN[DEN.index('5. 改后的话'):DEN.index('6. 行的先后')], '').replace('6. 行的先后', '5. 行的先后')   # 11-09：K11 第 5 段压出了“藏着装作没那么在乎”这种电报式写法，V2 加一条
prompt_lint.lint(DEN, 'dense.py')
LIM = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0


def L(sec): return sum(len(x['text']) if x['kind'] == 'line' else sum(len(i['text']) for i in x['items']) for x in sec['rows'])


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); win = pub16.windows(w); log = []
    for s in scr['sections']:
        dur = win[s['sec']][1]-win[s['sec']][0]; now = L(s); bud = round(LIM*dur)
        only = os.environ.get('DENSE_ONLY')   # 11-09 K14：只收紧绝对验收里反复报偏密的几屏，各给上限，例如 op60:S05:7,op61:S11:6.5
        if only:
            m = {(a, b): float(c) for a, b, c in (x.split(':') for x in only.split(','))}
            if (w, s['sec']) not in m: continue
            bud = round(m[(w, s['sec'])]*dur)
            if now <= bud: continue
        elif now <= bud*1.05: continue
        txt = []
        for x in s['rows']:
            if x['kind'] == 'line':
                t = x['text']
                for kk in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(kk, f'【{kk}】', 1)
                txt.append('话：' + t)
            else: txt.append('感受：' + ' / '.join(i['text'] for i in x['items']))
        msg = DEN.replace('{SEC}', str(round(dur))).replace('{NOW}', str(now)).replace('{BUD}', str(bud)).replace('{SCREEN}', '\n'.join(txt))
        ok = False
        for t in range(3):
            try:
                r = parse(call(f'pub24DEN{"3" if os.environ.get("DENSE_V3") else "2" if os.environ.get("DENSE_V2") else ""}_{w}_{s["sec"]}_{new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-dense'))['rows']
                old = s['rows']
                if [x.get('kind') for x in r] != [x['kind'] for x in old]: raise ValueError('行数或种类变了')
                rows = []
                for x, y in zip(old, r):
                    if x['kind'] == 'line':
                        nt = (y.get('text') or '').strip()
                        ks = re.findall('【([^】]+)】', nt); clean = nt.replace('【', '').replace('】', '')
                        if not all(k in clean for k in x.get('keys') or []): raise ValueError('放大词丢了')
                        rows.append(dict(x, text=clean or x['text']))
                    else:
                        its = [str(i).strip().rstrip('，。、；') for i in y.get('items') or [] if str(i).strip()]
                        base = x['items']
                        rows.append(dict(x, items=[dict(base[min(len(base)-1, q)], text=tx) for q, tx in enumerate(its)]))
                cand = dict(s, rows=[x for x in rows if x['kind'] == 'line' or x['items']])
                if L(cand) > bud*1.1: raise ValueError(f'仍然太长 {L(cand)}/{bud}')
                s['rows'] = cand['rows']; ok = True; log.append(f"{s['sec']} {round(dur)}秒 {now}→{L(s)}字"); break
            except Exception as ex: print('不合格', w, s['sec'], repr(ex)[:150], flush=True)
        if not ok: log.append(f"{s['sec']} 退回原样")
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '改了过密的屏：', '；'.join(log) or '无', '；小节号', gate2.barnums(w, new), flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
