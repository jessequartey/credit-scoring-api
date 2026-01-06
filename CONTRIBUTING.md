# Contributing to Credit ML

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/credit-ml.git
   cd credit-ml
   ```

3. Set up the development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

5. Generate training data and train the model:
   ```bash
   python ml/generate_training_data.py
   python ml/train_model.py
   ```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure:
   - Code follows Python best practices
   - All tests pass: `pytest`
   - Code is properly documented
   - No sensitive data is committed

3. Commit your changes:
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Test:` for test-related changes

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request on GitHub

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 120 characters

## Testing

- Write tests for new features
- Ensure all existing tests pass
- Run tests before submitting PR:
  ```bash
  pytest tests/ -v
  ```

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure CI/CD pipeline passes
- Request review from maintainers
- Be responsive to feedback

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages or logs

## Security Issues

If you discover a security vulnerability, please email the maintainers directly instead of opening a public issue.

## Questions?

Feel free to open an issue for any questions or discussions about the project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.
