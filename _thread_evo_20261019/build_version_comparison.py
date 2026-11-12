"""Generate a complete version comparison from source graphs and bound evidence.

Read-only with respect to products, prompts and judgments; makes no model calls.
The default is an interim report. A final claim requires a separate verified
convergence audit whose version hashes still match the actual products.
"""
import argparse
import copy
import difflib
import json
import os
from pathlib import Path

os.environ.setdefault('JV', '2')
import experiment_batch as B
import round37_fair as FAIR
import round50_measure as MEASURE

ROOT = B.ROOT
SOURCES = {}


def read(path):
    path = Path(path)
    text = path.read_text(encoding='utf-8')
    SOURCES[str(path.relative_to(ROOT)).replace('\\', '/')] = B.digest(text)
    return text


def obj(path):
    return json.loads(read(path))


def link(path, label=None):
    path = Path(path).resolve()
    assert path.exists(), path
    return f'[{label or path.name}](<{path.as_posix()}>)'


def graph(work, tag):
    return obj(B.V.OUT / f'{work}_{tag}.json')['graph']


def bound(rid):
    folder = B.evo.RUNS / rid
    if not B.reviewed(rid):
        return False
    read(folder / 'output.txt')
    inspection = obj(folder / 'inspection.json')
    assert inspection['output_sha256'] == B.digest(B.evo.output(rid))
    return True


def comparison(tag, base):
    rows, pending = [], []
    for rid, expected, judge in MEASURE.jobs('fair', tag, base):
        folder = B.evo.RUNS / rid
        if not bound(rid):
            pending.append(rid + ': 未完整收取或尚未全文核验')
            continue
        actual = folder / 'prepared_input.txt'
        if not actual.exists() or read(actual) != expected:
            pending.append(rid + ': 当前两版与冻结评审输入不匹配')
            continue
        d = B.V.parse(rid)
        work = 'op60' if '_op60_' in rid else 'op61'
        secs = {s['sec'] for s in B.V.graph_of(work, tag)['segments']}
        if (not d or len(d.get('sections', [])) != len(secs)
                or {s['sec'] for s in d['sections']} != secs
                or any(s[k] not in ('X', 'Y', '差不多') for s in d['sections'] for k in B.F.DIMENSIONS)
                or any(d.get(k) not in ('是', '否') for k in ('X_replacing_Y_regress', 'Y_replacing_X_regress'))):
            pending.append(rid + ': 结构或枚举未通过')
            continue
        seat = rid.rsplit('_', 1)[-1]
        row = FAIR.read(work, judge, tag, base, seat)
        assert row is not None
        rows.append({**row, 'rid': rid})
    sums = {k: sum(r['net'][k] for r in rows) for k in B.F.DIMENSIONS} if rows else None
    return {'tag': tag, 'base': base, 'rows': rows, 'pending': pending, 'net_sums': sums,
            'wins': sum(r['new_win'] for r in rows), 'no_regress': sum(r['no_regress'] for r in rows)}


def lineage(tag, base):
    stages, seen = [], set()
    while tag != base:
        assert tag not in seen, 'Cyclic provenance'
        seen.add(tag)
        paths = [ROOT / 'runs/_batches' / folder / f'{tag}_applied.json'
                 for folder in ('round50_from_r49b', 'round54_broader')]
        existing = [p for p in paths if p.exists()]
        if len(existing) != 1:
            raise ValueError(f'{tag}: unambiguous mechanical application receipt required')
        receipt = obj(existing[0])
        parent = receipt['base']
        sources = {}
        for work in B.F.WORKS:
            rid = receipt.get('source_rids', {}).get(work, f'sc{tag}_{work}_A5')
            assert bound(rid), f'Unread product source: {rid}'
            answer = B.pipe.call(rid, '', 'g6', 'comparison-read-only')
            if 'edits' in answer:
                old = copy.deepcopy(graph(work, parent))
                index = B.V.index(old)
                for edit in answer['edits']:
                    sec, item = index[edit['id']]
                    if edit['op'] == 'replace':
                        item['text'] = edit['text']
                    elif edit['op'] == 'delete':
                        sec['items'].remove(item)
                    else:
                        raise ValueError('Unverified model edit operation')
                expected = [i['text'] for s in old['segments'] for i in s['items']]
            else:
                expected = [i['text'] for s in answer['segments'] for i in s['items']]
            actual = [i['text'] for s in graph(work, tag)['segments'] for i in s['items']]
            assert expected == actual, f'{work}/{tag}: prose differs from model source'
            prompt = B.evo.RUNS / rid / 'prepared_input.txt'
            read(prompt)
            sources[work] = {'rid': rid, 'prompt': prompt, 'output': B.evo.RUNS / rid / 'output.txt'}
        stages.append({'tag': tag, 'base': parent, 'receipt': existing[0], 'sources': sources})
        tag = parent
    return list(reversed(stages))


