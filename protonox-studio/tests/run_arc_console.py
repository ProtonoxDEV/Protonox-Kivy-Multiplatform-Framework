from playwright.sync_api import sync_playwright
import sys
URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4173"
print('Debug with console logs against', URL)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.on('console', lambda msg: print('PAGE LOG>', msg.type, msg.text))
    page.goto(URL)
    page.wait_for_timeout(1000)
    page.screenshot(path='/tmp/protonox_console_before.png', full_page=True)
    page.evaluate("""
    () => { document.querySelectorAll('[data-px-test]').forEach(e=>e.removeAttribute('data-px-test')); }
    """)
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
    print('marked ok=', ok)
    el = page.locator('[data-px-test="1"]')
    box = el.bounding_box()
    print('box=', box)
    cx = box['x'] + box['width']/2
    cy = box['y'] + box['height']/2
    tx = cx + 220
    ty = cy
    page.evaluate('(opts)=>{let t=document.getElementById("__px_test_drop"); if(!t){t=document.createElement("div");t.id="__px_test_drop";document.body.appendChild(t);} t.classList.add("arc-drop"); t.style.position="fixed"; t.style.left=opts.x+"px"; t.style.top=opts.y+"px"; t.style.width="220px"; t.style.height="220px"; t.style.zIndex="99999998"; t.style.background="rgba(255,0,0,0.05)"}', {"x": tx, "y": ty})
    page.wait_for_timeout(200)
    page.keyboard.down('Alt')
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(tx+20, ty+20, steps=16)
    page.mouse.up()
    page.keyboard.up('Alt')
    page.wait_for_timeout(800)
    page.screenshot(path='/tmp/protonox_console_after.png', full_page=True)
    print('done, saved screenshots')
    browser.close()
    print('browser closed')
