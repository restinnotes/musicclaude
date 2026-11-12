"""Copy bead graphs and add evidence-backed source annotations; never rewrite items."""
import collections
import difflib
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path('D:/musicclaude')
EVO = ROOT / '_thread_evo_20261019'
ORIGINAL = EVO / 'deliverable/bead_graph'
OUT = ORIGINAL / '标注模型来源'
WORKS = {'Op60': '_bead_saturation_20261018', 'Op61': '_bead_op61_20261020'}
MODELS = {'gpt56w': 'GPT‑5.6w', 'gpt6w': 'GPT‑6w', 'gflash': 'Gemini Flash', 'luna': 'Luna'}


def norm(s):
    return re.sub(r'[^\w]', '', s)


def model(src):
    return MODELS[src.removeprefix('SRC-').split('-')[0]]


def model_list(srcs):
    return '、'.join(dict.fromkeys(model(s) for s in sorted(srcs)))


def link(path, line=None, label=None):
    suffix = f':{line}' if line else ''
    return f'[{label or path.name}](<{path.as_posix()}{suffix}>)'


def load_work(work, folder):
    base = ROOT / folder
    a = {}
    for p in sorted((base / 'inputs/A').glob('*.md')):
        text = p.read_text(encoding='utf-8-sig')
        a[p.stem] = {'path': p, 'text': text, 'normalized': norm(text)}
    assert len(a) == 24
    structs = {}
    for p in sorted((base / 'deliverable/struct').glob('S*.json')):
        s = json.loads(p.read_text(encoding='utf-8'))
        structs[s['segment']] = (s, p)
    items = json.loads((EVO / f'evaluations/beadgraph/bg2_{work.lower()}_fixed.json').read_text(encoding='utf-8'))['items']
    result = {}
    correction_count = 0
    for sid, (s, path) in structs.items():
        for b in s['beads']:
            records = []
            seen = set()
            for field in ('sources', 'also_expressed_by', 'vivid_lines'):
                for q in b.get(field, []):
                    key = (q['src'], q['quote'])
                    if key in seen:
                        continue
                    seen.add(key)
                    nq = norm(q['quote'])
                    actual = [q['src']] if q['src'] in a and nq in a[q['src']]['normalized'] else [src for src, data in a.items() if nq in data['normalized']]
                    assert actual, (work, sid, b['id'], q)
                    corrected = q['src'] not in actual
                    correction_count += corrected
                    records.append({'field': field, 'claimed_src': q['src'], 'actual_src': actual, 'quote': q['quote'], 'corrected': corrected})
            assert records, (work, sid, b['id'])
            upstream = sorted({src for q in records for src in q['actual_src']})
            result[sid, b['id']] = {'struct': path, 'text': b['text'], 'records': records, 'upstream': upstream, 'items': []}
            for idx, it in enumerate(items[sid][b['id']]):
                text = it.get('text_display') or it['text']
                nt = norm(text)
                exact = [src for src, data in a.items() if nt in data['normalized']]
                fragments = []
                if not exact:
                    # Only literal shared substrings, never a fuzzy/semantic attribution.
                    for q in records:
                        nq = norm(q['quote'])
                        m = difflib.SequenceMatcher(None, nt, nq, autojunk=False).find_longest_match()
                        if m.size >= max(8, len(nt) * .25):
                            fragments.append({'actual_src': q['actual_src'], 'fragment': nt[m.a:m.a + m.size], 'quote': q['quote']})
                level = '原稿原句' if exact else ('综合改写，有可逐字对照片段' if fragments else '综合改写，仅标珠子级来源')
                result[sid, b['id']]['items'].append({'id': f'{sid}-{b["id"]}-{idx+1:02}', 'text': text, 'text_original': it['text'], 'kind': it['kind'], 'bars': it['bars'], 'level': level, 'exact_src': exact, 'fragments': fragments, 'upstream_bead_src': upstream})
    return a, result, correction_count


def locate(data, quote):
    q = norm(quote)
    pos = data['normalized'].find(q)
    assert pos >= 0
    offset = 0
    for line, text in enumerate(data['text'].splitlines(), 1):
        length = len(norm(text))
        if offset + length > pos:
            return line
        offset += length
    raise AssertionError(quote)


