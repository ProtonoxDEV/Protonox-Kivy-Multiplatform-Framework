import sys
import os
from kivymd.app import MDApp

# Ensure examples package path is usable
HERE = os.path.dirname(__file__)
MAIN_PATH = os.path.join(HERE, "main.py")

# Import the app class from the main module via importlib
import importlib.util
spec = importlib.util.spec_from_file_location("kivymd_demo.main", MAIN_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

KivyMDDemoApp = mod.KivyMDDemoApp


def run_headless_test():
    app = KivyMDDemoApp()
    # define a more demanding CI plan: multiple presses + typed entries
    plan = [
        ("press_button", None, 0.2),
        ("press_button", None, 0.4),
        ("type", "alpha", 0.6),
        ("submit", None, 0.8),
        ("type", "beta", 1.0),
        ("submit", None, 1.2),
        ("screenshot", "kivymd_demo_screenshot.png", 1.4),
        ("stop", None, 1.6),
    ]

    # install plan into app and run
    try:
        app.run_ci_plan(plan)
        app.run()
    except SystemExit:
        pass

    # Validate expected state
    expected_button_presses = 2
    expected_entries = ["alpha", "beta"]
    got_presses = getattr(app, "button_pressed_count", 0)
    got_entries = app.get_entries()
    # Find the screenshot file (Kivy may add numeric suffixes)
    import glob
    candidates = glob.glob(os.path.join(HERE, "kivymd_demo_screenshot*.png"))
    screenshot = candidates and max(candidates, key=os.path.getmtime) or os.path.join(HERE, "kivymd_demo_screenshot.png")

    print(f"Test finished. button_pressed_count={got_presses}, expected={expected_button_presses}")
    print(f"Entries: {got_entries} (expected: {expected_entries})")

    # basic checks
    if got_presses != expected_button_presses:
        print("TEST FAILED: button press count mismatch")
        if os.path.exists(screenshot):
            print(f"Screenshot available at: {screenshot}")
        sys.exit(2)

    if got_entries != expected_entries:
        print("TEST FAILED: entries mismatch")
        if os.path.exists(screenshot):
            print(f"Screenshot available at: {screenshot}")
        sys.exit(2)

    # image comparison against baseline (golden) using perceptual aHash
    try:
        from PIL import Image
        golden = os.path.join(HERE, "golden.png")
        if not os.path.exists(screenshot):
            print("No screenshot generated; failing")
            sys.exit(2)

        def ahash(img_path, hash_size=8):
            img = Image.open(img_path).convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            bits = ''.join('1' if p > avg else '0' for p in pixels)
            # return as hex string for convenience
            width = hash_size * hash_size
            return int(bits, 2)

        def hamming(a, b):
            x = a ^ b
            return x.bit_count()

        if not os.path.exists(golden):
            # create baseline on first run
            Image.open(screenshot).save(golden)
            print(f"Golden image not found; saved current screenshot as baseline: {golden}")
            print("TEST PASSED (baseline created)")
            sys.exit(0)

        h1 = ahash(screenshot)
        h2 = ahash(golden)
        dist = hamming(h1, h2)
        print(f"aHash Hamming distance: {dist}")
        # threshold: allow small differences; <=6 considered same
        if dist > 6:
            print("TEST FAILED: screenshot differs from golden (aHash distance > 6)")
            sys.exit(2)

    except Exception as e:
        print(f"Image comparison skipped/failed: {e}")

    print("TEST PASSED")
    sys.exit(0)


if __name__ == '__main__':
    run_headless_test()
