from fastapi import APIRouter, HTTPException, status
from datetime import timedelta, datetime
import pymysql
from app.schemas.auth import UsuarioCreate, UsuarioLogin, Token, RecuperarSenha, RedefinirSenha
from app.security.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "123456",
    "database": "concog",
    "cursorclass": pymysql.cursors.DictCursor,
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@router.post("/register", response_model=Token)
async def register(user_data: UsuarioCreate):
    if user_data.senha != user_data.confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não coincidem"
        )

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT usuario_id FROM usuario WHERE login = %s", (user_data.email,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Login já cadastrado"
                )

            data_cad = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO usuario (nome, login, senha, data_cad) VALUES (%s, %s, %s, %s)",
                (user_data.nome, user_data.email, user_data.senha, data_cad)
            )
            conn.commit()
            user_id = cursor.lastrowid
    finally:
        conn.close()

    access_token = create_access_token(
        data={"sub": str(user_id), "email": user_data.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": user_id,
            "nome": user_data.nome,
            "email": user_data.email,
            "ativo": True,
            "criado_em": data_cad
        }
    }

@router.post("/login", response_model=Token)
async def login(credentials: UsuarioLogin):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT usuario_id, nome, login, senha, data_cad FROM usuario WHERE login = %s",
                (credentials.email,)
            )
            user = cursor.fetchone()

        if not user or user["senha"] != credentials.senha:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
    finally:
        conn.close()

    access_token = create_access_token(
        data={"sub": str(user["usuario_id"]), "email": user["login"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": user["usuario_id"],
            "nome": user["nome"],
            "email": user["login"],
            "ativo": True,
            "criado_em": user["data_cad"].strftime("%Y-%m-%dT%H:%M:%S") if isinstance(user["data_cad"], datetime) else user["data_cad"]
        }
    }

@router.post("/forgot-password")
async def forgot_password(data: RecuperarSenha):
    return {"mensagem": "Se o login existir, você receberá instruções"}

@router.post("/reset-password")
async def reset_password(data: RedefinirSenha):
    return {"mensagem": "Senha redefinida com sucesso"}
