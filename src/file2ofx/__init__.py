"""file2ofx - Convert transaction files to OFX format with auto-column detection."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.detector import ColumnDetector
from .core.ofx_generator import OFXGenerator
from .core.parser import FileParser
from .utils.file_utils import get_output_filename

__all__ = [
    "ColumnDetector",
    "FileParser",
    "OFXGenerator",
    "get_output_filename",
]
