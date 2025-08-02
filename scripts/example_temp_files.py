#!/usr/bin/env python3
"""Example script demonstrating temporary file naming convention."""

from pathlib import Path

from file2ofx.utils import create_temp_file


def main():
    """Demonstrate temporary file creation with _.filename.ext convention."""
    print("Creating temporary files with _.filename.ext naming convention...")
    
    # Create temporary files in current directory
    temp_dir = Path(".")
    
    # Example 1: Basic temporary file
    temp1 = create_temp_file("example", ".txt", temp_dir)
    print(f"Created: {temp1}")
    
    # Example 2: Temporary CSV file
    temp2 = create_temp_file("data", ".csv", temp_dir)
    print(f"Created: {temp2}")
    
    # Example 3: Temporary OFX file
    temp3 = create_temp_file("output", ".ofx", temp_dir)
    print(f"Created: {temp3}")
    
    # Write some content to demonstrate
    temp1.write_text("This is a temporary file that will be ignored by git.")
    temp2.write_text("date,description,amount\n2023-01-01,test,100.00")
    temp3.write_text("<OFX><BANKMSGSRSV1></BANKMSGSRSV1></OFX>")
    
    print("\nFiles created successfully!")
    print("Note: These files will be automatically ignored by git due to the _.* pattern.")
    print("You can safely delete them when no longer needed.")


if __name__ == "__main__":
    main() 