def anchor(sid, bid):
    return f'src-{sid.lower()}-{bid.lower()}'


def annotation(item, sid, bid):
    bead_link = f'[珠子完整来源](#{anchor(sid, bid)})'
    if item['exact_src']:
        return f'〔原稿原句：{model_list(item["exact_src"])}；{bead_link}〕'
    if item['fragments']:
        srcs = {src for f in item['fragments'] for src in f['actual_src']}
        return f'〔GPT‑6 综合改写；可逐字对照片段：{model_list(srcs)}；{bead_link}〕'
    return f'〔GPT‑6 综合改写；上游（珠子级）：{model_list(item["upstream_bead_src"])}；{bead_link}〕'


def source_appendix(a, beads):
    lines = ['', '## 模型来源与原稿核对', '',
             '以下逐珠子列出完整 STRUCT 保存的来源。`sources` 是主要素材，`also_expressed_by` 是并入的相近说法，`vivid_lines` 是保留的鲜明原句；它们均按实际原稿重新核验。链接直接定位原稿行。', '']
    fields = {'sources': '主要素材', 'also_expressed_by': '相近说法', 'vivid_lines': '鲜明原句'}
    for (sid, bid), bead in beads.items():
        lines += [f'<a id="{anchor(sid, bid)}"></a>', '', f'### {sid} · {bid}', '',
                  f'完整记录：{link(bead["struct"])}。本珠子上游模型：**{model_list(bead["upstream"])}**。', '']
        for q in bead['records']:
            refs = '、'.join(link(a[src]['path'], locate(a[src], q['quote']), f'{model(src)} / {src}') for src in q['actual_src'])
            correction = f' **来源核正：原记录写 `{q["claimed_src"]}`，此处按原稿实际位置标注。**' if q['corrected'] else ''
            lines += [f'- {fields[q["field"]]}｜{refs}：“{q["quote"]}”{correction}']
        # Item-level evidence makes the literal-fragment labels independently reviewable.
        lines += ['', '本珠子各条目的核对依据：', '']
        for it in bead['items']:
            evidence = []
            if it['exact_src']:
                evidence = [link(a[src]['path'], locate(a[src], it['text']), f'{model(src)} 原稿') for src in it['exact_src']]
            elif it['fragments']:
                for f in it['fragments']:
                    refs = '、'.join(link(a[src]['path'], locate(a[src], f['quote']), model(src)) for src in f['actual_src'])
                    evidence.append(f'共同片段“{f["fragment"]}”见 {refs}')
            else:
                evidence = ['目前证据只落实到上述整颗珠子的来源，未强行指定单句原作者']
            lines += [f'- `{it["id"]}` {it["text"]} → {"；".join(dict.fromkeys(evidence))}。']
        lines.append('')
    return lines


INTRO = [
    '> **模型来源标注说明**：整理后的珠子文字由 GPT‑6 Thinking / max 产出。每条新增标注区分三种证据：①“原稿原句”＝在 A 原稿找到整条文字（忽略标点、空白和 Markdown 排版）；②“可逐字对照片段”＝只确认部分文字的来源，整句仍属综合改写；③“上游（珠子级）”＝只能确认所属珠子的完整来源，不能据此认定每个模型都写过这一句。',
    '>',
    '> `GPT‑5.6w`、`GPT‑6w`、`Gemini Flash`、`Luna` 是上游原稿的模型标签；具体 int/web、轮次、文件和引文见每条“珠子完整来源”。原记录中的错误来源编号按原稿实查核正；原珠子正文、顺序和分类保留。',
    '',
]


