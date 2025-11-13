# Contributing to Auto Trading Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setting Up Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/auto_trading_assistant.git
cd auto_trading_assistant
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up pre-commit hooks** (optional but recommended)

```bash
pip install pre-commit
pre-commit install
```

5. **Create .env file**

```bash
cp .env.example .env
# Edit .env with your test credentials
```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent fixes
- `docs/description` - Documentation updates
- `test/description` - Test additions/modifications
- `refactor/description` - Code refactoring

### Making Changes

1. **Create a new branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Keep functions small and focused

3. **Write tests**
   - Add unit tests for new features
   - Ensure existing tests still pass
   - Aim for >80% code coverage

4. **Run tests locally**

```bash
pytest tests/ -v
```

5. **Check code quality**

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy . --ignore-missing-imports
```

6. **Commit your changes**

```bash
git add .
git commit -m "feat: add awesome new feature"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

7. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

**Example:**

```python
def calculate_profit(entry_price: float, exit_price: float, quantity: float) -> float:
    """Calculate profit from a trade.
    
    Args:
        entry_price: Price at which position was entered
        exit_price: Price at which position was exited
        quantity: Number of units traded
    
    Returns:
        Profit or loss as a float
    
    Example:
        >>> calculate_profit(100.0, 110.0, 1.0)
        10.0
    """
    return (exit_price - entry_price) * quantity
```

### Testing Guidelines

- Write unit tests for all new code
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls
- Keep tests independent

**Example:**

```python
def test_calculate_profit_positive():
    """Test profit calculation with gain."""
    profit = calculate_profit(100.0, 110.0, 1.0)
    assert profit == 10.0

def test_calculate_profit_negative():
    """Test profit calculation with loss."""
    profit = calculate_profit(100.0, 90.0, 1.0)
    assert profit == -10.0
```

## Pull Request Guidelines

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests added for new features
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No merge conflicts
- [ ] Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests pass locally
```

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Exact steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS and version
   - Python version
   - Package versions
6. **Logs**: Relevant log output
7. **Screenshots**: If applicable

### Feature Requests

When requesting features, include:

1. **Use Case**: Why this feature is needed
2. **Proposed Solution**: How you envision it working
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, email the maintainers directly with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit credentials or API keys
- Always use environment variables
- Test in paper trading mode first
- Review code for potential security issues
- Keep dependencies up-to-date

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep comments concise and relevant

### Project Documentation

When updating documentation:

- Keep README.md accurate
- Update ARCHITECTURE.md for structural changes
- Add examples for new features
- Update configuration docs

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_risk_manager.py

# Run specific test
pytest tests/test_risk_manager.py::TestRiskManager::test_can_trade_first_trade
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Mock external dependencies

## Code Review Process

1. **Automated Checks**: CI/CD runs automatically
2. **Maintainer Review**: Code reviewed by maintainers
3. **Feedback**: Address any comments or suggestions
4. **Approval**: Requires 1+ approvals
5. **Merge**: Maintainer merges PR

## Questions?

If you have questions:

- Check existing documentation
- Search existing issues
- Create a new issue with the `question` label
- Join discussions in issues/PRs

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to Auto Trading Assistant! 🚀