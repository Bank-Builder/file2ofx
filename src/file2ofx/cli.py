"""CLI entry point for file2ofx."""

import sys
from pathlib import Path
from typing import Optional

import click

from .core.ofx_generator import OFXGenerator
from .core.parser import FileParser
from .utils.file_utils import get_output_filename


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
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
    help="Output file path (default: input filename with .ofx extension)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    file: Path,
    format: str,
    encoding: str,
    output: Optional[Path],
    verbose: bool,
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
        generator.generate_ofx(transactions, output)

        click.echo(f"Successfully converted {file} to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
