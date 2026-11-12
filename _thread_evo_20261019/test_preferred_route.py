"""gpt3 priority, ordinary outage fallback, and no protection failover."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evo
import gpt3_call
import mg_call
import mg_schedule


class PreferredRoute(unittest.TestCase):
    def test_primary_success_does_not_send_backup(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(evo, 'RUNS', Path(folder)), \
                patch.dict(os.environ, {'THREAD_ROUTE':'gpt3s','THREAD_ROUTE_G6':'gpt3s'}), \
                patch.object(evo, 'check_submission'), patch.object(gpt3_call, 'call', return_value='complete') as primary, \
                patch.object(mg_call, 'call') as backup:
            self.assertEqual(evo.call('test','prompt'), 'complete')
            primary.assert_called_once(); backup.assert_not_called()

    def test_ordinary_failure_uses_backup_and_backoff_expires(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(evo, 'RUNS', Path(folder)), \
                patch.dict(os.environ, {'THREAD_ROUTE':'gpt3s','THREAD_ROUTE_G6':'gpt3s'}), \
                patch.object(evo, 'check_submission'), patch.object(gpt3_call, 'call', return_value=None), \
                patch.object(gpt3_call, 'stopped', return_value='two transport failures'), \
                patch.object(gpt3_call, 'protection_signal', return_value=False), \
                patch.object(mg_call, 'call', return_value='backup complete') as backup:
            self.assertEqual(evo.call('test','prompt'),'backup complete')
            backup.assert_called_once()
            down=Path(folder)/'gpt3_down.txt'; state=json.loads(down.read_text())
            self.assertGreater(state['retry_after'], state['failed_at'])
            state['retry_after']=0; down.write_text(json.dumps(state))
            with patch.object(gpt3_call, 'resume_transient', return_value=True), \
                    patch.object(gpt3_call, 'call', return_value='primary recovered'):
                self.assertEqual(evo.call('next','prompt'),'primary recovered')
            self.assertFalse(down.exists())
            self.assertEqual(backup.call_count,1)

    def test_protection_failure_never_uses_backup(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(evo, 'RUNS', Path(folder)), \
                patch.dict(os.environ, {'THREAD_ROUTE':'gpt3s','THREAD_ROUTE_G6':'gpt3s'}), \
                patch.object(evo, 'check_submission'), patch.object(gpt3_call, 'call', return_value=None), \
                patch.object(gpt3_call, 'stopped', return_value='protection signal'), \
                patch.object(gpt3_call, 'protection_signal', return_value=True), \
                patch.object(mg_schedule, 'fail') as pause, patch.object(mg_call, 'call') as backup:
            self.assertIsNone(evo.call('test','prompt'))
            pause.assert_called_once(); backup.assert_not_called()

    def test_backup_transport_cooldown_does_not_block_available_primary(self):
        with patch.dict(os.environ, {'THREAD_ROUTE':'gpt3s','THREAD_ROUTE_G6':'gpt3s'}), \
                patch.object(mg_schedule, 'status', return_value={'cooling':True,'cooldown_kind':'transient_failure'}), \
                patch.object(mg_schedule, 'check') as check:
            evo.check_submission(); check.assert_not_called()
        with patch.dict(os.environ, {'THREAD_ROUTE':'gpt3s','THREAD_ROUTE_G6':'gpt3s'}), \
                patch.object(mg_schedule, 'status', return_value={'cooling':True,'cooldown_kind':'suspicious_behavior'}), \
                patch.object(mg_schedule, 'check', side_effect=mg_schedule.CoolingDown('test')):
            with self.assertRaises(mg_schedule.CoolingDown):evo.check_submission()

    def test_suspicious_signal_stops_on_first_failure(self):
        with patch.dict(gpt3_call._state, {'row':0,'total':0,'stop':None,'last_error':''},clear=True):
            gpt3_call._fail('test','suspicious behavior')
            self.assertTrue(gpt3_call.stopped())
            self.assertFalse(gpt3_call.resume_transient())


if __name__ == '__main__':unittest.main()
