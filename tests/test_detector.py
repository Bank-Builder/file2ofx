"""Tests for column detection functionality."""

import pandas as pd

from file2ofx.core.detector import ColumnDetector


class TestColumnDetector:
    """Test column detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ColumnDetector()

    def test_detect_from_headers_date(self):
        """Test detection of date columns from headers."""
        headers = ["Date", "Transaction_Date", "Post_Date", "Value_Date"]

        detected = self.detector.detect_from_headers(headers)

        assert detected["Date"] == "date"
        assert detected["Transaction_Date"] == "date"
        assert detected["Post_Date"] == "date"
        assert detected["Value_Date"] == "date"

    def test_detect_from_headers_amount(self):
        """Test detection of amount columns from headers."""
        headers = ["Amount", "Value", "Sum", "Total", "Debit", "Credit"]

        detected = self.detector.detect_from_headers(headers)

        assert detected["Amount"] == "amount"
        assert detected["Value"] == "amount"
        assert detected["Sum"] == "amount"
        assert detected["Total"] == "amount"
        assert detected["Debit"] == "debit"
        assert detected["Credit"] == "credit"

    def test_detect_from_headers_description(self):
        """Test detection of description columns from headers."""
        headers = ["Description", "Memo", "Note", "Details", "Reference"]

        detected = self.detector.detect_from_headers(headers)

        assert detected["Description"] == "description"
        assert detected["Memo"] == "description"
        assert detected["Note"] == "description"
        assert detected["Details"] == "description"
        assert detected["Reference"] == "description"

    def test_detect_from_headers_type(self):
        """Test detection of type columns from headers."""
        headers = ["Type", "Category", "Classification", "Transaction_Type"]

        detected = self.detector.detect_from_headers(headers)

        assert detected["Type"] == "type"
        assert detected["Category"] == "type"
        assert detected["Classification"] == "type"
        assert detected["Transaction_Type"] == "type"

    def test_detect_from_data_date_column(self):
        """Test detection of date columns from data."""
        data = {
            "col1": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "col2": ["100.00", "200.00", "300.00"],
            "col3": ["Description 1", "Description 2", "Description 3"],
        }
        df = pd.DataFrame(data)

        detected = self.detector.detect_from_data(df)

        assert "col1" in detected
        assert detected["col1"] == "date"

    def test_detect_from_data_amount_column(self):
        """Test detection of amount columns from data."""
        data = {
            "col1": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "col2": ["100.00", "200.00", "300.00"],
            "col3": ["Description 1", "Description 2", "Description 3"],
        }
        df = pd.DataFrame(data)

        detected = self.detector.detect_from_data(df)

        assert "col2" in detected
        assert detected["col2"] == "amount"

    def test_detect_from_data_description_column(self):
        """Test detection of description columns from data."""
        data = {
            "col1": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "col2": ["100.00", "200.00", "300.00"],
            "col3": ["Description 1", "Description 2", "Description 3"],
        }
        df = pd.DataFrame(data)

        detected = self.detector.detect_from_data(df)

        assert "col3" in detected
        assert detected["col3"] == "description"

    def test_detect_from_data_type_column(self):
        """Test detection of type columns from data."""
        data = {
            "col1": ["debit", "credit", "debit"],
            "col2": ["100.00", "200.00", "300.00"],
            "col3": ["Description 1", "Description 2", "Description 3"],
        }
        df = pd.DataFrame(data)

        detected = self.detector.detect_from_data(df)

        assert "col1" in detected
        assert detected["col1"] == "type"

    def test_is_date_value_valid_formats(self):
        """Test date value detection with valid formats."""
        valid_dates = [
            "2023-01-01",
            "01/01/2023",
            "2023/01/01",
            "01-01-2023",
            "20230101",
        ]

        for date_str in valid_dates:
            assert self.detector._is_date_value(date_str)

    def test_is_date_value_invalid_formats(self):
        """Test date value detection with invalid formats."""
        invalid_dates = [
            "not a date",
            "123",
            "abc",
            "",
        ]

        for date_str in invalid_dates:
            assert not self.detector._is_date_value(date_str)

    def test_is_amount_value_valid_formats(self):
        """Test amount value detection with valid formats."""
        valid_amounts = [
            "100.00",
            "100",
            "1,000.00",
            "$100.00",
            "-100.00",
            "100.50",
        ]

        for amount_str in valid_amounts:
            assert self.detector._is_amount_value(amount_str)

    def test_is_amount_value_invalid_formats(self):
        """Test amount value detection with invalid formats."""
        invalid_amounts = [
            "not an amount",
            "abc",
            "",
            "100.abc",
        ]

        for amount_str in invalid_amounts:
            assert not self.detector._is_amount_value(amount_str)

    def test_is_description_value_valid(self):
        """Test description value detection with valid descriptions."""
        valid_descriptions = [
            "Grocery store purchase",
            "ATM withdrawal",
            "Online payment",
            "Restaurant bill",
        ]

        for desc_str in valid_descriptions:
            assert self.detector._is_description_value(desc_str)

    def test_is_description_value_invalid(self):
        """Test description value detection with invalid descriptions."""
        invalid_descriptions = [
            "123",
            "2023-01-01",
            "100.00",
            "ab",
            "",
        ]

        for desc_str in invalid_descriptions:
            assert not self.detector._is_description_value(desc_str)

    def test_is_type_column_valid(self):
        """Test type column detection with valid transaction types."""
        data = {
            "col1": ["debit", "credit", "deposit", "withdrawal"],
        }
        df = pd.DataFrame(data)

        assert self.detector._is_type_column(df["col1"])

    def test_is_type_column_invalid(self):
        """Test type column detection with invalid transaction types."""
        data = {
            "col1": ["random", "text", "values"],
        }
        df = pd.DataFrame(data)

        assert not self.detector._is_type_column(df["col1"])

    def test_matches_patterns(self):
        """Test pattern matching functionality."""
        text = "transaction_date"
        patterns = [r"date", r"transaction"]

        assert self.detector._matches_patterns(text, patterns)

    def test_matches_patterns_no_match(self):
        """Test pattern matching with no matches."""
        text = "random_text"
        patterns = [r"date", r"amount"]

        assert not self.detector._matches_patterns(text, patterns)

    def test_get_required_columns(self):
        """Test getting required columns."""
        required = self.detector.get_required_columns()

        assert "date" in required
        assert "description" in required
        # Note: amount is no longer always required since we support separate debit/credit columns
        assert len(required) == 2

    def test_validate_detected_columns_valid(self):
        """Test validation of detected columns with all required."""
        detected = {
            "col1": "date",
            "col2": "amount",
            "col3": "description",
        }

        is_valid, missing = self.detector.validate_detected_columns(detected)

        assert is_valid
        assert missing == []

    def test_validate_detected_columns_missing(self):
        """Test validation of detected columns with missing required."""
        detected = {
            "col1": "date",
            "col2": "amount",
        }

        is_valid, missing = self.detector.validate_detected_columns(detected)

        assert not is_valid
        assert "description" in missing
