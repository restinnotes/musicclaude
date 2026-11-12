import asyncio,json
from patchright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.connect_over_cdp('http://127.0.0.1:9222'); page=b.contexts[0].pages[0]
  print('PATH',page.url.split('chatgpt.com')[-1])
  print('BUTTONS',json.dumps(await page.locator('button,[role=menuitemradio]').evaluate_all('els=>els.filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height).filter(e=>e.getBoundingClientRect().left>300).map(e=>({text:e.innerText,aria:e.getAttribute("aria-label"),testid:e.getAttribute("data-testid"),pressed:e.getAttribute("aria-pressed")}))')))
  print('TAIL',(await page.locator('body').inner_text())[-1600:])
  print('TEMP_DOM',json.dumps(await page.locator('[aria-label*="emporary"],[data-testid*="temporary"]').evaluate_all('els=>els.map(e=>e.outerHTML.slice(0,2500))')))
  await b.close()
asyncio.run(main())
