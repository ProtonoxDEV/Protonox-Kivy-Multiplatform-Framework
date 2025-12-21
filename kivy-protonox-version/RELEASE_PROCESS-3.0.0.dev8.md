# Release process log — protonox-kivy 3.0.0.dev8

Date: 2025-12-20

Summary:
- Built and uploaded source distribution (sdist) for `protonox-kivy==3.0.0.dev8` from `kivy-protonox-version`.
- Attempted to upload built linux wheel; PyPI rejected the platform-specific wheel tag. Uploaded only the sdist.

Artifacts:
- sdist: dist/protonox_kivy-3.0.0.dev8.tar.gz
- wheel (local): dist/protonox_kivy-3.0.0.dev8-cp312-cp312-linux_x86_64.whl (not uploaded)

PyPI:
- View at: https://pypi.org/project/protonox-kivy/3.0.0.dev8/

Notes / Next steps:
- Build manylinux-compatible wheels (use `cibuildwheel` / manylinux Docker) and upload them.
- Rebuild `.deb` for dev8 with updated defaults and copy to `deb_artifacts/`.
- Tag & push the release (tag created locally by this commit). Consider pushing and creating the GitHub release.

Build log excerpt:
```
Wheel upload failed: Binary wheel has an unsupported platform tag 'linux_x86_64'.
Uploaded sdist successfully.
```

Recorded-by: automated release helper
