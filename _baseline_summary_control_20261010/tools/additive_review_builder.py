#!/usr/bin/env python3
"""Additive D/G/F review builder v3 (mechanical, no model calls).

Strict path copies frozen build_repeat_judges.py logic; trial loading reuses
validate_delivery_v2.check_trial_slot + check_source_payload (strict
transport/source, nothing re-implemented).

Writes ONLY into --out-dir, which must be absent/empty (any existing file =
REFUSE, never rewrite):
  <out>/jobs/reviews/<judge>/<id>.txt
  <out>/review_manifest_merged.json       (prompt_file ABSOLUTE everywhere)
  <out>/private/review_mapping_merged_DO_NOT_SHOW_JUDGES.json
  <out>/review_queue_v3.json              (pipeline_v3 tasks schema)
Old 97: rebuilt bytes sha-compared; conflict aborts before any write.
Queue: new strict IDs + --gap-aware-target8 supplements + old missing rows,
only when the results prefix holds NO file of any kind (never blind-resend).
Gap-aware F: frozen template bytes verbatim + factual missingness metadata
(target/available lists, n_valid, original T numbers, missing never SILENCE);
new supplement IDs, protocol_deviation, never strict F.

Usage:
  python3 -I tools/additive_review_builder.py --data-root <frozen> --out-dir <new> [--gap-aware-target8]
"""
import argparse, collections, hashlib, importlib.util, json, re
from pathlib import Path

MODELS = ['gpt6w', 'gpt56w']
TPL = {'D': 'D_BLIND_COMPARISON_v1.txt', 'G': 'G_DIRECT_BLIND_PAIRWISE_v1.txt',
       'F': 'F_E7_SEMANTIC_SATURATION_v1.txt'}
KS = (2, 11, 18, 20, 23)
FIXED_R = (1, 5, 8, 12)
FIXED_N = (5, 8, 12)
GAP_TARGET = 8
GAP_MIN = 2
LIMIT = 65536
F_SHORT = ('action', 'new_screen_items', 'keep_ids', 'retire_ids',
           'final_screen_text', 'editorial_tradeoff')


def parse(s):
    s = s.strip().lstrip('﻿')
    if s.startswith('```'):
        s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s)
    return json.loads(s)


