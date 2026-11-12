"""Build reviewable prompt/product/evidence notes for paired local repairs."""
import argparse
import difflib
import json
from pathlib import Path

import audit_r80 as A

ROOT, BATCH = A.C.ROOT, A.C.BATCH


def link(path, label=None):
    path = Path(path)
    return f'[{label or path.name}](<{path.resolve().as_posix()}>)'


def build(tag):
    matches = [(p, json.loads(p.read_text(encoding='utf-8')))
               for p in BATCH.glob('*_manifest.json')]
    manifest_path, manifest = next((p, d) for p, d in matches if tag in d['tags'])
    source = manifest['base']
    base = manifest.get('comparison_base', source)
    comparison_context = BATCH / f'{tag}_comparison_context.json'
    if comparison_context.exists():
        context = json.loads(comparison_context.read_text(encoding='utf-8'))
        assert context['production_base'] == source
        base = context['comparison_base']
    stage = manifest.get('stage', 'F2')
    template = 'RESTORE' if stage == 'F1' else 'REPAIR'
    full_path = BATCH / f'{tag}_vs{base}_full_audit.json'
    audit_path = full_path if full_path.exists() else BATCH / f'{tag}_vs{base}_quick_audit.json'
    disposition = BATCH / f'{tag}_disposition.json'
    md = [f'## {tag} 对 {base}：双曲局部修订', '',
          '候选测量记录；是否接纳以完整验收和主线记录为准。', '',
          '### 提示词与实际输入', '',
          f'同一 {template} 模板，从 {source} 两首一起修改，每首最多改 {manifest["max_edits"]} 条；'
          f'守护范围限定于当前稿已有内容：{manifest.get("scope_guard_to_current", False)}。', '',
          f'两首同跑，正文 Mimic g6/High；Gemini 不进入修补。'
          f'模板 SHA256：`{manifest["template_sha256"]}`。', '',
          f'守护来源：`{manifest["guard"]}`；{link(manifest_path, "冻结参数与来源哈希")}。', '',
          '### 已测结果', '']
    if manifest.get('semantic_check_before_edit'):
        md[md.index('### 已测结果'):md.index('### 已测结果')] = [
            '生成前逐条核对心理动作的种类、发生先后、确定程度、主动性和强弱；拿不准则不改。'
            '这是生成办法，标准、评委和通过门槛未改。', '']
    if manifest.get('surface_only_nonexpanding_items'):
        md[md.index('### 已测结果'):md.index('### 已测结果')] = [
            '本轮仅改句内措辞，保留原有心理分句及连接，每条字数不增加；'
            '机械核对条目编号、操作类型、条数和字数。此限制只约束生成，不替代质量验收。', '']
    if audit_path.exists():
        data = json.loads(audit_path.read_text(encoding='utf-8'))
        md += ['| 范围 | 已回票 | 选新 | 不退步 | 单独成立 | 不啰嗦 | 人话 | 接珠子 |',
               '|---|---:|---:|---:|---:|---:|---:|---:|']
        for scope, row in [('双曲', data['total']), *data['per_work'].items()]:
            md.append(f'| {scope} | {row["n"]} | {row["wins"]} | {row["no_regress"]} | '
                      + ' | '.join(f'{row["net"][k]:+d}' for k in A.F.DIMENSIONS) + ' |')
        md += ['', f'测量阶段：{data["phase"]}。净胜为实际已回票的合计；缺票不计零。', '',
               link(audit_path, '原票编号、哈希及完整性核对') + '。']
        if data.get('phase') == 'full':
            md += ['', f'两首分别验收是否同时通过：`{data.get("paired_pass", "未复核")}`。'
                   '合计通过不能抵消单首未通过；仍须另查底线与固定锚点。']
    else:
        md += ['盲比未测，不以零代替。']
    if disposition.exists():
        d = json.loads(disposition.read_text(encoding='utf-8'))
        md += ['', f'处置：`{d["decision"]}`。{d["reason"]}', '', link(disposition) + '。']
    else:
        md += ['', '尚无接纳或归档结论。']
    md += ['', '覆盖、单独读或完整八票未测者均不推定通过；失败快筛不继续购买后续关卡。']
    for kind, label in [('coverage', '覆盖底线'), ('alone', '单独读底线')]:
        binding = BATCH / f'{tag}_{kind}_binding.json'
        if binding.exists():
            floor = json.loads(binding.read_text(encoding='utf-8'))
            md += ['', f'{label}：`{floor["state"]["status"]}`；'
                   + link(binding, '逐票输入、原文哈希与底线结果') + '。']
    anchor_path = BATCH / f'{tag}_anchor_floor.json'
    if anchor_path.exists():
        anchor = json.loads(anchor_path.read_text(encoding='utf-8'))
        md += ['', f'对固定锚点 {anchor["anchor"]} 的底线：`{anchor["state"]["status"]}`；'
               + '；'.join(anchor['state']['failures']) + '。'
               + link(anchor_path, '冻结底线结果')]
    fixed = BATCH / f'{tag}_vsr49b_full_audit.json'
    if base != 'r49b' and fixed.exists():
        data = json.loads(fixed.read_text(encoding='utf-8'))
        md += ['', '### 固定锚点 r49b（按作品诊断）', '',
               '| 范围 | 已回票 | 选新 | 不退步 | 单独成立 | 不啰嗦 | 人话 | 接珠子 |',
               '|---|---:|---:|---:|---:|---:|---:|---:|']
        for scope, row in [('双曲', data['total']), *data['per_work'].items()]:
            md.append(f'| {scope} | {row["n"]} | {row["wins"]} | {row["no_regress"]} | '
                      + ' | '.join(f'{row["net"][k]:+d}' for k in A.F.DIMENSIONS) + ' |')
        md += ['', f'固定锚点两首分别验收是否同时通过：`{data.get("paired_pass", "未复核")}`。'
               '单首必需净胜为负时不能接纳，不用合计结果抵消。'
               + link(fixed, '固定锚点完整原票与哈希')]
    held = BATCH / f'{tag}_heldout.json'
    if held.exists():
        data = json.loads(held.read_text(encoding='utf-8'))
        md += ['', f'留出 Gemini：{data["wins"]}/{data["complete"]} 选新，'
               f'{data["no_regress"]}/{data["complete"]} 不退步。只查一次，不进修补输入；'
               + link(held, '含反对票的完整来源')]
    for work in A.F.WORKS:
        rid = f'sc{tag}_{work}_{stage}'
        folder = ROOT / 'runs' / rid
        assert (folder / 'inspection_r80.json').exists(), f'{rid}: requires full read'
        md += ['', f'### {work} 全部前后差别', '',
               f'{link(folder / "input.txt", "实际完整提示词")}；'
               f'{link(folder / "output.txt", "模型原文")}；'
               f'{link(ROOT / "evaluations/v6fix" / f"{work}_{tag}.md", "机械生成的候选正文")}。', '', '```diff']
        old = A.V.view(A.V.graph_of(work, base), ids=True).splitlines()
        new = A.V.view(A.V.graph_of(work, tag), ids=True).splitlines()
        md += list(difflib.unified_diff(old, new, fromfile=base, tofile=tag, lineterm=''))
        md += ['```']
    output = ROOT / '版本说明' / f'{tag}_vs_{base}.md'
    output.parent.mkdir(exist_ok=True)
    output.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(output)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('tags', nargs='+')
    for tag in p.parse_args().tags:
        build(tag)
