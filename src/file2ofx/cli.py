"""CLI entry point for file2ofx."""

import os
import sys
from pathlib import Path
from typing import List, Optional

import click

from .core.ofx_generator import OFXGenerator
from .core.parser import FileParser
from .utils.file_utils import get_output_filename


def complete_file_path(ctx: click.Context, param: click.Parameter, incomplete: str) -> List[str]:
    """Complete file paths for input files (CSV, TXT)."""
    if not incomplete:
        incomplete = "."
    
    try:
        # Handle relative paths
        if incomplete.startswith("./"):
            incomplete = incomplete[2:]
        elif incomplete.startswith("/"):
            # Absolute path
            path = Path(incomplete)
        else:
            # Relative path
            path = Path.cwd() / incomplete
        
        # If incomplete ends with /, look in that directory
        if incomplete.endswith("/"):
            base_path = path
            incomplete_name = ""
        else:
            # Otherwise, look in the parent directory
            base_path = path.parent
            incomplete_name = path.name
        
        if not base_path.exists():
            return []
        
        completions = []
        for item in base_path.iterdir():
            if item.is_file():
                # Only suggest CSV and TXT files
                if item.suffix.lower() in [".csv", ".txt"]:
                    if incomplete.endswith("/"):
                        # If we're in a directory, show relative to current
                        try:
                            rel_path = item.relative_to(Path.cwd())
                            completions.append(str(rel_path))
                        except ValueError:
                            # If not relative, use absolute
                            completions.append(str(item))
                    else:
                        # If we're completing a filename, show matching names
                        if item.name.startswith(incomplete_name):
                            try:
                                rel_path = item.relative_to(Path.cwd())
                                completions.append(str(rel_path))
                            except ValueError:
                                # If not relative, use absolute
                                completions.append(str(item))
        
        return completions
    except Exception:
        return []


def complete_output_path(ctx: click.Context, param: click.Parameter, incomplete: str) -> List[str]:
    """Complete output file paths (suggest .ofx extension)."""
    if not incomplete:
        incomplete = "."
    
    try:
        # Handle relative paths
        if incomplete.startswith("./"):
            incomplete = incomplete[2:]
        elif incomplete.startswith("/"):
            # Absolute path
            path = Path(incomplete)
        else:
            # Relative path
            path = Path.cwd() / incomplete
        
        # If incomplete ends with /, look in that directory
        if incomplete.endswith("/"):
            base_path = path
            incomplete_name = ""
        else:
            # Otherwise, look in the parent directory
            base_path = path.parent
            incomplete_name = path.name
        
        if not base_path.exists():
            return []
        
        completions = []
        for item in base_path.iterdir():
            if item.is_file():
                # Suggest .ofx files or directories
                if item.suffix.lower() == ".ofx" or item.is_dir():
                    if incomplete.endswith("/"):
                        # If we're in a directory, show relative to current
                        try:
                            rel_path = item.relative_to(Path.cwd())
                            completions.append(str(rel_path))
                        except ValueError:
                            # If not relative, use absolute
                            completions.append(str(item))
                    else:
                        # If we're completing a filename, show matching names
                        if item.name.startswith(incomplete_name):
                            try:
                                rel_path = item.relative_to(Path.cwd())
                                completions.append(str(rel_path))
                            except ValueError:
                                # If not relative, use absolute
                                completions.append(str(item))
        
        # Also suggest creating new .ofx files
        if not incomplete.endswith("/"):
            completions.append(f"{incomplete}.ofx")
        
        return completions
    except Exception:
        return []


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), shell_complete=complete_file_path)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["auto", "csv", "txt"]),
    default="auto",
    help="Input file format (default: auto-detect)",
)
@click.option(
    "--encoding",
    "-e",
    default="utf-8",
    help="File encoding (default: utf-8)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    shell_complete=complete_output_path,
    help="Output file path (default: input filename with .ofx extension)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--ofx-version",
    type=click.Choice(["102", "103", "200", "201", "202", "203", "210", "211", "220"]),
    default="102",
    help="OFX version (default: 102 for OFX 1.0.2)",
)
@click.option(
    "--fi-org",
    help="Financial institution organization name",
)
@click.option(
    "--fi-id",
    help="Financial institution ID",
)
@click.option(
    "--account-id",
    help="Account ID",
)
@click.option(
    "--account-type",
    type=click.Choice(["CHECKING", "SAVINGS", "MONEYMRKT", "CREDITLINE"]),
    default="CHECKING",
    help="Account type (default: CHECKING)",
)
@click.option(
    "--currency",
    default="USD",
    help="Currency code (default: USD)",
)

def main(
    file: Path,
    format: str,
    encoding: str,
    output: Optional[Path],
    verbose: bool,
    ofx_version: str,
    fi_org: Optional[str],
    fi_id: Optional[str],
    account_id: Optional[str],
    account_type: str,
    currency: str,
) -> None:
    """Convert transaction files to OFX format.
    
    FILE: Input file path (CSV or TXT)
    """
    try:
        # Determine output file path
        if output is None:
            output = get_output_filename(file)

        if verbose:
            click.echo(f"Converting {file} to {output}")
            click.echo(f"Format: {format}, Encoding: {encoding}")

        # Parse input file
        parser = FileParser()
        transactions = parser.parse_file(file, format=format, encoding=encoding)

        if verbose:
            click.echo(f"Found {len(transactions)} transactions")

        # Generate OFX file
        generator = OFXGenerator()
        generator.generate_ofx(
            transactions, 
            output,
            ofx_version=ofx_version,
            fi_org=fi_org,
            fi_id=fi_id,
            account_id=account_id,
            account_type=account_type,
            currency=currency,
        )

        click.echo(f"Successfully converted {file} to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
