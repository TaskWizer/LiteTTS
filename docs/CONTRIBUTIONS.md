# Contributing to Kokoro ONNX TTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

Thank you for your interest in contributing to the Kokoro ONNX TTS API! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** with clear, descriptive commits
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/LiteTTS.git
cd LiteTTS

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv
uv sync

# Install development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pre-commit install

# Run tests
pytest LiteTTS/tests/unit/ -v

# Start development server
python -m uvicorn app:app --reload --port 8354
```

## 🧪 Testing

```bash
# Run all unit tests with coverage
pytest LiteTTS/tests/unit/ --cov=LiteTTS --cov-report=term-missing

# Run specific test file
pytest LiteTTS/tests/unit/test_phonemizer_preprocessor.py -v

# Run tests matching a pattern
pytest LiteTTS/tests/ -k "test_name"

# Run with verbose output
pytest LiteTTS/tests/ -vv --tb=long

# Run performance benchmarks
python LiteTTS/benchmarks/performance_benchmark.py
```

### Test Structure

```
LiteTTS/tests/
├── unit/           # Unit tests for individual modules
│   ├── test_*.py   # Tests for specific components
│   └── root_tests/ # Core functionality tests
├── test_api.py     # API endpoint tests
├── test_performance.py  # Performance regression tests
└── scripts/        # Test scripts and utilities
```

## 📝 Code Style

We use **ruff** for linting and formatting:

```bash
# Auto-fix linting issues
ruff check . --fix

# Check formatting
ruff format --check .

# Format code
ruff format .
```

### Style Guidelines

- Follow **PEP 8** Python style guidelines
- Use **type hints** for function parameters and return values
- Write **clear docstrings** for all public functions and classes
- Keep **line length at 88 characters** (ruff default)
- Use **absolute imports** within the package: `from LiteTTS.nlp import ...`
- Add **tests** for any new functionality

## 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **System information** (OS, Python version, etc.)
- **Relevant logs** or error messages

## 💡 Feature Requests

For new features:

- **Check existing issues** to avoid duplicates
- **Describe the use case** and benefits
- **Provide implementation suggestions** if possible
- **Consider backward compatibility**

## 🔧 Pull Request Guidelines

- **One feature per PR** - keep changes focused
- **Update tests** for any new functionality
- **Update documentation** as needed
- **Ensure all tests pass** before submitting
- **Write clear commit messages**
- **Run quality checks locally**:
  ```bash
  make all  # Runs lint, format check, type check, tests
  ```

### PR Checklist

- [ ] Tests added/updated for new functionality
- [ ] Code passes `ruff check . --fix`
- [ ] Code passes `ruff format --check .`
- [ ] Type hints added where applicable
- [ ] Documentation updated
- [ ] CHANGELOG.md updated if user-facing changes

## 📚 Documentation

- Update relevant **README files** for new features
- Add **API documentation** for new endpoints
- Include **usage examples** where appropriate
- Update **CHANGELOG.md** with your changes
- Document **environment variables** in ENVIRONMENT_VARIABLES.md if added

## 🏷️ Commit Message Format

```
type(scope): brief description

Longer description if needed

- List any breaking changes
- Reference related issues (#123)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Documentation** - Check the `docs/` directory

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

Thank you for contributing! 🎉
