# file2ofx

Convert transaction files (TXT/CSV) to OFX format with auto-column detection.

## Features

- **Auto-column detection**: Automatically identifies date, amount, description, and type columns
- **Multiple file formats**: Supports CSV and TXT files with various delimiters
- **Column definition files**: Use `.cols` files to specify headers for files without them
- **OFX compliance**: Generates OFX 1.0.2+ compliant output files
- **Smart file naming**: Handles output file conflicts with numbered suffixes
- **Tab completion**: Full tab completion support for file and output paths
- **Financial institution configuration**: Set bank details, account info, and balances

## Installation

```bash
pip install file2ofx
```

## Usage

### Basic Usage

Convert a CSV file to OFX:
```bash
file2ofx transactions.csv
```

Convert with verbose output:
```bash
file2ofx transactions.csv --verbose
```

### Advanced Options

Specify file format and encoding:
```bash
file2ofx transactions.txt --format txt --encoding utf-8
```

Set output file:
```bash
file2ofx transactions.csv --output my_transactions.ofx
```

### OFX Configuration Options

Set OFX version:
```bash
file2ofx transactions.csv --ofx-version 102
```

Configure financial institution details:
```bash
file2ofx transactions.csv \
  --fi-org "INVESTEC PRIVATE BANK" \
  --fi-id "580105" \
  --account-id "1100407033542" \
  --account-type SAVINGS \
  --currency ZAR
```

Set balance information:
```bash
file2ofx transactions.csv \
  --ledger-balance 14863.32 \
  --available-balance 14863.32
```

### Tab Completion

The CLI supports tab completion for file and output paths:

```bash
# Enable completion for bash
eval "$(_FILE2OFX_COMPLETE=bash_source file2ofx)"

# Enable completion for zsh
eval "$(_FILE2OFX_COMPLETE=zsh_source file2ofx)"

# Enable completion for fish
eval "$(_FILE2OFX_COMPLETE=fish_source file2ofx)"
```

Or install the completion script:

```bash
file2ofx completion > ~/.local/share/bash-completion/completions/file2ofx
```

**Features:**
- **Input files**: Tab completion for CSV and TXT files only
- **Output files**: Tab completion for existing .ofx files and suggests new .ofx files
- **Directory navigation**: Tab completion works with directories
- **Relative paths**: Supports both relative and absolute paths

## Input File Formats

### CSV Files
- Comma-separated values
- Auto-detected delimiters
- Support for quoted fields
- Header row detection

### TXT Files
- Fixed-width or delimited
- Auto-detected delimiters
- Support for `.cols` files for header specification

### Column Definition Files (.cols)
If your transaction file doesn't have headers, create a `.cols` file with the same name:
```
"Date","Description","Amount","Type"
```

## Output

The tool generates OFX-compliant files with:
- Proper OFX structure and formatting (SGML format)
- Transaction details (date, amount, description, type)
- Financial institution information (when provided)
- Balance information (when provided)
- Support for multiple OFX versions (1.0.2 through 2.2.0)

## Development

For development setup, testing, and contributing guidelines, see [docs/DEVELOPER.md](docs/DEVELOPER.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details. 