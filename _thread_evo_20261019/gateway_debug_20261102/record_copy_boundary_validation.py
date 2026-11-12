import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).parent
source = root / 'detector_copy_boundary_fixed.py'
local = root.parents[1] / 'mimic-cli/src/chatgpt/detector.py'
assert source.read_bytes() == local.read_bytes()
result = json.loads((root / 'exact-stream/capture.json').read_text())
structure = json.loads((root / 'exact-stream/structure.json').read_text())
call = json.loads((root.parent / 'runs/scr26t3_op61_A4/call.log').read_text())
record = {'candidate_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'tests': {'copy_boundary': 3, 'empty_finished_grace':3, 'completion_guards':11,
              'existing_reader_guard': 13, 'worker_logging': 4, 'schedule': 13},
    'reproduced_bugs': ['whole-turn Copy lookup borrows user button',
                        'geometry fallback borrows next user Copy button'],
    'latest_exact_retry': {key: call[key] for key in ('remote_id','seconds','completed','http_status','response_chars')},
    'capture': {'bytes': result['bytes'], 'truncated': result['truncated'], 'status': result['status'],
                'sse_done': structure['sse_done'], 'json_parse_errors': structure['json_parse_errors']},
    'empty_response_root_cause': 'latest failed UI had 9190-character DIL source whose body returns null; upstream conversion path unresolved',
    'cooldown_seconds': {'ordinary_failure': 60, 'suspicious_behavior': 1800}}
(root / 'copy_boundary_validation.json').write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))
