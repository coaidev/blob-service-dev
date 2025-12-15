import logging
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from internal.config import API_V1_PREFIX, TEMP_DIR
from routers import convert


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    This ensures the temporary directory exists on startup and logs
    basic lifecycle events to help diagnose issues related to temp files.
    """
    try:
        TEMP_DIR.mkdir(exist_ok=True)
        logger.info("Application startup: TEMP_DIR initialized at %s", TEMP_DIR)
    except Exception as e:
        logger.exception("Failed to initialize TEMP_DIR at startup: %s", e)

    yield

    if TEMP_DIR.exists():
        try:
            shutil.rmtree(TEMP_DIR)
            TEMP_DIR.mkdir(exist_ok=True)
            logger.info("Application shutdown: TEMP_DIR cleaned and recreated at %s", TEMP_DIR)
        except Exception as e:
            logger.warning("Failed to clean TEMP_DIR on shutdown: %s", e)


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(convert.router, prefix=API_V1_PREFIX)


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
