from backend.app.modules.conciliacao_contabil.services.splitar_lancamento_service import SplitarLancamentoService
import os

print(os.getenv("LLM_PROVIDER"))

def lambda_handler(event, context):
    service = SplitarLancamentoService()
    return service.processar(event)
