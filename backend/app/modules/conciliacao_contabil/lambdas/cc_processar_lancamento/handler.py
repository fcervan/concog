from backend.app.modules.conciliacao_contabil.services.processar_lancamento_service import ProcessarLancamentoService


def lambda_handler(event, context):
    service = ProcessarLancamentoService()
    return service.classificar(event)
