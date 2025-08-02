# file2ofx

A Python CLI application that automatically converts transaction files (TXT/CSV) to OFX (Open Financial Exchange) format.

## Features

- **Auto-column detection**: Automatically identifies transaction columns from headers or data analysis
- **Multiple input formats**: Supports TXT and CSV files
- **Column mapping**: Uses `.cols` files for custom column definitions when headers are missing
- **OFX compliance**: Generates standard OFX 2.x compliant output files
- **Smart file naming**: Automatically handles output file naming with conflict resolution

## Installation

```bash
pip install file2ofx
```

## Usage

### Basic Usage

```bash
file2ofx transactions.csv
```

This will create `transactions.ofx` in the same directory.

### With Options

```bash
file2ofx bankfile.txt --format csv --encoding utf-8
```

### Help

```bash
file2ofx --help
```

## Input File Formats

### CSV Files
- Standard CSV format with headers
- Automatic column detection from headers
- Supports quoted and unquoted values

### TXT Files
- Fixed-width or delimited text files
- Column detection through data analysis
- Can use `.cols` companion files for column definitions

### Column Definition Files (.cols)
When a text file has no headers, you can create a companion `.cols` file:

```
"Date","Description","Amount","Type"
```

This file should contain comma-separated column names (quoted or unquoted).

## Output

- **File naming**: Input filename with `.ofx` extension
- **Conflict resolution**: If output exists, creates `filename_1.ofx`, `filename_2.ofx`, etc.
- **OFX format**: Standard OFX 2.x compliant XML structure

## Column Auto-Detection

The application can automatically identify common transaction columns:

- **Date columns**: Various date formats (MM/DD/YYYY, YYYY-MM-DD, etc.)
- **Amount columns**: Numeric values with currency symbols
- **Description columns**: Text fields containing transaction descriptions
- **Type columns**: Transaction types (DEBIT, CREDIT, etc.)

## Development

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository>
   cd file2ofx
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install production dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Install package in editable mode**:
   ```bash
   pip install -e .
   ```

### Development Dependencies

The following tools are available for development:

- **pytest**: Unit and integration testing
- **pytest-cov**: Test coverage reporting
- **ruff**: Code linting and formatting
- **pre-commit**: Git hooks for code quality

### Testing

Run all tests:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=file2ofx --cov-report=term-missing
```

### Linting and Formatting

Check code quality:
```bash
ruff check .
```

Format code:
```bash
ruff format .
```

Fix auto-fixable issues:
```bash
ruff check . --fix
```

### Git Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

The repository includes:
- **pre-commit hook**: Runs ruff linting before commits
- **pre-push hook**: Runs tests before pushing to remote

### Test Data Generation

Generate sample test files:
```bash
python scripts/generate_test_data.py
```

This creates various test files in the `test_data/` directory for testing different scenarios.

### Building and Distribution

Build the package:
```bash
python -m build
```

The project uses `pyproject.toml` for configuration and supports modern Python packaging standards.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests
6. Submit a pull request

## Changelog

### 1.0.0
- Initial release
- Basic CSV/TXT to OFX conversion
- Auto-column detection
- Column definition file support 