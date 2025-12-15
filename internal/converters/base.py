"""Base converter interface."""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):
    """Abstract base class for document converters."""

    @abstractmethod
    async def convert(self, file_path: Path) -> str:
        """
        Convert document to markdown.

        Args:
            file_path: Path to the file to convert

        Returns:
            Markdown content as string

        Raises:
            Exception: If conversion fails
        """
        pass

