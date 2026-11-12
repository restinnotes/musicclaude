"""评审查出原文没有的内容时，只把那一句交回写稿模型改。结果存成新 tag。"""
import json, sys
import pub
sys.stdout.reconfigure(encoding='utf-8')
w, tag, new = sys.argv[1:4]
d = pub.rd(pub.ROOT/f'runs/script_{w}_{tag}.json'); k = pub.rd(pub.ROOT/f'runs/judge_{w}_{tag}_keep.json')
_, block = pub.source_block(w)
for x in k['added']:
    bad = x['text'].removeprefix('线：').removeprefix('珠：')
    sec = next(s for s in d['sections'] for b in s['beats'] if b['line']['text'] == bad or any(y['text'] == bad for y in b['beads']))
    msg = f"""下面是一首曲子的文字和给大众看的短版。评审指出短版里这一句超出了原文：\n“{bad}”\n理由：{x['why']}\n\n请只改这一句，让它不超出原文，别的不动。如果是线，不超过 24 字，平常话，能接上前后句；如果是珠子，不超过 20 字。key 是句中最要紧的连续几个字，不超过 10 字，逐字取自这句。\n只输出 JSON：{{"text":"…","key":"…"}}\n\n这一段的短版：{json.dumps(sec, ensure_ascii=False)}\n\n原文：{block}"""
    ans = pub.evo_call(f'pub_20261104_fixadded_{w}_{new}', msg, 'gpt-6-thinking', 'public-fix')
    r = pub.parse(ans); print(bad, '→', r)
    for b in sec['beats']:
        if b['line']['text'] == bad: b['line']['text'] = r['text']; b['line']['key'] = r['key']
        for y in b['beads']:
            if y['text'] == bad: y['text'] = r['text']
pub.wr(pub.ROOT/f'runs/script_{w}_{new}.json', d)
print(pub.check_script(w, d))
