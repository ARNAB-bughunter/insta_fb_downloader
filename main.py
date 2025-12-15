from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import logging, os
from urllib.parse import quote

from downloader import download_video, VideoDownloadError
from schemas import DownloadRequest, DownloadResponse
from pathlib import Path
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
    


@app.get("/files")
@limiter.limit("10/minute")
def stream_file(
    request: Request,
    file_path: str = Query(..., description="Relative file path returned by /download")
):
    resolved_path = Path(file_path).resolve()
    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    def file_iterator():
        try:
            with open(resolved_path, "rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
        finally:
            # ✅ Always delete file (success, error, disconnect)
            try:
                os.remove(resolved_path)
                print(f"Deleted file: {resolved_path}")
            except Exception as e:
                print(f"Failed to delete file: {e}")

    filename = resolved_path.name
    encoded_filename = quote(filename)

    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def redirect_to_index():
    print("HIII")
    return FileResponse("static/index.html")