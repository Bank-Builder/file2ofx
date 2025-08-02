#!/usr/bin/env python3
"""Test script to demonstrate tab completion functionality."""

import shutil
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from file2ofx.cli import complete_file_path, complete_output_path  # noqa: E402


def test_file_completion():
    """Test file path completion."""
    print("Testing file path completion...")

    # Create some test files
    test_dir = Path("test_completion")
    test_dir.mkdir(exist_ok=True)

    # Create test files
    (test_dir / "test1.csv").touch()
    (test_dir / "test2.txt").touch()
    (test_dir / "test3.ofx").touch()
    (test_dir / "ignore.py").touch()

    print(f"Created test files in {test_dir}")

    # Test completions
    test_cases = [
        "",  # Empty
        "test_completion/",  # Directory
        "test_completion/t",  # Partial filename
        "test_completion/test1",  # Full filename
    ]

    for incomplete in test_cases:
        completions = complete_file_path(None, None, incomplete)
        print(f"Input: '{incomplete}' -> Completions: {completions}")

    # Cleanup
    shutil.rmtree(test_dir)
    print("Cleaned up test files")


def test_output_completion():
    """Test output path completion."""
    print("\nTesting output path completion...")

    # Create some test files
    test_dir = Path("test_completion")
    test_dir.mkdir(exist_ok=True)

    # Create test files
    (test_dir / "output1.ofx").touch()
    (test_dir / "output2.txt").touch()
    (test_dir / "output3.csv").touch()

    print(f"Created test files in {test_dir}")

    # Test completions
    test_cases = [
        "",  # Empty
        "test_completion/",  # Directory
        "test_completion/o",  # Partial filename
        "test_completion/output1",  # Full filename
        "newfile",  # New file suggestion
    ]

    for incomplete in test_cases:
        completions = complete_output_path(None, None, incomplete)
        print(f"Input: '{incomplete}' -> Completions: {completions}")

    # Cleanup
    shutil.rmtree(test_dir)
    print("Cleaned up test files")


if __name__ == "__main__":
    test_file_completion()
    test_output_completion()
    print("\nTab completion test completed!")
