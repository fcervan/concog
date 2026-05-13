from pydantic import BaseModel
from typing import Dict

class DashboardStats(BaseModel):
    total_lancamentos: int
    conciliados: int
    nao_conciliados: int
    pendentes: int
    total_arquivos_processados: int
    ultimos_7_dias: Dict[str, int]
