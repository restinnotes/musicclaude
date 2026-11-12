import json
import unittest
from summarize_final_stream import summarize


def stream(*frames):
    return ('\n'.join('data: ' + json.dumps(frame) for frame in frames) + '\ndata: [DONE]\n').encode()


class FinalSummaryTests(unittest.TestCase):
    def test_only_final_not_analysis_or_user(self):
        raw = stream({'p':'','o':'add','v':{'message':{'author':{'role':'user'},'content':{'parts':['private-user']}}}},
            {'v':{'message':{'author':{'role':'assistant'},'channel':'analysis','content':{'parts':['private-analysis']}}}},
            {'v':{'message':{'author':{'role':'assistant'},'channel':'final','content':{'content_type':'text','parts':['{}']}}}},
            {'o':'patch','v':[{'p':'/message/status','o':'add','v':'finished_successfully'},
                {'p':'/message/end_turn','o':'add','v':True}]})
        result = summarize(raw)
        self.assertEqual(result['parse_or_patch_errors'], 0)
        self.assertEqual(len(result['finals']), 1)
        self.assertEqual(result['finals'][0]['text_characters'], 2)
        self.assertTrue(result['finals'][0]['json_valid'])
        self.assertNotIn('private', json.dumps(result))

    def test_inherited_append_and_terminal_patch(self):
        raw = stream({'p':'','o':'add','v':{'message':{'author':{'role':'assistant'},'channel':'final',
            'content':{'content_type':'text','parts':['']}}}},
            {'p':'/message/content/parts/0','o':'append','v':'{'}, {'v':'}'},
            {'o':'patch','v':[{'p':'/message/status','o':'add','v':'finished_successfully'}]})
        result = summarize(raw)
        self.assertEqual(result['parse_or_patch_errors'], 0)
        self.assertTrue(result['finals'][0]['json_valid'])

    def test_empty_final_is_not_confused_with_done(self):
        result = summarize(stream({'p':'','o':'add','v':{'message':{'author':{'role':'assistant'},
            'channel':'final','content':{'content_type':'text','parts':['']},
            'status':'finished_successfully','end_turn':True}}}))
        self.assertTrue(result['done'])
        self.assertEqual(result['finals'][0]['text_characters'], 0)

    def test_bad_patch_is_reported(self):
        result = summarize(stream({'p':'/missing/path','o':'append','v':'secret'}))
        self.assertEqual(result['parse_or_patch_errors'], 1)
        self.assertNotIn('secret', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
