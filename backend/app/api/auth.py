from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.schemas.auth import UsuarioCreate, UsuarioLogin, Token, RecuperarSenha, RedefinirSenha
from app.security.jwt import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# Mock de banco de dados - substituir pelo seu repositório real
usuarios_db = {}

@router.post("/register", response_model=Token)
async def register(user_data: UsuarioCreate):
    """Cadastra novo usuário"""
    if user_data.senha != user_data.confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não coincidem"
        )

    if user_data.email in usuarios_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    user_id = len(usuarios_db) + 1
    hashed_password = get_password_hash(user_data.senha)

    usuarios_db[user_data.email] = {
        "id": user_id,
        "nome": user_data.nome,
        "email": user_data.email,
        "senha_hash": hashed_password,
        "ativo": True
    }

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
            "criado_em": "2026-05-12T00:00:00"
        }
    }

@router.post("/login", response_model=Token)
async def login(credentials: UsuarioLogin):
    """Autentica usuário e retorna token JWT"""
    user = usuarios_db.get(credentials.email)

    if not user or not verify_password(credentials.senha, user["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "ativo": user["ativo"],
            "criado_em": "2026-05-12T00:00:00"
        }
    }

@router.post("/forgot-password")
async def forgot_password(data: RecuperarSenha):
    """Solicita recuperação de senha"""
    user = usuarios_db.get(data.email)
    if not user:
        # Não revelar se email existe ou não (segurança)
        return {"mensagem": "Se o email existir, você receberá instruções"}

    # Aqui você enviaria email com token
    return {"mensagem": "Se o email existir, você receberá instruções"}

@router.post("/reset-password")
async def reset_password(data: RedefinirSenha):
    """Redefine senha com token"""
    # Validar token e atualizar senha
    return {"mensagem": "Senha redefinida com sucesso"}
