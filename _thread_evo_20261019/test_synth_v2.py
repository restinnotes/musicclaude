"""Offline regression checks for the failure modes fixed during the handover."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import synth_v2


class FlowTests(unittest.TestCase):
    def make(self):
        r=object.__new__(synth_v2.Run)
        r.T='test';r.w='op60';r.a='g6';r.b='g56';r.pool='test';r.backs=0
        r.segs=[{'id':f'S{i:02}','start':i,'end':i} for i in range(1,4)]
        r.beads=[{'id':f'S{i:02}-B1','sec':f'S{i:02}','role':'主体验','text':'感受'} for i in range(1,4)]
        r.state={};r.checkpoints={};r.rejected=[];r.status='running'
        r.mechs=lambda sec:[{'id':'M1','text':'解释'}]
        r.dir=Path(self.temp.name)
        return r

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp.cleanup()

    def pick(self,sec='S01',depends=None):
        bid=sec+'-B1'
        return {'eval':[{'id':'M1'}],'chosen':[{'text':'原因与后果','from':['M1'],'depends':depends or [],'explains':[bid]}],
                'fate':{bid:'第1条'},'new_history':[{'text':'有依据的经历','explains':[bid]}]}

    def test_missing_bead_and_future_history_fail(self):
        r=self.make();p=self.pick();p['fate']={};p['chosen'][0]['depends']=['H99']
        errors=r.validate_pick('S01',p)
        self.assertTrue(any('去处' in e for e in errors))
        self.assertTrue(any('未来' in e for e in errors))

    def test_valid_pick_and_fate_consistency(self):
        r=self.make();p=self.pick();self.assertEqual(r.validate_pick('S01',p),[])
        p['fate']['S01-B1']='第2条';self.assertTrue(r.validate_pick('S01',p))

    def test_failed_section_does_not_become_later_history(self):
        r=self.make();seen=[]
        r.restore=lambda:None
        def segment(sec):
            seen.append(sec);r.state[sec]={'pick':{},'check':{'pass':False},'hist':[]};return {},{'pass':False}
        r.segment=segment;r.back=lambda *a:False
        self.assertEqual(r.run(),'needs_revision:S01')
        self.assertEqual(seen,['S01'])

    def test_repair_rolls_back_every_downstream_change(self):
        r=self.make()
        for i in range(1,4):
            sec=f'S{i:02}';r.state[sec]={'pick':self.pick(sec),'check':{'pass':True},'chosen':[{'text':f'old{i}'}],
                                      'hist':[{'id':f'H{i}','sec':sec,'text':f'old{i}','explains':[sec+'-B1']}]}
        before=copy.deepcopy(r.state)
        r.pick_msg=lambda *a:'pick';r.check_msg=lambda *a:'check'
        r.call=lambda rid,*a:self.pick('S01') if rid.endswith('_A') else {'pass':True,'problems':[]}
        def segment(sec,tag):
            r.state[sec]={'changed':True};return {},{'pass':False}
        r.segment=segment
        self.assertFalse(r.repair('S01','S03','test'))
        self.assertEqual(r.state,before)
        self.assertEqual(r.rejected[-1]['why'],'下游 S02 未通过')

    def test_content_hash_prevents_stale_history_cache(self):
        r=self.make();names=[]
        with patch.object(synth_v2.evo,'done',lambda rid:(names.append(rid) or True)), patch.object(synth_v2.evo,'output',lambda rid:'{}'):
            r.call('S02_A','history one','g6',{})
            r.call('S02_A','history two','g6',{})
            r.call('S02_A','history one','g6',{})
        self.assertNotEqual(names[0],names[1]);self.assertEqual(names[0],names[2])

    def test_checker_cannot_pass_duplicate_or_missing_coverage(self):
        r=self.make();p=self.pick()
        review={'mechanisms':[{'index':1,'usable':True}],'section_pass':True,'problems':[],
                'coverage':[{'id':'S01-B1','status':'explained','why':'理由'}]}
        self.assertEqual(r.validate_check('S01',p,review),[])
        review['coverage']*=2
        self.assertTrue(r.validate_check('S01',p,review))
        review['coverage']=[{'id':'S01-B1','status':'missing','why':'主要体验未解释'}]
        self.assertTrue(r.validate_check('S01',p,review))


if __name__=='__main__':
    unittest.main()
