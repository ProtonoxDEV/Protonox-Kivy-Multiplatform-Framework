Publishing to PyPI (GitHub Actions)

1) Add the PyPI API token as a repository secret:
   - Go to your repository: Settings → Secrets and variables → Actions → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: the full token you copied from PyPI (including the `pypi-` prefix)

2) How the workflow is triggered:
   - The workflow runs when you create a **GitHub Release** (type `published`).
   - Alternative: push an annotated tag like `v0.1.1` and create a release from it.
     Example local commands:
       git tag -a v0.1.1 -m "Release v0.1.1"
       git push origin v0.1.1

3) What the workflow does:
   - Builds `sdist` and `wheel` with `python -m build`
   - Runs `python -m twine check dist/*` to validate distributions
   - Uploads artifacts to PyPI using `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=$PYPI_API_TOKEN`

4) If you prefer to upload locally instead of using CI, run these commands locally (keep the token secret):
   export TWINE_USERNAME="__token__"
   export TWINE_PASSWORD="pypi-<YOUR_TOKEN>"
   python3 -m twine upload dist/*

---
If you want, I can (after you add the secret and create a release) verify the workflow run and confirm the package is available on PyPI and prepare a release note draft.