def stats(g):
    return {'sections': len(g['segments']), 'items': sum(len(s['items']) for s in g['segments']),
            'chars': sum(len(i['text']) for s in g['segments'] for i in s['items'])}


def segment_lines(s):
    lines = [f"关系：{s['relation']}", '']
    for item in s['items']:
        lines += [f"- `{item['id']}` {item['text']}"]
        if item.get('cite'):
            lines += ['  引用：' + '、'.join(item['cite']) + '。']
    return lines


def broader_search():
    """Show actual R54 evidence without promoting pending or rejected products."""
    folder = ROOT / 'runs/_batches/round54_broader'
    path = folder / 'candidates.json'
    if not path.exists():
        return []
    manifest = obj(path)
    md = ['## 扩大探索的实际结果', '',
          f"以下候选均针对当时主线 `{manifest['base']}`；不是与 `{manifest['base']}` 无关的起点改善，也不构成收敛声明。",
          '', '| 候选 / 机制 | 已核验盲比 | 新版 / 不退步 | 单独 / 简洁 / 人话 / 覆盖净胜总和 | 实际处置 |',
          '|---|---:|---:|---|---|']
    for candidate in manifest['candidates']:
        tag = candidate['tag']
        disposition_path = folder / f'{tag}_disposition.json'
        disposition = obj(disposition_path) if disposition_path.exists() else {}
        if disposition.get('status') == 'hard_constraint_archive':
            rid = disposition['failed_run']
            inspection = obj(B.evo.RUNS / rid / 'inspection.json')
            raw = read(B.evo.RUNS / rid / 'output.txt')
            assert inspection['read_complete'] and inspection['hard_constraints_ok'] is False
            assert inspection['output_sha256'] == disposition['output_sha256'] == B.digest(raw)
            md += [f"| {tag} / {candidate['name']} | 未进入盲比 | 未测 | 未测 | 硬约束归档：{link(disposition_path, '原文证据')} |"]
            continue
        applied = folder / f'{tag}_applied.json'
        if not applied.exists():
            md += [f"| {tag} / {candidate['name']} | 未进入盲比 | 未测 | 未测 | 生产及逐阶段全文检查尚未完成 |"]
            continue
        obj(applied)
        measured = comparison(tag, manifest['base'])
        n = len(measured['rows'])
        nets = '/'.join(f"{measured['net_sums'][k]:+d}" for k in B.F.DIMENSIONS) if n else '未测'
        if disposition.get('status') == 'archive':
            saved = disposition['quick']
            assert n == saved['complete'] and measured['wins'] == saved['wins']
            assert measured['no_regress'] == saved['no_regress'] and measured['net_sums'] == saved['net_sums']
            decision = f"归档：{link(disposition_path, '完整理由与绑定原票')}"
        else:
            accepted = ROOT / 'runs/_batches/round50_from_r49b' / f'{tag}_acceptance.json'
            if accepted.exists():
                receipt = obj(accepted)
                assert receipt['fair']['pass'] and receipt['floor']['status'] == 'pass'
                decision = f"已正式验收：{link(accepted, '完整记录')}"
            else:
                decision = '候选仍在测量，尚未验收'
        votes = f"{measured['wins']}/{n}、{measured['no_regress']}/{n}" if n else '未测'
        md += [f"| {tag} / {candidate['name']} | {n if n else '未测'} | {votes} | {nets} | {decision} |"]
    md += ['', '未测、未全文核验或与当前正文输入不匹配的票不计作0分。快筛通过后才测原底线，幸存者再补足8票；未验收改动不进入主线。', '']
    return md + followup_search()


