# Release process (SemVer)

We follow SemVer: `MAJOR.MINOR.PATCH`.

- **PATCH**: bugfixes, refactors, docs, CI tweaks (no behavior change).
- **MINOR**: new endpoints/features, backward-compatible.
- **MAJOR**: breaking changes (API contract, required env/config, behavior).

## Changelog
- Keep `CHANGELOG.md` updated.
- Add entries under **Unreleased** while working.
- Before a release: move **Unreleased** items into a new version section.

## Release steps
1. Ensure `main` is green (CI passed).
2. Update `CHANGELOG.md` for version `vX.Y.Z`.
3. Create a PR with changelog updates and merge it.
4. Create the tag on `main`: `vX.Y.Z`.
5. Create a GitHub Release for that tag using the changelog notes.
