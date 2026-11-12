import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from alignment_guard import assess, require_renderable


class ExportGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.audio = Path(self.tmp.name)/'recording.wav'
        self.audio.write_bytes(b'recording-one')

    def candidate(self, ts=None, strength=.8):
        ts = ts or [1+i*.4 for i in range(22)]
        ns = [dict(s=t, e=t+.01, p=45+i, h=0) for i, t in enumerate(ts)]
        rows = [dict(after=n['s'], pitches=[n['p']], grace_run='run', attack_support=strength) for n in ns]
        qa = dict(groups=rows, event_alignment=dict(unresolved_runs=[], runs=[dict(
            id='run', after=ts, pitches=[n['p'] for n in ns], boundary=[.5, 12])]))
        return dict(notes=ns, dur=14), qa

    def certify(self, m, qa):
        m['alignment'] = dict(automatic_validation=assess(m, qa, self.audio))
        return m

    def test_validated_output_is_renderable(self):
        m, qa = self.candidate()
        require_renderable(self.certify(m, qa), self.audio)

    def test_fast_supported_arpeggio_is_allowed(self):
        m, qa = self.candidate([1+i*.025 for i in range(22)])
        require_renderable(self.certify(m, qa), self.audio)

    def test_full_span_with_internal_clusters_is_rejected(self):
        m, qa = self.candidate([1+i*.02 for i in range(10)]+[6+i*.02 for i in range(12)])
        self.certify(m, qa)
        self.assertIn('internally_compressed_free_run', [x['code'] for x in m['alignment']['automatic_validation']['issues']])
        with self.assertRaises(ValueError): require_renderable(m, self.audio)

    def test_weak_evidence_is_not_promoted(self):
        m, qa = self.candidate(strength=.1)
        with self.assertRaises(ValueError): require_renderable(self.certify(m, qa), self.audio)

    def test_new_recording_invalidates_old_certificate(self):
        m, qa = self.candidate(); self.certify(m, qa)
        self.audio.write_bytes(b'recording-two')
        with self.assertRaisesRegex(ValueError, 'Recording changed'): require_renderable(m, self.audio)

    def test_note_edit_invalidates_old_certificate(self):
        m, qa = self.candidate(); self.certify(m, qa)
        m['notes'][0]['s'] += .001
        with self.assertRaisesRegex(ValueError, 'note data changed'): require_renderable(m, self.audio)

    def test_missing_validation_is_rejected(self):
        m, _ = self.candidate()
        with self.assertRaises(ValueError): require_renderable(m, self.audio)

    def test_unresolved_metadata_and_stale_report_are_exposed(self):
        m, qa = self.candidate()
        qa['event_alignment']['unresolved_runs'] = [{'reason': 'missing event'}]
        qa['groups'][0]['after'] += .2
        codes = [x['code'] for x in assess(m, qa, self.audio)['issues']]
        self.assertIn('unresolved_score_events', codes)
        self.assertIn('report_note_mismatch', codes)

    def test_invalid_intervals_are_exposed(self):
        m, qa = self.candidate(); m['notes'][0]['e'] = 0
        self.assertIn('invalid_note_intervals', [x['code'] for x in assess(m, qa, self.audio)['issues']])

    def test_onset_group_report_preserves_per_note_offsets(self):
        m, qa = self.candidate()
        # A second chord member is summarized by one group time, but keeps
        # its 8 ms source offset in the aligned note data.
        n = dict(m['notes'][0], s=m['notes'][0]['s']+.008, p=90)
        m['notes'].append(n); qa['groups'][0]['pitches'].append(90)
        codes = [x['code'] for x in assess(m, qa, self.audio)['issues']]
        self.assertNotIn('report_note_mismatch', codes)

    def test_actual_render_entry_points_refuse_unvalidated_data(self):
        import film_v6
        import film_v3
        import film_pub
        m, _ = self.candidate()
        fake = SimpleNamespace(music=m, audio=self.audio, src_audio=self.audio)
        for module, constructor in [(film_v6, 'Film6'), (film_v3, 'Page'), (film_pub, 'Film')]:
            with self.subTest(entry=module.__name__):
                output = Path(self.tmp.name)/module.__name__/'must-not-exist.mp4'
                with patch.object(module, constructor, return_value=fake), patch.object(module.subprocess, 'Popen') as encoder:
                    with self.assertRaisesRegex(ValueError, 'requires review'):
                        module.render('any-work', 'any-tag', 0, 1, str(output))
                    encoder.assert_not_called()
                    self.assertFalse(output.parent.exists())


if __name__ == '__main__': unittest.main()
