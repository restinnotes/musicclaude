"""Regression for the observed same-prompt cross-model recovery race; entirely offline."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import evo

class Matching(unittest.TestCase):
 def test_model_and_empty_attachments_are_part_of_identity(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);stamp=time.time();prompt='identical review text'
   for name,model,attachments,offset in [('first','gpt-6-thinking',[],0),('newer','gpt-5-6-thinking',[],1),('attached','gpt-6-thinking',[{'sha256':'different'}],2)]:
    p=root/('pro-bridge-'+name);p.mkdir();(p/'prompt.txt').write_text(prompt,encoding='utf-8')
    (p/'result.json').write_text(json.dumps({'model':model}),encoding='utf-8')
    (p/'attachment-manifest.json').write_text(json.dumps(attachments),encoding='utf-8');os.utime(p,(stamp+offset,stamp+offset))
   with patch.object(evo,'GPT3_RUNS',root):
    self.assertEqual(Path(evo.find_job(prompt,stamp,model='gpt-6-thinking')).name,'pro-bridge-first')
    self.assertEqual(Path(evo.find_job(prompt,stamp,model='gpt-5-6-thinking')).name,'pro-bridge-newer')
    self.assertIsNone(evo.find_job(prompt,stamp,model='unknown-model'))

if __name__=='__main__':unittest.main()
