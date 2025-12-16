from playwright.sync_api import sync_playwright
import sys, time
URL = sys.argv[1] if len(sys.argv)>1 else 'http://localhost:4173'
print('Debug run against', URL)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(1000)
    page.screenshot(path='/tmp/protonox_before.png', full_page=True)
    content_before = page.content()
    open('/tmp/protonox_before.html','w',encoding='utf-8').write(content_before)
    print('Saved before snapshot')
    ok = page.evaluate("""
    () => {
      const els = [...document.querySelectorAll('*')].filter(e=> {
        const r = e.getBoundingClientRect();
        return r.width > 60 && r.height > 60 && e !== document.body && e.nodeType === 1;
      });
      if (els.length === 0) return false;
      const el = els[0];
      el.setAttribute('data-px-test','1');
      return true;
    }
    """)
    if not ok:
        print('No element')
        browser.close(); sys.exit(2)
    el = page.locator('[data-px-test="1"]')
    box = el.bounding_box()
    print('box=',box)
    cx = box['x'] + box['width']/2
    cy = box['y'] + box['height']/2
    page.keyboard.down('Alt')
    page.mouse.move(cx,cy)
    page.mouse.down()
    page.mouse.move(cx+140, cy, steps=12)
    page.mouse.up()
    page.keyboard.up('Alt')
    page.wait_for_timeout(1000)
    page.screenshot(path='/tmp/protonox_after.png', full_page=True)
    content_after = page.content()
    open('/tmp/protonox_after.html','w',encoding='utf-8').write(content_after)
    print('Saved after snapshot and screenshots')
    # also capture console logs
    browser.close()
    print('Done')
