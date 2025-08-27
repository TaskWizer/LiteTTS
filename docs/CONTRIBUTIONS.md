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
git clone https://github.com/YOUR_USERNAME/kokoro_onnx_tts_api.git
cd kokoro_onnx_tts_api

# Install dependencies
uv sync

# Run tests
python -m pytest kokoro/tests/

# Start development server
python kokoro/start_server.py
```

## 🧪 Testing

- **Run all tests**: `python -m pytest kokoro/tests/`
- **Performance tests**: `python kokoro/tests/kokoro/scripts/benchmark_tts.py`
- **Integration tests**: `python kokoro/tests/test_api_endpoints.py`

## 📝 Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** for function parameters and return values
- Write **clear docstrings** for all public functions and classes
- Keep **line length under 100 characters**

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

## 📚 Documentation

- Update relevant **README files** for new features
- Add **API documentation** for new endpoints
- Include **usage examples** where appropriate
- Update **CHANGELOG.md** with your changes

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
