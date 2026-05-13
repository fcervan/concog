from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StatusLancamento(str, Enum):
    CONCILIADO = "conciliado"
    NAO_CONCILIADO = "nao_conciliado"
    PENDENTE = "pendente"

class LancamentoBase(BaseModel):
    data: datetime
    descricao: str
    valor: float = Field(..., gt=0)
    identificador: Optional[str] = None
    conta_debito: Optional[str] = None
    conta_credito: Optional[str] = None

class LancamentoCreate(LancamentoBase):
    arquivo_id: int

class LancamentoResponse(LancamentoBase):
    id: int
    status: StatusLancamento
    grupo_id: Optional[str] = None
    arquivo_id: int
    processado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class LancamentoFilter(BaseModel):
    status: Optional[StatusLancamento] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    identificador: Optional[str] = None

class LancamentoUpdateStatus(BaseModel):
    status: StatusLancamento
    observacao: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[LancamentoResponse]
    total: int
    page: int
    pages: int
    per_page: int
