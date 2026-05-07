from fastapi import FastAPI, Request
from backend.app.modules.conciliacao_contabil.lambdas.cc_splitar_lancamento.handler import lambda_handler

app = FastAPI()

@app.post("/webhook/s3")
async def s3_webhook(request: Request):
    event = await request.json()
    result = lambda_handler(event, "")
    return {"status": "ok", "result": result}