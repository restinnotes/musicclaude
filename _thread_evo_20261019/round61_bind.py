"""Bind the fully read R61 outputs and mechanically apply their exact edits."""
import json
import copy
import experiment_batch as B
import round54_candidates as R
from round59_inspect import exact

R.BASE = 'r54weave'
R.ROOT = B.ROOT / 'runs/_batches/round61_boundary'
author = 'r61_advisor_g6b'
folder = B.evo.RUNS / author
message = (folder / 'prepared_input.txt').read_text(encoding='utf-8')
task = next(t for t in json.loads((B.ROOT / 'runs/_batches/round61_new_findings/advisors.json').read_text(encoding='utf-8'))['tasks'] if t['rid'] == author)
assert B.digest(message) == task['input_sha256']
proof = exact(author, message)
assert len(B.V.parse(author)['candidates']) == 1
B.record_review(author, True, '全文读诊断/完整prompt/放弃方向/风险，实际冻结长附件逐字及字节manifest绑定。ChannelSplit与已选Event-State Bridge同一表达状态分离机制，不再作为独立机制购买；完整结构LINE接口不同于现有文本view，未选择执行，不擅自适配或拼写。' + B.json_text(proof))

c = json.loads((R.ROOT / 'candidates.json').read_text(encoding='utf-8'))['candidates'][0]
rows = []
for w in B.F.WORKS:
    rid = R.rid(c, w, 1)
    proof = R.verify_input(c, w, 1)
    d = R.parsed(rid)
    assert isinstance(d['edits'], list) and isinstance(d['note'], str)
    old = B.V.graph_of(w, R.BASE)
    by_id = B.V.index(old)
    sections = [s['sec'] for s in old['segments']]
    seen_ids, seen_sections = set(), set()
    for edit in d['edits']:
        assert edit['op'] == 'replace' and edit['id'] in by_id and edit['id'] not in seen_ids
        sec, item = by_id[edit['id']]
        assert sec['sec'] != sections[0] and sec['sec'] not in seen_sections
        assert edit['text'] != item['text']
        seen_ids.add(edit['id'])
        seen_sections.add(sec['sec'])
    B.record_review(rid, True, 'edits与完整note全文读，实际prepared/prompt/input逐字核验；Op60空改动保留相反读法，Op61仅S07-1安心→暖和及承接词，引用/元数据/事实不变；每条一句和2—4条通过，纯模型原文机械套用。' + B.json_text(proof))
    after = R.checked_result(c, w)
    assert [s['sec'] for s in after['segments']] == sections
    rows.append({'work': w, 'rid': rid, 'proof': proof, 'edits': d['edits'], 'note': d['note'],
                 'unchanged_body': not d['edits']})
applied = R.ROOT / f"{c['tag']}_applied.json"
if not applied.exists():
    R.apply(c['tag'])
else:
    receipt = json.loads(applied.read_text(encoding='utf-8'))
    for w, sha in receipt['graph_hashes'].items():
        assert B.digest((B.V.OUT / f"{w}_{c['tag']}.json").read_text(encoding='utf-8')) == sha
for row in rows:
    w = row['work']
    old, new = B.V.graph_of(w, R.BASE), B.V.graph_of(w, c['tag'])
    expected = copy.deepcopy(old['segments'])
    lookup = {i['id']: i for s in expected for i in s['items']}
    for edit in row['edits']:
        lookup[edit['id']]['text'] = edit['text']
        # Existing pipe.save derives the display shortcut from the exact text.
        lookup[edit['id']]['key'] = edit['text'][:8]
    assert new['segments'] == expected
    row['blind_view_identical_to_current_mainline'] = B.V.view(old) == B.V.view(new)
B.write_frozen(R.ROOT / 'production_verified.json', B.json_text({'base': R.BASE,
    'tag': c['tag'], 'rows': rows, 'only_edited_work': 'op61',
    'actual_quality_productions': 1, 'parent_collectors_terminal': ['65069', '83139'],
    'deduplication': 'All three advisers propose expression/event-state separation. Only one representative executed. No other independent candidate supplied.'}))
print(B.json_text({'tag': c['tag'], 'base': R.BASE, 'edits': {r['work']: len(r['edits']) for r in rows}, 'calls': 0}))
