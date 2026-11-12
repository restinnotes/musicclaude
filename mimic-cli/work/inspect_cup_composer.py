import asyncio,json
from patchright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.connect_over_cdp('http://127.0.0.1:9222'); page=b.contexts[0].pages[0]
  e=page.locator('[contenteditable=true]:visible').first
  print(json.dumps(await e.evaluate('e=>({innerText:e.innerText,textContent:e.textContent,html:e.innerHTML,tag:e.tagName,role:e.getAttribute("role")})'),ensure_ascii=False))
  await b.close()
asyncio.run(main())
