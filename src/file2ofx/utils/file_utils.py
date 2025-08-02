"""File utility functions for file2ofx."""

import tempfile
from pathlib import Path
from typing import List


def get_output_filename(input_file: Path) -> Path:
    """Generate output filename based on input file.
    
    Args:
        input_file: Path to input file
        
    Returns:
        Path to output file with .ofx extension
        
    Raises:
        ValueError: If input file has no stem
    """
    if not input_file.stem:
        raise ValueError("Input file must have a valid name")

    # Create base output filename
    output_file = input_file.with_suffix(".ofx")

    # Check if file exists and generate alternative name
    if output_file.exists():
        output_file = _generate_unique_filename(output_file)

    return output_file


def _generate_unique_filename(base_file: Path) -> Path:
    """Generate unique filename by appending number suffix.
    
    Args:
        base_file: Base file path
        
    Returns:
        Path with unique filename
    """
    stem = base_file.stem
    suffix = base_file.suffix

    # Try numbers 1-99
    for i in range(1, 100):
        new_name = f"{stem}_{i}{suffix}"
        candidate = base_file.parent / new_name

        if not candidate.exists():
            return candidate

    # If all 99 names are taken, raise error
    raise ValueError(f"Could not generate unique filename for {base_file}")


def read_cols_file(input_file: Path) -> List[str]:
    """Read column definitions from .cols file.
    
    Args:
        input_file: Path to input file
        
    Returns:
        List of column names
        
    Raises:
        FileNotFoundError: If .cols file doesn't exist
        ValueError: If .cols file is malformed
    """
    cols_file = input_file.with_suffix(".cols")

    if not cols_file.exists():
        raise FileNotFoundError(f"Column definition file not found: {cols_file}")

    try:
        with open(cols_file, encoding="utf-8") as f:
            content = f.read().strip()

        # Parse comma-separated values, handling quotes
        columns = _parse_csv_line(content)

        if not columns:
            raise ValueError("No column names found in .cols file")

        return columns

    except Exception as e:
        raise ValueError(f"Error reading .cols file: {e}")


def _parse_csv_line(line: str) -> List[str]:
    """Parse a single CSV line, handling quoted values.
    
    Args:
        line: CSV line to parse
        
    Returns:
        List of parsed values
    """
    if not line:
        return []

    # Simple CSV parsing for column names
    # This handles basic quoted and unquoted values
    result = []
    current = ""
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            result.append(current.strip())
            current = ""
        else:
            current += char

    # Add the last value
    result.append(current.strip())

    return result


def detect_file_format(file_path: Path) -> str:
    """Detect file format based on extension and content.
    
    Args:
        file_path: Path to file
        
    Returns:
        Detected format ('csv' or 'txt')
    """
    # Check extension first
    if file_path.suffix.lower() == ".csv":
        return "csv"

    # For .txt files, try to detect CSV format by reading first few lines
    if file_path.suffix.lower() == ".txt":
        try:
            with open(file_path, encoding="utf-8") as f:
                first_line = f.readline().strip()

            # Simple heuristic: if line contains commas, likely CSV
            if "," in first_line:
                return "csv"
            else:
                return "txt"
        except Exception:
            # If we can't read the file, default to txt
            return "txt"

    # Default to txt for unknown extensions
    return "txt"


def validate_file_path(file_path: Path) -> None:
    """Validate file path for security and accessibility.
    
    Args:
        file_path: Path to validate
        
    Raises:
        ValueError: If path is invalid or unsafe
    """
    # Check if path is absolute and within reasonable bounds
    if file_path.is_absolute():
        # Prevent directory traversal attacks
        resolved = file_path.resolve()

        # Check for suspicious patterns
        suspicious_patterns = [
            "..",
            "~",
            "/etc",
            "/var",
            "/usr",
            "/bin",
            "/sbin",
        ]

        for pattern in suspicious_patterns:
            if pattern in str(resolved):
                raise ValueError(f"Unsafe file path: {file_path}")

    # Check if file exists and is readable
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if not file_path.stat().st_size > 0:
        raise ValueError(f"File is empty: {file_path}")


def create_temp_file(prefix: str = "temp", suffix: str = "", directory: Path = None) -> Path:
    """Create a temporary file with the _.filename.ext naming convention.
    
    Args:
        prefix: File name prefix (default: "temp")
        suffix: File extension (default: "")
        directory: Directory to create file in (default: system temp directory)
        
    Returns:
        Path to created temporary file
        
    Note:
        Files created with this function will be automatically ignored by git
        due to the _.* pattern in .gitignore. The naming convention is
        _.filename.ext (underscore + dot + filename + extension) to avoid
        conflicts with system dunder files like __pycache__.
    """
    if directory is None:
        directory = Path(tempfile.gettempdir())
    
    # Create filename with _. prefix (underscore + dot + filename)
    filename = f"_.{prefix}{suffix}"
    temp_file = directory / filename
    
    # Create the file
    temp_file.touch()
    
    return temp_file