def render(source, a, beads, by_kind):
    original = source.read_text(encoding='utf-8-sig')
    lines = original.splitlines()
    out = []
    sid = bid = None
    count = 0
    used = []
    for i, line in enumerate(lines):
        if m := re.match(r'^### (S\d+) ', line):
            sid = m.group(1)
        if not by_kind and (m := re.match(r'^\*\*(B\d+)｜', line)):
            bid = m.group(1)
        if line.startswith('- （'):
            m = re.match(r'^- （([^）]+)）(.*)$', line)
            assert m, line
            prefix, text = m.groups()
            if by_kind:
                bid = prefix.rsplit('·', 1)[1]
            candidates = [it for it in beads[sid, bid]['items'] if norm(text) in (norm(it['text']), norm(it['text_original']))]
            assert len(candidates) == 1, (source, sid, bid, text)
            it = candidates[0]
            line += '　' + annotation(it, sid, bid)
            count += 1
            used.append(it['id'])
        out.append(line)
        if i == 2:
            out += ['', *INTRO]
    expected = [it['id'] for b in beads.values() for it in b['items']]
    assert sorted(used) == sorted(expected)
    assert len(used) == len(set(used))
    out += source_appendix(a, beads)
    target = OUT / source.name.replace('.md', '_标注模型来源.md')
    target.write_text('\n'.join(out) + '\n', encoding='utf-8')
    # Removing the inserted labels/intro/appendix must reproduce the original lines exactly.
    restored = []
    for line in out[:len(lines) + len(INTRO) + 1]:
        restored.append(line.split('　〔', 1)[0])
    del restored[3:3 + len(INTRO) + 1]
    assert restored == lines, target
    return {'file': str(target), 'items_annotated': count, 'original_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'original_preserved': True}


def main():
    OUT.mkdir(exist_ok=True)
    audit = {'policy': 'Only exact normalized source matches or literal matching fragments support item-level references. Other model attributions are explicitly bead-level. No semantic source guessing.', 'works': {}}
    for work, folder in WORKS.items():
        a, beads, corrections = load_work(work, folder)
        all_items = [it for b in beads.values() for it in b['items']]
        outputs = []
        for suffix, by_kind in [('_珠子图_按种类.md', True), ('_珠子图.md', False)]:
            outputs.append(render(ORIGINAL / f'{work}{suffix}', a, beads, by_kind))
        audit['works'][work] = {'beads': len(beads), 'items': len(all_items), 'evidence_levels': dict(collections.Counter(it['level'] for it in all_items)), 'corrected_unique_quote_records': corrections, 'outputs': outputs, 'provenance': [{'segment': sid, 'bead': bid, 'struct_file': str(b['struct']), 'sources': b['records'], 'items': b['items']} for (sid, bid), b in beads.items()]}
        print(work, json.dumps({k: v for k, v in audit['works'][work].items() if k != 'provenance'}, ensure_ascii=False))
    (OUT / '模型来源_核对记录.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    readme = ['# 两首曲子珠子图 · 模型来源标注副本', '',
              '本目录复制原珠子图并在每条后加来源标注。两首各保留“按种类”和“按珠子”两种排法；原目录的四份文件没有改动。', '',
              '## 阅读入口', '']
    for work, data in audit['works'].items():
        for output in data['outputs']:
            p = pathlib.Path(output['file'])
            readme.append(f'- {link(p)}：{output["items_annotated"]} 条。')
    readme += ['', '## 标注的准确范围', '', *INTRO[:3], '',
               '“原稿原句”允许忽略标点、空白和 Markdown 排版；不代表未经排版变化的逐字节复制。“可逐字对照片段”仅表明相同片段存在于对应原稿，不把它冒充整句唯一作者。无法可靠细分的条目列出整颗珠子的来源，并明确标注“珠子级”。', '',
               'int/web 及轮次沿用来源文件编号，不额外推断实际是否联网。所有引用均重新检查原稿内容；原编号标错时采用实际能找到该引文的来源，并保留纠错说明。', '',
               '## 核对统计', '', '| 作品 | 珠子数 | 短条目数 | 原稿原句 | 有可逐字对照片段 | 仅珠子级来源 |', '|---|---:|---:|---:|---:|---:|']
    for work, data in audit['works'].items():
        c = data['evidence_levels']
        readme.append(f'| {work} | {data["beads"]} | {data["items"]} | {c.get("原稿原句",0)} | {c.get("综合改写，有可逐字对照片段",0)} | {c.get("综合改写，仅标珠子级来源",0)} |')
    readme += ['', '两种排法使用同一套来源证据；统计按独立短条目计数，不把两种排法重复计入。完整结构化记录见 `模型来源_核对记录.json`。生成脚本：', '', link(pathlib.Path(__file__).resolve()), '']
    (OUT / 'README_模型来源标注.md').write_text('\n'.join(readme), encoding='utf-8')


if __name__ == '__main__':
    main()
