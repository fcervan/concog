from fastapi import APIRouter, HTTPException, status
from datetime import timedelta, datetime
import pymysql
from app.schemas.auth import UsuarioCreate, UsuarioLogin, Token, RecuperarSenha, RedefinirSenha
from app.security.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import jwt
from pydantic import BaseModel

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

class ParserConfigRequest(BaseModel):
    nome_fantasia: str
    cnpj: str
    arquivo_parser_id: int
    usuario_id: int = None

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

@router.post("/login")
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

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.usuario_id, u.nome, u.login,
                    c.cliente_id, c.nome_fantasia, c.cnpj,
                    ap.arquivo_parser_id, ap.nome_parser, ap.descricao_arquivo_parser
                FROM usuario u
                    INNER JOIN cliente_usuario cu ON u.usuario_id = cu.usuario_id
                    INNER JOIN cliente c ON cu.cliente_id = c.cliente_id
                    INNER JOIN arquivo_parser_cliente apc ON c.cliente_id = apc.cliente_id
                    INNER JOIN arquivo_parser ap ON apc.arquivo_parser_id = ap.arquivo_parser_id
                WHERE u.usuario_id = %s
            """, (user["usuario_id"],))
            parser_config = cursor.fetchone()
    finally:
        conn.close()

    access_token = create_access_token(
        data={"sub": str(user["usuario_id"]), "email": user["login"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    usuario_data = {
        "id": user["usuario_id"],
        "nome": user["nome"],
        "email": user["login"],
        "ativo": True,
        "criado_em": user["data_cad"].strftime("%Y-%m-%dT%H:%M:%S") if isinstance(user["data_cad"], datetime) else user["data_cad"]
    }

    if parser_config:
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": usuario_data,
            "precisa_configurar": False,
            "sessao": {
                "cliente_id": parser_config["cliente_id"],
                "nome_fantasia": parser_config["nome_fantasia"],
                "cnpj": parser_config["cnpj"],
                "arquivo_parser_id": parser_config["arquivo_parser_id"],
                "nome_parser": parser_config["nome_parser"],
                "descricao_arquivo_parser": parser_config["descricao_arquivo_parser"],
            }
        }
    else:
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": usuario_data,
            "precisa_configurar": True,
            "sessao": None
        }

@router.post("/configurar-parser")
async def configurar_parser(data: ParserConfigRequest, token: str = None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT cliente_id FROM cliente WHERE cnpj = %s", (data.cnpj,))
            cliente = cursor.fetchone()

            if cliente:
                cliente_id = cliente["cliente_id"]
            else:
                data_cad = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO cliente (nome_fantasia, cnpj, data_cad) VALUES (%s, %s, %s)",
                    (data.nome_fantasia, data.cnpj, data_cad)
                )
                conn.commit()
                cliente_id = cursor.lastrowid

            usuario_id = data.usuario_id
            if not usuario_id and token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                usuario_id = int(payload.get("sub"))

            if not usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário não identificado"
                )

            cursor.execute(
                "SELECT 1 FROM cliente_usuario WHERE cliente_id = %s AND usuario_id = %s",
                (cliente_id, usuario_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO cliente_usuario (cliente_id, usuario_id) VALUES (%s, %s)",
                    (cliente_id, usuario_id)
                )

            cursor.execute(
                "SELECT 1 FROM arquivo_parser_cliente WHERE cliente_id = %s AND arquivo_parser_id = %s",
                (cliente_id, data.arquivo_parser_id)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parser já configurado para este cliente"
                )

            cursor.execute(
                "INSERT INTO arquivo_parser_cliente (cliente_id, arquivo_parser_id) VALUES (%s, %s)",
                (cliente_id, data.arquivo_parser_id)
            )
            conn.commit()

            cursor.execute("""
                SELECT
                    c.cliente_id, c.nome_fantasia, c.cnpj,
                    ap.arquivo_parser_id, ap.nome_parser, ap.descricao_arquivo_parser
                FROM cliente c
                    INNER JOIN arquivo_parser_cliente apc ON c.cliente_id = apc.cliente_id
                    INNER JOIN arquivo_parser ap ON apc.arquivo_parser_id = ap.arquivo_parser_id
                WHERE c.cliente_id = %s AND ap.arquivo_parser_id = %s
            """, (cliente_id, data.arquivo_parser_id))
            sessao = cursor.fetchone()
    finally:
        conn.close()

    return {"mensagem": "Parser configurado com sucesso", "sessao": sessao}

@router.get("/parsers-disponiveis")
async def parsers_disponiveis():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT arquivo_parser_id, nome_parser, descricao_arquivo_parser FROM arquivo_parser")
            parsers = cursor.fetchall()
    finally:
        conn.close()

    return {"parsers": parsers}

@router.post("/forgot-password")
async def forgot_password(data: RecuperarSenha):
    return {"mensagem": "Se o login existir, você receberá instruções"}

@router.post("/reset-password")
async def reset_password(data: RedefinirSenha):
    return {"mensagem": "Senha redefinida com sucesso"}
