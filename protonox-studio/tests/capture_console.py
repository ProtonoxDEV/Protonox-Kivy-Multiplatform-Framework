#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import sys
import json
import time

url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173"
out = {"console": [], "pageerrors": [], "requests": []}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()

    def on_console(msg):
        try:
            loc = msg.location
        except Exception:
            loc = None
        out["console"].append({"type": msg.type, "text": msg.text, "location": loc})

    def on_pageerror(err):
        out["pageerrors"].append({"error": str(err)})

    def on_request_failed(req):
        out["requests"].append({"url": req.url, "failure": repr(req.failure)})

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)
    page.on("requestfailed", on_request_failed)

    print(f"Opening {url} and collecting console events...")
    page.goto(url)
    # give the page some time to run scripts and for async errors to surface
    time.sleep(3)
    screenshot = "/tmp/protonox_console.png"
    page.screenshot(path=screenshot, full_page=True)
    browser.close()

with open('/tmp/protonox_console.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Saved /tmp/protonox_console.json and /tmp/protonox_console.png')
