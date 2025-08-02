#!/usr/bin/env python3
"""Generate test data for file2ofx project."""

import csv
from datetime import datetime
from pathlib import Path


def generate_csv_test_data(output_dir: Path) -> None:
    """Generate CSV test data files.
    
    Args:
        output_dir: Directory to save test files
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate sample CSV with headers
    csv_file = output_dir / "example_transactions.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write headers
        writer.writerow(["Date", "Description", "Amount", "Type"])

        # Generate sample transactions
        base_date = datetime(2023, 1, 1)
        transactions = [
            ["2023-01-01", "Grocery store purchase", "125.50", "debit"],
            ["2023-01-02", "ATM withdrawal", "200.00", "debit"],
            ["2023-01-03", "Salary deposit", "2500.00", "credit"],
            ["2023-01-04", "Gas station", "45.75", "debit"],
            ["2023-01-05", "Online payment", "89.99", "debit"],
            ["2023-01-06", "Restaurant bill", "67.25", "debit"],
            ["2023-01-07", "Interest payment", "12.50", "credit"],
            ["2023-01-08", "Utility bill", "150.00", "debit"],
            ["2023-01-09", "Refund", "25.00", "credit"],
            ["2023-01-10", "Coffee shop", "4.50", "debit"],
        ]

        writer.writerows(transactions)

    print(f"Generated CSV test file: {csv_file}")

    # Generate CSV with different column names
    csv_file2 = output_dir / "example_bank_statement.csv"
    with open(csv_file2, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write headers
        writer.writerow(["Transaction_Date", "Memo", "Value", "Category"])

        # Generate sample transactions
        transactions = [
            ["01/15/2023", "Direct deposit", "3000.00", "deposit"],
            ["01/16/2023", "Check payment", "500.00", "payment"],
            ["01/17/2023", "Service fee", "15.00", "fee"],
            ["01/18/2023", "Transfer in", "1000.00", "transfer"],
            ["01/19/2023", "Purchase", "75.25", "purchase"],
        ]

        writer.writerows(transactions)

    print(f"Generated CSV test file: {csv_file2}")


def generate_txt_test_data(output_dir: Path) -> None:
    """Generate TXT test data files.
    
    Args:
        output_dir: Directory to save test files
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate TXT file with .cols companion file
    txt_file = output_dir / "bankfile.txt"
    cols_file = output_dir / "bankfile.cols"

    # Write .cols file
    with open(cols_file, "w", encoding="utf-8") as f:
        f.write('"Date","Description","Amount","Type"\n')

    # Write TXT file (CSV format without headers)
    with open(txt_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Generate sample transactions
        transactions = [
            ["2023-02-01", "Grocery purchase", "85.30", "debit"],
            ["2023-02-02", "ATM withdrawal", "100.00", "debit"],
            ["2023-02-03", "Salary deposit", "2800.00", "credit"],
            ["2023-02-04", "Gas station", "52.45", "debit"],
            ["2023-02-05", "Online shopping", "120.75", "debit"],
        ]

        writer.writerows(transactions)

    print(f"Generated TXT test file: {txt_file}")
    print(f"Generated COLS file: {cols_file}")

    # Generate fixed-width TXT file
    fixed_width_file = output_dir / "fixed_width_statement.txt"

    with open(fixed_width_file, "w", encoding="utf-8") as f:
        # Fixed-width format: Date(10) Description(30) Amount(10) Type(10)
        transactions = [
            "2023-03-01Grocery store purchase   125.50    debit    ",
            "2023-03-02ATM withdrawal           200.00    debit    ",
            "2023-03-03Salary deposit           2500.00   credit   ",
            "2023-03-04Gas station              45.75     debit    ",
            "2023-03-05Online payment           89.99     debit    ",
        ]

        for transaction in transactions:
            f.write(transaction + "\n")

    print(f"Generated fixed-width TXT file: {fixed_width_file}")


def generate_malformed_test_data(output_dir: Path) -> None:
    """Generate malformed test data for error testing.
    
    Args:
        output_dir: Directory to save test files
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Empty file
    empty_file = output_dir / "empty.csv"
    empty_file.touch()
    print(f"Generated empty file: {empty_file}")

    # File with missing required columns
    missing_cols_file = output_dir / "missing_columns.csv"
    with open(missing_cols_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Status"])
        writer.writerow(["1", "John", "Active"])
        writer.writerow(["2", "Jane", "Inactive"])

    print(f"Generated file with missing columns: {missing_cols_file}")

    # File with invalid data
    invalid_data_file = output_dir / "invalid_data.csv"
    with open(invalid_data_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Description", "Amount"])
        writer.writerow(["not-a-date", "Description", "not-an-amount"])
        writer.writerow(["2023-01-01", "", "100.00"])

    print(f"Generated file with invalid data: {invalid_data_file}")


def main():
    """Generate all test data files."""
    output_dir = Path("test_data")

    print("Generating test data files...")

    # Generate CSV test data
    generate_csv_test_data(output_dir)

    # Generate TXT test data
    generate_txt_test_data(output_dir)

    # Generate malformed test data
    generate_malformed_test_data(output_dir)

    print("\nTest data generation complete!")
    print(f"Files saved in: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
