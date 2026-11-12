"""Generate a temporary client copy with a fixed-prompt, one-shot manual send gate."""
from pathlib import Path
import hashlib
import json
import py_compile

root = Path(__file__).resolve().parents[1]
out = root / 'experiments' / 'yi-rootcause' / '20261006T0746Z'
source = (out / 'client.original.py').read_text(encoding='utf-8')
needle = '                send_state = await self._click_send(visible_send_only=bool(all_attachments))'
assert source.count(needle) == 1
replacement = '''                manual_flag = Path('/app/state/yi-rootcause-manual-send-once.flag')
                fixed_cup_hash = '6941db951890638011b431dc77b33bccbe691c7628484308a252956549814d15'
                manual_cup = (__import__('hashlib').sha256(submitted_text.strip().replace("\\r\\n", "\\n").encode()).hexdigest() == fixed_cup_hash)
                if getattr(self, "_standard_one_shot", False) and manual_flag.exists() and manual_cup:
                    manual_flag.unlink()
                    from src.api.probe_evidence import capture_probe_evidence
                    prepared = await capture_probe_evidence(self, 'manual-prepared')
                    self._standard_evidence['diagnostic_manual_send'] = {
                        'method': 'remote_vnc_mouse', 'prepared_at': time.time(),
                        'automatic_send_executed': False, 'prepared_evidence': prepared}
                    emit('diagnostic_manual_send_waiting', request_id=self._standard_request_id,
                         page_object_id=id(self.page), fixed_prompt_verified=True)
                    if not await self._wait_for_message_submission(pre_user_signature, submitted_text, timeout_ms=180000):
                        raise StandardStateError('timeout', 'Manual-send diagnostic expired without a submission')
                    send_state = 'clicked'
                else:
                    send_state = await self._click_send(visible_send_only=bool(all_attachments))'''
target = out / 'client.manual-send.py'
target.write_text(source.replace(needle, replacement), encoding='utf-8')
py_compile.compile(str(target), doraise=True)
record = {'original_sha256': hashlib.sha256((out / 'client.original.py').read_bytes()).hexdigest(),
          'temporary_client_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'fixed_prompt_canonical_sha256': '6941db951890638011b431dc77b33bccbe691c7628484308a252956549814d15',
          'only_send_action_changed': True, 'standard_model_effort_contract_preserved': True,
          'restore_required_after_experiment': True}
(out / 'manual-send-hook.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record))
