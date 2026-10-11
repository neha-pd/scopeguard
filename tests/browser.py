import asyncio,json,sys,tempfile
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 out=Path(__file__).resolve().parents[1]/'artifacts';out.mkdir(exist_ok=True)
 base=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8838'
 checks=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  context=await browser.new_context(viewport={'width':1440,'height':1100},permissions=['clipboard-read','clipboard-write'])
  page=await context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  await page.goto(base,wait_until='networkidle');await page.locator('h1').wait_for()
  await page.get_by_role('button',name='Compare requests').click()
  assert await page.locator('article').count()==4
  assert 'Contact form with email notifications' in await page.locator('article').nth(0).inner_text()
  assert await page.locator('input[name="decision-0"]:checked').input_value()=='review'
  assert 'No clear keyword overlap' in await page.locator('article').nth(1).inner_text()
  checks.append('Shared-word reference and unmatched request; all decisions initially require review')
  await page.locator('input[name="decision-0"][value="include"]').check()
  await page.locator('input[name="decision-1"][value="change"]').check()
  await page.locator('input[name="decision-3"][value="change"]').check()
  await page.get_by_role('button',name='Prepare change-request draft').click()
  assert 'No complete estimate supplied' in await page.locator('#draft-text').input_value()
  checks.append('Manual decisions feed draft; missing pricing never becomes an invented quote')
  await page.locator('#rate').fill('-10')
  assert await page.get_by_role('alert').is_visible()
  await page.locator('#rate').fill('20');await page.locator('#hours-1').fill('5')
  assert 'Estimate incomplete' in await page.locator('.estimate-total').inner_text()
  await page.locator('#hours-3').fill('3')
  assert '$160.00' in await page.locator('.estimate-total').inner_text()
  draft=await page.locator('#draft-text').input_value()
  assert '8 hours at USD 20.00/hour = $160.00' in draft
  assert 'ORIGINAL AGREED SCOPE' in draft and 'STILL TO CLARIFY' in draft
  checks.append('Negative and incomplete pricing rejected; valid user hours/rate calculate correctly')
  await page.get_by_role('button',name='Copy draft',exact=True).click()
  assert await page.evaluate('navigator.clipboard.readText()')==draft
  async with page.expect_download() as d:
   await page.get_by_role('button',name='Download .txt').click()
  download=await d.value
  assert download.suggested_filename=='scopeguard-change-request.txt'
  assert Path(await download.path()).read_text()==draft
  checks.append('Clipboard and downloaded text exactly match visible draft')
  await page.reload(wait_until='networkidle')
  assert await page.locator('input[name="decision-1"]:checked').input_value()=='change'
  assert await page.locator('#hours-1').input_value()=='5'
  assert '$160.00' in await page.locator('.estimate-total').inner_text()
  checks.append('Brief, decisions and estimates survive reload in local storage')
  await page.evaluate('window.scrollTo(0,0)')
  await page.wait_for_timeout(150)
  await page.screenshot(path=str(out/'scopeguard-desktop.png'),full_page=True)
  await page.locator('#scope').fill('A changed agreed scope')
  assert await page.get_by_role('button',name='Prepare change-request draft').is_disabled()
  checks.append('Editing source disables draft export until comparison refreshed')
  await page.get_by_role('button',name='Clear workspace',exact=True).click()
  await page.get_by_role('button',name='Keep working',exact=True).click()
  assert await page.locator('#scope').input_value()=='A changed agreed scope'
  await page.get_by_role('button',name='Clear workspace',exact=True).click()
  await page.get_by_role('button',name='Yes, clear',exact=True).click()
  assert await page.locator('#scope').input_value()==''
  await page.reload(wait_until='networkidle');assert await page.locator('#scope').input_value()==''
  checks.append('Reset confirmation/cancel and persistent clearing')
  await page.locator('#scope').fill('Contact form')
  await page.locator('#requests').fill('<img src=x onerror="window.xss=1"> contact form')
  await page.get_by_role('button',name='Compare requests').click()
  assert await page.locator('article img').count()==0
  assert await page.evaluate('window.xss') is None
  assert '<img src=x' in await page.locator('article h3').inner_text()
  checks.append('Untrusted request HTML renders as text, without script execution')
  await page.get_by_role('button',name='Load example',exact=True).click()
  await page.get_by_role('button',name='Compare requests').click()
  await page.set_viewport_size({'width':390,'height':844})
  assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  await page.evaluate('window.scrollTo(0,0)')
  await page.wait_for_timeout(150)
  await page.screenshot(path=str(out/'scopeguard-mobile.png'),full_page=True)
  checks.append('Mobile 390px layout without horizontal overflow')
  assert not errors,errors
  checks.append('No browser runtime or console errors')
  (out/'checks.json').write_text(json.dumps({'base_url':base,'checks':checks,'errors':errors},indent=2))
  print(json.dumps({'passed':len(checks),'checks':checks},indent=2))
  await browser.close()
asyncio.run(main())
