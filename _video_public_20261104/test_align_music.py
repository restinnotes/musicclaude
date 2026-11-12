import unittest
from collections import Counter
import numpy as np
from align_music import FPS, groups_of, ordered_refine, input_anomalies

def note(t, p, h=0, length=.08):
    return dict(s=t, e=t+length, p=p, h=h, en=.5, sky=False)

def impulses(events, seconds=4):
    a = np.zeros((88, round(seconds*FPS)), dtype=float)
    for t, p, strength in events:
        k = round(t*FPS)
        a[p-21, k] = strength
    return a

class OrderedAlignmentTests(unittest.TestCase):
    def test_fast_arpeggio_keeps_distinct_onsets(self):
        ns = [note(1+i*.03, 60+i) for i in range(10)]
        self.assertEqual(len(groups_of(ns)), 10)
        out, _ = ordered_refine(ns, impulses([(n['s']+.2, n['p'], 1) for n in ns]), radius=.5)
        np.testing.assert_allclose([n['s'] for n in out], [n['s']+.2 for n in ns], atol=1/FPS)

    def test_repeated_pitch_cannot_reuse_one_attack(self):
        ns = [note(1, 60), note(1.2, 60)]
        out, _ = ordered_refine(ns, impulses([(1.1, 60, 1), (1.3, 60, .9)]), radius=.5)
        self.assertGreater(out[1]['s']-out[0]['s'], .15)

    def test_other_pitch_attack_does_not_attract_note(self):
        ns = [note(1, 60), note(1.4, 64)]
        out, _ = ordered_refine(ns, impulses([(1.1, 60, .8), (1.5, 64, .8), (1, 75, 20), (1.4, 75, 20)]), radius=.5)
        np.testing.assert_allclose([n['s'] for n in out], [1.1, 1.5], atol=1/FPS)

    def test_silence_retains_timing_and_reports_weak_evidence(self):
        ns = [note(1, 60), note(1.2, 64)]
        out, rows = ordered_refine(ns, impulses([]), radius=.5)
        np.testing.assert_allclose([n['s'] for n in out], [1, 1.2], atol=1/FPS)
        self.assertTrue(all(r['attack_support'] == 0 for r in rows))

    def test_identity_and_chord_members_preserved(self):
        ns = [note(1, 60), note(1, 64, 1), note(1.3, 67)]
        out, _ = ordered_refine(ns, impulses([(1.1, 60, 1), (1.1, 64, 1), (1.4, 67, 1)]), radius=.5)
        self.assertEqual(Counter((n['h'], n['p']) for n in ns), Counter((n['h'], n['p']) for n in out))
        self.assertEqual(out[0]['s'], out[1]['s'])
        self.assertTrue(all(n['e'] > n['s'] for n in out))

    def test_same_pitch_overlap_is_exposed(self):
        ns = [note(1, 60, length=1), note(1.2, 60), note(1.3, 60, 1)]
        self.assertEqual(input_anomalies(ns)['same_pitch_overlaps'], 1)

    def test_invalid_search_radius_rejected(self):
        with self.assertRaises(ValueError):
            ordered_refine([note(1, 60)], impulses([]), radius=0)

if __name__ == '__main__': unittest.main()
