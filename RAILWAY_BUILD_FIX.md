# Railway Build Fix

If Railway fails during Python installation with a `mise python@3.11.9` GitHub attestation error, use a generic supported Python minor version instead of pinning an exact patch build.

Files included for Railway:

- `runtime.txt` -> `3.11`
- `.python-version` -> `3.11`
- `railway.json` start command -> `python railway_start.py`

Optional Railway Variables if the build still uses the old cached Python artifact:

```env
RAILPACK_PYTHON_VERSION=3.11
MISE_PYTHON_GITHUB_ATTESTATIONS=false
```

After changing these files or variables, trigger a fresh deployment.
