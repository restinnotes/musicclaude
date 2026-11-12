"""Op.52 分段：N01 自动选的 Rothstein 只有 7 段，一段 94 小节，放不进视频。改用同一次调研里 Klein 的 14 段，
共享的小节归后一段（校验器要求闭区间不重叠），原始标注保留。这是人工选择，记在 source.note 里。"""
import json, sys
sys.path.insert(0, 'D:/musicclaude/_thread_evo_20261019')
import seg
sys.stdout.reconfigure(encoding='utf-8')
j = json.load(open('D:/musicclaude/_thread_evo_20261019/runs/seg_op52_v1/parsed.json', encoding='utf-8'))
s4 = next(s for s in j['sources'] if s['id'] == 'S4'); lv = next(l for l in s4['levels'] if '正式段落' in l['level'])
raw = lv['segments']; segs = []
for i, x in enumerate(raw):
    start, end = int(x['start']), int(x['end'])
    if i+1 < len(raw) and int(raw[i+1]['start']) == end: end -= 1
    segs.append({'start': start, 'end': end, 'label': x.get('label', '')})
source = {k: s4.get(k) for k in ('id', 'author_or_institution', 'title', 'url', 'locator', 'accessed_original')}
source.update({'level': lv['level'], 'run': 'seg_op52_v1', 'note': 'N01 自动选 Rothstein 七段（Variation 2 长 94 小节，约 4 分钟一屏，不适合视频）。人工改用同一次调研的 Klein 十四段；原表相邻段共享小节处，共享小节归后一段。', 'numbering_note': j.get('numbering_note'), 'disagreements': j.get('disagreements')})
d = seg.build(j.get('work') or seg.CFG['op52']['work'], j.get('short_name') or '第四叙事曲', int(j['total_measures']), segs, source, 'published_structure_manual_pick (Klein 2004, shared bars to later segment)', [{'source_id': 'S1', 'who': 'William Rothstein', 'level': '外层主题—变奏结构', 'boundaries': [1, 8, 23, 58, 152, 203, 211, 240]}])
seg.save('op52', d)
p = 'D:/musicclaude/_thread_evo_20261019/works/op52/work.json'; w = json.load(open(p, encoding='utf-8'))
w['segmentation_source'] = 'Klein'; w['segmentation_source_note'] = source['note']; json.dump(w, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print([(x['start'], x['end'], x['label']) for x in d['segments']])
