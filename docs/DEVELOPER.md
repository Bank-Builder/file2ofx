# Developer Documentation

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/file2ofx.git
   cd file2ofx
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

## Development Workflow

### Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=file2ofx --cov-report=html
```

Run specific test files:
```bash
pytest tests/test_detector.py
```

### Linting and Code Quality

Run ruff linter:
```bash
ruff check src/
```

Format code with ruff:
```bash
ruff format src/
```

### Git Hooks

The project includes pre-commit and pre-push hooks:

- **Pre-commit hook**: Runs ruff linting before each commit
- **Pre-push hook**: Runs the full test suite before pushing

To install the hooks:
```bash
pre-commit install
```

### Test Data Generation

Generate test data files:
```bash
python scripts/generate_test_data.py
```

This creates various test files in the `test_data/` directory:
- CSV files with headers
- CSV files without headers (with .cols files)
- Fixed-width TXT files
- Files with missing columns
- Files with invalid data

### Building and Distribution

Build the package:
```bash
python -m build
```

This creates distribution files in the `dist/` directory.

## Project Structure

```
file2ofx/
├── src/file2ofx/          # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI entry point
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── detector.py    # Column detection logic
│   │   ├── parser.py      # File parsing
│   │   └── ofx_generator.py # OFX generation
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── file_utils.py  # File handling utilities
├── tests/                 # Test files
├── scripts/               # Test data generation scripts
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md             # Project documentation
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for all modules, classes, and functions
- Maximum line length: 88 characters (ruff formatter default)
- Use meaningful variable and function names

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Test both success and error cases
- Aim for high code coverage

### Integration Tests
- Test end-to-end workflows
- Test file parsing and OFX generation
- Test error handling and edge cases

### Test Data
- Use realistic transaction data
- Test various file formats and encodings
- Test column detection with different headers

## OFX Format Support

The application supports multiple OFX versions:
- OFX 1.0.2 (default)
- OFX 1.0.3
- OFX 2.0.0 through 2.2.0

### OFX Structure
- Proper SGML format (not XML)
- SIGNONMSGSRSV1 section with financial institution details
- BANKMSGSRSV1 section with transaction data
- Balance information (LEDGERBAL, AVAILBAL)
- Proper date/time formatting (YYYYMMDDHHMMSS)

### Financial Institution Configuration
- Organization name (--fi-org)
- Institution ID (--fi-id)
- Account ID (--account-id)
- Account type (--account-type)
- Currency code (--currency)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Commit Guidelines
- Use imperative mood in commit messages
- Keep subject line under 50 characters
- Separate subject from body with a blank line
- Use message body for explaining "why" not "what"

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure virtual environment is activated
- Install package in development mode: `pip install -e .`

**Test failures:**
- Check that all dependencies are installed
- Run `pytest --tb=short` for shorter tracebacks

**Linting errors:**
- Run `ruff check --fix src/` to auto-fix issues
- Check the ruff configuration in `pyproject.toml`

### Performance Considerations

- Large files: The parser processes files in chunks to manage memory
- Column detection: Uses efficient regex patterns and data analysis
- OFX generation: Optimized XML generation with lxml

## Security

- Validate all input files
- Sanitize data before OFX generation
- Handle file paths safely
- Prevent path traversal attacks
- Use secure temporary file creation

## License

This project is licensed under the MIT License - see the LICENSE file for details. 