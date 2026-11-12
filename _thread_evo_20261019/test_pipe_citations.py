"""Preserve model references when the presentation normalizes item IDs."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pipe


class CitationRoundTrip(unittest.TestCase):
    def convert(self, result):
        reference = {'center': 'unchanged', 'segments': [
            {'sec': s['sec'], 'bars': str(n)} for n, s in enumerate(result['segments'], 1)]}
        original = copy.deepcopy(result)
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / 'op61_ref.json').write_text('{"rows": []}', encoding='utf-8')
            with patch.object(pipe.V, 'OUT', out), contextlib.redirect_stdout(io.StringIO()):
                pipe.save('op61', reference, result, 'test', 'candidate', 'ref')
            saved = json.loads((out / 'op61_candidate.json').read_text(encoding='utf-8'))['graph']
            rendered = (out / 'op61_candidate.md').read_text(encoding='utf-8')
        self.assertEqual(result, original, 'conversion must not mutate the model response')
        self.assertEqual([i['text'] for s in result['segments'] for i in s['items']],
                         [i['text'] for s in saved['segments'] for i in s['items']])
        return saved, rendered

    def test_real_complete_candidate_keeps_all_prior_references(self):
        result = json.loads((pipe.HERE / 'runs/scr27p2_op61_A4/parsed.json').read_text(encoding='utf-8'))
        saved, rendered = self.convert(result)
        expected, seen = [], {}
        for segment in result['segments']:
            for n, item in enumerate(segment['items'], 1):
                target = f"{segment['sec']}-{n}"
                expected += [(seen[c], target) for c in item.get('cite', []) if c in seen]
                seen[item['id']] = target
        actual = [(e['from'], e['to']) for s in saved['segments'] for e in s['because']]
        self.assertGreater(len(expected), 20)
        self.assertEqual(actual, expected)
        self.assertIn('〔', rendered)

    def test_legacy_canonical_ids_and_backward_boundary(self):
        result = {'segments': [
            {'sec': 'S01', 'items': [{'id': 'S01-1', 'text': 'first', 'cite': []}]},
            {'sec': 'S02', 'items': [
                {'id': 'S02-1', 'text': 'second', 'cite': ['S01-1', 'S02-1', 'S02-2', 'unknown']},
                {'id': 'S02-2', 'text': 'third', 'cite': ['S02-1']}]},
        ]}
        saved, _ = self.convert(result)
        self.assertEqual(saved['segments'][1]['because'], [
            {'from': 'S01-1', 'to': 'S02-1', 'rel': '引用'},
            {'from': 'S02-1', 'to': 'S02-2', 'rel': '引用'}])


if __name__ == '__main__':
    unittest.main()
