"""Local CLI checks for redaction, probe parsing and isolated concurrent logs."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
import json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mg", ROOT / "cli" / "mg.py")
mg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)


class CLIGuardTests(unittest.TestCase):
    def test_probe_screenshot_export_rejects_escape_and_verifies_bytes(self):
        import hashlib
        with TemporaryDirectory() as folder, patch.object(mg.subprocess, 'run') as copy:
            result = mg.save_probe_screenshots({'diagnostics': {'screenshot_evidence': {
                'request_id': '../private', 'directory': '/app/state/private'}}}, Path(folder))
            self.assertFalse(result['complete'])
            copy.assert_not_called()
            request_id = 'a' * 32
            record = {'diagnostics': {'screenshot_evidence': {'request_id': request_id,
                'directory': '/app/state/probe-artifacts/' + request_id, 'success': True,
                'files': [{'filename': name, 'sha256': hashlib.sha256(name.encode()).hexdigest()}
                    for name in ('response-viewport.jpg', 'response-full.jpg')]}}}
            def perform_copy(*args, **kwargs):
                for item in record['diagnostics']['screenshot_evidence']['files']:
                    Path(folder, 'screenshots', item['filename']).write_bytes(item['filename'].encode())
                return type('Result', (), {'returncode': 0})()
            copy.side_effect = perform_copy
            self.assertTrue(mg.save_probe_screenshots(record, Path(folder))['complete'])
            record['diagnostics']['screenshot_evidence']['files'][0]['sha256'] = '0' * 64
            self.assertFalse(mg.save_probe_screenshots(record, Path(folder))['complete'])
    def test_fresh_missing_session_stops_before_any_http(self):
        import time
        status={'observed_epoch':time.time(),'session_cookie_count':0}
        result=type('Result',(),{'returncode':0,'stdout':json.dumps(status)})()
        with patch.object(mg,'session_frozen',return_value=False),patch.object(mg.subprocess,'run',return_value=result),patch.object(mg,'http_json') as http,patch.object(mg,'read_auth') as auth:
            with self.assertRaises(mg.CLIError) as error:
                mg.standard_call('NEVER SEND',{})
            self.assertEqual(error.exception.kind,'authentication_missing')
            http.assert_not_called()
            auth.assert_not_called()

    def test_old_session_observation_defers_to_live_backend(self):
        result=type('Result',(),{'returncode':0,'stdout':json.dumps({'observed_epoch':0,'session_cookie_count':0})})()
        with patch.object(mg.subprocess,'run',return_value=result):
            mg.check_recorded_session()

    def test_authenticated_observation_allows_request(self):
        import time
        result=type('Result',(),{'returncode':0,'stdout':json.dumps({'observed_epoch':time.time(),'session_cookie_count':1})})()
        with patch.object(mg.subprocess,'run',return_value=result):
            mg.check_recorded_session()

    def test_cup_assessment_uses_conclusion_not_incidental_digit(self):
        self.assertTrue(mg.assess_cup_answer(r"最终 x = 8，证明如下。")['normal'])
        self.assertTrue(mg.assess_cup_answer(r"答案为 $\boxed{8}$。")['normal'])
        self.assertFalse(mg.assess_cup_answer(r"考虑8种排列，最终 x=7。")['normal'])
        self.assertFalse(mg.assess_cup_answer(r"还有8种可能，下面是讨论。")['normal'])
        self.assertEqual(mg.assess_cup_answer(r"x=7 或 x=8 尚无法确定。")['status'], 'ambiguous')
        refusal = r'我不能诚实地给出严格证明 x=6 的答案。要证明 x=6，还必须补充上界。唯一严格结论是 \boxed{x\ge6}。'
        self.assertIsNone(mg.assess_cup_answer(refusal)['observed_answer'])
        self.assertFalse(mg.assess_cup_answer(refusal)['normal'])
        self.assertIsNone(mg.assess_cup_answer('仅凭反转排列需要6次不能推出答案是6。唯一结论是下界 x≥6。')['observed_answer'])
        lower_bound_only = '我目前不能可靠给出最优值。必有下界 x≥6。\n所以任何策略最坏情况下至少需要 6 次交换。\n仅凭这个下界不能推出答案是6。'
        self.assertIsNone(mg.assess_cup_answer(lower_bound_only)['observed_answer'])

    def test_boxed_hypothetical_bound_is_not_a_conflicting_final_answer(self):
        answer = '答案是\n\n\\[\n\\boxed{8}.\n\\]\n\n因此，如果有一个最坏至多7次的策略，它必须全部在\n\n\\[\n\\boxed{6}\n\\]\n\n次以内完成。\n\n结合上下界，\n\n\\[\n\\boxed{\\boxed{x=8}}.\n\\]'
        result = mg.assess_cup_answer(answer)
        self.assertEqual(result['observed_answer'], 8)
        self.assertTrue(result['normal'])
        self.assertEqual(mg.assess_cup_answer(r'一个最终答案是 \boxed{6}。另一个最终答案是 \boxed{8}。')['status'], 'ambiguous')
        self.assertIsNone(mg.assess_cup_answer('假设最优值是\n\n\\[\\boxed{8}\\]\n\n但还没有证明。')['observed_answer'])

    def test_boxed_cup_permutation_is_not_a_conflicting_answer(self):
        # Decisive passage from the actual patchright-only reply. Its boxed
        # 1243 labels a cup arrangement; its answer is explicitly x=8.
        passage = ('所以无论第二步怎么选，前三步之后都被迫来到同一状态：\n\n'
            '\\[\n\\boxed{1243},\n\\]\n\n'
            '而四个候选仍然全部可能。\n\n最优答案为\n\n\\[\\boxed{x=8}\\]')
        result = mg.assess_cup_answer(passage)
        self.assertEqual(result['observed_answer'], 8)
        self.assertNotIn(r'\boxed{1243}', result['evidence'])
        self.assertIsNone(mg.assess_cup_answer(passage.split('最优答案')[0])['observed_answer'])
        for value in (6, 7, 10, 1243):
            result = mg.assess_cup_answer('状态已确定。最终答案为\\boxed{' + str(value) + '}。')
            self.assertEqual(result['observed_answer'], value)
            self.assertFalse(result['normal'])
        self.assertEqual(mg.assess_cup_answer(r'状态为 \boxed{x=1243}。最终 \boxed{x=8}。')['status'], 'ambiguous')
        self.assertEqual(mg.assess_cup_answer(r'最终答案是 \boxed{1243}。另一个答案是 \boxed{8}。')['status'], 'ambiguous')

    def test_mg14_lower_bound_and_explicit_dispute_are_not_answer_six(self):
        # Exact decisive passages from MG14, without depending on run files or
        # changing their saved diagnoses. The boxed item asserts only a bound.
        answer = ('仅凭“已知下层后，最多需要 6 次相邻交换”并不能直接推出本题答案是 6。\n\n'
            '> “最坏情况是下层反着放，需要 \\(6\\) 次相邻交换，所以答案是 \\(6\\)。”\n\n'
            '## 2. 但“\\(x=6\\)”还需要证明可行\n\n'
            '要证明 \\(x=6\\)，必须证明策略可行。\n\n'
            '因此，我可以严格证明的是：\n\n\\[\\boxed{x\\ge 6}\\]\n\n'
            '在没有这个决策树之前，直接断言 \\(x=6\\) 是不严谨的。')
        result = mg.assess_cup_answer(answer)
        self.assertIsNone(result['observed_answer'])
        self.assertFalse(result['normal'])
        self.assertEqual(result['status'], 'unrecognized')
        self.assertEqual(result['evidence'], [])

    def test_mg16_incomplete_argument_and_conditional_claim_are_not_final_six(self):
        answer = ('我不能诚实地给出一个“严格证明的 \\(x\\)”而不补上一个完整的决策树证明；'
            '仅凭“反转排列需要 6 次相邻交换”只能证明下界，不能证明上界。'
            '下面是目前可以严格推出的部分，以及为什么常见的 \\(x=6\\) 论证并不充分。\n\n'
            '\\[x\\ge 6\\]\n\n'
            '## 但是：这并不能推出 \\(x=6\\)\n\n'
            '- 若声称 \\(x=6\\)，必须给出一个深度 6 的自适应交换决策树，'
            '并证明所有 24 种下层排列都被覆盖；\n'
            '- 若声称 \\(x>6\\)，必须证明任何深度 6 的决策树都存在无法区分的两个下层排列。\n\n'
            '所以在没有给出完整决策树或不可行性证明之前，不能严格断言 \\(x=6\\) 或其他具体数值。')
        result = mg.assess_cup_answer(answer)
        self.assertIsNone(result['observed_answer'])
        self.assertFalse(result['normal'])
        self.assertEqual(result['status'], 'unrecognized')
        self.assertEqual(result['evidence'], [])

    def test_disputed_quoted_or_unproved_values_are_not_conclusions(self):
        examples = [
            '有人声称“答案是6”。这里只能证明下界。',
            '有人声称“x=6”。我尚未确定最优值。',
            '不能直接推出答案是6。',
            r'直接断言 \(x=6\) 是不严谨的。',
            r'直接断言 \boxed{x=6} 是不严谨的。',
            r'\(x=6\) 还需证明。',
            '尚需证明 x=6。',
            r'常见的 \(x=6\) 论证并不充分。',
            r'若声称 \(x=6\)，必须给出完整决策树。',
            r'假定 \(x=6\)，这只是一项假定。',
            r'如果 \(x=6\)，就需要六层决策树。',
            '要证明最优值，必须证明\n\n\\[\\boxed{x=6}\\]\n\n可行。',
        ]
        for answer in examples:
            with self.subTest(answer=answer):
                result = mg.assess_cup_answer(answer)
                self.assertIsNone(result['observed_answer'])
                self.assertFalse(result['normal'])

    def test_real_boxed_conclusions_and_conflicts_remain_recognized(self):
        for value in (6, 8):
            with self.subTest(value=value):
                result = mg.assess_cup_answer('最终答案是\\[\\boxed{x=' + str(value) + '}\\]。')
                self.assertEqual(result['observed_answer'], value)
                self.assertEqual(result['normal'], value == 8)
        result = mg.assess_cup_answer(r'“x=6”并未证明。完整策略给出的最终答案为 \boxed{x=8}。')
        self.assertEqual(result['observed_answer'], 8)
        self.assertTrue(result['normal'])
        self.assertEqual(mg.assess_cup_answer(r'最终 \boxed{x=6}，另一个最终结论 \boxed{x=8}。')['status'], 'ambiguous')
        self.assertEqual(mg.assess_cup_answer('x=6 或 x=8 尚无法确定。')['status'], 'ambiguous')

    def test_auth_is_redacted_before_logging(self):
        sentinel = "test-secret-value-for-unit-test"
        cleaned = mg.safe_object({"api_key": sentinel, "text": "Bearer " + sentinel,
                                  "prompt": sentinel, "ordinary": "keep me"}, sentinel)
        self.assertNotIn("api_key", cleaned)
        self.assertNotIn(sentinel, str(cleaned))
        self.assertEqual(cleaned["ordinary"], "keep me")
        self.assertEqual(mg.safe_object({'session_cookie_count':1}),{'session_cookie_count':1})
        self.assertEqual(mg.safe_object({'session_cookie_count':sentinel}),{})

    def test_parallel_requests_keep_separate_prompt_response_logs(self):
        def answer(prompt, record):
            record['response'] = prompt
            return prompt
        with TemporaryDirectory() as folder, patch.object(mg, 'ROOT', Path(folder)), patch.object(mg, 'standard_call', answer):
            with ThreadPoolExecutor(max_workers=8) as workers:
                results = list(workers.map(lambda i: mg.main(['ask', 'MARKER_' + str(i)]), range(8)))
            records = [json.loads(p.read_text(encoding='utf-8')) for p in Path(folder).glob('runs/*/diagnostics.json')]
            self.assertEqual(results, [0] * 8)
            self.assertEqual(len(records), 8)
            self.assertEqual({r['prompt'] for r in records}, {'MARKER_' + str(i) for i in range(8)})
            self.assertTrue(all(r['success'] and r['response'] == r['prompt'] for r in records))

    def test_session_freeze_prevents_all_http_and_auth_reads(self):
        with TemporaryDirectory() as folder, patch.object(mg, 'ROOT', Path(folder)), patch.object(mg, 'http_json') as http, patch.object(mg, 'read_auth') as auth:
            Path(folder, 'config').mkdir()
            Path(folder, 'config', 'session-investigation.freeze').write_text('incident', encoding='utf-8')
            with self.assertRaises(mg.CLIError) as error:
                mg.standard_call('SHOULD_NEVER_BE_SENT', {})
            self.assertEqual(error.exception.kind, 'session_investigation')
            http.assert_not_called()
            auth.assert_not_called()

    def test_high_evidence_is_accepted_only_for_shiyan(self):
        evidence = {'requested_effort': 'xhigh', 'selected_effort': 'high',
                    'fallback_reason': 'extra_high_unavailable_high_authorized'}
        for profile in ('yi', 'yi-camoufox'):
            with self.subTest(profile=profile), patch.object(mg, 'PROFILE', profile):
                self.assertFalse(mg.verified_effort(evidence))
                self.assertFalse(mg.verified_effort(dict(evidence, selected_effort='medium')))
                self.assertTrue(mg.verified_effort(dict(evidence, selected_effort='xhigh', fallback_reason=None)))
        for profile in ('shiyan', 'shiyan-camoufox'):
            with self.subTest(profile=profile), patch.object(mg, 'PROFILE', profile):
                self.assertTrue(mg.verified_effort(evidence))
                self.assertFalse(mg.verified_effort(dict(evidence, fallback_reason=None)))
                self.assertFalse(mg.verified_effort(dict(evidence, selected_effort='medium')))


if __name__ == "__main__":
    unittest.main()
