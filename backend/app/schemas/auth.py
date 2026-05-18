from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: str

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=1, max_length=100)
    confirmar_senha: str = Field(..., min_length=1, max_length=100)

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse

class RecuperarSenha(BaseModel):
    email: str

class RedefinirSenha(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=1)
