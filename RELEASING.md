# Releasing geotech-references

Pushing a release tag publishes the package to PyPI at once, and PyPI never
accepts the same version twice. So a release is made only with the owner's
word, from a tree that is already green on GitHub.

## 1. Before

- **Everything is merged:** every change for the release is on `main`.
- **`main` is green:** the latest "Tests" run on `main`'s head commit has
  passed (GitHub, Actions). To read it from a shell:

  ```
  curl -s "https://api.github.com/repos/soconnell345-geotech/geotech-references/actions/runs?per_page=5"
  ```

  Match the run by `head_sha`. The branch filter is not reliable.
- **Pick the version:**
  - **Patch** (x.y.Z): corrections only.
  - **Minor** (x.Y.0): new content, new keys, or a renamed key (the changelog
    says which).
  - **Major** (X.0.0): a removed function or a changed return type.

## 2. The release commit, on `main`

Four files can change:

- **`pyproject.toml`:** `version = "X.Y.Z"`. This is the only place the
  version is written; `importlib.metadata.version("geotech-references")`
  reads it.
- **`CHANGELOG.md`:** `## Unreleased` becomes `## X.Y.Z`. Below it goes
  `Released YYYY-MM-DD.`, then a short account of what a caller will notice,
  changed behaviour first. Read every entry once more against the merged code.
- **`README.md` and `CLAUDE.md`:** only if a count changed (functions,
  references, catalog totals).

```
git add pyproject.toml CHANGELOG.md README.md CLAUDE.md
git commit -m "X.Y.Z: <what the release is>"
git push origin HEAD:main
```

Wait until that commit's "Tests" run is green. (A commit that changes only
`.md` files starts no run, but the version change in `pyproject.toml` does.)

## 3. The tag, which publishes

```
git tag -a vX.Y.Z -m "geotech-references X.Y.Z" <release commit>
git push origin vX.Y.Z
```

The tag starts `.github/workflows/publish.yml`.

- **What it does:** builds the sdist and the wheel, and publishes them through
  PyPI trusted publishing. It runs in the `pypi` environment, and no token is
  stored in the repository.
- **What the wheel holds:** `geotech_references` only. It has no PDFs, no
  `agents/` and no tests.

## 4. Check

1. The "Publish to PyPI" run has passed.
2. PyPI reports the new version:

   ```
   curl -s https://pypi.org/pypi/geotech-references/json | python -c "import sys, json; print(json.load(sys.stdin)['info']['version'])"
   ```

3. A fresh environment installs it:

   ```
   pip install geotech-references==X.Y.Z
   python -c "import importlib.metadata as m; print(m.version('geotech-references'))"
   ```

If a release is wrong, publish a corrected patch version. Yank a release on
PyPI only if it gives wrong values.

## 5. The app follows

GeotechStaffEngineer uses the library in two ways, and both move together:

1. **The submodule:** move it to the new tag.

   ```
   cd geotech-references && git fetch --tags && git checkout vX.Y.Z && cd ..
   git add geotech-references
   ```

2. **The requirement:** in the app's `pyproject.toml`,
   `"geotech-references>=X.Y.Z"`.
3. **What the app builds from the library:** rebuild it with the submodule at
   the new tag first on `PYTHONPATH`. Today that is the user manual,
   `docs/user_manual/build_manual.py`, which
   `webapp/tests/test_user_manual_current.py` checks.
4. **The rest:** update the app's notes that record the pinned version, and
   run its tests on GitHub. Then release the app by its own `RELEASING.md`.

## As done for 1.7.0 (13 November 2026)

1. The review branch was merged, and its "Tests" run was green.
2. Release commit `0d0e6a1` changed `pyproject.toml`, `CHANGELOG.md` (the
   unreleased entries became 1.7.0, under a short account) and `README.md`.
3. Merged to `main` as `e1bbc5b`. "Tests" was green.
4. Tag `v1.7.0` was pushed. "Publish to PyPI" was green, and PyPI showed 1.7.0.
5. The app followed: its requirement became `>=1.7.0`, its submodule moved to
   `e1bbc5b`, and its user manual was rebuilt.
