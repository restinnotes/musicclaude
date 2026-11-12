"""Resume the existing paired repair loop; freeze evidence before model calls."""
import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

os.environ.setdefault('JV', '2')
import round65_fix as R

ROOT = Path(__file__).resolve().parent
BATCH = ROOT / 'runs/_batches/continue_r80'

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def generate(base, tags, limit, guard, scope_guard=False, semantic_check=False, surface_only=False):
    if scope_guard:
        R.REPAIR = R.REPAIR.replace('最多改 {MAX} 条。', '''守护清单只用于防止删除当前稿已经具备的实质内容，不是待补写清单。它来自不同版本的历史比较，里面可能有当前稿从未采用的说法，也可能有不成立的意见。每一项先核对当前稿：已有的意思要保住；当前稿没有的意思，不仅凭这条历史评语补进去。任何守护意见都不能要求新增前史、对方举动或把推测写成事实；当前稿的猜测与愿望须保持原来的不确定程度。

最多改 {MAX} 条。''')
    if semantic_check:
        R.REPAIR = R.REPAIR.replace('最多改 {MAX} 条。', '''每条修改在列入 edits 前，先与当前稿核对实质含义。去重或换口气时，保住原有心理动作的种类、发生先后、确定程度、主动性和强弱；表达相近不代表这些都相同。在 note 中逐条说明保住的意思和真正去掉的重复。无法确认没有实质损失，就撤销这一条修改；不必用满名额，必要时可以不改。

最多改 {MAX} 条。''')
    if surface_only:
        R.REPAIR = R.REPAIR.replace('最多改 {MAX} 条。', '''这一轮只做句子内部的措辞精简，不重组心理发展。每条原有的心理动作、回想、判断依据及其连接关系都留在原条目，不删除或合并整条，不删去承载它们的分句，不把叙述改成引语，也不另加一个总结或解释。只在确实拗口或重复的词语、指代、词序和句法上动手；改后这条的字数不得超过改前。少几个字本身不算改善，须同时更自然且意思完整；做不到就保持原文。note 说明每条改动的具体语言问题及完整保留的意思。

最多改 {MAX} 条。''')
    os.environ['THREAD_ROUTE'] = 'mimic'
    R.F.configure()
    BATCH.mkdir(parents=True, exist_ok=True)
    manifest = {'base': base, 'tags': tags, 'works': list(R.F.WORKS),
                'template_sha256': digest(R.REPAIR), 'route': 'mimic', 'model': 'g6',
                'max_edits': limit, 'guard': guard, 'scope_guard_to_current': scope_guard, 'gemini_in_repair': False,
                'sources': {}, 'started': datetime.now(ZoneInfo('America/New_York')).isoformat()}
    if semantic_check:
        manifest['semantic_check_before_edit'] = True
    if surface_only:
        manifest['surface_only_nonexpanding_items'] = True
    for w in R.F.WORKS:
        issues = R.open_issues(w, base)
        assert issues and all(not x['读者'].startswith('gem') for x in issues)
        manifest['sources'][w] = {'line_sha256': digest(R.V.view(R.V.graph_of(w, base))),
                                  'beads_sha256': digest(R.V.beads(w)),
                                  'feedback_count': len(issues),
                                  'guard_count': len(R.guard_list(w, guard))}
    dest = BATCH / ('_'.join(tags) + '_manifest.json')
    if dest.exists():
        old = json.loads(dest.read_text(encoding='utf-8'))
        assert all(old[k] == manifest[k] for k in manifest if k != 'started'), 'frozen run mismatch'
    else:
        write(dest, manifest)
    print(json.dumps(manifest, ensure_ascii=False), flush=True)
    def one(tag):
        a = SimpleNamespace(source=base, tag=tag, open=base, vs='', guard=guard, max=limit, model='g6')
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda w: R.one_repair(a, w), R.F.WORKS))
        R.show(tag, base)
        return tag
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(one, tags):
            print('PAIR_READY_REQUIRES_FULL_READ', result, flush=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('base')
    p.add_argument('tags', nargs='+')
    p.add_argument('--max', type=int, default=8)
    p.add_argument('--scope-guard', action='store_true')
    p.add_argument('--semantic-check', action='store_true')
    p.add_argument('--surface-only', action='store_true')
    p.add_argument('--guard', default='r68a:r67a,r78a:r67a,r78a:r49b,r78a:r54weave')
    a = p.parse_args()
    generate(a.base, a.tags, a.max, a.guard, a.scope_guard, a.semantic_check, a.surface_only)
