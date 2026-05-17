from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api import auth, upload, lancamentos, dashboard

app = FastAPI(
    title="Conciliação Contábil API",
    description="API para conciliação de lançamentos contábeis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ROTAS DA API ===
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(lancamentos.router, prefix="/api/lancamentos", tags=["Lançamentos"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

# === ESTÁTICOS ===
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")

# Montar tudo em /static
app.mount("/statics", StaticFiles(directory=frontend_path), name="statics")

# Raiz serve index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)