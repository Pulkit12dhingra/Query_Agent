# Development Workflow

This document describes the development workflow and CI/CD setup for the Query Automation Agent Pipeline.

## GitHub Actions CI/CD Pipeline

### Workflow Overview

The CI pipeline consists of 5 main jobs that run in parallel:

#### 1. **Test Job** (`test`)
- **Purpose**: Core testing and validation
- **Runs on**: Ubuntu Latest with Python 3.13
- **Steps**:
  - Checkout code
  - Set up Python and uv package manager
  - Install dependencies with `uv sync --dev`
  - Run Ruff linting: `uv run ruff check . --exclude "*.ipynb"`
  - Check formatting: `uv run ruff format --check . --exclude "*.ipynb"`
  - Run pytest tests: `uv run python -m pytest tests/ -v --tb=short`
  - Check file formatting (trailing whitespace, newlines)

#### 2. **Lint and Format Job** (`lint-and-format`)
- **Purpose**: Run pre-commit hooks
- **Steps**:
  - Install dependencies
  - Run all pre-commit hooks: `uv run pre-commit run --all-files --show-diff-on-failure`

#### 3. **Security Job** (`security`)
- **Purpose**: Security vulnerability scanning
- **Steps**:
  - Run Ruff security checks: `uv run ruff check . --select=S --exclude "*.ipynb"`

#### 4. **Type Check Job** (`type-check`)
- **Purpose**: Static type checking (optional)
- **Steps**:
  - Install mypy
  - Run type checking: `uv run mypy src/ --ignore-missing-imports --no-strict-optional`
  - Set to `continue-on-error: true` (non-blocking)

#### 5. **Coverage Job** (`coverage`)
- **Purpose**: Test coverage reporting
- **Steps**:
  - Install coverage tools
  - Run tests with coverage: `uv run coverage run -m pytest tests/`
  - Generate reports: `uv run coverage report --show-missing`
  - Upload to Codecov

### Trigger Conditions

The CI pipeline triggers on:
- **Push** to branches: `main`, `master`, `develop`
- **Pull requests** to branches: `main`, `master`, `develop`

### Configuration Files

#### `.github/workflows/ci.yml`
Main CI workflow configuration with all job definitions.

#### `pyproject.toml`
Contains tool configurations:
- **Ruff**: Linting and formatting rules
- **Coverage**: Coverage reporting settings

#### `.pre-commit-config.yaml`
Pre-commit hooks configuration (mirrors CI checks for local development).

## Local Development Setup

### Prerequisites
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd query_automation

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Local Checks** (Optional - auto-runs on commit)
   ```bash
   # Run all pre-commit hooks
   uv run pre-commit run --all-files

   # Run specific checks
   uv run ruff check . --fix
   uv run ruff format .
   uv run python -m pytest tests/ -v
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks run automatically
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   # CI pipeline runs automatically
   ```

## Quality Standards

### Code Quality
- **Linting**: Ruff with strict rules (pycodestyle, Pyflakes, isort, etc.)
- **Formatting**: Consistent code formatting with Ruff
- **Type Hints**: Encouraged but not enforced (mypy runs as advisory)

### Testing
- **Coverage**: Aim for >80% test coverage
- **Test Types**: Unit tests, integration tests, and end-to-end tests
- **Test Data**: Use fixtures and mocks to ensure reproducible tests

### Security
- **Security Scanning**: Automated security checks with Ruff
- **Dependency Management**: Regular dependency updates with uv

### Documentation
- **Code Documentation**: Docstrings for all public functions/classes
- **README**: Keep README.md updated with latest setup instructions
- **Changelog**: Update for significant changes

## Troubleshooting CI Issues

### Common Failures

#### Linting Failures
```bash
# Fix locally
uv run ruff check . --fix
uv run ruff format .
git add .
git commit -m "fix: resolve linting issues"
```

#### Test Failures
```bash
# Run tests locally
uv run python -m pytest tests/ -v --tb=long

# Debug specific test
uv run python -m pytest tests/test_specific.py::test_function -vvv
```

#### Coverage Issues
```bash
# Generate coverage report
uv run coverage run -m pytest tests/
uv run coverage report --show-missing

# View HTML report
uv run coverage html
open htmlcov/index.html
```

#### Pre-commit Hook Failures
```bash
# Update pre-commit hooks
uv run pre-commit autoupdate

# Run specific hook
uv run pre-commit run ruff --all-files
```

### Performance Optimization

The CI pipeline is optimized for speed:
- **Parallel Jobs**: Multiple jobs run simultaneously
- **Dependency Caching**: uv handles dependency caching
- **Targeted Checks**: Only relevant files are checked
- **Fast Tools**: Ruff is much faster than traditional linters

### Monitoring and Maintenance

- **Badge Status**: README badges show current CI status
- **Coverage Tracking**: Codecov integration tracks coverage trends
- **Dependency Updates**: Regular updates to maintain security
- **Performance Monitoring**: CI run times are monitored for optimization

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Codecov Documentation](https://docs.codecov.com/)
