# Release process

This repo uses SemVer-like tags (`vX.Y.Z`) and GitHub Releases.

## Principles
- Main is always releasable.
- All changes go through Pull Requests (no direct pushes to `main`).
- CI must be green before merge.
- Releases are created from `main` via an annotated tag and GitHub Release notes.

## When to release
Create a new release when:
- a user-visible change is shipped (new endpoint, behavior change)
- deps/tooling changes affect local dev/CI/runtime
- you want a stable checkpoint (milestone)

## Versioning
- `vMAJOR.MINOR.PATCH`
  - MAJOR: breaking changes (API/behavior)
  - MINOR: backward-compatible features
  - PATCH: backward-compatible fixes

## Changelog
- Keep `CHANGELOG.md` in the repo root.
- Add entries under a new "Unreleased" section while working.
- When releasing, convert "Unreleased" to the new version section.

Recommended format:
- Added / Changed / Fixed / Removed / Security

## Standard flow (PR -> merge -> release)
1) Create a branch from `main`
   - Example: `feat/sub-endpoint`, `fix/health-timeout`, `chore/ci-cache`

2) Implement change + tests
   - Ensure these pass locally:
     - `make test`
     - `make lint`
     - `make fmt`

3) Open PR
   - Keep the diff small and reviewable
   - CI must be green

4) Merge via squash
   - Delete branch after merge

5) Update changelog (via PR if branch protection requires it)
   - Add the release notes you want to appear in GitHub Release

6) Tag and create GitHub Release (from `main`)
   - Create tag + release:
     - `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md`
   - If tag already exists, update the existing release instead:
     - `gh release edit vX.Y.Z --notes-file CHANGELOG.md`

## Commands cheat-sheet

### Start a change
- `git switch main`
- `git pull`
- `git switch -c feat/my-change`

### Run checks
- `make test`
- `make lint`
- `make fmt`

### Push branch
- `git push -u origin feat/my-change`

### Create PR (CLI)
- `gh pr create --base main --head feat/my-change --title "..." --body "..."`

### Merge PR (squash)
- `gh pr merge --squash --delete-branch`

### Sync local main after merge
- `git switch main`
- `git pull`
- If diverged: `git reset --hard origin/main`

### Create a release
- `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG.md`

### Update an existing release
- `gh release edit vX.Y.Z --notes-file CHANGELOG.md`

## Notes
- Do not include secrets/tokens in commits (hooks + .gitignore should block).
- Prefer small releases; large releases make debugging harder.