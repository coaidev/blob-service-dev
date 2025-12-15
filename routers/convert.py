import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from internal.converters.markitdown_converter import get_converter
from internal.models.request import ConvertFromUrlRequest
from internal.models.response import ConvertResponse
from internal.utils.file import (
    cleanup_temp_file,
    download_file_from_url,
    save_uploaded_file,
)
from internal.utils.validators import ValidationError, validate_file


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/upload", response_model=ConvertResponse)
async def convert_from_upload(file: UploadFile = File(...)) -> ConvertResponse:
    """
    Convert uploaded file to markdown.

    Args:
        file: Uploaded file

    Returns:
        ConvertResponse with markdown content
    """
    temp_file_path: Path | None = None
    try:
        logger.info(
            "Received upload request: filename=%s, content_type=%s",
            file.filename,
            getattr(file, "content_type", None),
        )

        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        temp_file_path = save_uploaded_file(file_content, file.filename or "unknown")
        logger.info("Saved uploaded file to temp path: %s", temp_file_path)

        validate_file(temp_file_path)
        logger.info("Validated temp file: %s (exists=%s)", temp_file_path, temp_file_path.exists())

        converter = get_converter()
        logger.info("Starting conversion for temp file: %s", temp_file_path)
        markdown_content = await converter.convert(temp_file_path)
        logger.info(
            "Conversion finished for temp file: %s, markdown_length=%s",
            temp_file_path,
            len(markdown_content) if markdown_content is not None else None,
        )

        return ConvertResponse(
            success=True,
            markdown=markdown_content,
            filename=file.filename,
            file_type=temp_file_path.suffix.lower() if temp_file_path.suffix else None,
        )

    except ValidationError as e:
        logger.warning(
            "Validation error for uploaded file '%s': %s",
            getattr(file, "filename", None),
            e,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(
            "Unexpected error while processing uploaded file '%s': %s",
            getattr(file, "filename", None),
            e,
        )
        return ConvertResponse(
            success=False,
            error=str(e),
            filename=file.filename if file else None,
        )
    finally:
        if temp_file_path:
            logger.info("Cleaning up temp file for upload: %s", temp_file_path)
            cleanup_temp_file(temp_file_path)


@router.post("/url", response_model=ConvertResponse)
async def convert_from_url(request: ConvertFromUrlRequest) -> ConvertResponse:
    """
    Convert file from URL to markdown.

    Args:
        request: ConvertFromUrlRequest with file URL

    Returns:
        ConvertResponse with markdown content
    """
    temp_file_path: Path | None = None
    try:
        logger.info("Received URL conversion request: url=%s", request.url)

        temp_file_path = await download_file_from_url(str(request.url))
        logger.info("Downloaded URL content to temp path: %s", temp_file_path)

        validate_file(temp_file_path)
        logger.info(
            "Validated downloaded temp file: %s (exists=%s)",
            temp_file_path,
            temp_file_path.exists(),
        )

        converter = get_converter()
        logger.info("Starting conversion for downloaded temp file: %s", temp_file_path)
        markdown_content = await converter.convert(temp_file_path)
        logger.info(
            "Conversion finished for downloaded temp file: %s, markdown_length=%s",
            temp_file_path,
            len(markdown_content) if markdown_content is not None else None,
        )

        return ConvertResponse(
            success=True,
            markdown=markdown_content,
            filename=temp_file_path.name,
            file_type=temp_file_path.suffix.lower() if temp_file_path.suffix else None,
        )

    except ValidationError as e:
        logger.warning(
            "Validation error for URL '%s': %s",
            getattr(request, "url", None),
            e,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(
            "Unexpected error while processing URL '%s': %s",
            getattr(request, "url", None),
            e,
        )
        return ConvertResponse(
            success=False,
            error=str(e),
        )
    finally:
        if temp_file_path:
            logger.info("Cleaning up temp file for URL: %s", temp_file_path)
            cleanup_temp_file(temp_file_path)
