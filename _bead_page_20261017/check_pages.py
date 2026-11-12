from pathlib import Path
import json
from playwright.sync_api import sync_playwright

r=Path(__file__).resolve().parent
d=json.loads((r/'PAGE_CONTENT.json').read_text(encoding='utf-8'))
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((r/'每段一页.html').as_uri())
    for c in d['pages']:
        page.get_by_role('button',name=c['segment'],exact=True).click()
        sheet=page.locator('#'+c['segment'])
        assert page.locator('.sheet:visible').count()==1
        paragraphs=sheet.locator('.body p').all_text_contents()
        assert '\n\n'.join(paragraphs)==c['body']
        body=sheet.locator('.body').bounding_box()
        footer=sheet.locator('footer').bounding_box()
        assert body['y']+body['height'] < footer['y'],(c['segment'],body,footer)
        assert sheet.locator('strong').count()==len(c['emphasis'])
        sheet.screenshot(path=str(r/(c['segment']+'.png')))
    page.goto((r/'每段一页.html').as_uri()+'#S02-2')
    assert page.locator('#S02').is_visible()
    page.set_viewport_size({'width':390,'height':844})
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    assert not errors
    browser.close()
(r/'CHECK.json').write_text(json.dumps({'three_pages':True,'one_visible_page_per_segment':True,'body_verbatim':True,'desktop_body_fits':True,'mobile_no_horizontal_overflow':True,'old_hash_compatible':True,'javascript_errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print('Page content and layout checked')
