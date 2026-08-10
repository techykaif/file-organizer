# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation
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
