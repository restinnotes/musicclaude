"""Offline: metadata generality and byte-for-byte preservation of frozen experiments."""
import json
from pathlib import Path
from unittest.mock import patch

import pipe

root = Path(__file__).parent
checks = []
for name, tag in [('R26T3', 'r26t3'), ('R27P2', 'r27p2')]:
    spec = pipe.load_spec(root / f'schemes/{name}.json')
    for work in ('op60', 'op61'):
        builtins, graph = pipe.work_context(work, 'qu')
        for phase in ('A1', 'A4'):
            folder = root / f'runs/sc{tag}_{work}_{phase}'
            frozen = folder / 'prepared_input.txt'
            if not frozen.exists():
                continue
            outputs = {}
            for sid in spec['_deps'][phase]:
                outputs[sid] = pipe.call(f'sc{tag}_{work}_{sid}', '', spec['_steps'][sid]['model'], spec['name'])
            assert pipe.render_step(spec, phase, builtins, outputs) == frozen.read_text(encoding='utf-8')
            checks.append(str(frozen.relative_to(root)))
metadata = {'composer': '巴托克', 'title_zh': '《弦乐、打击乐与钢片琴音乐》', 'opus': 'Sz.106'}
with patch.object(pipe.work_meta, 'load', return_value=metadata), \
     patch.object(pipe.V, 'graph_of', return_value={'center': '测试中心', 'segments': [{'sec': 'S01', 'bars': '1–5'}]}), \
     patch.object(pipe.covjudge, 'bead_text', return_value='冻结珠子'):
    builtins, graph = pipe.work_context('different_composer', 'qu')
assert builtins['WORK_INFO'] == '作曲家：巴托克\n作品：《弦乐、打击乐与钢片琴音乐》Sz.106'
assert '肖邦' not in builtins['WORK_INFO'] and 'Chopin' not in builtins['WORK_INFO']
checks.append('different_composer_metadata')
(root / 'runs/pipe_metadata_verification_20261102.json').write_text(json.dumps(
    {'checks': checks, 'model_requests': 0, 'frozen_inputs_unchanged': True,
     'scope': 'WORK_INFO metadata only; other loaders retain their own work registrations'},
    ensure_ascii=False, indent=2), encoding='utf-8')
print('Verified', len(checks), 'metadata/frozen-input checks; no model requests')
