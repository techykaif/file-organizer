# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add detailed structured CLI operation summaries (moved, duplicates skipped, collisions handled).
- Add integration test suite (`tests/test_cli.py`) and unit tests for core file organizer operations.
- Add CodeQL automated security scanning and Dependabot configurations.
- Add full suite of community governance documentation (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/SECURITY.md`, and issue/PR templates).

### Changed
- Enhance CI validation to automatically build and test `.whl` distributions in isolated environments.
- Harden GitHub Actions workflows (`tests.yml`) with explicitly scoped least-privilege permissions.
- Improve CLI standard output UX and `dry-run` simulation semantics.
- Improve project README and update repository installation URLs.

## [0.1.2]

### Added
- Upgrade supported Python versions to 3.12, 3.13, and 3.14.

### Fixed
- Derive CLI version directly from package metadata instead of hardcoding.
- Require compatible `setuptools` version (`>=77.0.3`) for robust builds.

## [0.1.1]

### Added
- Transform the script into an installable CLI package.
- Add GitHub Actions CI workflow for PyPI trusted publishing via OIDC.

### Fixed
- Remove deprecated license classifier and update license metadata in `pyproject.toml`.
- Update repository URLs to point to `techykaif/file-organizer`.
