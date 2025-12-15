"""MarkItDown converter implementation."""
from pathlib import Path

from markitdown import MarkItDown

from internal.converters.base import BaseConverter


class MarkItDownConverter(BaseConverter):
    """Converter using MarkItDown library."""

    def __init__(self):
        """Initialize MarkItDown converter."""
        self.converter = MarkItDown()

    async def convert(self, file_path: Path) -> str:
        """
        Convert document to markdown using MarkItDown.

        Args:
            file_path: Path to the file to convert

        Returns:
            Markdown content as string

        Raises:
            Exception: If conversion fails
        """
        try:
            result = self.converter.convert(str(file_path))
            return result.text_content
        except Exception as e:
            raise Exception(f"Failed to convert file: {str(e)}") from e


# Global converter instance
_converter_instance: MarkItDownConverter | None = None


def get_converter() -> MarkItDownConverter:
    """
    Get or create converter instance.

    Returns:
        MarkItDownConverter instance
    """
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = MarkItDownConverter()
    return _converter_instance

