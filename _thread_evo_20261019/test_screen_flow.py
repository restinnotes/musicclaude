"""Regression tests for paid-call avoidance and unchanged experimental gates."""
import copy
import contextlib
import io
import json
import os
from pathlib import Path
import random
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

import screen_flow as F
import experiment_batch as B
import measure_candidates_20261102 as M


class Gates(unittest.TestCase):
    def test_batch_entry_selects_current_judges_before_loading_pipe(self):
        env = dict(os.environ)
        env.pop('JV', None)
        result = subprocess.run(
            [sys.executable, '-c', 'import experiment_batch as B; B.F.configure(); print(B.V.JV)'],
            cwd=Path(B.__file__).parent, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), '2')

    def test_complete_survivor_uses_only_twelve_measurements_with_cached_base(self):
        graph = {'center':'center','segments':[{'sec':'S01','bars':'1','relation':'正在面对',
                  'items':[{'id':'S01-1','text':'one complete sentence.'}],'because':[]}]}
        data = self.evidence([True]*4)
        for w in F.WORKS:
            for j in F.JUDGES:
                data[f'cov2_{w}_{j}_base'] = {'beads':[{'sec':'S01','bead':'B1','status':'说清'}]}
                data[f'al2_{w}_{j}_base'] = {'sections':[{'sec':'S01','self':'成立'}]}
        # Start with no candidate measurements, serve a complete response on demand.
        blind = {k:data.pop(k) for k in list(data) if k.startswith('v6b2_')}
        calls = []
        def submit(jobs, workers=2):
            for rid, message, model, stage in jobs:
                calls.append(rid)
                if rid.startswith('v6b2_'):data[rid]=blind[rid]
                elif rid.startswith('cov2_'):data[rid]={'beads':[{'sec':'S01','bead':'B1','status':'说清'}]}
                elif rid.startswith('al2_'):data[rid]={'sections':[{'sec':'S01','self':'成立'}]}
                else:raise AssertionError('unexpected paid diagnostic '+rid)
            return [j[0] for j in jobs]
        with tempfile.TemporaryDirectory() as folder, patch.object(F.V,'OUT',Path(folder)), \
                patch.object(F.V,'graph_of',return_value=graph), patch.object(F.V,'beads',return_value='beads'), \
                patch.object(F.V,'parse',side_effect=lambda rid:data.get(rid)), \
                patch.object(F.evo,'done',side_effect=lambda rid:rid in data), \
                patch.object(F.evo,'output',side_effect=lambda rid:json.dumps(data.get(rid))), \
                patch.object(F.verdict,'bead_keys',return_value={('S01','B1')}), \
                patch.object(F,'submit',side_effect=submit), contextlib.redirect_stdout(io.StringIO()):
            result=F.screen('candidate','base')
            self.assertEqual(result['status'],'quick_pass')
            self.assertEqual(len(calls),12)
            self.assertEqual({x.split('_')[0] for x in calls},{'v6b2','cov2','al2'})
            self.assertEqual(len(F.verdict.rows('candidate','base')),4)

    def evidence(self, wins, net_new=True):
        out = {}
        for (rid, w, j), win in zip(F.blind_ids('candidate', 'base'), wins):
            new, old = ('X', 'Y') if random.Random(rid).random() < .5 else ('Y', 'X')
            out[rid] = {'better': new if win else old,
                        f'{new}_replacing_{old}_regress': '否',
                        'sections': [{'sec': 'S01', **{k: new if net_new else old for k in F.DIMENSIONS}}]}
        return out

    def state(self, evidence):
        with patch.object(F.V, 'graph_of', return_value={'segments': [{'sec': 'S01'}]}), \
                patch.object(F.V, 'parse', side_effect=lambda rid: evidence.get(rid)):
            return F.blind_state('candidate', 'base')

    def test_two_losses_stop_without_scoring_missing_as_zero(self):
        s = self.state(self.evidence([False, False]))
        self.assertEqual(s['status'], 'reject')
        self.assertEqual(s['complete'], 2)
        self.assertEqual(len(s['missing']), 2)
        self.assertEqual(s['remaining_segment_upper_bound'], 2)

    def test_three_wins_in_incomplete_set_do_not_pass(self):
        s = self.state(self.evidence([True, True, True]))
        self.assertEqual(s['status'], 'pending')

    def test_invalid_evidence_is_not_used_for_early_rejection(self):
        e = self.evidence([False, False])
        next(iter(e.values()))['sections'] = []
        self.assertEqual(self.state(e)['status'], 'invalid')

    def test_real_rejected_candidate_spends_no_more_calls(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(F, 'submit') as submit, \
                patch.object(F, 'run_floor') as floor:
            original = F.V.OUT
            s = F.blind_state('r27p2', 'qurefs')
            self.assertEqual(s['status'], 'reject')
            self.assertEqual(s['net_sums']['plain'], -41)
            self.assertEqual(s['complete'], 3)
            with patch.object(F.V, 'OUT', Path(folder)), patch.object(F, 'run_blind', return_value=s):
                self.assertEqual(F.screen('r27p2')['status'], 'reject')
            submit.assert_not_called(); floor.assert_not_called()

    def test_floor_failure_does_not_launch_alone(self):
        state = self.state(self.evidence([True]*4))
        with tempfile.TemporaryDirectory() as folder, patch.object(F.V, 'OUT', Path(folder)), \
                patch.object(F, 'run_blind', return_value=state), \
                patch.object(F, 'publish_blind'), \
                patch.object(F, 'run_floor', return_value={'status': 'reject', 'failures': ['one section']}) as floor:
            self.assertEqual(F.screen('candidate', 'base')['status'], 'reject')
            self.assertEqual([c.args[2] for c in floor.call_args_list], ['coverage'])

    def test_only_near_boundary_complete_candidates_return_to_author(self):
        near = self.state(self.evidence([True, True, False, False]))
        self.assertEqual(F.feedback_policy(near), 'return_to_author')
        self.assertEqual(F.feedback_policy(near, attempt=3), 'archive_and_change_direction')
        self.assertEqual(F.feedback_policy(near, hard_constraint_failure=True), 'archive_and_change_direction')
        far = self.state(self.evidence([True, False, False, False], net_new=False))
        self.assertEqual(F.feedback_policy(far), 'archive_and_change_direction')

    def test_repeat_cannot_bypass_quick_failure(self):
        with patch.object(M.F, 'configure'), patch.object(M.F, 'screen', return_value={'status': 'reject'}) as screen:
            self.assertEqual(M.measure('candidate', repeat=True)['status'], 'reject')
            screen.assert_called_once_with('candidate', 'qurefs')

    def test_alone_floor_does_not_request_translation_diagnostics(self):
        missing = [f'al2_{w}_{j}_candidate' for w in F.WORKS for j in F.JUDGES]
        graph = {'center': 'center', 'segments': [{'sec': 'S01', 'bars': '1', 'relation': '正在面对',
                                                  'items': [{'id': 'S01-1', 'text': 'text'}], 'because': []}]}
        with tempfile.TemporaryDirectory() as folder, patch.object(F.V, 'OUT', Path(folder)), \
                patch.object(F, 'floor_state', side_effect=[{'status': 'pending', 'missing': missing}, {'status': 'pass'}]), \
                patch.object(F.evo, 'done', return_value=False), patch.object(F.V, 'graph_of', return_value=graph), \
                patch.object(F, 'submit') as submit:
            F.run_floor('candidate', 'base', 'alone')
            jobs = submit.call_args.args[0]
            self.assertEqual(len(jobs), 4)
            self.assertTrue(all(job[0].startswith('al2_') for job in jobs))


class ReuseAndBatch(unittest.TestCase):
    def workspace(self, root):
        import pipe
        (root/'schemes').mkdir()
        for name in ('Q15.json', 'Q6_A1.txt', 'Q6_A2.txt', 'Q6_A3.txt', 'Q15_A4.txt'):
            (root/'schemes'/name).write_bytes((pipe.HERE/'schemes'/name).read_bytes())
        (root/'标准.md').write_text('standard', encoding='utf-8')
        (root/'迭代准则.md').write_text('## 二、迭代范围和硬约束\nlimits\n## 三、流程', encoding='utf-8')
        (root/'试验记录.md').write_text('history', encoding='utf-8')
        (root/'用户判定.md').write_text('user judgments', encoding='utf-8')

    def source(self, root, model='gpt-6', message='exact input'):
        p = root / 'source'; p.mkdir()
        (p/'input.txt').write_text(message, encoding='utf-8')
        (p/'output.txt').write_text('{"original":true}', encoding='utf-8')
        (p/'call.log').write_text(json.dumps({'completed': True, 'model': model,
                                             'route': 'mimic', 'thinking_effort': 'high'}), encoding='utf-8')

    def test_reuse_checks_exact_input_and_model_and_preserves_raw_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.source(root)
            with patch.object(B.evo, 'RUNS', root):
                self.assertFalse(B.reuse_completed('changed', 'exact input ', 'g6', ['source']))
                self.assertFalse(B.reuse_completed('wrongmodel', 'exact input', 'g56', ['source']))
                self.assertTrue(B.reuse_completed('target', 'exact input', 'g6', ['source']))
                self.assertEqual((root/'target/output.txt').read_bytes(), (root/'source/output.txt').read_bytes())
                receipt = json.loads((root/'target/reuse.json').read_text())
                self.assertEqual(receipt['new_model_calls'], 0)

    def test_reuse_never_overwrites_inflight_request(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.source(root)
            (root/'target').mkdir(); (root/'target/mg_request.json').write_text('{}')
            with patch.object(B.evo, 'RUNS', root):
                self.assertFalse(B.reuse_completed('target', 'exact input', 'g6', ['source']))

    def test_review_is_bound_to_the_output_not_just_a_flag(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.source(root)
            with patch.object(B.evo, 'RUNS', root):
                B.record_review('source', True, 'read original full output')
                self.assertTrue(B.reviewed('source'))
                (root/'source/output.txt').write_text('{"different":true}')
                self.assertFalse(B.reviewed('source'))

    def test_prompt_hash_changes_when_body_changes(self):
        import pipe
        spec = pipe.load_spec('schemes/Q15.json')
        original = B.spec_hash(spec)
        other = copy.deepcopy(spec)
        other['_texts']['Q15_A4.txt'] += ' changed'
        self.assertNotEqual(original, B.spec_hash(other))

    def test_stage_stops_for_reading_before_downstream_generation(self):
        import pipe
        spec = pipe.load_spec('schemes/Q15.json')
        with tempfile.TemporaryDirectory() as folder, patch.object(B.evo, 'RUNS', Path(folder)), \
                patch.object(B.pipe, 'load_spec', return_value=spec), \
                patch.object(B.pipe, 'work_context', return_value=({'WORK_INFO':'work','SEGMENTS':'S01','CENTER':'c'}, {})), \
                patch.object(B, 'reuse_completed', return_value=False), patch.object(B, 'reviewed', return_value=False), \
                patch.object(B.evo, 'done', return_value=False), patch.object(B.F.mg_schedule, 'check'), \
                patch.object(B.pipe, 'call', return_value={'routes': []}) as call:
            result = B.generate_work({'tag': 'candidate', 'spec': 'schemes/Q15.json'}, 'op60', 'base', [])
            self.assertEqual(result['status'], 'read_required')
            self.assertEqual(call.call_count, 1)
            self.assertTrue(call.call_args.args[0].endswith('_A1'))

    def test_three_advisors_export_ten_immutable_a4_candidates_without_calls(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.workspace(root)
            with patch.object(B, 'ROOT', root), patch.object(B.evo, 'RUNS', root/'runs'), \
                    patch.object(B.pipe, 'SCHEMES', root/'schemes'), \
                    patch.object(B.V, 'graph_of', return_value={}), patch.object(B.V, 'view', return_value='line'), \
                    patch.object(B.evo, 'call') as paid:
                path = B.prepare_advisors('batch', root/'schemes/Q15.json')
                d = json.loads(path.read_text(encoding='utf-8'))
                self.assertEqual([t['requested'] for t in d['advisors']], [4, 3, 3])
                answers = {}
                for task in d['advisors']:
                    answers[task['run_id']] = {'candidates': [
                        {'hypothesis': f"{task['judge']} hypothesis {i}",
                         'A4': '{SECTIONS} {CENTER} {ROUTES} {TARGETS} '+task['judge']+str(i)}
                        for i in range(task['requested'])]}
                with patch.object(B.V, 'parse', side_effect=lambda rid: answers[rid]):
                    mp = B.import_advisors(d)
                manifest = B.load_manifest(mp)
                self.assertEqual(len(manifest['candidates']), 10)
                for c in manifest['candidates']:
                    spec = B.pipe.load_spec(root/c['spec'])
                    self.assertEqual([s['prompt_file'] for s in spec['steps'][:3]],
                                     ['Q6_A1.txt', 'Q6_A2.txt', 'Q6_A3.txt'])
                paid.assert_not_called()

    def test_factorial_cross_can_separate_a1_and_a2(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.workspace(root)
            with patch.object(B, 'ROOT', root), patch.object(B.pipe, 'SCHEMES', root/'schemes'):
                original = json.loads((root/'schemes/Q15.json').read_text(encoding='utf-8'))
                changed = copy.deepcopy(original)
                changed['steps'][0]['prompt_file'] = 'alternative_A1.txt'
                changed['steps'][1]['prompt_file'] = 'alternative_A2.txt'
                for sid in ('A1', 'A2'):
                    (root/f'schemes/alternative_{sid}.txt').write_text('alternative '+sid, encoding='utf-8')
                (root/'schemes/alternative.json').write_text(json.dumps(changed), encoding='utf-8')
                paths = [root/'schemes/Q15.json', root/'schemes/alternative.json']
                mp = B.cross('factorial', paths, paths, 'base', ['old'], split_upstream=True)
                manifest = B.load_manifest(mp)
                self.assertEqual(len(manifest['candidates']), 8)
                combinations = set()
                for c in manifest['candidates']:
                    spec = B.pipe.load_spec(root/c['spec'])
                    combinations.add((spec['_steps']['A1']['prompt_file'], spec['_steps']['A2']['prompt_file'], c['writer']))
                self.assertEqual(len(combinations), 8)

    def test_real_baseline_prerequisites_reuse_both_works_including_array_response(self):
        import pipe
        spec = pipe.load_spec('schemes/Q15.json')
        spec['_texts']['Q15_A4.txt'] += '\nDifferent writer experiment.'
        real_call = pipe.call
        production_runs = B.evo.RUNS
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for w in F.WORKS:
                for sid in ('A1', 'A2', 'A3'):
                    rid = f'scqu_{w}_{sid}'
                    dst = root/rid; dst.mkdir()
                    for filename in ('input.txt', 'output.txt', 'call.log'):
                        (dst/filename).write_bytes((production_runs/rid/filename).read_bytes())
            generated = []
            def call(rid, message, model, name):
                if rid.endswith('_A4'):
                    generated.append(rid)
                    return {'segments': []}
                return real_call(rid, message, model, name)
            with patch.object(B.evo, 'RUNS', root), patch.object(B.pipe, 'load_spec', return_value=spec), \
                    patch.object(B.pipe, 'call', side_effect=call), patch.object(B.pipe, 'save'), \
                    patch.object(B.evo, 'call', side_effect=AssertionError('no live requests')), \
                    patch.object(B.F.mg_schedule, 'check'):
                for w in F.WORKS:
                    result = B.generate_work({'tag':'newwriter','spec':'schemes/Q15.json'}, w, 'qurefs', ['qu'])
                    self.assertEqual(result['status'], 'read_required')
                    self.assertTrue(result['run_id'].endswith('_A4'))
                    for sid in ('A1', 'A2', 'A3'):
                        self.assertTrue((root/f'scnewwriter_{w}_{sid}'/'reuse.json').exists())
                self.assertEqual(len(generated), 2)


if __name__ == '__main__':
    unittest.main()
