from playwright.sync_api import sync_playwright
import sys, json

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4173"

print(f"Diagnosing ARC on {URL}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(URL)
    page.wait_for_timeout(800)

    # inject drop target
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
    page.wait_for_timeout(120)

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

    info = page.evaluate('''() => {
      const diag = { helperType: typeof window.__protonox_test_reparent, helperExists: !!window.__protonox_test_reparent };
      diag.foundEl = !!document.querySelector('[data-px-test="1"]');
      const el = document.querySelector('[data-px-test="1"]');
      if (el) {
        const r = el.getBoundingClientRect();
        diag.el = { tag: el.tagName, id: el.id || null, classes: el.className || null, rect: { x: r.x, y: r.y, w: r.width, h: r.height } };
      }
      diag.foundDrop = !!document.getElementById('__px_test_drop');
      const d = document.getElementById('__px_test_drop');
      if (d) { const rd = d.getBoundingClientRect(); diag.dropRect = { x: rd.x, y: rd.y, w: rd.width, h: rd.height }; }
      // attempt to call helper and capture result or error
      try {
        const res = window.__protonox_test_reparent ? window.__protonox_test_reparent('[data-px-test="1"]', '#__px_test_drop') : null;
        diag.helperCall = { result: res };
      } catch (e) {
        diag.helperCall = { error: String(e) };
      }
      return diag;
    }''')

    print('DIAG:', json.dumps(info, indent=2))

    path = '/tmp/protonox_arc_diagnose.png'
    page.screenshot(path=path, full_page=True)
    print('Saved screenshot to', path)

    browser.close()

