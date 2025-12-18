from playwright.sync_api import sync_playwright
import sys
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:4173'
print('Running ARC move test v2 against', URL)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(1000)
    content = page.content()
    print('ARC present:', 'PROTONOX ARC MODE PROFESSIONAL' in content)
    ok = page.evaluate('''
    () => {
      const els = [...document.querySelectorAll('*')].filter(e=> {
        const r = e.getBoundingClientRect();
        return r.width > 60 && r.height > 60 && r.width < 800 && r.height < 600 && e !== document.body && e.nodeType === 1;
      });
      if (els.length === 0) return false;
      const el = els[0];
      el.setAttribute('data-px-test','1');
      return true;
    }
    ''')
    if not ok:
        print('No suitable element found to drag.')
        browser.close()
        sys.exit(2)
    el = page.locator('[data-px-test="1"]')
    box = el.bounding_box()
    print('box=', box)
    cx = box['x'] + box['width']/2
    cy = box['y'] + box['height']/2
    page.keyboard.down('Alt')
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx+200, cy, steps=16)
    page.mouse.up()
    page.keyboard.up('Alt')
    page.wait_for_timeout(800)
    undo_count = page.locator('text=Undo').count()
    print('Undo buttons found:', undo_count)
    browser.close()
    sys.exit(0 if undo_count > 0 else 4)
