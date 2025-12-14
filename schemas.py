from pydantic import BaseModel, HttpUrl, Field

class DownloadRequest(BaseModel):
    url: HttpUrl = Field(..., description="Instagram or Facebook video URL")
    output_dir: str | None = Field(
        default="downloads",
        description="Directory to save the downloaded video"
    )

class DownloadResponse(BaseModel):
    status: str
    file_path: str | None = None
    message: str
