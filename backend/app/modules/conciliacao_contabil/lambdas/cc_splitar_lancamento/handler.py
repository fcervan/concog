from backend.app.modules.conciliacao_contabil.services.splitar_lancamento_service import SplitarLancamentoService


def lambda_handler(event, context):
    service = SplitarLancamentoService()
    return service.processar(event)