def load_validator(path):
    spec = importlib.util.spec_from_file_location('validate_delivery_v2', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def strict_load(cache, vd, root, cjobs, model, k, r):
    """Verified C draft or None. Strict transport+source via validator."""
    key = (model, k, r)
    if key in cache:
        return cache[key]
    cache[key] = None
    job = cjobs.get(f'C{k:02d}')
    if job is None:
        return None
    try:
        pb = (root / job['model_prompt_paths'][model]).read_bytes()
    except Exception:
        return None
    if hashlib.sha256(pb).hexdigest() != job['input_sha256']:
        return None
    try:
        rec = vd.check_trial_slot(root, job, model, r, pb, True)
    except Exception:
        return None
    if rec.get('final_class') != 'transport_valid_success' or rec.get('source_valid') is not True:
        return None
    try:
        o = parse((root / 'results' / 'trials' / model / f'C{k:02d}' / f'r{r:02d}.txt').read_text(encoding='utf-8'))
        assert o.get('task') == 'C' and o.get('station_k') == k and isinstance(o.get('new_screen_items'), list)
        cache[key] = o
        return o
    except Exception:
        return None


def rep(x):
    keys = ('action', 'keep_ids', 'retire_ids', 'new_screen_items',
            'final_screen_text', 'expand_ids', 'recap_ids', 'editorial_tradeoff')
    return json.dumps({z: x.get(z) for z in keys}, ensure_ascii=False, indent=2)


def has_any_evidence(root, judge, jid):
    """True if results prefix holds ANY file (meta/txt/raw/stderr/attempt*)."""
    d = root / 'results' / 'reviews' / judge
    if not d.is_dir():
        return False
    try:
        return next(d.glob(jid + '.*'), None) is not None
    except Exception:
        return True


def sha_txt(txt):
    return hashlib.sha256((txt.strip() + '\n').encode('utf-8')).hexdigest()


def mk_task(judge, jid, kind, meta, prompt_abs, h, origin):
    num = meta.get('repeat') if kind in ('D', 'G') else meta.get('sample_count')
    t = {'kind': 'review', 'model': judge, 'job_id': jid, 'round': kind,
         'number': num, 'mode': 'new', 'prompt_rel': prompt_abs, 'prompt_hash': h,
         'task_id': f'review:{judge}:{jid}:new',
         'prefix_rel': f'results/reviews/{judge}/{jid}', 'origin': origin}
    if meta.get('protocol') == 'gap_aware_supplement':
        t['target_n'] = meta.get('target_sample_count')
        t['available_rounds'] = meta.get('available_trial_rounds')
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-root', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--validator',
                    default='D:/musicclaude/_baseline_delivery_control_20261010/validate_delivery_v2.py')
    ap.add_argument('--gap-aware-target8', action='store_true')
    a = ap.parse_args()
    root = Path(a.data_root)
    out = Path(a.out_dir)
    if out.exists() and any(p.is_file() for p in out.rglob('*')):
        print(f'REFUSE: out-dir not empty, nothing written: {out}')
        return 2
    vd = load_validator(a.validator)
    manifest = json.loads((root / 'jobs/manifest.json').read_text(encoding='utf-8'))
    plan = json.loads((root / 'jobs/repetition_plan.json').read_text(encoding='utf-8'))
    cjobs = {j['job_id']: j for j in manifest['jobs'] if j['job_id'].startswith('C')}
    tpl = {k: (root / 'prompts' / v).read_bytes().decode('utf-8') for k, v in TPL.items()}
    old_man = json.loads((root / 'jobs/reviews/review_manifest.json').read_text(encoding='utf-8'))['jobs']
    old_ids = {j['job_id']: j for j in old_man}
    pmap = {j['job_id']: j for j in
            json.loads((root / 'private/review_mapping_DO_NOT_SHOW_JUDGES.json').read_text(encoding='utf-8'))['jobs']}
    cache, cand, miss = {}, {}, []
    for k in KS:
        i = json.loads((root / f'inputs/op60/C_k{k:02d}.json').read_text(encoding='utf-8'))
        e = ('【音乐位置（既有研究文字，非独立谱面事实）】\n' + str(i['meta']['section_title']) +
             '\n【屏幕先前状态】\n' + json.dumps(i['screen_before'], ensure_ascii=False, indent=2) +
             '\n【可用当前素材】\n' + json.dumps(i['current_candidates'], ensure_ascii=False, indent=2) + '\n')
        old = (root / f'private/legacy_target_k{k:02d}.txt').read_text(encoding='utf-8').split('\n\n', 1)[1]
        for gen in MODELS:
            judge = 'gpt56w' if gen == 'gpt6w' else 'gpt6w'
            for r in FIXED_R:
                x = strict_load(cache, vd, root, cjobs, gen, k, r)
                if x is None:
                    if r in (8, 12):
                        miss.append(f'D k{k:02d} {gen} r{r:02d}')
                    continue
                new = '\n'.join('- ' + t['text'] for t in x['new_screen_items']) or '(此段没有新增文字)'
                for o in ('AB', 'BA'):
                    aa, bb = (new, old) if o == 'AB' else (old, new)
                    jid = f'D_k{k:02d}_r{r:02d}_gen{gen}_judge{judge}_{o}'
                    cand[jid] = ('D', judge, tpl['D'] + f'\n【站点】k{k:02d}\n' + e +
                                 f'【匿名版本 A】\n{aa}\n【匿名版本 B】\n{bb}\n',
                                 {'k': k, 'repeat': r, 'generating_model': gen,
                                  'new_side': 'A' if o == 'AB' else 'B', 'old_side': 'B' if o == 'AB' else 'A'})
        for r in FIXED_R:
            xx = {m: strict_load(cache, vd, root, cjobs, m, k, r) for m in MODELS}
            if any(v is None for v in xx.values()):
                if r in (8, 12):
                    miss.append(f'G k{k:02d} r{r:02d}')
                continue
            for judge in MODELS:
                for o in ('AB', 'BA'):
                    am = 'gpt6w' if o == 'AB' else 'gpt56w'
                    bm = 'gpt56w' if o == 'AB' else 'gpt6w'
                    jid = f'G_k{k:02d}_r{r:02d}_judge{judge}_{o}'
                    cand[jid] = ('G', judge, tpl['G'] + f'\n【站点】k{k:02d}\n' + e +
                                 '\n【匿名版本 A（含屏幕编辑操作）】\n' + rep(xx[am]) +
                                 '\n【匿名版本 B（含屏幕编辑操作）】\n' + rep(xx[bm]) + '\n',
                                 {'k': k, 'repeat': r, 'A_model': am, 'B_model': bm, 'judge_may_be_self': True})
        for n in FIXED_N:
            for gen in MODELS:
                xs = [strict_load(cache, vd, root, cjobs, gen, k, r) for r in range(1, n + 1)]
                if any(v is None for v in xs):
                    miss.append(f'F k{k:02d} {gen} n{n:02d}')
                    continue
                judge = 'gpt56w' if gen == 'gpt6w' else 'gpt6w'
                rd = [f'【T{t}】\n' + json.dumps({z: ob.get(z) for z in F_SHORT}, ensure_ascii=False, indent=2)
                      for t, ob in enumerate(xs, 1)]
                jid = f'F_k{k:02d}_n{n:02d}_judge{judge}'
                cand[jid] = ('F', judge, tpl['F'] + f'\n【station_k】{k}\n【sample_count】{n}\n' + e +
                             '\n【同一匿名作者在独立会话中的各次输出】\n' + '\n'.join(rd) + '\n',
                             {'k': k, 'sample_count': n, 'generating_model': gen, 'independent_review': True})
    new = {}
    for jid, (kind, judge, txt, meta) in cand.items():
        h = sha_txt(txt)
        if jid in old_ids:
            if h != old_ids[jid]['prompt_sha256']:
                print(f'CONFLICT {jid}: rebuilt bytes differ from frozen manifest; STOP, nothing written')
                return 1
        else:
            new[jid] = (kind, judge, txt, meta, h)
    gap = {}
    if a.gap_aware_target8:
        for k in KS:
            i = json.loads((root / f'inputs/op60/C_k{k:02d}.json').read_text(encoding='utf-8'))
            e = ('【音乐位置（既有研究文字，非独立谱面事实）】\n' + str(i['meta']['section_title']) +
                 '\n【屏幕先前状态】\n' + json.dumps(i['screen_before'], ensure_ascii=False, indent=2) +
                 '\n【可用当前素材】\n' + json.dumps(i['current_candidates'], ensure_ascii=False, indent=2) + '\n')
            for gen in MODELS:
                avail = [r for r in range(1, GAP_TARGET + 1)
                         if strict_load(cache, vd, root, cjobs, gen, k, r) is not None]
                if not (GAP_MIN <= len(avail) < GAP_TARGET):
                    continue
                missing = [r for r in range(1, GAP_TARGET + 1) if r not in avail]
                xs = {r: strict_load(cache, vd, root, cjobs, gen, k, r) for r in avail}
                rd = [f'【T{r}】\n' + json.dumps({z: xs[r].get(z) for z in F_SHORT}, ensure_ascii=False, indent=2)
                      for r in avail]
                judge = 'gpt56w' if gen == 'gpt6w' else 'gpt6w'
                jid = f'F_gapaware_k{k:02d}_target{GAP_TARGET:02d}_available{len(avail):02d}_judge{judge}'
                txt = (tpl['F'] + f'\n【station_k】{k}\n【sample_count】{len(avail)}\n'
                       f'【target_sample_count】{GAP_TARGET}\n'
                       f'【available_trial_rounds】{json.dumps(avail)}\n'
                       f'【missing_trial_rounds】{json.dumps(missing)}\n'
                       '【protocol】gap_aware_supplement_not_strict_F\n' + e +
                       '\n【同一匿名作者在独立会话中的各次输出（T 编号为原始轮次，未重新编号）】\n' +
                       '\n'.join(rd) + '\n'
                       '\n【缺失事实（构建者附加，非评审标准）】\n'
                       f'- target_rounds=1..{GAP_TARGET}；实际可用 n_valid={len(avail)}：{json.dumps(avail)}；'
                       f'缺失轮：{json.dumps(missing)}。\n'
                       '- 缺失轮无任何正文；不得将其视为 SILENCE、空白稿或低质量证据，不得因缺失扣分。\n'
                       '- T 编号为原始轮次号，未重新编号；样本内饱和判断仅限可用稿（样本内 sat 不等于全 8 sat）。\n'
                       '- 本 prompt 为 protocol_deviation 补充审计，不冒充冻结严格 F。\n')
                meta = {'k': k, 'sample_count': len(avail), 'target_sample_count': GAP_TARGET,
                        'available_trial_rounds': avail, 'missing_trial_rounds': missing,
                        'generating_model': gen, 'independent_review': True,
                        'protocol': 'gap_aware_supplement'}
                gap[jid] = ('F', judge, txt, meta, sha_txt(txt))
    rp = out / 'jobs' / 'reviews'
    pp = out / 'private'
    rp.mkdir(parents=True, exist_ok=True)
    pp.mkdir(parents=True, exist_ok=True)
    fwd = lambda p: str(p).replace('\\', '/')
    mrows = [dict(j, prompt_file=fwd(root / j['prompt_file'])) for j in old_man]
    prows = [dict(pmap[j['job_id']], absolute_prompt_file=fwd(root / j['prompt_file'])) for j in old_man]
    tasks = []
    origins = {}
    for jid, (kind, judge, txt, meta, h) in sorted({**new, **gap}.items()):
        content = txt.strip() + '\n'
        if len(content) > LIMIT:
            print(f'SKIP {jid}: exceeds {LIMIT} chars')
            continue
        dest = rp / judge / f'{jid}.txt'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding='utf-8', newline='\n')
        mrows.append({'job_id': jid, 'kind': kind, 'judge_model': judge, 'prompt_file': fwd(dest),
                      'prompt_sha256': h, 'station_k': meta['k'], 'added_by': 'summary_control',
                      'protocol': meta.get('protocol', 'strict_frozen')})
        prows.append({'job_id': jid, 'kind': kind, 'judge_model': judge,
                      'absolute_prompt_file': fwd(dest), **meta})
        origin = 'gap_aware_supplement' if jid in gap else 'strict_new'
        origins[jid] = origin
        if not has_any_evidence(root, judge, jid):
            tasks.append(mk_task(judge, jid, kind, meta, fwd(dest), h, origin))
    old_missing = []
    for j in old_man:
        rev = root / 'results' / 'reviews' / j['judge_model']
        if (rev / (j['job_id'] + '.meta.json')).exists() or (rev / (j['job_id'] + '.txt')).exists():
            continue
        old_missing.append(j['job_id'])
        pf = root / j['prompt_file']
        if not pf.exists() or hashlib.sha256(pf.read_bytes()).hexdigest() != j['prompt_sha256']:
            print(f"SKIP old-missing {j['job_id']}: frozen prompt bytes mismatch")
            continue
        if not has_any_evidence(root, j['judge_model'], j['job_id']):
            tasks.append(mk_task(j['judge_model'], j['job_id'], j['kind'], pmap[j['job_id']],
                                 fwd(pf), j['prompt_sha256'], 'frozen_old_missing'))
    (out / 'review_manifest_merged.json').write_text(
        json.dumps({'schema': 'music-blind-reviews-v2+summary-control-additive-v3',
                    'frozen_old_count': len(old_man), 'strict_new_count': len(new),
                    'gap_aware_count': len(gap), 'jobs': mrows},
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (pp / 'review_mapping_merged_DO_NOT_SHOW_JUDGES.json').write_text(
        json.dumps({'jobs': prows, 'note': 'Never pass this mapping to D/G/F review models'},
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'review_queue_v3.json').write_text(
        json.dumps({'tasks': tasks, 'old_missing_rows': sorted(old_missing),
                    'gap_aware_built': sorted(gap.keys()),
                    'missing_inputs': sorted(set(miss)),
                    'note': ('pipeline_v3 tasks: kind=review, model=judge short name, round=D/G/F letter, '
                             'number=repeat(D/G)/sample_count(F), mode=new, prompt_rel=ABSOLUTE prompt path, '
                             'prompt_hash, task_id=review:<model>:<id>:new, '
                             'prefix_rel=data-root-relative results prefix. '
                             'Only zero-evidence IDs queued (any file under prefix excludes); '
                             'ambiguous/failed never resent.')},
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'OK old={len(old_man)} hash-equal, strict_new={len(new)}, gap_aware={len(gap)}, '
          f'tasks={len(tasks)}, old_missing={len(old_missing)}, missing_inputs={len(set(miss))}')
    print('task origins:', dict(collections.Counter(t['origin'] for t in tasks)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
