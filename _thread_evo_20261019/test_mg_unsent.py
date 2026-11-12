"""A cooldown before dispatch must never become a fake receiver failure."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import mg_call
import mg_schedule


class UnsentRequest(unittest.TestCase):
    def test_cooldown_retains_audit_but_is_not_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'case').mkdir()
            with patch.object(mg_call.evo, 'RUNS', root), patch.object(mg_call, 'docker') as docker, \
                 patch.object(mg_schedule, 'reserve', side_effect=mg_schedule.CoolingDown('test')):
                with self.assertRaises(mg_schedule.CoolingDown):
                    mg_call.once('case', 0, 'original prompt', 'gpt-6')
            self.assertFalse((root / 'case/mg_request.json').exists(), 'unsent request must not be resumed as dispatched')
            archived = list((root / 'case').glob('mg_unsubmitted_*.json'))
            self.assertEqual(len(archived), 1)
            self.assertEqual(json.loads(archived[0].read_text(encoding='utf-8'))['prompt'], 'original prompt')
            self.assertFalse(any('-d' in c.args for c in docker.call_args_list))

    def test_dispatched_request_remains_collectable(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'case').mkdir()
            with patch.object(mg_call.evo, 'RUNS', root), patch.object(mg_call, 'docker') as docker, \
                 patch.object(mg_schedule, 'reserve', side_effect=lambda rid, submit: submit()), \
                 patch.object(mg_call, 'poll', return_value={'http_status': 200}):
                remote, result = mg_call.once('case', 0, 'original prompt', 'gpt-6')
            request = json.loads((root / 'case/mg_request.json').read_text(encoding='utf-8'))
            self.assertEqual(request['remote_id'], remote)
            self.assertEqual(result['http_status'], 200)
            self.assertEqual(sum('-d' in c.args for c in docker.call_args_list), 1)
            self.assertFalse(list((root / 'case').glob('mg_unsubmitted_*.json')))


if __name__ == '__main__':
    unittest.main()
