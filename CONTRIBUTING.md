# Contributing

First off, thank you for considering contributing to `kaif-file-organizer`. It's people like you that make open source such a great community!

## Getting Started

### Prerequisites
- Python 3.12, 3.13, or 3.14
- Git

### Development Setup

The repository uses a standard `src/` layout. Follow these steps to set up your local development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/techykaif/file-organizer.git
   cd file-organizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

We use `pytest` for our test suite. To run the tests:
```bash
pytest tests/
```

### Running Ruff

We use `ruff` for linting and code formatting. To run the checks:
```bash
ruff check .
```

### Building the Package

To build the source distribution and wheel:
```bash
python -m pip install build
python -m build
```

### Testing the CLI

Once installed in editable mode, you can test the CLI commands locally to ensure your changes work as expected:
```bash
file-organizer --help
file-organizer --version
file-organizer ./test_directory --dry-run
```

## Making Changes

- **Focused changes:** Keep your pull requests focused on a single issue or feature. This makes them easier to review and maintain.
- **Tests:** Write or update tests for any changed functionality.
- **Documentation:** Update the `README.md` or other documentation if your changes affect how users interact with the tool.

## Pull Requests

When submitting a pull request, please ensure:
- The PR description is clear and explains the reason for the change.
- You have run `pytest tests/` and all tests pass.
- You have run `ruff check .` and there are no linting errors.
- There are no unrelated or formatting-only changes mixed in with your feature/fix.

## Reporting Bugs

We use GitHub Issues to track bugs and feature requests. 
If you find a bug, please open an issue here:
[https://github.com/techykaif/file-organizer/issues](https://github.com/techykaif/file-organizer/issues)

Please use the provided issue templates to ensure you include all the necessary information.
