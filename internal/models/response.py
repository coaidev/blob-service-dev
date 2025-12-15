"""Response models."""
from pydantic import BaseModel


class ConvertResponse(BaseModel):
    """Response model for conversion result."""

    success: bool
    """Whether conversion was successful"""
    markdown: str | None = None
    """Converted markdown content"""
    error: str | None = None
    """Error message if conversion failed"""
    filename: str | None = None
    """Original filename"""
    file_type: str | None = None
    """File type/extension"""

