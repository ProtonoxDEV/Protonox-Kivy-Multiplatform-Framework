from playwright.sync_api import sync_playwright
import sys, time, json

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4173"

print(f"Network ARC test against {URL}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    requests = []
    def on_request(req):
        try:
            if req.url.endswith('/__protonox'):
                print('REQUEST:', req.method, req.url)
                requests.append(req)
        except Exception as e:
            print('on_request error', e)

    page.on('request', on_request)

    def on_console(msg):
        print('PAGE LOG>', msg.type, msg.text)
    page.on('console', on_console)

    page.goto(URL)
    # Give the page more time to load scripts and for injected ARC to initialize
    page.wait_for_timeout(1200)
    content = page.content()
    print('ARC injected:', 'PROTONOX ARC MODE PROFESSIONAL' in content)

    # create a visible drop target to ensure reparenting can occur
    page.evaluate("""
    () => {
        let t = document.getElementById('__px_test_drop');
        if (!t) {
            t = document.createElement('div');
            t.id = '__px_test_drop';
            t.style.cssText = 'position:fixed;left:70%;top:40%;width:240px;height:160px;background:rgba(255,70,130,0.08);border:2px dashed #ff6ec7;z-index:99999999;';
            document.body.appendChild(t);
        }
        return true;
    }
    """)
    page.wait_for_timeout(200)

    # mark candidate element
    ok = page.evaluate("""
    () => {
            const els = [...document.querySelectorAll('*')].filter(e=> {
                const r = e.getBoundingClientRect();
                return r.width > 60 && r.height > 60 && e !== document.body && e !== document.documentElement && e.nodeType === 1;
            });
      if (els.length === 0) return false;
      const el = els[0];
      el.setAttribute('data-px-test','1');
      return true;
    }
    """)
    if not ok:
        print('No element for test')
        browser.close()
        sys.exit(2)

    el = page.locator('[data-px-test="1"]')
    box = el.bounding_box()
    cx = box['x'] + box['width']/2
    cy = box['y'] + box['height']/2
    print('Drag center', cx, cy)

    # Simulate Control+Drag (Protonox uses Ctrl activation)
    page.keyboard.down('Control')
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx+160, cy, steps=18)
    page.mouse.up()
    page.keyboard.up('Control')

    # Wait and poll for any `/__protonox` requests that may arrive asynchronously
    total_wait = 0
    while total_wait < 4000 and len(requests) == 0:
        page.wait_for_timeout(300)
        total_wait += 300

    # Inspect recorded requests
    print('Captured requests:', len(requests))
    for i, r in enumerate(requests[-10:], 1):
        try:
            print(i, r.method, r.url)
            # try to get post data
            post = r.post_data
            if post:
                try:
                    print('  BODY:', json.loads(post))
                except Exception:
                    print('  BODY RAW:', post[:200])
        except Exception as e:
            print('err', e)

    # Try forcing reparent via helper
    forced = page.evaluate('''() => (window.__protonox_test_reparent ? window.__protonox_test_reparent('[data-px-test="1"]', '#__px_test_drop') : false)''')
    print('forced helper returned', forced)

    # Save screenshot for later
    path = '/tmp/protonox_arc_network_test.png'
    page.screenshot(path=path, full_page=True)
    print('Saved screenshot to', path)

    browser.close()
