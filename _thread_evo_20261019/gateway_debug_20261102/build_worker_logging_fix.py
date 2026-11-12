"""Retain the deployed music policy while applying only worker logging changes."""
from pathlib import Path

root = Path(__file__).parent
source = (root.parent.parent / 'mimic-cli/src/chatgpt/client.py').read_text(encoding='utf-8')
deployed = (root / 'client_deployed_before.py').read_text(encoding='utf-8')
policy = '''        if getattr(self, "_music_experiment_mode", False):
            from src.chatgpt.music_requested_mode import verify_requested_mode
            return await verify_requested_mode(self, requested_model, reasoning_effort, verification_stage)
'''
assert deployed.count(policy) == 1
assert source.count(policy) == 0
anchor = '        if requested_model not in {"mimicgate-browser", "gpt-5.6-sol"}:\n'
assert source.count(anchor) == 1
source = source.replace(anchor, policy + anchor)
(root / 'client_worker_logging_fixed.py').write_text(source, encoding='utf-8')
print('Built worker logging fix; deployed music model policy retained')
standard = (root / 'standard_completion_before_worker_logging.py').read_text(encoding='utf-8')
assert standard.count('        client._recent_backend_events = []\n') == 1
standard = standard.replace('        client._recent_backend_events = []\n',
                            '        client._recent_backend_events.clear()\n')
(root / 'standard_completion_worker_logging_fixed.py').write_text(standard, encoding='utf-8')
