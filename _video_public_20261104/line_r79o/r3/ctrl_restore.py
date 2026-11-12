"""11-12 局部回补（记忆：成品修补“局部修订+回补赢、重写输”）：主线 CTRLsk2F 的小字改写丢了覆盖里“重要”一层的内容（多是心里话和珠子里的具体说法）。
把两位覆盖评委都判“没有”或“部分”的重要/核心单元逐屏交给 Argon，只在小字上做最小改动把内容放回去：可以改一两条小字、可以在一条里补半句，不加新条目（除非这一屏小字不到 3 条）；
大字、旁注不动；小字仍是听的人的具体感受或心里话，不复述大字、不总结道理；这一屏小字总字数最多比现在多 15%。
python r3/ctrl_restore.py SRC_TAG NEW_TAG → r3/s24/screen_{作品}_{NEW_TAG}.json"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import S, rd, parse, WORKS
sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); import evo
sys.stdout.reconfigure(encoding='utf-8')
SRC, NEW = sys.argv[1], sys.argv[2]

ASK = """下面是一份钢琴曲视频屏幕稿：每屏有大字（一个人在经历什么）和小字（听的人这时的感受或心里话）。审读发现，原料里有一些内容在屏幕上丢了（列在每屏下面）。

请只改小字，把丢掉的内容放回去，改动越小越好：
- 优先在已有的小字里补半句或换几个字；实在放不进去才新加一条（这一屏小字不到 3 条时才可以加）。
- 小字写成听的人具体感到的东西（身体感觉、画面、声音、比喻）或第一人称的心里话；不复述同一屏大字的意思，不替人物解释心理，不总结道理。
- 不加原料里没有的事、人物、关系。
- 这一屏小字的总字数最多比现在多 {CAPP}；不写音乐本身（乐器、音型、和弦、调性、声部）的描述；每条最多两个逗号，不用分号。
- 不需要改的小字原样照抄。编号必须一条不少；新加的用“新”编号（例如 S03#新1）。

只输出 JSON：{"items":[{"id":"S01#0","text":"…"}]}

{SCREEN}
"""


def one(w):
    sc = rd(S/f'screen_{w}_{SRC}.json'); us = {u['uid']: u for u in rd(S/f'units2_{w}.json')}
    votes = {}; BASEV = {}
    for j in ('g6', 'g56'):
        if os.environ.get('RESTORE_BASE'):
            for x in rd(S/f"cov3_{w}_{j}_{os.environ['RESTORE_BASE']}.json")['items']: BASEV.setdefault(x['uid'], []).append(x.get('verdict'))
    for j in ('g6', 'g56'):
        for x in rd(S/f'cov3_{w}_{j}_{SRC}.json')['items']: votes.setdefault(x['uid'], []).append(x.get('verdict'))
    miss = {}
    for u, v in votes.items():
        base = BASEV.get(u, [])
        narrow = os.environ.get('RESTORE_NARROW')   # 11-12 M1R 补过头（把讲音乐的也塞回小字、中等涨回 33）：只补讲体验的、而且是底稿（K28b）原来留住、改写后丢掉的
        if u in us and us[u]['tier'] in ('核心', '重要', '重要或补充') and v.count('留住') == 0 and not us[u].get('dup_of')            and (not narrow or (not us[u]['music_any'] and base.count('留住') >= 1)):
            miss.setdefault(us[u]['sec'], []).append(us[u]['what'])
    lines = []; ids = []
    for s in sc['sections']:
        lines.append(f"### {s['sec']}"); k = 0
        for r in s['rows']:
            if r['kind'] == 'line': lines.append(f"【大】{r['text']}")
            else:
                for it in r['items']:
                    i = f"{s['sec']}#{k}"; k += 1; ids.append(i); lines.append(f"【小 {i}】{it['text']}")
        for m in miss.get(s['sec'], []): lines.append(f"（丢了：{m}）")
    print(w, '丢掉的单元', sum(map(len, miss.values())), flush=True)
    got = None
    for t in range(3):
        try:
            r = parse(evo.call_argon_direct(f'restore_{NEW}_{w}' + ('' if not t else f'_r{t}'), ASK.replace('{CAPP}', os.environ.get('RESTORE_CAP', '15%')).replace('{SCREEN}', '\n'.join(lines)), meta={'stage': 'ctrl-restore'}) or '')
            got = {x['id']: x['text'] for x in r['items']}; assert all(i in got for i in ids); break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); got = None
    if not got: return
    new = copy.deepcopy(sc)
    for s in new['sections']:
        k = 0; feel = None
        for r in s['rows']:
            if r['kind'] != 'line':
                feel = r
                for it in r['items']:
                    old = it['text']; it['text'] = got[f"{s['sec']}#{k}"].strip().rstrip('。'); k += 1
                    if old != it['text']: print(w, s['sec'], '｜原：', old, '｜改：', it['text'], flush=True)
        adds = [v for i, v in got.items() if i.startswith(s['sec'] + '#新')]
        if adds and feel is not None:
            for v in adds:
                feel['items'].append({'text': v.strip().rstrip('。'), 'bead': '', 'from': [], 'bars': ''}); print(w, s['sec'], '｜新加：', v, flush=True)
    (S/f'screen_{w}_{NEW}.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))
