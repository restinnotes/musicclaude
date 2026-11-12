"""Read-only source audit; writes only its two deliverables in this audits folder.

No model, network, pool build, old-file mutation, or music-fact adjudication.
Run: python D:/musicclaude/_bead_quality_20261017/audits/audit_source_pool.py
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
import hashlib
import json
import re

ROOT = Path('D:/musicclaude')
Q = ROOT / '_bead_quality_20261017'
AUDIT = Q / 'audits'
OLD = ROOT / '_bead_auto_20261016'
BASE = Q / 'baseline_package'

def readj(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def norm(p):
    return Path(p).read_text(encoding='utf-8')

def link(p, line=None, label=None):
    p = Path(p).as_posix()
    return f'[{label or p}]({p}' + (f':{line}' if line else '') + ')'

ledger = readj(BASE / 'out/A36_LEDGER.json')
unitdoc = readj(BASE / 'out/A36_units.json')
pool = readj(BASE / 'out/A_POOL_MAP_v3.json')
repl = readj(AUDIT / 'REPLACEMENT_UNITS.json')
original = [a for a in ledger['adopted'] if not a['src_id'].startswith('SRC-gpro-')]
excluded = {'SRC-gpt56w-int-1', 'SRC-gpt56w-web-1'}
all_units = {u['uid']: u for d in unitdoc['sources'].values() for u in d['units']}
all_units.update({u['uid']: u for d in repl['sources'].values() for u in d['units']})
all_source_data = dict(unitdoc['sources'], **repl['sources'])
source_paths = {a['src_id']: Path(a['path']) for a in ledger['adopted'] + repl['adopted']}
old_prompts = {sid: norm(BASE / 'STEP4_inputs_v3' / f'STEP4_prompt_{sid}.txt') for sid in pool['segments']}
uidre = re.compile(r'SRC-[A-Za-z0-9-]+-U\d+')

def log_evidence(a, m, meta_path):
    src = a['src_id']
    ev = {'requested_or_runner_model': m.get('model_name') or m.get('model_cli'),
          'server_model_slug': None, 'runner_init_models': [], 'session_or_thread_ids': [],
          'completed_web_search_events': [], 'observed_tool_types': {},
          'identity_limit': 'Local runner declaration; not independent attestation of upstream model weights.'}
    if src.endswith('-r1'):
        ev.update(a['historical_candidate_evidence'])
        ev['identity_limit'] = 'Request and stored server model_slug agree; source/response hash verified. Not a music-fact endorsement.'
        return ev
    if a['kind'] == 'fill' and src != 'SRC-luna-int-3':
        rawpath = OLD / 'research_fill/raw' / (a['job_id'] + '.json')
        raw = readj(rawpath)
        cm = raw.get('metadata', {})
        obs = cm.get('stream_completion', {}).get('bounded_server_observations', {})
        response = raw.get('response', '')
        ev.update(raw_path=str(rawpath), raw_sha256=sha(rawpath.read_bytes()),
                  server_model_slug=cm.get('server_metadata_summary', {}).get('model_slug'),
                  requested_or_runner_model=cm.get('model'), completed=raw.get('completed'),
                  response_matches_source_after_BOM_and_terminal_newline=norm(a['path']).lstrip('\ufeff').rstrip('\r\n') == response.rstrip('\r\n'),
                  session_or_thread_ids=[cm.get('session_handle')],
                  tool_result_observations=obs.get('tool_result_observations', []),
                  tool_message_observation_count=obs.get('tool_message_observation_count'),
                  thinking_effort=cm.get('thinking_effort'),
                  identity_limit='Request/CLI metadata and stored server model_slug agree; opaque model weights are not independently attested.')
        return ev
    if src == 'SRC-luna-int-3':
        rawpath = OLD / 'research_fill/raw/A-int__A_int_v1__luna__op60__f1.jsonl'
        ev['requested_or_runner_model'] = 'gpt-6-luna'
        ev['invocation_evidence_path'] = str(OLD / 'research_fill/run_luna_fill.ps1')
        ev['invocation_evidence_line'] = 12
    else:
        rawpath = meta_path.parent.parent / m['stdout_file']
    ev.update(raw_path=str(rawpath), raw_sha256=sha(rawpath.read_bytes()))
    ids, models, tools = set(), set(), Counter()
    for n, line in enumerate(norm(rawpath).splitlines(), 1):
        try:
            o = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(o, dict):
            continue
        for k in ['conversation_id', 'sessionID', 'thread_id']:
            if o.get(k):
                ids.add(o[k])
        if o.get('init', {}).get('model'):
            models.add(o['init']['model'])
        item, part = o.get('item', {}), o.get('part', {})
        if o.get('type') == 'item.completed' and item.get('type') == 'web_search':
            ev['completed_web_search_events'].append({'line': n, 'query': item.get('query'), 'result_count': len(item.get('results', []))})
            tools['web_search:completed'] += 1
        if o.get('type') == 'tool_use':
            tools[str(part.get('tool')) + ':' + str(part.get('state', {}).get('status'))] += 1
    ev.update(runner_init_models=sorted(models), session_or_thread_ids=sorted(ids), observed_tool_types=dict(tools))
    return ev

def source_record(a):
    src, p = a['src_id'], Path(a['path'])
    d = all_source_data[src]
    raw = p.read_bytes()
    decoded = raw.decode('utf-8')
    txt = norm(p)
    mp = ROOT / a['meta_rel']
    meta = readj(mp)
    evidence = log_evidence(a, meta, mp)
    pf = Path(a['prompt_file'] if src.endswith('-r1') else meta['prompt_file'])
    if not pf.is_absolute():
        pf = mp.parent.parent / pf
    prompt = pf.read_text(encoding='utf-8-sig').rstrip()
    covered = [False] * len(txt)
    audits = []
    for u in d['units']:
        text = u['text']
        start = txt.find(text)
        assert start >= 0, u['uid']
        end = start + len(text)
        covered[start:end] = [True] * len(text)
        title_records = []
        for title in u.get('title_inherited', []):
            j = txt.rfind(title, 0, start)
            assert j >= 0, (u['uid'], title)
            covered[j:j+len(title)] = [True] * len(title)
            title_records.append({'text': title, 'source_line': txt[:j].count('\n') + 1})
        place = pool['units'].get(u['uid'], {'slot': u.get('recommended_slot'), 'ranges': u['ranges']})
        audits.append({'uid': u['uid'], 'chars': len(text), 'text_sha256': sha(text.encode()),
                       'source_start_char_lf': start, 'source_end_char_lf_exclusive': end,
                       'source_line_start': txt[:start].count('\n') + 1,
                       'source_line_end': txt[:end].count('\n') + (int(bool(end) and txt[end-1] != '\n')),
                       'exact_contiguous_after_CRLF_CR_to_LF': True,
                       'exact_contiguous_without_newline_normalization': text in decoded,
                       'kind': u['kind'], 'ranges': u['ranges'], 'head_line': u['head_line'],
                       'title_inherited': title_records,
                       'heading_only': u['kind'] == 'head' and text.strip() == u['head_line'],
                       'baseline_placement': place})
    notes = []
    if src in excluded:
        notes.append('Excluded: actual declared model is gpt-5.6-sol#xhigh (web, mimicgate); gpt56w is a misleading family key.')
    if src == 'SRC-luna-int-3':
        notes.append('Keep as authorized quality-pool source with route warning: gpt-6-luna requested, seven completed web_search events contradict tool-free/noweb. Do not count as matched offline replicate.')
    if src in ['SRC-muse-int-2', 'SRC-muse-int-3']:
        notes.append('Original preamble assumes 138 measures; current pool fixes 116. Removing the preamble does not validate remaining numeric alignment.')
    if src == 'SRC-gflash-web-3':
        notes.append('Same web prompt as rounds 1/2, but raw tool event format is OpenCode-style rather than earlier init/ndjson; harness condition differs.')
    if a['kind'] == 'historical' and not src.endswith('-r1'):
        notes.append('Old ledger chars is file byte count, not Unicode character count.')
    return dict(a, actual_sha256=sha(raw), sha_matches_ledger=sha(raw) == a['sha256'],
                actual_bytes=len(raw), actual_characters_lf=len(txt), metadata_path=str(mp),
                prompt_path=str(pf), prompt_normalized_sha256=sha(prompt.encode()),
                prompt_normalization='UTF-8-sig decode; CRLF/CR -> LF; rstrip trailing whitespace',
                identity_evidence=evidence, eligible_identity_pool=src not in excluded,
                same_offline_condition_as_other_luna_int=False if src == 'SRC-luna-int-3' else None,
                audit_notes=notes, units=audits,
                nonwhitespace_characters_uncovered_after_inherited_titles=sum(not ok and not c.isspace() for c, ok in zip(txt, covered)))

baseline_records = [source_record(a) for a in original]
replacement_records = [source_record(a) for a in repl['adopted']]
formal = [a for a in baseline_records if a['src_id'] not in excluded] + replacement_records
formal_ids = {a['src_id'] for a in formal}
formal_unit_ids = {u['uid'] for a in formal for u in a['units']}
assert len(formal) == 30 and len(formal_unit_ids) == 353
assert len({a['actual_sha256'] for a in formal}) == 30
assert all(a['sha_matches_ledger'] for a in baseline_records + replacement_records)
assert all(a['nonwhitespace_characters_uncovered_after_inherited_titles'] == 0 for a in baseline_records + replacement_records)

segments = {}
references = {}
for sid, pd in pool['segments'].items():
    old_prompt = old_prompts[sid]
    wide = re.findall(r'\[(SRC-[^｜\]]+)｜[^\n]*WIDE跨段条', old_prompt)
    entries = [e['uid'] for e in pd['entries']]
    beadpath = BASE / 'beads' / f'STEP4_{sid}.md'
    bead = norm(beadpath)
    refs = sorted(set(uidre.findall(bead)))
    references[sid] = {'path': str(beadpath), 'mentioned_uids': refs,
                       'nonexistent_uids': sorted(set(refs) - set(all_units)),
                       'outside_segment_map': sorted(set(refs) - set(entries)),
                       'wide_header_only_mentions': sorted(set(refs) & set(wide)),
                       'now_excluded_identity_mentions': [x for x in refs if x.rsplit('-U', 1)[0] in excluded or x.startswith('SRC-gpro-')],
                       'mapped_but_unmentioned': sorted(set(entries) - set(refs)),
                       'warning': 'Mentions include retention, rejection and risk notes. Not every mentioned UID is an adopted reader-text citation.'}
    segments[sid] = {'original_36_source_unit_count': len(entries), 'original_wide_header_only_uids': wide,
                     'wide_header_only_from_audited_original_30': [x for x in wide if not x.startswith('SRC-gpro-')],
                     'old_full_body_count': sum(all_units[x]['text'].rstrip() in old_prompt for x in entries),
                     'original_global_units_not_supplied': len(pool['global'])}

livepath = Q / 'sources/SOURCE_MANIFEST.json'
live = readj(livepath)
live_ids = {a['src_id'] for a in live['sources']}
live_check = {'manifest_path': str(livepath), 'manifest_sha256': sha(livepath.read_bytes()),
              'source_count': len(live['sources']), 'source_ids_match_audited_formal30': live_ids == formal_ids,
              'hash_checks': [], 'segment_checks': {}}
for a in live['sources']:
    p = Path(a['path'])
    archive = Q / a['archive']
    live_check['hash_checks'].append({'src_id': a['src_id'], 'original_sha256': sha(p.read_bytes()),
                                     'manifest_hash_matches': sha(p.read_bytes()) == a['actual_sha256'],
                                     'archive_byte_equal_original': archive.read_bytes() == p.read_bytes()})
index = readj(Q / 'pools/POOL_INDEX.json')
for sid, v in index.items():
    p = Q / 'pools' / f'{sid}_FULL.txt'
    text = norm(p)
    ids = [x['uid'] for x in v['units']]
    missing = [uid for uid in ids if all_units[uid]['text'].rstrip() not in text]
    missing_titles = [{'uid': uid, 'title': title} for uid in ids for title in all_units[uid].get('title_inherited', []) if title not in text]
    live_check['segment_checks'][sid] = {'path': str(p), 'sha256': sha(p.read_bytes()), 'bytes': len(p.read_bytes()),
                                        'units': len(ids), 'missing_unit_bodies': missing,
                                        'unknown_or_excluded_uids': sorted(set(uidre.findall(text)) - formal_unit_ids),
                                        'missing_inherited_titles': missing_titles}

summary = {'formal_source_count': len(formal), 'formal_units': len(formal_unit_ids),
           'baseline_audited_source_count': len(baseline_records), 'baseline_audited_units': sum(len(a['units']) for a in baseline_records),
           'baseline_units_contiguous_after_newline_normalization': sum(u['exact_contiguous_after_CRLF_CR_to_LF'] for a in baseline_records for u in a['units']),
           'baseline_units_contiguous_without_newline_normalization': sum(u['exact_contiguous_without_newline_normalization'] for a in baseline_records for u in a['units']),
           'baseline_global_all36': len(pool['global']),
           'baseline_global_original30': sum(not e['src'].startswith('SRC-gpro-') for e in pool['global']),
           'formal_global_count': sum(e['src'] in formal_ids for e in pool['global']) + len(repl['global_uids']),
           'baseline_title_only_shells_retained_as_inherited': sum(len(u['title_inherited']) for a in baseline_records for u in a['units']),
           'baseline_remaining_heading_only_units': sum(u['heading_only'] for a in baseline_records for u in a['units']),
           'baseline_nonexistent_uid_mentions': sum(len(v['nonexistent_uids']) for v in references.values()),
           'duplicate_formal_output_hashes': 0,
           'old_package_files_identical': {f: (BASE/'out'/f).read_bytes() == (OLD/'out'/f).read_bytes() for f in ['A36_LEDGER.md','A36_LEDGER.json','A36_units.json','A_POOL_MAP_v3.json']}}
manifest = {'schema_version': 'source-pool-audit/1', 'audited_at_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'Formal30 provenance manifest plus baseline30 fidelity audit. Not a replacement Pool.',
            'summary': summary, 'sources': formal,
            'excluded_audited_sources': [a for a in baseline_records if a['src_id'] in excluded],
            'baseline_prompt_delivery': segments, 'baseline_uid_mentions': references,
            'live_formal30_validation': live_check,
            'replacement_index_path': str(AUDIT/'REPLACEMENT_UNITS.json'),
            'replacement_evidence_path': str(AUDIT/'REPLACEMENT_CANDIDATES.json'),
            'scope_exclusions': ['GPro identity/factual audit', 'S13 music-fact adjudication', 'V2A production use', 'Any new model sampling']}
(AUDIT/'SOURCE_POOL_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

def source_quote(uid, quote):
    src = uid.rsplit('-U', 1)[0]
    p = source_paths[src]
    txt = norm(p)
    assert quote in all_units[uid]['text'], (uid, quote)
    i = txt.index(quote)
    return f'`{uid}`；{link(p, txt[:i].count(chr(10))+1)}\n\n> ' + quote.replace('\n','\n> ') + '\n'

def bead_quote(sid, quote):
    p = BASE/'beads'/f'STEP4_{sid}.md'
    txt = norm(p)
    reader = txt[txt.index('## ②'):]
    assert quote in reader, (sid, quote)
    i = txt.index(quote, txt.index('## ②'))
    return f'旧读者正文：{link(p, txt[:i].count(chr(10))+1)}\n\n> ' + quote.replace('\n','\n> ') + '\n'

report = [f'''# SOURCE / Pool 保真审计

审计时间：{manifest['audited_at_utc']}。根目录：`D:\\musicclaude`。只读原件、旧构建代码和新 manifest；本次仅在 `_bead_quality_20261017/audits/` 写交付文件。未调用模型、未访问网络、未生成珠子、未修改旧文件或生产 Pool。S13 只做 UID 与传输完整性的机械检查，不重复其音乐事实核查。

**结论：正式来源可以冻结为真实标签证据支持的 30 份。** 原名义 30 份含两份 Sol，已明确排除；在 safechain 的 10 月 11 日旧任务目录找到两份真实 `gpt-5-6-thinking` 同提示输出，主 agent 已采用为 `SRC-gpt56w-int-r1` / `SRC-gpt56w-web-r1`。这不是新增采样。先前按 28 份运行的 pilot 应继续标作 pilot28，其两路同 Pool 的对照关系不变。

这里的“身份支持”按证据层级记录：请求配置、运行器初始化、服务端返回标签分别保存；不将本地别名当作对上游权重的独立鉴定。**Luna-int 第三份实际联网，30 份不等于每个组都有三次严格同条件离线/联网样本。**

## 1. 最终交付与主 agent 使用方式

- `SOURCE_POOL_MANIFEST.json` 的 `sources` 恰好 30 条正式来源；另有 `excluded_audited_sources` 保留两条已剔除 Sol 的审计证据，不可混算。
- 每条包含原始绝对路径、完整 SHA256、真实字符/字节数、原元数据、prompt 规范化 SHA、模型与工具证据，以及每个 UID 的原文偏移、行号、范围、文本 SHA、继承标题。
- `REPLACEMENT_UNITS.json` 顶层 `adopted` 为 ledger 结构元数据，`sources` 与 A36 的单元结构兼容；两份各 12 个连续原文段，24 段串接可精确还原原文件。两份各 U01、U12 为前言/整曲总结，单列 GLOBAL；不从总结正文里的小节号推导局部范围。
- 未重写 Pool。下面的旧 Pool 问题针对冻结包；新 FULL 的修复状态以本次 `live_formal30_validation` 快照为准，不按 `sources/` 目录文件总数判断。

## 2. 身份纠错与历史替补

`SRC-gpt56w-int-1` 和 `SRC-gpt56w-web-1` 的原 meta 逐字为 `"model_name": "gpt-5.6-sol#xhigh (web, mimicgate)"`，`stdin_mode` 为 `mg_file`。它们的 `gpt56w` 只是旧 key，不是 5.6 Thinking 身份。旧 ledger 的“排除旧 Sol”与实际采用存在矛盾。当前正式名单必须保留排除记录，不能只改模型显示名。
''']
for src in ['SRC-gpt56w-int-1','SRC-gpt56w-web-1']:
    a = next(a for a in baseline_records if a['src_id']==src)
    report.append(f'- `{src}`：原件 {link(a["path"])}；元数据 {link(a["metadata_path"])}；SHA `{a["actual_sha256"]}`。')
report.append('\n已核实的替补（使用新 SRC，旧 Sol UID 不复用）：\n')
for a in replacement_records:
    e = a['identity_evidence']
    report.append(f'- `{a["src_id"]}`：{link(a["path"])}，{a["chars"]} 字；SHA `{a["actual_sha256"]}`。请求/服务端均 `gpt-5-6-thinking`，`max`；完成记录、终端消息和 response SHA 均通过。prompt 规范化 SHA `{a["prompt_normalized_sha256"]}`，与现用 {a["prompt_version"]} 完全一致。工具消息观察数 {e["tool_message_observation_count"]}；int 为 0，web 实际观察到 `web.run`。详见同目录 `started.json`、`result.json`。')
report.append('''
替补来自 10 月 11 日原任务存档，不在 `music_work_since_1008v3_20261009` 的 A36 inventory 采集范围内，因此只查旧 A36 inventory 会错误地得出“无替补”。此前发现的 run30 不是本次替补：s1 `failed`、0 字；s2 `suspect_degraded`，且 provider_meta 记有 web_citations=2、search_result_groups=6，不应作为同条件 int 填数。最终 30 份原件 SHA 均不同，两份替补也不同于已有四份 5.6 Thinking fill。

## 3. Luna 第三份与同条件限制

`research_fill/run_luna_fill.ps1` 第 12 行显式 `-m gpt-6-luna`，所以不能因为 ledger 没有 model_cli 就把它认成 GPT-6 Thinking。该命令没有禁止内建 web_search；raw 第 6 行 assistant_message 为：

> 我会先核对乐谱的小节编号，再按听感把作品分成几个有依据的阶段来讲；情绪描述会明确当作聆听中的解释，而不是唯一标准答案。

同一 raw 在 8、11、14、17、20、24、27 行出现七条 `item.completed` / `web_search`，前五条有结果，后两条结果为空。第 8 行 query 为 `Chopin Barcarolle Op 60 score measure numbers pdf 112 bars ...`。因此“tool-free / noweb”描述不真实；模型命令身份可证，后端原始模型标识未在这份 JSONL 中返回。作为用户批准的质量材料可留用，作为第三次离线重复不成立。前两份 Luna-int raw 未观察到 web_search；Luna-web 三份分别有 10、15、12 次完成的 web_search。
''')
report.append(link(OLD/'research_fill/run_luna_fill.ps1',12) + '；' + link(OLD/'research_fill/raw/A-int__A_int_v1__luna__op60__f1.jsonl',8) + '\n')
report.append('''
同条件还应分开记录以下变化：

- 历史 gflash/muse/luna A-int prompt 为 273 字，规范化 SHA 前缀 `1c769a248faa`；GPT-w A-int 为 289 字、`c4c4f98386ab`，额外带有“回答时请不要进行联网搜索。”。相同 `A_int_v1` 名称不代表逐字同 prompt。Luna fill 仍用 273 字版本。
- A-web 同提示规范化 SHA 前缀为 `8066a8b43e47`。gflash-web 前两轮为 init/ndjson 日志，第三轮为 OpenCode 风格工具日志，不能称同一 harness 的严格复测。
- gflash-int 三份各记录 attempts=2；gflash-web 第二份 attempts=3。独立结果/独立会话可核实，不代表无重试随机样本。
- Muse-int raw 有 read/bash/glob 等失败工具请求；不能凭“int”声称模型从未尝试工具。GPT-w int fill 的 bounded observations 出现 unknown 工具事件，未足以证明为联网，也不应据此宣称已强制完全无工具。
- Muse 及部分历史来源只有 meta 的模型路由声明；gflash 的五份 raw init 可再次核对 `gemini-3.8-flash-high`；GPT-w fill 与两份替补另有 server model_slug。manifest 区分这些证据强弱，不伪装成等强度的身份鉴定。

## 4. 连续原文、截断和计数
''')
report.append(f'''冻结包与 `_bead_auto_20261016/out/` 的 ledger、units、v3 map 逐字节相同。原名义 30 份的原件 SHA 全部匹配 ledger，全部 **{summary['baseline_audited_units']} 个 unit** 经 CRLF/CR→LF 标准换行解码后均为连续原文子串。严格不做换行规范化时仅 **{summary['baseline_units_contiguous_without_newline_normalization']} / 354** 命中；其余为原文件 CRLF 与 JSON LF 的差异，不能把“逐字”误报成“逐字节”。manifest 同时提供两种结果。

将 unit 正文与 `title_inherited` 对回原文件，**未覆盖的非空白字符为 0**，没有找到 unitize 把正文重写、定长剪尾或漏掉整个后半段的证据。13 个无范围标题壳已折入后继单元的 `title_inherited`，UID 出现跳号是正常的；例如 gflash-int-3 的 U03/U05/U07/U09/U11/U13 对应六个阶段，不是只留了三段。`n_units` 是折叠前计数，数组长度/`n_units_real` 是折叠后计数。

仍有 **{summary['baseline_remaining_heading_only_units']} 个带范围的 Markdown 标题单元**没有自有正文，因为 title-only pass 只折叠“没有范围”的标题。例：`SRC-gpt6w-web-1-U09` 只是“mm.40–61…心事”的标题，实质段落在 U10；`SRC-gpt6w-web-3-U02` 也是标题。不能用这些标题当新增证据票；单行 bullet 可能本身含完整叙述，不能把所有 `text == head_line` 都误判为空标题。

旧 ledger 的 19 份 historical “chars”实际是文件字节数，11 份 fill 则为输出字符串长度；例如 gflash-int-1 为 6937 字节、2714 个 LF 文本字符。该列混用单位，不宜用于模型表达长度比较。最终 manifest 已分别给 bytes 与 characters。

正式 30 份包括原 28 份的 329 个 unit，加替补 24 个，共 **353 个 unit**；被剔除 Sol 与 V2A 均不计入。

## 5. Pool 收纳与假引用判别

旧 `build_step4_v3.py` 正文实现（不是头部注释）在超过字节预算时把 WIDE 门槛从 4 降为 3；只在第一个覆盖段放全文，后续段仅列 UID/模型/范围，并禁止引用缺失正文。

| 旧段 | map 条目 | 真正可见正文 | WIDE 头行 |
|---|---:|---:|---:|
| S02 | {segments['S02']['original_36_source_unit_count']} | {segments['S02']['old_full_body_count']} | {len(segments['S02']['original_wide_header_only_uids'])} |
| S07 | {segments['S07']['original_36_source_unit_count']} | {segments['S07']['old_full_body_count']} | {len(segments['S07']['original_wide_header_only_uids'])} |

S02 的非 GPro 缺正文 UID：{', '.join('`'+s+'`' for s in segments['S02']['wide_header_only_from_audited_original_30'])}。S07 的非 GPro 缺正文 UID：{', '.join('`'+s+'`' for s in segments['S07']['wide_header_only_from_audited_original_30'])}。例如 S07 的 Muse-int-3 U04 有 264 字正文，旧附件只有头行；不能把未读正文当作“模型阅读后主动舍弃”。

GLOBAL 全部 55 条未随旧段输入（原名义 30 份中为 49 条）。提示称“全文见 A_POOL_MAP_v3.json”，但该 map 的 global 只有 UID/ranges/chars 等索引，**没有 text 字段**；真正全文在 A36_units 和原件。旧 `A_POOL_REVIEW.md` 的“GLOBAL 进入每段第五部分”与实际 builder 相矛盾。最终正式 30 来源的 GLOBAL 为 {summary['formal_global_count']} 条，仍应明确它们是否只归档、是否实际输入，不把归档数当阅读覆盖数。

14 个旧珠子的机器提取 UID 均存在：未发现捏造不存在 UID。S02、S07 的提及 UID 也都属于其旧 map。可是 `merge_step4_beads.py` 只检查 ID 存在，不验证本段是否传了正文、是否在当前白名单、更不验证句子被该来源支持。旧内部文本把“保留／舍弃／风险／不可使用”中的 UID 一并抽取为引用，因而**mentions 不是 adopted citations**。尤其当前被排除的 GPro/Sol 在旧珠子有真实 UID，属于不合格来源引用，不能自动洗白为新 30 份的证据，也不能一概说旧作者编造了 UID。

S02 的 map 有 `SRC-muse-int-1-U03` 正文，但旧珠子全文未提及其 UID；S07 的 `SRC-gpt56w-web-3-U06` 也未提及。相反，“不可使用的 WIDE”清单列出的 UID 只是拒用登记。manifest 分开列出 missing / unmentioned / WIDE / now-excluded，避免混算。

## 6. S02：具体表达在哪里被泛化

以下均为现存文件逐字引文；比较的是表达保留，不把源文本的编号、历史陈述视为已核真的事实。
''')

comparisons = [
('S02','SRC-muse-int-1-U03','像靠在船舷上，眼睛看着远处，不敢看太用力，怕把这片刻看碎了。','眼前的一切太珍贵了，怕自己动作稍微大一点，就把它惊醒。','视线、船舷和“不敢看太用力”的具体身体动作，变为通用的动作轻重与怕惊醒。该源 UID 未出现在旧内部账本，不能认定句子直接由此改写；这里只确认本可使用的独特表达没有保留。'),
('S02','SRC-muse-int-2-U03','你想起一段很好的过去，你知道回不去了，但你此刻并不想回去，你只是觉得“有过真好，但有过就意味着没了”。','像忽然翻到一张发黄的旧照片，先感到曾经的暖意，过一会儿，才感到那一点无法重新触及的距离。','原来的“不想回去”与“有过即意味着没了”的矛盾被改成常见的旧照片与距离。原件的 138 小节前提有风险；表达好不等于能不经对齐直接入 S02。'),
('S02','SRC-muse-web-3-U03','第一次是安慰，第二次是犹豫，第三次已经有点疼了。','第一次是：“此刻很好。”\n\n再说一次，已经有一点不舍。\n\n又一次回到那里，仿佛心里多了一句没有说出口的话：“能不能再久一点？”','保留了三次停留的结构，却把安慰→犹豫→疼的不同质地改成幸福→不舍→延长幸福，更统一，也更单一。标题“太幸福了，反而不敢用力”则确实沿用了这份源的好表达，不能说全盘丢失。'),
('S07','SRC-muse-web-2-U04','好不容易幻想出一个温暖的地方，赶紧搬进去，但心里不踏实，总要起来检查门锁。','越珍惜，越不能完全安心；越不能安心，反而越想靠近。','“检查门锁”的强迫性动作和安居失败消失，剩下抽象的珍惜／不安／靠近循环。该 unit 覆盖35–61，须保留范围边界意识。'),
('S07','SRC-gpt56w-int-3-U07','像深夜里一个人已经决定睡觉，却发现脑子开始重新播放白天的一段谈话。你并没有新的事实可想，却不停从另一个角度重新想它。','一个念头说过了，还是觉得不够；似乎安慰了自己，过一会儿又重新想起。','深夜回放谈话、没有新事实仍反刍，是比泛称念头反复更准确的心理过程。旧珠子有相关概念，但削弱了它可辨认的处境。'),
('S07','SRC-gpt56w-web-2-U06','**原来是在想着某个人、某件事；现在却开始沉迷于“自己正在感觉”这件事。**','美好本身开始发烫。','源里有“感受对象→沉迷感受本身”的层次变化；旧文主要变成温度、浓度、热烈程度的增加。这是 S07 最有价值的被泛化维度之一。'),
]
for sid, uid, quote, oldq, comment in comparisons:
    if sid == 'S07' and not any('## 7. S07' in s for s in report):
        report.append('\n## 7. S07：中段的身体处境与二阶感受\n')
    report.append(source_quote(uid, quote))
    report.append(bead_quote(sid, oldq))
    report.append(comment + '\n')
report.append('''
反例也必须记录：S02 的“对方偶尔望你一眼，你心里就已经很满足”直接存在于 `SRC-gpt6w-int-3-U03`；gflash-int-3 U05 的潮湿、倦意、微醺、皮肤触感在旧正文仍有保留。S07 的“语言暂时跟不上感受”明显保留了 `SRC-gpt56w-int-2-U06` 的表达；`SRC-gpt6w-int-2-U05` 的“无法彻底进入对方内心／无法让此刻永远停住”也被近原文保留。因此问题不是一律禁止沿用原句，而是一些鲜明动作、悖论和感受机制被统一成泛泛的“太珍惜，所以害怕”。

S07 的“竞争解释”还混有定位误差：gflash-int-3 U07 把自己标作40–61并写“mm.51开始…dolce sfogato”；Muse-int-3 U04 则把该标记放在45附近，原件前言又假设138小节。这里仅指出它们与其他源的分段定位不一致，不在本审计重做外部事实核查。这样的差异不能直接升级为同一正确乐段的平等审美竞争；应先交给定位核查。旧 S07 已主动拒用其中部分 WIDE，不能反过来指控它引用了没看到的那份正文。

另一个来源性问题：`SRC-gflash-int-1-U11` 原句“我的身体在衰竭，但我的心依然能跳得如此滚烫。”是模型给出的拟人化独白，并非肖邦真实引语。旧 S07 把它列为不进入正文的内容，这一限制是恰当的；不能为保留文采而删掉该来源性质说明。

## 8. 新 formal30 manifest / FULL 快照
''')
report.append(f'本次按 {link(livepath)} 审查，来源数 **{live_check["source_count"]}**，与审计正式 30 ID 集合一致：**{live_check["source_ids_match_audited_formal30"]}**。所有 manifest 哈希和归档副本与原件相等：**{all(x["manifest_hash_matches"] and x["archive_byte_equal_original"] for x in live_check["hash_checks"])}**。不因目录中残留不被引用的排除文件判污染。\n')
report.append('| 段 | 新 FULL 单元数 | 字节 | 缺正文 | 不合格/未知 UID | 缺继承标题 |\n|---|---:|---:|---:|---:|---:|')
for sid in ['S02','S07','S13']:
    v = live_check['segment_checks'][sid]
    report.append(f'| {sid} | {v["units"]} | {v["bytes"]} | {len(v["missing_unit_bodies"])} | {len(v["unknown_or_excluded_uids"])} | {len(v["missing_inherited_titles"])} |')
report.append('\n继承标题是独立字段；早期新 builder 只传 `u[text]`，会漏掉它们。本次以实际文件检查结果为准：缺标题清单逐项保存在 manifest 的 `live_formal30_validation.segment_checks`。不要把单元正文完整误写成“连标题也全量保留”。S13 此处只验文件传输与身份，不评价内容。\n')

report.append('## 9. 独立旧提示词表达对照：V2A Gemini Flash（不进生产 Pool）\n')
report.append('亲读 ledger `kept_and_exclude` 中 run16 的两份 A_orig_V2A 原件。它们没有 A36 UID，以下只用真实路径与原文件行号。选择依据是表达的可感性，不是对传记、谱面、术语位置或历史引语真实性的背书；不以旧提示词质量参照补足正式30，也不参与同版本三轮统计。\n')
v2a = [
('s1','左手那永不停止的摇晃，是水的物理属性，它不在乎人的喜怒哀乐；而右手的歌声却充满了人的脆弱、迟疑与渴望。','把不理会人的水流和人的脆弱放在两个并行声部上，张力来自可感到的不同力量；比笼统“甜蜜又忧伤”有结构。'),
('s2','它既像两个深爱的人靠在一起低语，又像一个疲惫不堪的人在与自己的内心对话。','同一声音保留双人相伴和一个人自语两种方向，用具体动作表达解释差异。'),
('s1','音乐结束了，你依然身处冰凉昏暗的房间里。','从音乐里的空间切回听者所处房间，感官和视角都很明确。只取文学表达参照，不把原件相邻的尾声小节说法带入正式材料。'),
]
v2records = []
for sample, quote, comment in v2a:
    p = ROOT/f'music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__{sample}.md'
    txt = norm(p)
    i = txt.index(quote)
    n = txt[:i].count('\n') + 1
    report.append(f'{link(p,n)}；无 A36 UID。\n\n> {quote}\n\n{comment}\n')
    v2records.append({'path': str(p), 'sha256': sha(p.read_bytes()), 'line': n, 'quote': quote,
                      'role': 'independent_old_prompt_expression_control', 'production_pool': False})
manifest['v2a_expression_controls'] = v2records
manifest['final_audit_disposition'] = {
    'status': 'complete',
    'decision_basis': 'User final instruction after reading this audit',
    'experimental_inputs': 'Keep frozen pilot28 and formal30 model-comparison inputs; do not backfill or overwrite them.',
    'context_repair': 'Owner will create a separate production_context30 revision restoring title_inherited; original experiments stay unchanged.',
    'context_repair_verified_by_this_audit': False,
    'luna_int3': 'Explicitly disclose actual web use; do not count it as a third matched offline replicate; retain under authorized quality-first scope.',
    'new_A_sampling': False,
    'replacement_search': 'Closed; two existing historical Thinking replacements verified and adopted.',
    'v2a': 'Three independent expression controls are sufficient; excluded from production Pool.',
    'remaining_subagent_work': 'None; no bead generation or further search. Main agent owns later editing.'
}

report.append('## 10. 逐来源索引（正式 30 份）\n')
report.append('完整原件/日志/提示路径、SHA、UID offsets 见 JSON。此表便于人工定位；替补与旧 Sol 分开，不暗中覆盖身份。\n')
report.append('| SRC | 原件 | SHA前12 | unit数 | 关键备注 |\n|---|---|---|---:|---|')
for a in formal:
    note = '实际联网；不可计为第三轮离线' if a['src_id']=='SRC-luna-int-3' else ('历史真5.6补位，新UID' if a['src_id'].endswith('-r1') else ('原件假设138小节，位置需复核' if a['src_id'] in ['SRC-muse-int-2','SRC-muse-int-3'] else '原文连续匹配；模型证据层级见JSON'))
    report.append(f'| `{a["src_id"]}` | {link(a["path"],label=Path(a["path"]).name)} | `{a["actual_sha256"][:12]}` | {len(a["units"])} | {note} |')

report.append('''
## 11. 本子任务实际改动文件

仅创建/维护本目录的 `SOURCE_POOL_AUDIT.md`、`SOURCE_POOL_MANIFEST.json`、`REPLACEMENT_CANDIDATES.json`、`REPLACEMENT_UNITS.json`、`audit_source_pool.py`。未改旧文件、未调用模型、未生成珠子、未改 production manifest/Pool。新 Pool 的集成属于主 agent 操作。
''')
report.append('''
## 12. 最终审计限定与处置决定

用户阅读本报告后确认以下边界，本审计据此完成，不继续扩大搜索：

- **实验输入保留冻结。** 已运行的 pilot28 和正式模型比较使用各自冻结的输入；不把后来发现的继承标题补回旧输入，不回写旧实验。两份同 Pool 的 pilot28 对照仍按原条件报告，不事后改称 formal30。
- **上下文修复另立版本。** `title_inherited` 缺失是真实的上下文遗漏。主 agent 将另建 `production_context30` 修复版，保留原实验输入和哈希。本审计只证实原快照存在遗漏，未声称未来修复版已经建立、核验或用于已有实验。
- **Luna 条件如实纠正。** `SRC-luna-int-3` 请求模型为 `gpt-6-luna`，实际发生 web_search；保留为用户允许的质量材料，显式披露采样条件，不能作为第三份同条件离线证据。不为凑严格 int 再调用 A。
- **表达参照止于三个 V2A 原句。** 它们独立于生产 Pool，不补轮次、不进入既有输入。
- **本子任务到此结束。** 两份历史 Thinking 替补及其原文索引已交付；剩余模型返回后的主编辑由主 agent 负责。本子任务不生成珠子、不新增模型调用、不修改生产或实验输入。
''')
(AUDIT/'SOURCE_POOL_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
rendered_report = '\n\n'.join(report) + '\n'
# Markdown tables require adjacent rows, while prose blocks need blank lines.
rendered_report = re.sub(r'(?m)(^\|[^\n]*\|)\n(?:[ \t]*\n)+(?=\|)', r'\1\n', rendered_report)
(AUDIT/'SOURCE_POOL_AUDIT.md').write_text(rendered_report, encoding='utf-8')
print(json.dumps({'summary': summary, 'live_formal30': {k:v for k,v in live_check.items() if k!='hash_checks'},
                  'outputs': ['SOURCE_POOL_AUDIT.md','SOURCE_POOL_MANIFEST.json']}, ensure_ascii=False))
