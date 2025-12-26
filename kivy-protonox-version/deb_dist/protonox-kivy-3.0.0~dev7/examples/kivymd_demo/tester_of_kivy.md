KivyMD Demo (protonox-kivy)
=============================

This example demonstrates a minimal KivyMD app compatible with KivyMD 1.x
and includes a small headless test runner to exercise UI actions automatically.

Files
- `main.py`: The app implementation. Exposes programmatic helpers for CI.
- `test_runner.py`: Runs the app headless, presses the demo button, takes a screenshot, and validates state.
- `requirements.txt`: Example-specific requirements.

Quick run (using the QA venv created earlier):

```bash
source /tmp/protonox-qa/bin/activate
pip install --no-cache-dir "kivymd>=1.1.1"
# Run interactively
python kivy-protonox-version/examples/kivymd_demo/main.py
# Run CI-style headless test (use xvfb on headless hosts)
xvfb-run -s "-screen 0 1024x768x24" python kivy-protonox-version/examples/kivymd_demo/test_runner.py
```

Test runner behavior
- Schedules a button press after 0.5s
- Saves a screenshot as `kivymd_demo_screenshot.png` after 1.0s
- Stops the app after 1.5s
- Exits with code 0 on success, 2 on mismatch
