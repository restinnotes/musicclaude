import asyncio,json
from patchright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.connect_over_cdp('http://127.0.0.1:9222'); page=b.contexts[0].pages[0]
  print(json.dumps(await page.locator('[contenteditable=true]').evaluate_all('els=>els.map(e=>({visible:!!(e.getBoundingClientRect().width&&e.getBoundingClientRect().height),id:e.id,aria:e.getAttribute("aria-label"),length:e.innerText.length}))')))
  await b.close()
asyncio.run(main())
