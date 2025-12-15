"""File validation utilities."""
from pathlib import Path

from internal.config import MAX_FILE_SIZE, SUPPORTED_EXTENSIONS


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_file_type(file_path: Path) -> None:
    """
    Validate if file type is supported.

    Args:
        file_path: Path to the file to validate

    Raises:
        ValidationError: If file type is not supported
    """
    extension = file_path.suffix.lower()
    if not extension:
        raise ValidationError("File has no extension")
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValidationError(
            f"File type '{extension}' is not supported. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def validate_file_size(file_path: Path) -> None:
    """
    Validate if file size is within limits.

    Args:
        file_path: Path to the file to validate

    Raises:
        ValidationError: If file size exceeds limit
    """
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum "
            f"allowed size ({MAX_FILE_SIZE / 1024 / 1024:.2f} MB)"
        )


def validate_file(file_path: Path) -> None:
    """
    Validate file type and size.

    Args:
        file_path: Path to the file to validate

    Raises:
        ValidationError: If validation fails
    """
    if not file_path.exists():
        raise ValidationError("File does not exist")
    if not file_path.is_file():
        raise ValidationError("Path is not a file")
    validate_file_type(file_path)
    validate_file_size(file_path)

