from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UploadResponse(BaseModel):
    arquivo_id: int
    nome_arquivo: str
    tipo_arquivo: str
    total_registros: int
    status: str
    mensagem: str
    processado_em: Optional[datetime] = None

class UploadHistory(BaseModel):
    id: int
    nome_arquivo: str
    tipo_arquivo: str
    total_registros: int
    processado_em: datetime
    status: str
