from pydantic import BaseModel


class UploadRead(BaseModel):
    file_name: str
    url: str
    content_type: str
    size: int
