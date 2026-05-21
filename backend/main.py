from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

from app.api import auth, upload, lancamentos, dashboard
from app.core.logging.loki_handler import setup_loki_logger

app = FastAPI(
    title="Conciliação Contábil API",
    description="API para conciliação de lançamentos contábeis",
    version="1.0.0"
)

logger = setup_loki_logger("concog-api", extra_labels={"component": "web"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("API iniciada")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API encerrada")

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