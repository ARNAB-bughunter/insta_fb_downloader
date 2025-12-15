import yt_dlp
import os
from pathlib import Path
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

SUPPORTED_DOMAINS = ("instagram.com", "facebook.com")

class VideoDownloadError(Exception):
    pass

def download_video(url: str) -> str:
    if not any(domain in url for domain in SUPPORTED_DOMAINS):
        raise VideoDownloadError("Only Instagram and Facebook URLs are supported")

    output_dir = f"Downloads/{str(uuid4().hex)}"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "best",
        "outtmpl": str(output_path / "%(title).200s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            raise VideoDownloadError("Download completed but file not found")

        logger.info("Video downloaded successfully: %s", file_path)
        return file_path

    except yt_dlp.utils.DownloadError as e:
        logger.error("yt-dlp download error: %s", str(e))
        raise VideoDownloadError("Failed to download video. The content may be private or unavailable.")

    except Exception as e:
        logger.exception("Unexpected error during download")
        raise VideoDownloadError("Internal error occurred while downloading the video")
