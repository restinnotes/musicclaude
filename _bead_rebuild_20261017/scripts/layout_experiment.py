from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'CONTENT.json').read_text(encoding='utf-8'))
style='@media(min-width:1700px){.blocks{display:block;column-count:4;column-gap:26px}.block{break-inside:avoid;margin-bottom:14px}}'
out=[]
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True);t=b.new_page(viewport={'width':1920,'height':1080})
 t.goto((R/'船歌·每段一页.html').as_uri());t.add_style_tag(content=style)
 for c in d['pages']:
  t.get_by_role('button',name=c['segment'],exact=True).click()
  t.locator('#'+c['segment']+'.active').wait_for(state='visible')
  out.append({'segment':c['segment'],'masonry_bottom':t.locator('.sheet.active').bounding_box()['height']+t.locator('.sheet.active').bounding_box()['y']})
 t.get_by_role('button',name='S02',exact=True).click();t.locator('#S02.active').wait_for(state='visible');t.screenshot(path=str(R/'layout_columns_S02.png'),full_page=True)
 b.close()
(R/'LAYOUT_EXPERIMENT.json').write_text(json.dumps({'same_content_same_font':True,'column_style':style,'metrics':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out))
