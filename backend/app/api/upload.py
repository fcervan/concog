from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
import shutil
import os
from datetime import datetime

from app.schemas.upload import UploadResponse, UploadHistory
from app.security.jwt import get_current_user
from app.integrations import integracao

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploads_db = []

@router.post("/upload", response_model=UploadResponse)
async def upload_planilha(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Recebe planilha e inicia processamento de conciliação"""

    allowed_extensions = {".xlsx", ".xls", ".csv"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{current_user['id']}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    finally:
        file.file.close()

    # Usar integração com seu serviço
    resultado = await integracao.processar_planilha(file_path, current_user["id"])

    arquivo_id = len(uploads_db) + 1
    upload_record = {
        "id": arquivo_id,
        "nome_arquivo": file.filename,
        "tipo_arquivo": file_ext.replace(".", ""),
        "total_registros": resultado.get("total_registros", 0),
        "status": resultado.get("status", "processando"),
        "usuario_id": current_user["id"],
        "caminho": file_path,
        "processado_em": datetime.now()
    }
    uploads_db.append(upload_record)

    return UploadResponse(
        arquivo_id=arquivo_id,
        nome_arquivo=file.filename,
        tipo_arquivo=file_ext.replace(".", ""),
        total_registros=resultado.get("total_registros", 0),
        status=resultado.get("status", "processando"),
        mensagem=resultado.get("mensagem", "Arquivo recebido"),
        processado_em=datetime.now()
    )

@router.get("/upload/history", response_model=List[UploadHistory])
async def get_upload_history(
    current_user: dict = Depends(get_current_user)
):
    """Retorna histórico de uploads do usuário"""
    user_uploads = [u for u in uploads_db if u["usuario_id"] == current_user["id"]]

    return [
        UploadHistory(
            id=u["id"],
            nome_arquivo=u["nome_arquivo"],
            tipo_arquivo=u["tipo_arquivo"],
            total_registros=u["total_registros"],
            processado_em=u["processado_em"],
            status=u["status"]
        )
        for u in user_uploads
    ]
