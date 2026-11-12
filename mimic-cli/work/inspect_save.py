import asyncio,json
from patchright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.connect_over_cdp('http://127.0.0.1:9222'); page=b.contexts[0].pages[0]
  save=page.get_by_role('button',name='Save chat',exact=True)
  print('SAVE_HTML',await save.evaluate('(e)=>e.parentElement.outerHTML'))
  await save.hover(); await asyncio.sleep(.7)
  print('TOOLTIP',json.dumps(await page.get_by_role('tooltip').all_text_contents()))
  await page.screenshot(path='/app/state/mg-after-inspect.png')
  await b.close()
asyncio.run(main())
