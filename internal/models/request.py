"""Request models."""
from pydantic import BaseModel, HttpUrl


class ConvertFromUrlRequest(BaseModel):
    """Request model for URL-based conversion."""

    url: HttpUrl
    """URL of the file to convert"""