def followup_search():
    """Keep later actual trials and their real comparison baselines visible."""
    md = ['', '### 后续独立机制与实际退回', '',
          '| 候选 / 机制 | 实际比较基准 | 已核验票数 | 新版 / 不退步 | 四维净胜总和 | 处置证据 |',
          '|---|---|---:|---:|---|---|']
    entries = []
    for batch in ('round55_current', 'round56_paired', 'round57_a4_checkpoint',
                  'round58_upstream', 'round59_trace_repair', 'round59_target_coupling', 'round59_a4_order',
                  'round61_boundary', 'round62_sample_checkpoint'):
        folder = ROOT / 'runs/_batches' / batch
        path = folder / 'candidates.json'
        if path.exists():
            manifest = obj(path)
            entries.extend((folder, manifest['base'], c) for c in manifest['candidates'])
    continuation = ROOT / 'runs/_batches/round50_from_r49b/r55restored_manifest.json'
    if continuation.exists():
        manifest = obj(continuation)
        entries.append((ROOT / 'runs/_batches/round55_current', manifest['base'],
                        {'tag': manifest['target'], 'name': 'RepairRestore 原作者回补'}))
    for folder, base, candidate in entries:
        tag = candidate['tag']
        disposition = next((p for p in (folder / f'{tag}_final_disposition.json',
                                       folder / f'{tag}_disposition.json',
                                       folder / f'{tag}_first_disposition.json') if p.exists()), None)
        measured = (comparison(tag, base) if all((B.V.OUT / f'{w}_{tag}.json').exists() for w in B.F.WORKS)
                    else {'rows': [], 'net_sums': None, 'wins': 0, 'no_regress': 0})
        n = len(measured['rows'])
        nets = '/'.join(f"{measured['net_sums'][k]:+d}" for k in B.F.DIMENSIONS) if n else '未测'
        votes = f"{measured['wins']}/{n}、{measured['no_regress']}/{n}" if n else '未测'
        if disposition:
            state = obj(disposition)
            decision = f"{state['status']}：{link(disposition, '完整原始处置')}"
        elif continuation.exists() and manifest.get('revised') == tag:
            decision = f"按原作者继续为 {manifest['target']}：{link(continuation, '实际完整反馈及回补输入')}"
        else:
            decision = '生产或评审待完成，尚未验收'
        md.append(f"| {tag} / {candidate['name']} | {base} | {n} | {votes} | {nets} | {decision} |")
    md += ['', 'qu为上游改法的同层检查点；该处通过仍须重跑受影响的后续节点，再对实际当时主线验收。'
           '表内每行保留实际比较基准，不把检查点票当作最终主线票，不把父版本票数相加。', '']
    return md


