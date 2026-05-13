from fastapi import APIRouter, Depends
from app.schemas.dashboard import DashboardStats
from app.security.jwt import get_current_user
from app.integrations import integracao

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Retorna estatísticas para o dashboard"""

    stats = await integracao.obter_estatisticas()

    return DashboardStats(
        total_lancamentos=stats["total_lancamentos"],
        conciliados=stats["conciliados"],
        nao_conciliados=stats["nao_conciliados"],
        pendentes=stats["pendentes"],
        total_arquivos_processados=stats["total_arquivos_processados"],
        ultimos_7_dias=stats["ultimos_7_dias"]
    )
