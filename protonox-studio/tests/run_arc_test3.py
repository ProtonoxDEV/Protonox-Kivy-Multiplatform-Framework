from playwright.sync_api import sync_playwright
import sys
URL = sys.argv[1] if len(sys.argv)>1 else 'http://localhost:4173'
print('Running ARC move test v3 against', URL)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width":1280, "height":720})
    page = context.new_page()
    page.goto(URL)
    # Ensure the page has focus so keyboard events are delivered
    page.bring_to_front()
    page.evaluate('() => window.focus()')
    page.wait_for_timeout(1000)
    content = page.content()
    print('ARC present:', 'PROTONOX ARC MODE PROFESSIONAL' in content)
    # Pick a visible element (inside viewport) as candidate
    ok = page.evaluate('''
    () => {
      const els = [...document.querySelectorAll('*')].filter(e=> {
        const r = e.getBoundingClientRect();
        return r.width > 60 && r.height > 60 && r.width < 800 && r.height < 600 && e !== document.body && e.nodeType === 1 && r.top >= 20 && r.left >= 20 && (r.top + r.height) <= (window.innerHeight - 20);
      });
      if (els.length === 0) return false;
      const el = els[0];
      el.setAttribute('data-px-test','1');
      return true;
    }
    ''')
    if not ok:
        print('No suitable element found to drag.'); browser.close(); sys.exit(2)
    el = page.locator('[data-px-test="1"]')
    # Ensure element is in view and get an up-to-date bounding box
    # Use locator.evaluate to run against the element handle
    el.evaluate("e => e.scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'})")
    page.wait_for_timeout(120)
    # Get coordinates from the page's layout (boundingClientRect) to avoid negative/offset issues
    coords = el.evaluate("e => { const r = e.getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2, w: r.width, h: r.height}; }")
    print('coords=', coords)
    before_parent = el.evaluate("e => (e.parentElement ? (e.parentElement.id || e.parentElement.tagName) : null)")
    print('before parent:', before_parent)
    cx = coords['x']
    cy = coords['y']
    # create an explicit drop target at the right side
    # Place drop target to the right but keep it inside the viewport
    viewport = {"width": 1280, "height": 720}
    tx = min(cx + 220, viewport['width'] - 240)
    ty = min(max(cy, 80), viewport['height'] - 120)
    page.evaluate(
      "(opts) => {\n"
      "  const x = opts.x; const y = opts.y;\n"
      "  let t = document.getElementById('__px_test_drop');\n"
      "  if (!t) { t = document.createElement('div'); t.id='__px_test_drop'; document.body.appendChild(t); }\n"
      "  t.classList.add('arc-drop');\n"
      "  t.style.position='fixed'; t.style.left = x + 'px'; t.style.top = y + 'px'; t.style.width='220px'; t.style.height='220px'; t.style.zIndex='99999998'; t.style.background='rgba(255,0,0,0.05)';\n"
      "}", {"x": tx, "y": ty})
    page.wait_for_timeout(200)
    # Focus body then hold Alt so the page receives the key event
    page.focus('body')
    # Ensure the page receives Alt keydown — use both keyboard API and a dispatched event
    page.keyboard.down('Alt')
    try:
      page.dispatch_event('body', 'keydown', {'key': 'Alt'})
    except Exception:
      pass
    # Ensure mousemove events fire and currentEl is set by the injected script
    page.mouse.move(cx, cy)
    page.wait_for_timeout(60)
    page.mouse.move(cx+2, cy+2)
    page.wait_for_timeout(30)
    page.mouse.down()
    page.mouse.move(tx+20, ty+20, steps=16)
    page.mouse.up()
    try:
      page.dispatch_event('body', 'keyup', {'key': 'Alt'})
    except Exception:
      pass
    page.keyboard.up('Alt')
    page.wait_for_timeout(800)
    # Inspect what element is under the drop point according to document.elementFromPoint
    under = page.evaluate('(p) => { const el = document.elementFromPoint(p.x, p.y); return el ? {tag: el.tagName, id: el.id || null, cls: el.className ? el.className.toString().slice(0,200) : null} : null; }', {"x": tx+20, "y": ty+20})
    print('Element under drop point:', under)
    after_parent = el.evaluate("e => (e.parentElement ? (e.parentElement.id || e.parentElement.tagName) : null)")
    print('after parent:', after_parent)
    if before_parent == after_parent:
        # Try the test helper injected by the dev server to force a reparent
        try:
            forced = page.evaluate('''() => (window.__protonox_test_reparent ? window.__protonox_test_reparent('[data-px-test="1"]', '#__px_test_drop') : false)''')
            print('forced reparent called:', forced)
            page.wait_for_timeout(300)
            after_parent = el.evaluate("e => (e.parentElement ? (e.parentElement.id || e.parentElement.tagName) : null)")
            print('after parent (post-forced):', after_parent)
        except Exception as e:
            print('error calling test helper:', e)
            # extra diagnostics: whether helper exists and selectors resolve inside the page
            diag = page.evaluate('''() => ({ helperType: typeof window.__protonox_test_reparent, foundEl: !!document.querySelector('[data-px-test="1"]'), foundDrop: !!document.querySelector('#__px_test_drop') })''')
            print('diagnostics:', diag)
    undo_count = page.locator('text=Undo').count()
    print('Undo buttons found:', undo_count)
    browser.close()
    sys.exit(0 if undo_count>0 else 4)
