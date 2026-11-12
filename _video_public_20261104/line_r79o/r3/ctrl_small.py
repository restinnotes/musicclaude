"""11-12 写稿层诊断（Fable 审查：写稿层和线层的问题分两条道同时做）：开放评审反复报小字“复述大字”“替人物解释心理、下定义”。
假设：小字的腔调来自写稿层留下的小字说法（珠子原文不动，只看屏上小字怎么说）。验证：Argon 把 K28b 屏上的小字一条对一条改成听的人的具体感受（身体、画面、声音），
不复述大字、不解释人物心理，大字旁注不动；同一套快筛。看开放评审还报不报、盲比 small/human 变没变。
python r3/ctrl_small.py → r3/s24/screen_{作品}_g68CTRLs.json"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import S, rd, parse, WORKS, call, G6
TAG = os.environ.get('CTRL_S_TAG', 'g68CTRLs'); WHO = os.environ.get('CTRL_S_WHO', 'argon')
CAP = ('\n- 每条不能比原来那条长（字数小于等于原条）；屏幕停留时间有限，宁短勿长。' if os.environ.get('CTRL_S_CAP') else '')
sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019'); import evo
sys.stdout.reconfigure(encoding='utf-8')
ASK = """下面是一份钢琴曲视频屏幕稿：每屏有大字（一个人在经历什么）和小字（听的人这时的感受）。普通读者说：小字常常把旁边大字的意思换个说法再讲一遍，或者在替人物解释心理、给情绪下定义，不像听音乐时真实的感受。

请只改小字，一条对一条：
- 写成听的人这时具体感到的东西：身体的感觉、眼前的画面、声音给人的感觉、一个比喻。用“像……”或不带主语，不写“他”在想什么。
- 不复述同一屏大字的意思；不解释人物为什么这样；不总结道理。
- 意思的方向（情绪、强弱）跟原来那条一样，不加新的事、人物、关系。
- 像人平常说话，长度和原来差不多，最多两个逗号，不用分号。{CAP}
- 条目编号必须一条不少。

只输出 JSON：{"items":[{"id":"S01#0","text":"…"}]}

屏幕稿（【大】是大字，【小 编号】是要改的小字）：
{SCREEN}
"""


def one(w):
    sc = rd(S/f'screen_{w}_g68K28b.json'); lines = []; ids = []
    for s in sc['sections']:
        lines.append(f"### {s['sec']}"); k = 0
        for r in s['rows']:
            if r['kind'] == 'line': lines.append(f"【大】{r['text']}")
            else:
                for it in r['items']:
                    i = f"{s['sec']}#{k}"; k += 1; ids.append(i); lines.append(f"【小 {i}】{it['text']}")
    got = None
    for t in range(3):
        try:
            msg = ASK.replace('{CAP}', CAP).replace('{SCREEN}', '\n'.join(lines))
            rid = (f'ctrlsmall_{w}' if TAG == 'g68CTRLs' else f'ctrlsmall_{TAG}_{w}') + ('' if not t else f'_r{t}')   # 11-12：rid 带 TAG，免得不同版本误用同一份缓存
            r = parse((evo.call_argon_direct(rid, msg, meta={'stage': 'ctrl-small'}) if WHO == 'argon' else call(rid, msg, G6, 'gpt3s', 'ctrl-small')) or '')
            got = {x['id']: x['text'] for x in r['items']}; assert all(i in got for i in ids); break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); got = None
    if not got: return
    new = copy.deepcopy(sc)
    for s in new['sections']:
        k = 0
        for r in s['rows']:
            if r['kind'] != 'line':
                for it in r['items']:
                    old = it['text']; it['text'] = got[f"{s['sec']}#{k}"].strip().rstrip('。'); k += 1
                    print(w, s['sec'], '｜原：', old, '｜改：', it['text'], flush=True)
    (S/f'screen_{w}_{TAG}.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, WORKS))
