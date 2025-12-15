import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from internal.config import TEMP_DIR


logger = logging.getLogger(__name__)


async def download_file_from_url(url: str, timeout: int = 30) -> Path:
    """
    Download a file from URL to temporary directory.

    Args:
        url: The URL to download from
        timeout: Request timeout in seconds

    Returns:
        Path to the downloaded temporary file

    Raises:
        httpx.HTTPError: If download fails
        ValueError: If URL is invalid
    """
    logger.info("Starting download from URL: %s (timeout=%s)", url, timeout)

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {url}")

    # Generate temporary file path
    file_extension = Path(parsed_url.path).suffix or ".tmp"
    temp_file = tempfile.NamedTemporaryFile(
        dir=TEMP_DIR, suffix=file_extension, delete=False
    )
    temp_path = Path(temp_file.name)
    temp_file.close()

    logger.info(
        "Created temporary file for download: path=%s, extension=%s, temp_dir_exists=%s",
        temp_path,
        file_extension,
        TEMP_DIR.exists(),
    )

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                with open(temp_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

        logger.info(
            "Finished downloading URL to temp file: path=%s, size=%s bytes, exists=%s",
            temp_path,
            temp_path.stat().st_size if temp_path.exists() else None,
            temp_path.exists(),
        )
        return temp_path
    except Exception as e:
        logger.exception(
            "Failed to download URL '%s' to temp file '%s': %s", url, temp_path, e
        )
        if temp_path.exists():
            try:
                temp_path.unlink()
                logger.info("Cleaned up temp file after download failure: %s", temp_path)
            except Exception:
                logger.warning("Failed to remove temp file after download failure: %s", temp_path)
        raise


def save_uploaded_file(file_content: bytes, filename: str) -> Path:
    """
    Save uploaded file content to temporary directory.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        Path to the saved temporary file
    """
    file_extension = Path(filename).suffix
    temp_file = tempfile.NamedTemporaryFile(
        dir=TEMP_DIR, suffix=file_extension, delete=False
    )
    temp_path = Path(temp_file.name)
    temp_file.close()

    logger.info(
        "Created temporary file for upload: original_filename=%s, temp_path=%s, extension=%s, temp_dir_exists=%s",
        filename,
        temp_path,
        file_extension,
        TEMP_DIR.exists(),
    )

    with open(temp_path, "wb") as f:
        f.write(file_content)

    logger.info(
        "Saved uploaded file content to temp file: path=%s, size=%s bytes, exists=%s",
        temp_path,
        temp_path.stat().st_size if temp_path.exists() else None,
        temp_path.exists(),
    )

    return temp_path


def cleanup_temp_file(file_path: Path) -> None:
    """
    Remove temporary file.

    Args:
        file_path: Path to the file to remove
    """
    try:
        if file_path.exists():
            if file_path.is_file():
                logger.info("Removing temporary file: %s", file_path)
                file_path.unlink()
            elif file_path.is_dir():
                logger.info("Removing temporary directory recursively: %s", file_path)
                shutil.rmtree(file_path)
        else:
            logger.info("Temporary path does not exist during cleanup: %s", file_path)
    except Exception as e:
        # Ignore cleanup errors but log them for debugging.
        logger.warning("Failed to clean up temporary path '%s': %s", file_path, e)


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes
    """
    return file_path.stat().st_size


def detect_file_type(file_path: Path) -> Optional[str]:
    """
    Detect file type based on extension.

    Args:
        file_path: Path to the file

    Returns:
        File extension in lowercase, or None if no extension
    """
    extension = file_path.suffix.lower()
    return extension if extension else None
