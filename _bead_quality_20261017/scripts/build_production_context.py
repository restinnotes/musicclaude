"""Restore inherited original headings without modifying any dispatched experimental input."""
from pathlib import Path
import json,hashlib
from build_v2 import COMMON,METHODS
R=Path(__file__).resolve().parents[1]
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,t):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and p.read_text(encoding='utf-8')!=t:raise ValueError('Production input is immutable: '+str(p))
 p.write_text(t,encoding='utf-8',newline='\n')
def main():
 units=j(R/'sources/units.json');index=j(R/'pools/POOL_INDEX.json');sources={x['src_id']:x for x in j(R/'sources/SOURCE_MANIFEST.json')['sources']}
 records={}
 for seg,spec in index.items():
  text=(R/f'pools/{seg}_FULL.txt').read_text(encoding='utf-8');restored=[]
  for e in spec['units']:
   u=units[e['uid']];heads=u.get('title_inherited',[])
   if heads:
    original=(R/sources[u['src']]['archive']).read_text(encoding='utf-8-sig')
    assert all(h in original for h in heads)
    body=u['text'].rstrip(); assert text.count(body)==1
    text=text.replace(body,'【以下为原文继承标题，不是新增研究】\n'+'\n'.join(heads)+'\n'+body,1)
    restored.append({'uid':u['uid'],'titles':heads})
  text=text.replace('codex exec luna_noweb (tool-free)', 'gpt-6-luna（CLI请求标识；旧int标签；实测有web_search）')
  put(R/f'production_context/pools/{seg}.txt',text)
  facts=R/f'audits/facts_{seg}.txt'
  prompt=COMMON+'\n'+METHODS['A2']+'\n\n【固定输入：30份已有A；全文加原文继承标题；来源标签已纠正】\n'+text+'\n\n【位置与事实校核】\n'+(facts.read_text(encoding='utf-8-sig') if facts.exists() else '')
  put(R/f'production_context/inputs/{seg}_A2.txt',prompt)
  records[seg]={'source_count':30,'experimental_pool_sha256':spec['pool_sha256'],'production_pool_sha256':sha(text.encode()),'restored_titles':restored,'body_rewritten':False,'route_changed':False,'metadata_correction':'Luna-int-3 web_search observed, not tool-free','prompt_sha256':sha(prompt.encode()),'prompt_bytes':len(prompt.encode())}
 put(R/'production_context/CONTEXT_REPAIR.json',json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'segments':14,'headings_restored':sum(len(x['restored_titles']) for x in records.values()),'max_prompt_bytes':max(x['prompt_bytes'] for x in records.values())},ensure_ascii=False))
if __name__=='__main__':main()