def build(tag, base, output, convergence=None):
    SOURCES.clear()
    read(Path(__file__))
    products = {w: {t: graph(w, t) for t in (base, tag)} for w in B.F.WORKS}
    accepted_file = ROOT / 'runs/_batches/round50_from_r49b' / f'{tag}_acceptance.json'
    accepted = obj(accepted_file)
    assert accepted['tag'] == tag and accepted['fair']['pass'] and accepted['floor']['status'] == 'pass'
    for w in B.F.WORKS:
        assert accepted['integrity'][w]['source_sha256'] == B.digest((B.V.OUT / f'{w}_{tag}.json').read_text(encoding='utf-8'))
    final = False
    if convergence:
        audit = obj(convergence)
        assert audit['status'] == 'verified' and audit['tag'] == tag and audit['base'] == base
        assert audit.get('source_hashes') and audit.get('requirements'), 'A statement alone is not a convergence audit'
        for path, expected in audit['source_hashes'].items():
            assert B.digest(read(ROOT / path)) == expected, f'Stale convergence evidence: {path}'
        assert all(r.get('status') == 'proven' and r.get('evidence') for r in audit['requirements'])
        final = True
    direct = comparison(tag, base)
    chain = lineage(tag, base)
    title = '最终版本' if final else '当前已验收版本（阶段性对比）'
    md = ['<!-- Generated by build_version_comparison.py; do not hand edit. -->',
          f'# {title}：{tag} vs {base}', '',
          f'版本：`{tag}`；固定比较起点：`{base}`。', '',
          ('收敛状态：有逐项验证的收敛审计，见文末。' if final else '收敛状态：尚未证明，迭代继续；这份文件记录当前已验收版本。'), '',
          '本文件由脚本从两版正文、模型原始返回、冻结评审输入和验收记录生成；没有手选示例。正文差异逐段完整列出，引用与关系标签另列。', '',
          '迭代中的成品验收跟随当时最新已验收主线，接纳后推进基准；中间步骤只与当前流程的同位置产物快筛。本文件的固定起点只用于最终对照，不替代滚动的验收基准。', '',
          f'生成器：{link(Path(__file__))}。本次生成不请求模型，不改正文、珠子、评审或判定线。', '',
          '## 提示词与实际生成链', '',
          '实际产物继承顺序：`' + base + '`' + ''.join(' → `' + s['tag'] + '`' for s in chain) + '。', '']
    for stage in chain:
        md += [f"- `{stage['base']} → {stage['tag']}`：{link(stage['receipt'], '机械套用记录')}。"]
        for work, source in stage['sources'].items():
            md += [f"  {work}：{link(source['prompt'], '完整实发输入')} · {link(source['output'], '模型完整返回')}。"]
    templates = ROOT / 'DAG/prompts/N05e_写后修订'
    for name in ('模板.txt', '回补模板.txt'):
        path = templates / name
        md += ['', '<details>', f'<summary>N05e 写后修订通用提示词原文：{name}</summary>', '', '```text', read(path), '```', '', '</details>']
    for stage in chain:
        if stage['receipt'].parent.name != 'round54_broader':
            continue
        manifest = obj(stage['receipt'].parent / 'candidates.json')
        candidate = next(c for c in manifest['candidates'] if c['tag'] == stage['tag'])
        for step in candidate['steps']:
            text = read(ROOT / step['path'])
            assert B.digest(text) == step['sha256']
            md += ['', '<details>', f"<summary>{stage['tag']} 通用提示词原文：{step['id']}</summary>", '', '```text', text, '```', '', '</details>']
    md += ['', '## 直接比较的测量', '', f"本节只比较 `{tag}` 与 `{base}`。完整收取且已全文核验、与当前两版输入逐字匹配：{len(direct['rows'])}/8 票。", '']
    if direct['rows']:
        md += ['| 整体选当前版 | 不退步 | 单独成立净胜总和 | 不啰嗦净胜总和 | 人话净胜总和 | 接珠子净胜总和 |', '|---:|---:|---:|---:|---:|---:|',
               f"| {direct['wins']}/{len(direct['rows'])} | {direct['no_regress']}/{len(direct['rows'])} | " + ' | '.join(f"{direct['net_sums'][k]:+d}" for k in B.F.DIMENSIONS) + ' |', '',
               '净胜总和是逐票“当前版赢的段数−起点版赢的段数”相加，不是提升百分比。少于8票时只显示部分测量，不作正式验收结论。', '',
               '| 作品 | 评委 | 当前版座位 | 选当前版 | 不退步 | 单独 / 简洁 / 人话 / 覆盖 | 原始返回 |', '|---|---|---|---|---|---|---|']
        for row in direct['rows']:
            md += [f"| {row['w']} | {row['j']} | {row['seat']} | {'是' if row['new_win'] else '否'} | {'是' if row['no_regress'] else '否'} | " + '/'.join(f"{row['net'][k]:+d}" for k in B.F.DIMENSIONS) + f" | {link(B.evo.RUNS / row['rid'] / 'output.txt', '原文')} |"]
    if direct['pending']:
        md += ['', '未纳入的票：', ''] + ['- ' + x for x in direct['pending']]
    md += ['', f"当前版正式验收的实际基准是 `{accepted['base']}`，验收时间 {accepted['accepted_at']}；{link(accepted_file, '完整验收记录')}。", '',
           '## 原覆盖与单独读底线', '',
           '| 作品 / 评委 | 起点说清珠子数 | 当前说清珠子数 | 起点单独成立段 | 当前单独成立段 |', '|---|---:|---:|---:|---:|']
    for w in B.F.WORKS:
        for judge in B.F.JUDGES:
            numbers = []
            for prefix in ('cov2', 'al2'):
                for t in (base, tag):
                    rid = f'{prefix}_{w}_{judge}_{t}'
                    if not bound(rid):
                        numbers.append('未完整核验')
                    elif prefix == 'cov2':
                        numbers.append(str(sum(B.F.verdict.cov_secs(w, judge, t).values())))
                    else:
                        numbers.append(str(B.F.verdict.alone_count(w, judge, t)))
            md += [f'| {w} / {judge} | ' + ' | '.join(numbers) + ' |']
    floor = B.F.floor_state(tag, base)
    md += ['', '原逐段底线计算结果：`' + floor['status'] + '`。覆盖按同段两位评委是否均下降至少2颗判断，单独读按原成立段数门槛判断；全曲总数不代替逐段判断。', '']
    if len(direct['rows']) == 8 and not direct['pending']:
        direct_pass = (direct['wins'] >= 6 and direct['no_regress'] >= 6
                       and all(direct['net_sums'][k] >= 0 for k in ('alone', 'lean', 'plain'))
                       and floor['status'] == 'pass')
        md += [f"对固定起点 `{base}` 的这组直接八票，按原完整门槛计算：**{'通过' if direct_pass else '未通过'}**。",
               '门槛同时要求至少6票选当前版、至少6票不退步，单独成立/简洁/人话净胜非负，以及原逐段底线通过。', '']
        if not direct_pass:
            md += [f"对父版本 `{accepted['base']}` 的验收仍保留原记录；它不能替代这次对 `{base}` 的直接结果，也不能证明相对起点是无损提升。", '']
    for name in ('r50progress1rr_coverage_citation_audit.json',):
        path = ROOT / 'runs/_batches/round50_from_r49b' / name
        if tag == 'r50progress1rr' and path.exists():
            read(path)
            md += [f'覆盖评审的引用限制另见 {link(path, "逐项误引审计")}。', '']
    md += ['## 全部正文与元数据差异', '', '| 作品 | 起点字数 / 条数 | 当前字数 / 条数 | 正文变化段 | 仅引用或关系变化段 |', '|---|---:|---:|---|---|']
    changes = {}
    for w in B.F.WORKS:
        a, b = products[w][base], products[w][tag]
        assert a['center'] == b['center']
        assert [(s['sec'], s['bars']) for s in a['segments']] == [(s['sec'], s['bars']) for s in b['segments']]
        body, meta = [], []
        for old, new in zip(a['segments'], b['segments']):
            if [i['text'] for i in old['items']] != [i['text'] for i in new['items']]:
                body.append(old['sec'])
            elif old['relation'] != new['relation'] or [(i['id'], i.get('cite', [])) for i in old['items']] != [(i['id'], i.get('cite', [])) for i in new['items']]:
                meta.append(old['sec'])
        changes[w] = {'body': body, 'metadata_only': meta}
        x, y = stats(a), stats(b)
        md += [f"| {w} | {x['chars']} / {x['items']} | {y['chars']} / {y['items']} | {', '.join(body) or '无'} | {', '.join(meta) or '无'} |"]
    for w in B.F.WORKS:
        md += ['', f'### {w}', '', f"Center：{products[w][tag]['center']}", '']
        for old, new in zip(products[w][base]['segments'], products[w][tag]['segments']):
            if old['sec'] not in changes[w]['body'] + changes[w]['metadata_only']:
                continue
            md += [f"#### {old['sec']}｜{old['bars']} 小节", '', f'**{base} 原文**', ''] + segment_lines(old)
            md += ['', f'**{tag} 原文**', ''] + segment_lines(new) + ['']
        md += ['<details>', '<summary>完整逐行差异（含编号、引用和关系）</summary>', '', '```diff']
        a = B.V.view(products[w][base], ids=True).splitlines()
        b = B.V.view(products[w][tag], ids=True).splitlines()
        md += list(difflib.unified_diff(a, b, fromfile=base, tofile=tag, lineterm='')) + ['```', '', '</details>', '']
    md += ['## 完整开放评审的现状', '', '下表逐份读取当前版已完成、已核验的评审，保留原评级和位置；有意见不等于已解决，意见是否符合标准仍看原文及输入范围审计。', '', '| 原始评审 | 等级 | 维度 | 位置 |', '|---|---|---|---|']
    for w in B.F.WORKS:
        for judge in ('g6', 'g56', 'gem'):
            for k in ((1,) if judge == 'gem' else (1, 2)):
                rid = f'eo2_{w}_{tag}_{judge}_r{k}'
                if not bound(rid):
                    md += [f'| {rid} | 未完整核验 | — | — |']
                    continue
                d = B.V.parse(rid)
                for issue in d.get('problems', []):
                    clean = lambda v: str(v).replace('|', '\\|').replace('\n', ' ')
                    md += [f"| {link(B.evo.RUNS / rid / 'output.txt', rid)} | {clean(issue.get('severity', '未标'))} | {clean(issue.get('goal', '未标'))} | {clean(issue.get('where', '未标'))} |"]
    scope = ROOT / 'runs/_batches/round52_current/open_input_scope_audit.json'
    if scope.exists():
        read(scope)
        md += ['', f'开放评审输入与交付珠子措辞的范围核对：{link(scope)}。']
    for collected in sorted((ROOT / 'runs/_batches').glob('i14_after_r*/collection_result.json')):
        collection = obj(collected)
        rows = [r for r in collection.get('review_slots', []) if f'_{tag}_' in r['rid']]
        if not rows:
            continue
        md += ['', f'### 后续原 I01 组：{collected.parent.name}', '',
               '这组使用原评审提示词。原评级、轻微项、相反判断均保留；是否新增标准缺点，另看具体匹配与反证审计。', '',
               '| 完整原始评审 | 原等级 | 维度 | 具体位置 |', '|---|---|---|---|']
        for row in rows:
            rid = row['rid']
            assert bound(rid) and row['output_sha256'] == B.digest(B.evo.output(rid))
            assert B.digest(read(B.evo.RUNS / rid / 'prepared_input.txt')) == row['input_sha256']
            for issue in B.V.parse(rid)['problems']:
                clean = lambda v: str(v).replace('|', '\\|').replace('\n', ' ')
                md += [f"| {link(B.evo.RUNS / rid / 'output.txt', rid)} | {clean(issue['severity'])} | {clean(issue['goal'])} | {clean(issue['where'])} |"]
        md += ['']
        for name in ('audit_scope.json', 'assessment.json', 'specific_matches.json',
                     'specific_subfinding_resolution.json', 'final_i14_assessment.json'):
            path = collected.parent / name
            if path.exists():
                read(path)
                md += [f'- {link(path)}']
    adviser_close = ROOT / 'runs/_batches/round64_diagnosis/final_disposition.json'
    if adviser_close.exists():
        closure = obj(adviser_close)
        if closure['tag'] == tag:
            md += ['', f"最新 I02 原三顾问完整读/绑定后均无独立新候选：{link(adviser_close)}。这只结束本次搜索，不证明旧问题全部解决或当前版为全局最优。"]
    md += [''] + broader_search() + ['', '## 成品与复现', '']
    for w in B.F.WORKS:
        matches = list(ROOT.glob(f'deliver_*_{tag}/{w}_线与珠子_{tag}.md'))
        assert len(matches) == 1
        read(matches[0])
        md += [f'- {link(matches[0])}']
    if final:
        md += [f'- 收敛审计：{link(convergence)}']
    command = f'python build_version_comparison.py {tag} --base {base}'
    if convergence:
        command += f' --convergence "{Path(convergence).relative_to(ROOT)}"'
    md += ['', '复现命令：', '', '```powershell', command, '```', '']
    content = '\n'.join(md)
    output = Path(output)
    if output.exists() and not output.read_text(encoding='utf-8').startswith('<!-- Generated by build_version_comparison.py;'):
        backup = ROOT / 'runs/_reports/manual_vs_r49b_before_script.md'
        B.write_frozen(backup, output.read_text(encoding='utf-8'))
    output.write_bytes(content.encode('utf-8'))
    proof = {'generator': 'build_version_comparison.py', 'tag': tag, 'base': base, 'phase': 'final' if final else 'interim',
             'report_sha256': B.digest(content), 'source_text_sha256': dict(sorted(SOURCES.items())),
             'changes': changes, 'comparison': direct, 'floor': floor,
             'all_changed_sections_included': True, 'model_calls': 0, 'product_mutations': 0}
    report_receipt = output.with_suffix('.receipt.json')
    report_receipt.write_bytes(B.json_text(proof).encode('utf-8'))
    print(B.json_text({'report': str(output), 'sha256': proof['report_sha256'], 'phase': proof['phase'], 'changes': changes, 'receipt': str(report_receipt)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tag')
    p.add_argument('--base', default='r49b')
    p.add_argument('--output', type=Path, default=ROOT / '最终版本_vs_r49b.md')
    p.add_argument('--convergence', type=lambda x: Path(x).resolve())
    args = p.parse_args()
    build(args.tag, args.base, args.output, args.convergence)
