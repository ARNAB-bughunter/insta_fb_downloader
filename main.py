from fastapi import FastAPI, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse, FileResponse
import logging

from downloader import download_video, VideoDownloadError
from schemas import DownloadRequest, DownloadResponse
from rate_limiter import limiter, rate_limit_exceeded_handler

app = FastAPI(
    title="Instagram & Facebook Video Downloader API",
    version="1.0.0",
    description="Download Instagram and Facebook videos using yt-dlp",
)

# Attach limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

@app.post("/download",response_model=DownloadResponse,status_code=status.HTTP_200_OK,)
@limiter.limit("5/minute")
async def download_endpoint(request: Request, payload: DownloadRequest):
    try:
        file_path = download_video(
            url=str(payload.url),
            output_dir=payload.output_dir or "downloads",
        )

        return DownloadResponse(
            status="success",
            file_path=file_path,
            message="Video downloaded successfully",
        )

    except VideoDownloadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        )

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def redirect_to_index():
    print("HIII")
    return FileResponse("static/index.html")