from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Form
from typing import List, Optional
import os
from datetime import datetime

from app.schemas.upload import UploadResponse, UploadHistory
from app.security.jwt import get_current_user
from app.core.storage.s3_client import storage

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_planilha(
    file: UploadFile = File(...),
    cliente_id: int = Form(...),
    arquivo_parser_id: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    allowed_extensions = {".xlsx", ".xls", ".csv"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
        )

    file_content = await file.read()

    try:
        s3_path = storage.upload_file(
            file_content=file_content,
            cliente_id=cliente_id,
            arquivo_parser_id=arquivo_parser_id,
            usuario_id=current_user["id"],
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar arquivo: {str(e)}"
        )

    return UploadResponse(
        arquivo_id=0,
        nome_arquivo=file.filename,
        tipo_arquivo=file_ext.replace(".", ""),
        total_registros=0,
        status="processando",
        mensagem=f"Arquivo enviado para {s3_path}",
        processado_em=datetime.now()
    )

@router.get("/upload/history", response_model=List[UploadHistory])
async def get_upload_history(
    current_user: dict = Depends(get_current_user)
):
    return []
