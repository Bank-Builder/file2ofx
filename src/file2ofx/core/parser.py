"""File parsing functionality for file2ofx."""

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from ..utils.file_utils import detect_file_format, read_cols_file, validate_file_path
from .detector import ColumnDetector


class FileParser:
    """Parse transaction files and extract structured data."""

    def __init__(self) -> None:
        """Initialize the file parser."""
        self.detector = ColumnDetector()

    def parse_file(
        self,
        file_path: Path,
        format: str = "auto",
        encoding: str = "utf-8",
    ) -> List[Dict[str, str]]:
        """Parse a transaction file and return structured data.

        Args:
            file_path: Path to input file
            format: File format ('auto', 'csv', 'txt')
            encoding: File encoding

        Returns:
            List of transaction dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid or parsing fails
        """
        # Validate file path
        validate_file_path(file_path)

        # Detect format if auto
        if format == "auto":
            format = detect_file_format(file_path)

        # Parse based on format
        if format == "csv":
            return self._parse_csv_file(file_path, encoding)
        elif format == "txt":
            return self._parse_txt_file(file_path, encoding)
        else:
            raise ValueError(f"Unsupported file format: {format}")

    def _parse_csv_file(self, file_path: Path, encoding: str) -> List[Dict[str, str]]:
        """Parse CSV file with column detection.

        Args:
            file_path: Path to CSV file
            encoding: File encoding

        Returns:
            List of transaction dictionaries
        """
        try:
            # Read CSV file with header detection
            df = pd.read_csv(file_path, encoding=encoding, header=None)

            if df.empty:
                raise ValueError("CSV file is empty")

            # Find the row with actual headers (skip empty rows)
            header_row = None
            for i, row in df.iterrows():
                if not row.isna().all() and any(
                    "date" in str(cell).lower() or "transaction" in str(cell).lower()
                    for cell in row
                ):
                    header_row = i
                    break

            if header_row is None:
                raise ValueError("Could not find header row in CSV file")

            # Read CSV again with the correct header row
            df = pd.read_csv(file_path, encoding=encoding, header=header_row)

            if df.empty:
                raise ValueError("CSV file is empty after header detection")

            # Detect columns from headers
            detected_columns = self.detector.detect_from_headers(df.columns.tolist())

            # If headers didn't provide enough info, analyze data
            if len(detected_columns) < 3:
                data_detected = self.detector.detect_from_data(df)
                detected_columns.update(data_detected)

            # Validate detected columns
            is_valid, missing = self.detector.validate_detected_columns(
                detected_columns
            )
            if not is_valid:
                raise ValueError(f"Missing required columns: {missing}")

            # Convert to transaction list
            return self._dataframe_to_transactions(df, detected_columns)

        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {e}") from e

    def _parse_txt_file(self, file_path: Path, encoding: str) -> List[Dict[str, str]]:
        """Parse TXT file with column detection.

        Args:
            file_path: Path to TXT file
            encoding: File encoding

        Returns:
            List of transaction dictionaries
        """
        try:
            # Check for .cols file
            try:
                column_names = read_cols_file(file_path)
                return self._parse_txt_with_headers(file_path, column_names, encoding)
            except FileNotFoundError:
                # No .cols file, try to detect format and parse
                return self._parse_txt_auto_detect(file_path, encoding)

        except Exception as e:
            raise ValueError(f"Error parsing TXT file: {e}") from e

    def _parse_txt_with_headers(
        self,
        file_path: Path,
        column_names: List[str],
        encoding: str,
    ) -> List[Dict[str, str]]:
        """Parse TXT file with provided column headers.

        Args:
            file_path: Path to TXT file
            column_names: List of column names
            encoding: File encoding

        Returns:
            List of transaction dictionaries
        """
        try:
            # Read as CSV with custom headers
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                names=column_names,
                header=None,
            )

            if df.empty:
                raise ValueError("TXT file is empty")

            # Detect columns from provided headers
            detected_columns = self.detector.detect_from_headers(column_names)

            # Validate detected columns
            is_valid, missing = self.detector.validate_detected_columns(
                detected_columns
            )
            if not is_valid:
                raise ValueError(f"Missing required columns: {missing}")

            # Convert to transaction list
            return self._dataframe_to_transactions(df, detected_columns)

        except Exception as e:
            raise ValueError(f"Error parsing TXT file with headers: {e}") from e

    def _parse_txt_auto_detect(
        self, file_path: Path, encoding: str
    ) -> List[Dict[str, str]]:
        """Parse TXT file with automatic format detection.

        Args:
            file_path: Path to TXT file
            encoding: File encoding

        Returns:
            List of transaction dictionaries
        """
        try:
            # Try different delimiters
            delimiters = [",", "\t", "|", ";"]

            for delimiter in delimiters:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        delimiter=delimiter,
                        header=None,
                    )

                    if not df.empty:
                        # Try to detect columns from data
                        detected_columns = self.detector.detect_from_data(df)

                        # Check if we have enough detected columns
                        is_valid, missing = self.detector.validate_detected_columns(
                            detected_columns
                        )
                        if is_valid:
                            return self._dataframe_to_transactions(df, detected_columns)

                except Exception:
                    continue

            # If no delimiter worked, try fixed-width format
            return self._parse_fixed_width_txt(file_path, encoding)

        except Exception as e:
            raise ValueError(f"Error parsing TXT file with auto-detection: {e}") from e

    def _parse_fixed_width_txt(
        self, file_path: Path, encoding: str
    ) -> List[Dict[str, str]]:
        """Parse fixed-width TXT file.

        Args:
            file_path: Path to TXT file
            encoding: File encoding

        Returns:
            List of transaction dictionaries
        """
        try:
            # Read file as text
            with open(file_path, encoding=encoding) as f:
                lines = f.readlines()

            if not lines:
                raise ValueError("TXT file is empty")

            # Try to detect column boundaries from first few lines
            column_boundaries = self._detect_fixed_width_boundaries(lines[:10])

            if not column_boundaries:
                raise ValueError("Could not detect fixed-width column boundaries")

            # Parse lines into structured data
            transactions = []
            for line in lines:
                if line.strip():
                    row_data = self._parse_fixed_width_line(line, column_boundaries)
                    if row_data:
                        transactions.append(row_data)

            # Convert to DataFrame for column detection
            if transactions:
                df = pd.DataFrame(transactions)
                detected_columns = self.detector.detect_from_data(df)

                # Validate detected columns
                is_valid, missing = self.detector.validate_detected_columns(
                    detected_columns
                )
                if is_valid:
                    return self._dataframe_to_transactions(df, detected_columns)

            raise ValueError("Could not detect required columns in fixed-width file")

        except Exception as e:
            raise ValueError(f"Error parsing fixed-width TXT file: {e}") from e

    def _detect_fixed_width_boundaries(self, lines: List[str]) -> List[Tuple[int, int]]:
        """Detect column boundaries in fixed-width text.

        Args:
            lines: List of text lines

        Returns:
            List of (start, end) column boundaries
        """
        if len(lines) < 2:
            return []

        # Find positions where all lines have consistent spacing
        line_length = max(len(line) for line in lines)
        boundaries = []

        # Simple heuristic: look for consistent spaces
        for i in range(1, line_length):
            if all(i < len(line) and line[i] == " " for line in lines):
                # Check if this is a consistent boundary
                if boundaries and i - boundaries[-1][1] > 1:
                    boundaries.append((boundaries[-1][1], i))

        # If no boundaries found, try to split on consistent spacing
        if not boundaries:
            # Split on multiple spaces
            for line in lines:
                parts = line.split("  ")
                if len(parts) > 1:
                    # Estimate boundaries based on parts
                    current_pos = 0
                    for part in parts[:-1]:
                        current_pos += len(part) + 2
                        boundaries.append((current_pos - 2, current_pos))
                    break

        return boundaries

    def _parse_fixed_width_line(
        self, line: str, boundaries: List[Tuple[int, int]]
    ) -> Dict[str, str]:
        """Parse a single fixed-width line.

        Args:
            line: Text line to parse
            boundaries: Column boundaries

        Returns:
            Dictionary of column values
        """
        result = {}

        for i, (start, end) in enumerate(boundaries):
            if start < len(line):
                value = line[start:end].strip()
                if value:
                    result[f"col_{i}"] = value

        return result

    def _dataframe_to_transactions(
        self,
        df: pd.DataFrame,
        detected_columns: Dict[str, str],
    ) -> List[Dict[str, str]]:
        """Convert DataFrame to list of transaction dictionaries.

        Args:
            df: DataFrame with transaction data
            detected_columns: Dictionary mapping column names to types

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Create reverse mapping from type to column name
        type_to_column = {}
        for col, col_type in detected_columns.items():
            type_to_column[col_type] = col

        for _, row in df.iterrows():
            transaction = {}

            # Map detected columns to transaction fields
            for col_type, col_name in type_to_column.items():
                if col_name in row and pd.notna(row[col_name]):
                    value = str(row[col_name]).strip()
                    if value:
                        transaction[col_type] = value

            # Only add transactions that have required fields
            required = self.detector.get_required_columns()
            if all(field in transaction for field in required):
                transactions.append(transaction)

        return transactions
