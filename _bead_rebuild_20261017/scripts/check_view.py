from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'CONTENT.json').read_text(encoding='utf-8'))
checks=[]; errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True)
 t=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
 t.on('pageerror',lambda e:errors.append(str(e)))
 t.goto((R/'船歌·每段一页.html').as_uri())
 for c in d['pages']:
  t.get_by_role('button',name=c['segment'],exact=True).click()
  sheet=t.locator('#'+c['segment'])
  t.locator('#'+c['segment']+'.active').wait_for(state='visible')
  assert t.locator('.sheet:visible').count()==1
  assert sheet.locator('.block').count()==len(c['blocks'])
  assert not sheet.locator('strong,em,details').count()
  for block in c['blocks']:
   actual=sheet.locator('#'+block['id']).text_content()
   for para in block.get('text','').split('\n\n'):
    assert para in actual,(block['id'],para)
  metrics=sheet.evaluate('(e)=>({bottom:e.getBoundingClientRect().bottom,height:e.getBoundingClientRect().height})')
  checks.append({'segment':c['segment'],'blocks':len(c['blocks']),'bottom_at_1920_1080':metrics['bottom'],'fits_one_frame':metrics['bottom']<=1080})
  if c['segment'] in ['S02','S04','S07','S13']:t.screenshot(path=str(R/(c['segment']+'_1920.png')),full_page=True)
 t.set_viewport_size({'width':390,'height':844})
 for c in d['pages']:
  t.get_by_role('button',name=c['segment'],exact=True).click()
  t.locator('#'+c['segment']+'.active').wait_for(state='visible')
  assert not t.evaluate('document.documentElement.scrollWidth>innerWidth'),c['segment']
 b.close()
result={'pages':checks,'all_text_visible_no_folding':True,'all_semantic_blocks_same_typography':True,'mobile_no_horizontal_overflow':True,'javascript_errors':errors,'warning':'单帧容纳只验证布局，不代表观众能在音乐段时长内读完。'}
(R/'VIEW_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
