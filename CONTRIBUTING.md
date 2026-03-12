# Contributing to GuardLLM

Thank you for your interest in contributing to GuardLLM! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip or conda

### Setting up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/guardllm.git
   cd guardllm
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the package in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names that explain what you're working on.

### Writing Code

- Follow [PEP 8](https://pep8.org/) style guidelines
- Add type hints to all functions and methods
- Write docstrings for public functions and classes
- Keep functions focused and modular

### Running Tests

Run the test suite before submitting changes:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=guardllm
```

### Code Formatting

We use black and ruff for code formatting and linting:

```bash
black .
ruff check .
```

Type checking with mypy:

```bash
mypy guardllm/
```

## Submitting Changes

### Before You Commit

1. Run tests: `pytest`
2. Format code: `black .`
3. Check linting: `ruff check .`
4. Run type checks: `mypy guardllm/`

### Commit Messages

Write clear, concise commit messages:

```
feat: Add prompt injection detector

- Implement regex-based pattern matching
- Add unit tests for common injection patterns
- Update documentation
```

Use conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

### Pull Request Process

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub with:
   - Clear title describing the changes
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots or examples if applicable

3. Address any review comments
4. Ensure all CI checks pass

## Areas for Contribution

- **New Detectors**: Add safety, governance, or observability detectors
- **Documentation**: Improve docs, examples, or API reference
- **Tests**: Increase test coverage and add edge case tests
- **Performance**: Optimize existing code
- **Bug Fixes**: Fix reported issues
- **Integration Examples**: Show how to use GuardLLM with popular LLM platforms

## Reporting Bugs

Found a bug? Please report it on [GitHub Issues](https://github.com/GuardLLM/guardllm/issues).

Include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Relevant code snippets
- Environment details

## Feature Requests

Suggest new features on [GitHub Discussions](https://github.com/GuardLLM/guardllm/discussions).

Include:
- Clear description of the feature
- Use cases and examples
- Potential implementation approach

## Documentation

Documentation is crucial! When adding features:

1. Add docstrings to your code
2. Update relevant documentation files
3. Add examples if applicable
4. Update the README if it's a major feature

## Questions?

- Check existing [issues](https://github.com/GuardLLM/guardllm/issues) and [discussions](https://github.com/GuardLLM/guardllm/discussions)
- Open a new discussion for questions
- Email: info@guardllm.dev

Thank you for contributing to GuardLLM!
