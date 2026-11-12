"""11-08 去音乐术语层：开放评审（K3N、K3M2，两首、两位评委都报，中等）说感受常先讲左手、和弦、声部、调性，再讲感受，像另起一套音乐赏析。
大众版标准第 4/6 条：纯写音乐本身的换成它带出的感受。这里只改含术语的感受块，长度不变（±15%），画面、比喻、身体感觉、心里话都留。
python term.py SRC NEW
"""
import copy, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script

TERMS = ['左手', '右手', '双手', '和弦', '声部', '内声部', '琶音', '颤音', '调性', '大调', '小调', '转调', '半音', '八度', '三连音', '音型', '花腔', '主题', '乐句', '终止', '伴奏', '切分', '低音', '高音区', '装饰音', '踏板', '声线', '旋律线', '和声', '舞曲', '马祖卡', '波兰舞曲', '再现', '尾声', '引子', '属', '主和弦']
TR = re.compile('|'.join(sorted(map(re.escape, TERMS), key=len, reverse=True)))
FIX = """下面是钢琴曲大众版“边听边看”视频屏幕上的几块感受小字。观众是普通人，不懂乐理，边听边扫。这几块里用了音乐术语（如左手、和弦、声部、琶音、颤音、调性、体裁名），观众要先理解这些词，才读得到感受。
请把每块改成观众直接能感到的说法：
1. 术语换成它让人听到、感到的东西（声音怎样动、身体怎样感觉、像什么）；能帮观众对上声音的说法可以留（高低、快慢、轻重、远近这类）。
2. 块里原有的画面、比喻、身体感觉、心里话、转折一个都不删，意思和语气不变；疑问仍是疑问，猜测仍是猜测。不加原块没有的事。
3. 长度和原块差不多（不多也不少于原块的七八成）。口语，不写术语，不写数字。{LEN}

只输出 JSON：{"items":[{"id":"编号","text":"改后的整块"}]}

{ITEMS}
"""
prompt_lint.lint(FIX, 'term.py')
import os
TMAX = float(os.environ.get('TERM_MAX', '1.15'))   # 11-08 K3M2T 不啰嗦 0:4：改后允许变长 15%；T2 改为不许变长


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); todo = {}
    for s in scr['sections']:
        for k, x in enumerate(s['rows'], 1):
            if x['kind'] != 'feel': continue
            for n, i in enumerate(x['items'], 1):
                if TR.search(i['text']): todo[f"{s['sec']}-r{k}-i{n}"] = i
    txt = '\n'.join(f"[{bid}] {i['text']}" for bid, i in todo.items())
    for t in range(3):
        ans = call(f'pub24TM{"2" if TMAX <= 1.0 else ""}_{w}_{new}' + ('' if not t else f'_r{t}'), FIX.replace('{ITEMS}', txt).replace('{LEN}', '改后不能比原块长，只能一样长或略短；术语换掉后，块里原来就重复的说法顺手合并。' if TMAX <= 1.0 else ''), G6, 'gpt3s', 'public24-term')
        try:
            r = {x['id']: (x.get('text') or '').strip().rstrip('，。、；') for x in parse(ans)['items']}; bad = 0
            for bid, i in todo.items():
                nt = r.get(bid) or ''
                if not nt or not (0.85*len(i['text']) <= len(nt) <= TMAX*len(i['text'])+(2 if TMAX > 1 else 0)) or re.search(r'\d', nt): bad += 1; continue
                i['text'] = nt
            left = sum(bool(TR.search(i['text'])) for i in todo.values())
            wr(p, scr); to_script(w, new, scr)
            print(w, new, '含术语的块', len(todo), '；长度不合没采用', bad, '；改后仍含术语', left, '；小节号', gate2.barnums(w, new), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
