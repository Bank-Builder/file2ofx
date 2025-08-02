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

```bash
git clone <repository>
cd file2ofx
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Testing

```bash
pytest tests/
```

### Linting

```bash
ruff check .
ruff format .
```

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