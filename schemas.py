from pydantic import BaseModel, HttpUrl, Field

class DownloadRequest(BaseModel):
    url: HttpUrl = Field(..., description="Instagram or Facebook video URL")

class DownloadResponse(BaseModel):
    status: str
    file_path: str | None = None
    message: str
