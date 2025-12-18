from playwright.sync_api import sync_playwright
import sys

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4173"

print(f"Running ARC move test against {URL}")

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=False)
    except Exception as e:
        print("Failed to launch browser:", e)
        raise
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(1000)

    content = page.content()
    if 'PROTONOX ARC MODE PROFESSIONAL' not in content:
        print("ARC inject string not found in page content. The script might not be injected.")
    else:
        print("ARC inject string found in page content.")

    # Find a candidate element with a bounding box > 60x60 and mark it for the test
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
        print("No suitable element found to drag. Test aborting.")
        browser.close()
        sys.exit(2)

    el = page.locator('[data-px-test="1"]')
    box = el.bounding_box()
    if not box:
        print("Could not get bounding box for element.")
        browser.close()
        sys.exit(3)

    cx = box['x'] + box['width'] / 2
    cy = box['y'] + box['height'] / 2

    print(f"Element center: {cx},{cy}. Performing Alt+Drag...")

    # Use Ctrl modifier (Brave/WM may intercept Alt). Use Ctrl down to simulate.
    page.keyboard.down('Control')
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx + 140, cy, steps=12)
    page.mouse.up()
    page.keyboard.up('Control')

    page.wait_for_timeout(800)

    # Check for mini-toolbar that contains 'Undo' text
    undo_count = page.locator('text=Undo').count()
    print(f"Undo buttons found: {undo_count}")
    if undo_count > 0:
        print("SUCCESS: Mini-toolbar detected after drag (Undo present).")
        browser.close()
        sys.exit(0)
    else:
        print("FAIL: Mini-toolbar not detected. The drag might not have triggered reparenting.")
        browser.close()
        sys.exit(4)
