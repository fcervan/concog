import os
import json
import requests
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, status
import pymysql

from app.security.jwt import get_current_user
from app.schemas.historico_uploads import UploadLogEntry

router = APIRouter()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3307")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "concog"),
    "cursorclass": pymysql.cursors.DictCursor,
}


def _get_loki_base() -> str:
    push_url = os.getenv(
        "LOKI_URL",
        "http://localhost:3100/loki/api/v1/push"
    )
    return push_url.replace("/loki/api/v1/push", "")


def _get_cliente_id(usuario_id: int) -> int:
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT cliente_id FROM cliente_usuario WHERE usuario_id = %s LIMIT 1",
                (usuario_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não vinculado a nenhum cliente"
                )
            return row["cliente_id"]
    finally:
        conn.close()


@router.get("/historico-uploads", response_model=List[UploadLogEntry])
async def historico_uploads(current_user: dict = Depends(get_current_user)):
    usuario_id = current_user["id"]
    cliente_id = _get_cliente_id(usuario_id)

    loki_base = _get_loki_base()
    query = (
        '{app="splitar-lancamento-service",cliente_id="' + str(cliente_id) + '"}'
    )

    now = datetime.now(timezone.utc)
    trinta_dias_atras = int(now.timestamp() - 30 * 24 * 3600)

    params = {
        "query": query,
        "limit": 200,
        "start": str(trinta_dias_atras * 1_000_000_000),
        "end": str(int(now.timestamp() * 1e9)),
    }

    try:
        resp = requests.get(
            f"{loki_base}/loki/api/v1/query_range",
            params=params,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        detail = f"Erro ao consultar Loki: {e}"
        try:
            detail += f" - {resp.text}"
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao consultar Loki: {str(e)}"
        )

    entries = []
    seen = {}

    for stream in data.get("data", {}).get("result", []):
        for ts_nano, raw_value in stream.get("values", []):
            try:
                log_entry = json.loads(raw_value)
                message_str = log_entry.get("message", "{}")
                parts = message_str.split(" - ", 2)
                json_str = parts[2] if len(parts) > 2 else message_str
                message = json.loads(json_str)

                evento = message.get("evento")
                if evento not in ("inicio_processo", "validacao", "fim_processo", "erro_processo"):
                    continue

                arquivo = message.get("arquivo", "desconhecido")
                status_atual = message.get("status", "desconhecido")
                erro = message.get("erro")

                ts_sec = int(ts_nano) / 1e9
                data = datetime.fromtimestamp(ts_sec, tz=timezone.utc)

                if status_atual == "processando":
                    continue

                if arquivo not in seen or data > seen[arquivo]["data"]:
                    detalhes = erro if erro else None
                    seen[arquivo] = {
                        "arquivo": arquivo,
                        "status": status_atual,
                        "data": data,
                        "detalhes": detalhes,
                    }
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    for info in seen.values():
        entries.append(UploadLogEntry(
            arquivo=info["arquivo"],
            status=info["status"],
            data=info["data"],
            detalhes=info["detalhes"],
        ))

    entries.sort(key=lambda e: e.data, reverse=True)

    return entries
