from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((root/'分镜与异质性预览.html').as_uri())
    assert page.locator('#stage h2').inner_text()=='肩膀贴着肩膀，声音放得极低。'
    page.get_by_role('button',name='下一张',exact=True).click()
    assert '千言万语' in page.locator('#stage h2').inner_text()
    page.screenshot(path=str(root/'audits/preview_S02.png'),full_page=True)
    page.locator('#stage').screenshot(path=str(root/'audits/frame_S02.png'))
    page.get_by_role('button',name='S07 · 51–61',exact=True).click()
    assert '决定睡了' in page.locator('#stage').inner_text()
    page.locator('#altbox summary').click()
    assert page.locator('#alternatives').is_visible()
    page.get_by_role('button',name='S13 · 103–110',exact=True).click()
    page.screenshot(path=str(root/'audits/preview_S13.png'),full_page=True)
    page.locator('#stage').screenshot(path=str(root/'audits/frame_S13.png'))
    assert not page.locator('#altbox').is_visible()
    page.set_viewport_size({'width':390,'height':844})
    page.get_by_role('button',name='S02 · 4–16',exact=True).click()
    page.screenshot(path=str(root/'audits/preview_mobile.png'),full_page=True)
    overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
    assert not overflow
    page.goto((root/'异质性逐条核对.html').as_uri())
    assert page.locator('.card').count()==213
    page.locator('#seg').select_option('S14')
    page.locator('#status').select_option('omitted')
    assert page.locator('.card').count()==4
    page.locator('#search').fill('结束')
    assert page.locator('.card').count()>=1
    page.locator('.card details summary').first.click()
    assert page.locator('.card blockquote').first.is_visible()
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.set_viewport_size({'width':1440,'height':1000})
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(root/'audits/audit_filtered.png'),full_page=True)
    assert not errors
    browser.close()
(root/'audits/PREVIEW_CHECK.json').write_text(json.dumps({'passed':True,'javascript_errors':errors,'mobile_horizontal_overflow':overflow,'checks':['3 case switches','frame navigation','alternate path expansion','hidden unavailable alternatives','390px viewport','screenshots rendered','213 audit rows','segment and status filters','text search','original quote expansion'],'not_tested':['audio sync','human attention','reading speed','viewer comprehension']},ensure_ascii=False,indent=2),encoding='utf-8')
print('preview checks passed')
