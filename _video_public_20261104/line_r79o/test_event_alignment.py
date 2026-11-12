import unittest
from collections import Counter
import numpy as np
from align_music import FPS
from event_alignment import align_events

def synthetic_passage(scale=1, transpose=0):
    notes, events, run = [], [], []
    C = np.zeros((88, round(14*FPS*scale)))
    D = np.zeros_like(C)
    def add(score, seed, actual, pitch, grace=None, strength=10):
        seed, actual, pitch = seed*scale, actual*scale, pitch+transpose
        i = len(notes)
        notes.append(dict(s=seed, e=seed+.08, p=pitch, h=0, en=.5, sky=False))
        events.append(dict(id=str(i), score_s=score, score_e=score+.06, grace_run=grace))
        k = round(actual*FPS)
        C[pitch-21, k] = strength
        D[pitch-21, k] = 1
        return i
    for p in [40, 44, 47]: add(0, 0, .5, p)
    for p in [48, 52, 55]: add(1, 3, 2, p)
    for j, p in enumerate([60, 62, 64, 65, 67, 69, 71, 72]):
        run.append(add(1+j*.1, 3+j*.1, 4+j*.6, p, 'run', strength=2))
    for p in [50, 53, 57]:
        add(2, 4, 10, p)
        # Matching normalized noise must not become a false chord anchor.
        C[p-21, round(4.5*FPS)] = .001
        D[p-21, round(4.5*FPS)] = 1
    for p in [45, 52, 57]: add(3, 11, 11.7, p)
    meta = dict(events=events, runs=[dict(id='run', measure=1, indices=run)], unresolved_runs=[])
    return notes, meta, C, D

class ScoreEventRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed, cls.meta, cls.C, cls.D = synthetic_passage()
        cls.out, cls.rows, cls.qa = align_events(cls.seed, cls.meta, cls.C, cls.D)

    def test_chord_and_grace_with_same_seed_time_are_separated(self):
        chord = next(n for n in self.out if n['p'] == 48)
        grace = next(n for n in self.out if n['p'] == 60)
        self.assertAlmostEqual(chord['s'], 2, delta=1/FPS)
        self.assertAlmostEqual(grace['s'], 4, delta=1/FPS)

    def test_compressed_run_is_recovered_beyond_local_search_radius(self):
        run = self.qa['runs'][0]
        self.assertGreater(run['after'][-1]-run['after'][0], 4)
        self.assertAlmostEqual(run['boundary'][1], 10, delta=1/FPS)
        self.assertFalse(run['intact_baseline'])

    def test_grace_releases_follow_recovered_spacing(self):
        gs = [n for n in self.out if n['p'] in [60, 62, 64, 65, 67, 69, 71, 72]]
        self.assertTrue(all(n['e']-n['s'] > .35 for n in gs))
        self.assertTrue(all(a['e'] <= b['s'] for a, b in zip(gs, gs[1:])))

    def test_full_span_does_not_hide_internally_compressed_run(self):
        seed, metadata, C, D = synthetic_passage()
        ids = metadata['runs'][0]['indices']
        # Endpoints cover most of the real run, but its first half is crushed.
        for i, t in zip(ids, [3, 3.03, 3.06, 3.09, 6.4, 7, 7.6, 8.2]):
            seed[i]['s'], seed[i]['e'] = t, t+.02
        _, _, qa = align_events(seed, metadata, C, D)
        run = qa['runs'][0]
        self.assertFalse(run['intact_baseline'])
        np.testing.assert_allclose(run['after'], np.arange(8)*.6+4, atol=1/FPS)

    def test_identities_and_positive_intervals_are_preserved(self):
        self.assertEqual(Counter((n['h'], n['p']) for n in self.seed), Counter((n['h'], n['p']) for n in self.out))
        self.assertTrue(all(n['s'] >= 0 and n['e'] > n['s'] for n in self.out))

    def test_stale_event_metadata_is_rejected(self):
        metadata = dict(self.meta, seed_signature='wrong')
        with self.assertRaisesRegex(ValueError, 'different seed'):
            align_events(self.seed, metadata, self.C, self.D)

    def test_recovery_generalizes_across_tempo_and_pitch(self):
        for scale, transpose in [(.7, -7), (1.5, 5), (1, 12)]:
            with self.subTest(scale=scale, transpose=transpose):
                seed, metadata, C, D = synthetic_passage(scale, transpose)
                _, _, qa = align_events(seed, metadata, C, D)
                np.testing.assert_allclose(qa['runs'][0]['after'],
                                           (np.arange(8)*.6+4)*scale, atol=1/FPS)

    def test_release_before_repaired_interval_uses_recovered_boundary(self):
        seed, metadata, C, D = synthetic_passage()
        metadata['events'][0]['score_e'] = 1
        seed[0]['e'] = 3
        out, _, _ = align_events(seed, metadata, C, D)
        bass = next(n for n in out if n['p'] == 40)
        self.assertAlmostEqual(bass['e'], 2, delta=1/FPS)

if __name__ == '__main__': unittest.main()
