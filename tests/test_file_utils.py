"""Tests for file utility functions."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from file2ofx.utils.file_utils import (
    create_temp_file,
    detect_file_format,
    get_output_filename,
    read_cols_file,
    validate_file_path,
)


class TestGetOutputFilename:
    """Test output filename generation."""

    def test_basic_output_filename(self, tmp_path):
        """Test basic output filename generation."""
        input_file = tmp_path / "test.csv"
        output_file = get_output_filename(input_file)

        assert output_file == tmp_path / "test.ofx"

    def test_output_filename_with_conflict(self, tmp_path):
        """Test output filename when file already exists."""
        input_file = tmp_path / "test.csv"
        existing_file = tmp_path / "test.ofx"
        existing_file.touch()

        output_file = get_output_filename(input_file)

        assert output_file == tmp_path / "test_1.ofx"

    def test_output_filename_multiple_conflicts(self, tmp_path):
        """Test output filename with multiple existing files."""
        input_file = tmp_path / "test.csv"

        # Create base file first
        base_file = tmp_path / "test.ofx"
        base_file.touch()

        # Create multiple existing files
        for i in range(1, 4):
            existing_file = tmp_path / f"test_{i}.ofx"
            existing_file.touch()

        output_file = get_output_filename(input_file)

        assert output_file == tmp_path / "test_4.ofx"

    def test_invalid_input_filename(self):
        """Test error handling for invalid input filename."""
        input_file = Path("")

        with pytest.raises(ValueError, match="Input file must have a valid name"):
            get_output_filename(input_file)


class TestDetectFileFormat:
    """Test file format detection."""

    def test_csv_extension(self, tmp_path):
        """Test CSV format detection from extension."""
        csv_file = tmp_path / "test.csv"
        csv_file.touch()

        format_type = detect_file_format(csv_file)

        assert format_type == "csv"

    def test_txt_extension_csv_content(self, tmp_path):
        """Test TXT file with CSV content."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("col1,col2,col3\nval1,val2,val3")

        format_type = detect_file_format(txt_file)

        assert format_type == "csv"

    def test_txt_extension_plain_content(self, tmp_path):
        """Test TXT file with plain content."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is plain text content")

        format_type = detect_file_format(txt_file)

        assert format_type == "txt"

    def test_unknown_extension(self, tmp_path):
        """Test unknown extension defaults to txt."""
        unknown_file = tmp_path / "test.xyz"
        unknown_file.touch()

        format_type = detect_file_format(unknown_file)

        assert format_type == "txt"


class TestReadColsFile:
    """Test reading column definition files."""

    def test_read_cols_file_success(self, tmp_path):
        """Test successful reading of .cols file."""
        input_file = tmp_path / "test.txt"
        cols_file = tmp_path / "test.cols"
        cols_file.write_text('"Date","Description","Amount"')

        columns = read_cols_file(input_file)

        assert columns == ["Date", "Description", "Amount"]

    def test_read_cols_file_unquoted(self, tmp_path):
        """Test reading unquoted column names."""
        input_file = tmp_path / "test.txt"
        cols_file = tmp_path / "test.cols"
        cols_file.write_text("Date,Description,Amount")

        columns = read_cols_file(input_file)

        assert columns == ["Date", "Description", "Amount"]

    def test_read_cols_file_mixed_quotes(self, tmp_path):
        """Test reading mixed quoted and unquoted names."""
        input_file = tmp_path / "test.txt"
        cols_file = tmp_path / "test.cols"
        cols_file.write_text('"Date",Description,"Amount"')

        columns = read_cols_file(input_file)

        assert columns == ["Date", "Description", "Amount"]

    def test_read_cols_file_not_found(self, tmp_path):
        """Test error when .cols file doesn't exist."""
        input_file = tmp_path / "test.txt"
        input_file.touch()

        with pytest.raises(FileNotFoundError, match="Column definition file not found"):
            read_cols_file(input_file)

    def test_read_cols_file_empty(self, tmp_path):
        """Test error when .cols file is empty."""
        input_file = tmp_path / "test.txt"
        cols_file = tmp_path / "test.cols"
        cols_file.write_text("")

        with pytest.raises(ValueError, match="No column names found"):
            read_cols_file(input_file)


class TestValidateFilePath:
    """Test file path validation."""

    def test_valid_file_path(self, tmp_path):
        """Test validation of valid file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Should not raise any exception
        validate_file_path(test_file)

    def test_file_not_found(self, tmp_path):
        """Test error when file doesn't exist."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError, match="File not found"):
            validate_file_path(test_file)

    def test_directory_not_file(self, tmp_path):
        """Test error when path is a directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(ValueError, match="Path is not a file"):
            validate_file_path(test_dir)

    def test_empty_file(self, tmp_path):
        """Test error when file is empty."""
        test_file = tmp_path / "empty.txt"
        test_file.touch()

        with pytest.raises(ValueError, match="File is empty"):
            validate_file_path(test_file)

    @patch("pathlib.Path.resolve")
    def test_unsafe_path(self, mock_resolve, tmp_path):
        """Test error for unsafe file paths."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Mock resolve to return an unsafe path
        mock_resolve.return_value = Path("/etc/passwd")

        with pytest.raises(ValueError, match="Unsafe file path"):
            validate_file_path(test_file)


class TestCreateTempFile:
    """Test temporary file creation."""

    def test_create_temp_file_basic(self, tmp_path):
        """Test basic temporary file creation."""
        temp_file = create_temp_file("test", ".txt", tmp_path)

        assert temp_file.name.startswith("_.test")
        assert temp_file.suffix == ".txt"
        assert temp_file.exists()
        assert temp_file.parent == tmp_path

    def test_create_temp_file_defaults(self):
        """Test temporary file creation with defaults."""
        temp_file = create_temp_file()

        assert temp_file.name.startswith("_.temp")
        assert temp_file.exists()
        assert temp_file.parent == Path(tempfile.gettempdir())

    def test_create_temp_file_custom_prefix_suffix(self, tmp_path):
        """Test temporary file creation with custom prefix and suffix."""
        temp_file = create_temp_file("custom", ".csv", tmp_path)

        assert temp_file.name == "_.custom.csv"
        assert temp_file.exists()
        assert temp_file.parent == tmp_path
