# Contributing

Thank you for considering a contribution to `kaif-file-organizer`.

## Project and license model

`kaif-file-organizer` is source-available, not an open-source project. The source is available for local inspection, testing, evaluation, and other permitted non-commercial use under the terms in [`LICENSE`](LICENSE).

Commercial use, resale, commercial redistribution, paid hosted use, or incorporation of a substantial portion of the Software into a commercial product or service requires prior written authorization from the copyright holder.

## Development environment

The project uses [`uv`](https://docs.astral.sh/uv/) and a committed `uv.lock` so development dependencies are reproducible.

### Prerequisites

- Python 3.12, 3.13, or 3.14
- Git
- `uv`

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/techykaif/file-organizer.git
   cd file-organizer
   ```

2. Install the project and development dependencies from the lockfile:

   ```bash
   uv sync --locked --extra dev
   ```

No separate virtual environment is required; `uv` manages the project environment.

## Proposing features and fixes

- **Bug reports:** Open a GitHub Issue with a clear reproduction, expected behavior, actual behavior, and relevant environment details.
- **Feature requests:** Open an Issue describing the problem, proposed behavior, and why the change would be useful before starting a substantial implementation.
- **Implementations:** Submit a Pull Request when you have a working fix or feature. The maintainer will review the implementation and may request changes before acceptance.
- **Official project changes:** A feature or fix becomes part of the official project only after the maintainer reviews and merges the Pull Request.

Opening an Issue or Pull Request does not itself grant permission for commercial use, resale, or commercial redistribution of the Software.

## Verification before opening a PR

Run the same core checks used by CI:

### Tests and coverage

```bash
uv run --locked pytest --cov=file_organizer --cov-fail-under=85 tests/
```

The repository requires at least 85% coverage.

### Ruff

Run both linting and formatting checks:

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
```

To apply formatting locally:

```bash
uv run --locked ruff format .
```

### Type checking

CI uses a pinned Pyright version:

```bash
uvx --from pyright==1.1.411 pyright
```

### Build verification

```bash
uv build
```

CI also installs the generated wheel into a clean environment as an installation smoke test.

### Dependency audit

CI audits the installed environment for known vulnerable dependencies with `pip-audit`.

## Testing the CLI

After syncing the environment, verify the CLI itself:

```bash
uv run file-organizer --help
uv run file-organizer --version
uv run file-organizer ./test_directory --dry-run
```

When testing organization behavior, prefer `--dry-run` first and use a temporary test directory for operations that actually move files.

## Making changes

- Keep each pull request focused on one feature, fix, or maintenance concern.
- Add or update tests for changed behavior.
- Update documentation when commands, configuration, safety guarantees, or user-facing behavior changes.
- Preserve the project's safety-first behavior: do not introduce silent overwrites or automatic deletion.
- Keep filesystem mutations and error handling explicit and testable.
- Avoid unrelated formatting or refactoring in feature commits.
- Retain the copyright and license notices in permitted copies and forks.

## Pull requests

Before submitting a pull request, ensure:

- the full test suite passes;
- coverage remains at or above 85%;
- Ruff lint and format checks pass;
- Pyright passes;
- the package builds successfully;
- documentation reflects the current development workflow;
- the PR description explains the behavior being changed and how it was verified.

GitHub Actions runs the authoritative CI checks on pushes and pull requests targeting `main`.

## Reporting bugs

Please open an issue with a clear reproduction, expected behavior, actual behavior, and relevant environment details:

https://github.com/techykaif/file-organizer/issues

## Commercial licensing

For commercial licensing, resale, commercial redistribution, paid hosted use, or other uses requiring authorization, contact the copyright holder through the repository's official issue tracker or the contact information published by the copyright holder.
