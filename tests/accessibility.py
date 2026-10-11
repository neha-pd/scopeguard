import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch();page=await b.new_page(viewport={'width':1440,'height':1000});await page.goto(sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8838');await page.get_by_role('button',name='Compare requests').click();await page.add_script_tag(path=sys.argv[2]);out={}
  for theme in ['light','dark']:
   await page.emulate_media(color_scheme=theme);await page.wait_for_timeout(350);out[theme]=await page.evaluate('async()=> (await axe.run()).violations');await page.screenshot(path=str(Path(__file__).resolve().parents[1]/'artifacts'/f'scopeguard-{theme}.png'),full_page=True)
  (Path(__file__).resolve().parents[1]/'artifacts/axe.json').write_text(json.dumps(out,indent=2));print({k:[(v['id'],[(n['target'],n.get('failureSummary')) for n in v['nodes']]) for v in vals] for k,vals in out.items()});await b.close()
asyncio.run(main())
