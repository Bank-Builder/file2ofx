"""Integration tests for file2ofx."""


import pytest

from file2ofx.core.ofx_generator import OFXGenerator
from file2ofx.core.parser import FileParser
from file2ofx.utils.file_utils import get_output_filename


class TestIntegration:
    """Integration tests for the complete file2ofx workflow."""

    def test_csv_to_ofx_workflow(self, tmp_path):
        """Test complete CSV to OFX conversion workflow."""
        # Create test CSV file
        csv_file = tmp_path / "test_transactions.csv"
        csv_content = """Date,Description,Amount,Type
2023-01-01,Grocery store purchase,125.50,debit
2023-01-02,ATM withdrawal,200.00,debit
2023-01-03,Salary deposit,2500.00,credit
2023-01-04,Gas station,45.75,debit
2023-01-05,Online payment,89.99,debit"""

        csv_file.write_text(csv_content)

        # Parse CSV file
        parser = FileParser()
        transactions = parser.parse_file(csv_file, format="csv")

        # Verify transactions were parsed correctly
        assert len(transactions) == 5
        assert all("date" in t for t in transactions)
        assert all("amount" in t for t in transactions)
        assert all("description" in t for t in transactions)

        # Generate OFX file
        output_file = get_output_filename(csv_file)
        generator = OFXGenerator()
        generator.generate_ofx(transactions, output_file)

        # Verify OFX file was created
        assert output_file.exists()
        assert output_file.suffix == ".ofx"

        # Verify OFX content
        ofx_content = output_file.read_text()
        assert "OFX" in ofx_content
        assert "BANKMSGSRSV1" in ofx_content
        assert "STMTTRN" in ofx_content

    def test_txt_with_cols_workflow(self, tmp_path):
        """Test TXT file with .cols file workflow."""
        # Create .cols file
        cols_file = tmp_path / "test_transactions.cols"
        cols_content = '"Date","Description","Amount","Type"'
        cols_file.write_text(cols_content)

        # Create TXT file (without headers)
        txt_file = tmp_path / "test_transactions.txt"
        txt_content = """2023-01-01,Grocery store purchase,125.50,debit
2023-01-02,ATM withdrawal,200.00,debit
2023-01-03,Salary deposit,2500.00,credit"""

        txt_file.write_text(txt_content)

        # Parse TXT file
        parser = FileParser()
        transactions = parser.parse_file(txt_file, format="txt")

        # Verify transactions were parsed correctly
        assert len(transactions) == 3
        assert all("date" in t for t in transactions)
        assert all("amount" in t for t in transactions)
        assert all("description" in t for t in transactions)

        # Generate OFX file
        output_file = get_output_filename(txt_file)
        generator = OFXGenerator()
        generator.generate_ofx(transactions, output_file)

        # Verify OFX file was created
        assert output_file.exists()
        assert output_file.suffix == ".ofx"

    def test_output_filename_conflict_resolution(self, tmp_path):
        """Test output filename conflict resolution."""
        # Create input file
        input_file = tmp_path / "test.csv"
        input_file.write_text("test content")

        # Create existing output file
        existing_file = tmp_path / "test.ofx"
        existing_file.write_text("existing content")

        # Get output filename
        output_file = get_output_filename(input_file)

        # Should generate unique filename
        assert output_file == tmp_path / "test_1.ofx"
        assert not output_file.exists()

    def test_error_handling_invalid_file(self, tmp_path):
        """Test error handling for invalid files."""
        # Create file with missing required columns
        invalid_file = tmp_path / "invalid.csv"
        invalid_content = """ID,Name,Status
1,John,Active
2,Jane,Inactive"""

        invalid_file.write_text(invalid_content)

        # Try to parse invalid file
        parser = FileParser()

        with pytest.raises(ValueError, match="Could not find header row in CSV file"):
            parser.parse_file(invalid_file, format="csv")

    def test_error_handling_empty_file(self, tmp_path):
        """Test error handling for empty files."""
        # Create empty file
        empty_file = tmp_path / "empty.csv"
        empty_file.touch()

        # Try to parse empty file
        parser = FileParser()

        with pytest.raises(ValueError, match="File is empty"):
            parser.parse_file(empty_file, format="csv")

    def test_ofx_generator_empty_transactions(self, tmp_path):
        """Test OFX generator with empty transactions."""
        generator = OFXGenerator()
        output_file = tmp_path / "empty.ofx"

        with pytest.raises(ValueError, match="No transactions to convert"):
            generator.generate_ofx([], output_file)

    def test_ofx_generator_invalid_transactions(self, tmp_path):
        """Test OFX generator with invalid transactions."""
        generator = OFXGenerator()
        output_file = tmp_path / "invalid.ofx"

        # Transactions missing required fields
        invalid_transactions = [
            {"date": "2023-01-01"},  # Missing amount and description
            {"amount": "100.00"},    # Missing date and description
        ]

        # Should still work as long as some transactions have required fields
        # The parser should filter out invalid transactions
        generator.generate_ofx(invalid_transactions, output_file)

        # Verify file was created (even if empty)
        assert output_file.exists()
