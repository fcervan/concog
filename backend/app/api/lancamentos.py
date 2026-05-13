from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from app.schemas.lancamento import (
    LancamentoResponse, LancamentoFilter, 
    LancamentoUpdateStatus, StatusLancamento, PaginatedResponse
)
from app.security.jwt import get_current_user
from app.integrations import integracao

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def listar_lancamentos(
    status: Optional[StatusLancamento] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    valor_minimo: Optional[float] = None,
    valor_maximo: Optional[float] = None,
    identificador: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Lista lançamentos com filtros e paginação"""

    filtros = {
        "status": status,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "valor_minimo": valor_minimo,
        "valor_maximo": valor_maximo,
        "identificador": identificador
    }

    # Usar integração com seu serviço
    resultado = await integracao.listar_lancamentos(filtros, page, per_page)

    return PaginatedResponse(**resultado)

@router.get("/{lancamento_id}", response_model=LancamentoResponse)
async def get_lancamento(
    lancamento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retorna detalhes de um lançamento específico"""
    # Implementar busca por ID usando integração
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Funcionalidade em desenvolvimento"
    )

@router.put("/{lancamento_id}/status", response_model=LancamentoResponse)
async def update_status(
    lancamento_id: int,
    status_update: LancamentoUpdateStatus,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza status de um lançamento (para validação manual)"""

    resultado = await integracao.atualizar_status(
        lancamento_id=lancamento_id,
        status=status_update.status,
        observacao=status_update.observacao
    )

    if not resultado["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado["message"]
        )

    return {"id": lancamento_id, "status": status_update.status}

@router.get("/stats/resumo")
async def get_resumo_status(
    current_user: dict = Depends(get_current_user)
):
    """Retorna resumo por status para o dashboard"""
    stats = await integracao.obter_estatisticas()

    total = stats["total_lancamentos"] or 1

    return {
        "total": stats["total_lancamentos"],
        "conciliados": stats["conciliados"],
        "nao_conciliados": stats["nao_conciliados"],
        "pendentes": stats["pendentes"],
        "taxa_conciliacao": round((stats["conciliados"] / total * 100), 2) if total > 0 else 0
    }
