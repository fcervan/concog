from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadLogEntry(BaseModel):
    arquivo: str
    status: str
    data: datetime
    detalhes: Optional[str] = None
