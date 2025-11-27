# Build Pipeline

Suggested CI/CD stages for Protonox apps:

1. **Lint & type-check**: Run `ruff`/`flake8` and `mypy` on app sources.
2. **Unit tests**: Execute `pytest` for business logic modules.
3. **Desktop package**: Build Linux/Windows artifacts via `tools/build_linux.sh` or `tools/build_windows.sh`.
4. **Android package**: Build release APK/AAB with `tools/build_android.sh` and sign using secure keystores.
5. **Upload artifacts**: Publish to your distribution channels (Play Store, private repo, etc.).
6. **Smoke tests**: Automate minimal UI flows using `adb` or desktop UI automation.
7. **Promotion**: Tag releases and generate changelogs.

Use environment variables or secret managers to inject Firebase and backend credentials during CI.
