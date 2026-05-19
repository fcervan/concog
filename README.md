# ConCog - Contabilidade Cognitiva - Sistema Web

Sistema completo de conciliação contábil com frontend e backend.

## Estrutura

```
conciliacao-contabil-web/
├── backend/          # API FastAPI
│   ├── main.py
│   ├── app/
│   │   ├── api/      # Rotas
│   │   ├── schemas/  # Modelos Pydantic
│   │   └── security/ # JWT, Auth
│   └── requirements.txt
└── frontend/         # HTML/CSS/JS
    ├── index.html    # Landing page
    ├── css/
    ├── js/
    └── pages/        # Telas do sistema
```

## Instalação

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar banco de dados

Edite `app/security/jwt.py` e configure:
- `SECRET_KEY` - chave secreta para JWT
- Conecte seus repositórios reais no lugar dos mocks

### 3. Rodar o backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000/docs (Swagger UI)

### 4. Frontend

O frontend é servido automaticamente pelo FastAPI.
Acesse: http://localhost:8000

Ou use um servidor estático separado:
```bash
cd frontend
python -m http.server 3000
```

## Telas

| Rota | Descrição |
|------|-----------|
| `/` | Landing page (pública) |
| `/pages/login.html` | Login |
| `/pages/register.html` | Cadastro |
| `/pages/forgot-password.html` | Recuperar senha |
| `/pages/dashboard.html` | Dashboard (requer login) |
| `/pages/upload.html` | Upload de planilha |
| `/pages/consulta.html` | Consulta de lançamentos |
| `/pages/validacao.html` | Validação de status |

## Integração com seu código existente

1. **Substitua os mocks** nos arquivos de API (`auth.py`, `upload.py`, `lancamentos.py`)
2. **Conecte seus repositórios** existentes em `app/modules/`
3. **Ajuste os schemas** se necessário para bater com seus modelos

## Próximos passos

- [ ] Conectar banco de dados real
- [ ] Implementar envio de email para recuperação de senha
- [ ] Adicionar testes automatizados
- [ ] Configurar deploy (Docker, AWS, etc.)
