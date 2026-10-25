# Releasing

Releases are fully automated by [.github/workflows/release.yaml](.github/workflows/release.yaml).
Pushing a version tag tests, builds, and publishes the package to
[PyPI](https://pypi.org/project/promcraft/) and creates a GitHub Release with the
built files attached.

## Cutting a release

1. Make sure everything to be released is merged into `main` and the `Pytest`
   workflow is green on `main`.

2. Pick the version following [Semantic Versioning](https://semver.org/). Pre-releases
   use [PEP 440](https://peps.python.org/pep-0440/) suffixes, e.g. `1.0.0rc1`.

3. Tag the `main` commit and push the tag:

   ```bash
   git switch main
   git pull
   git tag v0.7.0
   git push origin v0.7.0
   ```

4. Watch the run under **Actions → Publish to PyPI**. When it finishes, the new
   version is on PyPI and on the repository's **Releases** page.

Do not edit `version` in `pyproject.toml`. It is a placeholder; the workflow sets the
real version from the tag (`v0.7.0` → `0.7.0`) before building.

Only tags matching `v<major>.<minor>.<patch>` (optionally followed by a suffix, such as
`v1.0.0rc1`) start a release. Any other tag is ignored.

## What the workflow does

| Job | What it does | Permissions |
| --- | --- | --- |
| `test` | Runs the full `Pytest` workflow (Python 3.11–3.15: tests, mypy, ruff). | `contents: read` |
| `build` | Sets the version from the tag, runs `poetry build`, uploads `dist/` as an artifact. | `contents: read` |
| `publish` | Downloads `dist/` and uploads it to PyPI via trusted publishing (OIDC, no API token). Runs in the `pypi` environment. | `id-token: write` |
| `github-release` | Downloads the same `dist/` and creates a GitHub Release for the tag with generated notes. Pre-release and dev tags (`a`, `b`, `rc`, `.dev`, ...) are marked as pre-releases. | `contents: write` |

Each job runs only if the previous one succeeded, so a failing test stops the release
before anything is published.

## One-time setup

These are already configured; they are listed here in case they need to be recreated.

- **PyPI trusted publisher** for the `promcraft` project (PyPI → project → *Publishing*):
  owner `xbabka01`, repository `promcraft`, workflow `release.yaml`, environment `pypi`.
- **GitHub environment** named `pypi` (repository *Settings → Environments*). Add
  protection rules, such as required reviewers, here if releases should need approval.

Renaming the workflow file or the environment breaks publishing until the trusted
publisher on PyPI is updated to match.

## When something goes wrong

- **`test` or `build` failed.** Nothing was published. Fix the problem on `main`, then
  move the tag to the fixed commit and push it again:

  ```bash
  git tag -d v0.7.0
  git push origin :refs/tags/v0.7.0
  git tag v0.7.0
  git push origin v0.7.0
  ```

- **`publish` failed.** Check the job log. If the files never reached PyPI, re-run the
  failed jobs from the Actions page. If the version is already on PyPI, it cannot be
  uploaded again (PyPI never accepts the same version twice, even after deletion);
  release a new version instead.

- **`github-release` failed.** The package is already on PyPI. A common cause is a
  GitHub Release that already exists for the tag. Re-run the job after deleting that
  release, or attach the files to it by hand: download the `dist` artifact from the
  workflow run and run `gh release upload v0.7.0 dist/*`.
