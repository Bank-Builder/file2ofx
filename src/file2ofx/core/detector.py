"""Column detection logic for file2ofx."""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd


class ColumnDetector:
    """Detect transaction columns from data or headers."""

    # Common column name patterns
    DATE_PATTERNS = [
        r"date",
        r"transaction_date",
        r"post_date",
        r"value_date",
        r"timestamp",
    ]

    AMOUNT_PATTERNS = [
        r"amount",
        r"value",
        r"sum",
        r"total",
        r"debit",
        r"credit",
        r"balance",
    ]

    DESCRIPTION_PATTERNS = [
        r"description",
        r"memo",
        r"note",
        r"details",
        r"reference",
        r"payee",
        r"merchant",
        r"transaction",
    ]

    TYPE_PATTERNS = [
        r"^type$",
        r"^category$",
        r"^classification$",
        r"^transaction_type$",
    ]

    # Date format patterns
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]

    def __init__(self) -> None:
        """Initialize the column detector."""
        self.detected_columns: Dict[str, str] = {}

    def detect_from_headers(self, headers: List[str]) -> Dict[str, str]:
        """Detect column types from header names.
        
        Args:
            headers: List of column header names
            
        Returns:
            Dictionary mapping column names to detected types
        """
        detected = {}

        for header in headers:
            header_lower = header.lower().strip()

            # Check for date columns
            if self._matches_patterns(header_lower, self.DATE_PATTERNS):
                detected[header] = "date"
                continue

            # Check for amount columns
            if self._matches_patterns(header_lower, self.AMOUNT_PATTERNS):
                detected[header] = "amount"
                continue

            # Check for type columns (before description to avoid conflicts)
            if self._matches_patterns(header_lower, self.TYPE_PATTERNS):
                detected[header] = "type"
                continue

            # Check for description columns
            if self._matches_patterns(header_lower, self.DESCRIPTION_PATTERNS):
                detected[header] = "description"
                continue

        self.detected_columns = detected
        return detected

    def detect_from_data(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detect column types by analyzing data content.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to detected types
        """
        detected = {}

        for column in df.columns:
            # Skip if already detected from headers
            if column in self.detected_columns:
                detected[column] = self.detected_columns[column]
                continue

            # Analyze column data
            column_type = self._analyze_column_data(df[column])
            if column_type:
                detected[column] = column_type

        return detected

    def _analyze_column_data(self, series: pd.Series) -> Optional[str]:
        """Analyze a single column's data to determine its type.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Detected column type or None
        """
        # Remove null values for analysis
        non_null_series = series.dropna()

        if len(non_null_series) == 0:
            return None

        # Check for date columns
        if self._is_date_column(non_null_series):
            return "date"

        # Check for amount columns
        if self._is_amount_column(non_null_series):
            return "amount"

        # Check for description columns
        if self._is_description_column(non_null_series):
            return "description"

        # Check for type columns
        if self._is_type_column(non_null_series):
            return "type"

        return None

    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if column contains date data.
        
        Args:
            series: Series to check
            
        Returns:
            True if column appears to contain dates
        """
        # Sample up to 100 values for analysis
        sample = series.head(100)

        date_count = 0
        total_count = len(sample)

        for value in sample:
            if self._is_date_value(str(value)):
                date_count += 1

        # If more than 70% of values look like dates, consider it a date column
        return (date_count / total_count) > 0.7 if total_count > 0 else False

    def _is_date_value(self, value: str) -> bool:
        """Check if a value looks like a date.
        
        Args:
            value: String value to check
            
        Returns:
            True if value appears to be a date
        """
        # Remove common separators and try to parse
        cleaned = re.sub(r"[-/]", "", value.strip())

        # Check for common date patterns
        date_patterns = [
            r"\d{8}",  # YYYYMMDD
            r"\d{6}",  # MMDDYY or YYMMDD
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}/\d{2}/\d{2}",  # MM/DD/YY
        ]

        for pattern in date_patterns:
            if re.match(pattern, value.strip()):
                return True

        # Try parsing with various formats
        for fmt in self.DATE_FORMATS:
            try:
                datetime.strptime(value.strip(), fmt)
                return True
            except ValueError:
                continue

        return False

    def _is_amount_column(self, series: pd.Series) -> bool:
        """Check if column contains amount data.
        
        Args:
            series: Series to check
            
        Returns:
            True if column appears to contain amounts
        """
        # Sample up to 100 values for analysis
        sample = series.head(100)

        amount_count = 0
        total_count = len(sample)

        for value in sample:
            if self._is_amount_value(str(value)):
                amount_count += 1

        # If more than 60% of values look like amounts, consider it an amount column
        return (amount_count / total_count) > 0.6 if total_count > 0 else False

    def _is_amount_value(self, value: str) -> bool:
        """Check if a value looks like an amount.
        
        Args:
            value: String value to check
            
        Returns:
            True if value appears to be an amount
        """
        # Remove currency symbols and whitespace
        cleaned = re.sub(r"[$€£¥₹₽₿]", "", value.strip())

        # Check for numeric patterns with optional decimal places
        amount_patterns = [
            r"^-?\d+\.?\d*$",  # Basic number with optional decimal
            r"^-?\d{1,3}(,\d{3})*(\.\d{2})?$",  # With thousands separators
            r"^-?\d+\.\d{2}$",  # Currency format with cents
        ]

        for pattern in amount_patterns:
            if re.match(pattern, cleaned):
                return True

        return False

    def _is_description_column(self, series: pd.Series) -> bool:
        """Check if column contains description data.
        
        Args:
            series: Series to check
            
        Returns:
            True if column appears to contain descriptions
        """
        # Sample up to 100 values for analysis
        sample = series.head(100)

        desc_count = 0
        total_count = len(sample)

        for value in sample:
            if self._is_description_value(str(value)):
                desc_count += 1

        # If more than 50% of values look like descriptions, consider it a description column
        return (desc_count / total_count) > 0.5 if total_count > 0 else False

    def _is_description_value(self, value: str) -> bool:
        """Check if a value looks like a description.
        
        Args:
            value: String value to check
            
        Returns:
            True if value appears to be a description
        """
        # Descriptions are typically text with mixed case and punctuation
        if not value or len(value.strip()) < 3:
            return False

        # Check for text patterns (not just numbers or dates)
        if self._is_amount_value(value) or self._is_date_value(value):
            return False

        # Descriptions usually have mixed case and some punctuation
        has_mixed_case = any(c.isupper() for c in value) and any(c.islower() for c in value)
        has_punctuation = any(c in ".,!?;:" for c in value)

        return has_mixed_case or has_punctuation

    def _is_type_column(self, series: pd.Series) -> bool:
        """Check if column contains transaction type data.
        
        Args:
            series: Series to check
            
        Returns:
            True if column appears to contain transaction types
        """
        # Sample up to 100 values for analysis
        sample = series.head(100)

        # Check for common transaction type values
        type_values = {
            "debit", "credit", "deposit", "withdrawal", "transfer",
            "payment", "purchase", "refund", "fee", "interest",
            "atm", "check", "ach", "wire", "pos"
        }

        type_count = 0
        total_count = len(sample)

        for value in sample:
            if str(value).lower().strip() in type_values:
                type_count += 1

        # If more than 30% of values are known types, consider it a type column
        return (type_count / total_count) > 0.3 if total_count > 0 else False

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns.
        
        Args:
            text: Text to check
            patterns: List of regex patterns
            
        Returns:
            True if text matches any pattern
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def get_required_columns(self) -> List[str]:
        """Get list of required column types for OFX generation.
        
        Returns:
            List of required column types
        """
        return ["date", "amount", "description"]

    def validate_detected_columns(self, detected: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate that required columns are detected.
        
        Args:
            detected: Dictionary of detected column types
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        required = self.get_required_columns()
        detected_types = set(detected.values())

        missing = [col for col in required if col not in detected_types]
        is_valid = len(missing) == 0

        return is_valid, missing
